# DHT11实验快速开始指南

## 🚀 5分钟快速上手

### 1. 准备材料
- Arduino UNO R4 WiFi
- DHT11传感器
- 面包板 + 跳线
- USB数据线

### 2. 连接硬件
```
Arduino UNO R4 WiFi → DHT11传感器
5V                → VCC (红色)
GND               → GND (黑色)  
D2                → DATA (黄色)
```

### 3. 安装库
在Arduino IDE中安装：
- Arduino_LED_Matrix
- ArduinoGraphics  
- DHT sensor library
- Adafruit Unified Sensor

### 4. 上传代码
1. 打开 `dht11_experiment.ino`
2. 选择开发板：Arduino UNO R4 WiFi
3. 选择端口
4. 点击上传

### 5. 查看结果
- 串口监视器：显示详细温湿度数据
- LED矩阵：滚动显示 "T:25.3C" 和 "H:60.2%"

## ✅ 成功标志
- 串口显示正常温湿度数据
- LED矩阵滚动显示温度湿度
- 数据每6秒更新一次

## ❌ 常见问题
- **编译错误** → 检查库是否安装完整
- **上传失败** → 检查USB线和端口选择
- **显示ERR** → 检查DHT11接线和供电
- **矩阵不亮** → 确认Arduino UNO R4 WiFi型号

## 📞 需要帮助？
查看完整指南：`DHT11_EXPERIMENT_GUIDE.md`
