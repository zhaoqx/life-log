/*
 * 厨房环境监测系统 - 使用现有套件版本（渐进式采购支持）
 * 适用于: Arduino UNO R4 WiFi
 * 
 * 本版本支持渐进式采购，缺少的传感器会标记为"未获取"
 * 
 * 套件中已有的传感器（默认启用）：
 * - DHT11: 温湿度
 * - 声音传感器: 噪音检测
 * - MQ-135: 空气质量（如果你购买了）
 * - MQ-7: 一氧化碳（如果你购买了）
 * 
 * 可选的传感器（逐步添加）：
 * - PMS5003: PM2.5（第2阶段）
 * - HC-SR501: 人体感应（可选）
 * - MQ-4/5/9: 其他燃气传感器（可选）
 * 
 * 依赖库:
 * - Wire (Arduino官方)
 * - WiFiS3 (Arduino官方)
 * - DHT.h (Adafruit的DHT库)
 * - ArduinoGraphics
 * - Arduino_LED_Matrix
 */

#include "ArduinoGraphics.h"
#include "Arduino_LED_Matrix.h"
#include <Wire.h>
#include <WiFiS3.h>
#include <DHT.h>

// ========== WiFi配置 ==========
char ssid[] = "YOUR_WIFI_SSID";           // 修改为你的WiFi名称
char pass[] = "YOUR_WIFI_PASSWORD";        // 修改为你的WiFi密码
String serverHost = "192.168.3.4";        // PC服务器IP地址
int serverPort = 5000;

// ========== 传感器配置 ==========
// DHT11温湿度传感器（套件中已有）
#define DHTPIN 2
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// 引脚定义
#define MQ135_AO_PIN  A0   // MQ-135模拟输出
#define MQ7_AO_PIN    A1   // MQ-7模拟输出
#define SOUND_DO_PIN  5    // 套件中的声音传感器数字输出
#define SOUND_AO_PIN  A2   // 套件中的声音传感器模拟输出（可选）
#define PIR_PIN       6    // HC-SR501人体感应传感器（如果购买）
#define LED_BUILTIN_PIN 13 // 板载LED

// ========== LED矩阵显示 ==========
ArduinoLEDMatrix matrix;

// ========== 全局变量 ==========
unsigned long lastSensorRead = 0;
unsigned long lastSend = 0;
unsigned long lastDisplay = 0;
const unsigned long SENSOR_INTERVAL = 2000;   // 传感器读取间隔(ms)
const unsigned long SEND_INTERVAL = 5000;    // 数据发送间隔(ms)
const unsigned long DISPLAY_INTERVAL = 3000;  // 显示更新间隔(ms)

// 传感器状态标志
struct SensorStatus {
  bool dht11_available = true;   // 套件中必有的DHT11
  bool sound_available = true;   // 套件中必有的声音传感器
  bool mq135_available = false; // 需要确认是否购买
  bool mq7_available = false;   // 需要确认是否购买
  bool pms5003_available = false; // PMS5003（第2阶段）
  bool pir_available = false;   // HC-SR501（可选）
};

SensorStatus sensorStatus;

// 传感器数据
struct SensorData {
  float temperature = -999;    // -999表示未获取
  float humidity = -999;
  float pressure = -999;       // DHT11不支持，固定为-999
  int mq135_value = -999;
  int mq7_value = -999;
  int sound_analog = -999;
  bool sound_detected = false;
  bool motion_detected = false;
  int pm25 = -999;             // PM2.5值（如果购买了PMS5003）
  int pm10 = -999;             // PM10值
  unsigned long timestamp = 0;
};

SensorData currentData;

// ========== 初始化函数 ==========
void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n=================================");
  Serial.println("厨房环境监测系统（套件版-渐进式）启动");
  Serial.println("=================================\n");
  
  // 初始化引脚
  pinMode(SOUND_DO_PIN, INPUT);
  pinMode(PIR_PIN, INPUT);
  pinMode(LED_BUILTIN_PIN, OUTPUT);
  digitalWrite(LED_BUILTIN_PIN, LOW);
  
  // 检测传感器是否连接
  detectSensors();
  
  // 初始化LED矩阵
  matrix.begin();
  displayText("  KIT   ", 50);
  delay(1000);
  
  // 显示传感器状态
  printSensorStatus();
  
  // 初始化DHT11（套件中必须有）
  if (sensorStatus.dht11_available) {
    dht.begin();
    Serial.println("✓ DHT11传感器初始化");
  }
  
  // 连接WiFi
  connectToWiFi();
  
  // 等待传感器预热（MQ系列传感器需要预热）
  Serial.println("\n等待传感器预热（30秒）...");
  displayText("WARMING UP ", 50);
  
  for (int i = 0; i < 30; i++) {
    readSensors();
    delay(1000);
    digitalWrite(LED_BUILTIN_PIN, !digitalRead(LED_BUILTIN_PIN));  // LED闪烁
    Serial.print("预热中: ");
    Serial.println(30 - i);
  }
  
  digitalWrite(LED_BUILTIN_PIN, HIGH);  // LED常亮表示就绪
  displayText("READY ", 50);
  
  Serial.println("\n=================================");
  Serial.println("系统初始化完成，开始监测");
  Serial.println("=================================\n");
}

