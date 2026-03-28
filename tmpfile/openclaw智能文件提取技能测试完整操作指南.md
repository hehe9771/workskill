# openclaw智能文件提取技能测试完整操作指南

## 一、环境概览

### openclaw系统信息
- 访问地址：https://bot-uat.fh-lease.com/
- 登录秘钥：fL2x8Pq9RgTjW7nH5kYv3cM1bN6aX4zQwE9dF0rS5tV8yU2i
- 实际版本：v2026.3.23 (页面显示v2026.3.13是因为挂载文件未修改)
- 测试群ID：oc_7fe75f76d0a981e6af83460be24343a6
- 应用ID：cli_a93d7cb8a0fa1bb6

### MCP服务信息
- 应用名称：tool-mcp-server
- 程序目录：/app
- 入口文件：mcp_server.py
- 注意事项：该服务通过流水线发版，修改代码重启容器会消失，修改过的代码需备份给管理员做更新

### 集群信息
- 操作系统：Alibaba Cloud Linux 3.2104 LTS 64位
- 集群版本：v1.24.6-aliyun.1 containerd://1.6.38
- 空间：ai

## 二、技能和部署的应用

### 部署应用
- openclaw-gateway（用于聊天和处理复杂任务）
- openclaw-cron（用于完成定时任务）

### 重要ConfigMap
- openclaw-config: ai/openclaw.json
- openclaw-mcp-config: ai/mcporter.json
- openclaw-skill-config: 各种技能配置文件

### 关键环境变量（openclaw-gateway）
- CLAWDBOT_GATEWAY_TOKEN: fL2x8Pq9RgTjW7nH5kYv3cM1bN6aX4zQwE9dF0rS5tV8yU2i
- FEISHU_APP_SECRET: deCbzMgI0Xld5Nb5VomJkgqKM57i5dXJ
- FEISHU_APP_ID: cli_a93d7cb8a0fa1bb6
- API_TOKEN: sk-sp-fd06600a49e34c98855e866496101941
- CHAT_MODEL: qwen3.5-plus

## 三、智能文件提取技能信息

### 技能名称
- `extractor-smart`

### 支持的文件格式
- PDF ✅ (单文件或ZIP内)
- Word (doc/docx) ✅ (单文件或ZIP内)
- 图片 (png/jpg/jpeg) ✅ (单文件或ZIP内)
- ZIP ✅ (自动解压处理)
- GZ/TAR.GZ ✅ (自动解压处理)

### 核心功能
1. 动态提示词生成 - 根据飞书模板列名自动生成优化提示词
2. 批量处理 - 支持ZIP压缩包内多文件批量提取
3. 数据写入 - 自动将提取结果写入飞书模板表格
4. 多场景适配 - 支持简历、合同、票据等多种文档类型

## 四、测试执行计划

### 测试用例
1. 单份简历 PDF 提取
2. ZIP 批量简历提取
3. 单份合同 PDF 提取
4. ZIP 批量合同提取
5. 单张票据提取
6. ZIP 批量票据提取

### 执行步骤
1. 在飞书群 oc_7fe75f76d0a981e6af83460be24343a6 中进行测试
2. 使用指令 "@智能助手 智能提取" 触发机器人
3. 上传相应文件进行测试
4. 验证结果是否正确写入飞书表格

## 五、当前创建的测试资源

### 测试文件位置
- D:\mydoc\workskill\简历-张三.docx
- D:\mydoc\workskill\简历-李雨桐.docx
- D:\mydoc\workskill\2025年年度融资租赁合同.docx
- D:\mydoc\workskill\合同补充协议.docx
- D:\mydoc\workskill\票据_李四.docx
- D:\mydoc\workskill\票据_王五.docx
- D:\mydoc\workskill\简历批量测试-word.zip
- D:\mydoc\workskill\合同批量测试-word.zip
- D:\mydoc\workskill\票据批量测试-word.zip

### 相关文档
- D:\mydoc\workskill\智能文件提取技能操作手册.md
- D:\mydoc\workskill\飞书模板表格设置说明.md
- D:\mydoc\workskill\openclaw_extractor_smart测试报告.md

## 六、MCP服务文件备份

### 需要备份的重要文件
- /app/mcp_server.py (主入口文件)
- /app/config/mcporter.json (MCP配置文件)

### 操作说明
在进行任何MCP服务修改之前，请确保备份原始文件，并在测试完成后将备份发给管理员进行正式更新。

## 七、群聊测试步骤

1. 进入群聊：oc_7fe75f76d0a981e6af83460be24343a6
2. @智能助手 并上传测试文件
3. 发送指令："智能提取" 或 "智能提取文件"
4. 确认机器人响应和处理结果
5. 检查飞书表格中的数据写入情况
6. 重复测试不同类型的文档和ZIP压缩包

## 八、问题排查

### 飞书授权问题
- 检查 FEISHU_APP_SECRET 和 FEISHU_APP_ID 是否正确配置
- 验证 API_TOKEN 是否有效

### 提取准确性问题
- 检查 mcporter.json 中的配置
- 验证 CHAT_MODEL (qwen3.5-plus) 是否正常工作

### 群组权限问题
- 确认机器人已在测试群中被添加
- 验证机器人是否有读取消息和发送消息的权限

## 九、安全注意事项

1. 所有的API密钥和令牌应妥善保管
2. 修改MCP服务代码时要注意备份
3. 测试完成后清理敏感信息
4. 遵循最小权限原则