#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <time.h>
#if __has_include("config.local.h")
#include "config.local.h"
#else
#include "config.example.h"
#endif
#if __has_include("ca.h")
#include "ca.h"
#else
#include "ca.example.h"
#endif
WiFiClient plain;WiFiClientSecure secure;
PubSubClient mqtt(USE_TLS?static_cast<Client&>(secure):static_cast<Client&>(plain));
unsigned long lastAttempt=0,lastPub=0;bool attempted=false;
void setup(){Serial.begin(115200);WiFi.mode(WIFI_STA);WiFi.begin(WIFI_SSID,WIFI_PASSWORD);configTime(0,0,"pool.ntp.org","time.nist.gov");secure.setCACert(ROOT_CA);mqtt.setServer(MQTT_HOST,USE_TLS?8883:1883);mqtt.setSocketTimeout(2);}
void loop(){
 if(WiFi.status()!=WL_CONNECTED || (USE_TLS && time(nullptr)<1700000000)){delay(1);return;}
 if(!mqtt.connected()){
  if(attempted && millis()-lastAttempt<5000){delay(1);return;}
  attempted=true;lastAttempt=millis();unsigned long start=millis();
  bool ok=mqtt.connect("tls-sv01",MQTT_USER,MQTT_PASSWORD);
  Serial.printf("TLS=%d connected=%d connect_ms=%lu rc=%d\n",USE_TLS,ok,millis()-start,mqtt.state());if(!ok)return;
 }
 mqtt.loop();if(millis()-lastPub>=5000){lastPub=millis();mqtt.publish("iot/security/sv01/status","{\"temp\":30.5,\"simulated\":true}");}delay(1);
}
