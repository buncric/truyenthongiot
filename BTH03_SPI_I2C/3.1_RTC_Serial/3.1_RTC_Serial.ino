#include <Wire.h>
#include <RTClib.h>
RTC_DS1307 rtc;
unsigned long last=0;
void setup(){
  Serial.begin(9600);Wire.begin();
  if(!rtc.begin()){Serial.println("DS1307 not found (0x68)");while(true)delay(100);}
  if(!rtc.isrunning())rtc.adjust(DateTime(F(__DATE__),F(__TIME__)));
}
void loop(){
  if(millis()-last>=1000){last=millis();DateTime t=rtc.now();char out[32];
    snprintf(out,sizeof(out),"%02u/%02u/%04u - %02u:%02u:%02u",t.day(),t.month(),t.year(),t.hour(),t.minute(),t.second());Serial.println(out);
  }
}
