# Arduino UNO R4 WiFi 入门验证清单（LED/温湿度/Wi‑Fi）

本指南带你用 Arduino UNO R4 WiFi 和常见的温湿度传感器完成 3 个快速验证：

- 验证 1：板载 LED 与 12×8 LED 矩阵显示 "OK"。
- 验证 2：连接温湿度传感器（DHT11/22 或 AHT20），在 LED 矩阵滚动显示温度。
- 验证 3：连接 Wi‑Fi，输出 IP 并在矩阵显示网络状态。

适合完全新手，按步骤复制示例草图（sketch）到 Arduino IDE 上传即可。

## 🎯 推荐实验方案

**✅ 成功方案：PC端Web服务器模式**
- Arduino作为数据采集端，发送数据到PC
- PC运行Python Flask Web服务器
- 手机/PC浏览器访问Web界面查看实时数据

## 📚 相关实验文档

- **[DHT11实验完整指南](DHT11_EXPERIMENT_GUIDE.md)** - 详细的DHT11传感器实验步骤和说明
- **[DHT11快速开始](DHT11_QUICKSTART.md)** - 5分钟快速上手指南
- **[DHT11基础实验代码](dht11_experiment.ino)** - 基础LED矩阵显示代码
- **[DHT11数据发送器](../../src/arduino/dht11_data_sender.ino)** - 发送数据到PC服务器
- **[Python Web服务器](../../src/python/sensor_web_server.py)** - PC端Web服务器
- **[完整部署指南](../../DEPLOYMENT_GUIDE.md)** - 系统部署和使用说明

---

## 0. 准备工作

硬件：

- Arduino UNO R4 WiFi（自带 12×8 LED 矩阵）
- 面包板、跳线
- 温湿度传感器（二选一即可）：
	- DHT11 或 DHT22（单总线，3 针或 4 针封装）
	- AHT20（I2C，SDA/SCL）

软件与驱动：

1) 安装 Arduino IDE（≥ 2.x）。
2) 在“开发板管理器”安装 “Arduino UNO R4 Boards” 套件（最新）。
3) 连接数据线，选择正确的“开发板：Arduino UNO R4 WiFi”和对应端口。
4) 在“库管理器”安装以下库：
	 - Arduino_LED_Matrix（官方）
	 - ArduinoGraphics（官方，用于在矩阵打印文字）
	 - DHT 传感器库（若用 DHT11/22）和 Adafruit Unified Sensor（其依赖）
	 - Adafruit AHTX0 与 Adafruit BusIO（若用 AHT20）

小贴士：UNO R4 的 I2C 引脚为 SDA/SCL（丝印），与传统 UNO 的 A4/A5 一致；供电提供 5V 与 3.3V，AHT20 通常推荐 3.3V（查看你手头模块丝印/说明）。

---

## 1) 验证板载 LED 与 LED 矩阵显示 “OK”

你可以先做一个最简单的板载单个 LED 闪烁（LED_BUILTIN，在 UNO 传统为 D13），再在 LED 矩阵滚动显示 “OK”。

### 1.1 板载单 LED 闪烁（Blink）

将以下代码粘贴到新建草图并上传：

```cpp
void setup() {
	pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
	digitalWrite(LED_BUILTIN, HIGH);
	delay(500);
	digitalWrite(LED_BUILTIN, LOW);
	delay(500);
}
```

预期：板载小 LED 每 0.5 秒闪烁一次。

### 1.2 用板载 12×8 LED 矩阵显示 “OK”

此示例使用 ArduinoGraphics 在矩阵上滚动文本。

```cpp
// 注意：要先包含 ArduinoGraphics 再包含 Arduino_LED_Matrix
#include "ArduinoGraphics.h"
#include "Arduino_LED_Matrix.h"

ArduinoLEDMatrix matrix;

void setup() {
	Serial.begin(115200);
	matrix.begin();
}

void loop() {
	matrix.beginDraw();
	matrix.stroke(0xFFFFFFFF);           // 单色矩阵仍需指定颜色
	matrix.textFont(Font_5x7);           // 5x7 字体
	matrix.textScrollSpeed(60);          // 滚动速度（数值越小越快）

	const char text[] = "   OK   ";     // 两侧加空格获得更好的循环视觉
	matrix.beginText(0, 1, 0xFFFFFF);    // x=0, y=1 起始
	matrix.println(text);
	matrix.endText(SCROLL_LEFT);         // 向左滚动
	matrix.endDraw();

	// 注：无需额外 delay，库内部会处理滚动
}
```

预期：矩阵上循环滚动显示 “OK”。

