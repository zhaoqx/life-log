# 概要设计说明书

## 1. 系统架构

### 1.1 总体架构
```
┌─────────────────────────────────────────┐
│         用户接口层 (CLI/API)             │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│          业务逻辑层                      │
│  ┌─────────────┐  ┌──────────────────┐ │
│  │  OneNote    │  │   OneDrive       │ │
│  │  Service    │  │   Service        │ │
│  └─────────────┘  └──────────────────┘ │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│          Microsoft Graph API层          │
│  ┌─────────────┐  ┌──────────────────┐ │
│  │   认证      │  │   Graph API      │ │
│  │   模块      │  │   客户端         │ │
│  └─────────────┘  └──────────────────┘ │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│      配置与工具层                        │
│  ┌─────────────┐  ┌──────────────────┐ │
│  │   配置      │  │   日志           │ │
│  │   管理      │  │   工具           │ │
│  └─────────────┘  └──────────────────┘ │
└─────────────────────────────────────────┘
```

### 1.2 技术选型
- **开发语言**: Python 3.7+
- **API交互**: Microsoft Graph API
- **认证协议**: OAuth 2.0
- **HTTP客户端**: requests / msal (Microsoft Authentication Library)
- **配置格式**: JSON/YAML
- **日志**: Python logging模块

## 2. 模块设计

### 2.1 认证模块 (auth.py)
**职责**: 处理Microsoft OAuth 2.0认证流程

**主要类**:
```python
class MicrosoftAuthenticator:
    def __init__(self, client_id, client_secret, redirect_uri)
    def get_auth_url() -> str
    def get_token_from_code(code: str) -> dict
    def refresh_token(refresh_token: str) -> dict
    def get_access_token() -> str
```

**关键功能**:
- 生成认证URL
- 通过授权码获取令牌
- 刷新访问令牌
- 令牌缓存和自动刷新

---

### 2.2 OneNote服务模块 (onenote_service.py)
**职责**: 提供OneNote操作接口

**主要类**:
```python
class OneNoteService:
    def __init__(self, authenticator)
    def create_page(title: str, content: str, 
                   notebook_id: str = None, 
                   section_id: str = None) -> dict
    def list_notebooks() -> list
    def list_sections(notebook_id: str) -> list
    def get_default_notebook() -> dict
```

**关键功能**:
- 创建OneNote页面
- 查询笔记本列表
- 查询分区列表
- 获取默认笔记本

---

### 2.3 OneDrive服务模块 (onedrive_service.py)
**职责**: 提供OneDrive文件操作接口

**主要类**:
```python
class OneDriveService:
    def __init__(self, authenticator)
    def upload_file(file_path: str, 
                   target_folder: str = None) -> dict
    def upload_files(file_paths: list, 
                    target_folder: str = None) -> list
    def create_folder(folder_path: str) -> dict
    def list_files(folder_path: str = None) -> list
```

**关键功能**:
- 单文件上传
- 批量文件上传
- 创建文件夹
- 列出文件

---

### 2.4 配置管理模块 (config.py)
**职责**: 管理应用程序配置

**主要类**:
```python
class Config:
    def __init__(self, config_file: str = None)
    def get(key: str, default = None)
    def set(key: str, value)
    def save()
    def load_from_env()
```

**配置结构**:
```json
{
  "microsoft": {
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET",
    "redirect_uri": "http://localhost:8000/callback",
    "scopes": [
      "Notes.Create",
      "Notes.Read",
      "Files.ReadWrite"
    ]
  },
  "onenote": {
    "default_notebook_id": null,
    "default_section_id": null
  },
  "onedrive": {
    "default_folder": "/LifeLog"
  },
  "categories": {
    "enabled": false,
    "rules": []
  }
}
```

---

### 2.5 命令行接口模块 (cli.py)
**职责**: 提供命令行操作接口

**主要命令**:
- `auth` - 执行认证流程
- `note create` - 创建OneNote笔记
- `upload` - 上传文件到OneDrive
- `config` - 配置管理

## 3. 数据流设计

