# Dance Dance

This is the github repository for our CG4002 Capstone Project. The sections below explains the various subcomponents of our code.

## Hardware Sensor

'hardware_sensor_final.ino' configures the MPU6050 sensors and processes the raw data into a more meaningful value (converting to appropriate units). A dance and position detection algorithm is also implemented using a circular buffer and determining the status of the user from a threshold. Accordingly, the accelerometer and gyroscope values from the sensors will be printed.

## Hardware FPGA

*edit*

## Comms Internal

*edit*

## Comms External

*edit*

## SW Machine Learning

*edit*

## SW Dashboard

There are 2 main components: frontend and backend. The frontend code is found in the "dashboard" folder in the "Software Dashboard" folder. The backend code is found in the "dashboardbackend" folder in the "Software Dashboard" folder.

The components of the frontend are as follows:

1. In dancedashboard/src/component/Charts:

   a. BarChartSet.vue - 
   
   b. BarChartTime.vue - 
   
   c. PieChart.vue - 
   
   d. PieChartStatic.vue - 
   
2. In dancedashboard/src/component:

   a. DancerInformation.vue - This vue file contains the code for the Dancers Information page, which shows 2 charts - Time Spent (minutes) vs Dancers and Number of Sets Done vs Dancers for each of the dancers for the current week.
   
   b. HowToUse.vue - This vue file contains the code for the User Guide that is present to help users in the event that they are unsure of what the 3 main pages (Real-time Dashboard, Past Dance Sets and Dancers Information) are meant for or how they should be used.
   
   c. PastDanceSets.vue - This vue file contains the code for the Past Dance Sets page, which shows tables and sync pie charts regarding all the past dance sets that has taken place so far.
   
   d. PersistentSideNavDrawer.vue - This vue file contains the code for the side navigation drawer.
   
   e. RealTimeDashboard.vue - This vue file contains the code for the Real-time Dashboard page.
   
The components of the backend are as follows:

1. In dancedashboardbackend:

   a. server.js - This Javascript file contains the backend code to connect to the database and to send data for all the pages, for example, parsing through the data received from comms external, sending the necessary data to the Real-time Dashboard page, sending all data pertaining to the past dance sets to the Past Dance Sets page, sending specific past dance sets data as specified by the user to the Past Dance Sets page, sending all data pertaining to how long each of the dancers have practised and the number of sets each of them have participated in the current week to the Dancers Information page, sending specific dancers information as specified by the user to the Dancers Information page and receiving the names of the dancers from the frontend.
   
