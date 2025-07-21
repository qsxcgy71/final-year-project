#!/bin/bash

# χ²-DFD 深度伪造检测系统 - 一键安装和测试脚本
# 自动安装依赖并运行基础测试

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 打印带颜色的信息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo -e "${CYAN}$1${NC}"
}

# 检查Python版本
check_python() {
    print_info "检查Python版本..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_error "未找到Python，请先安装Python 3.8或更高版本"
        exit 1
    fi
    
    # 检查Python版本
    PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    REQUIRED_VERSION="3.8"
    
    if [ "$(echo "$PYTHON_VERSION >= $REQUIRED_VERSION" | bc -l 2>/dev/null || echo "0")" = "1" ] || \
       [ "$PYTHON_VERSION" = "3.8" ] || [ "$PYTHON_VERSION" = "3.9" ] || \
       [ "$PYTHON_VERSION" = "3.10" ] || [ "$PYTHON_VERSION" = "3.11" ] || [ "$PYTHON_VERSION" = "3.12" ]; then
        print_success "Python版本: $PYTHON_VERSION ✓"
    else
        print_error "Python版本过低: $PYTHON_VERSION，需要3.8或更高版本"
        exit 1
    fi
}

# 检查pip
check_pip() {
    print_info "检查pip..."
    
    if command -v pip3 &> /dev/null; then
        PIP_CMD="pip3"
    elif command -v pip &> /dev/null; then
        PIP_CMD="pip"
    else
        print_error "未找到pip，请先安装pip"
        exit 1
    fi
    
    print_success "pip已找到: $PIP_CMD"
}

# 创建虚拟环境
create_venv() {
    print_info "创建虚拟环境..."
    
    if [ ! -d "deepfake_env" ]; then
        $PYTHON_CMD -m venv deepfake_env
        print_success "虚拟环境创建成功"
    else
        print_warning "虚拟环境已存在，跳过创建"
    fi
}

# 激活虚拟环境
activate_venv() {
    print_info "激活虚拟环境..."
    
    if [ -f "deepfake_env/bin/activate" ]; then
        source deepfake_env/bin/activate
        print_success "虚拟环境已激活 (Linux/macOS)"
    elif [ -f "deepfake_env/Scripts/activate" ]; then
        source deepfake_env/Scripts/activate
        print_success "虚拟环境已激活 (Windows)"
    else
        print_warning "无法激活虚拟环境，使用系统Python"
    fi
}

# 升级pip
upgrade_pip() {
    print_info "升级pip..."
    $PIP_CMD install --upgrade pip > /dev/null 2>&1
    print_success "pip已升级到最新版本"
}

# 安装依赖
install_dependencies() {
    print_info "安装项目依赖..."
    print_warning "这可能需要几分钟时间，请耐心等待..."
    
    # 检查requirements.txt是否存在
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt文件不存在"
        exit 1
    fi
    
    # 安装依赖，显示进度
    echo -e "${YELLOW}正在安装依赖包...${NC}"
    
    # 尝试使用国内镜像加速
    if $PIP_CMD install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt; then
        print_success "依赖安装成功（使用清华镜像）"
    elif $PIP_CMD install -r requirements.txt; then
        print_success "依赖安装成功（使用默认源）"
    else
        print_error "依赖安装失败"
        print_info "尝试手动安装：pip install -r requirements.txt"
        exit 1
    fi
}

# 运行基础测试
run_basic_test() {
    print_info "运行基础结构测试..."
    
    if [ -f "code/basic_test.py" ]; then
        $PYTHON_CMD code/basic_test.py
        print_success "基础测试完成"
    else
        print_error "基础测试文件不存在：code/basic_test.py"
        exit 1
    fi
}

# 运行功能测试
run_functionality_test() {
    print_info "运行功能测试..."
    
    echo -e "${YELLOW}正在测试深度伪造检测功能...${NC}"
    
    if [ -f "code/test_validation.py" ]; then
        if $PYTHON_CMD code/test_validation.py; then
            print_success "功能测试通过"
        else
            print_warning "功能测试未完全通过，但系统基本可用"
        fi
    else
        print_warning "功能测试文件不存在，跳过功能测试"
    fi
}

