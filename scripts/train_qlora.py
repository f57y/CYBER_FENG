from __future__ import annotations

import argparse
import inspect
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


IGNORE_INDEX = -100
DEFAULT_MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"


@dataclass(frozen=True)
class ChatSample:
    sample_id: str
    source: str
    sample_type: str
    messages: list[dict[str, str]]


class EncodedChatDataset:
    def __init__(self, encoded_samples: list[dict[str, list[int]]]) -> None:
        self.encoded_samples = encoded_samples

    def __len__(self) -> int:
        return len(self.encoded_samples)

    def __getitem__(self, index: int) -> dict[str, list[int]]:
        return self.encoded_samples[index]


class SupervisedDataCollator:
    def __init__(self, pad_token_id: int, pad_to_multiple_of: int = 8) -> None:
        self.pad_token_id = pad_token_id
        self.pad_to_multiple_of = pad_to_multiple_of

    def __call__(self, features: list[dict[str, list[int]]]) -> dict[str, Any]:
        import torch

        max_length = max(len(feature["input_ids"]) for feature in features)
        if self.pad_to_multiple_of > 1 and max_length % self.pad_to_multiple_of != 0:
            max_length = (
                (max_length + self.pad_to_multiple_of - 1)
                // self.pad_to_multiple_of
                * self.pad_to_multiple_of
            )

        input_ids: list[list[int]] = []
        attention_mask: list[list[int]] = []
        labels: list[list[int]] = []

        for feature in features:
            pad_length = max_length - len(feature["input_ids"])
            input_ids.append(
                feature["input_ids"] + [self.pad_token_id] * pad_length
            )
            attention_mask.append(
                feature["attention_mask"] + [0] * pad_length
            )
            labels.append(
                feature["labels"] + [IGNORE_INDEX] * pad_length
            )

        return {
            "input_ids": torch.tensor(input_ids, dtype=torch.long),
            "attention_mask": torch.tensor(attention_mask, dtype=torch.long),
            "labels": torch.tensor(labels, dtype=torch.long),
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="使用 QLoRA 微调峰哥风格聊天模型。"
    )
    parser.add_argument(
        "--model-name-or-path",
        default=DEFAULT_MODEL_NAME,
        help="Hugging Face 模型名或本地模型目录",
    )
    parser.add_argument(
        "--train-data-path",
        type=Path,
        default=Path("data/training/sft/train.jsonl"),
        help="训练集 JSONL 路径",
    )
    parser.add_argument(
        "--eval-data-path",
        type=Path,
        default=Path("data/training/sft/val.jsonl"),
        help="验证集 JSONL 路径；如果文件不存在则跳过验证",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/training/runs/qwen25-7b-fengge-lora"),
        help="LoRA adapter 输出目录",
    )
    parser.add_argument(
        "--max-seq-length",
        type=int,
        default=1024,
        help="样本最大 token 长度",
    )
    parser.add_argument(
        "--num-train-epochs",
        type=float,
        default=3.0,
        help="训练轮数",
    )
    parser.add_argument(
        "--learning-rate",
        type=float,
        default=2e-4,
        help="学习率",
    )
    parser.add_argument(
        "--weight-decay",
        type=float,
        default=0.0,
        help="权重衰减",
    )
    parser.add_argument(
        "--warmup-ratio",
        type=float,
        default=0.03,
        help="warmup 比例",
    )
    parser.add_argument(
        "--per-device-train-batch-size",
        type=int,
        default=2,
        help="每张卡的训练 batch size",
    )
    parser.add_argument(
        "--per-device-eval-batch-size",
        type=int,
        default=2,
        help="每张卡的验证 batch size",
    )
    parser.add_argument(
        "--gradient-accumulation-steps",
        type=int,
        default=8,
        help="梯度累计步数",
    )
    parser.add_argument(
        "--logging-steps",
        type=int,
        default=10,
        help="日志打印步数",
    )
    parser.add_argument(
        "--save-total-limit",
        type=int,
        default=2,
        help="最多保留多少个 checkpoint",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="随机种子",
    )
    parser.add_argument(
        "--lora-r",
        type=int,
        default=64,
        help="LoRA rank",
    )
    parser.add_argument(
        "--lora-alpha",
        type=int,
        default=128,
        help="LoRA alpha",
    )
    parser.add_argument(
        "--lora-dropout",
        type=float,
        default=0.05,
        help="LoRA dropout",
    )
    parser.add_argument(
        "--target-modules",
        default="auto",
        help="逗号分隔的 target modules，默认自动推断",
    )
    parser.add_argument(
        "--dtype",
        choices=["auto", "bf16", "fp16"],
        default="auto",
        help="训练计算精度",
    )
    parser.add_argument(
        "--attn-implementation",
        choices=["auto", "sdpa", "flash_attention_2", "eager"],
        default="auto",
        help="attention 实现方式",
    )
    parser.add_argument(
        "--resume-from-checkpoint",
        default=None,
        help="从已有 checkpoint 恢复训练",
    )
    parser.add_argument(
        "--trust-remote-code",
        action="store_true",
        help="加载需要 trust_remote_code 的模型",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只检查数据与参数，不真正开始训练",
    )
    return parser.parse_args()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {path}")

    records: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number} 不是合法 JSON") from exc
    return records


