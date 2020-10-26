#include<Wire.h>

const int MPU_addr=0x68;  // I2C address of the MPU-6050

const byte AC_SENS = 0;   // Accelerometer sensitivity (0-3)
const byte GY_SENS = 0;   // Gyroscope sensitivity (0-3)

const float AC_SCALE = 16384/(AC_SENS + 1);
const float GY_SCALE = 131/(GY_SENS + 1);

int16_t AcX,AcY,AcZ,Tmp,GyX,GyY,GyZ;

long startTime = 0;
long elapsedTime = 0;

void setup() {
  Wire.begin();

  Wire.beginTransmission(MPU_addr);
  Wire.write(0x6B);  // PWR_MGMT_1 register
  Wire.write(0);     // set to zero (wakes up the MPU-6050)
  Wire.endTransmission(true);

  Wire.beginTransmission(MPU_addr);
  Wire.write(0x1B);  // Gyro config register
  Wire.write(GY_SENS<<3);
  Wire.endTransmission(true);

  Wire.beginTransmission(MPU_addr);
  Wire.write(0x1C);  // Acc config register
  Wire.write(AC_SENS<<3);
  Wire.endTransmission(true);

  Serial.begin(9600);
  Serial.print("t,AcX,AcY,AcZ,GyX,GyY,GyZ,");
//  Serial.print("Tmp");
  Serial.println();
  startTime = millis();
}

void loop() {
  Wire.beginTransmission(MPU_addr);
  Wire.write(0x3B);  // starting with register 0x3B (ACCEL_XOUT_H)
  Wire.endTransmission(false);
  Wire.requestFrom(MPU_addr,14,true);  // request a total of 14 registers

  elapsedTime = millis() - startTime;

  AcX=Wire.read()<<8|Wire.read();  // 0x3B (ACCEL_XOUT_H) & 0x3C (ACCEL_XOUT_L)
  AcY=Wire.read()<<8|Wire.read();  // 0x3D (ACCEL_YOUT_H) & 0x3E (ACCEL_YOUT_L)
  AcZ=Wire.read()<<8|Wire.read();  // 0x3F (ACCEL_ZOUT_H) & 0x40 (ACCEL_ZOUT_L)
  Tmp=Wire.read()<<8|Wire.read();  // 0x41 (TEMP_OUT_H) & 0x42 (TEMP_OUT_L)
  GyX=Wire.read()<<8|Wire.read();  // 0x43 (GYRO_XOUT_H) & 0x44 (GYRO_XOUT_L)
  GyY=Wire.read()<<8|Wire.read();  // 0x45 (GYRO_YOUT_H) & 0x46 (GYRO_YOUT_L)
  GyZ=Wire.read()<<8|Wire.read();  // 0x47 (GYRO_ZOUT_H) & 0x48 (GYRO_ZOUT_L)

  // Time (s)
  Serial.print(elapsedTime/1000.0, 3); Serial.print(',');

  // Linear acceleration (multiples of g)
  Serial.print(AcX/AC_SCALE, 3); Serial.print(',');
  Serial.print(AcY/AC_SCALE, 3); Serial.print(',');
  Serial.print(AcZ/AC_SCALE, 3); Serial.print(',');

  // Angular acceleration (°/s)
  Serial.print(GyX/GY_SCALE, 3); Serial.print(',');
  Serial.print(GyY/GY_SCALE, 3); Serial.print(',');
  Serial.print(GyZ/GY_SCALE, 3); Serial.print(',');

  // Temperature (°C)
//  Serial.print(Tmp/340.00+36.53);

  Serial.println();
}
