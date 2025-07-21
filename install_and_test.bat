@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM χ²-DFD 深度伪造检测系统 - Windows一键安装和测试脚本
REM 自动安装依赖并运行基础测试

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║            χ²-DFD 深度伪造检测系统                           ║
echo ║          Windows一键安装和测试脚本                           ║
echo ║                                                              ║
echo ║    🎯 可解释的深度伪造检测                                   ║
echo ║    🔍 基于论文 χ²-DFD 框架实现                               ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM 检查Python是否安装
echo [INFO] 检查Python版本...
python --version >nul 2>&1
if !errorlevel! neq 0 (
    echo [ERROR] 未找到Python，请先安装Python 3.8或更高版本
    echo         下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 获取Python版本
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [SUCCESS] Python版本: %PYTHON_VERSION%

REM 检查pip
echo [INFO] 检查pip...
pip --version >nul 2>&1
if !errorlevel! neq 0 (
    echo [ERROR] 未找到pip，请检查Python安装
    pause
    exit /b 1
)
echo [SUCCESS] pip已找到

REM 询问是否创建虚拟环境
echo.
echo [QUESTION] 是否创建虚拟环境？(推荐) [Y/n]
set /p CREATE_ENV=
if "!CREATE_ENV!"=="" set CREATE_ENV=Y

if /i "!CREATE_ENV!"=="Y" (
    echo [INFO] 创建虚拟环境...
    if not exist "deepfake_env" (
        python -m venv deepfake_env
        echo [SUCCESS] 虚拟环境创建成功
    ) else (
        echo [WARNING] 虚拟环境已存在，跳过创建
    )
    
    echo [INFO] 激活虚拟环境...
    call deepfake_env\Scripts\activate.bat
    echo [SUCCESS] 虚拟环境已激活
) else (
    echo [WARNING] 跳过虚拟环境创建
)

echo.
echo [INFO] 升级pip...
python -m pip install --upgrade pip >nul 2>&1
echo [SUCCESS] pip已升级

echo.
echo [INFO] 安装项目依赖...
echo [WARNING] 这可能需要几分钟时间，请耐心等待...

REM 检查requirements.txt是否存在
if not exist "requirements.txt" (
    echo [ERROR] requirements.txt文件不存在
    pause
    exit /b 1
)

REM 尝试使用国内镜像安装依赖
echo [INFO] 正在安装依赖包...
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt >nul 2>&1
if !errorlevel! equ 0 (
    echo [SUCCESS] 依赖安装成功（使用清华镜像）
) else (
    echo [WARNING] 镜像安装失败，尝试默认源...
    pip install -r requirements.txt >nul 2>&1
    if !errorlevel! equ 0 (
        echo [SUCCESS] 依赖安装成功（使用默认源）
    ) else (
        echo [ERROR] 依赖安装失败
        echo [INFO] 请尝试手动安装：pip install -r requirements.txt
        pause
        exit /b 1
    )
)

echo.
echo [INFO] 运行基础结构测试...
if exist "code\basic_test.py" (
    python code\basic_test.py
    echo [SUCCESS] 基础测试完成
) else (
    echo [ERROR] 基础测试文件不存在：code\basic_test.py
    pause
    exit /b 1
)

echo.
echo [QUESTION] 是否运行完整功能测试？(可能需要较长时间) [y/N]
set /p RUN_FULL_TEST=
if /i "!RUN_FULL_TEST!"=="Y" (
    echo [INFO] 运行功能测试...
    if exist "code\test_validation.py" (
        python code\test_validation.py
        echo [SUCCESS] 功能测试完成
    ) else (
        echo [WARNING] 功能测试文件不存在，跳过功能测试
    )
)

echo.
echo [QUESTION] 是否运行检测演示？[Y/n]
set /p RUN_DEMO=
if "!RUN_DEMO!"=="" set RUN_DEMO=Y

if /i "!RUN_DEMO!"=="Y" (
    echo.
    echo ═══════════════════════════════════════
    echo 开始演示 χ²-DFD 深度伪造检测系统
    echo ═══════════════════════════════════════
    
    if exist "code\main_detector.py" (
        python code\main_detector.py
        echo [SUCCESS] 演示完成！
    ) else (
        echo [ERROR] 主检测器文件不存在：code\main_detector.py
        pause
        exit /b 1
    )
)

echo.
echo ═══════════════════════════════════════
echo 🎉 χ²-DFD 安装成功！
echo ═══════════════════════════════════════
echo.
echo 📋 使用方法：
echo   🔍 检测单张图像：python code\main_detector.py path\to\image.jpg
echo   📁 批量检测：    python code\main_detector.py
echo   🧪 运行测试：    python code\test_validation.py
echo.
echo 📚 文档：
echo   📖 快速开始：    type QUICK_START.md
echo   📊 技术文档：    type 项目总结报告.md
echo   🛠️ 详细安装：    type 本地运行指南.md
echo.
echo 💡 提示：下次使用前请激活虚拟环境
if exist "deepfake_env\Scripts\activate.bat" (
    echo   deepfake_env\Scripts\activate.bat
)
echo.
echo ❓ 如果遇到问题：
echo   1. 检查Python版本 ≥ 3.8
echo   2. 确认依赖安装成功
echo   3. 查看文档获取帮助
echo.

pause
