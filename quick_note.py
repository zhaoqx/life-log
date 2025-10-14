#!/usr/bin/env python3
"""
Pythonista 快速笔记脚本

这个脚本专为 iOS Pythonista 应用设计，用于快速创建 OneNote 笔记。

使用方法:
1. 在 Pythonista 中创建此脚本
2. 配置好 config.json 文件
3. 运行脚本: python quick_note.py "标题" "内容"

或者在 Pythonista 中导入使用:
    from quick_note import quick_note
    quick_note("我的标题", "我的内容")
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mobile_collector import Config, MicrosoftAuthenticator, OneNoteService

def quick_note(title, content=None, content_file=None):
    """
    创建快速笔记到 OneNote
    
    参数:
        title: 笔记标题
        content: 笔记内容（如果提供）
        content_file: 内容文件路径（如果 content 为空）
    
    返回:
        创建的笔记信息字典
    """
    # 读取文件内容（如果指定）
    if content is None and content_file:
        try:
            with open(content_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"✗ 读取文件失败: {e}")
            sys.exit(1)
    
    # 验证内容
    if not content:
        print("✗ 错误: 必须提供笔记内容")
        sys.exit(1)
    
    try:
        # 初始化配置
        print("初始化配置...")
        config = Config()
        
        # 创建认证器
        print("准备认证...")
        auth = MicrosoftAuthenticator(
            client_id=config.get('microsoft.client_id'),
            client_secret=config.get('microsoft.client_secret'),
            redirect_uri=config.get('microsoft.redirect_uri'),
            scopes=config.get('microsoft.scopes')
        )
        
        # 检查认证状态
        if not auth.is_authenticated():
            print("需要认证。请先运行: python cli.py auth")
            sys.exit(1)
        
        # 创建 OneNote 服务
        print("创建笔记...")
        service = OneNoteService(auth)
        
        # 创建页面
        result = service.create_page(title, content)
        
        # 输出成功信息
        url = result['links']['oneNoteWebUrl']['href']
        print()
        print("=" * 50)
        print("✓ 笔记创建成功！")
        print("=" * 50)
        print(f"标题: {title}")
        print(f"链接: {url}")
        print(f"ID: {result['id']}")
        print("=" * 50)
        
        return result
        
    except Exception as e:
        print()
        print("=" * 50)
        print("✗ 创建笔记失败")
        print("=" * 50)
        print(f"错误: {str(e)}")
        print()
        print("故障排除:")
        print("1. 检查网络连接")
        print("2. 验证配置文件 config.json")
        print("3. 确认已完成认证: python cli.py auth")
        print("=" * 50)
        sys.exit(1)

def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("=" * 50)
        print("Pythonista 快速笔记工具")
        print("=" * 50)
        print()
        print("用法:")
        print("  python quick_note.py '标题' '内容'")
        print("  python quick_note.py '标题' --file 文件路径")
        print()
        print("示例:")
        print("  python quick_note.py '今日想法' '这是一个好主意'")
        print("  python quick_note.py '会议记录' --file notes.txt")
        print()
        print("=" * 50)
        sys.exit(1)
    
    title = sys.argv[1]
    content = None
    content_file = None
    
    # 解析参数
    if len(sys.argv) >= 3:
        if sys.argv[2] == '--file' and len(sys.argv) >= 4:
            content_file = sys.argv[3]
        else:
            content = sys.argv[2]
    
    # 创建笔记
    quick_note(title, content, content_file)

if __name__ == '__main__':
    main()
