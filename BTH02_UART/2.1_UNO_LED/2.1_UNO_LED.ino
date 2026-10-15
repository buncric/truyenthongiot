#include <SoftwareSerial.h>
SoftwareSerial link(10, 9); // RX, TX
void setup() { Serial.begin(9600); link.begin(9600); pinMode(13,OUTPUT); }
void loop() {
  while (link.available()) {
    char c=link.read();
    if (c=='1') { digitalWrite(13,HIGH); link.println("LED ON"); }
    else if (c=='0') { digitalWrite(13,LOW); link.println("LED OFF"); }
    else if(c!='\r' && c!='\n') link.println("Use 1 or 0");
  }
}
