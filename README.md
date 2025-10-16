# Life Log - 个人生活日志工具集

个人工具集项目，用于个人提升、文章备份、计划提醒等生活场景管理。

## 项目概述

Life Log 是一个复合型项目，包含多个逐步规划和完善的子项目。本项目统一在 `docs/` 目录下进行文档管理，分版本记录修改说明、用户故事、需求书、概要设计等文档。

## 当前版本: v1.1.0

### v1.1 功能特性

v1.1 版本在 v1.0 基础上增强了 iOS 平台支持：

- ✅ **OneNote 文章同步**: 将文本内容同步到 OneNote 笔记本
- ✅ **OneDrive 文件上传**: 上传文件和照片到 OneDrive
- ✅ **Microsoft 认证**: 使用 OAuth 2.0 安全认证
- ✅ **配置系统**: 灵活的配置管理，支持未来扩展（分类、目录映射等）
- 🆕 **iOS Pythonista 支持**: 完整的 Pythonista 集成方案和脚本
- 🆕 **iOS 快捷指令集成**: 通过 Siri 创建笔记的完整指南
- 🆕 **Flask API 封装**: 为移动端提供的轻量级 API 服务
- 🆕 **增强的移动端文档**: 详细的 iOS 使用指南和最佳实践

### 版本历史

- **v1.1.0** (2025-10-14): iOS 平台增强，详见 [v1.1 CHANGELOG](docs/v1.1/CHANGELOG.md)
- **v1.0.0** (2025-10-14): 初始版本，基础功能实现，详见 [v1.0 CHANGELOG](docs/v1.0/CHANGELOG.md)

## 快速开始

### 前置要求

1. Python 3.7 或更高版本
2. Microsoft 账户
3. 注册的 Microsoft 应用程序（获取 Client ID 和 Client Secret）

### 注册 Microsoft 应用程序

