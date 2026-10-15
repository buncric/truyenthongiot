#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <Preferences.h>
#include <mbedtls/md.h>
#include <time.h>
#if __has_include("config.local.h")
#include "config.local.h"
#else
#include "config.example.h"
#endif
WiFiClient network;PubSubClient mqtt(network);Preferences store;
uint64_t highest=0;unsigned long lastAttempt=0,lastMessage=0;bool seen=false,attempted=false;
void receive(char*,byte* data,unsigned int len){
 if(len>512)return;JsonDocument doc;if(deserializeJson(doc,data,len))return;
 if(!doc["cmd"].is<const char*>()||!doc["nonce"].is<const char*>()||!doc["mac"].is<const char*>()||!doc["seq"].is<uint64_t>()||!doc["time"].is<int64_t>())return;
 String cmd=doc["cmd"].as<String>(),nonce=doc["nonce"].as<String>(),mac=doc["mac"].as<String>();
 if((cmd!="OPEN"&&cmd!="CLOSE")||nonce.length()!=16||mac.length()!=64)return;
 uint64_t seq=doc["seq"].as<uint64_t>();int64_t sent=doc["time"].as<int64_t>(),now=time(nullptr);
 if(now<1700000000 || sent<now-10 || sent>now+10 || seq<=highest){Serial.println("REJECT stale/replay");return;}
 char canonical[128];snprintf(canonical,sizeof(canonical),"%s|%lld|%s|%llu",cmd.c_str(),(long long)sent,nonce.c_str(),(unsigned long long)seq);
 unsigned char digest[32];mbedtls_md_hmac(mbedtls_md_info_from_type(MBEDTLS_MD_SHA256),(const unsigned char*)HMAC_KEY,strlen(HMAC_KEY),(const unsigned char*)canonical,strlen(canonical),digest);
 char expected[65];for(int i=0;i<32;i++)snprintf(expected+2*i,3,"%02x",digest[i]);
 byte mismatch=0;for(int i=0;i<64;i++)mismatch|=expected[i]^mac[i];if(mismatch){Serial.println("REJECT bad MAC");return;}
 // Persist before actuation so a reboot cannot make the same sequence valid again.
 if(store.putULong64("highest",seq)!=sizeof(seq)){Serial.println("REJECT NVS write error");return;}
 highest=seq;digitalWrite(ESP32_LED_PIN,cmd=="OPEN"?HIGH:LOW);mqtt.publish("iot/security/sv01/state",cmd.c_str());Serial.println("ACCEPT signed fresh command");
}
void setup(){Serial.begin(115200);pinMode(ESP32_LED_PIN,OUTPUT);digitalWrite(ESP32_LED_PIN,LOW);store.begin("iot-replay",false);highest=store.getULong64("highest",0);WiFi.begin(WIFI_SSID,WIFI_PASSWORD);configTime(0,0,"pool.ntp.org");mqtt.setServer(MQTT_HOST,1883);mqtt.setBufferSize(768);mqtt.setSocketTimeout(2);mqtt.setCallback(receive);}
void loop(){
 if(WiFi.status()!=WL_CONNECTED){delay(1);return;}
 if(!mqtt.connected()){
  if(attempted&&millis()-lastAttempt<3000){delay(1);return;}attempted=true;lastAttempt=millis();
  if(mqtt.connect("signed-sv01",MQTT_USER,MQTT_PASSWORD))mqtt.subscribe("iot/security/sv01/cmd",1);
 }else mqtt.loop();delay(1);
}
