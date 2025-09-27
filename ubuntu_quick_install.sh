#!/bin/bash

# FlyAI Agent in Action - Ubuntu 22.04 一键安装脚本
# 完全自动化安装所有依赖和环境

set -e  # 遇到错误立即退出

echo "🚀 FlyAI Agent in Action - Ubuntu 22.04 一键安装"
echo "=================================================="
echo "目标环境: Ubuntu 22.04 LTS"
echo "Python版本: 3.12.11"
echo "Conda环境: flyai_agent_in_action"
echo "=================================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否为root用户
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "请不要使用root用户运行此脚本"
        exit 1
    fi
}

# 检查Ubuntu版本
check_ubuntu_version() {
    log_info "检查Ubuntu版本..."
    
    if [[ -f /etc/os-release ]]; then
        source /etc/os-release
        if [[ "$ID" == "ubuntu" ]]; then
            log_success "检测到Ubuntu系统: $PRETTY_NAME"
            if [[ "$VERSION_ID" == "22.04" ]]; then
                log_success "Ubuntu版本验证通过: 22.04 LTS"
            else
                log_warning "检测到Ubuntu版本: $VERSION_ID (推荐22.04)"
            fi
        else
            log_warning "未检测到Ubuntu系统，继续安装..."
        fi
    fi
}

# 更新系统包
update_system() {
    log_info "更新系统包..."
    sudo apt update && sudo apt upgrade -y
    log_success "系统包更新完成"
}

# 安装系统依赖
install_system_deps() {
    log_info "安装系统依赖..."
    
    PACKAGES=(
        "wget"
        "curl" 
        "git"
        "build-essential"
        "python3-dev"
        "python3-pip"
        "libssl-dev"
        "libffi-dev"
        "libgl1-mesa-glx"
        "libglib2.0-0"
    )
    
    sudo apt install -y "${PACKAGES[@]}"
    log_success "系统依赖安装完成"
}

# 安装Miniconda
install_miniconda() {
    log_info "检查Miniconda安装状态..."
    
    if command -v conda &> /dev/null; then
        log_success "检测到Conda已安装: $(conda --version)"
        return 0
    fi
    
    log_info "Miniconda未安装，开始安装..."
    
    MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
    INSTALLER="/tmp/miniconda_installer.sh"
    
    # 下载安装包
    log_info "下载Miniconda安装包..."
    wget -q --show-progress "$MINICONDA_URL" -O "$INSTALLER"
    
    # 安装Miniconda
    log_info "安装Miniconda到 $HOME/miniconda3..."
    bash "$INSTALLER" -b -p "$HOME/miniconda3"
    
    # 初始化conda
    log_info "初始化Conda..."
    "$HOME/miniconda3/bin/conda" init bash
    
    # 清理安装包
    rm -f "$INSTALLER"
    
    # 重新加载shell配置
    source ~/.bashrc || true
    
    # 添加conda到PATH
    export PATH="$HOME/miniconda3/bin:$PATH"
    
    log_success "Miniconda安装完成"
}

# 创建conda环境
create_conda_env() {
    log_info "创建Conda环境 flyai_agent_in_action..."
    
    # 确保conda在PATH中
    export PATH="$HOME/miniconda3/bin:$PATH"
    
    # 删除已存在的环境（如果有）
    if conda env list | grep -q "flyai_agent_in_action"; then
        log_warning "环境已存在，正在删除旧环境..."
        conda env remove -n flyai_agent_in_action -y
    fi
    
    # 创建新环境
    conda create -n flyai_agent_in_action python=3.12.11 -y
    log_success "Conda环境创建完成"
}

# 安装Python依赖
install_python_deps() {
    log_info "安装Python依赖包..."
    
    # 激活环境
    source "$HOME/miniconda3/etc/profile.d/conda.sh"
    conda activate flyai_agent_in_action
    
    # 更新pip
    pip install --upgrade pip
    
    # 检查requirements.txt文件是否存在
    if [[ -f "requirements.txt" ]]; then
        log_info "使用requirements.txt安装所有依赖..."
        pip install -r requirements.txt
    else
        log_warning "未找到requirements.txt文件"
    
    fi
    
    log_success "Python依赖安装完成"
}

