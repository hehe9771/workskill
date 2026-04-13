# 视频到Markdown转换操作流程

## 准备阶段

### 环境检查
1. 检查是否安装了opencli
2. 验证openai-whisper技能是否可用
3. 确认convert-plaintext-to-md技能是否已添加
4. 检查mermaid-diagrams技能是否已安装

### 输入验证
1. 验证视频URL格式是否正确
2. 测试视频链接是否可访问
3. 检查视频大小是否在处理范围内

## 执行阶段

### 第一步：视频下载
1. 使用opencli下载指定的视频
   ```
   opencli download [VIDEO_URL] -o [OUTPUT_PATH]
   ```
2. 验证下载是否成功
3. 记录视频信息（时长、大小、格式等）

### 第二步：音频提取
1. 使用openai-whisper技能提取音频并转换为文本
   ```
   npx skills add https://github.com/steipete/clawdis --skill openai-whisper [VIDEO_FILE]
   ```
2. 验证文本输出质量
3. 对文本进行初步清理和分段

### 第三步：文本转Markdown
1. 使用convert-plaintext-to-md技能转换文本
   ```
   npx skills add https://github.com/github/awesome-copilot --skill convert-plaintext-to-md [TEXT_FILE]
   ```
2. 确保章节划分清晰
3. 验证markdown格式正确性

### 第四步：图表生成
1. 分析markdown文档的章节结构
2. 使用mermaid-diagrams技能为每章生成图表
   ```
   npx skills add https://github.com/softaworks/agent-toolkit --skill mermaid-diagrams [MARKDOWN_FILE]
   ```
3. 将生成的图表插入到相应章节中
4. 验证图表的准确性和相关性

## 验证阶段

### 输出验证
1. 检查最终markdown文档的完整性
2. 验证所有图表都已正确嵌入
3. 确认章节划分清晰且内容完整

### 日志记录
1. 记录每个步骤的执行时间和状态
2. 记录错误信息（如果有的话）
3. 生成处理摘要报告

## 异常处理

### 网络错误
- 重试机制：最多重试3次
- 降级策略：尝试备用下载方法

### 格式错误
- 验证每个中间文件的格式
- 使用备用转换方法

### 超时错误
- 设置合理的超时时间
- 分段处理大文件