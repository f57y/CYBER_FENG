from __future__ import annotations

import threading
from pathlib import Path
from queue import Queue
from typing import Any, Callable, Iterator

from cyber_feng.config import Settings


_LOCAL_MODEL_LOCK = threading.Lock()
_LOCAL_MODEL_CACHE: dict[tuple[str, str, str], tuple[Any, Any]] = {}


def pending_user_messages(history: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not history:
        return []

    last_assistant_index = -1
    for index in range(len(history) - 1, -1, -1):
        if history[index].get("role") == "assistant":
            last_assistant_index = index
            break

    return history[last_assistant_index + 1 :]


def extract_text_content(content: Any) -> str | None:
    if isinstance(content, str):
        text = content.strip()
        return text or None

    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if not isinstance(item, dict):
                continue
            if item.get("type") != "text":
                continue
            text = item.get("text")
            if isinstance(text, str) and text.strip():
                parts.append(text.strip())
        if parts:
            return "\n".join(parts)

    return None


def visible_text_messages(
    history: list[dict[str, Any]],
    max_history_messages: int,
) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = []
    for item in history:
        role = item.get("role")
        content = item.get("content")
        if role not in {"user", "assistant"}:
            continue
        text_content = extract_text_content(content)
        if text_content is None:
            continue
        messages.append({"role": role, "content": text_content})
    return messages[-max_history_messages:]


def choose_local_torch_dtype(dtype_name: str) -> Any:
    import torch

    if dtype_name == "bf16":
        return torch.bfloat16
    if dtype_name == "fp16":
        return torch.float16
    if torch.cuda.is_available() and torch.cuda.is_bf16_supported():
        return torch.bfloat16
    return torch.float16


def resolve_local_base_model_name(settings: Settings) -> str:
    if settings.local_base_model_name:
        return settings.local_base_model_name

    adapter_path = Path(settings.local_adapter_path)
    adapter_config_path = adapter_path / "adapter_config.json"
    if not adapter_config_path.exists():
        raise RuntimeError(
            "未找到 adapter_config.json。请确认 `CYBER_FENG_LOCAL_ADAPTER_PATH` 指向训练输出目录。"
        )

    import json

    adapter_config = json.loads(adapter_config_path.read_text(encoding="utf-8"))
    base_model_name = adapter_config.get("base_model_name_or_path")
    if not isinstance(base_model_name, str) or not base_model_name.strip():
        raise RuntimeError("adapter_config.json 里没有有效的 base_model_name_or_path。")
    return base_model_name.strip()


def load_local_lora_model(
    settings: Settings,
    progress_callback: Callable[[str], None] | None = None,
) -> tuple[Any, Any]:
    adapter_path = settings.local_adapter_path
    if not adapter_path:
        raise RuntimeError(
            "当前模式是 local_transformers_lora，但没有配置 `CYBER_FENG_LOCAL_ADAPTER_PATH`。"
        )

    base_model_name = resolve_local_base_model_name(settings)
    cache_key = (adapter_path, base_model_name, settings.local_dtype)
    cached = _LOCAL_MODEL_CACHE.get(cache_key)
    if cached is not None:
        return cached

    with _LOCAL_MODEL_LOCK:
        cached = _LOCAL_MODEL_CACHE.get(cache_key)
        if cached is not None:
            return cached

        import torch
        from peft import PeftModel
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

        if progress_callback is not None:
            progress_callback("正在检查本地 LoRA 配置")

        if not torch.cuda.is_available():
            raise RuntimeError("本地 LoRA 推理模式当前只支持可用的 CUDA 环境。")

        dtype = choose_local_torch_dtype(settings.local_dtype)
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=dtype,
        )

        tokenizer_source = adapter_path if Path(adapter_path).exists() else base_model_name
        if progress_callback is not None:
            progress_callback("正在加载 tokenizer")
        tokenizer = AutoTokenizer.from_pretrained(
            tokenizer_source,
            trust_remote_code=True,
        )
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        if tokenizer.pad_token_id is None:
            raise RuntimeError("tokenizer 没有可用的 pad_token。")
        tokenizer.padding_side = "left"

        if progress_callback is not None:
            progress_callback("正在加载底座模型（首次会比较慢）")
        base_model = AutoModelForCausalLM.from_pretrained(
            base_model_name,
            quantization_config=quantization_config,
            torch_dtype=dtype,
            device_map="auto",
            trust_remote_code=True,
        )

        if progress_callback is not None:
            progress_callback("正在加载 LoRA 适配器")
        model = PeftModel.from_pretrained(
            base_model,
            adapter_path,
            is_trainable=False,
        )
        model.eval()

        _LOCAL_MODEL_CACHE[cache_key] = (tokenizer, model)
        return tokenizer, model


