# Dance Dance

This is the github repository for our CG4002 Capstone Project. The sections below explains the various subcomponents of our code.

## Hardware Sensor

'hardware_sensor_final.ino' configures the MPU6050 sensors and processes the raw data into a more meaningful value (converting to appropriate units). A dance and position detection algorithm is also implemented using a circular buffer and determining the status of the user from a threshold. Accordingly, the accelerometer and gyroscope values from the sensors will be printed.

## Hardware FPGA

*edit*

## Comms Internal

*edit*

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

*edit*

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
   
