#!/bin/bash

# Life Log 测试套件

echo "=========================================="
echo "Life Log - 功能测试套件"
echo "=========================================="
echo

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

passed=0
failed=0

# 测试函数
test_case() {
    local name="$1"
    local command="$2"
    
    echo -n "测试: $name ... "
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ 通过${NC}"
        ((passed++))
        return 0
    else
        echo -e "${RED}✗ 失败${NC}"
        ((failed++))
        return 1
    fi
}

# 1. 基础测试
echo "1. 基础功能测试"
echo "-------------------"
test_case "Python 导入测试" "python -c 'from mobile_collector import Config'"
test_case "CLI 帮助信息" "python cli.py --help"
test_case "配置初始化" "python cli.py config init && rm -f config.json"
test_case "验证脚本" "python verify_installation.py"
echo

# 2. 模块测试
echo "2. 模块导入测试"
echo "-------------------"
test_case "Config 模块" "python -c 'from mobile_collector.config import Config; c=Config()'"
test_case "Auth 模块" "python -c 'from mobile_collector.auth import MicrosoftAuthenticator'"
test_case "OneNote 模块" "python -c 'from mobile_collector.onenote_service import OneNoteService'"
test_case "OneDrive 模块" "python -c 'from mobile_collector.onedrive_service import OneDriveService'"
echo

# 3. CLI 命令测试
echo "3. CLI 命令测试"
echo "-------------------"
test_case "note 帮助" "python cli.py note --help"
test_case "upload 帮助" "python cli.py upload --help"
test_case "drive 帮助" "python cli.py drive --help"
test_case "config 显示" "python cli.py config show"
echo

# 4. 文件结构测试
echo "4. 文件结构测试"
echo "-------------------"
test_case "README 存在" "test -f README.md"
test_case "CLI 存在" "test -f cli.py"
test_case "示例脚本存在" "test -f examples.py"
test_case "需求文档存在" "test -f docs/v1.0/REQUIREMENTS.md"
test_case "设计文档存在" "test -f docs/v1.0/DESIGN.md"
echo

# 5. 配置测试
echo "5. 配置系统测试"
echo "-------------------"
test_case "配置模板存在" "test -f config.example.json"
test_case "配置读取" "python -c 'from mobile_collector import Config; c=Config(); c.get(\"microsoft.redirect_uri\")'"
test_case "配置设置" "python -c 'from mobile_collector import Config; c=Config(); c.set(\"test.key\", \"value\")'"
echo

# 6. 依赖测试
echo "6. 依赖检查"
echo "-------------------"
test_case "msal 已安装" "python -c 'import msal'"
test_case "requests 已安装" "python -c 'import requests'"
echo

# 总结
echo "=========================================="
echo "测试总结"
echo "=========================================="
echo -e "通过: ${GREEN}$passed${NC}"
echo -e "失败: ${RED}$failed${NC}"
echo -e "总计: $((passed + failed))"
echo

if [ $failed -eq 0 ]; then
    echo -e "${GREEN}✓ 所有测试通过！${NC}"
    exit 0
else
    echo -e "${RED}✗ 有 $failed 个测试失败${NC}"
    exit 1
fi
