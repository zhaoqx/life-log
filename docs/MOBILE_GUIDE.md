# 手机使用指南

本指南介绍如何在手机上使用 Life Log 工具采集信息到 OneNote 和 OneDrive。

## 方案一：Termux（Android）

### 安装步骤

1. 从 F-Droid 或 Google Play 安装 Termux
2. 在 Termux 中安装 Python：
```bash
pkg update
pkg install python git
```

3. 克隆项目：
```bash
git clone https://github.com/zhaoqx/life-log.git
cd life-log
```

4. 安装依赖：
```bash
pip install -r requirements.txt
```

5. 配置应用：
```bash
cp config.example.json config.json
nano config.json  # 编辑配置文件
```

### 使用方法

```bash
# 首次认证
python cli.py auth

# 创建笔记
python cli.py note create "今日想法" --content "这是我今天的想法..."

# 上传照片
python cli.py upload /sdcard/DCIM/photo.jpg --folder /Photos

# 上传文档
python cli.py upload ~/document.pdf --folder /Documents
```

### 快捷方式

创建别名以简化命令：

```bash
# 编辑 .bashrc
nano ~/.bashrc

# 添加以下内容
alias lifelog="cd ~/life-log && python cli.py"
alias note="cd ~/life-log && python cli.py note create"
alias upload="cd ~/life-log && python cli.py upload"

# 重新加载配置
source ~/.bashrc
```

使用快捷方式：
```bash
note "会议记录" --file meeting_notes.txt
upload photo1.jpg photo2.jpg --folder /Photos
```

## 方案二：Pythonista（iOS）

Pythonista 是 iOS 上的专业 Python 开发环境，非常适合运行 Life Log。

### 安装步骤

1. **安装 Pythonista**
   - 从 App Store 下载安装 Pythonista 3
   - 注意: Pythonista 是付费应用

2. **获取 Life Log**
   - 方法一: 使用 Pythonista 的 Git 客户端克隆仓库
   - 方法二: 从电脑通过 iCloud 或 iTunes 文件共享传输文件
   - 方法三: 使用 Pythonista 的 WebDAV 功能

3. **安装依赖库**
   
   在 Pythonista 控制台中执行：
   ```python
   import requests  # Pythonista 自带
   
   # 安装 msal（需要手动）
   # 1. 从 PyPI 下载 msal 包
   # 2. 解压到 site-packages 目录
   # 或使用 StaSh（Pythonista shell）
   import requests
   import zipfile
   import os
   
   # 下载并安装 msal
   # 注意: 这是简化示例，实际可能需要处理依赖
   ```

4. **配置文件**
   
   创建 `config.json`：
   ```json
   {
     "microsoft": {
       "client_id": "你的应用ID",
       "client_secret": "你的应用密钥",
       "redirect_uri": "http://localhost:8000/callback",
       "scopes": [
         "Notes.Create",
         "Notes.Read",
         "Files.ReadWrite"
       ]
     }
   }
   ```

### 使用方法

**快速开始 - 使用提供的脚本**

项目包含预制的 `quick_note.py` 脚本，可直接使用：

```python
# 在 Pythonista 中运行
python quick_note.py "我的标题" "我的内容"

# 或从文件读取
python quick_note.py "会议记录" --file notes.txt
```

**自定义脚本示例**

创建自己的快捷脚本：

```python
import sys
from mobile_collector import Config, MicrosoftAuthenticator, OneNoteService

def quick_note(title, content):
    config = Config()
    auth = MicrosoftAuthenticator(
        client_id=config.get('microsoft.client_id'),
        client_secret=config.get('microsoft.client_secret'),
        redirect_uri=config.get('microsoft.redirect_uri'),
        scopes=config.get('microsoft.scopes')
    )
    
    service = OneNoteService(auth)
    result = service.create_page(title, content)
    print(f"笔记已创建: {result['links']['oneNoteWebUrl']['href']}")

if __name__ == '__main__':
    if len(sys.argv) >= 3:
        quick_note(sys.argv[1], sys.argv[2])
    else:
        print("用法: python quick_note.py '标题' '内容'")
```

**上传照片示例**

```python
import photos
from mobile_collector import Config, MicrosoftAuthenticator, OneDriveService

def upload_photo():
    # 从相册选择照片
    img = photos.pick_image()
    if img is None:
        print("未选择照片")
        return
    
    # 保存临时文件
    import tempfile
    import os
    tmp_path = os.path.join(tempfile.gettempdir(), 'photo.jpg')
    img.save(tmp_path)
    
    # 上传到 OneDrive
    config = Config()
    auth = MicrosoftAuthenticator(
        client_id=config.get('microsoft.client_id'),
        client_secret=config.get('microsoft.client_secret'),
        redirect_uri=config.get('microsoft.redirect_uri'),
        scopes=config.get('microsoft.scopes')
    )
    
    service = OneDriveService(auth)
    result = service.upload_file(tmp_path, '/Photos')
    
    print(f"照片已上传: {result['webUrl']}")
    
    # 清理临时文件
    os.unlink(tmp_path)

if __name__ == '__main__':
    upload_photo()
```

