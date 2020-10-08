<template>
  <v-container>
    <div style="width: 20%; float: left">
      <psnd />
    </div>
    <div style="width: 80%; float: right">
      <v-row>
        <v-col class="mx-auto" md="3">
          <v-select
            v-model="selectDancer_1"
            :items="dancer_1"
            item-text="name"
            item-value="value"
            filled
            label="Dancer 1"
            background-color="#A9D66E"
            prepend-icon="mdi-account"
            clearable
            dense
            color="#000000"
            @input="selectDancer1"
            @click:clear="clearDancer1"
          ></v-select>
        </v-col>
        <v-spacer />
        <v-col class="mx-auto" md="3">
          <v-select
            v-model="selectDancer_2"
            :items="dancer_2"
            item-text="name"
            item-value="value"
            filled
            label="Dancer 2"
            background-color="#00D19C"
            prepend-icon="mdi-account"
            clearable
            dense
            color="#000000"
            @input="selectDancer2"
            @click:clear="clearDancer2"
          ></v-select>
        </v-col>
        <v-spacer />
        <v-col class="mx-auto" md="3">
          <v-select
            v-model="selectDancer_3"
            :items="dancer_3"
            item-text="name"
            item-value="value"
            filled
            label="Dancer 3"
            background-color="#3DDBD8"
            prepend-icon="mdi-account"
            clearable
            dense
            color="#000000"
            @input="selectDancer3"
            @click:clear="clearDancer3"
          ></v-select>
        </v-col>
        <v-col class="mx-auto" md="1">
          <v-btn icon color="green" fab outlined @click="submit">
            <v-icon>mdi-check</v-icon>
          </v-btn>
        </v-col>
      </v-row>
      <!-- No Data available, No Names provided then no live dance class yet -->
      <template v-if="nodata && noNames">
        <v-card
          class="mx-auto"
          width="60%"
          height="160"
          color="#ECEFF1"
          rounded
        >
          <v-card-title>
            <v-row align="center" justify="center">
              <v-icon light large center>mdi-timer-sand</v-icon>
            </v-row>
          </v-card-title>
          <p class="text-center">
            There is no live dance class happening at the moment.
            <br />Please wait for a session to start. <br />Thank you!
          </p>
        </v-card>
      </template>
      <!-- No Data available, Names provided and no moves performed i.e. live dance starting soon -->
      <template v-if="nodata && !noNames && noMoves">
        <v-row justify="center">
          <v-progress-circular
            indeterminate
            :size="70"
            :width="7"
            color="#FF9800"
          />
        </v-row>
        <br />
        <p class="text-center">
          Please stand by for the live data. <br />Thank you!
        </p>
      </template>
      <!-- Names provided and Moves performed, which means a live dance set is happening -->
      <template v-else-if="!noNames && !noMoves">
        <h1 style="text-align: center; font-size: 50px; font-weight: bold">
          {{ danceMove }}
        </h1>
        <h1 style="text-align: center; font-size: 50px; font-weight: bold">
          {{ dancers }}
        </h1>
        <br />
        <v-row class="mx-auto">
          <v-card width="50%" class="mx-auto">
            <v-card-title>
              Dance Set {{ dance_set_table }}
              <v-spacer />
            </v-card-title>
            <v-data-table
              :headers="headers"
              :items="dances"
              disable-filtering
              disable-sort
            ></v-data-table>
          </v-card>
          <v-card width="30%" class="mx-auto">
            <v-card-title>Sync Dance Set {{ dance_set_pie }}</v-card-title>
            <p style="font-size: 8px; color: grey; text-align: justify">
              *This pie chart shows the number of dance moves the dancers are in
              sync for. Hover over the pink and blue in the pie chart to view
              the percentages.
            </p>
            <PieChart :chartData="datacollection" />
          </v-card>
        </v-row>
      </template>
    </div>
  </v-container>
</template>

<script>
import axios from "axios";
import psnd from "./PersistentSideNavDrawer";
import Swal from "sweetalert2";
import PieChart from "./Charts/PieChart";

