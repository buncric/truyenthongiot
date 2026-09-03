#define LED1 13
#define LED2 14
#define LED3 15

void setup() {
pinMode(LED1, OUTPUT);
pinMode(LED2, OUTPUT);
pinMode(LED3, OUTPUT);
}

void loop() {
  digitalWrite(LED_BUILTIN, HIGH);  
  delay(1000);                     
  digitalWrite(LED_BUILTIN, LOW);   
  delay(1000);  
}
