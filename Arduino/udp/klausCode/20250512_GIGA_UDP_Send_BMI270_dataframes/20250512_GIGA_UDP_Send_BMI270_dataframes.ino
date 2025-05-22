/*
WiFi UDP Receive and Send String

 This sketch waits for a UDP packet on localPort using the WiFi module.
 When a packet is received an Acknowledge packet is sent to the client on port remotePort

 Circuit:
 * GIGA R1 WiFi

 created 30 December 2012
 by dlf (Metodo2 srl)

 modified 3 March 2023
 by Karl Söderby

 modified 12 May 2025
 by Klaus Heyer

 */


#include <SPI.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <Wire.h>
#include "SparkFun_BMI270_Arduino_Library.h"

int status = WL_IDLE_STATUS;
// #include "arduino_secrets.h" 
///////please enter your sensitive data in the Secret tab/arduino_secrets.h
char ssid[] = "SDD_Demo";        // your network SSID (name)
char pass[] = "Bobbycar";    // your network password (use for WPA, or use as key for WEP)
int keyIndex = 0;            // your network key index number (needed only for WEP)

unsigned int localPort = 2390;      // local port to listen on

unsigned int remPort = 1884;      // local port to listen on

// Create a new sensor object
BMI270 imu;

// I2C address selection
uint8_t i2cAddress = BMI2_I2C_PRIM_ADDR; // 0x68
//uint8_t i2cAddress = BMI2_I2C_SEC_ADDR; // 0x69

uint8_t acc_odr = BMI2_ACC_ODR_800HZ;
uint8_t gyro_odr = BMI2_GYR_ODR_800HZ;
uint8_t gyr_Range = BMI2_GYR_RANGE_250;

int count;
int idx;



char packetBuffer[256]; //buffer to hold incoming packet
char  ReplyBuffer[] = "acknowledged";       // a string to send back

//char DataSample[80] = "abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz";
//String DataFrame;


WiFiUDP Udp;

void setup() {
  //Initialize serial and wait for port to open:
  Serial.begin(500000);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }

  Serial.println("BMI270 800Hz, UDP data transfer");

   // Initialize the I2C library
    Wire.begin();

    // Check if sensor is connected and initialize
    // Address is optional (defaults to 0x68)
    while(imu.beginI2C(i2cAddress) != BMI2_OK)
    {
        // Not connected, inform user
        Serial.println("Error: BMI270 not connected, check wiring and I2C address!");

        // Wait a bit to see if connection is established
        delay(1000);
    }

    Serial.println("BMI270 connected!");
    
    imu.setAccelODR(acc_odr);
    imu.setGyroODR(gyro_odr);
   // imu.convertRawToDegSecScalar(gyr_Range);

  
    count = 1;
    delay(1000);

  Serial.println("Start WiFi... ");
  // check for the WiFi module:
  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("Communication with WiFi module failed!");
    // don't continue
    while (true);
  }

  // attempt to connect to WiFi network:
  while (status != WL_CONNECTED) {
    Serial.print("Attempting to connect to SSID: ");
    Serial.println(ssid);
    // Connect to WPA/WPA2 network. Change this line if using open or WEP network:
    status = WiFi.begin(ssid, pass);

    // wait 10 seconds for connection:
    delay(8000);
  }
  Serial.println("Connected to WiFi");
  printWifiStatus();

  Serial.println("\nStarting connection to server...");
  // if you get a connection, report back via serial:
  Udp.begin(localPort);
 

}

void loop() {
  idx = 1;
  // if there's data available, read a packet
  int packetSize = Udp.parsePacket();
  if (packetSize) {
    Serial.println("---------------------------------");
    Serial.print("Received packet of size ");
    Serial.println(packetSize);
    Serial.print("From ");
    IPAddress remoteIp = Udp.remoteIP();
    Serial.print(remoteIp);
    Serial.print(", port ");
    Serial.println(Udp.remotePort());

    // read the packet into packetBufffer
    int len = Udp.read(packetBuffer, 255);
    if (len > 0) {
      packetBuffer[len] = 0;
    }
    Serial.println("Contents:");
    Serial.println(packetBuffer);

    // send a reply, to the IP address and port that sent us the packet we received
    delay(1);
    Udp.beginPacket(Udp.remoteIP(), remPort);
    Udp.write(ReplyBuffer);
    Udp.endPacket();
    delay(1);
    long int startTime = millis();
    Serial.println(startTime);
    while (idx <= 10000) {
      //Serial.println(millis());
      
      imu.getSensorData();
      String DataFrame = String(millis(), DEC) + ',' + String(imu.data.accelX, 3) + ',' + String(imu.data.accelY, 3) + ',' + String(imu.data.accelZ, 3) + ',' + String(imu.data.gyroZ, 3);
      int str_len = DataFrame.length() + 1;
      char DataSample[str_len];
      DataFrame.toCharArray(DataSample, str_len);

      Udp.beginPacket(Udp.remoteIP(), remPort);
      Udp.write(DataSample);
      Udp.endPacket();
      delay(1);
      idx = idx + 1;
    }
    long int endTime = millis();
    Serial.println(endTime);
    long int duration = endTime - startTime;
    Serial.println("Duration for " + String(idx -1) + " samples: " + String(duration) + " msec");
  }
}


void printWifiStatus() {
  // print the SSID of the network you're attached to:
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print your board's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  // print the received signal strength:
  long rssi = WiFi.RSSI();
  Serial.print("signal strength (RSSI):");
  Serial.print(rssi);
  Serial.println(" dBm");
}