### Pythonista 小技巧

1. **添加到主屏幕**
   - 在 Pythonista 中长按脚本
   - 选择 "分享" > "添加到主屏幕"
   - 可以直接从主屏幕运行脚本

2. **使用小组件**
   - Pythonista 支持 iOS 小组件
   - 可以创建快捷笔记小组件

3. **整合 iOS 分享表单**
   - 使用 Pythonista 的 Share Extension
   - 可以从其他应用分享内容到 Life Log

### 常见问题

**Q: 如何处理认证？**

A: Pythonista 环境下认证稍复杂，建议：
1. 在电脑上先完成认证
2. 将生成的 `.auth_cache.json` 复制到 iOS 设备
3. 或使用设备码流程（需要额外配置）

**Q: MSAL 依赖安装困难？**

A: 可以考虑：
1. 使用 StaSh (Pythonista shell) 安装
2. 手动下载 wheel 文件并解压
3. 或使用远程服务器方案（方案三/四）

## 方案三：远程服务器（所有平台）

### 设置步骤

1. 在服务器上安装 Life Log
2. 使用 SSH 从手机连接服务器
3. 推荐的 SSH 客户端：
   - Android: Termux, JuiceSSH
   - iOS: Terminus, Prompt

### 使用方法

```bash
# 连接服务器
ssh user@your-server.com

# 切换到项目目录
cd ~/life-log

# 使用工具
python cli.py note create "远程笔记" --content "内容..."
```

## 方案四：快捷指令（iOS）+ 服务器

这是最适合日常使用的 iOS 方案，可以通过 Siri 语音创建笔记。

### 设置步骤

#### 1. 服务器端部署

在服务器上部署 Life Log API：

```bash
# 克隆项目
git clone https://github.com/zhaoqx/life-log.git
cd life-log

# 安装依赖
pip install -r requirements.txt
pip install flask

# 配置
cp config.example.json config.json
# 编辑 config.json 填入 Microsoft 凭据

# 首次认证
python cli.py auth

# 运行 API 服务
python ios_api.py
```

**生产环境部署（推荐）**：

```bash
# 安装 gunicorn
pip install gunicorn

# 使用 gunicorn 运行
gunicorn -w 4 -b 0.0.0.0:5000 ios_api:app

# 或使用 systemd 服务
sudo nano /etc/systemd/system/lifelog-api.service
```

示例 systemd 配置：
```ini
[Unit]
Description=Life Log iOS API
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/life-log
Environment="API_TOKEN=your-secret-token"
ExecStart=/usr/bin/gunicorn -w 4 -b 0.0.0.0:5000 ios_api:app
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl enable lifelog-api
sudo systemctl start lifelog-api
```

#### 2. 配置 HTTPS（重要）

使用 Nginx 和 Let's Encrypt：

```bash
# 安装 Nginx
sudo apt install nginx certbot python3-certbot-nginx

# 配置 Nginx
sudo nano /etc/nginx/sites-available/lifelog
```

Nginx 配置示例：
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

获取 SSL 证书：
```bash
sudo certbot --nginx -d your-domain.com
```

#### 3. 设置 API Token（安全）

```bash
# 设置环境变量
export API_TOKEN="your-secret-token-here"

# 或在 systemd 服务中配置
```

### iOS 快捷指令配置

#### 创建"快速笔记"快捷指令

1. **打开快捷指令 app**

2. **创建新快捷指令**，添加以下操作：

   **操作 1: 听写文本**
   - 添加 "听写文本" 操作
   - 语言: 中文（或你的语言）
   - 将结果存为变量 "笔记内容"

   **操作 2: 询问输入**（可选标题）
   - 添加 "询问输入" 操作
   - 提示: "笔记标题（可选）"
   - 默认答案: "快速笔记"
   - 将结果存为变量 "笔记标题"

   **操作 3: 获取 URL 内容**
   - 添加 "获取 URL 内容" 操作
   - URL: `https://your-domain.com/api/note`
   - 方法: `POST`
   - 请求头:
     - `Authorization`: `Bearer your-secret-token`
     - `Content-Type`: `application/json`
   - 请求体: `JSON`
     ```json
     {
       "title": "笔记标题",
       "content": "笔记内容"
     }
     ```

   **操作 4: 从输入获取字典值**
   - 键: `url`
   - 获取 OneNote 链接

   **操作 5: 显示通知**
   - 标题: "笔记创建成功"
   - 正文: "已保存到 OneNote"

   **操作 6: 打开 URL**（可选）
   - 打开上一步获取的 URL

