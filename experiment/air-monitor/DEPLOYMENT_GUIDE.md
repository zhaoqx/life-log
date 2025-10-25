# DHT11温湿度监控系统 - 完整部署指南

## 🎯 系统架构

```
Arduino UNO R4 WiFi (数据采集) 
    ↓ WiFi
PC Python Web服务器 (数据处理)
    ↓ HTTP
手机/PC浏览器 (数据展示)
```

## 📋 部署步骤

### 第一步：准备Python环境

1. **安装Python 3.8+**
   ```bash
   # Windows
   # 从官网下载安装: https://www.python.org/downloads/
   
   # 验证安装
   python --version
   pip --version
   ```

2. **安装依赖包**
   ```bash
   pip install flask flask-cors
   ```

### 第二步：配置PC端Web服务器

1. **获取PC的IP地址**
   ```bash
   # Windows
   ipconfig
   
   # 找到你的WiFi适配器IP地址，例如: 192.168.3.100
   ```

2. **修改Arduino代码中的服务器地址**
   ```cpp
   // 在 dht11_data_sender.ino 中修改
   const char* serverURL = "http://192.168.3.100:5000";  // 改为你的PC IP
   ```

3. **启动Python Web服务器**
   ```bash
   cd experiment/air-monitor/src/python
   python sensor_web_server.py
   ```

4. **验证服务器启动**
   - 浏览器访问: `http://localhost:5000`
   - 应该看到Web界面

### 第三步：配置Arduino端

1. **上传Arduino代码**
   - 打开 `dht11_data_sender.ino`
   - 修改WiFi配置和服务器地址
   - 上传到Arduino UNO R4 WiFi

2. **观察串口输出**
   - 应该看到WiFi连接成功
   - 每5秒发送一次数据到PC服务器

### 第四步：测试系统

1. **PC端测试**
   - 浏览器访问: `http://localhost:5000`
   - 应该看到实时更新的温湿度数据

2. **手机端测试**
   - 手机连接同一WiFi
   - 浏览器访问: `http://你的PC_IP:5000`
   - 例如: `http://192.168.3.100:5000`

## 🔧 配置说明

### Arduino配置

```cpp
// WiFi配置
char ssid[] = "你的WiFi名称";
char pass[] = "你的WiFi密码";

// PC服务器配置
const char* serverURL = "http://192.168.3.100:5000";  // 你的PC IP
const char* apiEndpoint = "/api/sensor-data";

// 发送间隔
int sendInterval = 5000; // 每5秒发送一次
```

### Python服务器配置

```python
# 服务器配置
app.run(host='0.0.0.0', port=5000, debug=True)

# 数据存储配置
max_history = 1000  # 内存中最多保存1000条记录
```

## 📊 功能特性

### Arduino端功能
- ✅ **传感器数据采集** - DHT11温湿度读取
- ✅ **WiFi连接** - 自动连接指定WiFi
- ✅ **数据发送** - HTTP POST发送JSON数据
- ✅ **LED矩阵显示** - 实时显示温湿度
- ✅ **错误处理** - 网络异常处理

### Python服务器功能
- ✅ **数据接收** - RESTful API接收Arduino数据
- ✅ **数据存储** - SQLite数据库持久化存储
- ✅ **Web界面** - 现代化响应式Web界面
- ✅ **实时更新** - 每3秒自动刷新数据
- ✅ **历史图表** - Chart.js显示趋势图
- ✅ **统计信息** - 平均值、最大值、最小值
- ✅ **跨域支持** - 支持手机访问

### Web界面功能
- ✅ **实时数据显示** - 当前温湿度
- ✅ **状态监控** - 连接状态、更新时间
- ✅ **历史图表** - 温湿度趋势图
- ✅ **自动刷新** - 可开启/关闭自动更新
- ✅ **响应式设计** - 手机和PC完美适配

## 🌐 API接口

### 1. 接收传感器数据
```http
POST /api/sensor-data
Content-Type: application/json

{
    "temperature": 23.5,
    "humidity": 51.0,
    "timestamp": 1234567890,
    "device_id": "arduino_dht11_001"
}
```

### 2. 获取当前数据
```http
GET /api/current-data

Response:
{
    "temperature": 23.5,
    "humidity": 51.0,
    "timestamp": 1234567890,
    "device_id": "arduino_dht11_001",
    "last_update": "2024-01-01 12:00:00"
}
```

### 3. 获取历史数据
```http
GET /api/history?limit=100

Response:
[
    {
        "temperature": 23.5,
        "humidity": 51.0,
        "timestamp": 1234567890,
        "device_id": "arduino_dht11_001",
        "created_at": "2024-01-01 12:00:00"
    }
]
```

### 4. 获取统计信息
```http
GET /api/stats

Response:
{
    "total_records": 100,
    "avg_temperature": 23.5,
    "avg_humidity": 51.0,
    "min_temperature": 20.0,
    "max_temperature": 25.0,
    "min_humidity": 45.0,
    "max_humidity": 60.0,
    "last_update": "2024-01-01 12:00:00"
}
```

## 🔧 故障排除

### 常见问题

1. **Arduino无法连接WiFi**
   - 检查WiFi名称和密码
   - 确认WiFi是2.4GHz网络
   - 检查信号强度

2. **Arduino无法发送数据到PC**
   - 检查PC的IP地址是否正确
   - 确认PC防火墙允许5000端口
   - 检查Python服务器是否启动

3. **Web界面无法访问**
   - 确认Python服务器正在运行
   - 检查端口5000是否被占用
   - 尝试访问 `http://localhost:5000`

4. **数据不更新**
   - 检查Arduino串口输出
   - 确认Python服务器收到数据
   - 检查浏览器控制台错误

### 调试方法

1. **Arduino调试**
   ```cpp
   Serial.println("调试信息");
   ```

2. **Python服务器调试**
   ```python
   print("调试信息")
   ```

3. **浏览器调试**
   - 按F12打开开发者工具
   - 查看Console和Network标签

## 📱 移动端访问

### 手机访问步骤

1. **确保手机和PC在同一WiFi网络**
2. **获取PC的IP地址**
3. **手机浏览器访问**: `http://PC_IP:5000`
4. **例如**: `http://192.168.3.100:5000`

### 移动端优化

- ✅ **响应式设计** - 自动适配手机屏幕
- ✅ **触摸友好** - 按钮大小适合手指操作
- ✅ **快速加载** - 优化的资源加载
- ✅ **离线提示** - 网络断开时的友好提示

## 🚀 高级功能

### 数据导出

```python
# 导出CSV数据
@app.route('/api/export/csv')
def export_csv():
    # 实现CSV导出功能
    pass
```

### 数据备份

```python
# 定期备份数据库
def backup_database():
    # 实现数据库备份功能
    pass
```

### 多设备支持

```python
# 支持多个Arduino设备
@app.route('/api/devices')
def get_devices():
    # 返回所有连接的设备列表
    pass
```

## 📋 总结

### 优势

1. **真正的实时数据** - Python服务器支持长连接和实时更新
2. **强大的数据处理** - 支持数据存储、统计、图表
3. **跨平台访问** - PC和手机都能完美访问
4. **易于扩展** - 可以轻松添加新功能
5. **稳定可靠** - 不依赖Arduino的Web服务器限制

### 适用场景

- ✅ **家庭环境监控** - 实时监测室内温湿度
- ✅ **实验室数据采集** - 科学实验数据记录
- ✅ **教学演示** - Arduino和Python结合教学
- ✅ **原型开发** - IoT项目原型验证

现在你有了一个完整的、真正实时的温湿度监控系统！🎉
