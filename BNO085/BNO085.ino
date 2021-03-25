// #include <SparkFun_BNO085_Arduino_Library.h>
#include "SparkFun_BNO080_Arduino_Library/src/SparkFun_BNO085_Arduino_Library.cpp"
#include <SoftwareSerial.h>

BNO085 imu;
long time;
float linAccelX, linAccelY, linAccelZ;
float quatReal, quatI, quatJ, quatK, quatRadianAccuracy;
byte linAccelAccuracy, quatAccuracy;
byte stability;
String imuReading;

SoftwareSerial XBee(2, 3); // RX, TX

void setup() {
  Serial.begin(115200);
  Wire.begin();
  Wire.setClock(400000);  //Increase I2C data rate to 400kHz
  XBee.begin(9600);

  imu.begin();
  imu.enableLinearAccelerometer(5000);  //Send data updates at 200Hz
  imu.enableRotationVector(5000);       //Send data updates at 200Hz
  imu.enableStabilityClassifier(5000);  //Send data updates at 200Hz

  imu.tareAllAxes(TARE_ROTATION_VECTOR);

  imuReading =
    String("t,")
    + "linAccelX,linAccelY,linAccelZ,linAccelAccuracy,"
    + "quatI,quatJ,quatK,quatReal,quatAccuracy,quatRadianAccuracy,"
    + "stabilityClassification,";
  Serial.println(imuReading);
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


    imuReading =
      String(time/1000.0, 3) + ","

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

    Serial.println(imuReading);
    XBee.print(imuReading);
  }
}
