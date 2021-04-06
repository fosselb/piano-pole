/*
BNO085_RFID.ino
Author: Fosse Lin-Bianco and Evan Mitchell
Purpose: To read IMU and RFID data. Transmit both via XBee.

Hardware Hookup:
  The XBee Shield makes all of the connections you'll need
  between Arduino and XBee. If you have the shield make
  sure the SWITCH IS IN THE "DLINE" POSITION. That will connect
  the XBee's DOUT and DIN pins to Arduino pins 2 and 3.
*/

#include <SparkFun_BNO085_Arduino_Library.h>
#include <SparkFun_Qwiic_Rfid.h>

#define NEW_RFID_ADDR 0x09

BNO085 imu;
long time;
float linAccelX, linAccelY, linAccelZ;
float quatReal, quatI, quatJ, quatK, quatRadianAccuracy;
byte linAccelAccuracy, quatAccuracy;
byte stability;
String imuReading;
const int intPin = 7;
byte rfidTag;

Qwiic_Rfid rfid(NEW_RFID_ADDR);

void setup() {
  SerialUSB.begin(9600);  // Initialize Serial Monitor USB
  Serial.begin(9600);     // Initialize hardware serial port, pins 17/16
  while (!SerialUSB);
  while (!Serial);

  Wire.begin();
  Wire.setClock(400000);  //Increase I2C data rate to 400kHz

  imu.begin();
  imu.enableLinearAccelerometer(5000);  //Send data updates at 200Hz
  imu.enableRotationVector(5000);       //Send data updates at 200Hz
  imu.enableStabilityClassifier(5000);  //Send data updates at 200Hz

  pinMode(intPin, INPUT_PULLUP);
  rfid.begin();
  
  imu.tareAllAxes(TARE_ROTATION_VECTOR);

  imuReading = "t,linAccelX,linAccelY,linAccelZ,linAccelAccuracy,quatI,quatJ,quatK,quatReal,quatAccuracy,quatRadianAccuracy,stabilityClassification,";
  SerialUSB.println(imuReading);
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

    SerialUSB.println(imuReading);
    Serial.println(imuReading);               //Transmit IMU data to XBee Coordinator
  }

  if (digitalRead(intPin) == LOW) {
    rfidTag = (byte) rfid.getTag().toInt();   //Extract final byte of tag

    SerialUSB.println("T" + String(rfidTag));
    Serial.println("T" + String(rfidTag));    //Transmit RFID tag to XBee Coordinator
  }
}
