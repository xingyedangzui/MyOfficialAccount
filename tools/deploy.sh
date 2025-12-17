#!/bin/bash

# WeChat Official Account Service 部署脚本
# 使用方法: bash deploy.sh

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置变量
SERVICE_NAME="wechat-service"
PROJECT_DIR=$(pwd)
SERVICE_FILE="${SERVICE_NAME}.service"
SYSTEMD_DIR="/etc/systemd/system"

echo -e "${GREEN}=== WeChat Official Account Service 部署脚本 ===${NC}"
echo "项目目录: $PROJECT_DIR"
echo "服务名称: $SERVICE_NAME"

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}错误: 请使用 sudo 运行此脚本${NC}"
    echo "使用方法: sudo bash deploy.sh"
    exit 1
fi

# 检查必要文件
if [ ! -f "script/main.py" ]; then
    echo -e "${RED}错误: 在script目录下未找到 main.py 文件${NC}"
    exit 1
fi

# 检查service文件（可能在当前目录或tools目录下）
if [ -f "$SERVICE_FILE" ]; then
    SERVICE_FILE_PATH="$SERVICE_FILE"
elif [ -f "configs/$SERVICE_FILE" ]; then
    SERVICE_FILE_PATH="configs/$SERVICE_FILE"
else
    echo -e "${RED}错误: 未找到 $SERVICE_FILE 文件${NC}"
    echo "请确保该文件存在于当前目录或tools目录下"
    exit 1
fi

echo -e "${YELLOW}1. 检查Python环境...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未安装 python3${NC}"
    exit 1
fi

# 安装Python依赖
echo -e "${YELLOW}2. 安装Python依赖...${NC}"
if [ -f "requirements.txt" ]; then
    echo -e "${YELLOW}从requirements.txt安装依赖...${NC}"
    pip3 install -r requirements.txt
elif [ -f "tools/requirements.txt" ]; then
    echo -e "${YELLOW}从tools/requirements.txt安装依赖...${NC}"
    pip3 install -r tools/requirements.txt
else
    echo -e "${YELLOW}未找到requirements.txt，安装基础依赖...${NC}"
    pip3 install web.py
fi

# 更新service文件中的路径
echo -e "${YELLOW}3. 更新服务配置...${NC}"
echo "使用service文件: $SERVICE_FILE_PATH"
# 获取Python3的完整路径
PYTHON3_PATH=$(which python3)
# 创建临时service文件并更新路径
cp "$SERVICE_FILE_PATH" "${SERVICE_FILE}.tmp"
sed -i "s|/MyOfficialAccount|$PROJECT_DIR|g" "${SERVICE_FILE}.tmp"
sed -i "s|/usr/bin/python3|$PYTHON3_PATH|g" "${SERVICE_FILE}.tmp"
sed -i "s|ExecStart=$PYTHON3_PATH main.py|ExecStart=$PYTHON3_PATH script/main.py|g" "${SERVICE_FILE}.tmp"

# 复制service文件到系统目录
echo -e "${YELLOW}4. 安装systemd服务...${NC}"
cp "${SERVICE_FILE}.tmp" "$SYSTEMD_DIR/$SERVICE_FILE"
chmod 644 "$SYSTEMD_DIR/$SERVICE_FILE"

# 清理临时文件
rm -f "${SERVICE_FILE}.tmp"

# 重新加载systemd配置
echo -e "${YELLOW}5. 重新加载systemd配置...${NC}"
systemctl daemon-reload

# 启用并启动服务
echo -e "${YELLOW}6. 启用并启动服务...${NC}"
systemctl enable "$SERVICE_NAME"
systemctl start "$SERVICE_NAME"

# 检查服务状态
sleep 2
if systemctl is-active --quiet "$SERVICE_NAME"; then
    echo -e "${GREEN}✅ 服务部署成功！${NC}"
    echo
    echo -e "${GREEN}常用命令:${NC}"
    echo "  查看状态:   sudo systemctl status $SERVICE_NAME"
    echo "  查看日志:   sudo journalctl -u $SERVICE_NAME -f"
    echo "  重启服务:   sudo systemctl restart $SERVICE_NAME"
    echo "  停止服务:   sudo systemctl stop $SERVICE_NAME"
    echo "  禁用服务:   sudo systemctl disable $SERVICE_NAME"
    echo
    echo -e "${GREEN}服务已在后台运行，端口: 80${NC}"
else
    echo -e "${RED}❌ 服务启动失败${NC}"
    echo "查看错误日志: sudo journalctl -u $SERVICE_NAME -n 20"
    exit 1
fi