// ========== 主循环 ==========
void loop() {
  unsigned long currentMillis = millis();
  
  // 读取传感器数据（每2秒）
  if (currentMillis - lastSensorRead >= SENSOR_INTERVAL) {
    readSensors();
    lastSensorRead = currentMillis;
  }
  
  // 发送数据到服务器（每5秒）
  if (currentMillis - lastSend >= SEND_INTERVAL) {
    sendDataToServer();
    lastSend = currentMillis;
  }
  
  // 更新LED矩阵显示（每3秒）
  if (currentMillis - lastDisplay >= DISPLAY_INTERVAL) {
    updateDisplay();
    lastDisplay = currentMillis;
  }
  
  // 板载LED状态指示
  if (WiFi.status() == WL_CONNECTED) {
    digitalWrite(LED_BUILTIN_PIN, HIGH);
  } else {
    digitalWrite(LED_BUILTIN_PIN, !digitalRead(LED_BUILTIN_PIN));  // 未连接时闪烁
  }
  
  delay(100);
}

// ========== 检测传感器是否连接 ==========
void detectSensors() {
  Serial.println("\n检测传感器状态...\n");
  
  // DHT11（套件中必有）
  sensorStatus.dht11_available = true;
  Serial.println("✓ DHT11: 可用（套件包含）");
  
  // 声音传感器（套件中必有）
  sensorStatus.sound_available = true;
  Serial.println("✓ 声音传感器: 可用（套件包含）");
  
  // MQ-135（需要确认是否购买）
  // 通过读取一个测试值来判断，如果值在合理范围内就认为已连接
  int testValue = analogRead(MQ135_AO_PIN);
  if (testValue > 50 && testValue < 1000) {
    sensorStatus.mq135_available = true;
    Serial.println("✓ MQ-135 (空气质量): 已连接");
  } else {
    sensorStatus.mq135_available = false;
    Serial.println("✗ MQ-135 (空气质量): 未连接（需购买）");
  }
  
  // MQ-7（需要确认是否购买）
  testValue = analogRead(MQ7_AO_PIN);
  if (testValue > 50 && testValue < 1000) {
    sensorStatus.mq7_available = true;
    Serial.println("✓ MQ-7 (一氧化碳): 已连接");
  } else {
    sensorStatus.mq7_available = false;
    Serial.println("✗ MQ-7 (一氧化碳): 未连接（需购买）");
  }
  
  // PMS5003（第2阶段）
  sensorStatus.pms5003_available = false;
  Serial.println("✗ PMS5003 (PM2.5): 未连接（第2阶段采购）");
  
  // HC-SR501（可选）
  sensorStatus.pir_available = false;
  Serial.println("✗ HC-SR501 (人体感应): 未连接（可选）");
  
  Serial.println();
}

// ========== 显示传感器状态 ==========
void printSensorStatus() {
  Serial.println("\n传感器状态汇总：");
  Serial.println("┌─────────────────────┬──────────┐");
  Serial.println("│ 传感器              │ 状态     │");
  Serial.println("├─────────────────────┼──────────┤");
  Serial.printf("│ DHT11 (温湿度)      │ %s │\n", 
    sensorStatus.dht11_available ? "  可用 ✓  " : " 不可用 ✗  ");
  Serial.printf("│ 声音传感器          │ %s │\n",
    sensorStatus.sound_available ? "  可用 ✓  " : " 不可用 ✗  ");
  Serial.printf("│ MQ-135 (空气质量)   │ %s │\n",
    sensorStatus.mq135_available ? "  可用 ✓  " : " 未安装 ✗  ");
  Serial.printf("│ MQ-7 (一氧化碳)     │ %s │\n",
    sensorStatus.mq7_available ? "  可用 ✓  " : " 未安装 ✗  ");
  Serial.printf("│ PMS5003 (PM2.5)     │ %s │\n",
    sensorStatus.pms5003_available ? "  可用 ✓  " : " 第2阶段 ");
  Serial.printf("│ HC-SR501 (人体感应) │ %s │\n",
    sensorStatus.pir_available ? "  可用 ✓  " : " 可选   ");
  Serial.println("└─────────────────────┴──────────┘\n");
}

