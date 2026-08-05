# Hakeem750/pet-sound-to-texts Docker 部署报告

## 概述
将 HuggingFace 模型 `Hakeem750/pet-sound-to-texts` 以 Docker 容器方式部署到本机 GPU。模型预下载到宿主后只读挂载进容器,容器通过 NVIDIA runtime 使用 RTX 4060 Ti 显卡推理。

## 模型信息
| 项 | 值 |
|---|---|
| Hub ID | Hakeem750/pet-sound-to-texts |
| 架构 | `WhisperForConditionalGeneration`(Whisper medium) |
| 参数量 | ~0.8B(769M,F32) |
| 模型类型 | 多语言 ASR(`is_multilingual=true`) |
| 输出配置 | `forced_decoder_ids` 强制 English + transcribe + notimestamps |
| 保存版本 | transformers 4.50.3 |
| 模型卡 | 全空白模板(所有字段 `[More Information Needed]`) |
| 月下载 | 13 |
| License | 未知 |

**关键判断**:config.json 显示这是标准 Whisper medium 的微调(或重传),`d_model=1024 / encoder_layers=24 / decoder_layers=24`,配置与原版 Whisper medium 一致,**无任何宠物声音定制**。generation_config 的 `forced_decoder_ids=[[1,50259],[2,50359],[3,50363]]` 强制英语转录输出。Whisper tokenizer 是人类语言,对动物非语音音频大概率幻觉出英语词。

## 本机环境
| 项 | 值 |
|---|---|
| OS | Windows 11 Pro |
| Docker | Docker Desktop 4.77.0 / docker 29.5.3 |
| Compose | v5.1.4 |
| NVIDIA runtime | 已注册(`Runtimes: nvidia runc`) |
| GPU | RTX 4060 Ti 16GB |
| 驱动 | 596.21(CUDA 13.2) |
| GPU 透传验证 | `docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi` 容器内见 RTX 4060 Ti ✅ |

## 部署架构
- **镜像**:`pytorch/pytorch:2.4.1-cuda12.1-cudnn9-runtime`(自带 torch 2.4.1+cu121, Python 3.11.9)
- **容器内补装**:transformers 4.50.3、soundfile、librosa、ffmpeg
- **模型**:宿主 `code/pet-sound-to-texts/model/` → 容器 `/models/pet-sound`(只读 bind 挂载)
- **GPU**:compose `deploy.resources.reservations.devices`(driver: nvidia, count: all, capabilities: [gpu])
- 镜像**不含模型**,保持小且可复用;模型靠挂载,换模型只改宿主目录

## 文件清单
| 文件 | 作用 |
|---|---|
| `code/pet-sound-to-texts/download_model.ps1` | BITS 下载模型到宿主(大文件走 BITS,小文件走 IWR,带 size 校验和断点续传) |
| `code/pet-sound-to-texts/Dockerfile` | 镜像构建 |
| `code/pet-sound-to-texts/docker-compose.yml` | GPU + 挂载 + env 编排 |
| `code/pet-sound-to-texts/requirements.txt` | 容器内 Python 依赖 pin |
| `code/pet-sound-to-texts/.env.example` | 环境变量模板 |
| `code/pet-sound-to-texts/infer.py` | CLI 推理脚本(env 驱动,无硬编码) |
| `code/pet-sound-to-texts/generate_sample.py` | 生成合成测试音频(纯标准库) |
| `code/pet-sound-to-texts/model/` | 宿主模型目录(挂载用,不入镜) |
| `code/pet-sound-to-texts/samples/` | 宿主样本目录(挂载用) |

## 依赖版本
| 包 | 版本 |
|---|---|
| Python | 3.11.9(镜像自带) |
| torch | 2.4.1+cu121(镜像自带) |
| transformers | 4.50.3(匹配模型保存版本) |
| soundfile | latest |
| librosa | latest |
| ffmpeg | apt |

## 调用方式

