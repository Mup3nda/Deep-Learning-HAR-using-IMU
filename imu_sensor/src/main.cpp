#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>

Adafruit_BNO055 bno;

void setup() {
  Serial.begin(9600);
  Serial.println("Orientation Sensor Test"); Serial.println("");


  if (!bno.begin()){
    Serial.print("Ooops, no BNO055 detected ... Check your wiring or I2C ADDR!");
    while(1);
  }

  delay(1000);

  bno.setExtCrystalUse(true);
  bno.setMode(OPERATION_MODE_IMUPLUS);

}

void loop() {

  sensors_event_t event;
  bno.getEvent(&event);
  imu::Vector<3> acc = bno.getVector(Adafruit_BNO055::VECTOR_ACCELEROMETER);
  imu::Vector<3> gyro = bno.getVector(Adafruit_BNO055::VECTOR_GYROSCOPE);


  // /* Display the floating point data */
  Serial.print(acc.x(), 4);
  Serial.print(",");
  Serial.print(acc.y(), 4);
  Serial.print(",");
  Serial.print(acc.z(), 4);
  Serial.print(",");
  Serial.print(gyro.x(), 4);
  Serial.print(",");
  Serial.print(gyro.y(), 4);
  Serial.print(",");
  Serial.print(gyro.z(), 4);
  Serial.println();

  // uint8_t system_cal, gyro_cal, acc_cal, mag_cal;
  // bno.getCalibration(&system_cal, &gyro_cal, &acc_cal, &mag_cal);
  // Serial.print("Gyro Calibration Status: ");
  // Serial.println(gyro_cal);
  // Serial.print("Acc Calibration Status: ");
  // Serial.println(acc_cal);
  // Serial.print("Sytem Calibration Status: ");
  // Serial.println(system_cal);
  // Serial.println("--------------------------------------------");

  delay(10);
}
