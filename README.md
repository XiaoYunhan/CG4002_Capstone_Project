# Dance Dance

This is the github repository for our CG4002 Capstone Project. The sections below explains the various subcomponents of our code.

## Hardware Sensor

'hardware_sensor_final.ino' configures the MPU6050 sensors and processes the raw data into a more meaningful value (converting to appropriate units). A dance and position detection algorithm is also implemented using a circular buffer and determining the status of the user from a threshold. Accordingly, the accelerometer and gyroscope values from the sensors will be printed.

## Hardware FPGA

There are 2 components for the hardware FPGA:

1. The FINN notebook for the synthesis and intermediate ONNX models:

   a. src/hardware_fpga/mlp_v*
      * mlp_v5 is the final version
      * mlp.ipynb contains the notebook used for synthesis
      * mlp_feat_1111_1002.onnx is the inital onnx model from the SW ML side

2. Deployment to FPGA board:

    a. src/hardware_fpga/mlp_v*_deployment
      * integrated into src/sw_machine_learning
      * mlp_v5_deployment_final is the final version
      
    b. contains:
      * driver.py: the driver file
      * fpga.py: file used to execute driver.py
      * resizer.bit: the bitfile generated by the notebook
      * resizer.hwh 
      * verify.py: used for hardware verification
      
## Comms Internal

1. src/arduino/arduino.ino: Contains the final version of code running on arduino side. 
                            It is based on hardware_sensor_final.ino and integrates Comms Internal part. Handshake and data format process are done here.

2. src/comm_internal/comm_internal.py: Set up BLE connection + handshake with beetle + receive and process sensor data received.  
   --> integrate into src/main_laptop.py: Contains the final version of code running on laptop side.

## Comms External

There are 4 parts for Comms External:  

1. Socket connection between laptop and ultra 96:  
    a. src/comm_external/socket_client.py (socket client with AES encryption + calculating RTT & offset for socket connection)  
    --> integrated into src/main_laptop.py  
    b. src/comm_external/socket_server.py (socket server with AES encryption + calculating RTT & offset for socket connection)  
    --> integrated into src/sw_machine_learning/multiuser_run.py

2. Socket connection between ultra 96 and evaluation server:  
    a. src/comm_external/eval_client.py (socket client to send processed message to the evaluation server)  
    --> integrated into src/sw_machine_learning/src/db_connect.py  
    b. src/comm_external/eval_server.py (provided by prof)  

3. Sync delay:  
    a. src/comm_external/multiple_server.py (run three socket server together & calculating the sync delay for dancers based on raw data)  
    --> integrated into src/sw_machine_learning/multiuser_run.py  

4. Connection between ultra 96 and database:  
    a. src/comm_external/DB_Client.py (send processed message to the dashboard database)  
    --> integrated into src/sw_machine_learning/src/db_connect.py  

## SW Machine Learning

1. Models

   a. Generated Quantised Models
      src/sw_machine_learning/quantised_models
      
   b. Generated Models
      src/sw_machine_learning/models
      
   c. Quantised Models Source
      src/sw_machine_learning/src/quantised_models
      
   d. Models Source
      src/sw_machine_learning/src/models
      
   e. src/sw_machine_learning/main.py
      * Driver script to train and store different models. Model to train, where to load data from and where to save model can all be configured here, along with number of Epochs, Learning Rate, etc.

2. Live Run Source

   a. src/sw_machine_learning/multiuser_run.py
      * Instantiates additional process to run the three user threads, as well as starts the 3 server connections to the 3 Beetle clients.
      * Instantiates connection to the database as well as evaluation server. 
      * Is able to run with different flags, allowing us to test with 1-3 users, with or without evaluation server, with or without FPGA model.
      
   b. src/sw_machine_learning/src/multiuser.py
      * Contains the MultiUser class that loads and stores the models used for prediction as well as the lock for thread sharing.
      * MultiUser.process_data() is the function that is continuously running on each thread to process the raw data from the server.
      
   c. src/sw_machine_learning/src/db_connect.py
      * Contains connection to database, evaluation server. Recieves data from multiuser process through a queue. 
      * For each type of packet recieved, the model takes in packets recieved within a certain time frame and aggregates all the predictions to give a more accurate prediction.

## SW Dashboard

There are 2 main components: frontend and backend. The frontend code is found in the "dashboard" folder in the "Software Dashboard" folder. The backend code is found in the "dashboardbackend" folder in the "Software Dashboard" folder.

The components of the frontend are as follows:

1. In dancedashboard/src/component/Charts:

   a. BarChartSet.vue - This vue file contains the code to plot the bar graph of Number of Sets Done vs Dancers, which plots the number of dance sets each dancer has partcipated in the current week so far.
   
   b. BarChartTime.vue - This vue file contains the code to plot the bar graph of Time Spent (minutes) vs Dancers, which plots how long each dancer has danced in the current week so far.
   
   c. PieChart.vue - This vue file contains the code to plot the Sync Pie Chart in the Real-time Dashboard page. The Sync Pie Chart shows the number of dance moves in the current set the dancers are in sync and not in sync so far. The code in this file accommodates the need to show the data in real-time.
   
   d. PieChartStatic.vue - This vue file contains the code to plot the Sync Pie Chart in the Past Dance Sets page. This code is different from the one above because this does not allow real-time display, which is not needed, since the data required is already available from the backend.
   
2. In dancedashboard/src/component:

   a. DancerInformation.vue - This vue file contains the code for the Dancers Information page, which shows 2 charts - Time Spent (minutes) vs Dancers and Number of Sets Done vs Dancers for each of the dancers for the current week.
   
   b. HowToUse.vue - This vue file contains the code for the User Guide that is present to help users in the event that they are unsure of what the 3 main pages (Real-time Dashboard, Past Dance Sets and Dancers Information) are meant for or how they should be used.
   
   c. PastDanceSets.vue - This vue file contains the code for the Past Dance Sets page, which shows tables and sync pie charts regarding all the past dance sets that has taken place so far.
   
   d. PersistentSideNavDrawer.vue - This vue file contains the code for the side navigation drawer.
   
   e. RealTimeDashboard.vue - This vue file contains the code for the Real-time Dashboard page.
   
The components of the backend are as follows:

1. In dancedashboardbackend:

   a. server.js - This Javascript file contains the backend code to connect to the database and to send data for all the pages, for example, parsing through the data received from comms external, sending the necessary data to the Real-time Dashboard page, sending all data pertaining to the past dance sets to the Past Dance Sets page, sending specific past dance sets data as specified by the user to the Past Dance Sets page, sending all data pertaining to how long each of the dancers have practised and the number of sets each of them have participated in the current week to the Dancers Information page, sending specific dancers information as specified by the user to the Dancers Information page and receiving the names of the dancers from the frontend.
   
