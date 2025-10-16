# 概要设计文档 - v1.1

## 1. 设计概述

### 1.1 设计目标
v1.1 版本专注于增强 iOS 平台支持，在不修改核心代码的前提下，通过文档、示例和集成方案，让 iOS 用户能够充分利用 Life Log 的功能。

### 1.2 设计原则
- **最小改动**: 保持 v1.0 核心代码不变
- **文档驱动**: 通过完善文档实现平台支持
- **实用优先**: 提供可直接使用的脚本和示例
- **向后兼容**: 不引入破坏性变更

## 2. iOS 集成架构

### 2.1 架构图

```
┌─────────────────────────────────────────────────┐
│              iOS 设备                            │
│                                                  │
│  ┌──────────────┐      ┌──────────────┐        │
│  │ Pythonista   │      │ 快捷指令 App │        │
│  │              │      │              │        │
│  │ quick_note.py│      │ HTTP Request │        │
│  └──────┬───────┘      └──────┬───────┘        │
│         │                     │                 │
│         │ Direct API          │ HTTPS           │
└─────────┼─────────────────────┼─────────────────┘
          │                     │
          │                     ▼
          │              ┌─────────────┐
          │              │ 服务器      │
          │              │             │
          │              │ Flask API   │
          │              │ Wrapper     │
          │              └──────┬──────┘
          │                     │
          └─────────────────────┘
                    │
                    ▼
          ┌─────────────────┐
          │ Life Log Core   │
          │                 │
          │ - Auth          │
          │ - OneNote       │
          │ - OneDrive      │
          └────────┬────────┘
                   │
                   ▼
          ┌─────────────────┐
          │ Microsoft Graph │
          │ API             │
          └─────────────────┘
```

### 2.2 使用场景

#### 场景一: Pythonista 直接调用
iOS 用户在 Pythonista 应用中直接运行 Python 脚本，调用 Life Log API。

**优点**:
- 无需服务器
- 完全离线工作（除 API 调用）
- 功能完整

**缺点**:
- 需要安装 Pythonista（付费应用）
- 部分依赖库需手动安装

#### 场景二: 快捷指令 + 服务器 API
通过 iOS 快捷指令调用服务器上的 Flask API，API 内部调用 Life Log。

**优点**:
- 使用系统自带快捷指令
- 支持 Siri 语音创建
- 可集成到 iOS 自动化

**缺点**:
- 需要运行服务器
- 网络依赖

#### 场景三: SSH 远程执行
通过 SSH 客户端连接服务器，直接执行命令行。

**优点**:
- 功能完整
- 适合技术用户
- 可以执行复杂操作

**缺点**:
- 需要服务器
- 操作相对复杂

## 3. 关键组件设计

### 3.1 Pythonista 快速笔记脚本

**文件**: `quick_note.py`

**设计要点**:
```python
#!/usr/bin/env python3
"""
Pythonista 快速笔记脚本
用法: python quick_note.py "标题" "内容"
"""

import sys
from mobile_collector import Config, MicrosoftAuthenticator, OneNoteService

def quick_note(title, content):
    """创建快速笔记到 OneNote"""
    # 初始化配置
    config = Config()
    
    # 创建认证器
    auth = MicrosoftAuthenticator(
        client_id=config.get('microsoft.client_id'),
        client_secret=config.get('microsoft.client_secret'),
        redirect_uri=config.get('microsoft.redirect_uri'),
        scopes=config.get('microsoft.scopes')
    )
    
    # 创建 OneNote 服务
    service = OneNoteService(auth)
    
    # 创建页面
    result = service.create_page(title, content)
    
    # 输出结果
    print(f"✓ 笔记已创建: {result['links']['oneNoteWebUrl']['href']}")
    return result

if __name__ == '__main__':
    if len(sys.argv) >= 3:
        quick_note(sys.argv[1], sys.argv[2])
    else:
        print("用法: python quick_note.py '标题' '内容'")
        sys.exit(1)
```

**使用方式**:
```python
# 在 Pythonista 中运行
python quick_note.py "今日想法" "这是一个好主意..."
```

### 3.2 Flask API 封装

**文件**: `ios_api.py`

**设计要点**:
```python
from flask import Flask, request, jsonify
from mobile_collector import Config, MicrosoftAuthenticator, OneNoteService, OneDriveService

app = Flask(__name__)

# 全局配置和服务初始化
config = Config()
auth = MicrosoftAuthenticator(
    client_id=config.get('microsoft.client_id'),
    client_secret=config.get('microsoft.client_secret'),
    redirect_uri=config.get('microsoft.redirect_uri'),
    scopes=config.get('microsoft.scopes')
)

@app.route('/api/note', methods=['POST'])
def create_note():
    """创建笔记 API"""
    try:
        data = request.json
        title = data.get('title')
        content = data.get('content')
        
        if not title or not content:
            return jsonify({
                'status': 'error',
                'message': 'Title and content are required'
            }), 400
        
        # 创建笔记
        service = OneNoteService(auth)
        result = service.create_page(title, content)
        
        return jsonify({
            'status': 'success',
            'url': result['links']['oneNoteWebUrl']['href'],
            'id': result['id']
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """上传文件 API"""
    try:
        # 处理文件上传
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No file provided'
            }), 400
        
        file = request.files['file']
        folder = request.form.get('folder', '/')
        
        # 上传到 OneDrive
        service = OneDriveService(auth)
        result = service.upload_file(file, folder)
        
        return jsonify({
            'status': 'success',
            'url': result['webUrl'],
            'id': result['id']
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    # 生产环境建议使用 gunicorn 等 WSGI 服务器
    app.run(host='0.0.0.0', port=5000, ssl_context='adhoc')
```

