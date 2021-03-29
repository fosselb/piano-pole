// XBee_Coordinator.ino
// Author: Fosse Lin-Bianco
// Purpose: To receive data from multiple XBees to the Coordinator XBee
//    and print HEX packet to Serial Monitor.
// Hardware: 1) XBee Series 3 + XBee Shield + Arduino RedBoard

#include <SoftwareSerial.h>

const char START_BYTE = 0x7E;
byte current;
byte previous;
int byteNum = -1;
int length = -1;
int address;
byte checksum;  //Only care about least significant byte, so  doesn't matter if carry is dropped
String line;

//SparkFun RedBoard
SoftwareSerial XBee(2, 3); // XBee DOUT, IN - Arduino pin 2, 3 (RX, TX)

//Arduino Mega
//SoftwareSerial XBee(19, 18); // XBee DOUT, IN - Arduino pin 19, 18 (RX, TX)

void setup() {
  XBee.begin(115200);
  Serial.begin(115200);
}

void loop() {
  if (XBee.available()) {
    current = XBee.read();
    if (current == START_BYTE) {
      Serial.println();
      line = "";
      byteNum = 0;
      length = -1;
      checksum = 0;
    } else if (byteNum == -1) {
      return;
    }

    // Serial.print(current, HEX);
    // Serial.print(",");

    if (byteNum == 2) {
      length = (previous << 8) | current;
      length += 3;  //Include start and length bytes but NOT checksum byte
    } else if (byteNum == 5) {
      address = (previous << 8) | current;
      Serial.println(address);  //Print source address
    } else if (byteNum >= 8 && byteNum < length) {
      line += (char) current;  //Append data
    }

    if (byteNum > 2) {
      checksum += current;
    }

    if (byteNum == length) {
      if (checksum == 0xFF) {
        Serial.print(line);
      } else {
        Serial.println("<ERROR>");
      }
    }

    previous = current;
    byteNum++;
  }
}
