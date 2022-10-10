#include <Servo.h>
Servo lockingLatch1;
Servo lockingLatch2;
Servo lockingLatch3;
int latchPin1 = 46;
int latchPin2 = 48;
int latchPin3 = 50;
String lockStat;

void setup(){
  lockingLatch1.attach(latchPin1);
  lockingLatch2.attach(latchPin2);
  lockingLatch3.attach(latchPin3);
  Serial.begin(9600);
  lockingLatch1.write(110);
  lockingLatch2.write(110);
  lockingLatch3.write(110);
  delay(100);
}

void loop(){
  while (Serial.available() == 0);
  delay(10);
  lockStat = Serial.readString();
  lockStat.trim();
  if (lockStat == "unlock") {
    lockingLatch1.write(0);
    lockingLatch2.write(0);
    lockingLatch3.write(0);
    delay(10);
  }
  if (lockStat == "lock") {
    lockingLatch1.write(110);
    lockingLatch2.write(110);
    lockingLatch3.write(110);
    delay(10);
  }
}