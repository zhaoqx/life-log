// DHT11温湿度传感器 + LED矩阵显示实验
// 适用于Arduino UNO R4 WiFi
// 作者：life-log项目
// 日期：2024

// 注意：必须先包含ArduinoGraphics，再包含Arduino_LED_Matrix
#include "ArduinoGraphics.h"
#include "Arduino_LED_Matrix.h"
#include <DHT.h>

// DHT11传感器配置
#define DHTPIN 2        // DHT11数据引脚连接到数字引脚2
#define DHTTYPE DHT11   // 传感器类型

// 初始化传感器和LED矩阵
DHT dht(DHTPIN, DHTTYPE);
ArduinoLEDMatrix matrix;

// 显示文本函数
void displayText(const char* text, uint8_t speed = 60) {
  matrix.beginDraw();
  matrix.stroke(0xFFFFFFFF);           // 白色显示
  matrix.textFont(Font_5x7);           // 5x7字体
  matrix.textScrollSpeed(speed);       // 滚动速度
  matrix.beginText(0, 1, 0xFFFFFF);    // 起始位置
  matrix.println(text);
  matrix.endText(SCROLL_LEFT);         // 向左滚动
  matrix.endDraw();
}

void setup() {
  // 初始化串口通信
  Serial.begin(115200);
  Serial.println("DHT11温湿度传感器实验开始");
  
  // 初始化DHT11传感器
  dht.begin();
  
  // 初始化LED矩阵
  matrix.begin();
  
  // 显示启动信息
  displayText("  DHT11 OK  ", 50);
  delay(2000);
  
  Serial.println("系统初始化完成");
}

void loop() {
  // 读取温湿度数据
  float temperature = dht.readTemperature();    // 读取温度(摄氏度)
  float humidity = dht.readHumidity();          // 读取湿度(%)
  
  // 检查数据是否有效
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("DHT11读取失败！");
    displayText("  ERR DHT11  ", 50);
  } else {
    // 在串口打印数据
    Serial.print("温度: ");
    Serial.print(temperature);
    Serial.print("°C, 湿度: ");
    Serial.print(humidity);
    Serial.println("%");
    
    // 在LED矩阵上显示温度
    char tempText[20];
    snprintf(tempText, sizeof(tempText), "  T:%.1fC  ", temperature);
    displayText(tempText, 60);
    
    delay(3000); // 显示温度3秒
    
    // 在LED矩阵上显示湿度
    char humText[20];
    snprintf(humText, sizeof(humText), "  H:%.1f%%  ", humidity);
    displayText(humText, 60);
    
    delay(3000); // 显示湿度3秒
  }
  
  delay(1000); // 每次循环间隔1秒
}

