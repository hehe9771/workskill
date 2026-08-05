# Python AI API(Docker)打包部署最佳实践

> 提炼自 PetDiseaseApi(FastAPI + YOLOv8 + OpenCV)Docker 打包部署实战。
> 适用于:Python + FastAPI/Uvicorn + 深度学习推理(torch/ultralytics/opencv)+ 含模型权重的仓库,本地 Docker Desktop 部署。
> 编写日期:2026-07-07

---

## 0. 一句话原则

**端口/镜像源/路径全部环境变量化,pip 镜像源 build-arg 注入,opencv 用 headless 不装 libgl1,健康检查给足模型加载时间,测试素材多源 fallback + 必含预期错误用例。**

---

## 1. 部署流程(5 步)

| 步骤 | 动作 | 产出 |
|---|---|---|
| 1. 调研 | 浅克隆(`--depth 1`)→ 读 README/入口/依赖/端口/上传字段名 | 项目结构清单、入口命令、API 端点表 |
| 2. 打包 | 写 Dockerfile / docker-compose.yml / .dockerignore | 三件套 |
| 3. 构建 | 注入镜像源 `docker compose build` | 镜像 |
| 4. 部署 | `docker compose up -d` → 轮询 `/health` 等模型加载 | healthy 容器 |
| 5. 测试 | 网络下载素材 → curl.exe multipart + Invoke-RestMethod | 8/8 报告 |

**调研要点**(避免返工):确认①Python 版本 ②入口(`uvicorn app.main:app`)③默认端口 ④`/predict` 上传字段名(`file` 还是 `image`)⑤模型文件是否在仓库内 ⑥上传目录环境变量名。

---

## 2. Dockerfile 模板(可复用)

```dockerfile
FROM python:3.10-slim

# 系统库:opencv-python-headless 只需 libglib2.0-0 等。
# 不要装 libgl1 —— 它会拉入 libgl1-mesa-dri + libllvm19,解包内存峰值大,WSL2 易 OOM(exit 137)。
# headless 不链接 libGL,根本不需要 libgl1。
RUN apt-get update && apt-get install -y --no-install-recommends \
        libglib2.0-0 libsm6 libxrender1 libxext6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 先装依赖(利用层缓存:源码变动不重装依赖)
COPY requirements.txt .

# pip 镜像源通过 build-arg 注入(不硬编码 URL);cache mount 跨构建复用 wheel。
ARG PIP_INDEX_URL
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip uninstall -y opencv-python 2>/dev/null || true \
    && pip install --no-deps --force-reinstall opencv-python-headless
# 末两行:ultralytics 会拉 opencv-python 覆盖 headless,强制还原 headless,避免运行时缺 libGL

COPY . .
RUN mkdir -p uploads && chmod 777 uploads

# 端口/上传目录环境变量化(不硬编码)
ENV PORT=10000 UPLOAD_DIR=uploads \
    PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
EXPOSE 10000
CMD ["sh","-c","uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
```

### 要点
- **不装 libgl1**:headless 不需要;装了会 OOM(见 §4 坑 1)
- **`ARG PIP_INDEX_URL`**:pip 自动读该环境变量作镜像源;默认空=官方,可通过 build-arg 注入清华/阿里源(见 §4 坑 2)
- **`--mount=type=cache`**:pip wheel 跨构建复用,重跑只装增量
- **依赖先装**:`COPY requirements.txt` 单独一层,源码变动不触发重装
- **headless 强制**:ultralytics 拉 opencv-python 覆盖 cv2,装后卸载 + 强制重装 headless(见 §4 坑 3)
- **端口环境变量**:`ENV PORT` + `CMD sh -c '...${PORT}'`,compose 可覆盖

---

## 3. docker-compose.yml 模板(可复用)

```yaml
services:
  app:
    build:
      context: .
      args:
        # pip 镜像源由宿主环境变量注入(默认空=官方 PyPI)
        PIP_INDEX_URL: ${PIP_INDEX_URL:-}
    image: app:latest
    container_name: app
    ports:
      - "${PORT:-10000}:${PORT:-10000}"
    environment:
      PORT: "${PORT:-10000}"
      UPLOAD_DIR: uploads
    volumes:
      - ./uploads:/app/uploads
    healthcheck:
      # 容器内读 PORT 环境变量自适应端口;urlopen 失败即 unhealthy
      test: ["CMD-SHELL","python -c \"import os,urllib.request;urllib.request.urlopen('http://127.0.0.1:'+os.environ.get('PORT','10000')+'/health',timeout=5).read()\""]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 90s   # 模型首次加载(CPU 可能 30-60s)留足时间
    restart: unless-stopped
```

