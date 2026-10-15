#include <SPI.h>
const byte CS=10, DEVICES=4;
// H E L O: columns, MSB top; orientation may depend on the physical module.
const byte font[][5]={{0x7f,8,8,8,0x7f},{0x7f,0x49,0x49,0x49,0x41},{0x7f,0x40,0x40,0x40,0x40},{0x3e,0x41,0x41,0x41,0x3e}};
const byte letters[]={0,1,2,2,3};
byte columns[64]={0}; unsigned long last=0;byte offset=0;
void command(byte reg,byte value){
 SPI.beginTransaction(SPISettings(1000000,MSBFIRST,SPI_MODE0));digitalWrite(CS,LOW);
 for(byte i=0;i<DEVICES;i++){SPI.transfer(reg);SPI.transfer(value);}digitalWrite(CS,HIGH);SPI.endTransaction();
}
void setup(){
 pinMode(CS,OUTPUT);digitalWrite(CS,HIGH);SPI.begin();command(0x0f,0);command(9,0);command(0x0b,7);command(0x0a,3);command(0x0c,1);
 for(byte l=0;l<5;l++)for(byte c=0;c<5;c++)columns[16+l*6+c]=font[letters[l]][c];
}
void loop(){if(millis()-last<90)return;last=millis();
 for(byte row=0;row<8;row++){
  SPI.beginTransaction(SPISettings(1000000,MSBFIRST,SPI_MODE0));digitalWrite(CS,LOW);
  for(int module=3;module>=0;module--){byte bits=0;for(byte x=0;x<8;x++)if(columns[(offset+module*8+x)%64]&(1<<row))bits|=1<<x;
   SPI.transfer(row+1);SPI.transfer(bits);}
  digitalWrite(CS,HIGH);SPI.endTransaction();
 } offset=(offset+1)%64;
}
