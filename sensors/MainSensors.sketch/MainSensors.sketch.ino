#include <Arduino.h>
#include <WiFi.h>
#include <ESPmDNS.h>
#include <WiFiUdp.h>
#include <stdarg.h>
#include <stddef.h>
#include <Timer.h>
#include <HardwareSerial.h>
#include <Adafruit_GPS.h>
#include <RTClib.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>
#include <Adafruit_BME280.h>
#include <Adafruit_TSL2561_U.h>
#include <RollingAverage.h>

#define WLAN_SSID       "your_ssid"
#define WLAN_PASS       "your_password"
#define toFeet(m) m * 3.28084
#define BME_SCK 22
#define BME_MISO 12
#define BME_MOSI 23
#define BME_CS 10

#define ctof(c) c * 9.0 / 5.0 + 32.0

// Setup variables
bool otaStarted=false;
Timer wifiTimer;
Timer udpTimer;
Timer bnoTimer;
Timer tslTimer;
Timer bmeTimer;
WiFiClient client;
int LED = 13;
int ppsPin = 27;
HardwareSerial Serial1(2);
Adafruit_GPS GPS(&Serial1);
float gpsAltitude;
float gpsSpeed;
float gpsBearing; // True North
Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x28);
Adafruit_BME280 bme;
Adafruit_TSL2561_Unified tsl = Adafruit_TSL2561_Unified(TSL2561_ADDR_FLOAT, 12345);
RollingAverage temp(5);
RollingAverage pressure(5,true);
RollingAverage humidity(5);
sensors_event_t bnoEulerEvent;
sensors_event_t tslEvent;
uint8_t packetBuffer[1500];
WiFiUDP udp;
bool connected = false;
uint32_t sequenceNo = 0;

