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

### 安装步骤

1. 从 App Store 安装 Pythonista
2. 在 Pythonista 中：
   - 创建新文件夹 `life-log`
   - 将项目文件复制到该文件夹

3. 安装依赖库（在 Pythonista 控制台）：
```python
import requests
import json
# MSAL 可能需要手动下载
```

### 使用方法

创建快捷脚本 `quick_note.py`：

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

### 设置步骤

1. 在服务器上部署 Life Log
2. 创建简单的 Web API 封装
3. 使用 iOS 快捷指令调用 API

### 示例 Web API（Flask）

```python
from flask import Flask, request
from mobile_collector import Config, MicrosoftAuthenticator, OneNoteService

app = Flask(__name__)

@app.route('/api/note', methods=['POST'])
def create_note():
    data = request.json
    # 创建笔记逻辑
    return {'status': 'success'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

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
