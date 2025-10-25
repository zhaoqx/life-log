# DHT11温湿度监控系统

## 项目概述

本项目是一个成功的Arduino + Python Web服务器实验，实现了DHT11温湿度传感器的实时数据监控。通过Arduino UNO R4 WiFi采集传感器数据，发送到PC端Python Flask Web服务器，提供现代化的Web界面进行实时数据展示和历史趋势分析。

## 🎯 成功方案

**✅ PC端Web服务器模式（推荐）**
- Arduino作为数据采集端，发送数据到PC
- PC运行Python Flask Web服务器
- 手机/PC浏览器访问Web界面查看实时数据
- 支持历史数据存储和图表展示

## 项目结构

```
experiment/air-monitor/
├── docs/                                          # 文档目录
│   ├── arduino/                                   # Arduino相关文档
│   │   ├── check_experiment.md                   # 实验检查清单
│   │   ├── DHT11_EXPERIMENT_GUIDE.md            # DHT11实验完整指南
│   │   ├── DHT11_QUICKSTART.md                  # DHT11快速开始
│   │   └── dht11_experiment.ino                 # 基础LED矩阵显示代码
│   ├── research-厨房空气质量监测与异常告警创意实验方案.md  # 实验方案
│   ├── project-plan-厨房空气监测实验计划.csv           # 项目计划
│   ├── materials-checklist-材料准备清单.md            # 材料清单
│   └── README.md                                  # 本文件
├── src/                                           # 源代码目录
│   ├── arduino/                                   # Arduino代码
│   │   └── dht11_data_sender.ino                # 数据发送器（发送到PC）
│   ├── python/                                    # Python Web服务器
│   │   └── sensor_web_server.py                 # Flask Web服务器
│   ├── backend/                                   # 后端服务（旧版本）
│   │   └── app.py                                # Flask应用主文件
│   ├── frontend/                                  # 前端界面（旧版本）
│   │   ├── index.html                            # 主页面
│   │   ├── css/                                  # 样式文件
│   │   ├── js/                                   # JavaScript文件
│   │   └── assets/                               # 静态资源
│   └── simulator/                                 # 模拟器（用于演示）
│       ├── air_quality_simulator.py              # 空气质量数据模拟器
│       └── sensor_simulator.py                   # 传感器数据模拟器
├── demo/                                          # 演示模块
│   ├── principle-animation/                       # 原理动画
│   │   ├── system_architecture.html              # 系统架构动画
│   │   ├── data_flow.html                        # 数据流程动画
│   │   └── README.md                             # 动画说明
│   └── monitoring-results/                        # 监测结果演示
│       ├── dashboard.html                         # 实时监控面板
│       ├── historical_data.html                  # 历史数据展示
│       └── README.md                              # 演示说明
├── data/                                          # 数据目录
│   ├── sample_data.csv                            # 示例数据
│   └── sensor_data.db                             # SQLite数据库（运行时生成）
├── DEPLOYMENT_GUIDE.md                            # 完整部署指南
├── requirements.txt                                # Python依赖
└── README.md                                       # 项目说明（本文件）
```

## 快速开始

### 环境要求

- Python 3.8+
- Arduino IDE 2.0+
- Arduino UNO R4 WiFi
- DHT11温湿度传感器
- 现代浏览器（Chrome、Firefox、Edge等）

### 安装步骤

1. **安装Python依赖**
```bash
pip install flask flask-cors
```

2. **启动Python Web服务器**
```bash
cd src/python
python sensor_web_server.py
```

3. **配置Arduino代码**
- 修改 `src/arduino/dht11_data_sender.ino` 中的WiFi配置
- 修改PC服务器IP地址
- 上传到Arduino UNO R4 WiFi

4. **访问Web界面**
- PC浏览器：`http://localhost:5000`
- 手机浏览器：`http://你的PC_IP:5000`

## 系统架构

### 硬件架构
```
Arduino UNO R4 WiFi (数据采集) 
    ↓ WiFi
PC Python Web服务器 (数据处理)
    ↓ HTTP
手机/PC浏览器 (数据展示)
```

### 软件架构
```
┌─────────────────────────────────────────┐
│            前端层（Web界面）              │
│  - HTML/CSS/JavaScript                  │
│  - Chart.js（图表）                     │
│  - 响应式设计                           │
└──────────────┬──────────────────────────┘
               │ HTTP
┌──────────────┴──────────────────────────┐
│            API层（Flask）                │
│  - RESTful API                          │
│  - 数据接收和存储                        │
│  - 跨域支持                              │
└──────────────┬──────────────────────────┘
               │
┌──────────────┴──────────────────────────┐
│          数据存储层（SQLite）            │
│  - 传感器数据存储                        │
│  - 历史数据查询                          │
└──────────────┬──────────────────────────┘
               │
┌──────────────┴──────────────────────────┐
│         Arduino数据采集层                │
│  - DHT11传感器读取                       │
│  - WiFi数据传输                          │
│  - LED矩阵显示                           │
└─────────────────────────────────────────┘
```