### 构建与启动命令
```powershell
# 注入清华镜像源(环境变量,不写进代码)
$env:PIP_INDEX_URL='https://pypi.tuna.tsinghua.edu.cn/simple'
docker compose -f path/to/docker-compose.yml build
docker compose -f path/to/docker-compose.yml up -d
```

---

## 4. 构建踩坑与规避(核心)

| # | 坑 | 现象 | 根因 | 规避 |
|---|---|---|---|---|
| 1 | apt 装 libgl1 → OOM | `exit code 137`(SIGKILL) | libgl1 依赖 `libgl1-mesa-dri` + `libllvm19`(~100MB+),解包内存峰值超 WSL2 限制被 kill | **不装 libgl1**;opencv 用 headless(不链接 libGL),只需 `libglib2.0-0` |
| 2 | PyPI 默认源极慢 | torch 532MB / 65 kB/s,预计 2 小时 | PyPI 默认源限速 | `ARG PIP_INDEX_URL` + compose `build.args` 注入;构建时设 `$env:PIP_INDEX_URL='https://pypi.tuna.tsinghua.edu.cn/simple'`(13 MB/s,200×) |
| 3 | opencv-python 覆盖 headless | 容器启动 cv2 import 失败(缺 libGL) | `ultralytics` 依赖 `opencv-python`,`pip install -r` 两者都装,opencv-python 后装覆盖 cv2 | Dockerfile 末尾 `pip uninstall -y opencv-python && pip install --no-deps --force-reinstall opencv-python-headless` |
| 4 | 镜像体积过大 | 8.68 GB | torch 默认 wheel 拉入 CUDA 13 依赖(cublas 423MB / cudnn 366MB / nccl 206MB...),CPU 部署用不到 | 改 CPU-only torch:`pip install torch --index-url https://download.pytorch.org/whl/cpu`(镜像可降至 ~2GB) |
| 5 | background 构建看不到进度 | 输出文件空 | PowerShell `2>&1 \| Out-String` 管道会缓冲到命令结束才输出 | background 构建不要接 `Out-String` 管道,直接 `docker compose build --progress plain` |
| 6 | PowerShell 5.1 `2>&1` native exe 误报 | $? 被设 false | PS 5.1 把 native exe stderr 包成 ErrorRecord | 不对 native exe 用 `2>&1`;stderr 由工具自行捕获 |

---

## 5. 部署验证

```powershell
# 等模型加载(首次 CPU 加载 30-60s)
Start-Sleep -Seconds 90
docker ps --filter "name=app" --format "{{.Names}} | {{.Status}} | {{.Ports}}"
Invoke-RestMethod http://localhost:10000/health -TimeoutSec 20
```

**验证标准**:
- 容器 `Status` 含 `(healthy)`
- `/health` 返回 `status=healthy` 且所有模型 `loaded=true`
- 若端口被占,改 `PORT` 环境变量重跑(`$env:PORT=10001; docker compose up -d`)

---

## 6. API 测试方法论

### 6.1 测试素材:多源 fallback
单一图片源易失败(dog.ceo TLS 拒绝、Wikimedia URL 难猜)。每个素材准备 2-3 个源,首个成功即停:

