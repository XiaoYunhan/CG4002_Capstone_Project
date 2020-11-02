#include <Wire.h> //for I2C communication
#include<math.h>
#include <string.h>

//for comm use
char receiveByte = "";
int handshakeDone = 0;
float rawData[12];
char rawDataStr[12] = "";
char dataPacket[20] = "";

float rotXWArray[11] = {0.0};
float rotYWArray[11] = {0.0};
float rotZWArray[11] = {0.0};

float rotXAArray[11] = {0.0};
float rotYAArray[11] = {0.0};
float rotZAArray[11] = {0.0};

//counter for serial printing
int positionIndex = 0;
int danceIndex = 0; 
int counterDance = 0;
int counterPosition = 0;

//store raw data of accel and gyro
long accelXW, accelYW, accelZW;  
long gyroXW, gyroYW, gyroZW;
long accelXA, accelYA, accelZA;  
long gyroXA, gyroYA, gyroZA;

//calculate accel and gyro in degree and g
float gForceXW, gForceYW, gForceZW;
float rotXW, rotYW, rotZW;
float gForceXA, gForceYA, gForceZA;
float rotXA, rotYA, rotZA;

void setup() {
  Serial.begin(115200);
  Wire.begin(); //initialise I2C communication
  setupMPUW();
  setupMPUA();
}

void loop() {
  initHandshake(); 
  recordAccelRegistersW(); //pre-processing
  recordGyroRegistersW();
  recordAccelRegistersA(); //pre-processing
  recordGyroRegistersA();
  updateDance();
  updatePosition();
  delay(100);
}

//Establish communication with MPU and set up needed registers to read data from
void setupMPUW() {
  Wire.beginTransmission(0b1101000); //I2C address of MPU
  Wire.write(0x6B); //Power Management
  Wire.write(0b00000000); //Power on MPU6050
  Wire.endTransmission();

  //Gyro configuration. 
  Wire.beginTransmission(0b1101000);
  Wire.write(0x1B); 
  Wire.write(0x00000000); //Set gyro full scale to +/- 250deg/sec
  Wire.endTransmission();
  
  //Acc configuration. 
  Wire.beginTransmission(0b1101000); 
  Wire.write(0x1C); 
  Wire.write(0b00000000); //Set acc full scale range to +/- 2g
  Wire.endTransmission();
}

void setupMPUA() {
  Wire.beginTransmission(0b1101001); //I2C address of MPU
  Wire.write(0x6B); //Power Management
  Wire.write(0b00000000); //Power on MPU6050
  Wire.endTransmission();

  //Gyro configuration. 
  Wire.beginTransmission(0b1101001);
  Wire.write(0x1B); 
  Wire.write(0x00000000); //Set gyro full scale to +/- 250deg/sec
  Wire.endTransmission();
  
  //Acc configuration. 
  Wire.beginTransmission(0b1101001); 
  Wire.write(0x1C); 
  Wire.write(0b00000000); //Set acc full scale range to +/- 2g
  Wire.endTransmission();
}

//retrieving raw data
void recordAccelRegistersW() {
  Wire.beginTransmission(0b1101000); //I2C address of MPU6050
  Wire.write(0x3B); //Starting register for acc readings.
  Wire.endTransmission();
  Wire.requestFrom(0b1101000,6);  //Request 6 acc registers (3B-40)

  while(Wire.available() < 6);
  accelXW = Wire.read()<<8|Wire.read();  //Store first two bytes 
  accelYW = Wire.read()<<8|Wire.read();  //Store middle two bytes
  accelZW = Wire.read()<<8|Wire.read();  //Store last two bytes
  processAccelDataW();
}

void processAccelDataW() {
  //convert data to g. LSB per g = 16384.0
  gForceXW = accelXW / 16384.0;
  gForceYW = accelYW / 16384.0;
  gForceZW = accelZW / 16384.0;
}

