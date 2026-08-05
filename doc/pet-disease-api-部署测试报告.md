# PetDiseaseApi Docker 打包与部署测试报告

> 仓库:[`Eswarchinthakayala-webdesign/PetDiseaseApi`](https://github.com/Eswarchinthakayala-webdesign/PetDiseaseApi)
> 任务:读取项目 → Docker 打包 → 本地部署 → API 使用测试
> 日期:2026-07-06
> 测试环境:Windows 11 + Docker Desktop 29.5.3(linux/amd64)
> 最终结果:**✅ 全部 4 项任务完成,API 测试 8/8 PASS**

---

## 1. 项目概述

PetDiseaseApi 是基于 **FastAPI + YOLOv8** 的宠物疾病预测 API,可从宠物图片识别 **22 种猫狗常见疾病**并返回疾病详情(描述/治疗/严重程度/预防建议)。

**两阶段推理**:
1. `yolov8n.pt`(COCO 预训练)检测图片中是否含猫(class 15)或狗(class 16)
2. 命中后裁剪,交 `model/best.pt`(22 类分类器)做疾病分类

**API 端点**:

| 端点 | 方法 | 说明 |
|---|---|---|
| `/` | GET | 根状态 |
| `/health` | GET | 健康检查 + 模型加载状态 |
| `/diseases` | GET | 列出 22 种疾病 |
| `/diseases/{name}` | GET | 单病详情(name 需 URL 编码) |
| `/predict` | POST | 上传图片预测疾病(multipart 字段 `file`,query `confidence` 默认 0.3) |
| `/docs` | GET | Swagger 交互文档 |

---

## 2. Docker 打包方案

仓库仅含 `render.yaml`(Render 云部署),**无 Dockerfile / docker-compose.yml**,需自写。打包文件位于 `code/pet-disease-api/`。

### 2.1 Dockerfile

设计要点:
- 基础镜像 `python:3.10-slim`(对齐 render.yaml 的 Python 3.10.12)
- 系统依赖:**只装 `libglib2.0-0 / libsm6 / libxrender1 / libxext6`,不装 `libgl1`**——因为 requirements.txt 中 `opencv-python-headless` 列于 `ultralytics` 之后,pip 最终用 headless,headless 不链接 libGL(详见 §6 踩坑 1)
- pip 镜像源通过 `ARG PIP_INDEX_URL` 注入(不硬编码 URL),pip 自动读该环境变量
- `--mount=type=cache,target=/root/.cache/pip` 跨构建复用 wheel
- 装完依赖后 `pip uninstall -y opencv-python` + `pip install --no-deps --force-reinstall opencv-python-headless`,强制 cv2 为 headless(详见 §6 踩坑 3)
- 端口环境变量 `ENV PORT=10000`,启动 `sh -c 'uvicorn app.main:app --host 0.0.0.0 --port ${PORT}'`(端口不硬编码)

完整内容见 `code/pet-disease-api/Dockerfile`。

### 2.2 docker-compose.yml

- 端口映射 `"${PORT:-10000}:${PORT:-10000}"`(由 `.env`/环境变量驱动)
- `build.args.PIP_INDEX_URL: ${PIP_INDEX_URL:-}` 从宿主环境注入 pip 镜像源
- 注入 `PORT`、`UPLOAD_DIR` 环境变量
- `volumes: ./uploads:/app/uploads`(上传文件持久化)
- `healthcheck`:容器内 `python urllib` 探测 `/health`,`start_period: 90s`(给模型加载留时间)
- `restart: unless-stopped`

完整内容见 `code/pet-disease-api/docker-compose.yml`。

### 2.3 .dockerignore

排除 `.git / __pycache__ / venv / uploads/* / assets/ / *.log`,减小构建上下文。

---

## 3. 构建与部署

### 3.1 镜像构建

```bash
# 注入清华镜像源加速(PIP_INDEX_URL 作为环境变量,compose 透传给 build-arg)
$env:PIP_INDEX_URL='https://pypi.tuna.tsinghua.edu.cn/simple'
docker compose -f code/pet-disease-api/docker-compose.yml build
```

- **最终镜像**:`pet-disease-api:latest`,**8.68 GB**(偏大,见 §6 优化建议)
- **构建耗时**:有效构建约 4 分钟(pip cache mount 命中后);首次构建下载 torch + CUDA 依赖约 6 分钟
- 构建过程中遇到 3 个坑(详见 §6),均已解决

### 3.2 容器部署

```bash
docker compose -f code/pet-disease-api/docker-compose.yml up -d
```

- **容器状态**:`pet-disease-api  Up (healthy)`
- **端口**:`0.0.0.0:10000->10000/tcp`
- **健康检查**:`/health` 返回 `status=healthy`,两模型 `loaded=true`
- 首次启动加载模型约 30–60 秒(CPU),`start_period: 90s` 覆盖

---

## 4. API 使用测试

### 4.1 测试素材(网络下载)

素材均从公网下载至 `doc/`(小文件,直接 HTTP 下载,未触发 BITS 规则):

| 文件 | 来源 | 大小 | 尺寸 | 用途 |
|---|---|---|---|---|
| `test-cat.jpg` | cataas.com (`/cat?width=600`) | 75 KB | 600×305 | 猫图预测 |
| `test-dog.png` | random.dog API (`/woof.json`) | 671 KB | 750×732 | 狗图预测 |
| `test-notpet.png` | placehold.co (`/600x400.png`) | 7 KB | 600×400 | 非宠物图(预期被拒) |

下载过程:cat 用 cataas;dog 用 random.dog API(dog.ceo 因 TLS 拒绝连接,已换源);非宠物图用 placehold.co 占位图。

### 4.2 测试用例与结果

测试命令:GET 用 `Invoke-RestMethod`,POST /predict 用 `curl.exe -F "file=@<img>"` 做 multipart 上传(`confidence=0.1` 取 top5)。

| # | 用例 | 请求 | 期望 | 实际结果 |
|---|---|---|---|---|
| 1 | 根端点 | `GET /` | 200,`status=ok` | ✅ `status=ok` |
| 2 | 健康检查 | `GET /health` | 200,两模型 loaded | ✅ `detector=True classifier=True classes=22` |
| 3 | 疾病目录 | `GET /diseases` | 200,`total=22` | ✅ `total=22` |
| 4 | 单病详情 | `GET /diseases/dental%20disease%20in%20cat` | 200,`severity=high` | ✅ `severity=high` |
| 5 | 预测-猫 | `POST /predict`(test-cat.jpg,conf=0.1) | 200,`top_prediction` 非空 | ✅ `top=Worm Infection in Cat conf=0.5374` |
| 6 | 预测-狗 | `POST /predict`(test-dog.png,conf=0.1) | 200,`top_prediction` 非空 | ✅ `top=Distemper in Dog conf=0.2409` |
| 7 | 非宠物图 | `POST /predict`(test-notpet.png) | 400,detail 含 "No dog or cat" | ✅ `400 No dog or cat detected. Please upload a valid pet image.` |
| 8 | Swagger | `GET /docs` | 200 | ✅ `http=200` |

**汇总:PASS 8 / 8**

> 说明:狗图预测置信度较低(0.24),因 random.dog 返回的是健康狗,而模型训练数据为病狗,分类不确定属正常现象;API 行为正确(返回 top5 中 conf≥阈值的结果)。本次测试目标是 API 可用性,非模型精度。

---

## 5. 结论

| 任务 | 状态 |
|---|---|
| 1. 读取项目 | ✅ 浅克隆到 `code/pet-disease-api/`,完成源码与结构调研 |
| 2. Docker 打包 | ✅ 新建 `Dockerfile` / `docker-compose.yml` / `.dockerignore` |
| 3. 完成部署 | ✅ 容器 `healthy`,端口 10000,两模型加载完成 |
| 4. 使用测试 | ✅ 8/8 PASS,素材从网络下载(cat/dog/非宠物) |

**容器与镜像信息**:
- 镜像:`pet-disease-api:latest`,8.68 GB
- 容器:`pet-disease-api`,`Up (healthy)`,`0.0.0.0:10000->10000/tcp`
- 访问入口:`http://localhost:10000/docs`(Swagger)

**容器管理**:
- 查看日志:`docker compose -f code/pet-disease-api/docker-compose.yml logs -f`
- 停止:`docker compose -f code/pet-disease-api/docker-compose.yml down`
- 重启:`docker compose -f code/pet-disease-api/docker-compose.yml restart`

---

## 6. 构建踩坑与优化建议

### 踩坑 1:apt 装 libgl1 触发 OOM(exit 137)
- **现象**:首次构建在 `apt-get install libgl1` 时 exit 137(SIGKILL)
- **根因**:`libgl1` 拉入 `libgl1-mesa-dri` + `libllvm19`(~100MB+,解包内存峰值大),WSL2 内存不足被 OOM kill
- **解决**:去掉 `libgl1`——因为 pip 最终装的是 `opencv-python-headless`(headless 不链接 libGL),根本不需要 libgl1

### 踩坑 2:PyPI 下载极慢(65 kB/s)
- **现象**:`torch` wheel 532MB,PyPI 默认源仅 65 kB/s,预计 2+ 小时
- **解决**:Dockerfile 加 `ARG PIP_INDEX_URL`,compose 通过 build-arg 从宿主环境注入;构建时设 `$env:PIP_INDEX_URL='https://pypi.tuna.tsinghua.edu.cn/simple'`,清华源 13 MB/s,200 倍加速。URL 作为参数注入,不硬编码在代码里

### 踩坑 3:opencv-python 覆盖 opencv-python-headless
- **现象**:`ultralytics` 依赖 `opencv-python`,`pip install -r requirements.txt` 两者都装,且 `opencv-python` 在 headless 之后装,覆盖 cv2 → 运行时 cv2 是非 headless,需要 libGL(已去掉)→ 启动会 import 失败
- **解决**:Dockerfile 装完依赖后 `pip uninstall -y opencv-python` + `pip install --no-deps --force-reinstall opencv-python-headless`,确保 cv2 为 headless

### 优化建议(未实施,不阻塞部署)
- **镜像体积**:当前 8.68GB,因 torch 2.12.1 默认 wheel 拉入大量 CUDA 13 依赖(nvidia-cublas 423MB / cudnn 366MB / cusparselt 170MB / nccl 206MB 等),CPU 部署完全用不到。可改用 CPU-only torch(`pip install torch --index-url https://download.pytorch.org/whl/cpu`),镜像可降至约 2GB。本次为快速完成部署未实施,留作后续改进
- **测试图清理**:`doc/test-cat.jpg / test-dog.png / test-notpet.png` 为测试素材(共约 750KB),可保留作复现证据或手动删除
