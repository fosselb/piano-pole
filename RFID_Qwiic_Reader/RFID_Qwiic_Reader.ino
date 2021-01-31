// RFID_QWiic_Reader.ino
// Author: Fosse Lin-Bianco
// Purpose: To read input from a detected RFID tag
// References:
//      Example code used from SparkFun Qwiic RFID Arduino Library by Elias Santistevan

#include <Wire.h>
#include <SparkFun_Qwiic_Rfid.h>

#define RFID_ADDR 0x7D // Default I2C address
#define MAX_RFID_STORAGE 20

String allTags[MAX_RFID_STORAGE];
float allTimes[MAX_RFID_STORAGE];
int serialInput;

Qwiic_Rfid myRfid(RFID_ADDR);

void setup() {
  // Begin I-squared-C
  Wire.begin(); 
  Serial.begin(115200); // Baud rate

  if(!myRfid.begin())
    Serial.println("Could not communicate with Qwiic RFID!"); 
  else
    Serial.println("Ready to scan some tags!"); 

  Serial.println("Enter '1' into ther Serial Terminal to retrieve all tags that have been scanned.");
}

void loop() {
  if (Serial.available() > 0) {
    serialInput = Serial.read();
    if (serialInput == 49) {      // "1" is Ascii 49. 

      // Fill the given tag and time arrays. 
      myRfid.getAllTags(allTags);
      myRfid.getAllPrecTimes(allTimes);

      for(int i = 0; i < MAX_RFID_STORAGE; i++)
      {
        Serial.print("RFID Tag: "); 
        Serial.print(allTags[i]);
        Serial.print(" Scan Time: ");
        Serial.println(allTimes[i]);
      }

    }
  }
}
