---
language:
- zh
base_model: Qwen/Qwen2.5-7B-Instruct
library_name: peft
pipeline_tag: text-generation
tags:
- lora
- peft
- qlora
- conversational
- chinese
---

# Cyber Feng LoRA

这是一个基于 `Qwen/Qwen2.5-7B-Instruct` 训练的中文 LoRA adapter，用于复现“峰哥式”直播连麦问答风格。

这个仓库只包含 LoRA adapter，不包含底座模型本体。实际运行时需要配合 `Qwen/Qwen2.5-7B-Instruct` 一起加载。

## 项目链接

- GitHub 仓库：`https://github.com/f57y/CYBER_FENG`
- 配套 SFT 数据集：`https://huggingface.co/datasets/yukeef57/cyber-feng-sft`
- 推荐底座模型：`Qwen/Qwen2.5-7B-Instruct`

## 模型概览

- 类型：PEFT LoRA adapter
- 语言：中文
- 训练方式：4-bit QLoRA
- 主要用途：本地娱乐、风格化问答、SFT / LoRA 流程演示

## 如何使用

### 在本项目中加载

```bash
git clone https://github.com/f57y/CYBER_FENG.git
cd CYBER_FENG

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

mkdir -p resources/adapters/fengge-lora
hf download yukeef57/cyber-feng-lora --local-dir resources/adapters/fengge-lora

CYBER_FENG_MODEL_MODE=local_transformers_lora \
CYBER_FENG_LOCAL_ADAPTER_PATH=resources/adapters/fengge-lora \
CYBER_FENG_LOCAL_BASE_MODEL_NAME=Qwen/Qwen2.5-7B-Instruct \
python run_app.py
```

### 在纯 Transformers / PEFT 环境中加载

```python
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

base_model_name = "Qwen/Qwen2.5-7B-Instruct"
adapter_repo_id = "yukeef57/cyber-feng-lora"

tokenizer = AutoTokenizer.from_pretrained(base_model_name)
base_model = AutoModelForCausalLM.from_pretrained(
    base_model_name,
    device_map="auto",
)
model = PeftModel.from_pretrained(base_model, adapter_repo_id)
```

## 训练数据

训练语料来自人工清洗后的中文直播切片 / 转录素材，统一整理成聊天式 `messages` 格式。

- 总样本数：1321
- Train：1113
- Validation：96
- Test：112
- 类型构成：`qa` + `monologue`
- 训练集唯一来源数：40

## 训练配置

以下为本次发布对应的训练摘要：

- Base model：`Qwen/Qwen2.5-7B-Instruct`
- `max_seq_length=1024`
- `num_train_epochs=3.0`
- `learning_rate=2e-4`
- `per_device_train_batch_size=2`
- `gradient_accumulation_steps=8`
- `dtype=bf16`
- `lora_r=64`
- `lora_alpha=128`
- `lora_dropout=0.05`
- target modules：`q_proj`、`k_proj`、`v_proj`、`o_proj`、`gate_proj`、`up_proj`、`down_proj`

## 使用边界与限制

- 这是风格化角色 LoRA，不适合作为通用事实问答模型。
- 数据风格偏直播连麦语境，回答可能带有攻击性、冒犯性或强烈主观判断。
- 该版本主要保留“单轮问答”的直播风格，不强调长上下文连续记忆。
- 项目当前定位为非商业娱乐用途；公开使用前，请自行确认底座模型许可、原始素材来源与二次分发边界。

## 适合谁

- 想直接体验“峰哥味”本地聊天效果的人
- 想研究 LoRA / QLoRA 训练链路的人
- 想在当前版本基础上继续精调风格的人

## 不适合谁

- 需要稳定、温和、通用助手输出的人
- 需要严肃建议、心理支持或高准确率知识问答的人

