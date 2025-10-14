# 开发指南

本文档面向希望扩展或修改 Life Log 的开发者。

## 开发环境设置

### 1. 克隆仓库

```bash
git clone https://github.com/zhaoqx/life-log.git
cd life-log
```

### 2. 创建虚拟环境（推荐）

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置开发环境

```bash
cp config.example.json config.json
cp .env.example .env
# 编辑 config.json 或 .env，填入测试用的凭据
```

## 项目结构说明

```
life-log/
├── docs/                       # 文档目录
│   ├── v1.0/                  # v1.0 版本文档
│   │   ├── CHANGELOG.md       # 变更日志
│   │   ├── USER_STORIES.md    # 用户故事
│   │   ├── REQUIREMENTS.md    # 需求规格
│   │   └── DESIGN.md          # 概要设计
│   ├── MOBILE_GUIDE.md        # 手机使用指南
│   └── DEVELOPMENT.md         # 本文件
│
├── mobile_collector/           # 核心包
│   ├── __init__.py            # 包初始化
│   ├── auth.py                # 认证模块
│   ├── config.py              # 配置管理
│   ├── onenote_service.py     # OneNote 服务
│   └── onedrive_service.py    # OneDrive 服务
│
├── cli.py                      # 命令行接口
├── examples.py                 # 示例脚本
├── requirements.txt            # Python 依赖
├── config.example.json         # 配置模板
├── .env.example               # 环境变量模板
├── .gitignore                 # Git 忽略规则
└── README.md                  # 项目说明
```

## 核心模块详解

### 1. 认证模块 (`auth.py`)

**职责**：处理 Microsoft OAuth 2.0 认证

**关键类**：`MicrosoftAuthenticator`

**主要方法**：
- `authenticate()`: 执行完整认证流程
- `get_access_token()`: 获取有效访问令牌（自动刷新）
- `is_authenticated()`: 检查认证状态

**认证流程**：
1. 生成认证 URL
2. 启动本地服务器监听回调
3. 用户在浏览器中完成认证
4. 接收授权码
5. 交换访问令牌和刷新令牌
6. 保存令牌到缓存文件

**扩展点**：
- 支持设备码流程（无浏览器环境）
- 支持交互式令牌输入
- 多租户支持

### 2. 配置模块 (`config.py`)

**职责**：管理应用程序配置

**关键类**：`Config`

**配置层次**：
1. 默认配置（硬编码）
2. 配置文件（`config.json`）
3. 环境变量（最高优先级）

**配置访问**：
```python
config = Config()
client_id = config.get('microsoft.client_id')
config.set('onenote.default_notebook_id', 'xxx')
config.save()
```

**扩展点**：
- 支持 YAML 格式
- 配置验证和迁移
- 配置加密

### 3. OneNote 服务 (`onenote_service.py`)

**职责**：OneNote API 操作封装

**关键类**：`OneNoteService`

**主要功能**：
- 列出笔记本和分区
- 创建页面
- 查询页面信息

**API 端点**：
- `GET /me/onenote/notebooks`
- `GET /me/onenote/notebooks/{id}/sections`
- `POST /me/onenote/sections/{id}/pages`

**扩展点**：
- 更新页面内容
- 删除页面
- 支持图片和附件
- Markdown 转 OneNote HTML

### 4. OneDrive 服务 (`onedrive_service.py`)

**职责**：OneDrive API 操作封装

**关键类**：`OneDriveService`

**主要功能**：
- 上传文件（单个/批量）
- 创建文件夹
- 列出文件
- 查询文件信息

**API 端点**：
- `PUT /me/drive/root:/{path}:/content`
- `POST /me/drive/root/children`
- `GET /me/drive/root/children`

**扩展点**：
- 大文件分块上传
- 下载文件
- 文件移动和复制
- 共享链接生成

## 添加新功能

### 示例：添加 SharePoint 支持

1. 创建新服务模块：

```python
# mobile_collector/sharepoint_service.py

class SharePointService:
    GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0"
    
    def __init__(self, authenticator):
        self.authenticator = authenticator
    
    def _get_headers(self):
        token = self.authenticator.get_access_token()
        return {"Authorization": f"Bearer {token}"}
    
    def list_sites(self):
        # 实现逻辑
        pass
```

2. 在 `__init__.py` 中导出：

```python
from .sharepoint_service import SharePointService

__all__ = [
    # ...existing...
    'SharePointService',
]
```

3. 在 CLI 中添加命令：

```python
# cli.py

def cmd_sharepoint_list(args, config):
    """列出 SharePoint 站点"""
    # 实现逻辑
    pass

# 在 main() 中添加子解析器
parser_sharepoint = subparsers.add_parser('sharepoint', help='SharePoint操作')
# ...
```

4. 更新文档和测试

### 示例：添加分类功能

1. 更新配置结构：

```json
{
  "categories": {
    "enabled": true,
    "rules": [
      {
        "name": "工作",
        "keywords": ["工作", "会议"],
        "onenote_section": "Work",
        "onedrive_folder": "/Work"
      }
    ]
  }
}
```

2. 创建分类模块：

```python
# mobile_collector/categorizer.py

class Categorizer:
    def __init__(self, config):
        self.rules = config.get('categories.rules', [])
    
    def categorize(self, title, content):
        """根据标题和内容判断分类"""
        for rule in self.rules:
            for keyword in rule['keywords']:
                if keyword in title or keyword in content:
                    return rule
        return None
```

3. 集成到服务中：