// ========== 读取所有传感器数据 ==========
void readSensors() {
  // 读取DHT11温湿度（套件中必有）
  if (sensorStatus.dht11_available) {
    currentData.temperature = dht.readTemperature();
    currentData.humidity = dht.readHumidity();
  } else {
    currentData.temperature = -999;
    currentData.humidity = -999;
  }
  
  // DHT11不提供气压数据
  currentData.pressure = -999;
  
  // 读取MQ-135（CO2等气体）
  if (sensorStatus.mq135_available) {
    currentData.mq135_value = analogRead(MQ135_AO_PIN);
  } else {
    currentData.mq135_value = -999;
  }
  
  // 读取MQ-7（一氧化碳）
  if (sensorStatus.mq7_available) {
    currentData.mq7_value = analogRead(MQ7_AO_PIN);
  } else {
    currentData.mq7_value = -999;
  }
  
  // 读取套件中的声音传感器
  if (sensorStatus.sound_available) {
    currentData.sound_analog = analogRead(SOUND_AO_PIN);
    currentData.sound_detected = (digitalRead(SOUND_DO_PIN) == HIGH);
  } else {
    currentData.sound_analog = -999;
    currentData.sound_detected = false;
  }
  
  // PMS5003（如果购买）
  if (sensorStatus.pms5003_available) {
    // TODO: 读取PMS5003的串口数据
    // currentData.pm25 = readPMS5003();
  } else {
    currentData.pm25 = -999;
    currentData.pm10 = -999;
  }
  
  // 读取人体感应传感器（如果购买了HC-SR501）
  if (sensorStatus.pir_available) {
    currentData.motion_detected = (digitalRead(PIR_PIN) == HIGH);
  } else {
    currentData.motion_detected = false;
  }
  
  // 更新时间戳
  currentData.timestamp = millis();
  
  // 打印到串口
  printSensorData();
}

// ========== 打印传感器数据 ==========
void printSensorData() {
  Serial.println("----------------");
  
  // 温度
  if (currentData.temperature > -900) {
    Serial.print("温度(DHT11): ");
    Serial.print(currentData.temperature);
    Serial.println("°C");
  } else {
    Serial.println("温度: 未获取");
  }
  
  // 湿度
  if (currentData.humidity > -900) {
    Serial.print("湿度: ");
    Serial.print(currentData.humidity);
    Serial.println("%");
  } else {
    Serial.println("湿度: 未获取");
  }
  
  // 气压（DHT11不支持）
  Serial.println("气压: N/A (DHT11不支持)");
  
  // MQ-135
  if (currentData.mq135_value > -900) {
    Serial.print("MQ135(CO2): ");
    Serial.println(currentData.mq135_value);
  } else {
    Serial.println("MQ135(空气质量): 未获取（需购买传感器）");
  }
  
  // MQ-7
  if (currentData.mq7_value > -900) {
    Serial.print("MQ7(CO): ");
    Serial.println(currentData.mq7_value);
  } else {
    Serial.println("MQ7(一氧化碳): 未获取（需购买传感器）");
  }
  
  // PM2.5
  if (currentData.pm25 > -900) {
    Serial.print("PM2.5: ");
    Serial.println(currentData.pm25);
  } else {
    Serial.println("PM2.5: 未获取（第2阶段采购PMS5003）");
  }
  
  // 声音
  if (currentData.sound_analog > -900) {
    Serial.print("声音模拟: ");
    Serial.print(currentData.sound_analog);
    Serial.print("  声音数字: ");
    Serial.println(currentData.sound_detected ? "检测到" : "无");
  } else {
    Serial.println("声音: 未获取");
  }
  
  // 人体感应
  Serial.print("人体感应: ");
  Serial.println(currentData.motion_detected ? "有活动" : "无活动");
}

// ========== 连接WiFi ==========
void connectToWiFi() {
  displayText(" WiFi... ", 50);
  
  Serial.print("正在连接WiFi: ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, pass);
  
  unsigned long startTime = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - startTime < 15000) {
    delay(500);
    Serial.print(".");
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✓ WiFi连接成功！");
    Serial.print("IP地址: ");
    Serial.println(WiFi.localIP());
    Serial.print("服务器地址: http://");
    Serial.print(serverHost);
    Serial.print(":");
    Serial.println(serverPort);
    displayText(" WiFi OK ", 50);
    delay(1000);
  } else {
    Serial.println("\n✗ WiFi连接失败！");
    displayText(" WiFi ERR ", 50);
  }
}

