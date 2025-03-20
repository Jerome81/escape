/**
* Valves and Gauges Puzzle, Copyright (c) 2022 Playful Technology
* 
* This puzzle demonstrates a typical "plumbing" escape room puzzle that makes use of: 
* - input valves (using an LED and LDR either side of a plumbing lever)
* - output gauges (using servo motors on a 3D printed gauge indicator)
* Players use the lever valves to adjust the pressure value displayed on each of the gauges
* When all gauge needles are pointing to the correct pressure (within allowed tolerance), a relay
* is energised which could release a maglock etc.
**/

// INCLUDES
// Wire library used for I2C communication
#include <Wire.h>
// PCA9685 16-channel PWM controller used to control the servo gauges
// See: https://github.com/NachtRaveVL/PCA9685-Arduino
#include "src/PCA9685/PCA9685.h"

// CONSTANTS
// To read analog inputs, we need to use a GPIO pin that supports analogRead (i.e. prefixed with "A")
const byte ldrPins[] = {A3, A2, A1, A0};
// This pin will be written LOW when the puzzle is solved
const byte relayPin = 2;
// The angle (-90 - 90) which each meter needs to be set to to solve the puzzle
// Positive angles rotate the servo clockwise BUT we're viewing gauges from the front, so
// 90 = min (extreme counter-clockwise), 0 = midpoint, -90 = max (extreme-clockwise) 
const int8_t targetValues[] = {60, -60, 0, -60};
// How much tolerance either side of target will we allow and still consider value as correct?
const uint8_t tolerance = 30;

// GLOBALS
// The PCA9685 controller will send values to servos 
PCA9685 pwmController;
// Helper class for calculating correct PWM values for angles etc.
PCA9685_ServoEval pwmServo;
// 10-bit input values from the ADC have values in the range (0-1023)
int inputValues[4] = {};
// Output values represent gauge angle from -90 to 90
// These will be converted to 16-bit PWM values in the range (0-4096)
int outputValues[4] = {};
// Has the puzzle been solved?
bool isSolved = false;

void setup() {
  // Start the serial connection (used for debugging)
  Serial.begin(115200);
  // Print some useful debug output - the filename and compilation time
  Serial.println(__FILE__);
  Serial.println("Compiled: " __DATE__ ", " __TIME__);

  // Initialise I2C interface used for the PCA9685 PWM controller
  Wire.begin();
  // Supported baud rates are 100kHz, 400kHz, and 1000kHz
  Wire.setClock(400000);
  // Initialise PCA9685
  pwmController.resetDevices();
  pwmController.init();
  // 50Hz provides 20ms standard servo phase length
  pwmController.setPWMFrequency(50);  

  // Set the output pin to control the relay when the puzzle is solved
  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, HIGH);
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
  }

  // SET OUTPUTS
  for(int i=0; i<4; i++){
    // Note that because we're looking at the servo from the front, we have to reverse the readings, so that
    // high values are negative angles.
    int gaugeAngle = map(inputValues[i], 900, 100, -90, 90);
    
    // Assign the result to the output values array,ensuring it doesn't exceed 90 degrees
    outputValues[i] = constrain(gaugeAngle, -90, 90);

    // Calculate PWM corresponding to desired angle
    int pwm = pwmServo.pwmForAngle(outputValues[i]);
    
    // Send this value to the appropriate channel on the PCA9685 servo controller
    pwmController.setChannelPWM(i, pwm);
  }
  
  // COMPARE AGAINST TARGET VALUES
  // Start by assuming that all gauges are correct
  bool allGaugesCorrect = true;
  // Loop over each output
  for(int i=0; i<4; i++){
    // If this gauge lies outside the allowed tolerance
    if(abs(outputValues[i] - targetValues[i]) > tolerance) {
      // All gauges are not correct
      allGaugesCorrect = false;
    }
  }

  // CHECK SOLUTION
  // If we get this far and allGaugesCorrect is still true, every value must have been within accepted tolerance
  if(allGaugesCorrect && !isSolved) {
    // Solve code here
    Serial.println("Solved!");
    isSolved = true;
    digitalWrite(relayPin, LOW);
  }
 // If the puzzle had been solved, but now the meters are no longer correct
  else if(isSolved && !allGaugesCorrect) {
    Serial.println("Unsolved!");
    isSolved = false;
    digitalWrite(relayPin, HIGH);
  }

  // DEBUG
  // If desired, print output to serial monitor for debugging
  for(int i=0; i<4; i++) {
    Serial.print(inputValues[i]);
    Serial.print(",");
    Serial.print(outputValues[i]);
    if(i<3) { Serial.print(","); }
  }
  Serial.println("");

  delay(50);
}
