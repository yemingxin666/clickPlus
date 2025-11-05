@echo off

REM =============================================
REM 自动请求管理员权限
REM =============================================
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"

if '%errorlevel%' NEQ '0' (
    echo 正在请求管理员权限...
    goto UACPrompt
) else (
    goto gotAdmin
)

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    del "%temp%\getadmin.vbs"
    exit /B

:gotAdmin
    if exist "%temp%\getadmin.vbs" ( del "%temp%\getadmin.vbs" )
    pushd "%CD%"
    CD /D "%~dp0"

REM =============================================
REM 开始主程序
REM =============================================
chcp 65001 > nul

echo ========================================
echo 🎯 鼠标动作录制器 v2.0 - GUI版本
echo ========================================
echo.

REM 检查虚拟环境
if not exist "venv\Scripts\python.exe" (
    echo ❌ 错误: 虚拟环境不存在！
    echo 请先运行 setup.bat 创建虚拟环境
    pause
    exit /b 1
)

REM 启动 GUI
echo ▶️  启动图形界面...
echo.
venv\Scripts\python.exe mouse_recorder_gui.py

if errorlevel 1 (
    echo.
    echo ❌ 程序运行出错！
    pause
)
