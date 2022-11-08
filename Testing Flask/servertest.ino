servertest.ino
#include <Servo.h> // servo library
#include <ArduinoJson.h>

int defaultPos = 0; //default position for servo
int pos = 90;

Servo myservo;

void setup()
{
  Serial.begin(9600);                                //  Sensor Buart Rate
  myservo.attach(9);                                   //  Servo PIN D9
  DynamicJsonDocument doc(1024); 
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

  int servo = String(str).toInt();// to integer

  if (servo == 1) {
     myservo.write(pos);              // tell servo to go to position in variable 'pos'
     delay(3000);
   } 
   else  {
    myservo.write(defaultPos);
  }
 }

   delay(1000);
}
