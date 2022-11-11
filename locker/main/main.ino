#include <Servo.h>
#include <ArduinoJson.h>

#define LOCKER "A"
#define OCCTHRESHOLD 10
#define CLSTHRESHOLD 10

// Assign ultrasonic pins
unsigned const int trig1 = 36;
unsigned const int echo1 = 37;
unsigned const int trig2 = 40;
unsigned const int echo2 = 41;
unsigned const int trig3 = 44;
unsigned const int echo3 = 45;

// Assign RGB LED pins
unsigned const int G1 = 11;
unsigned const int Y1 = 10;
unsigned const int R1 = 9;
unsigned const int G2 = 8;
unsigned const int Y2 = 7;
unsigned const int R2 = 6;
unsigned const int G3 = 5;
unsigned const int Y3 = 4;
unsigned const int R3 = 3;

// Assign IR range sensor
unsigned const int IR1 = A0;
unsigned const int IR2 = A1;
unsigned const int IR3 = A2;

// Group components based on lot
const int lots[][7] = {
  {1, trig1, echo1, IR1, G1, Y1, R1},
  {2, trig2, echo2, IR2, G2, Y2, R2}, 
  {3, trig3, echo3, IR3, G3, Y3, R3}
}; 

// Assign serial pins for servo controller
unsigned const int ServoTx = 18;
unsigned const int ServoRx = 19;

void setup() {
  // Set pin mode of LEDs to OUTPUT
  pinMode(G1, OUTPUT);
  pinMode(Y1, OUTPUT);
  pinMode(R1, OUTPUT);
  pinMode(G2, OUTPUT);
  pinMode(Y2, OUTPUT);
  pinMode(R2, OUTPUT);
  pinMode(G3, OUTPUT);
  pinMode(Y3, OUTPUT);
  pinMode(R3, OUTPUT);

  // Set pin mode of trigger pins to OUTPUT
  // Set pin mode of echo pins to INPUT
  pinMode(trig1, OUTPUT);             
  pinMode(echo1, INPUT);
  pinMode(trig2, OUTPUT);             
  pinMode(echo2, INPUT);
  pinMode(trig3, OUTPUT);             
  pinMode(echo3, INPUT);
  
  // Set pin mode of servo tx pin to OUTPUT
  // Set pin mode of servo rx pin to INPUT
  pinMode(ServoTx, OUTPUT);
  pinMode(ServoRx, INPUT);
  // Start serial for XBee (TX0, RX0 = 1, 0)
  Serial.begin(9600);

  while (!Serial) {
    // wait for serial port to XBee to open
  }
  
  // Start serial for servo controller (TX1, RX1 = 18, 19)
  Serial1.begin(9600);
  while (!Serial1) {
    // wait for serial port to servo controller to open
  }

  on_off_motor(0,1);
  // Lock all lockers
  set_ch_pos_spd(lots[0][0], 4000, 80);
  set_ch_pos_spd(lots[1][0], 4000, 80);
  set_ch_pos_spd(lots[2][0], 4000, 80);
}

void loop() {
  // Receive json input from central server
  if (Serial.available() > 0) {
    StaticJsonDocument<500> doc;
    deserializeJson(doc, Serial);

    if (doc["Locker"] == LOCKER) {
      // Run command function
      if (doc["Command"] == "Lock") {
        for (int i = 0; i < 3; i++) {
          if (doc["Lot"] == lots[i][0]) {
            lot_command(lots[i], true); 
          }
        }
      } 
      else {
        for (int i = 0; i < 3; i++) {
          if (doc["Lot"] == lots[i][0]) {
            lot_command(lots[i], false); 
          }
        }
      }
    }
  }
}

