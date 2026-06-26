# screenshot-to-code 最佳实践（安装 + 使用）

> 项目地址：https://github.com/abi/screenshot-to-code
> 官方托管：https://screenshottocode.com
> 文档生成日期：2026-06-22
> 信息来源：项目 README.md / pyproject.toml / package.json / docker-compose.yml / Troubleshooting.md（main 分支）

---

## 一、项目认知（先理解再装）

| 维度 | 内容 |
|---|---|
| 功能 | 截图 / 设计稿 / Figma / 网站录屏 → 功能性代码 |
| 架构 | React/Vite 前端 (5173) + FastAPI 后端 (7001) + WebSocket 流式输出 |
| 后端 | Python ^3.10 / Poetry / FastAPI / Playwright(Chromium) / moviepy(需 ffmpeg) |
| 前端 | React 18 / Vite 4 / TypeScript / Tailwind / Zustand / Radix UI / CodeMirror |
| AI 模型 | OpenAI(GPT-5.5 / GPT-5.4 Mini) · Anthropic(Opus 4.8 / Fable 5 / Sonnet 4.6) · Gemini(3 Flash Preview / 3.1 Pro Preview) · Replicate(z-image-turbo，图像生成) |
| 输出栈 | HTML+Tailwind · HTML+CSS · React+Tailwind · Vue+Tailwind · Bootstrap · Ionic+Tailwind |
| 可观测 | Langfuse ^3.0.2（依赖已内置，可选接入） |

**核心机制**：
- **Gemini** → 从截图提取真实素材（复用真实 logo/图片，保真度高）；视频模式必需
- **Replicate** → 图像生成 / 抠图(remove_background) / 图像编辑(edit_image)
- **LLM（OpenAI/Anthropic/Gemini）** → 代码生成
- **Playwright Chromium** → 启用 "screenshot preview"，agent 渲染自检生成页面的视觉效果

---

## 二、安装最佳实践

### 2.1 路径选择

| 场景 | 推荐 | 理由 |
|---|---|---|
| 快速体验 / 试用 | **Docker** (`docker-compose up -d --build`) | 一条命令，无需装 Poetry/Node |
| 定制、二次开发、贡献 | **本地开发** | 改文件热重载，Docker 不触发重建 |
| 不想本地装 | 官方托管 screenshottocode.com | 零配置，但无法调试 |

### 2.2 前置准备（Windows 适配）

> 环境：Windows 11 + conda。**不要污染现有 conda env**，为该项目建专用 env。

1. **Node.js ≥ 18**（package.json 标 ≥14.18，但 Vite4 + 依赖实际需 18+）；用 `nvm-windows` 管理版本
2. **Python 3.11**（项目要 ^3.10，3.11 最稳）：
   ```powershell
   conda create -n s2c python=3.11 -y
   conda activate s2c
   ```
3. **Poetry**（装在 s2c env 内）：`pip install --upgrade poetry`
4. **ffmpeg**：moviepy 视频模式必需。`conda install -c conda-forge ffmpeg` 或下载二进制加入 PATH
5. **Docker Desktop**（仅 Docker 路径需要）
6. **Git**：`git clone https://github.com/abi/screenshot-to-code.git`

### 2.3 方式 A：Docker（推荐快速体验）

```powershell
# 根目录创建 .env —— UTF-8 无 BOM 编码（Windows 关键坑）
@"
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx
GEMINI_API_KEY=xxx
REPLICATE_API_KEY=r8_xxx
BACKEND_PORT=7001
"@ | Out-File -FilePath .env -Encoding utf8

docker-compose up -d --build
# 访问 http://localhost:5173
```

> ⚠️ Docker 路径**不支持热重载**，改代码需重新 build，不适合开发。

### 2.4 方式 B：本地开发（推荐定制）

**后端**：
```powershell
cd backend
# .env 内容同上，UTF-8 无 BOM 编码（Windows 用 Notepad++ 转，否则报 UTF-8 错误）
poetry install
poetry run playwright install chromium          # Linux 加 --with-deps（需 sudo/apt）
poetry run uvicorn main:app --reload --port 7001
```

**前端**（新开终端）：
```powershell
cd frontend
# .env.local 指向后端
@"
VITE_WS_BACKEND_URL=ws://localhost:7001
VITE_HTTP_BACKEND_URL=http://localhost:7001
"@ | Out-File -FilePath .env.local -Encoding utf8

yarn
yarn dev
# 访问 http://localhost:5173
```

### 2.5 API Keys 配置策略（关键）

