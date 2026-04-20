# Summarize Skill 最佳实践

> 基于阿里云 Dashscope Coding Plan 的文本/文档总结方案

## 概览

本文档介绍如何在 Windows 环境下，使用 `summarize` CLI + 阿里云 Dashscope coding plan API 对本地文档（docx/pdf/txt 等）或网页进行智能总结。

### 技术链路

```
文档文件 → python-docx 提取文本 → summarize CLI → 阿里云 Dashscope (qwen3.6-plus) → 中文摘要
```

---

## 1. 安装

### 1.1 安装 summarize CLI

```bash
# 设置淘宝镜像（中国境内网络加速）
npm config set registry https://registry.npmmirror.com

# 全局安装
npm install -g @steipete/summarize

# 验证
summarize --version
```

### 1.2 安装文档预处理工具

#### python-docx（用于 .docx 文件）

```bash
"C:\Users\wuyan\.conda\envs\picproject\python.exe" -m pip install python-docx
```

#### uv / uvx（用于其他格式自动转换）

```bash
"C:\Users\wuyan\.conda\envs\picproject\python.exe" -m pip install uv

# 验证
uvx --version
```

---

## 2. 配置

### 2.1 环境变量

在你的 `.claude/settings.json` 的 `env` 部分确认以下配置：

```json
{
  "env": {
    "ANTHROPIC_API_KEY": "sk-sp-你的dashscope_coding_plan_key",
    "ANTHROPIC_BASE_URL": "https://coding.dashscope.aliyuncs.com/apps/anthropic",
    "ANTHROPIC_MODEL": "qwen3.6-plus",
    "UVX_PATH": "C:\\Users\\wuyan\\.local\\bin\\uvx"
  }
}
```

> **关键说明：**
> - `ANTHROPIC_API_KEY` 使用 Dashscope coding plan 的 Key（`sk-sp-` 开头），不是标准 Dashscope Key（`sk-` 开头）
> - `ANTHROPIC_BASE_URL` 必须指向 `coding.dashscope.aliyuncs.com/apps/anthropic`，不是标准 Dashscope 端点
> - 模型名称使用 `anthropic/qwen3.6-plus`（summarize 的模型标识格式）

### 2.2 可选：默认配置

创建 `~/.summarize/config.json`：

```json
{
  "model": "anthropic/qwen3.6-plus",
  "output": {
    "language": "zh",
    "length": "medium"
  }
}
```

---

## 3. 使用

### 3.1 总结 .docx 文件

由于 Windows 环境下 `uvx` 对 `.docx` 的直接处理可能存在问题，推荐先用 `python-docx` 提取文本再管道传入：

```bash
"C:\Users\wuyan\.conda\envs\picproject\python.exe" -c "
import docx, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
doc = docx.Document('文件路径.docx')
for table in doc.tables:
    for row in table.rows:
        cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
        if cells:
            print(' | '.join(cells))
for p in doc.paragraphs:
    if p.text.strip():
        print(p.text.strip())
" | summarize - --model "anthropic/qwen3.6-plus"
```

### 3.2 总结网页 URL

```bash
summarize "https://example.com/article" --model "anthropic/qwen3.6-plus"
```

### 3.3 总结本地文本文件

```bash
summarize "C:\path\to\file.txt" --model "anthropic/qwen3.6-plus"
```

### 3.4 总结 YouTube 视频

```bash
summarize "https://youtu.be/xxx" --youtube auto --model "anthropic/qwen3.6-plus"
```

### 3.5 仅提取内容（不总结）

```bash
summarize "https://example.com" --extract --model "anthropic/qwen3.6-plus"
```

---

## 4. 常用参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--model` | 指定 LLM 模型 | `anthropic/qwen3.6-plus` |
| `--length` | 摘要长度 | `short\|medium\|long\|xl\|xxl\|20000` |
| `--language` | 输出语言 | `zh\|en\|auto` |
| `--extract` | 仅提取，不总结 | — |
| `--json` | 输出 JSON 格式 | — |
| `--verbose` | 显示详细进度 | — |
| `--timeout` | 超时设置 | `2m\|5m` |
| `--prompt` | 自定义提示词 | `"请用3个要点总结"` |

---

## 5. 常见问题

### Q1: npm install 网络错误

```
npm error network This is a problem related to network connectivity
```

**解决：** 设置淘宝镜像源

```bash
npm config set registry https://registry.npmmirror.com
```

### Q2: 找不到 uvx/markitdown

```
Missing uvx/markitdown for preprocessing ...
```

**解决：** 安装 uv 并设置路径

```bash
"C:\Users\wuyan\.conda\envs\picproject\python.exe" -m pip install uv
# 设置环境变量 UVX_PATH
```

### Q3: API 返回 401

```
OpenAI API error (401) / Anthropic API error (401)
```

**解决：** 确认使用正确的 Dashscope coding plan Key（`sk-sp-` 开头），不是标准 Dashscope Key（`sk-` 开头）。

### Q4: 模型返回空输出

```
LLM returned an empty summary
```

**解决：** 确认 `ANTHROPIC_BASE_URL` 指向 `coding.dashscope.aliyuncs.com/apps/anthropic`，不是标准端点。某些模型名称可能不被支持，尝试 `anthropic/qwen3.6-plus`。

---

## 6. 参考

- summarize 项目: https://github.com/steipete/summarize
- 阿里云 Dashscope: https://help.aliyun.com/zh/model-studio/
- Dashscope coding plan: https://coding.dashscope.aliyuncs.com/