def normalize_chat_samples(path: Path) -> list[ChatSample]:
    samples: list[ChatSample] = []
    for index, record in enumerate(read_jsonl(path), 1):
        sample_id = require_str(record, "id", f"{path.name}[{index}]")
        source = require_str(record, "source", sample_id)
        sample_type = require_str(record, "type", sample_id)
        messages = record.get("messages")
        if not isinstance(messages, list) or len(messages) < 2:
            raise ValueError(f"{sample_id} 的 messages 至少要包含 user 和 assistant")

        normalized_messages: list[dict[str, str]] = []
        for item in messages:
            if not isinstance(item, dict):
                raise ValueError(f"{sample_id} 的 messages 项必须是对象")
            role = require_str(item, "role", sample_id)
            content = require_str(item, "content", sample_id).strip()
            if role not in {"system", "user", "assistant"}:
                raise ValueError(f"{sample_id} 出现了不支持的 role: {role!r}")
            if not content:
                raise ValueError(f"{sample_id} 的 {role} content 不能为空")
            normalized_messages.append({"role": role, "content": content})

        if normalized_messages[-1]["role"] != "assistant":
            raise ValueError(f"{sample_id} 的最后一条消息必须是 assistant")

        samples.append(
            ChatSample(
                sample_id=sample_id,
                source=source,
                sample_type=sample_type,
                messages=normalized_messages,
            )
        )

    return samples


def require_str(obj: dict[str, Any], key: str, sample_id: str) -> str:
    value = obj.get(key)
    if not isinstance(value, str):
        raise ValueError(f"{sample_id} 的 {key} 必须是字符串")
    return value


def summarize_samples(samples: list[ChatSample]) -> dict[str, Any]:
    type_counts: dict[str, int] = {}
    user_chars = 0
    assistant_chars = 0

    for sample in samples:
        type_counts[sample.sample_type] = type_counts.get(sample.sample_type, 0) + 1
        for message in sample.messages:
            if message["role"] == "user":
                user_chars += len(message["content"])
            elif message["role"] == "assistant":
                assistant_chars += len(message["content"])

    return {
        "samples": len(samples),
        "unique_sources": len({sample.source for sample in samples}),
        "type_counts": type_counts,
        "avg_user_chars": round(user_chars / max(len(samples), 1), 1),
        "avg_assistant_chars": round(assistant_chars / max(len(samples), 1), 1),
    }


def common_prefix_length(left: list[int], right: list[int]) -> int:
    length = min(len(left), len(right))
    index = 0
    while index < length and left[index] == right[index]:
        index += 1
    return index


def build_prompt_and_labels(
    sample: ChatSample,
    tokenizer: Any,
    max_seq_length: int,
) -> dict[str, list[int]] | None:
    if not hasattr(tokenizer, "apply_chat_template"):
        raise RuntimeError(
            "当前 tokenizer 不支持 chat template。请使用 instruct/chat 模型，例如 Qwen/Qwen2.5-7B-Instruct。"
        )

    prompt_ids = tokenizer.apply_chat_template(
        sample.messages[:-1],
        tokenize=True,
        add_generation_prompt=True,
    )
    full_ids = tokenizer.apply_chat_template(
        sample.messages,
        tokenize=True,
        add_generation_prompt=False,
    )

    assistant_start = common_prefix_length(prompt_ids, full_ids)
    if assistant_start >= len(full_ids):
        return None

    labels = [IGNORE_INDEX] * assistant_start + full_ids[assistant_start:]
    input_ids = full_ids

    if len(input_ids) > max_seq_length:
        input_ids = input_ids[-max_seq_length:]
        labels = labels[-max_seq_length:]

    if all(label == IGNORE_INDEX for label in labels):
        return None

    return {
        "input_ids": input_ids,
        "attention_mask": [1] * len(input_ids),
        "labels": labels,
    }


