#include <Wire.h> //for I2C communication

//store raw data of accel and gyro
long accelX, accelY, accelZ;  
long gyroX, gyroY, gyroZ;

//calculate accel and gyro in degree and g
float gForceX, gForceY, gForceZ;
float rotX, rotY, rotZ;

//calculate sum of accel and gyro in degree and g
float sumGForceX, sumGForceY, sumGForceZ;
float sumRotX, sumRotY, sumRotZ;

//calculate offset for xyz axis of accel and gyro
float offsetGForceX, offsetGForceY, offsetGForceZ;
float offsetRotX, offsetRotY, offsetRotZ;

//detect start/end move
boolean isStartDetected = false;
boolean toPrint = false;
float minGForceX=0.70, minGForceY=-0.30, minGForceZ=-0.90;
float maxGForceX=1.1, maxGForceY=0.2, maxGForceZ=-0.60;
int startCount=0;
int startPeriod = 30; //original 30
int startInterval = 1000;

//detect steps
int stepInterval = 2000;
int stepCount=0;
boolean isWalkingDetected = false;

unsigned long currentMillis, previousMillis;

void setup() {
  Serial.begin(9600);
  Wire.begin(); //initialise I2C communication
  setupMPU();
  calibrateAccel();
  calibrateGyro();
}

void loop() {
  recordAccelRegisters(); //pre-processing
  recordGyroRegisters();
  finalAccelData(); //subtract offset
  finalGyroData();
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

void calibrateAccel() {
  //sampling 100 acc data
  for (int i=0; i<100; i++) {
    recordAccelRegisters(); //pre-processing
    sumGForceX += gForceX;
    sumGForceY += gForceY;
    sumGForceZ += gForceZ;
  }
  //calculating acc xyz offset 
  offsetGForceX = sumGForceX/100;
  offsetGForceY = sumGForceY/100;
  offsetGForceZ = sumGForceZ/100;
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

void finalAccelData() {
  gForceX = gForceX - offsetGForceX;
  gForceY = gForceY - offsetGForceY;
  gForceZ = gForceZ - offsetGForceZ;
}

void calibrateGyro() {
  //sampling 100 gyro data
  for (int j=0; j<100; j++) {
    recordGyroRegisters();
    sumRotX += rotX;
    sumRotY += rotY;
    sumRotZ += rotZ;
  }
  //calculating gyro xyz offset
  offsetRotX = sumRotX/100;
  offsetRotY = sumRotY/100;
  offsetRotZ = sumRotZ/100;
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

void finalGyroData() {
  rotX = rotX - offsetRotX;
  rotY = rotY - offsetRotY;
  rotZ = rotZ - offsetRotZ;
}

void startMove() {    
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
  
  if (toPrint == false) {
    positionChange();
  }
}

//detect steps using accelerometer gForceX value
void positionChange() {   
  int totalCount = 0; 

  //first detection of position change    
  if (gForceX < 0.6) {
    isWalkingDetected = true;
    previousMillis=millis();
  }

  //Within stated duration. Waiting for follow-up move
  currentMillis=millis(); 
  if ((currentMillis - previousMillis <= stepInterval) && (isWalkingDetected)) {    
    //follow-up found
    if (gForceX >= 0.95) {
      stepCount++;
      isWalkingDetected = false;
      startCount = 0;
      isStartDetected = false;
    }
  }
  //no follow-up
  else {
    totalCount = stepCount;
  }

  if (startCount == 10) {   
    if (totalCount == 2) {
      Serial.println("1 position moved");
      stepCount = 0;
      startCount = 0;
    }

    if (totalCount > 2) {
      Serial.println("2 positions moved");
      stepCount = 0;
      startCount = 0;
    }
    //prevent misdetecting move if 1
    if (totalCount < 2) { 
      startCount++;
    }
    isWalkingDetected = false;
    isStartDetected = false;
  }
}

void printData() {
  Serial.print("Gyro (deg)");
  Serial.print(" X=");
  Serial.print(rotX);
  Serial.print(" Y=");
  Serial.print(rotY);
  Serial.print(" Z=");
  Serial.print(rotZ);
  Serial.print("Accel (g)");
  Serial.print(" X=");
  Serial.print(gForceX);
  Serial.print(" Y=");
  Serial.print(gForceY);
  Serial.print(" Z=");
  Serial.println(gForceZ);
}