void check_occupied(const int lot[]) {
  StaticJsonDocument doc(500);
  boolean occupied;
  
  // Ultrasonic sensor segment (occupancy)
  digitalWrite(lot[1], LOW);           // Clears the trigPin
  delayMicroseconds(2);
  digitalWrite(lot[1], HIGH);          // Sets the trigPin on HIGH state for 10 micro seconds
  delayMicroseconds(10);
  digitalWrite(lot[1], LOW);

  long duration = pulseIn(lot[2], HIGH);    // Reads the echoPin, returns the sound wave travel time in microseconds
  int occDistance = duration * 0.034 / 2;    // Calculating the distance

  if (occDistance < OCCTHRESHOLD) {
    // Light up Red LED to signify that lot is occupied
    digitalWrite(lot[4], LOW);
    digitalWrite(lot[5], LOW);
    digitalWrite(lot[6], HIGH);
    occupied = true;
  }
  else {
    // Light up Green LED to signify that lot is unoccupied
    digitalWrite(lot[4], HIGH);
    digitalWrite(lot[5], LOW);
    digitalWrite(lot[6], LOW);
    occupied = false;
  }

  // Create Json document, send it via Serial
  doc["Locker"] = LOCKER;
  doc["Lot"] = lot[0];
  doc["Occupied"] = occupied;

  serializeJson(doc, Serial);
  Serial.println();
}

void unlock_lot(const int lot[]) {
  boolean closed = false;
  
  // set servo to be open position 
  set_ch_pos_spd(lot[0], 0, 0);
  
  do {
    digitalWrite(lot[4], HIGH);
    digitalWrite(lot[5], HIGH);
    digitalWrite(lot[6], HIGH);
    delay(1000)
    digitalWrite(lot[4], LOW);
    digitalWrite(lot[5], LOW);
    digitalWrite(lot[6], LOW);
    delay(1000);

    // check if door is closed
    // Long range IR sensor (locker status)
    int raw = analogRead(lot[3]);
    float voltage = float(raw) * (5.0 / 1023.0);
    float distance = (voltage - (206/65)) * (-325 / 6);

    if (distance < CLSTHRESHOLD) {
      closed = true;
    }
  } while (!closed)

  // set servo to be open position 
  set_ch_pos_spd(lot[0], 4000, 0);
  check_occupied(lot);
}

void on_off_motor(unsigned char channel, unsigned char on) {
  unsigned char first_byte = 0;
  first_byte = 0b11000000 | channel;
  Serial1.write(first_byte);
  Serial1.write(on);
}

void set_ch_pos_spd(unsigned char channel, unsigned int position, unsigned char velocity)
{
 /*****Position and Speed Command*****
  * position: 0-8000
  * velocity: 0-100, 0 is faster than 100
 - 4 bytes involved
 - 1st byte: Start byte + Servo motor channel
   eg: 
     0b 0 1 x x x x x x 
      Start|Servo channel
       bit
 - 2 MSBs (01) is mode for position and speed command
 - the last xxxxxx can be assigned with value 1-32, where
   1 ---> select channel 1
   2 ---> select channel 2
   ....
   ....
   32 ---> select channel 32
 - 2nd byte: Position (High byte) higher 6-bit  
   eg: 
     0b 0 0 x x x x x x
 - the last xxxxxx can be assigned with value 0 - 63
 - 3nd byte: Position (Low byte) lower 6-bit
   eg: 
     0b 0 0 x x x x x x
 - the last xxxxxx can be assigned with value 0 - 63
   **2nd byte and 3byte is the position value when combined together into 12 bits position
 - 4th byte: Speed (0-63)
   eg:
     0b 0 0 x x x x x x
 - the last xxxxxx can be assigned with value 0 - 63
 ************************************/
  unsigned char first_byte = 0;
  unsigned char high_byte = 0;
  unsigned char low_byte = 0; 
 
  first_byte = 0b11100000 | channel;  //make up the 1st byte
  high_byte = (position >> 6) & 0b01111111;  //obtain the high byte of 12 bits position value
  low_byte = position & 0b00111111;  //obtain the low byte of 12 bits position value
 
  Serial1.write(first_byte);  //send the 1st byte
  Serial1.write(high_byte);  //send the 2nd byte
  Serial1.write(low_byte);  //send the 3rd byte
  Serial1.write(velocity);  //send the 4th byte
}