def encode_samples(
    samples: list[ChatSample],
    tokenizer: Any,
    max_seq_length: int,
) -> tuple[EncodedChatDataset, dict[str, Any]]:
    encoded_samples: list[dict[str, list[int]]] = []
    skipped_samples = 0
    truncated_samples = 0

    for sample in samples:
        encoded = build_prompt_and_labels(
            sample=sample,
            tokenizer=tokenizer,
            max_seq_length=max_seq_length,
        )
        if encoded is None:
            skipped_samples += 1
            continue
        if len(encoded["input_ids"]) == max_seq_length:
            full_ids = tokenizer.apply_chat_template(
                sample.messages,
                tokenize=True,
                add_generation_prompt=False,
            )
            if len(full_ids) > max_seq_length:
                truncated_samples += 1
        encoded_samples.append(encoded)

    stats = {
        "encoded_samples": len(encoded_samples),
        "skipped_samples": skipped_samples,
        "truncated_samples": truncated_samples,
    }
    return EncodedChatDataset(encoded_samples), stats


def choose_torch_dtype(dtype_name: str) -> Any:
    import torch

    if dtype_name == "bf16":
        return torch.bfloat16
    if dtype_name == "fp16":
        return torch.float16

    if torch.cuda.is_available() and torch.cuda.is_bf16_supported():
        return torch.bfloat16
    return torch.float16


def infer_target_modules(model: Any) -> list[str]:
    preferred = [
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
        "gate_proj",
        "up_proj",
        "down_proj",
    ]

    module_names: set[str] = set()
    for name, module in model.named_modules():
        last_name = name.rsplit(".", 1)[-1]
        class_name = module.__class__.__name__.lower()
        lowered = name.lower()

        if "linear" not in class_name:
            continue
        if any(token in lowered for token in ("lm_head", "embed", "norm", "rotary_emb")):
            continue

        module_names.add(last_name)

    if all(name in module_names for name in preferred):
        return preferred
    if not module_names:
        raise RuntimeError("自动推断 LoRA target modules 失败，请手动传 --target-modules")
    return sorted(module_names)


def build_training_summary(
    args: argparse.Namespace,
    dtype: Any,
    target_modules: list[str],
    train_stats: dict[str, Any],
    eval_stats: dict[str, Any] | None,
    encoded_train_stats: dict[str, Any],
    encoded_eval_stats: dict[str, Any] | None,
) -> dict[str, Any]:
    summary = {
        "model_name_or_path": args.model_name_or_path,
        "output_dir": str(args.output_dir),
        "max_seq_length": args.max_seq_length,
        "num_train_epochs": args.num_train_epochs,
        "learning_rate": args.learning_rate,
        "per_device_train_batch_size": args.per_device_train_batch_size,
        "gradient_accumulation_steps": args.gradient_accumulation_steps,
        "dtype": str(dtype).replace("torch.", ""),
        "target_modules": target_modules,
        "train_data": train_stats,
        "train_encoding": encoded_train_stats,
    }
    if eval_stats is not None and encoded_eval_stats is not None:
        summary["eval_data"] = eval_stats
        summary["eval_encoding"] = encoded_eval_stats
    return summary


def apply_training_arguments_compatibility(
    training_argument_kwargs: dict[str, Any],
    evaluation_value: str,
    training_arguments_cls: Any,
) -> dict[str, Any]:
    parameter_names = inspect.signature(training_arguments_cls.__init__).parameters

    if "evaluation_strategy" in parameter_names:
        training_argument_kwargs["evaluation_strategy"] = evaluation_value
        return training_argument_kwargs

    if "eval_strategy" in parameter_names:
        training_argument_kwargs["eval_strategy"] = evaluation_value
        return training_argument_kwargs

    raise RuntimeError(
        "当前 transformers 版本的 TrainingArguments 不支持 evaluation_strategy 或 eval_strategy。"
    )


