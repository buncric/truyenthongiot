#include <DHT.h>
DHT dht(2,DHT11);unsigned long last=0;
void setup(){Serial.begin(9600);dht.begin();}
void loop(){if(millis()-last<2000)return;last=millis();float t=dht.readTemperature(),h=dht.readHumidity();
 if(isnan(t)||isnan(h)){Serial.println("{\"error\":\"DHT read failed\"}");return;}
 Serial.print("{\"temp\":");Serial.print(t,1);Serial.print(",\"hum\":");Serial.print(h,1);Serial.println("}");
}
