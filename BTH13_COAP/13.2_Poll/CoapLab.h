// Minimal educational CoAP client: IPv4, 2-byte token, one in-flight exchange.
// RFC 7252 CON/NON + RFC 7641 Observe + RFC 7959 Block2, blocks of 128 bytes.
#if defined(ESP8266)
#include <ESP8266WiFi.h>
#else
#include <WiFi.h>
#endif
#include <WiFiUdp.h>
#if __has_include("config.local.h")
#include "config.local.h"
#else
#include "config.example.h"
#endif
WiFiUDP udp;byte sentPacket[256],inPacket[256];size_t sentLength=0;
byte token[2];uint16_t mid=0;bool pending=false,observing=false,finished=false,blockActive=false;
unsigned long deadline=0,timeoutMs=0,lastSend=0;byte retries=0;
uint32_t nextBlock=0,totalBytes=0;bool allA=true;
uint32_t observeSeq=0;bool haveObserveSeq=false;
void wireSend(const byte* p,size_t n){udp.beginPacket(COAP_SERVER_IP,COAP_SERVER_PORT);udp.write(p,n);udp.endPacket();}
void option(byte number,const byte* value,byte length,byte& previous,size_t& size){
 byte delta=number-previous;
 if(delta<13)sentPacket[size++]=(delta<<4)|length;
 else{sentPacket[size++]=0xd0|length;sentPacket[size++]=delta-13;}
 for(byte i=0;i<length;i++)sentPacket[size++]=value[i];previous=number;
}
void sendRequest(){
 size_t n=0;bool confirmable=MODE!=0;mid++;
 if(MODE!=4 || !blockActive){token[0]=random(256);token[1]=random(256);}
 sentPacket[n++]=confirmable?0x42:0x52;sentPacket[n++]=MODE<=1?2:1;
 sentPacket[n++]=mid>>8;sentPacket[n++]=mid&255;sentPacket[n++]=token[0];sentPacket[n++]=token[1];byte previous=0;
 if(MODE==3)option(6,nullptr,0,previous,n);
 if(MODE==4){const byte path[]="firmware";option(11,path,8,previous,n);
  uint32_t value=(nextBlock<<4)|3;byte encoded[3];byte count=value>65535?3:value>255?2:1;
  for(byte i=0;i<count;i++)encoded[count-1-i]=(value>>(i*8))&255;option(23,encoded,count,previous,n);blockActive=true;
 }else{const byte first[]="sensor",second[]="temp";option(11,first,6,previous,n);option(11,second,4,previous,n);}
 if(MODE<=1){const char payload[]="temp=30.5";sentPacket[n++]=255;memcpy(sentPacket+n,payload,9);n+=9;}
 sentLength=n;wireSend(sentPacket,n);pending=confirmable;timeoutMs=2000+random(1001);deadline=millis()+timeoutMs;retries=0;lastSend=millis();Serial.printf("SEND MID=%u bytes=%u\n",mid,(unsigned)n);
}
bool extended(byte nibble,const byte* p,size_t n,size_t& index,uint16_t& value){
 if(nibble<13){value=nibble;return true;}
 if(nibble==13 && index<n){value=13+p[index++];return true;}
 if(nibble==14 && index+1<n){value=269+((uint16_t)p[index]<<8)+p[index+1];index+=2;return true;}return false;
}
void receivePacket(size_t n){
 if(n<4 || (inPacket[0]>>6)!=1)return;byte type=(inPacket[0]>>4)&3,tkl=inPacket[0]&15,code=inPacket[1];uint16_t responseMid=((uint16_t)inPacket[2]<<8)|inPacket[3];
 if(code==0 && type==2 && responseMid==mid){pending=false;return;}
 if(code==0 || tkl!=2 || n<6 || memcmp(inPacket+4,token,2))return;
 if(type==2 && responseMid!=mid)return;
 if(type==0){byte ack[]={0x60,0,(byte)(responseMid>>8),(byte)responseMid};wireSend(ack,4);}
 pending=false;if((code>>5)!=2){Serial.printf("CoAP error %u.%02u\n",code>>5,code&31);finished=true;return;}
 size_t index=6;uint16_t number=0;bool hasBlock=false,more=false,hasObserve=false;uint32_t block=0,seq=0;byte szx=0;
 while(index<n && inPacket[index]!=255){byte head=inPacket[index++];uint16_t delta,len;
  if(!extended(head>>4,inPacket,n,index,delta)||!extended(head&15,inPacket,n,index,len)||index+len>n)return;
  number+=delta;
  if(number==23){if(len>3)return;uint32_t v=0;for(uint16_t i=0;i<len;i++)v=(v<<8)|inPacket[index+i];block=v>>4;more=v&8;szx=v&7;hasBlock=true;}
  if(number==6){if(len>3)return;hasObserve=true;for(uint16_t i=0;i<len;i++)seq=(seq<<8)|inPacket[index+i];}
  index+=len;
 }
 if(index<n && inPacket[index]==255)index++;
 size_t payloadLength=n-index;
 if(MODE==4){
  if(!hasBlock || szx!=3 || block!=nextBlock || payloadLength>128 || totalBytes+payloadLength>2048){Serial.println("Unexpected Block2");return;}
  for(size_t i=index;i<n;i++)if(inPacket[i]!='A')allA=false;
  totalBytes+=payloadLength;Serial.printf("BLOCK=%lu M=%d size=%u total=%lu\n",(unsigned long)block,more,(unsigned)payloadLength,(unsigned long)totalBytes);
  if(more){nextBlock++;sendRequest();}else{finished=true;Serial.println(totalBytes==2048&&allA?"PASS 2048 bytes A":"FAIL payload");}
 }else{
  if(MODE==3){if(!hasObserve){Serial.println("Observe not accepted");finished=true;return;}if(haveObserveSeq && ((seq-observeSeq)&0xffffff)>=0x800000)return;if(haveObserveSeq&&seq==observeSeq)return;observeSeq=seq;haveObserveSeq=true;observing=true;}
  Serial.printf("RESPONSE MID=%u: ",responseMid);Serial.write(inPacket+index,payloadLength);Serial.println();if(MODE<=1)finished=true;
 }
}
void setup(){Serial.begin(115200);randomSeed(micros());WiFi.begin(WIFI_SSID,WIFI_PASSWORD);udp.begin(56830);}
void loop(){
 if(WiFi.status()!=WL_CONNECTED){delay(1);return;}
 int bytes=udp.parsePacket();if(bytes>0){
  if(udp.remoteIP()==COAP_SERVER_IP && udp.remotePort()==COAP_SERVER_PORT && bytes<=(int)sizeof(inPacket)){int n=udp.read(inPacket,sizeof(inPacket));if(n>0)receivePacket(n);}else while(udp.available())udp.read();
 }
 if(pending && (int32_t)(millis()-deadline)>=0){
  if(retries>=4){pending=false;finished=true;Serial.println("TIMEOUT after 4 retries");}
  else{wireSend(sentPacket,sentLength);retries++;timeoutMs*=2;deadline=millis()+timeoutMs;Serial.printf("RETRY=%u MID=%u\n",retries,mid);}
 }
 if(!lastSend)sendRequest();
 else if(MODE==2 && !pending && millis()-lastSend>=2000)sendRequest();
 // Observe is established once; reboot board to cancel and start a new experiment.
 delay(1);
}