| 用途 | 推荐源(按优先级) |
|---|---|
| 猫图 | `cataas.com/cat?width=600` → `placekitten.com/600/600` → Wikimedia Special:FilePath |
| 狗图 | `random.dog/woof.json`(API 取 URL 再下)→ Wikimedia Commons API 搜索 → `dog.ceo`(<http://dog.ceo> 偶发 TLS 拒绝) |
| 非宠物图 | `placehold.co/600x400.png`(纯色占位,稳定可达) |

下载用 `Invoke-WebRequest -UserAgent`,小文件(<1MB)直接 HTTP,不触发 BITS 规则(>100MB 才用 BITS)。

### 6.2 POST multipart:用 curl.exe
PowerShell 5.1 的 `Invoke-RestMethod` **不支持** multipart/form-data(无 `-Form` 参数)。用 Windows 自带的 `curl.exe`:

```powershell
$raw = & curl.exe -s -o $tmpRespFile -w "%{http_code}" -X POST -F "file=@$imagePath" "$base/predict?confidence=0.1"
$httpCode = if ($LASTEXITCODE -eq 0) { "$raw".Trim() } else { '000' }
$resp = Get-Content $tmpRespFile -Raw | ConvertFrom-Json
```
- `-w "%{http_code}"` 把状态码输出到 stdout,`-o` 把 body 写文件
- `$LASTEXITCODE` 是 curl 退出码(0=执行成功,即使 HTTP 4xx/5xx)

### 6.3 测试用例必含项
1. 根/健康/列表/详情/文档(GET,`Invoke-RestMethod`)
2. 正向预测(猫、狗图,`POST /predict`)
3. **预期错误用例**(非宠物图 → 400 "No dog or cat",验证模型两阶段检测逻辑)
4. 无效文件类型(传 .txt → 400)

> 不要只测正向。预期错误用例验证错误处理分支,信号最强。

### 6.4 PS 5.1 多行测试脚本注意
- `if($ok){'PASS'}else{'FAIL'}` 表达式赋值在 PS 5.1 合法
- `Remove-Item $tmp` 可能被安全 hook 误拦(变量未展开时保守判断),**避免在命令行用 Remove-Item**,改用固定临时文件名覆盖
- `Invoke-RestMethod` 返回 PSCustomObject,嵌套属性用 `$r.model.disease_classifier.loaded` 访问

---

## 7. 通用 Checklist

打包前:
- [ ] 调研确认 Python 版本、入口、端口、上传字段名、模型文件位置
- [ ] `Dockerfile` 端口 `ENV PORT` + `CMD sh -c '${PORT}'`(不硬编码)
- [ ] `ARG PIP_INDEX_URL`(镜像源可注入,不硬编码 URL)
- [ ] `--mount=type=cache,target=/root/.cache/pip`
- [ ] 系统库只装 `libglib2.0-0` 等,**不装 libgl1**
- [ ] opencv-headless 强制(`uninstall opencv-python` + `force-reinstall headless`)
- [ ] `.dockerignore` 排除 `.git / __pycache__ / venv / uploads/*`

部署前:
- [ ] compose `ports: "${PORT:-10000}:${PORT:-10000}"`
- [ ] `build.args.PIP_INDEX_URL: ${PIP_INDEX_URL:-}`
- [ ] `healthcheck` + `start_period: 90s`(模型加载时间)
- [ ] `volumes` 持久化上传目录
- [ ] 端口冲突预检:`Get-NetTCPConnection -LocalPort 10000`

测试前:
- [ ] 素材多源 fallback(猫/狗/非宠物)
- [ ] curl.exe 做 POST multipart
- [ ] 测正向 + 预期错误 + 无效文件类型
- [ ] `/docs` Swagger 可达
- [ ] 测试图有效性预检(`System.Drawing.Image` 读尺寸)

---

## 8. 镜像优化(可选,CPU 推理场景)

torch 默认 PyPI wheel 含 CUDA 依赖,镜像可达 8GB+。CPU 部署改用 CPU-only wheel:

```dockerfile
# 替换原 pip install 行
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip \
    && pip install torch torchvision --index-url ${PIP_TORCH_INDEX_URL:-https://download.pytorch.org/whl/cpu} \
    && pip install -r requirements.txt \
    && pip uninstall -y opencv-python 2>/dev/null || true \
    && pip install --no-deps --force-reinstall opencv-python-headless
```
镜像可从 8.68GB 降至约 2GB。代价:CPU torch index 在国外,首次下载可能较慢(可找国内 PyTorch 镜像)。

---

## 9. 关联文档

- 本次任务记录:[pet-disease-api-部署测试报告.md](./pet-disease-api-部署测试报告.md)
- 打包产物:`code/pet-disease-api/`(Dockerfile / docker-compose.yml / .dockerignore)