---

## 2) 验证温湿度传感器并在矩阵显示温度

你手上若不确定传感器型号，可看模块丝印：

- DHT11/DHT22：通常 3 线（VCC/GND/DATA）或 4 线（带 NC）。需要单线协议与上拉电阻（很多模块已集成）。
- AHT20：I2C 设备，SDA/SCL + VCC/GND，一般 3.3V 供电（有的模块兼容 3.3–5V）。

下文分别给出两种方案的接线与代码，任选一种完成验证即可。

### 方案 A：DHT11/22（单总线）

接线（示例用 D2 作为数据脚）：

- DHT VCC → UNO 5V（或 3.3V，视模块说明）
- DHT GND → UNO GND
- DHT DATA → UNO D2
- 若是裸芯片或无上拉模块，给 DATA 加 10kΩ 上拉到 VCC（很多成品模块已内置，无需额外上拉）。

安装库：在库管理器安装 “DHT sensor library” 与 “Adafruit Unified Sensor”。

示例草图（滚动显示温度，单位 °C）：

```cpp
#include <DHT.h>
#include "ArduinoGraphics.h"
#include "Arduino_LED_Matrix.h"

#define DHTPIN 2
// 传感器型号按实际修改为 DHT11 或 DHT22
#define DHTTYPE DHT22

DHT dht(DHTPIN, DHTTYPE);
ArduinoLEDMatrix matrix;

void setup() {
	Serial.begin(115200);
	dht.begin();
	matrix.begin();
}

void scrollText(const char* text, uint8_t speed = 60) {
	matrix.beginDraw();
	matrix.stroke(0xFFFFFFFF);
	matrix.textFont(Font_5x7);
	matrix.textScrollSpeed(speed);
	matrix.beginText(0, 1, 0xFFFFFF);
	matrix.println(text);
	matrix.endText(SCROLL_LEFT);
	matrix.endDraw();
}

void loop() {
	float t = dht.readTemperature();      // 摄氏
	float h = dht.readHumidity();

	if (isnan(t) || isnan(h)) {
		Serial.println(F("DHT 读取失败"));
		scrollText("  ERR DHT  ", 50);
	} else {
		char buf[24];
		snprintf(buf, sizeof(buf), "  T:%.1fC  ", t);
		Serial.print("T:"); Serial.print(t);
		Serial.print("C  H:"); Serial.print(h);
		Serial.println("%");
		scrollText(buf, 60);
	}

	delay(2000); // 每 2 秒读取一次
}
```

预期：串口打印温湿度；LED 矩阵滚动显示 “T:xx.xC”。

### 方案 B：AHT20（I2C）

接线（默认 I2C 地址 0x38）：

- AHT20 VCC → UNO 3.3V（或按模块标注，若写明 3.3–5V 则 5V 亦可）
- AHT20 GND → UNO GND
- AHT20 SDA → UNO SDA（丝印 SDA，等同 A4）
- AHT20 SCL → UNO SCL（丝印 SCL，等同 A5）

安装库：在库管理器安装 “Adafruit AHTX0” 与 “Adafruit BusIO”。

示例草图（滚动显示温度，单位 °C）：

```cpp
#include <Adafruit_AHTX0.h>
#include "ArduinoGraphics.h"
#include "Arduino_LED_Matrix.h"

Adafruit_AHTX0 aht;
ArduinoLEDMatrix matrix;

void setup() {
	Serial.begin(115200);
	matrix.begin();

	if (!aht.begin()) {
		Serial.println(F("AHT20 初始化失败，请检查接线与供电"));
	} else {
		Serial.println(F("AHT20 初始化成功"));
	}
}

void scrollText(const char* text, uint8_t speed = 60) {
	matrix.beginDraw();
	matrix.stroke(0xFFFFFFFF);
	matrix.textFont(Font_5x7);
	matrix.textScrollSpeed(speed);
	matrix.beginText(0, 1, 0xFFFFFF);
	matrix.println(text);
	matrix.endText(SCROLL_LEFT);
	matrix.endDraw();
}

void loop() {
	sensors_event_t humidity, temp;
	aht.getEvent(&humidity, &temp);

	if (isnan(temp.temperature) || isnan(humidity.relative_humidity)) {
		Serial.println(F("AHT20 读取失败"));
		scrollText("  ERR AHT20  ", 50);
	} else {
		char buf[24];
		snprintf(buf, sizeof(buf), "  T:%.1fC  ", temp.temperature);
		Serial.print("T:"); Serial.print(temp.temperature);
		Serial.print("C  H:"); Serial.print(humidity.relative_humidity);
		Serial.println("%");
		scrollText(buf, 60);
	}

	delay(2000);
}
```