void recordAccelRegistersA() {
  Wire.beginTransmission(0b1101001); //I2C address of MPU6050
  Wire.write(0x3B); //Starting register for acc readings.
  Wire.endTransmission();
  Wire.requestFrom(0b1101001,6);  //Request 6 acc registers (3B-40)

  while(Wire.available() < 6);
  accelXA = Wire.read()<<8|Wire.read();  //Store first two bytes 
  accelYA = Wire.read()<<8|Wire.read();  //Store middle two bytes
  accelZA = Wire.read()<<8|Wire.read();  //Store last two bytes
  processAccelDataA();
}

void processAccelDataA() {
  //convert data to g. LSB per g = 16384.0
  gForceXA = accelXA / 16384.0;
  gForceYA = accelYA / 16384.0;
  gForceZA = accelZA / 16384.0;
}

void recordGyroRegistersW() {
  Wire.beginTransmission(0b1101000); //I2C address of MPU6050
  Wire.write(0x43); //Starting address for gyro readings 
  Wire.endTransmission();
  Wire.requestFrom(0b1101000,6);  //Request 6 gyro registers (43-48)

  while(Wire.available() < 6);
  gyroXW = Wire.read()<<8|Wire.read();  //Store first two bytes into
  gyroYW = Wire.read()<<8|Wire.read();  //Store middle two bytes into
  gyroZW = Wire.read()<<8|Wire.read();  //Store last two bytes into
  processGyroDataW();
}

void processGyroDataW() {
  //convert data to degrees. LSB per degrees per second = 131.0;
  rotXW = gyroXW / 131.0;
  rotYW = gyroYW / 131.0;
  rotZW = gyroZW / 131.0;
}

void recordGyroRegistersA() {
  Wire.beginTransmission(0b1101001); //I2C address of MPU6050
  Wire.write(0x43); //Starting address for gyro readings 
  Wire.endTransmission();
  Wire.requestFrom(0b1101001,6);  //Request 6 gyro registers (43-48)

  while(Wire.available() < 6);
  gyroXA = Wire.read()<<8|Wire.read();  //Store first two bytes into
  gyroYA = Wire.read()<<8|Wire.read();  //Store middle two bytes into
  gyroZA = Wire.read()<<8|Wire.read();  //Store last two bytes into
  processGyroDataA();
}

void processGyroDataA() {
  //convert data to degrees. LSB per degrees per second = 131.0;
  rotXA = gyroXA / 131.0;
  rotYA = gyroYA / 131.0;
  rotZA = gyroZA / 131.0;
}

void updateDance() {
  float meanXW=0, meanYW=0, meanZW=0, sumXW=0, sumYW=0, sumZW=0, differenceXW=0, differenceYW=0, differenceZW=0, totalDifferenceW=0, sqrtDifferenceW=0;
  danceIndex = counterDance % 10; //0-9 repeatedly

  //sum values in array
  for (int i=0; i<10; i++) {
    sumXW += rotXWArray[i];
    sumYW += rotYWArray[i];
    sumZW += rotZWArray[i];
  }
  meanXW = sumXW / 10.0;
  meanYW = sumYW / 10.0;
  meanZW = sumZW / 10.0;

  //save new value into index 10
  rotXWArray[10] = rotXW;
  rotYWArray[10] = rotYW;
  rotZWArray[10] = rotZW;
  
  differenceXW = sq(meanXW - rotXWArray[10]);
  differenceYW = sq(meanYW - rotYWArray[10]);
  differenceZW = sq(meanZW - rotZWArray[10]);

  totalDifferenceW = differenceXW + differenceYW + differenceZW;
  sqrtDifferenceW = sqrt(totalDifferenceW);

  //save value in counter index
  rotXWArray[positionIndex] = rotXW;
  rotYWArray[positionIndex] = rotYW;
  rotZWArray[positionIndex] = rotZW;  

  counterDance++;
  Serial.print(counterDance);
  Serial.print(" ");

  if (sqrtDifferenceW < 10) {
      Serial.print("-1/-1/-1/-1/-1/-1/");
    }
  else {
    processDanceData();
    //printDance();
  }
}

