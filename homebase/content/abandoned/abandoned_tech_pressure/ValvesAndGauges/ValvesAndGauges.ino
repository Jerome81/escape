/**
* 4 light sensors sending their values through serial to a raspi for further processing.
**/

// INCLUDES
// Wire library used for I2C communication
#include <Wire.h>

// CONSTANTS
// To read analog inputs, we need to use a GPIO pin that supports analogRead (i.e. prefixed with "A")
const byte ldrPins[] = {A3, A2, A1, A0};

// 10-bit input values from the ADC have values in the range (0-1023)
int inputValues[4] = {};


void setup() {
  // Start the serial connection (used for debugging)
  Serial.begin(9600);
  // Print some useful debug output - the filename and compilation time
  Serial.println(__FILE__);
  Serial.println("Compiled: " __DATE__ ", " __TIME__);
}

void loop() {
  
  // READ INPUTS
  for(int i=0; i<4; i++){
    // The ADC can retain capacitance from previous read, which causes erroneous results
    // To try to prevent this, we'll take a few "dummy" readings and discard them.
    for(int x=0; x<2; x++) {
      analogRead(ldrPins[i]);
      // And also delay a short time before taking another reading
      delay(5);
    }
    // Now we'll retrieve LDR value once more, and this time store in inputValues array
    inputValues[i] = analogRead(ldrPins[i]);
    //Serial.print(i);
    //Serial.print(" ");
    Serial.print(inputValues[i]);
    Serial.print(",");
  }
  Serial.println();
  delay(150);
}