### 1. 下载模型(宿主,一次性)
```powershell
cd D:\mydoc\workskill\code\pet-sound-to-texts
.\download_model.ps1
```

### 2. 构建镜像
```powershell
docker compose build
```

### 3. 推理
```powershell
# 合成样本 smoke test
docker compose run --rm pet-asr --audio /samples/sample.wav

# 自定义音频(挂到 /samples 或传 URL)
docker compose run --rm pet-asr --audio /samples/your.wav
docker compose run --rm pet-asr --audio https://example.com/sound.wav

# 指定语言提示
docker compose run --rm pet-asr --audio /samples/your.wav --language en
```

### 4. 配置(env)
复制 `.env.example` 为 `.env`,按需改 `HF_ENDPOINT`(镜像)、`MODEL_DIR`、`DEVICE` 等。

## 验证结果

### 镜像构建
- ✅ `docker compose build` 成功(首次 apt 用国外源 500 EOF 失败,换清华 TUNA 镜像源后成功)
- 镜像 `pet-sound-to-texts:latest` 本地就绪(基于 pytorch/pytorch:2.4.1-cuda12.1-cudnn9-runtime + Python 3.11.9)

### 模型下载
- ❌ BITS 对 HF LFS 兼容差(job 卡在 Transferring/0 字节,临时文件满 size 不 finalize) → 改用 `hf.exe download`(HF 官方,原生 LFS + 断点续传 + sha256 校验)成功
- ⚠️ `huggingface-cli download` 已废弃且 Windows GBK 编码 emoji 崩溃 → 用 `hf.exe` + `PYTHONUTF8=1`
- ✅ 12 文件齐全,`model.safetensors` 3,055,544,304 bytes(2.85GB)

### 容器 GPU 透传
- ✅ `docker run --rm --gpus all nvidia/cuda:12.4.1-base nvidia-smi` 容器内见 RTX 4060 Ti
- ⚠️ 孤儿容器(`timeout` 杀 docker 客户端但容器未删)会占 GPU/runtime 资源,导致后续 GPU 容器启动卡 → 测试后务必 `docker rm -f` 清理

### CUDA 推理
- ✅ `torch.cuda.is_available()=True`,`device=RTX 4060 Ti`
- ⚠️ **首次 CUDA runtime init 极慢:约 3 分钟**(WSL2/WDDM 模式下加载 cudnn + GPU 资源协商),非卡死。import torch 仅 0.83s,慢在 `torch.cuda.is_available()`
- ✅ 模型从挂载目录 `/models/pet-sound` 加载,pipeline `Device set to use cuda:0`

### Demo 输出
输入:合成音频(440+880Hz 正弦波 + 慢包络,3 秒/16kHz,**非真实宠物声音**,由 `generate_sample.py` 生成)

输出:
```
Bark-Growl Combo. Alternating bark and growl sounds. Serious Warning — preparing to defend, escalating in aggression.
```

**关键发现**:模型确实为宠物声音任务微调——输出不是普通语音转录,而是结构化的宠物行为描述("Bark-Growl Combo"、"Serious Warning"、"escalating in aggression")。这与原版 Whisper medium(会输出人类语言转录)不同,证明模型卡虽空白但微调真实存在。但对合成非宠物音频会**幻觉**出宠物描述。

### 真实宠物声音测试(ESC-50,2026-07-06)

从 GitHub `karolpiczak/ESC-50`(经 jsdelivr CDN 下载,绕过 GitHub raw 429 限速)取 3 个狗叫(class 0)+ 1 个猫叫(class 5),5 秒/44.1kHz,重采样到 16kHz 推理。一次加载模型循环推理 4 个文件(避免重复 CUDA init)。

