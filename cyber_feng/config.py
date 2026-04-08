from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_DIR.parent

DOTENV_PATH = PROJECT_ROOT / ".env"
DB_PATH = PROJECT_ROOT / "data" / "runtime" / "chat_history.db"

APP_TITLE = "赛博峰哥"


@dataclass(frozen=True)
class Settings:
    model_mode: str
    temperature: float
    max_history_messages: int
    system_prompt: str
    local_adapter_path: str
    local_base_model_name: str
    local_max_new_tokens: int
    local_dtype: str
    local_top_p: float
    local_top_k: int
    local_repetition_penalty: float
    local_no_repeat_ngram_size: int


def load_dotenv_file(path: Path) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()

        if not key:
            continue

        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]

        os.environ.setdefault(key, value)


def load_settings() -> Settings:
    load_dotenv_file(DOTENV_PATH)
    return Settings(
        model_mode=os.getenv("CYBER_FENG_MODEL_MODE", "local_transformers_lora").strip(),
        temperature=float(os.getenv("CYBER_FENG_TEMPERATURE", "0.7")),
        max_history_messages=int(os.getenv("CYBER_FENG_MAX_HISTORY_MESSAGES", "12")),
        system_prompt=os.getenv(
            "CYBER_FENG_SYSTEM_PROMPT",
            "你是峰哥。负责回答粉丝问题"
        ).strip(),
        local_adapter_path=os.getenv("CYBER_FENG_LOCAL_ADAPTER_PATH", "").strip(),
        local_base_model_name=os.getenv("CYBER_FENG_LOCAL_BASE_MODEL_NAME", "").strip(),
        local_max_new_tokens=int(os.getenv("CYBER_FENG_LOCAL_MAX_NEW_TOKENS", "192")),
        local_dtype=os.getenv("CYBER_FENG_LOCAL_DTYPE", "auto").strip(),
        local_top_p=float(os.getenv("CYBER_FENG_LOCAL_TOP_P", "0.85")),
        local_top_k=int(os.getenv("CYBER_FENG_LOCAL_TOP_K", "40")),
        local_repetition_penalty=float(
            os.getenv("CYBER_FENG_LOCAL_REPETITION_PENALTY", "1.15")
        ),
        local_no_repeat_ngram_size=int(
            os.getenv("CYBER_FENG_LOCAL_NO_REPEAT_NGRAM_SIZE", "4")
        ),
    )


def build_app_description(settings: Settings) -> str:
    backend_lines = [
        f"- 当前模式：`{settings.model_mode}`",
        f"- 当前底座模型：`{settings.local_base_model_name or '(从 adapter_config 自动解析)'}`",
    ]
    adapter_label = settings.local_adapter_path or "(未配置 adapter 路径)"
    backend_lines.append(f"- 当前 LoRA：`{adapter_label}`")

    return f"""
# {APP_TITLE}

当前版本先确保文本聊天链路稳定：

{chr(10).join(backend_lines)}
""".strip()