void updatePosition() {
  float meanXA=0, meanYA=0, meanZA=0, sumXA=0, sumYA=0, sumZA=0, differenceXA=0, differenceYA=0, differenceZA=0, totalDifferenceA=0, sqrtDifferenceA=0;
  positionIndex = counterPosition % 10; //0-9 repeatedly

  //sum values in array
  for (int i=0; i<10; i++) {
    sumXA += rotXAArray[i];
    sumYA += rotYAArray[i];
    sumZA += rotZAArray[i];
  }
  meanXA = sumXA / 10.0;
  meanYA = sumYA / 10.0;
  meanZA = sumZA / 10.0;

  //save new value into index 10
  rotXAArray[10] = rotXA;
  rotYAArray[10] = rotYA;
  rotZAArray[10] = rotZA;
  
  differenceXA = sq(meanXA - rotXAArray[10]);
  differenceYA = sq(meanYA - rotYAArray[10]);
  differenceZA = sq(meanZA - rotZAArray[10]);

  totalDifferenceA = differenceXA + differenceYA + differenceZA;
  sqrtDifferenceA = sqrt(totalDifferenceA);

  //save value in counter index
  rotXAArray[positionIndex] = rotXA;
  rotYAArray[positionIndex] = rotYA;
  rotZAArray[positionIndex] = rotZA;  

  if (sqrtDifferenceA < 10) {
      Serial.println("-1/-1/-1/-1/-1/-1/e");
    }
  else {
    processPositionData();
    //printPosition();
  }
}

void initHandshake() {
  while (!handshakeDone) {
    if (Serial.available()) {
      receiveByte = Serial.read();
      receiveByte = (char)receiveByte;
      if (receiveByte == 'H') {
        //Serial.println("Received 'H' from laptop.");
        Serial.write("ACK"); // Send 'ACK' to Laptop
        delay(500);
        handshakeDone = 1;
        break;
      }
    }
  }
}

void processDanceData() {
  memset(dataPacket, 0, sizeof(dataPacket));
  memset(rawDataStr, 0, sizeof(rawDataStr));
  rawData[0] = rotXW;
  rawData[1] = rotYW;
  rawData[2] = rotZW;
  rawData[3] = gForceXW;
  rawData[4] = gForceYW;
  rawData[5] = gForceZW;
    
  for(int i = 0; i < 6; i++) {
    char tempChar[7];
    dtostrf(rawData[i], 7, 4, tempChar);
    strcat(dataPacket, tempChar);
    strcat(dataPacket, rawDataStr);
    strcat(dataPacket,"/");
  }
  
  char checksumByte[2] = "";
  //checksumByte[0] = getChecksum(dataPacket);
  strcat(dataPacket,checksumByte);
  //strcat(dataPacket, "e");
  
  Serial.write(dataPacket);
  //Serial.println("");
}


void processPositionData() {
  memset(dataPacket, 0, sizeof(dataPacket));
  memset(rawDataStr, 0, sizeof(rawDataStr));
  rawData[6] = rotXA;
  rawData[7] = rotYA;
  rawData[8] = rotZA;
  rawData[9] = gForceXA;
  rawData[10] = gForceYA;
  rawData[11] = gForceZA;
    
  for(int i = 6; i < 12; i++) {
    char tempChar[7];
    dtostrf(rawData[i], 7, 4, tempChar);
    strcat(dataPacket, tempChar);
    strcat(dataPacket, rawDataStr);
    strcat(dataPacket,"/");
  }
  
  char checksumByte[2] = "";
  //checksumByte[0] = getChecksum(dataPacket);
  strcat(dataPacket,checksumByte);
  strcat(dataPacket, "e");
  
  Serial.write(dataPacket);
  Serial.println("");
}

char getChecksum(char dataPacket) {
  int len = strlen(dataPacket);
  char checksum = 0;
  return checksum;
}
