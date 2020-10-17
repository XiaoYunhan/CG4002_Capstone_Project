#include <Wire.h> //for I2C communication

//counter for serial printing
//int count = 0;

//store raw data of accel and gyro
long accelX, accelY, accelZ;  
long gyroX, gyroY, gyroZ;

//calculate accel and gyro in degree and g
float gForceX, gForceY, gForceZ;
float rotX, rotY, rotZ;

//detect start/end move
boolean isStartDetected = false;
boolean toPrint = false;
float minGForceX=0.8000, minGForceY=-0.0600, minGForceZ=0.3000;
float maxGForceX=1.1000, maxGForceY=0.2000, maxGForceZ=0.6000;
int startCount=0;
int startPeriod = 15;
int startInterval = 1000;

unsigned long currentMillis, previousMillis;

void setup() {
  Serial.begin(9600);
  Wire.begin(); //initialise I2C communication
  setupMPU();
}

void loop() {
  recordAccelRegisters(); //pre-processing
  recordGyroRegisters();
  //printData();
  startMove();
  delay(100);
}

//Establish communication with MPU and set up needed registers to read data from
void setupMPU() {
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

//retrieving raw data
void recordAccelRegisters() {
  Wire.beginTransmission(0b1101000); //I2C address of MPU6050
  Wire.write(0x3B); //Starting register for acc readings.
  Wire.endTransmission();
  Wire.requestFrom(0b1101000,6);  //Request 6 acc registers (3B-40)

  while(Wire.available() < 6);
  accelX = Wire.read()<<8|Wire.read();  //Store first two bytes 
  accelY = Wire.read()<<8|Wire.read();  //Store middle two bytes
  accelZ = Wire.read()<<8|Wire.read();  //Store last two bytes
  processAccelData();
}

void processAccelData() {
  //convert data to g. LSB per g = 16384.0
  gForceX = accelX / 16384.0;
  gForceY = accelY / 16384.0;
  gForceZ = accelZ / 16384.0;
}

void recordGyroRegisters() {
  Wire.beginTransmission(0b1101000); //I2C address of MPU6050
  Wire.write(0x43); //Starting address for gyro readings 
  Wire.endTransmission();
  Wire.requestFrom(0b1101000,6);  //Request 6 gyro registers (43-48)

  while(Wire.available() < 6);
  gyroX = Wire.read()<<8|Wire.read();  //Store first two bytes into
  gyroY = Wire.read()<<8|Wire.read();  //Store middle two bytes into
  gyroZ = Wire.read()<<8|Wire.read();  //Store last two bytes into
  processGyroData();
}

void processGyroData() {
  //convert data to degrees. LSB per degrees per second = 131.0;
  rotX = gyroX / 131.0;
  rotY = gyroY / 131.0;
  rotZ = gyroZ / 131.0;
}

void startMove() {
  //detect start move
  if (gForceX >= minGForceX && gForceX <= maxGForceX) {
    if (gForceY >= minGForceY && gForceY <= maxGForceY) {
      if (gForceZ >= minGForceZ && gForceZ <= maxGForceZ) { 
        startCount++;
        Serial.println(startCount);
        isStartDetected = true;
        previousMillis=millis();
      }
    }
  }
  currentMillis = millis();
  //no detection
  if ((currentMillis - previousMillis > startInterval) && (isStartDetected)) {
    isStartDetected = false;
    startCount = 0;
  }

  //detection for stated duration
  if (startCount == startPeriod) {
    toPrint = !toPrint;
    startCount = 0;
  }

  if (toPrint == true) {
    printData();
  } 
}

//Gyro x,y,z & Acc x,y,z
void printData() {
//  count++;
//  Serial.print(count);
//  Serial.print(" ");
  Serial.print(rotX, 4);
  Serial.print(" ");
  Serial.print(rotY, 4);
  Serial.print(" ");
  Serial.print(rotZ, 4);
  Serial.print(" ");
  Serial.print(gForceX, 4);
  Serial.print(" ");
  Serial.print(gForceY, 4);
  Serial.print(" ");
  Serial.println(gForceZ, 4);
}
