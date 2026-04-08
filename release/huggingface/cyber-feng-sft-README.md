---
language:
- zh
pretty_name: Cyber Feng SFT Dataset
tags:
- text
- conversational
- chinese
- sft
- instruction-tuning
task_categories:
- text-generation
size_categories:
- 1K<n<10K
---

# Cyber Feng SFT Dataset

这是 `Cyber Feng` 项目的清洗后 SFT 数据集，主要用于训练“峰哥式”中文问答 / 单口风格 LoRA。

## 项目链接

- GitHub 仓库：`https://github.com/f57y/CYBER_FENG`
- 配套 LoRA 权重：`https://huggingface.co/yukeef57/cyber-feng-lora`
- 推荐底座模型：`Qwen/Qwen2.5-7B-Instruct`

## 数据概览

- 总样本数：1321
- Train：1113
- Validation：96
- Test：112
- 类型：`qa` + `monologue`
- 语言：中文

按当前切分统计：

- Train 唯一来源数：40
- Validation 唯一来源数：5
- Test 唯一来源数：5

## 数据结构

每条样本为一行 JSON，字段结构如下：

```json
{
  "id": "sample-id",
  "source": "source-name",
  "type": "qa",
  "messages": [
    {"role": "system", "content": "系统提示词"},
    {"role": "user", "content": "用户问题"},
    {"role": "assistant", "content": "峰哥风格回答"}
  ]
}
```

说明：

- `type` 目前主要是 `qa` 或 `monologue`
- `messages` 采用聊天式结构，最后一条固定为 `assistant`
- 训练脚本默认只学习 assistant 回复部分

## 文件说明

- `train.jsonl`：训练集
- `val.jsonl`：验证集
- `test.jsonl`：测试集
- `stats.json`：切分与统计摘要

## 数据来源与处理方式

数据来自公开直播切片 / 转录内容的人工筛选与清洗，再统一转成聊天式 SFT 数据。

项目脚本会执行以下步骤：

1. 整理问答类与单口类模板样本
2. 转成统一的 `messages` 结构
3. 按 `source` 切分 `train / val / test`
4. 输出统计信息到 `stats.json`

## 如何下载

```bash
mkdir -p data/training/sft
hf download yukeef57/cyber-feng-sft --repo-type dataset --local-dir data/training/sft
```

## 如何用于训练

```bash
python3 scripts/train_qlora.py \
  --model-name-or-path Qwen/Qwen2.5-7B-Instruct \
  --train-data-path data/training/sft/train.jsonl \
  --eval-data-path data/training/sft/val.jsonl \
  --output-dir data/training/runs/qwen25-7b-fengge-lora
```

## 使用边界与注意事项

- 这不是通用中文对话数据集，而是强风格化角色数据。
- 数据中可能包含攻击性、羞辱式表达、强判断和夸张语气。
- 如果你要做公开产品或商业化场景，建议重新审查数据来源、表达风格、人格风险与分发边界。
- 使用前请自行确认原始素材、底座模型和二次发布行为是否符合你的目标场景要求。