export default {
  name: "RealTimeDashboard",

  components: {
    psnd,
    PieChart,
  },
  data: function () {
    return {
      headers: [
        { text: "Dance Position", value: "dance_position" },
        { text: "Left Position", value: "left_position" },
        { text: "Center Position", value: "center_position" },
        { text: "Right Position", value: "right_position" },
        {
          text: "Difference in timing (seconds)",
          value: "diff",
        },
      ],
      dances: [],
      selectDancer_1: null,
      selectDancer_2: null,
      selectDancer_3: null,
      dancer_1: [
        { name: "Jingxuan", value: "Jingxuan" },
        { name: "Karan", value: "Karan" },
        { name: "Kexin", value: "Kexin" },
        { name: "Sarah", value: "Sarah" },
        { name: "Tristy", value: "Tristy" },
        { name: "Yunhan", value: "Yunhan" },
      ],
      dancer_2: [
        { name: "Jingxuan", value: "Jingxuan" },
        { name: "Karan", value: "Karan" },
        { name: "Kexin", value: "Kexin" },
        { name: "Sarah", value: "Sarah" },
        { name: "Tristy", value: "Tristy" },
        { name: "Yunhan", value: "Yunhan" },
      ],
      dancer_3: [
        { name: "Jingxuan", value: "Jingxuan" },
        { name: "Karan", value: "Karan" },
        { name: "Kexin", value: "Kexin" },
        { name: "Sarah", value: "Sarah" },
        { name: "Tristy", value: "Tristy" },
        { name: "Yunhan", value: "Yunhan" },
      ],
      nodata: true,
      noNames: true,
      noMoves: true,
      danceMove: null,
      dancers: null,
      dance_set_table: null,
      dance_set_pie: null,
      no_sync: null,
      yes_sync: null,
      datacollection: {
        labels: ["Yes", "No"],
        datasets: [
          {
            borderWidth: 1,
            borderColor: ["rgba(245, 66, 158, 1)", "rgba(66, 194, 245, 1)"],
            backgroundColor: ["rgba(245, 66, 158, 1)", "rgba(66, 194, 245, 1)"],
            data: null,
          },
        ],
      },
    };
  },

  sockets: {
    connect() {
      // connect to the socket
      console.log("This is the frontend socket");
    },
    predictedData(data) {
      // get predicted dance move and dancers in the 3 positions for each dance move
      console.log("Predicted Data: " + data);
      var data_split = data.split(".");
      this.danceMove = data_split[0];
      this.dancers = data_split[1];
    },
    dataNotAvailable(data) {
      // when data is coming in and not End move, data is false, so nodata is set to false
      // when End move, data is true, so nodata is set to true to signal the end of a dance set
      this.nodata = data;
      this.noMoves = false;
      console.log("nodata: " + this.nodata);
    },
    newTableData(data) {
      // get the data needed for the table
      // dance set number, dance move, dancers in the 3 positions
      // and difference in timing between fastest and slowest dancer
      // psuhed into an array to show all the moves till current move
      var data_intermediate = data.split(",");
      if (data_intermediate[0] != this.dance_set_table) {
        this.dances = [];
      }
      this.dance_set_table = data_intermediate[0];
      var dance_move = data_intermediate[1];
      var left_dancer = data_intermediate[2];
      var center_dancer = data_intermediate[3];
      var right_dancer = data_intermediate[4];
      var difference = data_intermediate[5];
      var dance_array = {
        dance_position: dance_move,
        left_position: left_dancer,
        center_position: center_dancer,
        right_position: right_dancer,
        diff: difference,
      };
      this.dances.push(dance_array);
      console.log(data);
    },
    sendNewPieData(data) {
      // get the latest data for pie chart
      // contains number of moves for which the dancers are in sync for
      // and the number of moves the dancers are not in sync for
      console.log(data);
      var data_pie_intermediate = data.split(",");
      this.dance_set_pie = data_pie_intermediate[0];
      this.yes_sync = parseInt(data_pie_intermediate[1]);
      this.no_sync = parseInt(data_pie_intermediate[2]);
      var new_array = [this.yes_sync, this.no_sync];
      this.datacollection = {
        labels: ["Yes", "No"],
        datasets: [
          {
            borderWidth: 1,
            borderColor: ["rgba(245, 66, 158, 1)", "rgba(66, 194, 245, 1)"],
            backgroundColor: ["rgba(245, 66, 158, 1)", "rgba(66, 194, 245, 1)"],
            data: new_array,
          },
        ],
      };
    },
  },

  methods: {
    selectDancer1: function () {
      console.log(this.selectDancer_1);
    },
    selectDancer2: function () {
      console.log(this.selectDancer_2);
    },
    selectDancer3: function () {
      console.log(this.selectDancer_3);
    },
    clearDancer1: function () {
      this.selectDancer_1 = null;
    },
    clearDancer2: function () {
      this.selectDancer_2 = null;
    },
    clearDancer3: function () {
      this.selectDancer_3 = null;
    },
    checkDancers: function () {
      if (
        (this.selectDancer_1 == null ||
          this.selectDancer_1 == undefined ||
          this.selectDancer_1 == "-") &&
        (this.selectDancer_2 == null ||
          this.selectDancer_2 == undefined ||
          this.selectDancer_2 == "-") &&
        (this.selectDancer_3 == null ||
          this.selectDancer_3 == undefined ||
          this.selectDancer_3 == "-")
      ) {
        this.noNames = true;
        Swal.fire({
          icon: "error",
          title: "Oops...",
          text: "Please select at least 1 dancer",
        });
      } else {
        if (
          this.selectDancer_1 != null &&
          this.selectDancer_1 != undefined &&
          this.selectDancer_1 != "-" &&
          this.selectDancer_2 != null &&
          this.selectDancer_2 != undefined &&
          this.selectDancer_2 != "-" &&
          this.selectDancer_3 != null &&
          this.selectDancer_3 != undefined &&
          this.selectDancer_3 != "-" &&
          this.selectDancer_1 == this.selectDancer_2 &&
          this.selectDancer_2 == this.selectDancer_3
        ) {
          this.noNames = true;
          Swal.fire({
            icon: "error",
            title: "Oops...",
            text: "Dancers 1, 2 and 3 cannot be the same!",
          });
        } else if (
          this.selectDancer_1 != null &&
          this.selectDancer_1 != undefined &&
          this.selectDancer_1 != "-" &&
          this.selectDancer_2 != null &&
          this.selectDancer_2 != undefined &&
          this.selectDancer_2 != "-" &&
          this.selectDancer_1 == this.selectDancer_2
        ) {
          this.noNames = true;
          Swal.fire({
            icon: "error",
            title: "Oops...",
            text: "Dancers 1 and 2 cannot be the same!",
          });
        } else if (
          this.selectDancer_1 != null &&
          this.selectDancer_1 != undefined &&
          this.selectDancer_1 != "-" &&
          this.selectDancer_3 != null &&
          this.selectDancer_3 != undefined &&
          this.selectDancer_3 != "-" &&
          this.selectDancer_1 == this.selectDancer_3
        ) {
          this.noNames = true;
          Swal.fire({
            icon: "error",
            title: "Oops...",
            text: "Dancers 1 and 3 cannot be the same!",
          });
        } else if (
          this.selectDancer_2 != null &&
          this.selectDancer_2 != undefined &&
          this.selectDancer_2 != "-" &&
          this.selectDancer_3 != null &&
          this.selectDancer_3 != undefined &&
          this.selectDancer_3 != "-" &&
          this.selectDancer_2 == this.selectDancer_3
        ) {
          this.noNames = true;
          Swal.fire({
            icon: "error",
            title: "Oops...",
            text: "Dancers 2 and 3 cannot be the same!",
          });
        } else {
          if (this.selectDancer_1 == null) {
            this.selectDancer_1 = "-";
            console.log("Dancer 1: " + this.selectDancer_1);
          }
          if (this.selectDancer_2 == null) {
            this.selectDancer_2 = "-";
            console.log("Dancer 2: " + this.selectDancer_2);
          }
          if (this.selectDancer_3 == null) {
            this.selectDancer_3 = "-";
            console.log("Dancer 3: " + this.selectDancer_3);
          }
          Swal.fire({
            icon: "success",
            title: "Submit Successful!",
          });
          this.noNames = false;
        }
      }
    },
    submit: function () {
      // send the dancer names to the server to use in the data coming in
      this.checkDancers();
      const jsonDancers =
        '{ "dancer1":"' +
        this.selectDancer_1 +
        '", "dancer2":"' +
        this.selectDancer_2 +
        '", "dancer3":"' +
        this.selectDancer_3 +
        '" }';
      var dancers = JSON.parse(jsonDancers);
      console.log("JSON Dancers: " + JSON.stringify(dancers));
      axios
        .post("/dashboard/real-time-dashboard", {
          realTimeDashboard: dancers,
        })
        .then((response) => {
          console.log(response.data);
        });
    },
  },
};
</script>
