# Training Helpers

## Prepare SFT Dataset

把现有的：

- `configs/lora_qa_template.jsonl`
- `configs/lora_monologue_template.jsonl`

统一整理成聊天式 `messages` 格式，并按 `source` 切分成 `train / val / test`：

```bash
python3 scripts/prepare_sft_dataset.py
```

默认输出到：

- `data/training/sft/train.jsonl`
- `data/training/sft/val.jsonl`
- `data/training/sft/test.jsonl`
- `data/training/sft/stats.json`

这些文件默认作为本地生成结果使用，不建议直接提交回 Git 仓库。

可选参数示例：

```bash
python3 scripts/prepare_sft_dataset.py \
  --system-prompt "你是峰哥。回答粉丝问题。" \
  --val-ratio 0.1 \
  --test-ratio 0.1 \
  --seed 42
```

## Train QLoRA

先安装统一依赖。

推荐直接用 `uv`：

```bash
uv pip install --python .venv/bin/python -r requirements.txt
```

说明：

- `requirements.txt` 现在已经包含运行和训练所需依赖。
- 其中 `torch` 固定为当前项目验证可用的 `2.10.0+cu128`。
- 如果你的 CUDA 环境不同，请手动修改 [requirements.txt](../requirements.txt) 里的 `torch` 版本或安装源。
- 如果你的环境里只有 `python` 没有 `python3`，把下面命令里的 `python3` 换成 `python` 就行。

先做一次 dry run，确认数据入口没问题：

```bash
python3 scripts/train_qlora.py --dry-run
```

开始训练：

```bash
python3 scripts/train_qlora.py \
  --model-name-or-path Qwen/Qwen2.5-7B-Instruct \
  --train-data-path data/training/sft/train.jsonl \
  --eval-data-path data/training/sft/val.jsonl \
  --output-dir data/training/runs/qwen25-7b-fengge-lora
```

常用调参：

```bash
python3 scripts/train_qlora.py \
  --model-name-or-path Qwen/Qwen2.5-7B-Instruct \
  --max-seq-length 1536 \
  --per-device-train-batch-size 1 \
  --gradient-accumulation-steps 16 \
  --learning-rate 1e-4 \
  --num-train-epochs 4 \
  --output-dir data/training/runs/qwen25-7b-fengge-lora-v2
```

说明：

- 脚本默认使用 4-bit QLoRA，适合单机 NVIDIA GPU。
- 训练数据要求是聊天式 `messages` 格式，和 `data/training/sft/*.jsonl` 一致。
- 默认只训练 assistant 回复部分，system 和 user token 会被 mask 掉。