def main() -> None:
    args = parse_args()

    train_samples = normalize_chat_samples(args.train_data_path)
    eval_samples: list[ChatSample] | None = None
    if args.eval_data_path.exists():
        eval_samples = normalize_chat_samples(args.eval_data_path)

    train_stats = summarize_samples(train_samples)
    eval_stats = summarize_samples(eval_samples) if eval_samples is not None else None

    if args.dry_run:
        payload = {
            "model_name_or_path": args.model_name_or_path,
            "train_data_path": str(args.train_data_path),
            "eval_data_path": str(args.eval_data_path) if eval_samples is not None else None,
            "output_dir": str(args.output_dir),
            "train_data": train_stats,
            "eval_data": eval_stats,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    import torch
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        BitsAndBytesConfig,
        Trainer,
        TrainingArguments,
        set_seed,
    )

    if not torch.cuda.is_available():
        raise RuntimeError("这个脚本默认面向 NVIDIA CUDA 环境的 4-bit QLoRA 训练。")

    set_seed(args.seed)

    dtype = choose_torch_dtype(args.dtype)
    use_bf16 = dtype == torch.bfloat16
    use_fp16 = dtype == torch.float16

    tokenizer = AutoTokenizer.from_pretrained(
        args.model_name_or_path,
        trust_remote_code=args.trust_remote_code,
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    if tokenizer.pad_token_id is None:
        raise RuntimeError("tokenizer 没有可用的 pad_token，请手动检查底座模型。")
    tokenizer.padding_side = "right"

    train_dataset, encoded_train_stats = encode_samples(
        samples=train_samples,
        tokenizer=tokenizer,
        max_seq_length=args.max_seq_length,
    )
    if len(train_dataset) == 0:
        raise RuntimeError("训练集编码后为空，请检查 chat template 或 max_seq_length 设置。")
    eval_dataset = None
    encoded_eval_stats = None
    if eval_samples is not None:
        eval_dataset, encoded_eval_stats = encode_samples(
            samples=eval_samples,
            tokenizer=tokenizer,
            max_seq_length=args.max_seq_length,
        )
        if len(eval_dataset) == 0:
            eval_dataset = None
            encoded_eval_stats = None
            eval_stats = None

    local_rank = int(os.environ.get("LOCAL_RANK", "0"))
    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=dtype,
    )

    model_kwargs: dict[str, Any] = {
        "quantization_config": quantization_config,
        "trust_remote_code": args.trust_remote_code,
        "torch_dtype": dtype,
        "device_map": {"": local_rank},
    }
    if args.attn_implementation != "auto":
        model_kwargs["attn_implementation"] = args.attn_implementation

    model = AutoModelForCausalLM.from_pretrained(
        args.model_name_or_path,
        **model_kwargs,
    )
    model.config.use_cache = False
    model = prepare_model_for_kbit_training(
        model,
        use_gradient_checkpointing=True,
    )

    target_modules = (
        infer_target_modules(model)
        if args.target_modules == "auto"
        else [item.strip() for item in args.target_modules.split(",") if item.strip()]
    )

    lora_config = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=target_modules,
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    training_argument_kwargs: dict[str, Any] = {
        "output_dir": str(args.output_dir),
        "num_train_epochs": args.num_train_epochs,
        "learning_rate": args.learning_rate,
        "weight_decay": args.weight_decay,
        "warmup_ratio": args.warmup_ratio,
        "per_device_train_batch_size": args.per_device_train_batch_size,
        "per_device_eval_batch_size": args.per_device_eval_batch_size,
        "gradient_accumulation_steps": args.gradient_accumulation_steps,
        "logging_steps": args.logging_steps,
        "save_strategy": "epoch",
        "load_best_model_at_end": eval_dataset is not None,
        "save_total_limit": args.save_total_limit,
        "lr_scheduler_type": "cosine",
        "bf16": use_bf16,
        "fp16": use_fp16,
        "optim": "paged_adamw_8bit",
        "gradient_checkpointing": True,
        "gradient_checkpointing_kwargs": {"use_reentrant": False},
        "remove_unused_columns": False,
        "report_to": "none",
        "logging_dir": str(args.output_dir / "logs"),
        "seed": args.seed,
    }
    training_argument_kwargs = apply_training_arguments_compatibility(
        training_argument_kwargs=training_argument_kwargs,
        evaluation_value="epoch" if eval_dataset is not None else "no",
        training_arguments_cls=TrainingArguments,
    )
    if eval_dataset is not None:
        training_argument_kwargs["metric_for_best_model"] = "eval_loss"
        training_argument_kwargs["greater_is_better"] = False

    training_args = TrainingArguments(**training_argument_kwargs)

    data_collator = SupervisedDataCollator(
        pad_token_id=tokenizer.pad_token_id,
        pad_to_multiple_of=8,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=data_collator,
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary = build_training_summary(
        args=args,
        dtype=dtype,
        target_modules=target_modules,
        train_stats=train_stats,
        eval_stats=eval_stats,
        encoded_train_stats=encoded_train_stats,
        encoded_eval_stats=encoded_eval_stats,
    )
    (args.output_dir / "training_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    trainer.train(resume_from_checkpoint=args.resume_from_checkpoint)
    trainer.save_model()
    tokenizer.save_pretrained(args.output_dir)


if __name__ == "__main__":
    main()
