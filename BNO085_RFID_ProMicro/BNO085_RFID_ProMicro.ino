/*
BNO085_RFID.ino
Author: Fosse Lin-Bianco and Evan Mitchell
Purpose: To read IMU and RFID data. Transmit both via XBee.
*/

#include <SparkFun_BNO085_Arduino_Library.h>
#include <SparkFun_Qwiic_Rfid.h>

#define XBee Serial1

float time;

BNO085 imu;
float linAccelX, linAccelY, linAccelZ;
float quatReal, quatI, quatJ, quatK, quatRadianAccuracy;
byte linAccelAccuracy, quatAccuracy, stability;
String imuString;

Qwiic_Rfid rfid(0x7D);
byte rfidTag;
String rfidString;

void setup() {
  Serial.begin(9600);
  XBee.begin(9600);

  Wire.begin();
  Wire.setClock(400000);  //Increase I2C data rate to 400kHz

  imu.begin();
  imu.enableLinearAccelerometer(5000);  //Send data updates at 200Hz
  imu.enableRotationVector(5000);       //Send data updates at 200Hz
  imu.enableStabilityClassifier(5000);  //Send data updates at 200Hz
  imu.tareAllAxes(TARE_ROTATION_VECTOR);

  rfid.begin();

  imuString = "t,linAccelX,linAccelY,linAccelZ,linAccelAccuracy,quatI,quatJ,quatK,quatReal,quatAccuracy,quatRadianAccuracy,stabilityClassification,";
  Serial.println(imuString);
}

void loop() {
  if (imu.dataAvailable()) {
    time = millis() / 1000.0;

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


    imuString =
      String(time, 3) + ","

      + String(linAccelX, 4) + ","
      + String(linAccelY, 4) + ","
      + String(linAccelZ, 4) + ","
      + String(linAccelAccuracy) + ","

      + String(quatI, 4) + ","
      + String(quatJ, 4) + ","
      + String(quatK, 4) + ","
      + String(quatReal, 4) + ","
      + String(quatAccuracy) + ","
      + String(quatRadianAccuracy, 4) + ","

      + String(stability) + ",";

    Serial.println(imuString);
    XBee.println("i" + imuString);
  }

  rfidTag = (byte) rfid.getTag().toInt();   //Extract final byte of tag
  if (rfidTag != 0) {
    time = millis() / 1000.0 - rfid.getPrecReqTime();

    rfidString =
      String(time, 3) + ","
      + String(rfidTag) + ",";

    Serial.println(rfidString);
    XBee.println("r" + rfidString);
  }
}