### 3.1 认证流程
```
1. 用户 -> CLI: 执行auth命令
2. CLI -> Auth模块: 请求认证URL
3. Auth模块 -> 用户: 返回认证URL
4. 用户 -> Microsoft: 在浏览器中完成认证
5. Microsoft -> 本地服务器: 返回授权码
6. CLI -> Auth模块: 使用授权码请求令牌
7. Auth模块 -> Microsoft Graph API: 交换令牌
8. Microsoft Graph API -> Auth模块: 返回访问令牌和刷新令牌
9. Auth模块 -> 本地存储: 保存令牌
```

### 3.2 创建笔记流程
```
1. 用户 -> CLI: 执行note create命令
2. CLI -> Config: 读取配置
3. CLI -> Auth模块: 获取访问令牌
4. CLI -> OneNote服务: 调用create_page
5. OneNote服务 -> Graph API: POST请求创建页面
6. Graph API -> OneNote服务: 返回页面信息
7. OneNote服务 -> CLI: 返回结果
8. CLI -> 用户: 显示成功信息
```

### 3.3 文件上传流程
```
1. 用户 -> CLI: 执行upload命令
2. CLI -> Config: 读取配置
3. CLI -> Auth模块: 获取访问令牌
4. CLI -> OneDrive服务: 调用upload_file
5. OneDrive服务 -> 本地文件系统: 读取文件
6. OneDrive服务 -> Graph API: PUT请求上传文件
7. Graph API -> OneDrive服务: 返回文件信息
8. OneDrive服务 -> CLI: 返回结果
9. CLI -> 用户: 显示成功信息
```

## 4. 接口设计

### 4.1 Microsoft Graph API接口

**OneNote API**:
- `GET /me/onenote/notebooks` - 获取笔记本列表
- `GET /me/onenote/notebooks/{id}/sections` - 获取分区列表
- `POST /me/onenote/sections/{id}/pages` - 创建页面

**OneDrive API**:
- `GET /me/drive/root/children` - 列出根目录文件
- `PUT /me/drive/root:/{path}:/content` - 上传文件
- `POST /me/drive/root/children` - 创建文件夹

### 4.2 内部模块接口
详见各模块设计部分的类接口定义。

## 5. 错误处理

### 5.1 错误类型
- **认证错误**: 令牌无效、过期、权限不足
- **网络错误**: 连接超时、请求失败
- **业务错误**: 文件不存在、笔记本不存在
- **配置错误**: 配置缺失、格式错误

### 5.2 错误处理策略
- 所有异常统一捕获和记录
- 提供友好的错误提示信息
- 对于可重试的错误进行自动重试
- 对于令牌过期自动刷新

## 6. 安全设计

### 6.1 令牌安全
- 访问令牌和刷新令牌加密存储
- 令牌文件权限限制（仅所有者可读写）
- 不在日志中记录敏感信息

### 6.2 配置安全
- 敏感配置通过环境变量提供
- 提供配置文件模板（不含敏感信息）
- 在.gitignore中排除真实配置文件

## 7. 扩展性设计

### 7.1 分类系统预留
配置文件中预留`categories`配置项，未来可以实现：
```json
{
  "categories": {
    "enabled": true,
    "rules": [
      {
        "name": "工作笔记",
        "keywords": ["工作", "会议"],
        "onenote_section": "Work",
        "onedrive_folder": "/Work"
      },
      {
        "name": "个人日记",
        "keywords": ["日记", "随笔"],
        "onenote_section": "Diary",
        "onedrive_folder": "/Personal"
      }
    ]
  }
}
```

### 7.2 插件机制预留
- 模块化设计，易于添加新的服务提供商
- 统一的接口定义，支持不同实现
- 配置驱动，无需修改代码即可扩展

## 8. 部署设计

### 8.1 部署方式
- Python包安装（pip install）
- 直接克隆仓库运行
- 未来支持Docker容器化部署

### 8.2 环境要求
- Python 3.7+
- 网络连接（访问Microsoft Graph API）
- Microsoft账户和应用程序注册

### 8.3 初始化步骤
1. 安装依赖：`pip install -r requirements.txt`
2. 创建配置文件：复制`config.example.json`到`config.json`
3. 配置应用程序凭据
4. 执行认证：`python cli.py auth`
5. 开始使用
