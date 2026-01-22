#include <Arduino.h>
#include <Wire.h>
#include <MPU6050.h>

MPU6050 mpu;

// ESP32 default I2C pins
static const int I2C_SDA = 21;
static const int I2C_SCL = 22;

void setup() {
  Serial.begin(115200);
  delay(500);

  Wire.begin(I2C_SDA, I2C_SCL);
  // Wire.setClock(400000); // Fast I2C (optional) Fast I"C: 400000

  Serial.println("Initializing MPU6050...");
  mpu.initialize();

  if (!mpu.testConnection()) {
    Serial.println("MPU6050 connection failed! Check wiring/I2C address.");
    while (true) delay(1000);
  }

  // Optional: set ranges (defaults are usually OK)
  // mpu.setFullScaleAccelRange(MPU6050_ACCEL_FS_2);   // +/-2g
  // mpu.setFullScaleGyroRange(MPU6050_GYRO_FS_250);   // +/-250 deg/s

  Serial.println("MPU6050 connected.");

  // Wake up device (some modules start in sleep)
  mpu.setSleepEnabled(false);
}

void loop() {
  int16_t ax, ay, az;
  int16_t gx, gy, gz;

  mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);


    // Output CSV format: acc_x,acc_y,acc_z,gyro_x,gyro_y,gyro_z
  Serial.print(ax); Serial.print(",");
  Serial.print(ay); Serial.print(",");
  Serial.print(az); Serial.print(",");
  Serial.print(gx); Serial.print(",");
  Serial.print(gy); Serial.print(",");
  Serial.print(gz);
  Serial.println();

  // // Output CSV format: acc_x,acc_y,acc_z,gyro_x,gyro_y,gyro_z
  // Serial.print(ax/16384.0); Serial.print(",");
  // Serial.print(ay/16384.0); Serial.print(",");
  // Serial.print(az/16384.0); Serial.print(",");
  // Serial.print(gx/131.0); Serial.print(",");
  // Serial.print(gy/131.0); Serial.print(",");
  // Serial.print(gz/131.0);
  // Serial.println();

  delay(10); // 100 Hz sampling rate (matches your phone data)
}
