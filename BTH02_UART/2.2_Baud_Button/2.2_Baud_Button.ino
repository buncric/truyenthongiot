// Uno onboard LED is active HIGH. Button connects D2 to GND.
const byte BUTTON=2, LED=13;
bool rawOld=HIGH, stable=HIGH, configuring=false;
unsigned long changed=0,pressed=0,lastClick=0,baud=9600;
byte clicks=0;
void blink(byte n,unsigned int period) {
  for(byte i=0;i<n;i++){digitalWrite(LED,HIGH);delay(period);digitalWrite(LED,LOW);delay(period);}
}
void setup(){pinMode(BUTTON,INPUT_PULLUP);pinMode(LED,OUTPUT);Serial.begin(baud);Serial.println("RUN 9600");}
void loop(){
  unsigned long now=millis(); bool raw=digitalRead(BUTTON);
  if(raw!=rawOld){changed=now;rawOld=raw;}
  if(now-changed>=30 && raw!=stable){
    stable=raw;
    if(stable==LOW) pressed=now;
    else if(now-pressed>3000){
      configuring=!configuring;clicks=0;
      Serial.println(configuring?"CONFIG":"RUN");
      if(configuring) blink(3,80);
    }else if(configuring){clicks++;lastClick=now;}
  }
  if(configuring && stable==HIGH && clicks && now-lastClick>=600){
    if(clicks<=2){
      baud=clicks==1?9600:115200;
      Serial.print("Switch terminal to ");Serial.println(baud);Serial.flush();
      blink(clicks,150); Serial.end();Serial.begin(baud);
      Serial.print("BAUD=");Serial.println(baud);
    }else Serial.println("Invalid: use exactly 1 or 2 clicks");
    clicks=0;
  }
}