// ========== 发送数据到服务器 ==========
void sendDataToServer() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi未连接，无法发送数据");
    displayText(" NO WIFI ", 50);
    return;
  }
  
  // 创建WiFi客户端
  WiFiClient client;
  
  Serial.println("\n发送数据到服务器...");
  
  if (client.connect(serverHost.c_str(), serverPort)) {
    Serial.println("✓ 服务器连接成功");
    
    // 构建JSON数据（支持未获取的数据）
    String jsonData = "{";
    
    // 温度
    if (currentData.temperature > -900) {
      jsonData += "\"temperature\":" + String(currentData.temperature, 2) + ",";
    } else {
      jsonData += "\"temperature\":null,";  // null表示未获取
    }
    
    // 湿度
    if (currentData.humidity > -900) {
      jsonData += "\"humidity\":" + String(currentData.humidity, 2) + ",";
    } else {
      jsonData += "\"humidity\":null,";
    }
    
    // 气压（DHT11不支持）
    jsonData += "\"pressure\":null,";
    
    // MQ-135
    if (currentData.mq135_value > -900) {
      jsonData += "\"mq135_value\":" + String(currentData.mq135_value) + ",";
    } else {
      jsonData += "\"mq135_value\":null,";
    }
    
    // MQ-7
    if (currentData.mq7_value > -900) {
      jsonData += "\"mq7_value\":" + String(currentData.mq7_value) + ",";
    } else {
      jsonData += "\"mq7_value\":null,";
    }
    
    // PM2.5
    if (currentData.pm25 > -900) {
      jsonData += "\"pm25\":" + String(currentData.pm25) + ",";
      jsonData += "\"pm10\":" + String(currentData.pm10) + ",";
    } else {
      jsonData += "\"pm25\":null,";
      jsonData += "\"pm10\":null,";
    }
    
    // 声音
    if (currentData.sound_analog > -900) {
      jsonData += "\"sound_analog\":" + String(currentData.sound_analog) + ",";
      jsonData += "\"sound_detected\":" + String(currentData.sound_detected ? "true" : "false") + ",";
    } else {
      jsonData += "\"sound_analog\":null,";
      jsonData += "\"sound_detected\":false,";
    }
    
    // 人体感应
    jsonData += "\"motion_detected\":" + String(currentData.motion_detected ? "true" : "false") + ",";
    jsonData += "\"timestamp\":" + String(currentData.timestamp) + ",";
    jsonData += "\"device_id\":\"kitchen_monitor_kit_001\"";
    jsonData += "}";
    
    Serial.println("数据: " + jsonData);
    
    // 发送HTTP POST请求
    client.println("POST /api/sensor-data HTTP/1.1");
    client.println("Host: " + serverHost);
    client.println("Content-Type: application/json");
    client.println("Content-Length: " + String(jsonData.length()));
    client.println("User-Agent: Arduino-Kitchen-Monitor-Kit");
    client.println("Connection: close");
    client.println();
    client.println(jsonData);
    
    // 等待响应
    unsigned long timeout = millis();
    while (client.available() == 0) {
      if (millis() - timeout > 5000) {
        Serial.println("✗ 响应超时");
        client.stop();
        displayText("TIMEOUT ", 50);
        return;
      }
    }
    
    // 读取响应
    while (client.available()) {
      String line = client.readStringUntil('\n');
      Serial.println(line);
    }
    
    Serial.println("✓ 数据发送成功");
    displayText("SEND OK ", 50);
    
    client.stop();
  } else {
    Serial.println("✗ 无法连接到服务器");
    displayText("CONN ERR ", 50);
  }
}

// ========== LED矩阵显示函数 ==========
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

// ========== 更新显示内容 ==========
void updateDisplay() {
  static int displayCounter = 0;
  
  switch (displayCounter % 4) {
    case 0:
      // 显示温度
      {
        char text[20];
        snprintf(text, sizeof(text), "  T:%.1fC  ", currentData.temperature);
        displayText(text, 60);
      }
      break;
      
    case 1:
      // 显示湿度
      {
        char text[20];
        snprintf(text, sizeof(text), "  H:%.1f%%  ", currentData.humidity);
        displayText(text, 60);
      }
      break;
      
    case 2:
      // 显示MQ-135
      {
        char text[20];
        snprintf(text, sizeof(text), "  GAS:%d  ", currentData.mq135_value / 10);
        displayText(text, 60);
      }
      break;
      
    case 3:
      // 显示状态
      {
        if (currentData.sound_detected) {
          displayText("  SOUND!  ", 40);
        } else if (currentData.motion_detected) {
          displayText("  MOTION  ", 40);
        } else {
          displayText("  READY  ", 60);
        }
      }
      break;
  }
  
  displayCounter++;
}