## 主要功能

### 1. 实时数据监控
- ✅ Arduino每5秒发送温湿度数据到PC
- ✅ Web界面每3秒自动刷新显示
- ✅ 实时显示当前温度和湿度

### 2. 历史数据存储
- ✅ SQLite数据库持久化存储
- ✅ 支持历史数据查询
- ✅ 数据统计和分析

### 3. 可视化展示
- ✅ Chart.js图表显示温湿度趋势
- ✅ 现代化响应式Web界面
- ✅ 手机和PC完美适配

### 4. 多设备访问
- ✅ PC浏览器访问
- ✅ 手机浏览器访问
- ✅ 支持多用户同时访问

## 技术特点

### Arduino端
- **传感器**：DHT11温湿度传感器
- **通信**：WiFiS3库，原生HTTP客户端
- **显示**：12×8 LED矩阵实时显示
- **稳定性**：错误处理和重连机制

### Python服务器端
- **框架**：Flask + Flask-CORS
- **数据库**：SQLite轻量级存储
- **API**：RESTful接口设计
- **性能**：支持多并发连接

### Web前端
- **技术**：HTML5 + CSS3 + JavaScript
- **图表**：Chart.js数据可视化
- **设计**：现代化响应式界面
- **体验**：自动刷新和手动控制

## 部署指南

详细的部署步骤请参见：[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

### 快速部署

1. **PC端启动服务器**
```bash
cd experiment/air-monitor/src/python
python sensor_web_server.py
```

2. **Arduino端配置**
- WiFi名称和密码
- PC服务器IP地址
- 上传代码到Arduino

3. **访问Web界面**
- 浏览器访问显示的IP地址
- 开始实时监控

## 实验成果

### ✅ 成功解决的问题

1. **Arduino Web服务器限制**
   - ❌ Arduino WiFiS3库不支持长连接
   - ❌ JavaScript执行受限
   - ❌ 无法实现真正的实时数据推送

2. **PC Web服务器优势**
   - ✅ 支持真正的长连接和实时更新
   - ✅ 强大的数据处理和存储能力
   - ✅ 完美的Web界面和用户体验
   - ✅ 支持多设备同时访问

### 📊 性能表现

- **数据更新频率**：每3秒自动刷新
- **数据发送频率**：Arduino每5秒发送一次
- **响应时间**：< 100ms
- **并发支持**：多用户同时访问
- **数据存储**：SQLite数据库，支持长期存储

## 学习价值

### 技术学习
- Arduino传感器编程
- WiFi通信和数据传输
- Python Flask Web开发
- SQLite数据库操作
- 前端JavaScript和Chart.js
- 响应式Web设计

### 项目经验
- 硬件和软件集成
- 实时数据处理
- Web应用开发
- 系统架构设计
- 问题解决和调试

## 扩展可能

### 硬件扩展
- 添加更多传感器（光照、气压等）
- 支持多个Arduino设备
- 添加本地存储和离线功能

### 软件扩展
- 用户认证和权限管理
- 数据导出和分析功能
- 移动端APP开发
- 云端数据同步

### 功能扩展
- 告警和通知系统
- 数据可视化增强
- 历史数据对比分析
- 设备状态监控

## 常见问题

### Q1: Arduino无法连接WiFi？
A: 检查WiFi名称和密码，确保是2.4GHz网络，检查信号强度。

### Q2: PC服务器无法接收数据？
A: 检查防火墙设置，确认5000端口开放，检查IP地址配置。

### Q3: Web界面无法访问？
A: 确认Python服务器正在运行，检查浏览器控制台错误。

### Q4: 数据不更新？
A: 检查Arduino串口输出，确认数据发送状态，检查网络连接。

## 技术栈

### 硬件
- Arduino UNO R4 WiFi
- DHT11温湿度传感器
- 面包板和跳线

### 软件
- **Arduino**: WiFiS3库、DHT库、Arduino_LED_Matrix库
- **Python**: Flask、Flask-CORS、SQLite
- **前端**: HTML5、CSS3、JavaScript、Chart.js

## 项目状态

- ✅ **实验成功** - 系统正常运行
- ✅ **功能完整** - 实时监控、数据存储、Web界面
- ✅ **文档完善** - 详细的部署和使用指南
- ✅ **代码优化** - 清理了无效代码，保留最佳方案

## 总结

这个项目成功解决了Arduino Web服务器的限制问题，通过PC端Python Web服务器实现了真正的实时数据监控。项目展示了硬件和软件集成的完整流程，为IoT项目开发提供了很好的参考。

**关键成功因素**：
1. 选择了正确的技术架构（PC Web服务器）
2. 解决了Arduino HTTPClient库兼容性问题
3. 实现了真正的实时数据更新
4. 提供了现代化的Web界面

这个方案不仅解决了当前问题，还为未来的功能扩展提供了坚实的基础。

---

**最后更新**：2025-10-25  
**版本**：v2.0 - 成功版本  
**状态**：✅ 实验成功
