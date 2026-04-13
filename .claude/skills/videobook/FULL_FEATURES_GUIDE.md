# videobook技能 - 视频转markdown图表工具

## 简介

videobook是一个自动化处理工具，旨在将公网视频链接的内容转换为带有图表的markdown文档。该技能通过四个主要步骤来实现这一目标：
1. 从公网视频链接下载视频
2. 提取视频中的音频并转换为文本文件
3. 将文本转换为格式化的markdown文档
4. 为每个章节生成对应的图表（支持类图、序列图、流程图等多种图表类型）

## 安装

```bash
# 部署技能
bash videobook/scripts/deployment/deploy_skill.sh
```

## 使用方法

### 基本用法
```bash
# 处理视频
videobook https://www.bilibili.com/video/BV18vmxB3EBd/
```

### 指定输出目录
```bash
# 指定输出目录
videobook -o ./my-output https://www.bilibili.com/video/BV18vmxB3EBd/
```

## 功能特色

### 1. 视频下载
- 支持多种视频平台（YouTube, Bilibili, Vimeo等）
- 使用opencli工具进行高效下载
- 验证下载完整性和格式兼容性

### 2. 音频提取
- 集成openai-whisper进行高质量音频转文本
- 自动处理多种音频格式
- 智能分割长视频为处理单元

### 3. 文本处理
- 智能识别章节标题和结构
- 保持原文档语义和逻辑关系
- 生成清晰的目录结构

### 4. 图表生成
- 自动分析内容生成对应的图表
- 支持9种以上图表类型：
  - 流程图 (Flowchart)
  - 序列图 (Sequence diagram)
  - 类图 (Class diagram)
  - 状态图 (State diagram)
  - 实体关系图 (Entity Relationship)
  - 甘特图 (Gantt chart)
  - 饼图 (Pie chart)
  - Git图 (Git graph)
  - C4上下文图 (C4 Context)
- 自动嵌入图表到对应章节

## 目录结构

```
videobook/
├── SKILL.md                    # 主配置文件
├── README.md                   # 用户文档
├── references/                 # 参考资料
│   ├── specifications/         # 技术规范
│   ├── policies/              # 政策文档
│   ├── procedures/            # 操作流程
│   └── standards/             # 标准规范
├── scripts/                   # 执行脚本
│   ├── setup/                 # 初始化脚本
│   ├── validation/            # 验证脚本
│   ├── data-processing/       # 数据处理脚本
│   └── deployment/            # 部署脚本
└── assets/                    # 模板和静态资源
    ├── templates/             # 模板文件
    ├── static/                # 静态资源
    ├── data/                  # 数据文件
    └── themes/                # 主题文件
```

## 依赖项

- opencli（用于视频下载）
- openai-whisper（用于音频转文本）
- convert-plaintext-to-md（用于文本转markdown）
- mermaid-diagrams（用于生成图表）
- bash shell环境
- npm/node.js（用于运行相关技能）

## 输出格式

最终输出包含：
- 结构化的markdown文档
- 清晰的章节划分
- 生成的图表（使用Mermaid语法）
- 处理日志文件

## 错误处理

- 网络错误自动重试
- 格式错误降级处理
- 超时自动中断
- 临时文件自动清理

## 测试验证

所有功能模块都经过完整测试验证，确保：
- 视频下载成功
- 音频提取为txt成功
- txt转md格式正确且章节划分明确
- 每个章节都有对应的图表生成