```python
# 在 OneNoteService.create_page 中
from .categorizer import Categorizer

def create_page(self, title, content, **kwargs):
    if self.config.get('categories.enabled'):
        categorizer = Categorizer(self.config)
        category = categorizer.categorize(title, content)
        if category:
            kwargs['section_name'] = category['onenote_section']
    
    # 继续现有逻辑
```

## 测试

### 单元测试

创建 `tests/` 目录：

```python
# tests/test_config.py

import unittest
from mobile_collector.config import Config

class TestConfig(unittest.TestCase):
    def test_default_config(self):
        config = Config()
        self.assertEqual(config.get('microsoft.redirect_uri'), 
                        'http://localhost:8000/callback')
    
    def test_get_nested_key(self):
        config = Config()
        self.assertIsNotNone(config.get('microsoft.client_id'))
```

运行测试：
```bash
python -m unittest discover tests
```

### 集成测试

需要真实的 Microsoft 应用程序凭据：

```python
# tests/integration/test_onenote.py

import unittest
from mobile_collector import Config, MicrosoftAuthenticator, OneNoteService

class TestOneNoteIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        config = Config()
        cls.auth = MicrosoftAuthenticator(...)
        cls.service = OneNoteService(cls.auth)
    
    def test_list_notebooks(self):
        notebooks = self.service.list_notebooks()
        self.assertIsInstance(notebooks, list)
```

## 调试技巧

### 1. 启用详细日志

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 2. 查看 API 请求

使用 `requests` 的事件钩子：

```python
import requests

def log_request(response, *args, **kwargs):
    print(f"{response.request.method} {response.request.url}")
    print(f"Status: {response.status_code}")

session = requests.Session()
session.hooks['response'] = log_request
```

### 3. 令牌调试

查看令牌内容（JWT）：

```python
import base64
import json

def decode_jwt(token):
    parts = token.split('.')
    payload = parts[1]
    # 添加填充
    payload += '=' * (4 - len(payload) % 4)
    decoded = base64.b64decode(payload)
    return json.loads(decoded)

token = authenticator.get_access_token()
print(decode_jwt(token))
```

## 代码规范

### Python 风格

遵循 PEP 8：

```bash
# 安装 linter
pip install flake8 black

# 检查代码
flake8 mobile_collector/

# 格式化代码
black mobile_collector/
```

### 文档字符串

使用 Google 风格：

```python
def create_page(title: str, content: str) -> Dict:
    """
    创建 OneNote 页面
    
    Args:
        title: 页面标题
        content: 页面内容
    
    Returns:
        创建的页面信息字典，包含 id 和 url
    
    Raises:
        Exception: 当认证失败或 API 调用失败时
    """
    pass
```

### 类型提示

使用类型提示增强代码可读性：

```python
from typing import Optional, List, Dict

def list_files(folder_path: Optional[str] = None) -> List[Dict]:
    pass
```

## 发布流程

### 1. 更新版本号

在 `mobile_collector/__init__.py` 中：

```python
__version__ = '1.1.0'
```

### 2. 更新 CHANGELOG

在 `docs/v1.1/CHANGELOG.md` 中记录变更。

### 3. 创建标签

```bash
git tag -a v1.1.0 -m "Release version 1.1.0"
git push origin v1.1.0
```

### 4. 打包（可选）

```bash
# 安装打包工具
pip install build

# 构建包
python -m build

# 发布到 PyPI（如果需要）
pip install twine
twine upload dist/*
```

## 贡献指南

1. Fork 仓库
2. 创建特性分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'Add amazing feature'`
4. 推送到分支：`git push origin feature/amazing-feature`
5. 创建 Pull Request

### Pull Request 检查清单

- [ ] 代码遵循项目风格
- [ ] 添加了必要的文档
- [ ] 添加了测试（如适用）
- [ ] 所有测试通过
- [ ] 更新了 CHANGELOG
- [ ] 更新了 README（如有新功能）

## 常见问题

### Q: 如何调试认证问题？

A: 
1. 检查 Client ID 和 Secret 是否正确
2. 验证重定向 URI 配置是否匹配
3. 查看浏览器控制台的错误信息
4. 使用 `--verbose` 选项查看详细日志

### Q: 如何处理 API 限流？

A: Microsoft Graph API 有速率限制。建议：
- 实现指数退避重试
- 批量操作时添加延迟
- 使用 `Retry-After` 响应头

```python
import time

def call_api_with_retry(func, max_retries=3):
    for i in range(max_retries):
        try:
            return func()
        except Exception as e:
            if i < max_retries - 1:
                wait = 2 ** i
                print(f"重试中... 等待 {wait} 秒")
                time.sleep(wait)
            else:
                raise
```

### Q: 如何添加新的 OAuth 作用域？

A: 
1. 在 `config.json` 的 `scopes` 中添加
2. 在 Azure Portal 中授权新的 API 权限
3. 删除 `.token_cache.json` 重新认证

## 资源链接

- [Microsoft Graph API 文档](https://docs.microsoft.com/graph/)
- [OneNote API 参考](https://docs.microsoft.com/graph/api/resources/onenote)
- [OneDrive API 参考](https://docs.microsoft.com/graph/api/resources/onedrive)
- [OAuth 2.0 规范](https://oauth.net/2/)
- [MSAL Python 文档](https://msal-python.readthedocs.io/)

## 下一步

- 实现单元测试覆盖
- 添加 CI/CD 流程
- 创建 Docker 镜像
- 开发 Web 界面
- 移动端原生应用
