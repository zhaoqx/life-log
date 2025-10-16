#!/usr/bin/env python3
"""
iOS 快捷指令 API 封装
这个脚本提供了一个简单的 Flask API，用于通过 iOS 快捷指令调用 Life Log 功能。

使用方法:
1. 安装依赖: pip install flask
2. 运行服务: python ios_api.py
3. 在 iOS 快捷指令中配置 API 端点

安全提示:
- 生产环境请使用 HTTPS
- 建议添加 API token 认证
- 使用环境变量管理敏感信息
"""

from flask import Flask, request, jsonify
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mobile_collector import Config, MicrosoftAuthenticator, OneNoteService, OneDriveService

app = Flask(__name__)

# API token 认证（可选但推荐）
API_TOKEN = os.environ.get('API_TOKEN', '')

def verify_token():
    """验证 API token"""
    if API_TOKEN:
        token = request.headers.get('Authorization', '')
        if not token.startswith('Bearer '):
            return False
        return token[7:] == API_TOKEN
    return True  # 如果未设置 token，则不验证

# 全局初始化配置和认证
config = Config()
auth = MicrosoftAuthenticator(
    client_id=config.get('microsoft.client_id'),
    client_secret=config.get('microsoft.client_secret'),
    redirect_uri=config.get('microsoft.redirect_uri'),
    scopes=config.get('microsoft.scopes')
)

@app.route('/')
def index():
    """健康检查端点"""
    return jsonify({
        'status': 'ok',
        'version': '1.1.0',
        'service': 'Life Log iOS API'
    })

@app.route('/api/note', methods=['POST'])
def create_note():
    """
    创建 OneNote 笔记
    
    请求体:
    {
        "title": "笔记标题",
        "content": "笔记内容"
    }
    
    响应:
    {
        "status": "success",
        "url": "https://...",
        "id": "..."
    }
    """
    if not verify_token():
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    
    try:
        data = request.json
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Invalid JSON'
            }), 400
        
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        
        if not title:
            return jsonify({
                'status': 'error',
                'message': 'Title is required'
            }), 400
        
        if not content:
            return jsonify({
                'status': 'error',
                'message': 'Content is required'
            }), 400
        
        # 创建 OneNote 服务并创建笔记
        service = OneNoteService(auth)
        result = service.create_page(title, content)
        
        return jsonify({
            'status': 'success',
            'url': result['links']['oneNoteWebUrl']['href'],
            'id': result['id']
        })
    
    except Exception as e:
        app.logger.error(f"Error creating note: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    上传文件到 OneDrive
    
    请求: multipart/form-data
    - file: 文件数据
    - folder: 目标文件夹路径（可选）
    
    响应:
    {
        "status": "success",
        "url": "https://...",
        "id": "..."
    }
    """
    if not verify_token():
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    
    try:
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'No file selected'
            }), 400
        
        folder = request.form.get('folder', '/')
        
        # 保存临时文件
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name
        
        try:
            # 上传到 OneDrive
            service = OneDriveService(auth)
            result = service.upload_file(tmp_path, folder, file.filename)
            
            return jsonify({
                'status': 'success',
                'url': result.get('webUrl', ''),
                'id': result.get('id', '')
            })
        finally:
            # 清理临时文件
            os.unlink(tmp_path)
    
    except Exception as e:
        app.logger.error(f"Error uploading file: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    """404 错误处理"""
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """500 错误处理"""
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500

if __name__ == '__main__':
    # 开发环境配置
    # 生产环境建议使用 gunicorn 等 WSGI 服务器
    # 例: gunicorn -w 4 -b 0.0.0.0:5000 ios_api:app
    
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print("=" * 50)
    print("Life Log iOS API Server")
    print("=" * 50)
    print(f"Port: {port}")
    print(f"Debug: {debug}")
    if API_TOKEN:
        print("Token authentication: Enabled")
    else:
        print("Token authentication: Disabled (警告: 建议设置 API_TOKEN)")
    print()
    print("端点:")
    print("  GET  /           - 健康检查")
    print("  POST /api/note   - 创建笔记")
    print("  POST /api/upload - 上传文件")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=port, debug=debug)
