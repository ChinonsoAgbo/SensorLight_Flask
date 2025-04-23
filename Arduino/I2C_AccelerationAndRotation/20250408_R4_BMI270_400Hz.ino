#include <Wire.h>
#include "SparkFun_BMI270_Arduino_Library.h"

// Create a new sensor object
BMI270 imu;

// I2C address selection
uint8_t i2cAddress = BMI2_I2C_PRIM_ADDR; // 0x68
//uint8_t i2cAddress = BMI2_I2C_SEC_ADDR; // 0x69

uint8_t acc_odr = BMI2_ACC_ODR_400HZ;
uint8_t gyro_odr = BMI2_GYR_ODR_400HZ;
uint8_t gyr_Range = BMI2_GYR_RANGE_250;

int count;

void setup()
{
    // Start serial
    Serial.begin(230400);
    Serial.println("BMI270 Basic Readings 400Hz");

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
    delay(2000);
}


void loop()
{
    // Get measurements from the sensor. This must be called before accessing
    // the sensor data, otherwise it will never update
    imu.getSensorData();
    
    //Serial.print(count);
    Serial .print(count);
    Serial.print(", ");
    Serial.print(millis());
    Serial.print(", ");
    
    // Print acceleration data
    Serial.print(imu.data.accelX, 3);
    Serial.print(",");
    Serial.print(imu.data.accelY, 3);
    Serial.print(",");
    Serial.print(imu.data.accelZ, 3);

    Serial.print(",");

    // Print rotation data
    // Serial.print(imu.data.gyroX, 3);
    // Serial.print(",");
    // Serial.print(imu.data.gyroY, 3);
    // Serial.print(",");
    Serial.println(imu.data.gyroZ, 3);
  
    count = count + 1;
}
