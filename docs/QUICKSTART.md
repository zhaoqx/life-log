# 快速入门指南

欢迎使用 Life Log！本指南将帮助您在 5 分钟内开始使用。

## 第一步：安装

```bash
# 克隆项目
git clone https://github.com/zhaoqx/life-log.git
cd life-log

# 安装依赖
pip install -r requirements.txt
```

## 第二步：注册 Microsoft 应用程序

这是**必需**的步骤，只需要做一次。

### 简化版说明

1. 访问 https://portal.azure.com/
2. 搜索并进入 "应用注册"
3. 点击 "新注册"，填写：
   - 名称：Life Log（或任意名称）
   - 支持的账户类型：选择最后一项（个人账户）
   - 重定向 URI：Web，`http://localhost:8000/callback`
4. 注册后，复制 **应用程序(客户端) ID**
5. 进入 "证书和密码" → "新客户端密码"，创建后复制**值**
6. 进入 "API 权限" → "添加权限" → "Microsoft Graph" → "委托的权限"
   - 添加：Notes.Create, Notes.Read, Files.ReadWrite
   - 点击 "授予管理员同意"

### 详细说明

如果您是第一次使用，请参考 [README.md](../README.md) 中的详细步骤。

## 第三步：配置应用

```bash
# 复制配置模板
cp config.example.json config.json

# 编辑配置文件
nano config.json  # 或使用您喜欢的编辑器
```

填入第二步获取的信息：

```json
{
  "microsoft": {
    "client_id": "粘贴您的应用程序ID",
    "client_secret": "粘贴您的客户端密码",
    "redirect_uri": "http://localhost:8000/callback",
    "scopes": [
      "Notes.Create",
      "Notes.Read", 
      "Files.ReadWrite"
    ]
  }
}
```

**提示**：也可以使用环境变量：

```bash
export MS_CLIENT_ID="您的ID"
export MS_CLIENT_SECRET="您的密码"
```

## 第四步：认证

```bash
python cli.py auth
```

这将：
1. 打开浏览器
2. 要求您登录 Microsoft 账户
3. 授权应用访问您的 OneNote 和 OneDrive
4. 自动保存认证信息

**提示**：如果浏览器没有自动打开，请手动复制显示的 URL。

## 第五步：开始使用

### 创建您的第一条笔记

```bash
python cli.py note create "我的第一条笔记" --content "Hello, Life Log!"
```

成功后，您会看到：
```
笔记创建成功！
页面ID: xxxx
页面URL: https://...
```

### 上传您的第一个文件

```bash
# 创建测试文件
echo "测试内容" > test.txt

# 上传到 OneDrive
python cli.py upload test.txt
```

### 查看您的笔记本

```bash
python cli.py note list --sections
```

### 查看 OneDrive 文件

```bash
python cli.py drive list
```

## 常用命令速查

```bash
# 认证
python cli.py auth

# 创建笔记
python cli.py note create "标题" --content "内容"
python cli.py note create "标题" --file article.txt

# 上传文件
python cli.py upload file.jpg
python cli.py upload photo1.jpg photo2.jpg --folder /Photos

# 查看信息
python cli.py note list
python cli.py drive list --folder /LifeLog

# 查看配置
python cli.py config show
```

## 下一步

### 手机使用

如果您想在手机上使用，请查看：
- [手机使用指南](./MOBILE_GUIDE.md)

### 进阶使用

- 查看 [examples.py](../examples.py) 了解如何在代码中使用
- 查看 [README.md](../README.md) 了解完整功能
- 查看 [DEVELOPMENT.md](./DEVELOPMENT.md) 了解如何扩展

### 自动化

创建快捷脚本 `quick_note.sh`：

```bash
#!/bin/bash
cd ~/life-log
python cli.py note create "$1" --content "$2"
```

使用：
```bash
chmod +x quick_note.sh
./quick_note.sh "灵感" "今天想到一个好主意..."
```

## 故障排查

### 问题：认证失败

**解决**：
1. 检查 Client ID 和 Secret 是否正确
2. 确认重定向 URI 是 `http://localhost:8000/callback`
3. 确认 API 权限已添加并授予同意

### 问题：找不到笔记本

**解决**：
1. 确保您的 Microsoft 账户中有 OneNote 笔记本
2. 访问 https://www.onenote.com/ 创建一个笔记本

### 问题：上传文件失败

**解决**：
1. 检查文件是否存在
2. 检查文件大小（v1.0 建议小于 10MB）
3. 检查网络连接

### 问题：令牌过期

**解决**：
```bash
# 删除缓存并重新认证
rm .token_cache.json
python cli.py auth
```

## 获取帮助

- 查看命令帮助：`python cli.py --help`
- 查看子命令帮助：`python cli.py note --help`
- 查看文档：[docs/v1.0/](./v1.0/)
- 提交 Issue：https://github.com/zhaoqx/life-log/issues

## 安全提示

⚠️ **重要**：
- 不要分享您的 `config.json` 文件
- 不要分享您的 `.token_cache.json` 文件
- 不要将这些文件提交到 Git（已在 `.gitignore` 中排除）

## 完成！

恭喜！您已经成功设置并使用 Life Log。

现在您可以：
- 📝 随时记录想法到 OneNote
- 📁 备份重要文件到 OneDrive
- 🔄 跨设备同步您的内容
- 🚀 探索更多功能

享受您的 Life Log 之旅！
