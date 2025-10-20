/*
  Uno R4 WiFi -> Arduino IoT Cloud 示例
  - 读取传感器（此处用虚拟/占位函数），将数据发布到 Arduino IoT Cloud 变量
  - 建议把真传感器读取替换为你的实际驱动代码
*/

#include <ArduinoIoTCloud.h>
#include <Arduino_ConnectionHandler.h>

// 用 Arduino IoT Cloud 生成的凭据（在 Secrets 里）
const char SSID[]     = SECRET_SSID;
const char PASS[]     = SECRET_OPTIONAL_PASS;
const char DEVICE_LOGIN_NAME[] = SECRET_DEVICE_LOGIN_NAME;

// 云端变量（与 IoT Cloud 上的变量名一致）
float pm25;
float co;
float co2;
float temperature;
float humidity;
String activity; // 可选

// 连接处理
WiFiConnectionHandler ArduinoIoTPreferredConnection(SSID, PASS);

void initProperties() {
  ArduinoCloud.setDeviceProperty("pm25", &pm25);
  ArduinoCloud.setDeviceProperty("co", &co);
  ArduinoCloud.setDeviceProperty("co2", &co2);
  ArduinoCloud.setDeviceProperty("temperature", &temperature);
  ArduinoCloud.setDeviceProperty("humidity", &humidity);
  ArduinoCloud.setDeviceProperty("activity", &activity);
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  initProperties();
  ArduinoCloud.begin(ArduinoIoTPreferredConnection);

  // 可选：设置云端更新间隔
  setDebugMessageLevel(2);
  ArduinoCloud.printDebugInfo();
}

// ===== 传感器读取占位函数（替换为真实读数） =====
float readPM25() { return 35.0; }
float readCO() { return 5.0; }
float readCO2() { return 650.0; }
float readTemperature() { return 25.0; }
float readHumidity() { return 55.0; }
String detectActivity() { return String("idle"); }
// ============================================

unsigned long lastUpdate = 0;
const unsigned long UPDATE_INTERVAL_MS = 5000; // 每 5 秒上报一次

void loop() {
  ArduinoCloud.update();

  unsigned long now = millis();
  if (now - lastUpdate >= UPDATE_INTERVAL_MS) {
    lastUpdate = now;

    // 读取真实传感器值
    pm25 = readPM25();
    co = readCO();
    co2 = readCO2();
    temperature = readTemperature();
    humidity = readHumidity();
    activity = detectActivity();

    // 若使用 Thing API 的按变量变更触发 Webhook，确保值变化或使用定时触发
    Serial.print("Publish -> PM2.5:"); Serial.print(pm25);
    Serial.print(" CO:"); Serial.print(co);
    Serial.print(" CO2:"); Serial.print(co2);
    Serial.print(" T:"); Serial.print(temperature);
    Serial.print(" H:"); Serial.println(humidity);
  }
}
