#include <SoftwareSerial.h>
SoftwareSerial chipKit(2, 3);
char lockStat;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  chipKit.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  while (Serial.available() == 0);
  lockStat = Serial.read();
  chipKit.print(lockStat);
  chipKit.flush();
}
