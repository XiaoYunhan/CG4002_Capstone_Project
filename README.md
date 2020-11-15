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
   a. DancerInformation.vue
   b. HowToUse.vue - 
   c. PastDanceSets.vue - 
   d. PersistentSideNavDrawer.vue - 
   e. RealTimeDashboard.vue - 
   
The components of the backend are as follows:
1. In dancedashboardbackend:
   a. server.js - 