预期：串口打印温湿度；LED 矩阵滚动显示 “T:xx.xC”。

---

## 3) 验证 Wi‑Fi 功能

UNO R4 WiFi 通过协处理器提供 Wi‑Fi 功能，使用官方 `WiFiS3` 库。以下示例连接指定路由器，成功后在串口打印 IP，并在矩阵显示 “WiFi OK”。

先在代码中填写你家的 Wi‑Fi 名称与密码：

```cpp
#include <WiFiS3.h>
#include "ArduinoGraphics.h"
#include "Arduino_LED_Matrix.h"

// 修改为你的 Wi‑Fi 凭据
char ssid[] = "YOUR_SSID";
char pass[] = "YOUR_PASSWORD";

ArduinoLEDMatrix matrix;

void showText(const char* text) {
	matrix.beginDraw();
	matrix.stroke(0xFFFFFFFF);
	matrix.textFont(Font_5x7);
	matrix.textScrollSpeed(60);
	matrix.beginText(0, 1, 0xFFFFFF);
	matrix.println(text);
	matrix.endText(SCROLL_LEFT);
	matrix.endDraw();
}

void setup() {
	Serial.begin(115200);
	matrix.begin();

	Serial.print("Connecting to ");
	Serial.println(ssid);

	// 尝试连接
	WiFi.begin(ssid, pass);

	// 最长等待 ~15 秒
	unsigned long start = millis();
	while (WiFi.status() != WL_CONNECTED && millis() - start < 15000) {
		delay(500);
		Serial.print(".");
		showText("  WiFi...  ");
	}
	Serial.println();

	if (WiFi.status() == WL_CONNECTED) {
		IPAddress ip = WiFi.localIP();
		Serial.print("WiFi OK, IP: ");
		Serial.println(ip);
		showText("  WiFi OK  ");
	} else {
		Serial.println("WiFi 连接失败");
		showText("  WiFi ERR  ");
	}
}

void loop() {
	// 可在此处补充网络请求、MQTT、HTTP 测试等
}
```

预期：

- 串口监视器显示连接进度，成功后打印本机 IP。
- LED 矩阵滚动显示 “WiFi OK”。若失败则显示 “WiFi ERR”。

---

## 4) 上传与查看日志

1) 在 Arduino IDE：工具 → 选择 “开发板：Arduino UNO R4 WiFi”，选择正确端口。
2) 点击“验证/上传”。
3) 打开“串口监视器”（115200 波特率）查看日志与数值。

---

## 5) 常见问题排查（FAQ）

- 无法编译：
	- 确认已安装 “Arduino UNO R4 Boards” 套件与所需库（Arduino_LED_Matrix、ArduinoGraphics、DHT/Adafruit AHTX0 等）。
	- 代码顶部包含顺序：ArduinoGraphics 要在 Arduino_LED_Matrix 之前包含。
- 端口不可见/上传失败：
	- 更换数据线（确保支持数据传输，而非仅充电），尝试其他 USB 口。
	- Windows 设备管理器查看端口，必要时重插、重启 IDE。
- DHT 读数为 NaN：
	- 检查 DATA 引脚号码、接线牢固、上拉电阻是否就绪（成品模块一般自带）。
	- DHT22 建议使用 5V 供电；避免线过长带来时序问题。
- AHT20 读数失败：
	- 确认 SDA/SCL 接线准确、供电电压与模块要求一致。
	- 多个 I2C 设备时注意地址冲突（AHT20 常见地址 0x38）。
- Wi‑Fi 连接失败：
	- 确认 2.4GHz 网络、SSID/PASS 正确；靠近路由器测试。
	- 路由器若有 MAC 白名单/隔离，请临时关闭。

---

## 6) 进一步扩展

- 将温湿度与气体传感器读数通过 `WiFiS3` + HTTP/MQTT 上传到本仓库实验中的后端或 Arduino IoT Cloud（可参考 `docs/arduino/uno_r4_iot_cloud.ino`）。
- 使用 LED 矩阵的帧图库显示 Wi‑Fi/云/心跳等图标（见 Arduino_LED_Matrix 示例）。
- 在矩阵上做简单的 UI：温度阈值超限显示告警图标等。

---

祝你验证顺利！如需要，我可以把你的传感器具体型号接线图转成更直观的标注图，并把示例拆分成独立 `.ino` 文件放到 `docs/arduino/` 目录，便于直接打开上传。