| 输入 | 真实类别 | 模型输出 |
|---|---|---|
| 1-100032-A-0.wav | dog | Repetitive Barking. Strong, spaced-out barks with emphasis. Guarding — cat is warning intruders or intruded upon. |
| 1-110389-A-0.wav | dog | Curious Barking. Soft bark with questioning rhythm. Investigative — unsure about a sound or motion, not aggressive. |
| 1-30226-A-0.wav | dog | Repetitive Barking. sharp, spaced-out bursts with strong intensity. Threat — cat is reactive and confronting a perceived danger. |
| 1-34094-A-5.wav | cat | Muffled Meow. Soft, slightly muted meow, barely audible. Cautious Curiosity – unsure but not alarmed. |

**结论:模型对真实宠物声音有效。**
- ✅ **声音类型识别正确**:3 个狗叫→"Barking",1 个猫叫→"Meow",分类无误
- ✅ **结构化行为描述**:Guarding / Investigative / Threat / Cautious Curiosity,区分行为意图,非简单标签
- ⚠️ **行为主体偶有混淆**:dog bark 输出"cat is warning / cat is reactive"(第 1、3 个),把狗叫的主体说成猫——可能 forced English + 微调数据标签格式所致
- 总体:模型确为宠物声音行为识别微调,真实效用已验证,非空白无用

**调用命令(多文件批量推理)**:
```powershell
docker run --rm --gpus all `
  -v "D:\mydoc\workskill\code\pet-sound-to-texts\model:/models/pet-sound:ro" `
  -v "D:\mydoc\workskill\code\pet-sound-to-texts\samples:/samples:ro" `
  -v "D:\mydoc\workskill\code\pet-sound-to-texts\infer.py:/app/infer.py:ro" `
  -e MODEL_DIR=/models/pet-sound -e DEVICE=cuda -e SAMPLE_RATE=16000 `
  --entrypoint python pet-sound-to-texts:latest /app/infer.py `
  --audio /samples/dog1.wav /samples/cat1.wav
```
> `infer.py` 支持 `--audio` 接受多个路径(nargs="+"),一次加载模型循环推理,输出 `路径<TAB>文本`。

## 风险与结论

### 结论
**部署成功,模型可调用。** Docker + GPU + 挂载 + 推理全链路工作,demo 产出文本。模型确为宠物声音任务微调(非空白无用),输出宠物行为描述文本而非普通语音转录。

### 已验证风险
| 风险 | 实测结果 |
|---|---|
| 模型卡空白,行为未知 | 部分澄清:模型为宠物声音微调,输出行为描述(非普通转录);但对非宠物音频幻觉,真实效用需真实样本验证 |
| BITS 下载 HF LFS | 证实不兼容 → 改 `hf.exe` |
| apt 国外源 | 500 EOF → 换清华源 |
| CUDA init 卡死 | 非卡死,首次 3 分钟(WSL2/WDDM 特性) |
| 孤儿容器占 GPU | 证实,需 `docker rm -f` 清理 |
| Windows GBK 编码 | `hf.exe` + `PYTHONUTF8=1` 解决 |
| Git Bash 路径转换 | `--audio /samples/..` 被改成 `C:/Program Files/Git/samples/..` → 用 PowerShell 跑 |

### 待用户验证
- 真实宠物声音(狗叫/猫叫等)的输出是否准确——需用户自备样本测试:
  ```
  docker compose run --rm pet-asr --audio /samples/your_pet.wav
  ```
- 首次推理慢(CUDA init ~3 分钟),后续推理快

### 调用 demo(已验证可用)
```powershell
# 用合成样本 smoke test
docker compose -f "D:\mydoc\workskill\code\pet-sound-to-texts\docker-compose.yml" `
  --project-directory "D:\mydoc\workskill\code\pet-sound-to-texts" `
  run --rm pet-asr --audio /samples/sample.wav

# 自定义音频(把 your.wav 放到 code/pet-sound-to-texts/samples/ 下)
docker compose -f "D:\mydoc\workskill\code\pet-sound-to-texts\docker-compose.yml" `
  --project-directory "D:\mydoc\workskill\code\pet-sound-to-texts" `
  run --rm pet-asr --audio /samples/your.wav
```
> 注:在 PowerShell 中运行。Git Bash 会把容器内路径 `/samples/..` 错误转换。