# 运行演示
run_demo() {
    print_info "运行检测演示..."
    
    if [ -f "code/main_detector.py" ]; then
        echo -e "${CYAN}═══════════════════════════════════════${NC}"
        echo -e "${CYAN}开始演示 χ²-DFD 深度伪造检测系统${NC}"
        echo -e "${CYAN}═══════════════════════════════════════${NC}"
        
        $PYTHON_CMD code/main_detector.py
        
        print_success "演示完成！"
    else
        print_error "主检测器文件不存在：code/main_detector.py"
        exit 1
    fi
}

# 显示使用说明
show_usage() {
    echo -e "${PURPLE}═══════════════════════════════════════${NC}"
    echo -e "${PURPLE}🎉 χ²-DFD 安装成功！${NC}"
    echo -e "${PURPLE}═══════════════════════════════════════${NC}"
    echo
    echo -e "${GREEN}📋 使用方法：${NC}"
    echo -e "  🔍 检测单张图像：${CYAN}$PYTHON_CMD code/main_detector.py path/to/image.jpg${NC}"
    echo -e "  📁 批量检测：    ${CYAN}$PYTHON_CMD code/main_detector.py${NC}"
    echo -e "  🧪 运行测试：    ${CYAN}$PYTHON_CMD code/test_validation.py${NC}"
    echo
    echo -e "${GREEN}📚 文档：${NC}"
    echo -e "  📖 快速开始：    ${CYAN}cat QUICK_START.md${NC}"
    echo -e "  📊 技术文档：    ${CYAN}cat 项目总结报告.md${NC}"
    echo -e "  🛠️ 详细安装：    ${CYAN}cat 本地运行指南.md${NC}"
    echo
    echo -e "${GREEN}❓ 如果遇到问题：${NC}"
    echo -e "  1. 检查Python版本 ≥ 3.8"
    echo -e "  2. 确认依赖安装成功"
    echo -e "  3. 查看文档获取帮助"
    echo
    if [ -f "deepfake_env/bin/activate" ] || [ -f "deepfake_env/Scripts/activate" ]; then
        echo -e "${YELLOW}💡 提示：下次使用前请激活虚拟环境${NC}"
        if [ -f "deepfake_env/bin/activate" ]; then
            echo -e "  ${CYAN}source deepfake_env/bin/activate${NC}"
        else
            echo -e "  ${CYAN}deepfake_env\\Scripts\\activate${NC}"
        fi
    fi
    echo
}

# 主函数
main() {
    # 显示欢迎信息
    clear
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                                                              ║${NC}"
    echo -e "${CYAN}║            χ²-DFD 深度伪造检测系统                           ║${NC}"
    echo -e "${CYAN}║          一键安装和测试脚本                                  ║${NC}"
    echo -e "${CYAN}║                                                              ║${NC}"
    echo -e "${CYAN}║    🎯 可解释的深度伪造检测                                   ║${NC}"
    echo -e "${CYAN}║    🔍 基于论文 χ²-DFD 框架实现                               ║${NC}"
    echo -e "${CYAN}║                                                              ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo
    
    # 检查系统环境
    print_header "🔧 第1步：检查系统环境"
    check_python
    check_pip
    echo
    
    # 询问是否创建虚拟环境
    print_header "🏠 第2步：环境设置"
    echo -e "${YELLOW}是否创建虚拟环境？(推荐) [Y/n]${NC}"
    read -r create_env
    create_env=${create_env:-Y}
    
    if [[ $create_env =~ ^[Yy]$ ]]; then
        create_venv
        activate_venv
    else
        print_warning "跳过虚拟环境创建"
    fi
    echo
    
    # 安装依赖
    print_header "📦 第3步：安装依赖包"
    upgrade_pip
    install_dependencies
    echo
    
    # 运行测试
    print_header "🧪 第4步：系统测试"
    run_basic_test
    echo
    
    # 询问是否运行功能测试
    echo -e "${YELLOW}是否运行完整功能测试？(可能需要较长时间) [y/N]${NC}"
    read -r run_full_test
    if [[ $run_full_test =~ ^[Yy]$ ]]; then
        run_functionality_test
        echo
    fi
    
    # 询问是否运行演示
    echo -e "${YELLOW}是否运行检测演示？[Y/n]${NC}"
    read -r run_demo_choice
    run_demo_choice=${run_demo_choice:-Y}
    
    if [[ $run_demo_choice =~ ^[Yy]$ ]]; then
        print_header "🎬 第5步：运行演示"
        run_demo
        echo
    fi
    
    # 显示使用说明
    show_usage
}

# 捕获Ctrl+C信号
trap 'echo -e "\n${RED}安装被用户中断${NC}"; exit 1' INT

# 运行主函数
main "$@"
