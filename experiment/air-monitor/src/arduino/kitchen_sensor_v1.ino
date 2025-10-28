// 厨房空气质量监测系统 - 多传感器版本
// 适用于Arduino UNO R4 WiFi
// 传感器：DHT11温湿度 + MQ7一氧化碳 + MQ135空气质量 + 声音传感器

#include "ArduinoGraphics.h"
#include "Arduino_LED_Matrix.h"
#include <DHT.h>
#include <WiFiS3.h>

// DHT11传感器配置
#define DHTPIN 2
#define DHTTYPE DHT11

// 模拟引脚定义
#define MQ7_PIN A0        // MQ7一氧化碳传感器
#define MQ135_PIN A1      // MQ135空气质量传感器
#define SOUND_PIN A2      // 声音传感器

// WiFi配置 - 请修改为你的WiFi信息
char ssid[] = "HUAWEI-400DZ5";        // 你的WiFi名称
char pass[] = "xiaoyezi";              // 你的WiFi密码

// PC端Web服务器配置
String host = "192.168.3.4";          // 你的PC IP地址
int port = 5000;

// 组件初始化
ArduinoLEDMatrix matrix;
DHT dht(DHTPIN, DHTTYPE);

// 全局变量
float currentTemperature = 0.0;
float currentHumidity = 0.0;
float currentCO = 0.0;              // 一氧化碳浓度 (ppm)
float currentAirQuality = 0.0;       // 空气质量指数
float currentSound = 0.0;            // 声音强度

unsigned long lastUpdate = 0;
unsigned long lastSend = 0;
unsigned long lastDisplay = 0;
int sendInterval = 5000;    // 每5秒发送一次数据
int displayInterval = 2000; // LED显示间隔

// 显示模式
int displayMode = 0;  // 0:温度, 1:湿度, 2:一氧化碳, 3:空气质量

// 显示文本函数
void displayText(const char* text, uint8_t speed = 60) {
  matrix.beginDraw();
  matrix.stroke(0xFFFFFFFF);
  matrix.textFont(Font_5x7);
  matrix.textScrollSpeed(speed);
  matrix.beginText(0, 1, 0xFFFFFF);
  matrix.println(text);
  matrix.endText(SCROLL_LEFT);
  matrix.endDraw();
}

void setup() {
  Serial.begin(115200);
  
  // 初始化传感器和LED矩阵
  dht.begin();
  matrix.begin();
  
  // 配置模拟引脚
  pinMode(MQ7_PIN, INPUT);
  pinMode(MQ135_PIN, INPUT);
  pinMode(SOUND_PIN, INPUT);
  
  Serial.println("厨房空气质量监测系统启动");
  Serial.println("传感器配置:");
  Serial.println("  - DHT11: 温湿度传感器");
  Serial.println("  - MQ7: 一氧化碳传感器");
  Serial.println("  - MQ135: 空气质量传感器");
  Serial.println("  - 声音传感器");
  
  displayText("  STARTING  ", 50);
  delay(1000);
  
  // 连接WiFi
  connectToWiFi();
  
  displayText("  SENSOR OK  ", 50);
  delay(1000);
  
  Serial.println("系统启动完成，开始监测...");
}

void connectToWiFi() {
  Serial.print("正在连接WiFi: ");
  Serial.println(ssid);
  displayText("  WiFi...  ", 50);
  
  WiFi.begin(ssid, pass);
  
  unsigned long startTime = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - startTime < 15000) {
    delay(500);
    Serial.print(".");
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.println("WiFi连接成功！");
    Serial.print("IP地址: ");
    Serial.println(WiFi.localIP());
    Serial.print("PC服务器地址: http://");
    Serial.print(host);
    Serial.print(":");
    Serial.println(port);
    displayText("  WiFi OK  ", 50);
    delay(2000);
  } else {
    Serial.println();
    Serial.println("WiFi连接失败！");
    displayText("  WiFi ERR ", 50);
  }
}

