/*****************************************************************
Software_Serial_IO_test.ino
Author: edited by Fosse Lin-Bianco
Notes: Original tutorial taken from SparkFun website

Set up a software serial port to pass data between an XBee Shield
and the serial monitor.

Hardware Hookup:
  The XBee Shield makes all of the connections you'll need
  between Arduino and XBee. If you have the shield make
  sure the SWITCH IS IN THE "DLINE" POSITION. That will connect
  the XBee's DOUT and DIN pins to Arduino pins 2 and 3.

*****************************************************************/
// We'll use SoftwareSerial to communicate with the XBee:
#include <SoftwareSerial.h>
#include <Wire.h>
#include <SparkFun_Qwiic_Rfid.h>

#define RFID_ADDR 0x7D // Default I2C address
#define NEW_RFID_ADDR 0x09 // Default I2C address

int serialInput;
const int intPin = 8; // Interrupt Pin on pin 3
String current_tag_string;
int current_tag_string_length;

Qwiic_Rfid myRfid(NEW_RFID_ADDR);

//For Atmega328P's
// XBee's DOUT (TX) is connected to pin 2 (Arduino's Software RX)
// XBee's DIN (RX) is connected to pin 3 (Arduino's Software TX)
SoftwareSerial XBee(2, 3); // RX, TX

void setup()
{
  XBee.begin(9600);
  Wire.begin();
  Serial.begin(115200); // RFID Baud rate

  pinMode(intPin, INPUT_PULLUP); 

  if(!myRfid.begin())
    Serial.println("Could not communicate with Qwiic RFID!"); 
  else
    Serial.println("Ready to scan some tags!"); 
}

void loop()
{
  
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
