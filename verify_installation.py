#!/usr/bin/env python3
"""
安装验证脚本

检查 Life Log 是否正确安装和配置。
"""

import sys
import os

def check_python_version():
    """检查 Python 版本"""
    print("检查 Python 版本...", end=" ")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} (需要 3.7+)")
        return False

def check_dependencies():
    """检查依赖包"""
    print("检查依赖包...")
    
    required = {
        'msal': 'MSAL (Microsoft Authentication Library)',
        'requests': 'Requests HTTP 库'
    }
    
    all_ok = True
    for module, name in required.items():
        try:
            __import__(module)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✗ {name} - 未安装")
            all_ok = False
    
    return all_ok

def check_project_structure():
    """检查项目结构"""
    print("检查项目结构...")
    
    required_files = [
        'README.md',
        'cli.py',
        'requirements.txt',
        'config.example.json',
        'mobile_collector/__init__.py',
        'mobile_collector/auth.py',
        'mobile_collector/config.py',
        'mobile_collector/onenote_service.py',
        'mobile_collector/onedrive_service.py',
        'docs/v1.0/CHANGELOG.md',
        'docs/QUICKSTART.md',
    ]
    
    all_ok = True
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} - 缺失")
            all_ok = False
    
    return all_ok

def check_modules():
    """检查模块导入"""
    print("检查模块导入...", end=" ")
    
    try:
        from mobile_collector import Config, MicrosoftAuthenticator
        from mobile_collector import OneNoteService, OneDriveService
        print("✓ 所有模块可正常导入")
        return True
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        return False

def check_config():
    """检查配置"""
    print("检查配置...")
    
    from mobile_collector import Config
    
    config = Config()
    
    # 检查配置文件
    if os.path.exists('config.json'):
        print("  ✓ 配置文件存在 (config.json)")
        
        # 检查必需配置
        if config.get('microsoft.client_id'):
            print("    ✓ Client ID 已配置")
        else:
            print("    ⚠ Client ID 未配置")
        
        if config.get('microsoft.client_secret'):
            print("    ✓ Client Secret 已配置")
        else:
            print("    ⚠ Client Secret 未配置")
    else:
        print("  ⚠ 配置文件不存在 - 运行 'python cli.py config init'")
    
    # 检查令牌缓存
    if os.path.exists('.token_cache.json'):
        print("  ✓ 认证令牌已缓存")
    else:
        print("  ⚠ 未找到认证令牌 - 运行 'python cli.py auth'")
    
    return True

def check_cli():
    """检查 CLI"""
    print("检查命令行接口...", end=" ")
    
    if os.path.exists('cli.py') and os.access('cli.py', os.X_OK):
        print("✓ CLI 可执行")
        return True
    elif os.path.exists('cli.py'):
        print("✓ CLI 存在")
        return True
    else:
        print("✗ CLI 不存在")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("Life Log - 安装验证")
    print("=" * 60)
    print()
    
    results = []
    
    results.append(("Python 版本", check_python_version()))
    results.append(("依赖包", check_dependencies()))
    results.append(("项目结构", check_project_structure()))
    results.append(("模块导入", check_modules()))
    results.append(("配置", check_config()))
    results.append(("CLI", check_cli()))
    
    print()
    print("=" * 60)
    print("验证结果")
    print("=" * 60)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name:20} {status}")
    
    all_passed = all(r for _, r in results)
    
    print()
    if all_passed:
        print("✓ 所有检查通过！Life Log 已正确安装。")
        print()
        print("下一步：")
        if not os.path.exists('config.json'):
            print("  1. 运行 'python cli.py config init' 创建配置文件")
            print("  2. 编辑 config.json，填入您的 Microsoft 凭据")
            print("  3. 运行 'python cli.py auth' 进行认证")
        elif not os.path.exists('.token_cache.json'):
            print("  1. 运行 'python cli.py auth' 进行认证")
        else:
            print("  - 运行 'python cli.py note list' 查看笔记本")
            print("  - 运行 'python cli.py note create \"标题\" --content \"内容\"'")
            print("  - 查看 docs/QUICKSTART.md 了解更多")
        
        return 0
    else:
        print("✗ 部分检查未通过，请查看上述错误。")
        print()
        print("常见解决方案：")
        print("  - 安装依赖：pip install -r requirements.txt")
        print("  - 检查 Python 版本：python --version")
        print("  - 查看文档：docs/QUICKSTART.md")
        
        return 1

if __name__ == '__main__':
    sys.exit(main())