| Key | 必需性 | 作用 | 配置位置 |
|---|---|---|---|
| `OPENAI_API_KEY` | 三选一 | GPT 系代码生成 | backend/.env 或前端设置弹窗 |
| `ANTHROPIC_API_KEY` | 三选一 | Claude 系代码生成 | 同上 |
| `GEMINI_API_KEY` | **强烈推荐** | 代码生成 + **素材提取 + 视频模式必需** | 同上 |
| `REPLICATE_API_KEY` | **强烈推荐** | 图像生成/抠图/编辑，否则这些功能不可用 | **仅 backend/.env** |

**最佳策略**：
- **四键全配** → 自动混合最强模型组合，可对比多模型，质量最高
- **仅一键** → 只用该 provider 模型，质量受限
- 前端设置弹窗（齿轮图标）可配 OpenAI/Anthropic/Gemini 并显示 screenshot preview 是否可用
- **Replicate 只能在 .env 配**，前端弹窗不支持

### 2.6 验证安装

1. 后端启动无报错，访问 `http://localhost:7001` 有响应
2. 前端 5173 加载，设置弹窗显示各 key 状态 + "screenshot preview: available"
3. 上传一张截图，能流式输出代码，右侧出现预览

---

## 三、使用最佳实践

### 3.1 基本工作流
1. 选目标栈（默认 HTML+Tailwind）
2. 上传截图 / 粘贴 Figma 链接 / 录制网站操作
3. 流式查看生成代码（左原图右预览）
4. 用 CodeMirror 直接改代码即时预览
5. 满意后复制导出

### 3.2 模型选择策略

| 需求 | 推荐模型 | 说明 |
|---|---|---|
| 最高质量还原 | Gemini 3.1 Pro Preview | README 标注为 best |
| 平衡速度/成本 | Gemini 3 Flash / GPT-5.4 Mini | 日常截图足够 |
| 复杂结构还原 | Claude Opus 4.8 | 长上下文 + 推理强 |
| 对比择优 | 四键全配，同图多 variant | 选最贴近原图的 |

### 3.3 场景技巧
- **截图还原**：配 Gemini（素材提取复用真实 logo/图片，保真度高）
- **Figma → 代码**：直接贴 Figma 链接，无需导出截图
- **录屏转原型**：必须配 Gemini（视频模式依赖它）+ ffmpeg；先录网站交互再转功能性原型
- **图像精修**：配 Replicate，用 `edit_image` / `remove_background`

### 3.4 Screenshot Preview（自检，建议保持开启）
Playwright Chromium 装好后自动启用。agent 会渲染自己生成的页面并视觉核对——显著提升还原准确度。若 Chromium 缺失，该工具被静默跳过（设置弹窗可见状态）。

---

## 四、典型场景方案（通用）

### 场景 1：纯本地开发定制
**目标**：改 prompt / 换模型默认值 / 加自定义输出栈。
- 走方式 B（本地开发）
- 改 `backend/prompts/` 目录下提示词，针对你的栈优化
- 改 `backend/config.py` 调整默认模型与参数
- 接 Langfuse（`backend/` 内已含依赖）追踪每次生成的 prompt/成本/质量

### 场景 2：团队部署共享
**目标**：团队多人共用一套后端，key 不下发到个人浏览器。
- 走 Docker 部署到内网服务器，`.env` 放服务器侧
- 前端 `.env.local` 的 `VITE_WS_BACKEND_URL` / `VITE_HTTP_BACKEND_URL` 指向服务器 IP，如 `http://124.10.20.1:7001`
- 各成员浏览器只需访问前端地址，无需各自配 key
- 建议在 provider 侧设用量上限，防成本失控

### 场景 3：集成到设计→代码工作流
**目标**：把生成结果接入现有项目而非独立预览。
- 选与现有项目一致的输出栈（如 React+Tailwind）
- 生成后在 CodeMirror 复制代码到现有项目
- 注意：生成代码是**原型级**，无语义化、无 a11y、可能有硬编码，需人工审查后再合并
- 可用 `backend/run_evals.py` 跑评测集量化不同模型在你常用 UI 类型上的质量，选最优模型

---

## 五、常见问题排错（Windows 为主）

