#include <ArduinoBLE.h>
#include <Wire.h>
#include "SparkFun_BMI270_Arduino_Library.h"
BLEService sensorService("180C");  // custom service UUID
BLECharacteristic sensorChar("2A56", BLERead | BLENotify, 100);  // characteristic UUID


// Create a new sensor object
BMI270 imu;
// I2C address selection
uint8_t i2cAddress = BMI2_I2C_PRIM_ADDR;  // 0x68
//uint8_t i2cAddress = BMI2_I2C_SEC_ADDR; // 0x69


uint8_t acc_odr = BMI2_ACC_ODR_400HZ;
uint8_t gyro_odr = BMI2_GYR_ODR_400HZ;
uint8_t gyr_Range = BMI2_GYR_RANGE_250;




void setup() {
  Serial.begin(115200);

    Serial.println("BMI270 200Hz Bluethoot ");

  while (!Serial) {
    ;  // wait for serial port to connect. Needed for native USB port only
  }
  Wire1.begin(); 
    // Check if sensor is connected and initialize
  // Address is optional (defaults to 0x68)
  while (imu.beginI2C(i2cAddress, Wire1) != BMI2_OK) {
    // Not connected, inform user
    Serial.println("Error: BMI270 not connected, check wiring and I2C address!");

    // Wait a bit to see if connection is established
    delay(1000);
  }

  Serial.println("BMI270 connected!");

  Serial.print("Attempting to connect through bluethoot to laptop: ");

  // Initialize the I2C library
  imu.setAccelODR(acc_odr);
  imu.setGyroODR(gyro_odr);

  if (!BLE.begin()) {
    Serial.println("BLE init failed!");
    while (1);
  }

  BLE.setLocalName("SensorNode");
  BLE.setAdvertisedService(sensorService);
  sensorService.addCharacteristic(sensorChar);
  BLE.addService(sensorService);
  BLE.advertise();
  Serial.println("BLE ready and advertising...");
   Serial.print("BLE MAC address: ");
  Serial.println(BLE.address());
}
uint64_t counter = 1;

void loop() {
  BLEDevice central = BLE.central();
  if (central) {
    Serial.println("Central connected");

  while (central.connected()) {
  imu.getSensorData();

  float data[] = {
    imu.data.accelX,
    imu.data.accelY,
    imu.data.accelZ,
    imu.data.gyroZ,
    millis()
  };

  long start = millis();
  sensorChar.writeValue((uint8_t*)data, sizeof(data));  // Send raw bytes
  long end = millis();
  Serial.println(end - start);
}

    Serial.println("Central disconnected");
  }
}
