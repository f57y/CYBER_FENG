<div align="center">
  <h1>赛博峰哥</h1>
  <p><strong>Cyber Feng</strong></p>
  <p>【有的人活着，他已经死了；有的人死了，他还活着。】</p>
  <p>
    <a href="./LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License"></a>
    <a href="https://huggingface.co/yukeef57/cyber-feng-lora"><img src="https://img.shields.io/badge/HuggingFace-LoRA-orange" alt="LoRA"></a>
    <a href="https://huggingface.co/datasets/yukeef57/cyber-feng-sft"><img src="https://img.shields.io/badge/HuggingFace-SFT%20Dataset-blue" alt="SFT Dataset"></a>
  </p>
  <p>
    <a href="#quick-look">一眼看懂</a> ·
    <a href="#samples">效果示例</a> ·
    <a href="#resources">下载资源</a> ·
    <a href="#paths">推荐使用路径</a> ·
    <a href="#project-overview">项目简介</a>
  </p>
</div>

---

<a id="quick-look"></a>
## 一眼看懂

| 项目 | 说明 |
| --- | --- |
| 项目定位 | 本地 Web 聊天界面 + 本地底座模型 + LoRA 推理 + 本地 QLoRA 数据整理与训练脚本 |
| 推荐底座模型 | `Qwen/Qwen2.5-7B-Instruct` |
| 已发布资源 | GitHub 代码仓库、Hugging Face LoRA、Hugging Face SFT Dataset |
| 适合人群 | 只想直接体验的人、想复现训练流程的人、想继续精调风格的人 |

> [!WARNING]
> 本项目仅做娱乐用途，不做任何商业化，不做任何盈利行为。

<a id="samples"></a>
## 效果示例

> **示例 1**
>
> **用户**
> 峰哥啊，我在大城市打工四年了，工资不高，存款也没多少，天天忙得像狗一样，我是不是这辈子也就这样了？
>
> **峰哥**
> 你这不就是底层人吗？底层人有什么不一样呢？底层人就是工作努力，工资不高，存款不多，生活压力大，天天累得跟狗似的。你以为底层人还能干啥？你连大城市都待了四年，还在这儿问这辈子能不能翻身，那你还指望啥？真要说，底层人就是工资低，存款少，累得跟狗，但至少生活正常，每天上班下班，日子过得去就行。这东西你真想变，唯一办法就是出去创业，干点副业，或者找点别的出路，而不是天天在这儿等别人给你开窍。

---

> **示例 2**
>
> **用户**
> 峰哥啊，我都快三十了，没钱、没对象、没本事，感觉自己像个废物，这种状态还有机会翻身吗？
>
> **峰哥**
> 你这种状态，基本没翻身的机会了。三十了还单身，说明你不是没机会，是你自己给机会拦住了。很多人三十都没对象，不是真的没可能，是觉得自己没魅力、没条件、没表现机会，然后把机会都自我封死了。你要是真着急，就先把自己能展示的都展示出来，别总憋在自己那，等别人主动来发现你。没对象，就多出去混混，多认识人，多尝试约会。没钱，就先把自己能挣的都挣出来，别老拿环境当借口。三十了，机会比以前少，但还不至于完全没机会。

---

> **示例 3**
>
> **用户**
> 峰哥啊，我谈恋爱总是特别卑微，明知道对方不尊重我，我还是舍不得走，是不是因为我太缺爱了？
>
> **峰哥**
> 你这个不是缺爱，是太怕被抛弃。你明知道对方不尊重你，还死守着这段关系，根本不是真爱，是在害怕自己没下家。你之所以觉得卑微，不是因为对方好，是因为你自己心里清楚，一旦分手，你真没人要。所以很多卑微恋情不是爱情，是自欺欺人的挽留。你越舍不得走，越说明你不是在谈恋爱，是在给自己找借口。


## 友情提示

