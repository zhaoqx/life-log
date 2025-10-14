#!/usr/bin/env python3
"""
命令行接口

提供命令行操作接口，用于认证、创建笔记和上传文件。
"""

import argparse
import sys
import os

from mobile_collector.config import Config
from mobile_collector.auth import MicrosoftAuthenticator
from mobile_collector.onenote_service import OneNoteService
from mobile_collector.onedrive_service import OneDriveService


def cmd_auth(args, config):
    """执行认证命令"""
    print("=== Microsoft账户认证 ===\n")
    
    # 验证配置
    if not config.validate():
        print("\n错误: 配置不完整，请先配置Microsoft应用程序凭据")
        print("可以编辑 config.json 文件或设置环境变量：")
        print("  - MS_CLIENT_ID")
        print("  - MS_CLIENT_SECRET")
        return 1
    
    # 创建认证器
    authenticator = MicrosoftAuthenticator(
        client_id=config.get('microsoft.client_id'),
        client_secret=config.get('microsoft.client_secret'),
        redirect_uri=config.get('microsoft.redirect_uri'),
        scopes=config.get('microsoft.scopes')
    )
    
    # 执行认证
    if authenticator.authenticate():
        print("\n认证成功！您现在可以使用OneNote和OneDrive功能了。")
        return 0
    else:
        print("\n认证失败！")
        return 1


