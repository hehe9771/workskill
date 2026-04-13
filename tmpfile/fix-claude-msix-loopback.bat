@echo off
echo 需要管理员权限解除 Claude MSIX 网络隔离...
CheckNetIsolation.exe LoopbackExempt -a -n="Claude_pzs8sxrjxfjjc"
if %errorlevel% == 0 (
    echo 成功：已解除 Claude MSIX loopback 隔离
) else (
    echo 失败：请确认以管理员身份运行此脚本
)
echo.
echo 当前 loopback 豁免列表（验证）：
CheckNetIsolation.exe LoopbackExempt -s | findstr /i Claude
pause
