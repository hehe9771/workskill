@echo off
set CLAUDE_EXE=C:\Program Files\WindowsApps\Claude_1.1.5368.0_x64__pzs8sxrjxfjjc\app\claude.exe
set PROXY=http://127.0.0.1:7897

if exist "%CLAUDE_EXE%" (
    echo 启动 Claude 桌面端（代理: %PROXY%）...
    start "" "%CLAUDE_EXE%" --proxy-server=%PROXY%
) else (
    echo 未找到 Claude.exe，改用 MSIX 协议启动（无法传参，需依赖系统代理）...
    start "" explorer.exe "shell:appsFolder\Claude_pzs8sxrjxfjjc!App"
)
