# videobook 技能

将公网视频链接自动转换为带 Mermaid 图表的结构化 Markdown 文档。

## 工作流程

| 步骤 | 说明 | 驱动方式 |
|------|------|---------|
| 1. 视频下载 | 从 URL 下载视频文件 | opencli / yt-dlp 脚本 |
| 2. 音频提取 | 视频音频转录为 txt | openai-whisper 脚本 |
| 3. TXT 转 Markdown | 按模板生成结构化文档 | LLM 提示词（禁止脚本） |
| 4. 图表生成 | 为每章生成 Mermaid 图表 | mermaid-diagrams skill（禁止脚本） |

## 前置依赖

- `opencli`: `npm install -g @jackwener/opencli`
- `yt-dlp`: `pip install yt-dlp`
- `openai-whisper`: Python 环境中安装
- `FFmpeg`: 系统可用
- `mermaid-diagrams skill`: `npx skills add https://github.com/softaworks/agent-toolkit --skill mermaid-diagrams`

## 快速开始

在 Claude Code 中提供视频链接即可触发此技能，例如：

```
请使用 videobook 技能处理这个视频：https://www.bilibili.com/video/BV18vmxB3EBd/
```

## 输出

- `{video}.mp4` - 下载的视频（临时文件）
- `{video}.txt` - 音频转录文本
- `{video}.md` - 最终的结构化 Markdown 文档，含章节和 Mermaid 图表