| 问题 | 解决 |
|---|---|
| 后端报 UTF-8 错误 | Windows 用 Notepad++ 打开 `.env` → 编码 → UTF-8（无 BOM） |
| OpenAI 403 / 地区限制 | 设 `OPENAI_BASE_URL=https://代理域名/v1`（必须含 `/v1`），写 .env 或前端设置弹窗 |
| 改后端端口不生效 | 同步改 `frontend/.env.local` 的 `VITE_WS_BACKEND_URL` 与 `VITE_HTTP_BACKEND_URL` |
| Playwright Chromium 装不上 | Windows 一般无系统依赖问题；Linux 需 `--with-deps` + sudo/apt |
| GPT-4 Vision 无权限 | OpenAI 充值 ≥$5 → Tier 1，最多等 30 分钟生效（见 Troubleshooting.md） |
| 视频模式不可用 | 必须配 `GEMINI_API_KEY` + 装 ffmpeg |
| `edit_image`/`remove_background` 不可用 | 必须配 `REPLICATE_API_KEY`（仅 .env 可配） |
| Ollama 本地模型质量差 | README 明确不推荐，建议用官方 API |

---

## 六、风险与限制

- **HIGH**：API Key 成本——多键混合 + 视频 + 图像生成，单次还原可能消耗较多 token；建议设 provider 侧用量上限
- **MEDIUM**：Windows 编码/路径问题（.env 必须 UTF-8 无 BOM；moviepy 依赖 ffmpeg）
- **MEDIUM**：生成代码非生产级——无语义化、无 a11y、可能有硬编码，适合原型/起手架，合并前需人工审查
- **LOW**：端口冲突（前端 5173 / 后端 7001）

---

## 七、可选增强

- **Langfuse**（`langfuse ^3.0.2` 已内置）：接入可观测性，追踪每次生成的 prompt/成本/质量
- **自定义 prompt**：`backend/prompts/` 目录改提示词，针对你的栈优化
- **Evals**：`backend/run_evals.py` / `backend/run_image_generation_evals.py` 跑评测集量化模型质量
- **OpenAI 代理**：`OPENAI_BASE_URL` 支持代理（需含 `/v1`），解决地区限制

---

## 八、实测部署记录（DashScope qwen3.7-plus）

> 本节为 2026-06-22 在 Windows 11 + Docker Desktop 环境的实际部署与复测记录，记录踩坑与修复，供复用参考。

### 8.1 部署概况

| 维度 | 内容 |
|---|---|
| 环境 | Windows 11 + Docker Desktop |
| 模型 | DashScope qwen3.7-plus（经 Anthropic 兼容端点） |
| Anthropic 兼容端点 | `https://coding.dashscope.aliyuncs.com/apps/anthropic` |
| 前端端口 | 宿主 5174 → 容器 5173 |
| 后端端口 | 7001 |
| 配置文件 | 项目根 `.env`（UTF-8 无 BOM） |

### 8.2 启动命令与前后端地址

**Docker 部署**（项目根目录）：

| 操作 | 命令 |
|---|---|
| 首次构建启动 | `docker-compose up -d --build` |
| 改 `.env` 后重启 | `docker-compose up -d --force-recreate` |
| 查看日志 | `docker-compose logs -f backend` / `docker-compose logs -f frontend` |
| 停止 | `docker-compose down` |

> ⚠️ `docker-compose restart` **不会重载** `env_file`，改 `.env` 后必须用 `up -d --force-recreate`。

**前后端访问地址**：

| 服务 | 地址 |
|---|---|
| 前端（Docker） | http://localhost:5174 |
| 后端 HTTP（Docker） | http://localhost:7001 |
| 后端 WebSocket | ws://localhost:7001/generate-code |

**本地开发模式**（改代码热重载）：

| 操作 | 命令 |
|---|---|
| 后端 | `cd backend && poetry run uvicorn main:app --reload --port 7001` |
| 前端 | `cd frontend && yarn && yarn dev` → http://localhost:5173 |
| 前端连后端 | `frontend/.env.local` 配 `VITE_WS_BACKEND_URL=ws://localhost:7001` 与 `VITE_HTTP_BACKEND_URL=http://localhost:7001` |

### 8.3 `.env` 配置（DashScope 实测）

```
ANTHROPIC_API_KEY=sk-sp-xxx
ANTHROPIC_BASE_URL=https://coding.dashscope.aliyuncs.com/apps/anthropic
BACKEND_PORT=7001
```

> ⚠️ 不要在 `.env` 放失效的 `OPENAI_API_KEY`：Claude Code / 后端若同时读到，会优先用 OpenAI key 报 403/variantError。DashScope 单 provider 部署时只配 Anthropic 两项即可。

### 8.4 过程问题与修复（7 个坑）

