//servertest.ino
#include <Servo.h> // servo library
#include <ArduinoJson.h>

int defaultPos = 0; //default position for servo
int pos = 90;

// Assign RGB LED pins
unsigned const int G1 = 11;
unsigned const int Y1 = 10;
unsigned const int R1 = 9;
void setup()
{
  Serial.begin(9600);                                //  Sensor Buart Rate

    // Set pin mode of LEDs to OUTPUT
  pinMode(G1, OUTPUT);
  pinMode(Y1, OUTPUT);
  pinMode(R1, OUTPUT);
  
    // Start serial for XBee (TX0, RX0 = 1, 0)
  Serial.begin(9600);

  while (!Serial) {
    // wait for serial port to XBee to open
  }
}
void loop()
{
  // parse incoming Serial data
 if(Serial.available()){
  String rxString = "";
  String str= ""; //Set the size of the array to equal the number of values you will be receiveing.
  //Keep looping until there is something in the buffer.
  while (Serial.available()) {
    //Delay to allow byte to arrive in input buffer.
    delay(2);
    //Read a single character from the buffer.
    char ch = Serial.read();
    //Append that single character to a string.
    rxString+= ch;
  }

  str = rxString.substring(0, 0);

  int led = String(str).toInt();// to integer

  if (led == 1) { //led on
    digitalWrite(G1, HIGH);
    digitalWrite(Y1, HIGH);
    digitalWrite(R1, HIGH);
     delay(3000);
   } 
   else  {
    digitalWrite(G1, LOW);
    digitalWrite(Y1, LOW);
    digitalWrite(R1, LOW);
  }
 }

   delay(1000);
}
