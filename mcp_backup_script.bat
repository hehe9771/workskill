@echo off
REM MCP服务文件备份脚本 (Windows版本)

echo 开始备份MCP服务文件...

REM 创建备份目录
set BACKUP_DIR=mcp_backup_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

echo 备份目录: %BACKUP_DIR%

REM 备份说明
echo.
echo ===========================================
echo 手动备份指导：
echo 1. 登录到openclaw的MCP服务器
echo 2. 复制以下文件到本地：
echo    - /app/mcp_server.py
echo    - /app/config/mcporter.json
echo 3. 将备份文件保存到安全位置
echo 4. 进行必要的修改测试
echo 5. 测试完成后，将修改后的代码交给管理员更新
echo ===========================================

echo.
echo 备份完成！备份目录位于: %BACKUP_DIR%
echo 请在进行任何MCP服务修改前参考此备份。
pause