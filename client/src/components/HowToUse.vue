<template>
  <v-container>
    <div style="width: 20%; float: left">
      <psnd />
    </div>
    <div style="width: 80%; float: right">
      <VueFaqAccordion
        :items="myItems"
        activeColor="#2196F3"
        fontColor="#424242"
        bordercolor="#BDBDBD"
      />
    </div>
  </v-container>
</template>

<script>
import psnd from "./PersistentSideNavDrawer";
import VueFaqAccordion from "vue-faq-accordion";

export default {
  name: "HowToUse",

  components: {
    psnd,
    VueFaqAccordion,
  },
  data() {
    return {
      myItems: [
        {
          title: "What is the purpose of the Dancer Information page?",
          value:
            "The Dancer Information page is designed to help dance students and teachers alike keep track of the following:" +
            "<br/>1. How long each student has practised (in minutes) over a range of dates" +
            "<br/>2. The number of dance sets each student has participated in over a range of dates <br/>" +
            "<br/> By default, both charts reflect data for the current week. However, this can be modified. For more details, please refer to the second point of this page.",
          category: "Dancer Information",
        },
        {
          title: "How do I use the Dancer Information page?",
          value:
            "There are a few ways to use the Dancer Information page." +
            " <br> <br> <u><b> To view information pertaining to the current week so far</b></u> <br>- Do not enter anything into the" +
            " dropdown boxes at the top of the page. <br>- If some options are selected and you wish" +
            " to clear them, simply click on the 'X' icon that is present in the dropdown boxes and" +
            " then click on the green check icon that is present on the extreme right of the dropdown" +
            " boxes. <br><br> <u><b>To search for specific information</b></u> <br/><br/>" +
            "<b>1. To choose specific charts (Time Spent Practising Bar Chart or Number of Sets Done Bar Chart)</b> <br>" +
            "&nbsp;&nbsp;&nbsp;&nbsp;Click on the 'Chart Type' dropdown box and make a selection (Time Spent or Sets Done). <br><br>" +
            "<b>2. To observe information of specific dancer(s)</b><br>" +
            "&nbsp;&nbsp;&nbsp;&nbsp;Click on the 'Dancer(s)' page and choose the name(s) of the dancers. <br>" +
            "&nbsp;&nbsp;&nbsp;&nbsp;Multiple dancers may be selected. <br><br>" +
            "<b>3. To observe dance set(s) over a range of date(s)</b> <br>" +
            "&nbsp;&nbsp;&nbsp;&nbsp;Click on the 'Choose a Range of Dates' page and select the start date and end date. <br/>" +
            "&nbsp;&nbsp;&nbsp;&nbsp;A range of minimum 5 days must be provided.<br><br>" +
            "Points 1, 2 and 3 may be used in various combinations as needed. <br><br>" +
            "<u><b> How to submit the selections?</b></u> <br>" +
            "After entering the necessary data in the dropdown boxes, click on the green check icon that is" +
            " present on the extreme right of the dropdown boxes.",
          category: "Dancer Information",
        },
        {
          title: "What is the purpose of the Real-Time Dashboard?",
          value:
            "The Real-Time Dashboard is designed to help you, as dance students and dance teachers, observe the dance set that is happening live. Think of it as a dance class that can occur in a dance studio or in one's home. In this COVID-19 situation, we would like to provide an opportunity for dancers to be able to practice as a team without having to travel to a dance studio and come into close contact with others.",
          category: "Real-Time Dashboard",
        },
        {
          title: "What can I observe in the Real-Time Dashboard?",
          value:
            "Through the Real-Time Dashboard, you will be able to observe the following: <br/> <br/>" +
            "1. Predicted dance move <br/>" +
            "2. Predicted dancer positions (order of the names represents the positions of the dancers i.e. left, center or &nbsp;&nbsp;&nbsp;&nbsp;right)<br/>" +
            "3. A table showing these details for each of the dance moves:<br/>" +
            "&nbsp;&nbsp;&nbsp;&nbsp;a. Dance moves <br/>" +
            "&nbsp;&nbsp;&nbsp;&nbsp;b. Positions of the 3 dancers <br/>" +
            "&nbsp;&nbsp;&nbsp;&nbsp;c. Sync Delay in seconds, which is the difference in timing between the fastest and slowest dancer <br/>" +
            "&nbsp;&nbsp;&nbsp;&nbsp;d. In Sync?, which shows whether the dancers were in sync or not <br/>" +
            "4. A pie chart that shows the proportion of dance moves of the current dance set that the dancers are in sync &nbsp;&nbsp;&nbsp;&nbsp;for <br/> <br/>" +
            "Note: <br/>" +
            "1. If the delay between the fastest and slowest dancer is less than or equal to 1 second, the dancers are said &nbsp;&nbsp;&nbsp;&nbsp;to be in sync. This is because 1 beat is taken to be 1 second. <br/>" +
            "2. Points 1, 2 and 3 occurs for each dance move, while point 4 is continuously updated for each dance move &nbsp;&nbsp;&nbsp;&nbsp;of that set. <br/>" +
            '3. A dance set refers to a group of moves that starts with the "Start" move and ends with the "End" move.',
          category: "Real-Time Dashboard",
        },
        {
          title: "How do I use the Real-Time Dashboard?",
          value:
            "Before the start of the dance, select dancer 1, 2 and 3 from the dropdown boxes above. Ensure that no dancers are repeated in the selection." +
            " After that, simply wait for the data to stream in. <br/> If no dancer names are provided, the names from the previous set will be used (if available). <br/> <br/>" +
            "Once data starts coming in, the side navigation will be disabled to prevent users from leaving the page " +
            "and potentially losing access to real-time data. Once the 'End' move is performed, the side navigation will be enabled again.",
          category: "Real-Time Dashboard",
        },
        {
          title: "What is the purpose of the Past Dance Sets page?",
          value:
            "With the Past Dance Sets, you can do a post-performance review with your team or students." +
            " Details such as the positions of dancers, dance moves, difference in synchronisation are" +
            " provided. Along with that, the sync pie chart is provided for you to analyse the" +
            " performance of the team.",
          category: "Past Dance Sets",
        },
        {
          title: "How do I use the Past Dance Sets page?",
          value:
            "There are a few ways to use the Past Dance Sets page." +
            " <br> <br> <u><b> To observe all data</b></u> <br>- Do not enter anything into the" +
            " dropdown boxes at the top of the page. <br>- If some options are selected and you wish" +
            " to clear them, simply click on the 'X' icon that is present in the dropdown boxes and" +
            " then click on the green check icon that is present on the extreme right of the dropdown" +
            " boxes. <br><br> <u><b>To search for specific information</b></u> <br/><br/>" +
            "<b>1. To choose specific charts (Dance Table or Sync Chart)</b> <br>" +
            "&nbsp;&nbsp;&nbsp;&nbsp;Click on the 'Chart Type' dropdown box and make a selection. <br />" +
            '&nbsp;&nbsp;&nbsp;&nbsp;Selecting "Dance Table" provides you with the time of each dancer for each dance move in which the &nbsp;&nbsp;&nbsp;&nbsp;dancer started the movement.  <br><br>' +
            "<b>2. To observe data from specific dance sets</b> <br>" +
            "&nbsp;&nbsp;&nbsp;&nbsp;Click on the 'Dance Set(s)' dropdown box and choose the dance set(s) you would like to see." +
            "<br>&nbsp;&nbsp;&nbsp;&nbsp;You may choose multiple dance sets if you wish to do so. <br><br>" +
            "<b>3. To observe dance set(s) of specific dancer(s)</b><br>" +
            "&nbsp;&nbsp;&nbsp;&nbsp;Click on the 'Dancer(s)' page and choose the name(s) of the dancers. <br>" +
            "&nbsp;&nbsp;&nbsp;&nbsp;A maximum of 3 dancers" +
            " are allowed at any point. This is because the dancer(s) selected will be matched &nbsp;&nbsp;&nbsp;&nbspexactly to the" +
            " dancers in the dance sets available. <br><br>" +
            "<b>4. To observe dance set(s) on specific date(s)</b> <br>" +
            "&nbsp;&nbsp;&nbsp;&nbsp;Click on the 'Choose Date(s)' page" +
            " and select the date(s). <br>&nbsp;&nbsp;&nbsp;&nbsp;Multiple dates can be selected. <br><br>" +
            "Points 1, 2, 3 and 4 may be used in various combinations as needed. <br><br>" +
            "<u><b> How to submit the selections?</b></u> <br>" +
            "After entering the necessary data in the dropdown boxes, click on the green check icon that is" +
            " present on the extreme right of the dropdown boxes.",
          category: "Past Dance Sets",
        },
      ],
    };
  },
};
</script>
