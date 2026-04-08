from __future__ import annotations

import argparse
import json
import random
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


DEFAULT_SYSTEM_PROMPT = "你是峰哥。"


@dataclass(frozen=True)
class Sample:
    id: str
    source: str
    sample_type: str
    user_text: str
    assistant_text: str

    def as_messages(self, system_prompt: str) -> dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source,
            "type": self.sample_type,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": self.user_text},
                {"role": "assistant", "content": self.assistant_text},
            ],
        }


def load_jsonl(path: Path) -> list[dict[str, Any]]:
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


def normalize_qa_records(records: list[dict[str, Any]]) -> list[Sample]:
    samples: list[Sample] = []
    for index, record in enumerate(records, 1):
        sample_id = require_str(record, "id", f"qa[{index}]")
        source = require_str(record, "source", sample_id)
        sample_type = require_str(record, "type", sample_id)
        if sample_type != "qa":
            raise ValueError(f"{sample_id} 的 type 应为 qa，实际是 {sample_type!r}")

        messages = record.get("messages")
        if not isinstance(messages, list) or len(messages) != 3:
            raise ValueError(f"{sample_id} 的 messages 必须是 3 条消息")

        roles = [message.get("role") for message in messages if isinstance(message, dict)]
        if roles != ["system", "user", "assistant"]:
            raise ValueError(f"{sample_id} 的 roles 必须是 system/user/assistant")

        user_text = require_str(messages[1], "content", sample_id).strip()
        assistant_text = require_str(messages[2], "content", sample_id).strip()

        if not user_text or not assistant_text:
            raise ValueError(f"{sample_id} 的 user/assistant 内容不能为空")

        samples.append(
            Sample(
                id=sample_id,
                source=source,
                sample_type=sample_type,
                user_text=user_text,
                assistant_text=assistant_text,
            )
        )
    return samples


def normalize_monologue_records(records: list[dict[str, Any]]) -> list[Sample]:
    samples: list[Sample] = []
    for index, record in enumerate(records, 1):
        sample_id = require_str(record, "id", f"monologue[{index}]")
        source = require_str(record, "source", sample_id)
        sample_type = require_str(record, "type", sample_id)
        if sample_type != "monologue":
            raise ValueError(f"{sample_id} 的 type 应为 monologue，实际是 {sample_type!r}")

        instruction = require_str(record, "instruction", sample_id).strip()
        output = require_str(record, "output", sample_id).strip()
        if not instruction or not output:
            raise ValueError(f"{sample_id} 的 instruction/output 不能为空")

        samples.append(
            Sample(
                id=sample_id,
                source=source,
                sample_type=sample_type,
                user_text=instruction,
                assistant_text=output,
            )
        )
    return samples


def require_str(obj: dict[str, Any], key: str, sample_id: str) -> str:
    value = obj.get(key)
    if not isinstance(value, str):
        raise ValueError(f"{sample_id} 的 {key} 必须是字符串")
    return value


def dedupe_samples(samples: list[Sample]) -> tuple[list[Sample], int]:
    seen_pairs: set[tuple[str, str]] = set()
    deduped: list[Sample] = []
    duplicates = 0
    for sample in samples:
        signature = (sample.user_text, sample.assistant_text)
        if signature in seen_pairs:
            duplicates += 1
            continue
        seen_pairs.add(signature)
        deduped.append(sample)
    return deduped, duplicates