void readSensors() {
  // 读取DHT11温湿度
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  
  if (!isnan(temperature) && !isnan(humidity)) {
    currentTemperature = temperature;
    currentHumidity = humidity;
  } else {
    Serial.println("DHT11读取失败！");
  }
  
  // 读取MQ7一氧化碳传感器
  // MQ7需要预热，输出值需要校准
  int mq7Raw = analogRead(MQ7_PIN);
  // 将0-1023映射到0-1000 ppm (需要实际校准)
  currentCO = map(mq7Raw, 0, 1023, 0, 1000);
  
  // 读取MQ135空气质量传感器
  int mq135Raw = analogRead(MQ135_PIN);
  // 将0-1023映射到0-500 空气质量指数 (需要实际校准)
  currentAirQuality = map(mq135Raw, 0, 1023, 0, 500);
  
  // 读取声音传感器
  int soundRaw = analogRead(SOUND_PIN);
  // 将0-1023映射到0-100 (声音强度百分比)
  currentSound = map(soundRaw, 0, 1023, 0, 100);
  
  Serial.println("--- 传感器数据 ---");
  Serial.print("温度: "); Serial.print(currentTemperature); Serial.println("°C");
  Serial.print("湿度: "); Serial.print(currentHumidity); Serial.println("%");
  Serial.print("一氧化碳: "); Serial.print(currentCO); Serial.println(" ppm");
  Serial.print("空气质量: "); Serial.print(currentAirQuality); Serial.println(" AQI");
  Serial.print("声音强度: "); Serial.print(currentSound); Serial.println(" %");
  Serial.println("----------------");
}

void sendDataToServer() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi未连接，无法发送数据");
    return;
  }
  
  // 创建WiFi客户端
  WiFiClient client;
  
  Serial.println("连接到服务器: " + host + ":" + String(port));
  
  // 连接到服务器
  if (client.connect(host.c_str(), port)) {
    Serial.println("服务器连接成功");
    
    // 构建JSON数据
    String jsonData = "{";
    jsonData += "\"temperature\":" + String(currentTemperature, 1) + ",";
    jsonData += "\"humidity\":" + String(currentHumidity, 1) + ",";
    jsonData += "\"co\":" + String(currentCO, 0) + ",";
    jsonData += "\"air_quality\":" + String(currentAirQuality, 0) + ",";
    jsonData += "\"sound\":" + String(currentSound, 0) + ",";
    jsonData += "\"timestamp\":" + String(millis()) + ",";
    jsonData += "\"device_id\":\"kitchen_sensor_001\"";
    jsonData += "}";
    
    Serial.println("发送数据: " + jsonData);
    
    // 发送HTTP POST请求
    client.println("POST /api/sensor-data HTTP/1.1");
    client.println("Host: " + host);
    client.println("Content-Type: application/json");
    client.println("Content-Length: " + String(jsonData.length()));
    client.println("User-Agent: Arduino-Multi-Sensor");
    client.println("Connection: close");
    client.println();
    client.println(jsonData);
    
    // 等待响应
    unsigned long timeout = millis();
    while (client.available() == 0) {
      if (millis() - timeout > 5000) {
        Serial.println("响应超时");
        client.stop();
        displayText("  TIMEOUT ", 50);
        return;
      }
    }
    
    // 读取响应
    String response = "";
    while (client.available()) {
      response += client.readString();
    }
    
    Serial.println("服务器响应:");
    Serial.println(response);
    
    // 检查响应状态
    if (response.indexOf("200 OK") > 0) {
      Serial.println("数据发送成功");
      displayText("  SEND OK  ", 50);
    } else {
      Serial.println("数据发送失败");
      displayText("  SEND ERR ", 50);
    }
    
    client.stop();
  } else {
    Serial.println("无法连接到服务器");
    displayText("  CONN ERR ", 50);
  }
}

void updateDisplay() {
  char textBuffer[20];  // 改名避免与函数displayText()冲突
  
  switch(displayMode) {
    case 0:  // 温度
      snprintf(textBuffer, sizeof(textBuffer), "  T:%.1fC  ", currentTemperature);
      displayText(textBuffer, 60);
      break;
      
    case 1:  // 湿度
      snprintf(textBuffer, sizeof(textBuffer), "  H:%.1f%%  ", currentHumidity);
      displayText(textBuffer, 60);
      break;
      
    case 2:  // 一氧化碳
      snprintf(textBuffer, sizeof(textBuffer), "  CO:%03.0f  ", currentCO);
      displayText(textBuffer, 60);
      break;
      
    case 3:  // 空气质量
      snprintf(textBuffer, sizeof(textBuffer), "  AQ:%03.0f  ", currentAirQuality);
      displayText(textBuffer, 60);
      break;
  }
  
  displayMode = (displayMode + 1) % 4;  // 循环显示0-3
}

void loop() {
  // 更新传感器数据
  if (millis() - lastUpdate > 2000) { // 每2秒更新一次传感器数据
    readSensors();
    lastUpdate = millis();
  }
  
  // 发送数据到服务器
  if (millis() - lastSend > sendInterval) { // 每5秒发送一次数据
    sendDataToServer();
    lastSend = millis();
  }
  
  // LED矩阵显示
  if (millis() - lastDisplay > displayInterval) { // 每2秒切换显示
    updateDisplay();
    lastDisplay = millis();
  }
  
  delay(100);
}
