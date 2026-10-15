#include <WiFi.h>
#include <PubSubClient.h>
#if __has_include("config.local.h")
#include "config.local.h"
#else
#include "config.example.h"
#endif
WiFiClient network;PubSubClient mqtt(network);unsigned long nextAttempt=0;
void receive(char*,byte* data,unsigned int n){if(n==4 && memcmp(data,"OPEN",4)==0){digitalWrite(ESP32_LED_PIN,HIGH);Serial.println("OPEN accepted (vulnerable)");}if(n==5 && memcmp(data,"CLOSE",5)==0)digitalWrite(ESP32_LED_PIN,LOW);}
void setup(){Serial.begin(115200);pinMode(ESP32_LED_PIN,OUTPUT);WiFi.begin(WIFI_SSID,WIFI_PASSWORD);mqtt.setServer(MQTT_HOST,1883);mqtt.setSocketTimeout(2);mqtt.setCallback(receive);}
void loop(){if(WiFi.status()!=WL_CONNECTED){delay(1);return;}if(!mqtt.connected()){if((int32_t)(millis()-nextAttempt)>=0){nextAttempt=millis()+3000;if(mqtt.connect("vulnerable-sv01",MQTT_USER,MQTT_PASSWORD))mqtt.subscribe("iot/security/sv01/cmd");}}else mqtt.loop();delay(1);}
