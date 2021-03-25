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

#include "../SparkFun_BNO080_Arduino_Library/src/SparkFun_BNO085_Arduino_Library.cpp"
#include <SparkFun_Qwiic_Rfid.h>
#include <SoftwareSerial.h>
#include <Wire.h>

#define NEW_RFID_ADDR 0x09

BNO085 imu;
long time;
float linAccelX, linAccelY, linAccelZ;
float quatReal, quatI, quatJ, quatK, quatRadianAccuracy;
byte linAccelAccuracy, quatAccuracy;
byte stability;
String imuReading;
const int intPin = 8; // Interrupt Pin on pin 3
String current_tag_string;
int current_tag_string_length;

Qwiic_Rfid myRfid(NEW_RFID_ADDR);

//SparkFun RedBoard
//SoftwareSerial XBee(2, 3); // RX, TX

//Arduino Mega
SoftwareSerial XBee(19, 18); // XBee DOUT, IN - Arduino pin 19, 18 (RX, TX)

void setup() {
  Serial.begin(115200);
  Wire.begin();
  Wire.setClock(400000);  //Increase I2C data rate to 400kHz
  XBee.begin(9600);  
  pinMode(intPin, INPUT_PULLUP); 

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

  if (!myRfid.begin()) {
    Serial.println("Could not communicate with Qwiic RFID!");
  }
  else {
    Serial.println("Ready to scan some tags!");
  }
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

  if(digitalRead(intPin) == LOW) {  
  //if (Serial.available()) {  // without buzzer
      //Serial.readString();   // without buzzer
      
      current_tag_string = myRfid.getTag();
      //current_tag_string = "77777766"; // without buzzer

      // extract last 2 digits of tag
      current_tag_string_length = current_tag_string.length();
      String last_two_RFID_digits = current_tag_string.substring(current_tag_string_length - 2, current_tag_string_length);
      int current_tag = last_two_RFID_digits.toInt();
      XBee.write(current_tag); // transmit tag info to XBee Coordinator
      Serial.print("Tag ID (last 2 digits): ");
      Serial.println(current_tag);
  }
}
