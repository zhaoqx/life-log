// DHT11温湿度传感器 + HTTP数据发送器
// 适用于Arduino UNO R4 WiFi
// 功能：读取传感器数据并发送到PC端Web服务器

#include "ArduinoGraphics.h"
#include "Arduino_LED_Matrix.h"
#include <DHT.h>
#include <WiFiS3.h>

// DHT11传感器配置
#define DHTPIN 2
#define DHTTYPE DHT11

// WiFi配置 - 请修改为你的WiFi信息
char ssid[] = "HUAWEI-400DZ5";        // 你的WiFi名称
char pass[] = "xiaoyezi";    // 你的WiFi密码

// PC端Web服务器配置 - 请修改为你的PC IP地址
// 注意：Arduino UNO R4 WiFi不支持HTTPClient库，使用原生WiFiClient

// 组件初始化
ArduinoLEDMatrix matrix;
DHT dht(DHTPIN, DHTTYPE);

// 全局变量
float currentTemperature = 0.0;
float currentHumidity = 0.0;
unsigned long lastUpdate = 0;
unsigned long lastSend = 0;
int sendInterval = 5000; // 每5秒发送一次数据

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
  
  Serial.println("DHT11 数据发送器启动");
  displayText("  STARTING  ", 50);
  
  // 连接WiFi
  connectToWiFi();
  
  displayText("  SENDER OK ", 50);
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
    Serial.println("PC服务器地址: http://192.168.3.4:5000");
    displayText("  WiFi OK  ", 50);
    delay(2000);
  } else {
    Serial.println();
    Serial.println("WiFi连接失败！");
    displayText("  WiFi ERR ", 50);
  }
}

void updateSensorData() {
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  
  if (!isnan(temperature) && !isnan(humidity)) {
    currentTemperature = temperature;
    currentHumidity = humidity;
    lastUpdate = millis();
    
    Serial.print("温度: ");
    Serial.print(temperature);
    Serial.print("°C, 湿度: ");
    Serial.print(humidity);
    Serial.println("%");
  }
}

void sendDataToServer() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi未连接，无法发送数据");
    return;
  }
  
  // 创建WiFi客户端
  WiFiClient client;
  
  // 解析服务器URL
  String host = "192.168.3.4";  // 你的PC IP地址
  int port = 5000;
  
  Serial.println("连接到服务器: " + host + ":" + String(port));
  
  // 连接到服务器
  if (client.connect(host.c_str(), port)) {
    Serial.println("服务器连接成功");
    
    // 构建JSON数据
    String jsonData = "{";
    jsonData += "\"temperature\":" + String(currentTemperature, 1) + ",";
    jsonData += "\"humidity\":" + String(currentHumidity, 1) + ",";
    jsonData += "\"timestamp\":" + String(millis()) + ",";
    jsonData += "\"device_id\":\"arduino_dht11_001\"";
    jsonData += "}";
    
    Serial.println("发送数据: " + jsonData);
    
    // 发送HTTP POST请求
    client.println("POST /api/sensor-data HTTP/1.1");
    client.println("Host: " + host);
    client.println("Content-Type: application/json");
    client.println("Content-Length: " + String(jsonData.length()));
    client.println("User-Agent: Arduino-DHT11-Sender");
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

void loop() {
  // 更新传感器数据
  if (millis() - lastUpdate > 2000) { // 每2秒更新一次传感器数据
    updateSensorData();
  }
  
  // 发送数据到服务器
  if (millis() - lastSend > sendInterval) { // 每5秒发送一次数据
    sendDataToServer();
    lastSend = millis();
  }
  
  // LED矩阵显示
  static unsigned long lastDisplay = 0;
  if (millis() - lastDisplay > 8000) { // 每8秒更新显示
    char tempText[20];
    snprintf(tempText, sizeof(tempText), "  T:%.1fC  ", currentTemperature);
    displayText(tempText, 60);
    delay(3000);
    
    char humText[20];
    snprintf(humText, sizeof(humText), "  H:%.1f%%  ", currentHumidity);
    displayText(humText, 60);
    
    lastDisplay = millis();
  }
  
  delay(100);
}