**部署**:
```bash
# 安装依赖
pip install flask pyopenssl

# 运行服务
python ios_api.py
```

### 3.3 iOS 快捷指令配置

**快捷指令流程**:
1. 获取文本输入（或使用 Siri 听写）
2. 设置变量（标题、内容）
3. 构建 JSON 请求体
4. 发送 POST 请求到服务器 API
5. 解析响应
6. 显示通知或打开链接

**示例配置**:
```
1. 添加"询问输入"操作 → 提示"笔记标题"
2. 添加"文本"操作 → 设为变量"标题"
3. 添加"询问输入"操作 → 提示"笔记内容"
4. 添加"文本"操作 → 设为变量"内容"
5. 添加"获取URL内容"操作:
   - URL: https://your-server.com/api/note
   - 方法: POST
   - 请求体: JSON
     {
       "title": "标题",
       "content": "内容"
     }
6. 添加"显示通知"操作 → 显示成功消息
```

## 4. 安全设计

### 4.1 API 认证
建议为 Flask API 添加简单的 token 认证:

```python
API_TOKEN = os.environ.get('API_TOKEN', 'your-secret-token')

@app.before_request
def verify_token():
    if request.endpoint not in ['health']:
        token = request.headers.get('Authorization')
        if not token or token != f'Bearer {API_TOKEN}':
            return jsonify({'error': 'Unauthorized'}), 401
```

### 4.2 HTTPS 加密
- 生产环境必须使用 HTTPS
- 可使用 Let's Encrypt 免费证书
- 或使用 nginx 作为反向代理处理 SSL

### 4.3 配置文件保护
```bash
# 设置适当的文件权限
chmod 600 config.json
chmod 600 .env
```

## 5. 数据流设计

### 5.1 创建笔记流程

```
用户输入
  ├─> Pythonista: 
  │   └─> quick_note.py
  │       └─> Life Log API
  │           └─> Microsoft Graph API
  │               └─> OneNote
  │
  └─> iOS 快捷指令:
      └─> HTTP Request
          └─> Flask API
              └─> Life Log API
                  └─> Microsoft Graph API
                      └─> OneNote
```

### 5.2 上传文件流程

```
文件选择
  ├─> Pythonista photos 模块:
  │   └─> 获取照片数据
  │       └─> Life Log API
  │           └─> Microsoft Graph API
  │               └─> OneDrive
  │
  └─> 快捷指令文件输入:
      └─> HTTP Multipart Upload
          └─> Flask API
              └─> Life Log API
                  └─> Microsoft Graph API
                      └─> OneDrive
```

## 6. 错误处理

### 6.1 常见错误场景

1. **认证失败**
   - 检查配置文件
   - 重新认证
   - 验证 token 有效性

2. **网络错误**
   - 检查网络连接
   - 重试机制
   - 超时处理

3. **API 限制**
   - 遵守速率限制
   - 实现退避策略

### 6.2 错误消息设计

所有错误消息应该:
- 清晰描述问题
- 提供可能的解决方案
- 记录详细日志供调试

## 7. 性能优化

### 7.1 Pythonista 优化
- 缓存认证 token
- 避免重复导入
- 使用异步 API（如适用）

### 7.2 API 优化
- 使用连接池
- 实现请求缓存
- 异步处理长时间操作

## 8. 测试策略

### 8.1 手动测试
- [ ] 在实际 iOS 设备上测试 Pythonista 脚本
- [ ] 测试快捷指令端到端流程
- [ ] 验证 SSH 连接和命令执行

### 8.2 文档测试
- [ ] 所有代码示例可运行
- [ ] 配置步骤准确无误
- [ ] 链接有效

## 9. 部署指南

### 9.1 Pythonista 部署
1. 安装 Pythonista app
2. 创建 life-log 文件夹
3. 复制脚本和配置文件
4. 安装必要的依赖库

### 9.2 服务器部署
1. 安装 Python 和依赖
2. 配置 Flask API
3. 设置 SSL 证书
4. 配置防火墙规则
5. 设置服务自动启动

### 9.3 快捷指令配置
1. 创建新快捷指令
2. 配置 API 端点
3. 添加认证 token
4. 测试和调试

## 10. 文档结构

### 10.1 v1.1 文档
- CHANGELOG.md - 变更日志
- USER_STORIES.md - 用户故事
- REQUIREMENTS.md - 需求规格
- DESIGN.md - 本文档

### 10.2 更新的文档
- MOBILE_GUIDE.md - 增强 iOS 章节
- README.md - 添加 v1.1 引用
- DEVELOPMENT.md - iOS 开发注意事项

## 11. 未来改进

### 11.1 短期改进（v1.2）
- 添加更多自动化示例
- 优化 Pythonista 脚本性能
- 增强错误处理和用户反馈

### 11.2 长期规划（v2.0）
- 开发原生 iOS 应用
- 实现本地数据缓存
- 支持离线模式
- 添加小组件支持
