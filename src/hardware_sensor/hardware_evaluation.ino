#include <Wire.h> //for I2C communication
#include<math.h>

float rotXWArray[11] = {0.0};
float rotYWArray[11] = {0.0};
float rotZWArray[11] = {0.0};

//counter for serial printing
int countIndex = 0;
int counter = 0;

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
  Serial.begin(9600);
  Wire.begin(); //initialise I2C communication
  setupMPUW();
  setupMPUA();
}

void loop() {
  recordAccelRegistersW(); //pre-processing
  recordGyroRegistersW();
  recordAccelRegistersA(); //pre-processing
  recordGyroRegistersA();
  updateGyro();
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

void updateGyro() {
  float meanX=0, meanY=0, meanZ=0, sumX=0, sumY=0, sumZ=0, differenceX=0, differenceY=0, differenceZ=0, totalDifference=0, sqrtDifference=0;
  countIndex = counter % 10; //0-9 repeatedly

  //sum values in array
  for (int i=0; i<10; i++) {
    sumX += rotXWArray[i];
    sumY += rotYWArray[i];
    sumZ += rotZWArray[i];
  }
  meanX = sumX / 10.0;
  meanY = sumY / 10.0;
  meanZ = sumZ / 10.0;

  //save new value into index 10
  rotXWArray[10] = rotXW;
  rotYWArray[10] = rotYW;
  rotZWArray[10] = rotZW;
  
  differenceX = sq(meanX - rotXWArray[10]);
  differenceY = sq(meanY - rotYWArray[10]);
  differenceZ = sq(meanZ - rotZWArray[10]);

  totalDifference = differenceX + differenceY + differenceZ;
  sqrtDifference = sqrt(totalDifference);

  //save value in counter index
  rotXWArray[countIndex] = rotXW;
  rotYWArray[countIndex] = rotYW;
  rotZWArray[countIndex] = rotZW;  
  
  counter++;
  if (counter > 5) {
    Serial.print(counter-5); Serial.print(" ");
    if (sqrtDifference < 5) {
      Serial.println("-1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1");
    }
    else {
      printData();
    }
  }
}

//Gyro x,y,z & Acc x,y,z
void printData() {
  Serial.print(rotXW, 4);
  Serial.print(" ");
  Serial.print(rotYW, 4);
  Serial.print(" ");
  Serial.print(rotZW, 4);
  Serial.print(" ");
  Serial.print(gForceXW, 4);
  Serial.print(" ");
  Serial.print(gForceYW, 4);
  Serial.print(" ");
  Serial.print(gForceZW, 4);
  Serial.print(" ");
  Serial.print(rotXA, 4);
  Serial.print(" ");
  Serial.print(rotYA, 4);
  Serial.print(" ");
  Serial.print(rotZA, 4);
  Serial.print(" ");
  Serial.print(gForceXA, 4);
  Serial.print(" ");
  Serial.print(gForceYA, 4);
  Serial.print(" ");
  Serial.println(gForceZA, 4);
}
