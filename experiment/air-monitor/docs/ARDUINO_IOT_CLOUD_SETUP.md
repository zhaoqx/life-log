# 将厨房空气监测接入 Arduino IoT Cloud 指南

本指南说明如何用 Arduino Uno R4 WiFi 将 PM2.5/CO/CO2/温湿度数据发布到 Arduino IoT Cloud，并通过 Webhook 推送到本项目后端 `/api/ingest/iotcloud`。

## 前置条件
- 硬件：Arduino Uno R4 WiFi + 传感器（PMS5003/SDS011, MH-Z19B, MQ-7, BME280/DHT22 等）
- 软件：Arduino IDE 2.x 或 Arduino Cloud Web Editor
- Wi‑Fi SSID/密码
- 运行本项目后端（Flask）供 Webhook 接收

## 步骤概览
1. 在 Arduino IoT Cloud 创建 Thing 和设备，定义下列变量（变量名与类型可参考）：
   - pm25: float
   - co: float
   - co2: float
   - temperature: float
   - humidity: float
   - activity: String（可选）
2. 在 Arduino IDE/Cloud 生成和下载凭据（Secret），编写示例草图（见 `uno_r4_iot_cloud.ino`）。
3. 在 IoT Cloud 中添加一个 Webhook：
   - 触发：变量更新或按固定频率（如每 5–10 秒）
   - 方法：POST
   - URL：`http://<你的后端IP或域名>:5000/api/ingest/iotcloud`
   - Content-Type：application/json
   - Body（JSON 模板）：
     {
       "pm25": "{{pm25}}",
       "co": "{{co}}",
       "co2": "{{co2}}",
       "temperature": "{{temperature}}",
       "humidity": "{{humidity}}",
       "activity": "{{activity}}",
       "timestamp": "{{timestamp}}"
     }
4. 启动后端服务，确认 `/api/ingest/iotcloud` 返回 201 且可在 `/api/history`、`/api/alerts` 中看到数据与告警。

## 后端本地运行
- Windows PowerShell 启动（已安装依赖）后：
  - 默认监听 `http://0.0.0.0:5000`，确保 IoT Cloud 能访问到你的机器（同网或内网穿透）。
  - 开发测试可使用 `ngrok`/`frp` 暴露本地服务，然后在 Webhook URL 中填写公网地址。

## 变量与阈值
- 后端根据 `/api/thresholds` 中的阈值计算 `warning`/`danger`，你可以按需调整后端逻辑。
- 如果你的 PM 模块能提供 `pm10`，可在 Webhook 中额外添加 `pm10` 字段。

## 故障排查
- Webhook 4xx：检查 JSON 字段是否完整（pm25/co/co2/temperature/humidity 必填）。
- 数据延迟或断续：适当放宽上报频率，保证 5V/2A 供电稳定，Wi‑Fi 信号良好。
- 数值异常：校准 MQ‑7/MH-Z19B，保持 PM 传感器进风顺畅并定期清洁。