def split_sources(
    samples: list[Sample],
    val_ratio: float,
    test_ratio: float,
    seed: int,
) -> dict[str, list[Sample]]:
    by_source: dict[str, list[Sample]] = defaultdict(list)
    for sample in samples:
        by_source[sample.source].append(sample)

    sources = list(by_source)
    random.Random(seed).shuffle(sources)

    total_sources = len(sources)
    val_count = min(max(1, round(total_sources * val_ratio)), max(total_sources - 2, 1))
    test_count = min(max(1, round(total_sources * test_ratio)), max(total_sources - val_count - 1, 1))

    test_sources = set(sources[:test_count])
    val_sources = set(sources[test_count:test_count + val_count])
    train_sources = set(sources[test_count + val_count:])

    splits = {"train": [], "val": [], "test": []}
    for source, source_samples in by_source.items():
        if source in test_sources:
            splits["test"].extend(source_samples)
        elif source in val_sources:
            splits["val"].extend(source_samples)
        else:
            splits["train"].extend(source_samples)

    if not train_sources or not splits["train"]:
        raise ValueError("切分后 train 为空，请降低 val/test 比例")

    return splits


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(record, ensure_ascii=False) for record in records]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_stats(
    original_samples: list[Sample],
    deduped_samples: list[Sample],
    splits: dict[str, list[Sample]],
    duplicate_count: int,
    seed: int,
    val_ratio: float,
    test_ratio: float,
) -> dict[str, Any]:
    def split_stats(split_samples: list[Sample]) -> dict[str, Any]:
        type_counts = Counter(sample.sample_type for sample in split_samples)
        return {
            "samples": len(split_samples),
            "unique_sources": len({sample.source for sample in split_samples}),
            "type_counts": dict(type_counts),
            "avg_user_chars": round(
                sum(len(sample.user_text) for sample in split_samples) / len(split_samples),
                1,
            ) if split_samples else 0.0,
            "avg_assistant_chars": round(
                sum(len(sample.assistant_text) for sample in split_samples) / len(split_samples),
                1,
            ) if split_samples else 0.0,
        }

    return {
        "seed": seed,
        "val_ratio": val_ratio,
        "test_ratio": test_ratio,
        "original_samples": len(original_samples),
        "deduped_samples": len(deduped_samples),
        "removed_duplicates": duplicate_count,
        "splits": {name: split_stats(split_samples) for name, split_samples in splits.items()},
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="校验并切分峰哥 SFT 数据集，输出统一的 messages 格式 JSONL。"
    )
    parser.add_argument(
        "--qa-path",
        type=Path,
        default=Path("configs/lora_qa_template.jsonl"),
        help="问答样本 JSONL 路径",
    )
    parser.add_argument(
        "--monologue-path",
        type=Path,
        default=Path("configs/lora_monologue_template.jsonl"),
        help="单口样本 JSONL 路径",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/training/sft"),
        help="输出目录",
    )
    parser.add_argument(
        "--system-prompt",
        default=DEFAULT_SYSTEM_PROMPT,
        help="写入 messages[0] 的 system prompt",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="随机种子",
    )
    parser.add_argument(
        "--val-ratio",
        type=float,
        default=0.1,
        help="验证集 source 占比",
    )
    parser.add_argument(
        "--test-ratio",
        type=float,
        default=0.1,
        help="测试集 source 占比",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.val_ratio <= 0 or args.test_ratio <= 0:
        raise ValueError("val/test 比例必须大于 0")
    if args.val_ratio + args.test_ratio >= 1:
        raise ValueError("val_ratio + test_ratio 必须小于 1")

    qa_samples = normalize_qa_records(load_jsonl(args.qa_path))
    monologue_samples = normalize_monologue_records(load_jsonl(args.monologue_path))

    original_samples = [*qa_samples, *monologue_samples]
    deduped_samples, duplicate_count = dedupe_samples(original_samples)
    splits = split_sources(
        samples=deduped_samples,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio,
        seed=args.seed,
    )

    for split_name, split_samples in splits.items():
        records = [sample.as_messages(args.system_prompt) for sample in split_samples]
        write_jsonl(args.output_dir / f"{split_name}.jsonl", records)

    stats = build_stats(
        original_samples=original_samples,
        deduped_samples=deduped_samples,
        splits=splits,
        duplicate_count=duplicate_count,
        seed=args.seed,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio,
    )
    stats_path = args.output_dir / "stats.json"
    stats_path.write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
