#include <Wire.h>
#include "SparkFun_BNO085_Arduino_Library.h"

BNO085 imu;
long time;
float linAccelX, linAccelY, linAccelZ;
float quatReal, quatI, quatJ, quatK, quatRadianAccuracy;
byte linAccelAccuracy, quatAccuracy;
byte stability;

void setup() {
  Serial.begin(115200);
  Wire.begin();
  Wire.setClock(400000);  //Increase I2C data rate to 400kHz

  imu.begin();
  imu.enableLinearAccelerometer(5000);  //Send data updates at 200Hz
  imu.enableRotationVector(5000);       //Send data updates at 200Hz
  imu.enableStabilityClassifier(5000);  //Send data updates at 200Hz

  imu.tareAllAxes(TARE_ROTATION_VECTOR);

  Serial.print("t,");
  Serial.print("linAccelX,linAccelY,linAccelZ,");
  Serial.print("linAccelAccuracy,");
  Serial.print("quatI,quatJ,quatK,quatReal,");
  Serial.print("quatAccuracy,quatRadianAccuracy");
  Serial.print("stabilityClassification");
  Serial.println();
}

void loop() {
  if (imu.dataAvailable()) {
    time = millis();

    linAccelX = imu.getLinAccelX();
    linAccelY = imu.getLinAccelY();
    linAccelZ = imu.getLinAccelZ();
    linAccelAccuracy = imu.getLinAccelAccuracy();

    quatI = imu.getQuatI();
    quatJ = imu.getQuatJ();
    quatK = imu.getQuatK();
    quatReal = imu.getQuatReal();
    quatAccuracy = imu.getQuatAccuracy();
    quatRadianAccuracy = imu.getQuatRadianAccuracy();

    stability = imu.getStabilityClassification();


    Serial.print(time/1000.0, 3); Serial.print(",");

    Serial.print(linAccelX, 4); Serial.print(",");
    Serial.print(linAccelY, 4); Serial.print(",");
    Serial.print(linAccelZ, 4); Serial.print(",");
    Serial.print(linAccelAccuracy); Serial.print(",");

    Serial.print(quatI, 4); Serial.print(",");
    Serial.print(quatJ, 4); Serial.print(",");
    Serial.print(quatK, 4); Serial.print(",");
    Serial.print(quatReal, 4); Serial.print(",");
    Serial.print(quatAccuracy); Serial.print(",");
    Serial.print(quatRadianAccuracy, 4); Serial.print(",");

    Serial.print(stability); Serial.print(",");

    Serial.println();
  }
}
