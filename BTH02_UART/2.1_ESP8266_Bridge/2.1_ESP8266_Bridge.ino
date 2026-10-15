#include <SoftwareSerial.h>
// NodeMCU: D2=GPIO4 RX; D1=GPIO5 TX. Uno TX must be level shifted to 3.3V.
SoftwareSerial link(4, 5);
void setup() { Serial.begin(115200); link.begin(9600); }
void loop() {
  while (Serial.available()) link.write(Serial.read());
  while (link.available()) Serial.write(link.read());
  yield();
}