# 安装可选依赖
install_optional_deps() {
    read -p "是否安装可选依赖（安全监控和数据处理扩展）？[y/N]: " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "安装可选依赖..."
        
        # 激活环境
        source "$HOME/miniconda3/etc/profile.d/conda.sh"
        conda activate flyai_agent_in_action
        
        pip install llm-guard==0.3.16 unstructured==0.18.13 selenium==4.35.0 langchain-chroma==0.2.5
        
        log_success "可选依赖安装完成"
    else
        log_info "跳过可选依赖安装"
    fi
}

# 配置环境变量
setup_env_vars() {
    log_info "配置环境变量..."
    
    ENV_FILE="$HOME/.bashrc"
    
    # 备份原文件
    cp "$ENV_FILE" "$ENV_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    
    # 添加conda初始化（如果不存在）
    if ! grep -q "conda initialize" "$ENV_FILE"; then
        echo "" >> "$ENV_FILE"
        echo "# >>> conda initialize >>>" >> "$ENV_FILE"
        echo "# !! Contents within this block are managed by 'conda init' !!" >> "$ENV_FILE"
        echo 'eval "$($HOME/miniconda3/bin/conda shell.bash hook)"' >> "$ENV_FILE"
        echo "# <<< conda initialize <<<" >> "$ENV_FILE"
    fi
    
    # 添加环境变量占位符
    if ! grep -q "FlyAI Agent API Keys" "$ENV_FILE"; then
        cat >> "$ENV_FILE" << 'EOF'

        # FlyAI Agent API Keys
        # 请替换为您的实际API密钥
        # export OPENAI_API_KEY="your_openai_api_key_here"
        # export LANGFUSE_SECRET_KEY="your_langfuse_secret_key"
        # export LANGFUSE_PUBLIC_KEY="your_langfuse_public_key"
        # export TAVILY_API_KEY="your_tavily_api_key"
        EOF
    fi
    
    log_success "环境变量配置完成"
}

# 验证安装
verify_installation() {
    log_info "验证安装..."
    
    # 激活环境
    source "$HOME/miniconda3/etc/profile.d/conda.sh"
    conda activate flyai_agent_in_action
    
    # 运行验证脚本
    if [[ -f "verify_environment.py" ]]; then
        python verify_environment.py
    else
        # 简单验证
        python -c "
import langchain, langgraph, langfuse, trustcall
print('✅ 核心依赖验证成功!')
print(f'LangChain: {langchain.__version__}')
print(f'LangGraph: {langgraph.__version__}')
print(f'Langfuse: {langfuse.__version__}')
print(f'Trustcall: {trustcall.__version__}')
"
    fi
    
    log_success "安装验证完成"
}

# 显示完成信息
show_completion_info() {
    echo ""
    echo "=================================================="
    log_success "🎉 FlyAI Agent in Action 安装完成！"
    echo "=================================================="
    echo ""
    echo "📝 接下来的步骤:"
    echo "1. 重新加载shell配置: source ~/.bashrc"
    echo "2. 激活环境: conda activate flyai_agent_in_action"
    echo "3. 配置API密钥:"
    echo "   编辑 ~/.bashrc 文件，取消注释并填入您的API密钥"
    echo "4. 启动Jupyter: jupyter notebook"
    echo ""
    echo "🔍 验证安装: python verify_environment.py"
    echo "📚 查看文档: cat README.md"
    echo ""
    echo "=================================================="
}

# 主函数
main() {
    echo "开始安装..."
    
    check_root
    check_ubuntu_version
    update_system
    install_system_deps
    install_miniconda
    create_conda_env
    install_python_deps
    install_optional_deps
    setup_env_vars
    verify_installation
    show_completion_info
    
    log_success "安装流程全部完成！"
}

# 运行主函数
main "$@"
