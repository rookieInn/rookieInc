#!/bin/bash
# 微信公众号菜单系统启动脚本

echo "======================================"
echo "   微信公众号菜单管理系统启动脚本"
echo "======================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查Python环境
echo -e "\n${YELLOW}检查Python环境...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到Python3，请先安装Python3${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python3已安装${NC}"

# 检查配置文件
echo -e "\n${YELLOW}检查配置文件...${NC}"
if [ ! -f "wechat_official_account_config.ini" ]; then
    echo -e "${RED}错误: 配置文件不存在${NC}"
    echo -e "${YELLOW}正在创建默认配置文件...${NC}"
    python3 wechat_official_menu.py --create-config
    echo -e "${YELLOW}请编辑 wechat_official_account_config.ini 文件，填入您的公众号信息${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 配置文件已存在${NC}"

# 检查依赖
echo -e "\n${YELLOW}检查依赖包...${NC}"
python3 -c "import flask, requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}正在安装依赖包...${NC}"
    pip3 install flask requests -i https://pypi.tuna.tsinghua.edu.cn/simple
fi
echo -e "${GREEN}✓ 依赖包已安装${NC}"

# 创建媒体目录
echo -e "\n${YELLOW}创建媒体目录...${NC}"
mkdir -p media/images media/videos media/audios
echo -e "${GREEN}✓ 媒体目录已创建${NC}"

# 显示菜单
echo -e "\n======================================"
echo -e "请选择操作："
echo -e "1. 创建/更新菜单"
echo -e "2. 启动消息响应服务器"
echo -e "3. 查询当前菜单"
echo -e "4. 删除菜单"
echo -e "5. 运行完整示例"
echo -e "6. 退出"
echo -e "======================================"

read -p "请输入选项 (1-6): " choice

case $choice in
    1)
        echo -e "\n${GREEN}创建/更新菜单...${NC}"
        python3 wechat_official_menu.py
        ;;
    2)
        echo -e "\n${GREEN}启动消息响应服务器...${NC}"
        python3 wechat_official_server.py
        ;;
    3)
        echo -e "\n${GREEN}查询当前菜单...${NC}"
        python3 -c "from wechat_official_menu import WeChatOfficialMenuManager; import json; m = WeChatOfficialMenuManager(); menu = m.get_menu(); print(json.dumps(menu, ensure_ascii=False, indent=2) if menu else '当前没有菜单')"
        ;;
    4)
        echo -e "\n${YELLOW}确认删除菜单? (y/n): ${NC}"
        read confirm
        if [ "$confirm" = "y" ]; then
            echo -e "${GREEN}删除菜单...${NC}"
            python3 -c "from wechat_official_menu import WeChatOfficialMenuManager; m = WeChatOfficialMenuManager(); print('菜单已删除' if m.delete_menu() else '删除失败')"
        else
            echo -e "${YELLOW}已取消删除${NC}"
        fi
        ;;
    5)
        echo -e "\n${GREEN}运行完整示例...${NC}"
        python3 wechat_official_example.py
        ;;
    6)
        echo -e "\n${GREEN}退出${NC}"
        exit 0
        ;;
    *)
        echo -e "\n${RED}无效的选项${NC}"
        exit 1
        ;;
esac

echo -e "\n${GREEN}======================================"
echo -e "操作完成！"
echo -e "======================================${NC}"
