#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266mDNS.h>
#include <WiFiUdp.h>
#include <stdarg.h>
#include <stddef.h>
#include <Timer.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <RollingAverage.h>
#include <SPI.h>
#include <Adafruit_BMP3XX.h>
#include <OneWire.h>
#include <DallasTemperature.h>

#define WLAN_SSID       "your_ssid"
#define WLAN_PASS       "your_password"
#define toFeet(m) m * 3.28084
#define BMP_SCK 14
#define BMP_MISO 12
#define BMP_MOSI 13
#define BMP_CS1 15
#define BMP_CS2 4
#define ONE_WIRE_BUS 5 // OAT sensor pin

#define ctof(c) c * 9.0 / 5.0 + 32.0

// Setup variables
bool otaStarted=false;
Timer wifiTimer;
Timer udpTimer;
Timer bmpTimer;
Timer oatTimer;
WiFiClient client;
int LED = 0;
Adafruit_BMP3XX bmp1(BMP_CS1, BMP_MOSI, BMP_MISO,  BMP_SCK);
Adafruit_BMP3XX bmp2(BMP_CS2, BMP_MOSI, BMP_MISO,  BMP_SCK);
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature oatsensor(&oneWire);
double oat;
RollingAverage temp1(5);
RollingAverage pressure1(5,true);
RollingAverage temp2(5);
RollingAverage pressure2(5,true);
uint8_t packetBuffer[1500];
WiFiUDP udp;
bool connected = false;
uint32_t sequenceNo = 0;

// Setup packet struct
struct packetInfoType {
	uint32_t sequenceNo;
	float oat;
	float temperature1;
	float pressure1;
	float temperature2;
	float pressure2;
} packetData;

 void setup() {
	// Initialize
	Serial.begin(115200);
	delay(100);
  	pinMode(LED, OUTPUT);
	digitalWrite(LED, LOW);
	udpTimer.startTimer();
	bmpTimer.startTimer();
	Serial.println("Starting Wire...");
	Wire.begin(23,22);

	// Setup barometric sensors
	if (!bmp1.begin()) {
		Serial.println("Could not find a valid BMP3 sensor on CS1, check wiring!");
		while (1);
	}

	if (!bmp2.begin()) {
		Serial.println("Could not find a valid BMP3 sensor on CS2, check wiring!");
		while (1);
	}
	bmp1.setTemperatureOversampling(BMP3_OVERSAMPLING_8X);
	bmp1.setPressureOversampling(BMP3_OVERSAMPLING_4X);
	bmp1.setIIRFilterCoeff(BMP3_IIR_FILTER_COEFF_3);
	bmp2.setTemperatureOversampling(BMP3_OVERSAMPLING_8X);
	bmp2.setPressureOversampling(BMP3_OVERSAMPLING_4X);
	bmp2.setIIRFilterCoeff(BMP3_IIR_FILTER_COEFF_3);
	bmp1.setOutputDataRate(BMP3_ODR_50_HZ);
	bmp2.setOutputDataRate(BMP3_ODR_50_HZ);

	// OAT Sensor (DS18S20)
	oatsensor.begin();
	oatsensor.setWaitForConversion(false);
	oatsensor.requestTemperatures();
	oatTimer.startTimer();
	Serial.print("Found ");
	Serial.print(oatsensor.getDeviceCount());
	Serial.println(" DS18S20 devices.");

	// Connect to Wifi
	Serial.print("\nConnecting to ");
	Serial.println(WLAN_SSID);
	WiFi.persistent(false);
	WiFi.mode(WIFI_STA);
	WiFi.begin(WLAN_SSID, WLAN_PASS);
	wifiTimer.startTimer();
	int retry = 20; // Retry 20 seconds
	while (WiFi.status() != WL_CONNECTED) {
		delay(1000);
		Serial.println(retry);
		if(!retry--) break; // Try to connect later
	}
	if(WiFi.status() == WL_CONNECTED) {
		Serial.println();
		Serial.println("WiFi connected");
		Serial.print("IP address: ");
		Serial.println(WiFi.localIP());
		connected = true;
		digitalWrite(LED,HIGH);
	}
	wifiTimer.startTimer();
}

void loop() {
	// Make sure we're still connected
	if(WiFi.status() == WL_CONNECTED) {
		if(connected == false) {
			Serial.print("Connected to ");
			Serial.print(WLAN_SSID);
			Serial.println(".");
		}
		connected = true;
		wifiTimer.resetTimer();
	} else {
		if(connected == true) {
			Serial.println("WiFi disconnected.");
		}
		connected = false;
	}
	if(WiFi.status() != WL_CONNECTED && !wifiTimer.isTimerRunning()) wifiTimer.restartTimer();
	if(WiFi.status() != WL_CONNECTED && wifiTimer.getElapsedTime() > 20000) {
		Serial.print("Connecting to ");
		Serial.print(WLAN_SSID);
		Serial.println("...");
		WiFi.disconnect();
		WiFi.begin(WLAN_SSID, WLAN_PASS);
		wifiTimer.restartTimer();
	}
	if(connected) digitalWrite(LED,HIGH);
	else digitalWrite(LED,LOW);

	// Read BMP388
	if(bmpTimer.getElapsedTime() >= 50) {
	    	temp1.addValue(ctof(bmp1.readTemperature()));
	    	pressure1.addValue(bmp1.readPressure() * 0.00029529983071445);
	    	temp2.addValue(ctof(bmp2.readTemperature()));
	    	pressure2.addValue(bmp2.readPressure() * 0.00029529983071445);
	    	bmpTimer.restartTimer();
	}

	// Read OAT (DS18S20)
	if(oatTimer.getElapsedTime() > 750) {
		oat = oatsensor.getTempFByIndex(0);
		oatsensor.requestTemperatures();
		oatTimer.restartTimer();
	}

	// Prepare UDP packet
	if (udpTimer.getElapsedTime() >= 100) {
		// Sequence number
		packetData.sequenceNo = sequenceNo++;

		// OAT sensor
		Serial.print(oat);
		Serial.print(",");
	   	packetData.oat = oat;

		// BMP388
	    	Serial.print(temp1.getAverage());
	    	Serial.print(",");
	    	Serial.print(String(pressure1.getAverage(),5));
	    	Serial.print(",");
	    	Serial.print(temp2.getAverage());
	    	Serial.print(",");
	    	Serial.println(String(pressure2.getAverage(),5));
	    	packetData.temperature1 = temp1.getAverage();
	    	packetData.pressure1 = pressure1.getAverage();
	    	packetData.temperature2 = temp2.getAverage();
	    	packetData.pressure2 = pressure2.getAverage();

		// Send packet
		IPAddress remoteAddr;
		remoteAddr.fromString("192.168.46.1");
		digitalWrite(LED,LOW);
		udp.beginPacket(remoteAddr, 61533);
		udp.write((uint8_t*)&packetData, sizeof(packetData));
		digitalWrite(LED,connected);
		if(udp.endPacket() == 0) Serial.println("Error sending packet");
		// For sending multicast, try updating to the latest version of the ESP32 board code in the boards manager
		//IPAddress ipMulti(224, 224, 4, 46);
		//unsigned int portMulti = 64532;
		//udp.beginPacketMulticast(ipMulti, portMulti, WiFi.localIP());
		//udp.write("UDP Multicast packet sent by ");
		//udp.println(WiFi.localIP());
		//udp.endPacket();
		udpTimer.restartTimer();
	}
}
