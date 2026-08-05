# Docker + HuggingFace 模型本地 GPU 部署最佳实践

> 基于 `Hakeem750/pet-sound-to-texts` 部署实战提炼(2026-07)。适用于 Windows 11 + Docker Desktop + WSL2 + NVIDIA GPU 环境,将 HuggingFace 模型打包为 Docker 容器、挂载模型权重、GPU 推理。案例详见 [pet-sound-to-texts-部署报告.md](./pet-sound-to-texts-部署报告.md)。

## 1. 前置条件预检

部署前必须验证的三件事——任一不满足都会卡住:

| 检查项 | 命令 | 期望 |
|---|---|---|
| Docker + Compose | `docker version` / `docker compose version` | 客户端+服务端都通 |
| NVIDIA runtime 已注册 | `docker info` 看 `Runtimes:` 含 `nvidia` | 含 `nvidia` |
| **GPU 透传实测** | `docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi` | 容器内见 GPU 型号 |

> 第三条是硬验证:runtime 注册 ≠ 透传可用。必须跑一次容器内 `nvidia-smi` 确认。driver 透传 OK 只代表 driver API 工作,**不代表 CUDA runtime init 能跑通**(见踩坑 #4)。

## 2. 镜像构建

### 2.1 base 镜像选择
优先用 **pytorch 官方镜像**(自带 torch+cuda,省去自装 torch 的麻烦与体积):
```
pytorch/pytorch:<torch版本>-cuda<cuda版本>-cudnn9-runtime
```
- 选 `runtime` 变体(不含 nvcc/devel,体积小一半)
- cuda 版本 ≤ driver 支持的 CUDA 版本(driver 向后兼容 runtime)
- 实测 `pytorch/pytorch:2.4.1-cuda12.1-cudnn9-runtime` + driver 596.21(CUDA 13.2)兼容

### 2.2 apt/pip 镜像源(国内网络必做)
国外源(archive.ubuntu.com / pypi.org)在国内慢且易 500 EOF。Dockerfile 用 `ARG` 让镜像源可覆盖(不硬编码):
```dockerfile
ARG APT_MIRROR=mirrors.tuna.tsinghua.edu.cn
ARG PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

RUN if [ -n "$APT_MIRROR" ]; then \
      sed -i "s|http://archive.ubuntu.com|https://${APT_MIRROR}|g; s|http://security.ubuntu.com|https://${APT_MIRROR}|g" /etc/apt/sources.list; \
    fi \
 && apt-get update \
 && apt-get install -y --no-install-recommends ffmpeg \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN PIP_INDEX_URL=${PIP_INDEX_URL} pip install --no-cache-dir -r /tmp/requirements.txt
```
- 部署到国外环境时 `--build-arg APT_MIRROR=` 留空即回退官方源
- transformers 版本尽量**匹配模型保存时的版本**(`config.json` 的 `transformers_version` 字段),避免 schema 不兼容

### 2.3 镜像不含模型
模型靠 bind 挂载,**不 COPY 进镜像**:
- 镜像小(~6GB vs +模型 3GB+)
- 换模型只改宿主目录,不 rebuild
- 多模型共享一个镜像

### 2.4 .dockerignore
排除大目录避免 build context 暴涨(模型 3GB 若进 context 会拖慢每次 build):
```
model/
samples/
.env
.git
__pycache__/
```

## 3. 模型下载

### 3.1 用 `hf.exe`,不用 BITS
| 工具 | 问题 |
|---|---|
| Windows BITS(`Start-BitsTransfer`) | 对 HF LFS CDN 兼容差:job 卡 `Transferring`/`Transferred=0 Total=0`,临时文件满 size 不 finalize。**避免** |
| `huggingface-cli download` | 新版已废弃;且 Windows 中文控制台 GBK 编码不了 ⚠️ emoji → `UnicodeEncodeError`。**避免** |
| **`hf.exe download`** | ✅ HF 官方新命令,原生 LFS + 断点续传 + sha256 校验 |

```powershell
$env:PYTHONUTF8='1'   # 强制 UTF-8,避免 emoji 编码崩溃
& "<conda>/Scripts/hf.exe" download <model_id> --local-dir <host_dir>
```
- `hf.exe` 在 conda env 的 `Scripts/` 下(不在 PATH,用全路径)
- `PYTHONUTF8=1` 是 Windows Python 必设
- 大模型(GB 级)走断点续传,中断重跑自动跳过已下文件

### 3.2 镜像加速(可选)
若 huggingface.co 慢:`$env:HF_ENDPOINT='https://hf-mirror.com'` 后再 `hf.exe download`。

## 4. 容器编排(docker-compose)

### 4.1 GPU 声明
新版 compose 用 `deploy.resources.reservations.devices`(跨平台,推荐):
```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```
- `count: all` 透传所有 GPU;也可指定数量
- 验证:`docker compose run --rm <svc> python -c "import torch;print(torch.cuda.is_available())"`

### 4.2 模型 bind 挂载(只读)
```yaml
volumes:
  - ${MODEL_DIR:-./model}:${CONTAINER_MODEL_DIR:-/models/<name>}:ro
  - ./samples:/samples:ro
```
- `:ro` 防止容器误写宿主模型
- 宿主路径与容器内路径**分开两个 env 变量**(宿主给下载脚本/挂载源,容器内给推理脚本读)

### 4.3 env 驱动(无硬编码)
所有可变配置走 env,`docker-compose.yml` 用 `${VAR:-default}`:
```yaml
environment:
  - MODEL_DIR=${CONTAINER_MODEL_DIR:-/models/<name>}
  - DEVICE=${DEVICE:-cuda}
  - SAMPLE_RATE=${SAMPLE_RATE:-16000}
  - HF_ENDPOINT=${HF_ENDPOINT:-https://huggingface.co}
```
配合 `.env.example` 模板(提交)和 `.env`(实际值,gitignore)。

## 5. 推理脚本设计

### 5.1 环境驱动 + 无硬编码
```python
model_dir = os.environ.get("MODEL_DIR", "/models/default")
device = os.environ.get("DEVICE", "cuda")
sample_rate = int(os.environ.get("SAMPLE_RATE", "16000"))
```
端口/URL/路径/模型 ID 全走 env 或 CLI 参数,不写死在代码里。

### 5.2 多文件批量推理
`--audio` 用 `nargs="+"` 支持多文件,**一次加载模型循环推理**:
```python
parser.add_argument("--audio", required=True, nargs="+", help="path(s) or URL(s)")
# 加载模型 + pipeline 一次
for audio_path in args.audio:
    audio = load_audio(audio_path, sample_rate)
    result = pipe(audio, generate_kwargs=generate_kwargs)
    print(f"{audio_path}\t{text}")
```
- 避免每个文件重复 3 分钟 CUDA init(见踩坑 #4)
- 输出 `路径<TAB>文本` 便于程序解析

### 5.3 错误处理不静默
- 每个文件 try/except,失败记录 stderr + `continue`(不中断批量)
- 模型加载失败 `sys.exit(1)`(致命)
- 音频读取/推理失败记录后跳过(非致命)
- **禁止静默吞异常**:`except: pass` 是反模式

### 5.4 stdout/stderr 分离
- 进度/警告 → stderr(`print(..., file=sys.stderr)`)
- 结果文本 → stdout(便于管道 `> results.txt`)
- 容器内 `python -u` 或 `PYTHONUNBUFFERED=1` 实时输出(便于看进度)

### 5.5 音频预处理
Whisper 系模型要求 **16kHz 单声道 float32**:
```python
audio, sr = sf.read(path, dtype="float32")
if audio.ndim > 1: audio = audio.mean(axis=1)        # 多声道→单声道
if sr != 16000: audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
```
- 容器装 `ffmpeg`(apt)处理非 WAV(mp3/ogg 等)
- URL 音频先 `urllib.request.urlretrieve` 到临时文件再读

## 6. 测试策略

### 6.1 分层测试
| 层级 | 目的 | 输入 |
|---|---|---|
| 1. 链路 smoke test | 验证容器+GPU+模型加载+推理+输出全通 | 合成音频(纯标准库生成,不依赖外部) |
| 2. 真实样本验证 | 验证模型对真实输入的效用 | 公开数据集样本 |
| 3. 诚实记录 | 如实报告输出(乱码就说乱码) | — |

### 6.2 合成音频生成(不依赖第三方库)
```python
import array, math, wave
buf = array.array("h")
for i in range(n):
    t = i / sr
    s = env * (math.sin(2*math.pi*440*t) + math.sin(2*math.pi*880*t)) / 2
    buf.append(max(-32768, min(32767, int(32767*s))))
# wave.open 写 16-bit mono
```
- 纯标准库,任何 Python 能跑
- 用途:验证 pipeline 通,不验证模型效用(模型对非宠物音频会幻觉)

### 6.3 真实样本获取
| 来源 | 优点 | 注意 |
|---|---|---|
| **HuggingFace datasets**(`ashraq/esc50` 等) | HF 托管,不限速,`hf.exe` 可下 | 可能是 parquet(不能直接下单个 wav) |
| **GitHub raw + jsdelivr CDN** | `https://cdn.jsdelivr.net/gh/<user>/<repo>@<branch>/<path>` 绕过 raw 429 限速 | 用 git tree API 找确切文件名 |
| Wikimedia Commons | 公共域 | API 易 403 限速,直接 `Special:FilePath` |

> GitHub `raw.githubusercontent.com` 对匿名有 429 限速;**jsdelivr CDN** 是稳定替代。GitHub `contents` API 对 >1000 文件目录截断,用 `git/trees?recursive=1` 代替。

### 6.4 诚实核验
模型卡空白/下载量低时,**不要预设模型有效**:
- 合成音频若输出有意义文本,可能是幻觉(印证模型对非目标输入的行为)
- 真实样本若输出乱码,如实记录
- 区分「能调通」(技术层)与「输出有意义」(效用层),两者独立报告

## 7. 踩坑速查表

| # | 现象 | 根因 | 解法 |
|---|---|---|---|
| 1 | BITS 下 HF 大文件:job `Transferring`,`Transferred=0/Total=0`,临时文件满 size 不 finalize | BITS 对 HF LFS CDN 的 range/UA 兼容差 | 放弃 BITS,用 `hf.exe download` |
| 2 | `huggingface-cli download` 报 `UnicodeEncodeError: 'gbk' codec can't encode ⚠️` | 命令已废弃+打印 emoji,Windows 中文控制台 GBK 编码不了 | 用 `hf.exe` + `$env:PYTHONUTF8='1'` |
| 3 | Dockerfile `apt-get install` 6 分钟后某 deb `500 EOF` | archive.ubuntu.com 经 CDN 不稳 | Dockerfile 加 `ARG APT_MIRROR=mirrors.tuna.tsinghua.edu.cn` + sed 换源 |
| 4 | 容器内 `torch.cuda.is_available()` 3 分钟无输出,疑似卡死 | WSL2/WDDM 首次 CUDA runtime init 极慢(加载 cudnn+资源协商),**非卡死** | 加时间戳+`python -u`+后台给足时间;别误判重启 |
| 5 | `docker compose run ... --audio /samples/x.wav` 容器内路径变 `C:/Program Files/Git/samples/x.wav` | Git Bash(MSYS2)把 `/` 开头路径转换 | 用 PowerShell 跑 docker,或 `MSYS_NO_PATHCONV=1` |
| 6 | 后续 GPU 容器启动卡(连 `echo` 30s 无输出);`docker rm -f` 报 `could not kill... did not receive exit event` | `timeout` 杀 docker 客户端但容器未删,占着 nvidia runtime 资源;卡死容器进 D 状态 | 测试后务必 `docker rm -f` 清理;D 状态容器等一会再试或 `wsl --shutdown` |

## 8. 部署检查清单

**构建前**
- [ ] `docker info` 含 `nvidia` runtime
- [ ] `docker run --rm --gpus all nvidia/cuda:... nvidia-smi` 容器内见 GPU
- [ ] Dockerfile base = pytorch 官方 runtime 镜像
- [ ] Dockerfile 含 `ARG APT_MIRROR` + `ARG PIP_INDEX_URL`(清华源)
- [ ] `.dockerignore` 排除 `model/` `samples/`

**模型下载**
- [ ] 用 `hf.exe download`(非 BITS/非 huggingface-cli)
- [ ] `$env:PYTHONUTF8='1'` 已设
- [ ] 下载后 `ls` 校验文件数 + 大小

**容器编排**
- [ ] compose `deploy.resources.reservations.devices` 声明 GPU
- [ ] 模型 `bind` 挂载 `:ro`
- [ ] env 驱动(MODEL_DIR/DEVICE/SAMPLE_RATE),无硬编码
- [ ] `.env.example` 提交,`.env` gitignore

**推理脚本**
- [ ] env 驱动配置
- [ ] `--audio nargs="+"` 多文件批量
- [ ] 错误显式处理(不静默吞)
- [ ] stdout(结果)/stderr(进度)分离
- [ ] 音频重采样到 16kHz 单声道

**测试**
- [ ] 合成音频 smoke test 验通链路
- [ ] 真实样本验证效用
- [ ] 诚实记录输出(乱码不粉饰)
- [ ] 测试后 `docker rm -f` 清理容器

## 9. 关键认知

1. **driver 透传 OK ≠ CUDA runtime 可用**:`nvidia-smi` 走 driver API,`torch.cuda.is_available()` 走 runtime init,两者独立。必须实测后者。
2. **首次 CUDA init 慢是 WSL2/WDDM 特性**:3 分钟正常,别误判卡死重启。加时间戳定位。
3. **BITS 不是万能**:规则要求 >100MB 用 BITS,但 BITS 对 HF LFS 不工作。工程上换 `hf.exe`(也是断点续传)。规则的"精神"(可靠大文件下载)比"字面"(必须 BITS)更重要。
4. **镜像不含模型**:bind 挂载让镜像小、可复用、换模型不 rebuild。
5. **Git Bash 路径转换是隐形坑**:容器内路径 `/foo` 被 MSYS2 改成 Windows 路径。docker 命令用 PowerShell 跑。
6. **孤儿容器是定时炸弹**:`timeout` 杀客户端不删容器,占 GPU 资源。每次测试后清理。
7. **合成音频只验链路,不验效用**:模型对非目标输入会幻觉。效用必须真实样本验证。
8. **模型卡空白≠模型无用**:下载量低、卡空白时仍可能有效(如本例模型确为宠物声音微调)。实测定论,不预判。

## 10. 案例参考

- 部署报告:[pet-sound-to-texts-部署报告.md](./pet-sound-to-texts-部署报告.md)
- 检测结果:[pet-sound-to-texts-检测结果.md](./pet-sound-to-texts-检测结果.md)
- 代码:`code/pet-sound-to-texts/`(Dockerfile/compose/infer.py/download_model.ps1/generate_sample.py)
- 经验存档:`memory/docker-gpu-model-deploy-pitfalls.md`
