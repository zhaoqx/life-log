# 项目目录重构说明

## 重构日期
2025-10-28

## 重构目标
解决项目目录结构混乱、重复目录、业务代码散落等问题。

## 主要问题

### 1. 重复目录
- ❌ `experiment/air-monitor` (完整内容)
- ❌ `experiments/experiment/air-monitor` (空目录结构)
- ❌ `mobile_collector/` (完整包)
- ❌ `src/life_log/mobile_collector/` (空的__pycache__)

### 2. 业务代码散落在根目录
- `cli.py` - 命令行接口
- `ios_api.py` - iOS API
- `quick_note.py` - 快速笔记脚本
- `examples.py` - 示例代码
- `generate_gantt.py` - 甘特图工具
- `verify_installation.py` - 安装验证

### 3. 空目录
- `scripts/` - 空目录
- `tools/` - 空目录
- `src/` - 几乎为空

## 重构方案

### 目录结构调整

```
life-log/
├── cli.py                      # 命令行接口（主入口）★ 保留在根目录
├── mobile_collector/            # 主程序包 ★ 保留在根目录
│   ├── __init__.py
│   ├── auth.py
│   ├── config.py
│   ├── onenote_service.py
│   └── onedrive_service.py
├── scripts/                     # 脚本目录 ✨ 新建
│   ├── ios_api.py              # iOS API服务
│   └── quick_note.py           # 快速笔记脚本
├── tools/                       # 工具脚本 ✨ 新建
│   ├── examples.py             # 使用示例
│   ├── generate_gantt.py       # 甘特图生成工具
│   └── verify_installation.py  # 安装验证
├── docs/                        # 文档目录
├── experiment/                  # 实验项目
│   └── air-monitor/            # 厨房空气监测
├── config.example.json         # 配置模板
├── requirements.txt             # 依赖列表
└── README.md                   # 项目说明
```

### 变更内容

#### 删除的目录/文件
1. ❌ `experiments/` - 重复的空目录结构
2. ❌ `src/` - 几乎为空，移除
3. ❌ `sync_git.ps1` - 临时脚本
4. ❌ `test_suite.sh` - 临时脚本

#### 移动的文件
1. ✨ `ios_api.py` → `scripts/ios_api.py`
2. ✨ `quick_note.py` → `scripts/quick_note.py`
3. ✨ `examples.py` → `tools/examples.py`
4. ✨ `generate_gantt.py` → `tools/generate_gantt.py`
5. ✨ `verify_installation.py` → `tools/verify_installation.py`

#### 保留的文件
1. ✅ `cli.py` - 保留在根目录作为主入口
2. ✅ `mobile_collector/` - 保留在根目录作为Python包
3. ✅ 所有配置文件、README等

### 更新的文件

#### README.md
- 更新项目结构说明
- 更新命令行使用方式：`python -m cli` 代替 `python cli.py`
- 更新iOS使用脚本路径

#### scripts/ios_api.py
- 更新Python路径导入：`os.path.dirname(os.path.dirname(...))`

#### scripts/quick_note.py
- 更新Python路径导入：`os.path.dirname(os.path.dirname(...))`

## 新的使用方式

### 命令行使用
```bash
# 认证
python -m cli auth

# 创建笔记
python -m cli note create "标题" --content "内容"

# 上传文件
python -m cli upload photo.jpg

# 查看配置
python -m cli config show
```

### iOS脚本使用
```bash
# 快速笔记
python scripts/quick_note.py "标题" "内容"

# iOS API服务
python scripts/ios_api.py
```

### 工具脚本使用
```bash
# 安装验证
python tools/verify_installation.py

# 使用示例
python tools/examples.py

# 生成甘特图
python tools/generate_gantt.py
```

## 重构优势

### 1. 结构清晰
- ✅ 根目录只保留核心入口文件
- ✅ 业务代码分类存放（scripts/、tools/）
- ✅ 消除了重复和空目录

### 2. 易于维护
- ✅ 文件分类明确，易于查找
- ✅ 减少了根目录文件数量
- ✅ 遵循Python项目最佳实践

### 3. 向后兼容
- ✅ `cli.py` 仍可通过 `python -m cli` 调用
- ✅ 模块导入路径已更新
- ✅ 配置文件位置不变

## 待处理事项

1. ⚠️ 如有其他脚本依赖路径，需要更新
2. ⚠️ 更新部署文档（如有）
3. ⚠️ 提交重构到git

## 重构验证清单

- [x] 删除重复目录
- [x] 移动文件到合适位置
- [x] 更新文件内的路径引用
- [x] 更新README.md
- [x] 验证新结构
- [ ] 提交到git (需要用户确认)

