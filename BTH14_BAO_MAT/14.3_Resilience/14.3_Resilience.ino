#include <WiFi.h>
#include <PubSubClient.h>
#include <esp_task_wdt.h>
#include <esp_idf_version.h>
#if __has_include("config.local.h")
#include "config.local.h"
#else
#include "config.example.h"
#endif
WiFiClient network;PubSubClient mqtt(network);
unsigned long lastWifi=0,lastMQTT=0,lastProcessed=0,lastStatus=0,backoff=1000;bool first=true,accepted=false,wdtReady=false;unsigned long dropped=0;
void receive(char*,byte* data,unsigned int length){
 if(length>50 || (accepted && millis()-lastProcessed<100)){dropped++;return;}
 if(length==2 && memcmp(data,"ON",2)==0)digitalWrite(ESP32_LED_PIN,HIGH);
 else if(length==3 && memcmp(data,"OFF",3)==0)digitalWrite(ESP32_LED_PIN,LOW);else{dropped++;return;}
 accepted=true;lastProcessed=millis();
}
void setup(){Serial.begin(115200);pinMode(ESP32_LED_PIN,OUTPUT);WiFi.mode(WIFI_STA);WiFi.begin(WIFI_SSID,WIFI_PASSWORD);mqtt.setServer(MQTT_HOST,1883);mqtt.setCallback(receive);mqtt.setBufferSize(256);mqtt.setSocketTimeout(2);
 esp_task_wdt_config_t cfg={};cfg.timeout_ms=10000;cfg.idle_core_mask=0;cfg.trigger_panic=true;
 esp_err_t result=esp_task_wdt_init(&cfg);if(result==ESP_ERR_INVALID_STATE)result=esp_task_wdt_reconfigure(&cfg);
 if(result==ESP_OK)wdtReady=esp_task_wdt_add(NULL)==ESP_OK;
}
void loop(){
 if(wdtReady)esp_task_wdt_reset();unsigned long now=millis();
 if(WiFi.status()!=WL_CONNECTED){if(now-lastWifi>=10000){lastWifi=now;WiFi.reconnect();}delay(1);return;}
 if(!mqtt.connected()){
  if(first || now-lastMQTT>=backoff){first=false;lastMQTT=now;
   if(mqtt.connect("resilient-sv01",MQTT_USER,MQTT_PASSWORD)){mqtt.subscribe("iot/resilience/sv01/cmd",1);backoff=1000;}
   else backoff=min(backoff*2,30000UL);
  }
 }else{mqtt.loop();if(now-lastStatus>=5000){lastStatus=now;char msg[100];snprintf(msg,sizeof(msg),"{\"uptime_ms\":%lu,\"dropped\":%lu}",now,dropped);mqtt.publish("iot/resilience/sv01/status",msg);}}
 delay(1);
}
