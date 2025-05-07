#include "SparkFun_BMI270_Arduino_Library.h"

// Create a new sensor object
BMI270 imu;
// I2C address selection
uint8_t i2cAddress = BMI2_I2C_PRIM_ADDR;  // 0x68
//uint8_t i2cAddress = BMI2_I2C_SEC_ADDR; // 0x69

uint8_t acc_odr = BMI2_ACC_ODR_400HZ;
uint8_t gyro_odr = BMI2_GYR_ODR_400HZ;
uint8_t gyr_Range = BMI2_GYR_RANGE_250;

void setup () {
  Serial.begin(2000000);
  Serial.println("BMI270 200Hz usb ");

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
}

void loop() {
  imu.getSensorData();
  String dataString =
    String(imu.data.accelX,3) + "," + String(imu.data.accelY, 3) + "," + String(imu.data.accelZ, 3) + "," + String(imu.data.gyroZ, 3) + "," + String(millis());

  Serial.println(dataString);
}