| # | 问题 | 根因 | 修复 |
|---|---|---|---|
| 1 | CodeMirror TS 类型冲突，前端编译失败 | `@codemirror/language@6.12.3` 嵌套独立 `@codemirror/view` 与顶层 6.41.1 的 private field `dispatchTransactions` 不兼容 | `frontend/package.json` 加 `"resolutions": {"@codemirror/view": "6.41.1"}` 强制单一版本 |
| 2 | DashScope HTTP 413，生成中途退出 | Anthropic 兼容端点请求体 ≤6MB；111111.png 1920×1080 → 1.69MB base64 + system prompt 超 6MB | `backend/agent/providers/anthropic/image.py` 的 `CLAUDE_MAX_IMAGE_DIMENSION` 7990→1568，触发压缩，base64 1.69MB→0.28MB |
| 3 | DashScope 模型名不兼容 / thinking 报错 | provider 硬编码 Claude 模型名；`thinking:{"type":"adaptive"}` DashScope 不支持 | `backend/agent/providers/anthropic/provider.py` 全改 `qwen3.7-plus`，`THINKING_MODELS`/`ADAPTIVE_THINKING_MODELS` 置空 |
| 4 | variantError "Incorrect OpenAI key" | 系统过期 `OPENAI_API_KEY`；`.env` 加后 `restart` 不重载 env_file | 删 `OPENAI_API_KEY` + `docker-compose up -d --force-recreate` |
| 5 | 前端 5173 被占用 | 宿主 node 进程占 5173 | `docker-compose.yml` 改 `5174:5173` |
| 6 | 测试脚本 413 误判 | `"413" in str(msg)` 误匹配数字子串 | 改为只在 `variantError`/`error` 文本精确匹配 "413"/"Request Entity Too Large" |
| 7 | 部分 variant 返回反问文本非 HTML | 4 路并偶发 LLM 未识别截图 | 保存逻辑只写含 `<html`/`<!doctype`/`<div` 的 variant，其余入 errors.txt |

**关键经验**：
- DashScope Anthropic 兼容端点有 **6MB 总请求体限制**（与单图 5MB 限制独立），大图必须先压缩到 1568px 长边以内
- Yarn `resolutions` 字段可强制整棵依赖树单一版本，解决 transitive dependency 重复实例
- WebSocket 关闭码 1000 是正常关闭；variant 全失败会触发 WS 关闭，不是 WS 关闭导致 variant 失败
- `docker-compose restart` ≠ 重新加载 env_file，改环境变量必须 `--force-recreate`

### 8.5 生成结果打包

复测脚本 `D:\mydoc\workskill\s2c-retest-111111.py` 生成 4 个 variant HTML，打包交付：

| 项 | 值 |
|---|---|
| 打包路径 | `D:\mydoc\workskill\s2c-output.zip`（16.9 KB） |
| 输出目录 | `D:\mydoc\workskill\s2c-output\` |
| 输入图 | `C:\Users\wuyan\Desktop\111111.png` |
| 输出栈 | html_css |
| variant 数 | 4（全部成功生成有效 HTML，0 错误，0 个 413） |

**包内文件**：

| 文件 | 大小 |
|---|---|
| variant-0.html | 23,271 字节 |
| variant-1.html | 23,570 字节 |
| variant-2.html | 19,377 字节 |
| variant-3.html | 19,377 字节 |
| README.txt | 610 字节 |

解压后双击任一 `variant-*.html` 可在浏览器预览生成效果。

### 8.6 源码改动清单（DashScope 适配）

| 文件 | 改动 |
|---|---|
| `backend/agent/providers/anthropic/provider.py` | `ANTHROPIC_MODEL_CONFIG` 全部 `api_name` 改 `qwen3.7-plus`；`THINKING_MODELS`/`ADAPTIVE_THINKING_MODELS` 置空 |
| `backend/agent/providers/anthropic/image.py` | `CLAUDE_MAX_IMAGE_DIMENSION` 7990→1568 |
| `frontend/package.json` | 加 `"resolutions": {"@codemirror/view": "6.41.1"}` |
| `docker-compose.yml` | 前端端口 `5173:5173`→`5174:5173` |
| `.env` | 仅 `ANTHROPIC_API_KEY` + `ANTHROPIC_BASE_URL` + `BACKEND_PORT` |

---

## 附：复杂度评估

- 安装：30–60 min（Docker 最快，本地开发需配 Poetry/Node/ffmpeg）
- 使用：即开即用，学习成本低
- 整体复杂度：**LOW–MEDIUM**
