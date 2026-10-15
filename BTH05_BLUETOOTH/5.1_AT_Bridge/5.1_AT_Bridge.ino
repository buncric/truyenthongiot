#include <SoftwareSerial.h>
SoftwareSerial bluetooth(10,11); // HC-05 TX -> D10; D11 -> divider -> HC-05 RX
void setup(){Serial.begin(9600);bluetooth.begin(38400);Serial.println("HC05 AT mode, CR+LF. KEY=3.3V before power on.");}
void loop(){while(Serial.available())bluetooth.write(Serial.read());while(bluetooth.available())Serial.write(bluetooth.read());}
