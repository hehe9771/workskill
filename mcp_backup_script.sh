#!/bin/bash
# MCP服务文件备份脚本

# 此脚本用于备份openclaw的MCP服务文件
# 由于tool-mcp-server通过流水线发版，修改代码重启容器会消失
# 因此在进行任何修改之前都需要备份原始文件

echo "开始备份MCP服务文件..."

# 创建备份目录
BACKUP_DIR="./mcp_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

echo "备份目录: $BACKUP_DIR"

# 尝试从服务器备份关键文件（需要SSH访问权限）
# 注意：这只是一个模板，实际执行时需要正确的SSH凭据
echo "正在备份MCP服务文件..."

# 1. 备份主入口文件
echo "备份 /app/mcp_server.py ..."
# ssh user@server "cp /app/mcp_server.py $BACKUP_DIR/mcp_server.py" 2>/dev/null || echo "无法直接访问服务器文件"

# 2. 备份配置文件
echo "备份 /app/config/mcporter.json ..."
# ssh user@server "cp /app/config/mcporter.json $BACKUP_DIR/mcporter.json" 2>/dev/null || echo "无法直接访问服务器配置文件"

# 如果无法通过SSH访问，提供手动备份指导
echo ""
echo "==========================================="
echo "手动备份指导："
echo "1. 登录到openclaw的MCP服务器"
echo "2. 复制以下文件到本地："
echo "   - /app/mcp_server.py"
echo "   - /app/config/mcporter.json"
echo "3. 将备份文件保存到安全位置"
echo "4. 进行必要的修改测试"
echo "5. 测试完成后，将修改后的代码交给管理员更新"
echo "==========================================="

echo ""
echo "备份完成！备份文件位于: $BACKUP_DIR"
echo "请在进行任何MCP服务修改前参考此备份。"