#!/usr/bin/env python3
"""
示例脚本 - 演示如何使用 Mobile Collector

本脚本展示了如何在代码中使用 mobile_collector 包的各个模块。
"""

import os
from mobile_collector import Config, MicrosoftAuthenticator, OneNoteService, OneDriveService


def example_basic_usage():
    """基础使用示例"""
    print("=== 基础使用示例 ===\n")
    
    # 1. 加载配置
    config = Config()
    
    # 2. 创建认证器
    authenticator = MicrosoftAuthenticator(
        client_id=config.get('microsoft.client_id'),
        client_secret=config.get('microsoft.client_secret'),
        redirect_uri=config.get('microsoft.redirect_uri'),
        scopes=config.get('microsoft.scopes')
    )
    
    # 3. 检查认证状态
    if not authenticator.is_authenticated():
        print("未认证，请先运行: python cli.py auth")
        return
    
    # 4. 使用 OneNote 服务
    onenote = OneNoteService(authenticator)
    
    # 列出笔记本
    print("您的笔记本：")
    notebooks = onenote.list_notebooks()
    for nb in notebooks[:3]:  # 只显示前3个
        print(f"  - {nb['displayName']} (ID: {nb['id']})")
    
    # 5. 使用 OneDrive 服务
    onedrive = OneDriveService(authenticator)
    
    # 列出文件
    print("\nOneDrive 根目录文件：")
    files = onedrive.list_files()
    for item in files[:5]:  # 只显示前5个
        print(f"  - {item['name']}")


def example_create_note():
    """创建笔记示例"""
    print("\n=== 创建笔记示例 ===\n")
    
    config = Config()
    authenticator = MicrosoftAuthenticator(
        client_id=config.get('microsoft.client_id'),
        client_secret=config.get('microsoft.client_secret'),
        redirect_uri=config.get('microsoft.redirect_uri'),
        scopes=config.get('microsoft.scopes')
    )
    
    if not authenticator.is_authenticated():
        print("未认证，请先运行: python cli.py auth")
        return
    
    onenote = OneNoteService(authenticator)
    
    # 创建示例笔记
    title = "Life Log 测试笔记"
    content = """这是一个测试笔记。

功能特性：
1. 支持多行文本
2. 支持特殊字符：<>&"
3. 自动转换为 HTML 格式

创建时间：自动记录
"""
    
    try:
        result = onenote.create_page(title, content)
        print(f"✓ 笔记创建成功！")
        print(f"  标题: {title}")
        print(f"  页面ID: {result['id']}")
        print(f"  链接: {result['links']['oneNoteWebUrl']['href']}")
    except Exception as e:
        print(f"✗ 创建失败: {e}")


def example_upload_file():
    """上传文件示例"""
    print("\n=== 上传文件示例 ===\n")
    
    config = Config()
    authenticator = MicrosoftAuthenticator(
        client_id=config.get('microsoft.client_id'),
        client_secret=config.get('microsoft.client_secret'),
        redirect_uri=config.get('microsoft.redirect_uri'),
        scopes=config.get('microsoft.scopes')
    )
    
    if not authenticator.is_authenticated():
        print("未认证，请先运行: python cli.py auth")
        return
    
    onedrive = OneDriveService(authenticator)
    
    # 创建测试文件
    test_file = "/tmp/lifelog_test.txt"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("这是一个测试文件\n")
        f.write("由 Life Log 系统创建\n")
        f.write(f"文件大小：{os.path.getsize(test_file)} 字节\n")
    
    try:
        result = onedrive.upload_file(
            test_file, 
            target_folder=config.get('onedrive.default_folder')
        )
        print(f"✓ 文件上传成功！")
        print(f"  名称: {result['name']}")
        print(f"  大小: {result['size']} 字节")
        print(f"  链接: {result['webUrl']}")
    except Exception as e:
        print(f"✗ 上传失败: {e}")
    finally:
        # 清理测试文件
        if os.path.exists(test_file):
            os.remove(test_file)


def example_batch_operations():
    """批量操作示例"""
    print("\n=== 批量操作示例 ===\n")
    
    config = Config()
    authenticator = MicrosoftAuthenticator(
        client_id=config.get('microsoft.client_id'),
        client_secret=config.get('microsoft.client_secret'),
        redirect_uri=config.get('microsoft.redirect_uri'),
        scopes=config.get('microsoft.scopes')
    )
    
    if not authenticator.is_authenticated():
        print("未认证，请先运行: python cli.py auth")
        return
    
    onedrive = OneDriveService(authenticator)
    
    # 创建多个测试文件
    test_files = []
    for i in range(3):
        test_file = f"/tmp/lifelog_test_{i}.txt"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(f"测试文件 #{i}\n")
        test_files.append(test_file)
    
    try:
        results = onedrive.upload_files(
            test_files,
            target_folder=config.get('onedrive.default_folder')
        )
        
        success_count = sum(1 for r in results if 'id' in r)
        print(f"✓ 批量上传完成: {success_count}/{len(test_files)} 成功")
        
        for i, result in enumerate(results):
            if 'id' in result:
                print(f"  [{i+1}] ✓ {result['name']}")
            else:
                print(f"  [{i+1}] ✗ {result.get('file', '未知')}")
    
    except Exception as e:
        print(f"✗ 批量上传失败: {e}")
    
    finally:
        # 清理测试文件
        for test_file in test_files:
            if os.path.exists(test_file):
                os.remove(test_file)


def main():
    """主函数"""
    print("Life Log - Mobile Collector 示例脚本\n")
    print("=" * 60)
    
    # 检查配置
    config = Config()
    if not config.get('microsoft.client_id'):
        print("\n⚠️  警告: 未找到配置文件或配置不完整")
        print("请先运行: python cli.py config init")
        print("然后编辑 config.json 文件，填入您的凭据\n")
        return
    
    print("\n请选择要运行的示例：")
    print("1. 基础使用（查看笔记本和文件）")
    print("2. 创建笔记")
    print("3. 上传文件")
    print("4. 批量上传文件")
    print("0. 全部运行")
    
    choice = input("\n请输入选项 (0-4): ").strip()
    
    if choice == '1':
        example_basic_usage()
    elif choice == '2':
        example_create_note()
    elif choice == '3':
        example_upload_file()
    elif choice == '4':
        example_batch_operations()
    elif choice == '0':
        example_basic_usage()
        example_create_note()
        example_upload_file()
        example_batch_operations()
    else:
        print("无效的选项")


if __name__ == '__main__':
    main()