def cmd_note_create(args, config):
    """创建OneNote笔记"""
    print("=== 创建OneNote笔记 ===\n")
    
    # 创建认证器和服务
    authenticator = MicrosoftAuthenticator(
        client_id=config.get('microsoft.client_id'),
        client_secret=config.get('microsoft.client_secret'),
        redirect_uri=config.get('microsoft.redirect_uri'),
        scopes=config.get('microsoft.scopes')
    )
    
    # 检查认证状态
    if not authenticator.is_authenticated():
        print("错误: 未认证，请先执行 'python cli.py auth' 进行认证")
        return 1
    
    service = OneNoteService(authenticator)
    
    # 读取内容
    if args.file:
        if not os.path.exists(args.file):
            print(f"错误: 文件不存在: {args.file}")
            return 1
        with open(args.file, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = args.content
    
    try:
        # 创建页面
        result = service.create_page(
            title=args.title,
            content=content,
            notebook_id=args.notebook_id,
            section_id=args.section_id
        )
        
        print(f"笔记创建成功！")
        print(f"页面ID: {result['id']}")
        print(f"页面URL: {result['links']['oneNoteWebUrl']['href']}")
        return 0
        
    except Exception as e:
        print(f"创建笔记失败: {e}")
        return 1


def cmd_note_list(args, config):
    """列出笔记本"""
    print("=== OneNote笔记本列表 ===\n")
    
    authenticator = MicrosoftAuthenticator(
        client_id=config.get('microsoft.client_id'),
        client_secret=config.get('microsoft.client_secret'),
        redirect_uri=config.get('microsoft.redirect_uri'),
        scopes=config.get('microsoft.scopes')
    )
    
    if not authenticator.is_authenticated():
        print("错误: 未认证，请先执行 'python cli.py auth' 进行认证")
        return 1
    
    service = OneNoteService(authenticator)
    
    try:
        notebooks = service.list_notebooks()
        
        if not notebooks:
            print("没有找到笔记本")
            return 0
        
        for nb in notebooks:
            print(f"\n笔记本: {nb['displayName']}")
            print(f"  ID: {nb['id']}")
            
            if args.sections:
                sections = service.list_sections(nb['id'])
                for section in sections:
                    print(f"    分区: {section['displayName']} (ID: {section['id']})")
        
        return 0
        
    except Exception as e:
        print(f"获取笔记本列表失败: {e}")
        return 1


def cmd_upload(args, config):
    """上传文件到OneDrive"""
    print("=== 上传文件到OneDrive ===\n")
    
    authenticator = MicrosoftAuthenticator(
        client_id=config.get('microsoft.client_id'),
        client_secret=config.get('microsoft.client_secret'),
        redirect_uri=config.get('microsoft.redirect_uri'),
        scopes=config.get('microsoft.scopes')
    )
    
    if not authenticator.is_authenticated():
        print("错误: 未认证，请先执行 'python cli.py auth' 进行认证")
        return 1
    
    service = OneDriveService(authenticator)
    
    # 获取目标文件夹
    target_folder = args.folder or config.get('onedrive.default_folder')
    
    try:
        # 上传文件
        if len(args.files) == 1:
            result = service.upload_file(args.files[0], target_folder)
            print(f"\n文件信息:")
            print(f"  名称: {result['name']}")
            print(f"  大小: {result['size']} 字节")
            print(f"  URL: {result['webUrl']}")
        else:
            results = service.upload_files(args.files, target_folder)
            print(f"\n上传完成，成功: {sum(1 for r in results if 'id' in r)}/{len(results)}")
        
        return 0
        
    except Exception as e:
        print(f"上传文件失败: {e}")
        return 1


def cmd_drive_list(args, config):
    """列出OneDrive文件"""
    print("=== OneDrive文件列表 ===\n")
    
    authenticator = MicrosoftAuthenticator(
        client_id=config.get('microsoft.client_id'),
        client_secret=config.get('microsoft.client_secret'),
        redirect_uri=config.get('microsoft.redirect_uri'),
        scopes=config.get('microsoft.scopes')
    )
    
    if not authenticator.is_authenticated():
        print("错误: 未认证，请先执行 'python cli.py auth' 进行认证")
        return 1
    
    service = OneDriveService(authenticator)
    
    try:
        files = service.list_files(args.folder)
        
        if not files:
            print("文件夹为空")
            return 0
        
        print(f"文件夹: {args.folder or '根目录'}\n")
        
        for item in files:
            item_type = "📁" if 'folder' in item else "📄"
            size = f"{item['size']} 字节" if 'size' in item else ""
            print(f"{item_type} {item['name']} {size}")
        
        return 0
        
    except Exception as e:
        print(f"列出文件失败: {e}")
        return 1


def cmd_config(args, config):
    """配置管理"""
    if args.action == 'show':
        print("=== 当前配置 ===\n")
        print(f"Client ID: {config.get('microsoft.client_id') or '(未设置)'}")
        print(f"Client Secret: {'***' if config.get('microsoft.client_secret') else '(未设置)'}")
        print(f"Redirect URI: {config.get('microsoft.redirect_uri')}")
        print(f"OneNote默认笔记本: {config.get('onenote.default_notebook_id') or '(自动)'}")
        print(f"OneDrive默认文件夹: {config.get('onedrive.default_folder')}")
    
    elif args.action == 'init':
        print("=== 初始化配置文件 ===\n")
        config.save()
        print(f"配置文件已创建: {config.config_file}")
        print("\n请编辑配置文件，填入您的Microsoft应用程序凭据：")
        print(f"  - microsoft.client_id")
        print(f"  - microsoft.client_secret")
    
    return 0


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Life Log - 手机信息采集到OneNote和OneDrive',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--config',
        help='配置文件路径',
        default=None
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # auth命令
    parser_auth = subparsers.add_parser('auth', help='执行Microsoft账户认证')
    parser_auth.set_defaults(func=cmd_auth)
    
    # note命令组
    parser_note = subparsers.add_parser('note', help='OneNote操作')
    note_subparsers = parser_note.add_subparsers(dest='note_command')
    
    # note create
    parser_note_create = note_subparsers.add_parser('create', help='创建笔记')
    parser_note_create.add_argument('title', help='笔记标题')
    parser_note_create.add_argument(
        '--content', '-c',
        help='笔记内容',
        default=''
    )
    parser_note_create.add_argument(
        '--file', '-f',
        help='从文件读取内容'
    )
    parser_note_create.add_argument(
        '--notebook-id',
        help='笔记本ID'
    )
    parser_note_create.add_argument(
        '--section-id',
        help='分区ID'
    )
    parser_note_create.set_defaults(func=cmd_note_create)
    
    # note list
    parser_note_list = note_subparsers.add_parser('list', help='列出笔记本')
    parser_note_list.add_argument(
        '--sections', '-s',
        action='store_true',
        help='同时显示分区'
    )
    parser_note_list.set_defaults(func=cmd_note_list)
    
    # upload命令
    parser_upload = subparsers.add_parser('upload', help='上传文件到OneDrive')
    parser_upload.add_argument('files', nargs='+', help='要上传的文件路径')
    parser_upload.add_argument(
        '--folder', '-d',
        help='目标文件夹路径'
    )
    parser_upload.set_defaults(func=cmd_upload)
    
    # drive命令组
    parser_drive = subparsers.add_parser('drive', help='OneDrive操作')
    drive_subparsers = parser_drive.add_subparsers(dest='drive_command')
    
    # drive list
    parser_drive_list = drive_subparsers.add_parser('list', help='列出文件')
    parser_drive_list.add_argument(
        '--folder', '-d',
        help='文件夹路径'
    )
    parser_drive_list.set_defaults(func=cmd_drive_list)
    
    # config命令
    parser_config = subparsers.add_parser('config', help='配置管理')
    parser_config.add_argument(
        'action',
        choices=['show', 'init'],
        help='配置操作'
    )
    parser_config.set_defaults(func=cmd_config)
    
    # 解析参数
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # 加载配置
    config = Config(args.config)
    
    # 执行命令
    if hasattr(args, 'func'):
        return args.func(args, config)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