// Setup packet struct
struct packetInfoType {
	uint32_t sequenceNo;
	float temperature;
	float pressure;
	float humidity;
	float x;
	float y;
	float z;
    float light;
    double latitude;
    double longitude;
    double gpsAltitude;
    double gpsSpeed;
    double gpsBearing;
    int year;
    int month;
    int day;
    int hour;
    int minute;
    int second;
    unsigned int millisecond;
} packetData;

 void setup() {
	// Initialize
	Serial.begin(115200);
	delay(100);
  	pinMode(LED, OUTPUT);
	digitalWrite(LED, HIGH);
	udpTimer.startTimer();
	bnoTimer.startTimer();
	tslTimer.startTimer();
	bmeTimer.startTimer();
	Serial.println("Starting Wire...");
	Wire.begin(23,22);

	// Setup GPS
	Serial.println("Starting GPS...");
	GPS.begin(9600);
	//GPS.sendCommand(PMTK_SET_BAUD_57600);
	//GPS.begin(57600);
	GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);
	GPS.sendCommand(PMTK_SET_NMEA_UPDATE_10HZ);
	GPS.sendCommand(PMTK_API_SET_FIX_CTL_5HZ);
	GPS.sendCommand(PGCMD_ANTENNA);
	Serial1.println(PMTK_Q_RELEASE); // Request firmware version

	// Setup 9DOF sensor (BNO055)
	Serial.println("Starting BNO55...");
	if(!bno.begin()) {
		// There was a problem detecting the BNO055 ... check your connections
		Serial.print("Ooops, no BNO055 detected ... Check your wiring or I2C ADDR!");
		while(1);
	}
	delay(1000);
	bno.setExtCrystalUse(true);

	// Setup BME280 (weather)
	Serial.println("Starting BME280...");
    if(!bme.begin()) {
      Serial.println("Could not find a valid BME280 sensor, check wiring!");
      while(1);
    }
    bme.setSampling(Adafruit_BME280::MODE_NORMAL,
                    Adafruit_BME280::SAMPLING_X16, // temperature
                    Adafruit_BME280::SAMPLING_X16, // pressure
                    Adafruit_BME280::SAMPLING_X16, // humidity
                    Adafruit_BME280::FILTER_OFF);

    // Setup TSL2561 (lux sensor)
	Serial.println("Starting TSL2561...");
    if(!tsl.begin()) {
      Serial.print("Ooops, no TSL2561 detected ... Check your wiring or I2C ADDR!");
      while(1);
    }
    sensor_t sensor;
    tsl.getSensor(&sensor);
    Serial.println("------------------------------------");
    Serial.print  ("Sensor:       "); Serial.println(sensor.name);
    Serial.print  ("Driver Ver:   "); Serial.println(sensor.version);
    Serial.print  ("Unique ID:    "); Serial.println(sensor.sensor_id);
    Serial.print  ("Max Value:    "); Serial.print(sensor.max_value); Serial.println(" lux");
    Serial.print  ("Min Value:    "); Serial.print(sensor.min_value); Serial.println(" lux");
    Serial.print  ("Resolution:   "); Serial.print(sensor.resolution); Serial.println(" lux");
    Serial.println("------------------------------------");
    Serial.println("");
    // tsl.setGain(TSL2561_GAIN_1X);      // No gain ... use in bright light to avoid sensor saturation
    // tsl.setGain(TSL2561_GAIN_16X);     // 16x gain ... use in low light to boost sensitivity
    tsl.enableAutoRange(true);            // Auto-gain ... switches automatically between 1x and 16x
    // Changing the integration time gives you better sensor resolution (402ms = 16-bit data)
    tsl.setIntegrationTime(TSL2561_INTEGRATIONTIME_13MS);      // fast but low resolution
    // tsl.setIntegrationTime(TSL2561_INTEGRATIONTIME_101MS);  // medium resolution and speed
    // tsl.setIntegrationTime(TSL2561_INTEGRATIONTIME_402MS);  // 16-bit data but slowest conversions

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
		digitalWrite(LED,LOW);
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
	if(connected) digitalWrite(LED,LOW);
	else digitalWrite(LED,HIGH);

	// Update GPS
	char c = GPS.read();
	if (GPS.newNMEAreceived()) {
		if (!GPS.parse(GPS.lastNMEA())) return;
		gpsAltitude = toFeet(GPS.altitude);
		gpsSpeed = GPS.speed;
		gpsBearing = GPS.angle;
	}

	// Read BME280
	if(bmeTimer.getElapsedTime() >= 20) {
	    temp.addValue(ctof(bme.readTemperature()));
	    pressure.addValue(bme.readPressure() * 0.00029529983071445);
	    //Serial.print("pressure: ");
	    //Serial.print(String(pressure.getLatestValue(),5));
	    //Serial.print(", average: ");
	    //Serial.println(String(pressure.getAverage(),5));
	    humidity.addValue(bme.readHumidity());
	    bmeTimer.restartTimer();
	}

	// Read BNO055 sensor
	if(bnoTimer.getElapsedTime() >= 50) {
		bno.getEvent(&bnoEulerEvent);
		bnoTimer.restartTimer();
	}

	// Read TSL2561
	if(tslTimer.getElapsedTime() >= 50) {
		tsl.getEvent(&tslEvent);
		tslTimer.restartTimer();
	}

	// Prepare UDP packet
	if (udpTimer.getElapsedTime() >= 100) {
		// Sequence number
		packetData.sequenceNo = sequenceNo++;

		// BME280
	    Serial.print(temp.getAverage());
	    Serial.print(",");
	    Serial.print(String(pressure.getAverage(),5));
	    Serial.print(",");
	    Serial.print(humidity.getAverage());
	    packetData.temperature = temp.getAverage();
	    packetData.pressure = pressure.getAverage();
	    packetData.humidity = humidity.getAverage();

		// BNO055
		Serial.print(",");
		Serial.print(bnoEulerEvent.acceleration.x, 2);
		Serial.print(",");
		Serial.print(bnoEulerEvent.acceleration.y, 2);
		Serial.print(",");
		Serial.print(bnoEulerEvent.acceleration.z, 2);
		packetData.x = bnoEulerEvent.acceleration.x;
		packetData.y = bnoEulerEvent.acceleration.y;
		packetData.z = bnoEulerEvent.acceleration.z;

		// TSL2561
		Serial.print(",");
		Serial.print(tslEvent.light);
		packetData.light = tslEvent.light;

		// GPS
	    Serial.print(",");
	    Serial.print(String(GPS.latitudeDegrees,6));
	    Serial.print(",");
	    Serial.print(String(GPS.longitudeDegrees,6));
	    Serial.print(",");
	    Serial.print(String(gpsAltitude,1));
	    Serial.print(",");
	    Serial.print(String(gpsSpeed,1));
	    Serial.print(",");
	    Serial.print(String(gpsBearing,1));
	    Serial.print(",");
		Serial.print(GPS.year);
		Serial.print(",");
		Serial.print(GPS.month);
		Serial.print(",");
		Serial.print(GPS.day);
		Serial.print(",");
		Serial.print(GPS.hour);
		Serial.print(",");
		Serial.print(GPS.minute);
		Serial.print(",");
		Serial.print(GPS.seconds);
		Serial.print(",");
		Serial.println(GPS.milliseconds);
		packetData.latitude = GPS.latitudeDegrees;
		packetData.longitude = GPS.longitudeDegrees;
		packetData.gpsAltitude = gpsAltitude;
		packetData.gpsSpeed = gpsSpeed;
		packetData.gpsBearing = gpsBearing;
		packetData.year = GPS.year;
		packetData.month = GPS.month;
		packetData.day = GPS.day;
		packetData.hour = GPS.hour;
		packetData.minute = GPS.minute;
		packetData.second = GPS.seconds;
		packetData.millisecond = GPS.milliseconds;

		// Send packet
		IPAddress remoteAddr;
		remoteAddr.fromString("192.168.46.1");
		digitalWrite(LED,HIGH);
		udp.beginPacket(remoteAddr, 61532);
		udp.write((uint8_t*)&packetData, sizeof(packetData));
		digitalWrite(LED,!connected);
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