> [!NOTE]
> 数据来源：B站 up 主 [雅典大学峰主任](https://space.bilibili.com/3690981457136435?spm_id_from=333.788.upinfo.head.click)
>
> 99.9%的代码都是在Codex的辅助下完成的（其实是我辅助Codex）

### 当前项目缺点

- 训练数据太少，总共1113条，想要更像峰哥，需要更大量的高质量数据，不只是直播切片。可以从峰哥的访谈/视频里提取
- 模型本身能力不强，目前是Qwen2.5-7B的本地模型，有能力者可以部署32B的模型，再进行微调训练。可能效果更好，但是训练的成本也更高
- 可以参考：https://github.com/YixiaJack/feng-ge-skill，峰哥.skill里的内容，对该项目做进一步的优化，更像峰哥。我的提示词也是参考这个skill写的。
- 后期可以加入语音输出，让模型学习峰哥的音色/语气/语调，这样我们就可以每天听着峰哥的声音入眠了。😊
- 这次训练数据主要是峰哥羞辱B友了，导致这个版本的峰哥攻击性比较强（喜欢被骂的有福了）
- 如果有B友想多问问性压抑相关的，好事相关的，可以多找点类似的训练数据来调教峰哥
- 每一次重新启动都需要加载推理模型权重，比较慢。跟本地的显卡性能相关。
- 因为主要想保留直播问答时的风格，每个B友问的问题都是独立的，所以没有上下文。我们每次问的问题峰哥回答完就忘了
- CYBER_FENG_TEMPERATURE经过我的测试，大概是0.72左右比较像峰哥。太低了就会一直重复，太高了就不像峰哥了。但是0.72的TEMPERATURE也会导致同一个问题的可复现能力较差。B友们也可以自己尝试调参看看效果

### 报错了怎么办

> [!TIP]
> 有问题问AI，无论是部署的问题，推理的问题还是训练的问题，将报错发给AI即可。有条件的用Claude Code/Codex。没有条件的用免费的Trae，要养成独立解决问题的能力。💪💪💪

<a id="prompts"></a>
## 测试问题

<details>
<summary><strong>苦大仇深型</strong></summary>

- 峰哥啊，我在大城市打工四年了，工资不高，存款也没多少，天天忙得像狗一样，我是不是这辈子也就这样了？

- 峰哥啊，我现在做销售，天天陪笑脸，心里特别烦，但又不敢辞职，我到底是在熬阶段，还是在浪费人生？

- 峰哥啊，我都快三十了，没钱、没对象、没本事，感觉自己像个废物，这种状态还有机会翻身吗？

- 峰哥啊，我一直觉得自己不是不努力，是努力了也没结果，为什么别人一发力就有效果，我一发力就像打水漂？

- 峰哥啊，我在工厂上班，每天两点一线，感觉人都麻了。我知道这样下去不行，但下班以后又什么都不想干，怎么办？

- 峰哥啊，我想回老家，至少压力没那么大，但又怕一回去这辈子就彻底没机会了，我到底该不该回去？

- 峰哥啊，我爸妈总说我眼高手低，可我真不想一辈子干没前途的活，这到底是我太飘了，还是他们把我看死了？

- 峰哥啊，我现在特别想做自媒体，因为我真的不想打工了，但我又怀疑自己是不是在逃避现实，你怎么看？

- 峰哥啊，我发了几个视频，播放量特别差，我有点怀疑自己根本不是这块料，还要不要继续做？

- 峰哥啊，我总是特别在意别人怎么看我，发个朋友圈都要想半天，做事也怕丢脸，这种人是不是天生就做不成事？

- 峰哥啊，我谈恋爱总是特别卑微，明知道对方不尊重我，我还是舍不得走，是不是因为我太缺爱了？

- 峰哥啊，我现在最大的痛苦不是穷，是看不到希望。每天都活着，但不知道活着到底是为了什么，这种时候该怎么撑过去？

</details>

<details>
<summary><strong>男女关系型</strong></summary>

- 峰哥啊，我条件一般，长相一般，收入也一般，是不是这种男人在感情里天然就没有选择权？

- 峰哥啊，我发现自己一谈恋爱就失去自我，生活重心全放对方身上，这是不是很多男人都会犯的错？

- 峰哥啊，一个女生如果真的喜欢你，会有哪些表现？还是说男人总是在自作多情？

- 峰哥啊，我跟她在一起两年了，但我越来越觉得她看不起我，这种关系还有必要硬撑吗？

- 峰哥啊，我特别怕失去她，所以很多不爽都忍着不说，结果越忍越憋屈，这到底是在爱还是在讨好？

- 峰哥啊，为什么有些女生明明不想跟你认真在一起，却又一直吊着你，不拒绝也不答应？

- 峰哥啊，我分手半年了，嘴上说放下了，但一看到她朋友圈还是难受，这到底是还爱，还是不甘心？

- 峰哥啊，我对象总拿我跟别的男人比，说别人更会赚钱、更会来事，这种话我该怎么接？

- 峰哥啊，我喜欢的女生条件比我好很多，我总觉得自己配不上她，这种自卑感怎么破？

- 峰哥啊，我谈了几段恋爱，最后发现自己每次都在重复同一种失败，是我运气差，还是我这个人本身有问题？

</details>

<a id="resources"></a>
## 可下载资源

| 资源 | 适合谁 | 链接 / ID |
| --- | --- | --- |
| GitHub 仓库 | 想看代码、流程和配置方式的用户 | [CYBER_FENG](https://github.com/f57y/CYBER_FENG.git) |
| 训练好的 LoRA 权重 | 适合想直接体验“峰哥”的用户 | [LoRA 仓库](https://huggingface.co/yukeef57/cyber-feng-lora) / `yukeef57/cyber-feng-lora` |
| 清洗好的 SFT 数据 | 适合想自己跑一遍训练过程的用户 | [SFT 数据集](https://huggingface.co/datasets/yukeef57/cyber-feng-sft) / `yukeef57/cyber-feng-sft` |
| 推荐底座模型 | 当前推荐配套底座 | `Qwen/Qwen2.5-7B-Instruct` |

- 后续更高质量的数据版本：适合想继续精调风格的用户

## 诚实边界

> [!IMPORTANT]
> - 这个仓库主要公开的是代码、流程和配置方式，不是把所有素材打包塞进 GitHub。
> - GitHub 仓库不再直接提交切分后的 `data/training/sft/*.jsonl`；想用完整训练集，请去 Hugging Face 下载，或者自己运行脚本生成。
> - 本地聊天记录默认会写进 `data/runtime/chat_history.db`；如果你不想保留，删掉这个文件即可。
> - LoRA 权重、SFT 数据集和第三方底座模型的许可边界，请以各自页面和原始来源说明为准。

<a id="paths"></a>
## 推荐使用路径

以下主命令默认以 Linux / WSL2 终端为例。

平台说明：

| 平台 / 项目 | 说明 |
| --- | --- |
| Linux / WSL2 | 下面三条路线的命令可以直接参考 |
| Windows | 可以运行，但命令需要换成 PowerShell 写法，并且仍然要求 NVIDIA CUDA 环境 |
| macOS | 由于CUDA的限制，当前版本不能直接运行本地 LoRA 推理，也不能直接运行训练 |
| `python` / `python3` | 如果你的环境里 `python` 已经指向 Python 3，可以直接用 `python`；如果只有 `python3`，把下面示例里的 `python` 替换成 `python3` 就行 |
| Hugging Face 下载 | 下面涉及 Hugging Face 下载的路线默认使用 `hf` 命令；如果你的环境里还没有它，先执行 `pip install "huggingface-hub>=0.34.0,<1.0"` |

<details>
<summary><strong>Windows PowerShell 快速启动参考</strong></summary>

如果你是原生 Windows 用户，下面按路线 1、2、3 分开给出 PowerShell 写法。

#### Windows 路线 1：直接加载已发布的权重

适合谁：
只想尽快跑起来，直接体验“峰哥”。

```powershell
# 第 1 步：把项目下载到本地
git clone https://github.com/f57y/CYBER_FENG.git
cd CYBER_FENG

# 第 2 步：创建 Python 虚拟环境，并进入这个项目专用环境
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 第 3 步：安装项目运行和训练所需依赖
pip install -r requirements.txt

# 第 4 步：创建本地权重目录，准备放你下载的 LoRA 权重
New-Item -ItemType Directory -Force resources\adapters\fengge-lora

# 第 5 步：从 Hugging Face 下载发布的 LoRA 权重仓库内容
hf download yukeef57/cyber-feng-lora --local-dir resources\adapters\fengge-lora

# 第 6 步：复制配置模板，生成你自己的 .env 配置文件
Copy-Item .env_example .env

# 第 7 步：临时指定本次运行要使用的模式、权重路径和底座模型
$env:CYBER_FENG_MODEL_MODE="local_transformers_lora"
$env:CYBER_FENG_LOCAL_ADAPTER_PATH=(Resolve-Path "resources\adapters\fengge-lora").Path
$env:CYBER_FENG_LOCAL_BASE_MODEL_NAME="Qwen/Qwen2.5-7B-Instruct"

# 第 8 步：启动 Web 聊天界面
python run_app.py
```

#### Windows 路线 2：下载发布的训练数据，自己训练

适合谁：
想自己体验训练过程，但不想从原始素材开始清洗。

```powershell
# 第 1 步：把项目下载到本地
git clone https://github.com/f57y/CYBER_FENG.git
cd CYBER_FENG

# 第 2 步：创建 Python 虚拟环境，并进入这个项目专用环境
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 第 3 步：安装项目运行和训练所需依赖
pip install -r requirements.txt

# 第 4 步：创建训练数据目录
New-Item -ItemType Directory -Force data\training\sft

# 第 5 步：从 Hugging Face 下载发布的清洗后训练数据
hf download yukeef57/cyber-feng-sft --repo-type dataset --local-dir data\training\sft

# 第 6 步：先检查数据和训练参数是否正常
python scripts\train_qlora.py --dry-run

# 第 7 步：启动训练
python scripts\train_qlora.py `
  --model-name-or-path Qwen/Qwen2.5-7B-Instruct `
  --train-data-path data/training/sft/train.jsonl `
  --eval-data-path data/training/sft/val.jsonl `
  --output-dir data/training/runs/qwen25-7b-fengge-lora

# 第 8 步：把训练输出的 LoRA 权重作为当前启动权重
$env:CYBER_FENG_MODEL_MODE="local_transformers_lora"
$env:CYBER_FENG_LOCAL_ADAPTER_PATH=(Resolve-Path "data\training\runs\qwen25-7b-fengge-lora").Path
$env:CYBER_FENG_LOCAL_BASE_MODEL_NAME="Qwen/Qwen2.5-7B-Instruct"

# 第 9 步：启动 Web 聊天界面
python run_app.py
```

#### Windows 路线 3：自己整理数据，再训练

适合谁：
愿意自己提取更高质量素材，长期迭代风格效果。

```powershell
# 第 1 步：把项目下载到本地
git clone https://github.com/f57y/CYBER_FENG.git
cd CYBER_FENG

# 第 2 步：创建 Python 虚拟环境，并进入这个项目专用环境
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 第 3 步：安装项目运行和训练所需依赖
pip install -r requirements.txt

# 第 4 步：先手动编辑这两个模板文件，填入你整理好的样本
# configs\lora_qa_template.jsonl
# configs\lora_monologue_template.jsonl

# 第 5 步：把清洗后的样本转成可直接训练的数据
python scripts\prepare_sft_dataset.py

# 第 6 步：检查切分结果
Get-Content data\training\sft\stats.json

# 第 7 步：先检查训练参数是否正常
python scripts\train_qlora.py --dry-run

# 第 8 步：启动训练
python scripts\train_qlora.py `
  --model-name-or-path Qwen/Qwen2.5-7B-Instruct `
  --train-data-path data/training/sft/train.jsonl `
  --eval-data-path data/training/sft/val.jsonl `
  --output-dir data/training/runs/qwen25-7b-fengge-lora

# 第 9 步：把训练输出的 LoRA 权重作为当前启动权重
$env:CYBER_FENG_MODEL_MODE="local_transformers_lora"
$env:CYBER_FENG_LOCAL_ADAPTER_PATH=(Resolve-Path "data\training\runs\qwen25-7b-fengge-lora").Path
$env:CYBER_FENG_LOCAL_BASE_MODEL_NAME="Qwen/Qwen2.5-7B-Instruct"

# 第 10 步：启动 Web 聊天界面
python run_app.py
```

</details>


### 路线 1：我就想直接用“峰哥”

> [!TIP]
> 适合谁：完全不想自己训练，只想把项目拉下来、下载你已经发布好的权重，然后尽快在自己电脑上跑起来。

快速启动命令：

```bash
git clone https://github.com/f57y/CYBER_FENG.git
cd CYBER_FENG

# 1) 安装项目依赖
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2) 下载你发布的权重文件
mkdir -p resources/adapters/fengge-lora
hf download yukeef57/cyber-feng-lora --local-dir resources/adapters/fengge-lora

# 3) 加载权重并启动推理
CYBER_FENG_MODEL_MODE=local_transformers_lora \
CYBER_FENG_LOCAL_ADAPTER_PATH=resources/adapters/fengge-lora \
CYBER_FENG_LOCAL_BASE_MODEL_NAME=Qwen/Qwen2.5-7B-Instruct \
python run_app.py
```

使用说明：
这条路线默认目标就是“直接得到峰哥味效果”。用户不需要理解 API、网关或第三方模型服务，只要本机有可用的 NVIDIA CUDA 环境，并且已经下载好发布的 LoRA 权重，就可以直接启动。这个项目最终实际加载的是“底座模型 + LoRA adapter”，而不是一个通用聊天 API。

### 路线 2：我想体验完整训练过程，但不想自己洗数据

> [!TIP]
> 适合谁：想自己体验“下载现成数据 -> 启动训练 -> 加载自己训出来的权重 -> 启动应用”这一整套流程的人。

快速启动命令：

```bash
git clone https://github.com/f57y/CYBER_FENG.git
cd CYBER_FENG

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 下载发布的清洗后训练数据
mkdir -p data/training/sft
hf download yukeef57/cyber-feng-sft --repo-type dataset --local-dir data/training/sft

# 先检查数据和参数
python3 scripts/train_qlora.py --dry-run

# 启动训练
python3 scripts/train_qlora.py \
  --model-name-or-path Qwen/Qwen2.5-7B-Instruct \
  --train-data-path data/training/sft/train.jsonl \
  --eval-data-path data/training/sft/val.jsonl \
  --output-dir data/training/runs/qwen25-7b-fengge-lora

# 训练完成后直接加载你自己训出来的权重
CYBER_FENG_MODEL_MODE=local_transformers_lora \
CYBER_FENG_LOCAL_ADAPTER_PATH=data/training/runs/qwen25-7b-fengge-lora \
CYBER_FENG_LOCAL_BASE_MODEL_NAME=Qwen/Qwen2.5-7B-Instruct \
python run_app.py
```

使用说明：
这条路线和路线 1 的区别，只是把“下载权重”改成了“下载训练数据并自己训练”。当前训练脚本最常调的参数有：

- `--max-seq-length`：默认 `1024`，越大越吃显存
- `--num-train-epochs`：默认 `3.0`，想多学几轮可调高
- `--learning-rate`：默认 `2e-4`
- `--per-device-train-batch-size`：每张卡的 batch size，显存越小越要降
- `--gradient-accumulation-steps`：显存不够时可以调高，等效增大总 batch
- `--lora-r` / `--lora-alpha` / `--lora-dropout`：LoRA 核心参数

按当前发布出去的这套数据规模来看，`train.jsonl` 大约 1113 条、`val.jsonl` 大约 96 条。下面这些训练时长是基于这份数据规模做的经验性估计，不是严格实测：

- 12GB 显存：建议 `batch_size=1`、`gradient_accumulation_steps=16`，大约 6 到 12 小时
- 16GB 显存：建议 `batch_size=1` 或 `2`、`gradient_accumulation_steps=8~16`，大约 3 到 8 小时
- 24GB 显存：建议 `batch_size=2`、`gradient_accumulation_steps=8`，大约 2 到 6 小时
- 48GB 显存及以上：可以更激进地提 batch，通常 1 到 3 小时能跑完一轮基础实验

如果你只是想体验训练过程，建议先不要急着上 32B，先用 7B 把全流程跑通。

### 路线 3：我愿意自己提取高质量训练数据，再训练

> [!TIP]
> 适合谁：已经不满足于现成数据，准备自己从直播回放、字幕、转录文本里提取更高质量样本，然后做长期迭代的人。

快速启动命令：

```bash
git clone https://github.com/f57y/CYBER_FENG.git
cd CYBER_FENG

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 第一步：手动把样本整理进模板
# configs/lora_qa_template.jsonl
# configs/lora_monologue_template.jsonl

# 第二步：把清洗后的样本转成可直接训练的数据
python3 scripts/prepare_sft_dataset.py

# 第三步：检查切分结果
cat data/training/sft/stats.json

# 第四步：启动训练
python3 scripts/train_qlora.py --dry-run
python3 scripts/train_qlora.py \
  --model-name-or-path Qwen/Qwen2.5-7B-Instruct \
  --train-data-path data/training/sft/train.jsonl \
  --eval-data-path data/training/sft/val.jsonl \
  --output-dir data/training/runs/qwen25-7b-fengge-lora

# 第五步：加载自己训练出的权重并启动
CYBER_FENG_MODEL_MODE=local_transformers_lora \
CYBER_FENG_LOCAL_ADAPTER_PATH=data/training/runs/qwen25-7b-fengge-lora \
CYBER_FENG_LOCAL_BASE_MODEL_NAME=Qwen/Qwen2.5-7B-Instruct \
python run_app.py
```

使用说明：
这条路线分三步理解最清楚：

1. 提取原始素材  
从直播录屏、字幕、自动转录文本、手工笔记里挑出真正有“峰哥味”的片段。

2. 清洗并整理成模板  
问答类内容放进 [configs/lora_qa_template.jsonl](configs/lora_qa_template.jsonl)，单口观点类内容放进 [configs/lora_monologue_template.jsonl](configs/lora_monologue_template.jsonl)。整理原则见 [configs/lora_data_notes.md](configs/lora_data_notes.md)。

3. 转成训练集并启动训练  
运行 `python3 scripts/prepare_sft_dataset.py` 后，脚本会自动校验结构、去重、按 `source` 切分 `train / val / test`，并统一转成聊天式 `messages` 格式。得到的 `data/training/sft/*.jsonl` 就是可直接训练的数据。

如果你准备长期做这个项目，真正拉开效果差距的通常不是多跑几轮训练，而是原始素材提取和数据清洗质量。

<a id="project-overview"></a>
## 项目简介

这个仓库目前包含三条主线能力：

- 本地 Web 聊天界面
- 本地底座模型 + LoRA 权重推理
- 本地 QLoRA 数据整理与训练脚本

如果你现在只是想快速验证“本地人格聊天”这条链路，直接启动 Web 聊天即可；如果你已经开始整理训练语料，也可以继续用仓库里的脚本准备 SFT 数据并训练 LoRA 适配器。

## 功能特性

- 基于 Gradio 的本地聊天页面
- 支持本地 `Transformers + LoRA` 推理模式
- 支持通过 `.env` 配置 LoRA 路径、底座模型、温度等参数
- 使用 SQLite 持久化聊天记录
- 提供问答式与单口式两类 `JSONL` 数据模板
- 提供 SFT 数据校验、去重、按 `source` 切分脚本
- 提供最小可用的 QLoRA 训练脚本

## 项目结构

```text
Cyber_Feng/
├── cyber_feng/
│   ├── app.py
│   ├── backend.py
│   ├── config.py
│   ├── storage.py
│   └── __init__.py
├── configs/
│   ├── lora_qa_template.jsonl
│   ├── lora_monologue_template.jsonl
│   └── lora_data_notes.md
├── data/
│   └── training/
│       └── sft/              # 运行脚本后生成 / 从 HF 下载
├── scripts/
│   ├── prepare_sft_dataset.py
│   ├── train_qlora.py
│   └── README.md
├── .env_example
├── run_app.py
├── requirements.txt
└── README.md
```

## 环境要求

- Python 3.10+
- 一套可用的本地 CUDA + Transformers + LoRA 环境

## 安装

先创建虚拟环境并安装统一依赖：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

说明：

- `requirements.txt` 已经包含运行和训练所需依赖。
- 其中 `torch` 固定为当前项目验证可用的 `2.10.0+cu128`。
- 如果你的 CUDA 环境不同，请修改 [requirements.txt](requirements.txt) 中的 `torch` 版本或安装源。
- 如果你的环境里 `python` 就是 Python 3，也可以把这里的 `python3` 换成 `python`。
- 更细的训练安装说明见 [scripts/README.md](scripts/README.md)。

## 配置说明

先复制根目录示例文件：

```bash
cp .env_example .env
```

然后按你的路线修改 `.env`。优先参考 [.env_example](.env_example)。

最小可用示例：

```env
CYBER_FENG_MODEL_MODE=local_transformers_lora
CYBER_FENG_TEMPERATURE=0.7
CYBER_FENG_MAX_HISTORY_MESSAGES=12
CYBER_FENG_SYSTEM_PROMPT=你是峰哥。回答粉丝问题。
CYBER_FENG_LOCAL_ADAPTER_PATH=/absolute/path/to/your/lora_adapter
CYBER_FENG_LOCAL_BASE_MODEL_NAME=Qwen/Qwen2.5-7B-Instruct
```

常用配置项：

| 变量 | 说明 |
| --- | --- |
| `CYBER_FENG_MODEL_MODE` | 当前固定使用 `local_transformers_lora` |
| `CYBER_FENG_TEMPERATURE` | 采样温度 |
| `CYBER_FENG_MAX_HISTORY_MESSAGES` | 发送给模型的最大历史消息数 |
| `CYBER_FENG_SYSTEM_PROMPT` | 系统提示词 |
| `CYBER_FENG_LOCAL_ADAPTER_PATH` | 本地 LoRA adapter 输出目录 |
| `CYBER_FENG_LOCAL_BASE_MODEL_NAME` | 本地推理时可显式指定底座模型 |

## 运行模式说明

### `local_transformers_lora`

用于本地加载底座模型和已训练好的 LoRA adapter 进行推理。

启用这个模式时，需要至少配置：

```env
CYBER_FENG_MODEL_MODE=local_transformers_lora
CYBER_FENG_LOCAL_ADAPTER_PATH=/path/to/adapter
```

如果 `adapter_config.json` 中能解析到底座模型路径，则 `CYBER_FENG_LOCAL_BASE_MODEL_NAME` 可以留空。

## 当前限制

- 当前只支持文本输入
- 当前没有自动转录、自动清洗和自动评测流程
- 本地 LoRA 推理模式默认面向可用的 CUDA 环境
- 训练脚本是“最小可用”版本，适合单机单卡起步验证

## Roadmap

- 持续整理高质量训练数据
- 补充评测题集和对比基线
- 对比提示词版与 LoRA 版效果
- 接入语音链路与数字人前端能力

<a id="docs"></a>
## 相关文档

- [scripts/README.md](scripts/README.md)
- [release/huggingface/cyber-feng-lora-README.md](release/huggingface/cyber-feng-lora-README.md)
- [release/huggingface/cyber-feng-sft-README.md](release/huggingface/cyber-feng-sft-README.md)
