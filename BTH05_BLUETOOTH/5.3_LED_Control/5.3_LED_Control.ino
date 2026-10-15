// Hardware UART D0/D1: disconnect HC-05 while uploading through USB.
char line[16];byte used=0;bool overflow=false;
void setup(){pinMode(13,OUTPUT);Serial.begin(9600);}
void loop(){while(Serial.available()){
 char c=Serial.read();if(c=='\r')continue;
 if(c=='\n'){
  line[used]=0;
  if(!overflow && strcmp(line,"on")==0){digitalWrite(13,HIGH);Serial.println("LED ON");}
  else if(!overflow && strcmp(line,"off")==0){digitalWrite(13,LOW);Serial.println("LED OFF");}
  else Serial.println("ERROR use on/off + newline");
  used=0;overflow=false;
 }else if(used<sizeof(line)-1)line[used++]=c;else overflow=true;
}}