1. 访问 [Azure Portal](https://portal.azure.com/)
2. 进入 "Azure Active Directory" > "应用注册"
3. 点击 "新注册"
4. 填写应用名称（如 "Life Log"）
5. 选择 "任何组织目录中的帐户和个人 Microsoft 帐户"
6. 重定向 URI 选择 "Web"，填入 `http://localhost:8000/callback`
7. 注册后，记录下 "应用程序(客户端) ID"
8. 进入 "证书和密码"，创建新的客户端密码，记录下密码值
9. 进入 "API 权限"，添加以下权限：
   - Microsoft Graph > Notes.Create
   - Microsoft Graph > Notes.Read
   - Microsoft Graph > Files.ReadWrite

### 安装

1. 克隆仓库：
```bash
git clone https://github.com/zhaoqx/life-log.git
cd life-log
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置应用：
```bash
# 复制配置模板
cp config.example.json config.json

# 编辑 config.json，填入您的 Client ID 和 Client Secret
# 或者使用环境变量：
cp .env.example .env
# 编辑 .env 文件
```

### 使用方法

#### 1. 认证

首次使用需要进行 Microsoft 账户认证：

```bash
python cli.py auth
```

这将打开浏览器进行认证，完成后认证信息将被安全保存。

#### 2. 创建 OneNote 笔记

```bash
# 创建简单笔记
python cli.py note create "我的笔记标题" --content "笔记内容"

# 从文件创建笔记
python cli.py note create "今日总结" --file article.txt

# 指定笔记本和分区
python cli.py note create "会议记录" --content "..." --notebook-id <ID> --section-id <ID>
```

#### 3. 上传文件到 OneDrive

```bash
# 上传单个文件
python cli.py upload photo.jpg

# 上传多个文件
python cli.py upload photo1.jpg photo2.jpg document.pdf

# 指定目标文件夹
python cli.py upload photo.jpg --folder /Photos/2024
```

#### 4. 查看笔记本和文件

```bash
# 列出所有笔记本
python cli.py note list

# 列出笔记本和分区
python cli.py note list --sections

# 列出 OneDrive 文件
python cli.py drive list

# 列出指定文件夹
python cli.py drive list --folder /LifeLog
```

#### 5. 配置管理

```bash
# 查看当前配置
python cli.py config show

# 初始化配置文件
python cli.py config init
```

## iOS 移动端使用

v1.1 版本提供了完整的 iOS 平台支持方案：

### 方案一: Pythonista

在 iOS 上使用 Pythonista 应用直接运行脚本：

```python
# 使用提供的快速笔记脚本
python quick_note.py "我的标题" "我的内容"
```

### 方案二: iOS 快捷指令 + 服务器 API

1. 在服务器上运行 Flask API：
   ```bash
   python ios_api.py
   ```

2. 在 iOS 快捷指令中配置 API 调用

3. 通过 Siri 语音创建笔记

### 方案三: SSH 远程访问

使用 iOS SSH 客户端（如 Terminus）连接服务器使用完整功能。

**详细说明**: 查看 [手机使用指南](docs/MOBILE_GUIDE.md)

## 项目结构

```
life-log/
├── docs/                    # 文档目录
│   ├── v1.1/               # v1.1 版本文档
│   │   ├── CHANGELOG.md    # v1.1 变更日志
│   │   ├── USER_STORIES.md # v1.1 用户故事
│   │   ├── REQUIREMENTS.md # v1.1 需求规格
│   │   └── DESIGN.md       # v1.1 设计文档
│   ├── v1.0/               # v1.0 版本文档
│   │   ├── CHANGELOG.md    # v1.0 变更日志
│   │   ├── USER_STORIES.md # v1.0 用户故事
│   │   ├── REQUIREMENTS.md # v1.0 需求规格
│   │   └── DESIGN.md       # v1.0 设计文档
│   ├── MOBILE_GUIDE.md     # 手机使用指南
│   └── DEVELOPMENT.md      # 开发指南
├── mobile_collector/        # 主程序包
│   ├── __init__.py
│   ├── auth.py             # 认证模块
│   ├── config.py           # 配置管理
│   ├── onenote_service.py  # OneNote 服务
│   └── onedrive_service.py # OneDrive 服务
├── cli.py                  # 命令行接口
├── ios_api.py              # iOS 快捷指令 API (v1.1 新增)
├── quick_note.py           # Pythonista 快速笔记脚本 (v1.1 新增)
├── config.example.json     # 配置文件模板
├── .env.example            # 环境变量模板
├── requirements.txt        # 依赖列表
└── README.md              # 本文件
```

## 配置说明

### 配置文件 (config.json)

```json
{
  "microsoft": {
    "client_id": "您的应用程序ID",
    "client_secret": "您的应用程序密钥",
    "redirect_uri": "http://localhost:8000/callback",
    "scopes": ["Notes.Create", "Notes.Read", "Files.ReadWrite"]
  },
  "onenote": {
    "default_notebook_id": null,  // 默认笔记本ID（可选）
    "default_section_id": null    // 默认分区ID（可选）
  },
  "onedrive": {
    "default_folder": "/LifeLog"  // 默认上传文件夹
  },
  "categories": {
    "enabled": false,              // v2.0 功能预留
    "rules": []
  }
}
```

### 环境变量

也可以通过环境变量配置敏感信息：

- `MS_CLIENT_ID`: Microsoft 应用程序 ID
- `MS_CLIENT_SECRET`: Microsoft 应用程序密钥
- `MS_REDIRECT_URI`: 重定向 URI

## 安全提示

- ⚠️ **不要将 `config.json` 和 `.env` 文件提交到版本控制系统**
- ⚠️ 这些文件已在 `.gitignore` 中排除
- ⚠️ 认证令牌保存在 `.token_cache.json` 中，同样不应提交

## 未来计划

### v2.0 规划功能

- 自定义分类和标签系统
- 目录自动映射规则
- 定时同步功能
- 移动端应用界面
- 更多存储后端支持

### 扩展性

当前版本已为未来扩展做好准备：

- 配置系统支持分类规则定义
- 模块化设计支持添加新的存储后端
- 预留插件机制接口

## 文档

详细文档请查看 `docs/v1.0/` 目录：

- [变更日志](docs/v1.0/CHANGELOG.md)
- [用户故事](docs/v1.0/USER_STORIES.md)
- [需求规格说明](docs/v1.0/REQUIREMENTS.md)
- [概要设计说明](docs/v1.0/DESIGN.md)

## 常见问题

### 1. 认证失败怎么办？

确保：
- Client ID 和 Client Secret 配置正确
- 在 Azure Portal 中正确配置了重定向 URI
- API 权限已添加并授予管理员同意

### 2. 如何查看我的笔记本 ID？

运行 `python cli.py note list --sections` 可以看到所有笔记本和分区的 ID。

### 3. 上传大文件失败？

v1.0 版本适合上传小于 10MB 的文件。大文件上传将在后续版本中优化。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

本项目为个人工具，仅供学习和个人使用。

## 联系方式

- 作者: zhaoqx
- 项目地址: https://github.com/zhaoqx/life-log