3. **配置 Siri**
   - 为快捷指令添加 Siri 短语
   - 例如: "创建笔记"、"记录想法"

4. **添加到主屏幕**
   - 在快捷指令详情中
   - 选择 "添加到主屏幕"
   - 设置图标和名称

### 高级快捷指令示例

#### 语音笔记
```
1. 听写文本 → 笔记内容
2. 获取当前日期 → 格式化为 "YYYY-MM-DD HH:mm"
3. 设置变量: 标题 = "语音笔记 - {日期}"
4. 调用 API
5. 显示通知
```

#### 分享扩展
```
1. 接收输入（从分享菜单）
2. 获取分享的 URL 或文本
3. 询问笔记标题
4. 调用 API 保存
5. 显示通知
```

#### 定时笔记
```
1. 设置自动化: 每天晚上 10 点
2. 询问今日总结
3. 调用 API 保存
4. 发送完成通知
```

### 示例 Web API（完整版）

项目包含完整的 `ios_api.py` 文件，提供：

```python
# 主要端点
GET  /           # 健康检查
POST /api/note   # 创建笔记
POST /api/upload # 上传文件

# 使用示例
curl -X POST https://your-domain.com/api/note \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{"title": "测试", "content": "内容"}'
```

### 故障排除

**问题: 快捷指令调用失败**
- 检查服务器是否运行
- 验证 URL 和 token 正确
- 查看服务器日志

**问题: 认证错误**
- 确认 API_TOKEN 配置正确
- 检查请求头格式

**问题: HTTPS 证书问题**
- 确认证书有效
- 使用 Let's Encrypt 自动续期

## 常见问题

### Q: 认证在手机上如何完成？

A: 认证需要打开浏览器。在 Termux 中可以使用 `termux-open-url` 打开认证链接。认证完成后，复制回调 URL 中的授权码手动输入。

### Q: 如何从手机相册上传照片？

A: 
- Android (Termux): 使用 `termux-storage-get` 或直接访问 `/sdcard/DCIM/`
- iOS (Pythonista): 使用 `photos` 模块选择照片

### Q: 能否实现自动同步？

A: v1.0 不支持自动同步，但可以使用 cron 定时任务：

```bash
# 编辑 crontab
crontab -e

# 添加定时任务（每天晚上10点上传某目录）
0 22 * * * cd ~/life-log && python cli.py upload ~/notes/*.md --folder /Notes
```

### Q: 电池消耗如何？

A: Life Log 只在执行命令时运行，不会后台运行，因此不会额外消耗电池。

## 实用技巧

### 1. 快速笔记脚本

创建 `quick.sh`：
```bash
#!/bin/bash
cd ~/life-log
python cli.py note create "$1" --content "$2"
```

使用：
```bash
./quick.sh "灵感" "突然想到一个好主意..."
```

### 2. 照片批量上传

```bash
# 上传今天拍的所有照片
find /sdcard/DCIM/Camera -name "IMG_$(date +%Y%m%d)*" -exec python cli.py upload {} --folder /Photos/$(date +%Y-%m) \;
```

### 3. 语音转文字后上传

结合其他应用的语音识别功能，将结果通过文件传给 Life Log：

```bash
# 假设语音识别结果保存在 voice_note.txt
python cli.py note create "语音笔记-$(date +%H:%M)" --file voice_note.txt
```

## 安全建议

1. **保护配置文件**：确保 `config.json` 权限设置为 600
   ```bash
   chmod 600 config.json
   ```

2. **使用环境变量**：在共享设备上，使用环境变量而非配置文件
   ```bash
   export MS_CLIENT_ID="your_id"
   export MS_CLIENT_SECRET="your_secret"
   ```

3. **定期刷新令牌**：令牌会自动刷新，但如果长时间不用，建议重新认证

4. **备份配置**：将配置文件加密备份到安全位置

## 进阶使用

### 创建统一入口脚本

`lifelog.py`:
```python
#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path

# 添加常用操作的快捷方式

def quick_note(title, content=None, file=None):
    # 快速创建笔记
    pass

def quick_upload(*files, folder=None):
    # 快速上传文件
    pass

if __name__ == '__main__':
    # 解析参数并执行
    pass
```

### 集成到其他应用

Life Log 可以作为库导入到其他 Python 脚本中：

```python
from mobile_collector import Config, MicrosoftAuthenticator, OneNoteService

# 在你的应用中使用
config = Config()
auth = MicrosoftAuthenticator(...)
service = OneNoteService(auth)
service.create_page("自动生成的笔记", "内容...")
```

## 下一步

- 查看 [README.md](../README.md) 了解完整功能
- 查看 [examples.py](../examples.py) 学习更多用法
- 查看 [docs/v1.0/](../docs/v1.0/) 了解技术细节
