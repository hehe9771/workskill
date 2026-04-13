---
name: videobook
description: 自动化视频内容处理技能，将公网视频链接转换为带Mermaid图表的结构化Markdown文档
---

# videobook 技能

自动化将公网视频链接转换为带图表的 Markdown 文档。整个流程分为 4 个步骤，其中步骤 3（文本转 Markdown）和步骤 4（图表生成）由 LLM 和 Skill 驱动，禁止使用脚本处理。

> **技能目录**：本 skill 位于 `~/.claude/skills/videobook/`。以下步骤中所有相对路径均相对于此目录。

## 执行流程

**收到视频链接后，按顺序执行以下全部 4 个步骤，不要跳过任何一步。**

### 步骤 1：视频下载

1. 运行依赖检查：
   ```bash
   bash ~/.claude/skills/videobook/scripts/validation/check_dependencies.sh
   ```
2. 创建输出目录并下载视频：
   ```bash
   mkdir -p output
   bash ~/.claude/skills/videobook/scripts/data-processing/download_video.sh "<video_url>" "output/video.mp4"
   ```
3. 验证：`output/video.mp4` 文件存在且大小 > 0

**失败降级：** 如 opencli 不可用，脚本自动使用 `yt-dlp`。

### 步骤 2：音频提取为 TXT

1. 运行提取脚本：
   ```bash
   bash ~/.claude/skills/videobook/scripts/data-processing/extract_audio.sh "output/video.mp4" "output/transcript.txt"
   ```
2. 验证：`output/transcript.txt` 存在且包含非空文本

### 步骤 3：TXT 转 Markdown（LLM 直接处理，禁止脚本）

1. 读取模板文件：`~/.claude/skills/videobook/assets/templates/documents/output_format_template.md`
2. 读取音频转录文本：`output/transcript.txt`
3. **作为 LLM，直接按照模板的结构化要求将 txt 内容转换为 Markdown**：
   - 将内容划分为有意义的章节（每章约 500-800 字）
   - 每章包含：章节标题、内容概要、关键词汇、章节内容、本章要点
   - 提取全局专业术语表、个人思考和行动项
4. 将生成的 Markdown 写入 `output/output.md`

**关键要求：此步骤必须由 LLM 直接处理文本并写入文件，不得使用任何脚本。**

### 步骤 4：为每个章节生成 Mermaid 图表（LLM 直接处理，禁止脚本）

1. 读取 `output/output.md`
2. 识别所有章节标题（`## 第X章: ...`）
3. 根据每个章节的内容特征选择合适的图表类型：

   | 内容特征 | Mermaid 类型 |
   |---------|-------------|
   | 流程、步骤、阶段 | `flowchart TD` |
   | 交互、对话、消息传递 | `sequenceDiagram` |
   | 类、对象、继承关系 | `classDiagram` |
   | 实体、关系、属性 | `erDiagram` |
   | 系统架构、组件层次 | `C4Context` / `C4Container` |
   | 状态、转换、事件 | `stateDiagram-v2` |
   | 版本控制、分支合并 | `gitGraph` |
   | 时间线、项目计划 | `gantt` |
   | 比例、占比、分布 | `pie` |
   | 用户旅程、体验流程 | `journey` |
   | 思维导图、知识梳理 | `mindmap` |
   | 需求关系、依赖 | `requirementDiagram` |

4. 为每个章节生成对应的 Mermaid 代码块，在章节内容后插入：
   ```markdown
   ### 图表

   ```mermaid
   [Mermaid 图表代码]
   ```
   ```
5. 更新 `output/output.md`，确保每个章节至少包含一个 Mermaid 图表

**关键要求：此步骤由 LLM 直接生成 Mermaid 代码并写入文件，参考 mermaid-diagrams skill 的语法规范。**

## 所需输入

- **必填**：公网视频链接（如 Bilibili、YouTube 等平台的视频地址）
- **可选**：输出目录路径（默认为当前工作目录下的 `output` 文件夹）
- **可选**：图表类型偏好设置

## 依赖文件

| 文件 | 用途 |
|------|------|
| `<skill-dir>/scripts/data-processing/download_video.sh` | 视频下载脚本 |
| `<skill-dir>/scripts/data-processing/extract_audio.sh` | 音频提取脚本 |
| `<skill-dir>/scripts/validation/check_dependencies.sh` | 依赖检查脚本 |
| `<skill-dir>/scripts/validation/validate_video_url.sh` | URL 格式验证 |
| `<skill-dir>/assets/templates/documents/output_format_template.md` | Markdown 格式模板 |

## 输出产物

| 产物 | 说明 |
|------|------|
| 视频文件（.mp4） | 步骤 1 产物，临时文件 |
| 音频转录文本（.txt） | 步骤 2 产物 |
| 结构化 Markdown（.md） | 步骤 3 产物，带章节划分 |
| 带图表 Markdown（.md） | 步骤 4 最终产物，含 Mermaid 图表 |

## 成功标准

1. 成功下载测试视频（如 `https://www.bilibili.com/video/BV18vmxB3EBd/`）
2. 成功将音频提取为 txt 文件，包含有效文本内容
3. txt 转换为格式良好的 Markdown，章节划分明确
4. Markdown 中每个章节都生成了对应的 Mermaid 图表
5. 生成的文档具有良好的可读性和视觉呈现效果
6. 所有处理步骤均无错误

## 前置依赖

- **opencli**：`npm install -g @jackwener/opencli`
- **yt-dlp**：`pip install yt-dlp`（opencli 下载视频的底层依赖）
- **Python + openai-whisper**：Python 环境需安装 `openai-whisper` 包
- **FFmpeg**：系统路径中可用或配置 `FFMPEG_BINARY` 环境变量
- **mermaid-diagrams skill**：`npx skills add https://github.com/softaworks/agent-toolkit --skill mermaid-diagrams`
