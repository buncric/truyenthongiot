#define LAB 2

#if defined(ESP8266)
#include <ESP8266WiFi.h>
const int LED_PIN=LED_BUILTIN;const byte LED_ON=LOW;
#else
#include <WiFi.h>
#endif
#include <PubSubClient.h>
#if __has_include("config.local.h")
#include "config.local.h"
#else
#include "config.example.h"
#endif
#if !defined(ESP8266)
const int LED_PIN=ESP32_LED_PIN;const byte LED_ON=HIGH;
#endif
WiFiClient transport;PubSubClient mqtt(transport);
String root,cmdTopic,stateTopic,lwtTopic;bool led=false;
unsigned long lastAttempt=0,lastTelemetry=0;bool attempted=false;
void apply(bool on){led=on;digitalWrite(LED_PIN,on?LED_ON:!LED_ON);}
void publishState(){mqtt.publish(stateTopic.c_str(),led?"ON":"OFF",LAB==3);}
void receive(char* topic,byte* data,unsigned int len){
 if(String(topic)!=cmdTopic || len>6)return;
 String command;for(unsigned int i=0;i<len;i++)command+=(char)data[i];
 if(command=="ON")apply(true);else if(command=="OFF")apply(false);
 else if(command=="TOGGLE")apply(!led);else return;
 publishState();
}
void setup(){
 Serial.begin(115200);pinMode(LED_PIN,OUTPUT);apply(false);
 root=String("iot/lab")+LAB+"/"+STUDENT_ID;cmdTopic=root+"/cmd";stateTopic=root+"/state";lwtTopic=root+"/lwt";
 WiFi.mode(WIFI_STA);WiFi.begin(WIFI_SSID,WIFI_PASSWORD);
 mqtt.setServer(MQTT_HOST,1883);mqtt.setCallback(receive);mqtt.setKeepAlive(30);mqtt.setSocketTimeout(2);
}
void loop(){
 if(WiFi.status()!=WL_CONNECTED){delay(1);return;}
 if(!mqtt.connected()){
  if(attempted && millis()-lastAttempt<3000){delay(1);return;}
  attempted=true;lastAttempt=millis();String id=String("lab")+LAB+"-"+STUDENT_ID;
  bool ok=LAB==3?mqtt.connect(id.c_str(),MQTT_USER,MQTT_PASSWORD,lwtTopic.c_str(),1,true,"OFFLINE"):mqtt.connect(id.c_str(),MQTT_USER,MQTT_PASSWORD);
  if(!ok){Serial.println(mqtt.state());return;}
  if(LAB>1){mqtt.subscribe(cmdTopic.c_str(),1);publishState();}
  if(LAB==3){mqtt.publish(lwtTopic.c_str(),"ONLINE",true);mqtt.publish((root+"/note").c_str(),"BOOT/RECONNECT",false);}
 }
 mqtt.loop();
 if(LAB==1 && millis()-lastTelemetry>=5000){lastTelemetry=millis();char payload[100];
  // Synthetic readings for protocol exercises, not measured sensor values.
  snprintf(payload,sizeof(payload),"{\"temp\":%.1f,\"hum\":%.1f,\"simulated\":true}",random(250,350)/10.0,random(400,800)/10.0);
  mqtt.publish((root+"/sensor").c_str(),payload);Serial.println(payload);
 }
 delay(1);
}