def first_model_device(model: Any) -> Any:
    import torch

    parameter = next(model.parameters(), None)
    if parameter is not None:
        return parameter.device
    return torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


def backend_event(event_type: str, text: str) -> dict[str, str]:
    return {"type": event_type, "text": text}


def format_backend_exception(exc: Exception) -> str:
    return f"[模型调用失败] {exc}"


def stream_local_lora_backend(
    messages: list[dict[str, str]],
    settings: Settings,
) -> Iterator[dict[str, str]]:
    event_queue: Queue[dict[str, str]] = Queue()

    def push_status(text: str) -> None:
        event_queue.put(backend_event("status", text))

    def push_delta(text: str) -> None:
        event_queue.put(backend_event("delta", text))

    def worker() -> None:
        try:
            import torch
            from transformers import TextIteratorStreamer

            tokenizer, model = load_local_lora_model(
                settings,
                progress_callback=push_status,
            )

            push_status("模型已就绪，开始生成")

            prompt_messages = [
                {"role": "system", "content": settings.system_prompt},
                *messages,
            ]
            model_inputs = tokenizer.apply_chat_template(
                prompt_messages,
                tokenize=True,
                add_generation_prompt=True,
                return_tensors="pt",
            )
            input_ids = model_inputs.to(first_model_device(model))
            attention_mask = torch.ones_like(input_ids)

            streamer = TextIteratorStreamer(
                tokenizer,
                skip_prompt=True,
                skip_special_tokens=True,
            )

            generation_kwargs: dict[str, Any] = {
                "input_ids": input_ids,
                "attention_mask": attention_mask,
                "max_new_tokens": settings.local_max_new_tokens,
                "pad_token_id": tokenizer.pad_token_id,
                "eos_token_id": tokenizer.eos_token_id,
                "repetition_penalty": settings.local_repetition_penalty,
                "no_repeat_ngram_size": settings.local_no_repeat_ngram_size,
                "renormalize_logits": True,
                "use_cache": True,
                "streamer": streamer,
            }
            if settings.temperature > 0:
                generation_kwargs["do_sample"] = True
                generation_kwargs["temperature"] = settings.temperature
                generation_kwargs["top_p"] = settings.local_top_p
                generation_kwargs["top_k"] = settings.local_top_k
            else:
                generation_kwargs["do_sample"] = False

            generation_error: dict[str, Exception] = {}

            def generation_target() -> None:
                try:
                    with torch.inference_mode():
                        model.generate(**generation_kwargs)
                except Exception as exc:  # noqa: BLE001
                    generation_error["exc"] = exc
                    streamer.end()

            generation_thread = threading.Thread(
                target=generation_target,
                daemon=True,
            )
            generation_thread.start()

            text_emitted = False
            for chunk in streamer:
                if not chunk:
                    continue
                text_emitted = True
                push_delta(chunk)

            generation_thread.join()
            if "exc" in generation_error:
                raise generation_error["exc"]

            if not text_emitted:
                push_delta("我一下子没组织好语言，你再问我一遍。")
        except Exception as exc:  # noqa: BLE001
            event_queue.put(backend_event("error", format_backend_exception(exc)))
        finally:
            event_queue.put(backend_event("done", ""))

    threading.Thread(target=worker, daemon=True).start()

    while True:
        event = event_queue.get()
        if event["type"] == "done":
            return
        yield event


def stream_assistant_reply_events(
    history: list[dict[str, Any]],
    settings: Settings,
) -> Iterator[dict[str, str]]:
    messages = visible_text_messages(history, settings.max_history_messages)

    if not messages:
        yield backend_event("error", "当前还没有可发送给模型的文本内容。")
        return

    if settings.model_mode != "local_transformers_lora":
        yield backend_event(
            "error",
            "当前版本只支持 `local_transformers_lora` 模式。请检查 `.env` 配置。",
        )
        return

    yield from stream_local_lora_backend(messages, settings)
