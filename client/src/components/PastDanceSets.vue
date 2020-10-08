<template>
  <v-container>
    <div style="width: 20%; float: left">
      <psnd />
    </div>
    <div style="width: 80%; float: right">
      <v-row>
        <v-col class="mx-auto" md="3">
          <v-select
            v-model="selectedChart"
            :items="chartType"
            item-text="name"
            item-value="value"
            filled
            label="Chart Type"
            background-color="#A9D66E"
            prepend-icon="mdi-view-dashboard"
            clearable
            dense
            color="#000000"
            @input="selectChart"
            @click:clear="clearCharts"
          />
        </v-col>
        <v-col class="mx-auto">
          <v-select
            v-model="search"
            :items="danceSetNum"
            item-text="name"
            item-value="value"
            filled
            label="Dance Set(s)"
            background-color="#76D57C"
            prepend-icon="mdi-magnify"
            clearable
            multiple
            dense
            color="#000000"
            @input="selectDanceSet"
            @click:clear="clearDanceSet"
          />
        </v-col>
        <v-col class="mx-auto">
          <v-select
            v-model="selectedDancers"
            :items="dancers"
            item-text="name"
            item-value="value"
            filled
            label="Dancer(s)"
            background-color="#00D19C"
            prepend-icon="mdi-account-multiple"
            clearable
            multiple
            dense
            color="#000000"
            @input="selectDancers"
            @click:clear="clearDancers"
          />
        </v-col>
        <v-col class="mx-auto" md="3">
          <v-menu
            v-model="dateMenu"
            :nudge-right="40"
            :close-on-content-click="false"
            transition="scale-transition"
            offset-y
            max-width="290px"
            min-width="290px"
          >
            <template v-slot:activator="{ on }">
              <v-text-field
                label="Choose Date(s)"
                :value="dateDisp"
                v-on="on"
                clearable
                prepend-icon="mdi-calendar"
                background-color="#3DDBD8"
                filled
                dense
                color="#000000"
                @click:clear="clearDates"
              />
            </template>
            <v-date-picker
              v-model="dateVal"
              @click:date="selectDates"
              :max="getEndDate"
              multiple
            />
          </v-menu>
        </v-col>
        <v-col class="mx-auto" md="1">
          <v-btn icon color="green" fab outlined @click="submit">
            <v-icon>mdi-check</v-icon>
          </v-btn>
        </v-col>
      </v-row>
      <p>{{ numOfRecords }} result(s) found</p>
      <!-- if page is loaded and there is table and pie chart data, display both -->
      <template v-if="loaded && haveTable && havePie">
        <v-list v-for="(number, i) in danceSetArr" :key="number">
          <v-row>
            <v-card width="65%">
              <v-card-title>
                Dance Set {{ number }}
                <br />
                {{ tableDate[i] }} {{ danceTimeArray[i] }}
                <v-spacer></v-spacer>
              </v-card-title>
              <v-data-table
                :headers="headers"
                :items="getDances(number)"
              ></v-data-table>
            </v-card>
            <v-spacer />
            <v-card width="30%">
              <v-card-title>
                Sync Dance Set {{ number }}
                <br />
                {{ pieDate[i] }}
                <v-spacer></v-spacer>
              </v-card-title>
              <p style="font-size: 8px; color: grey; text-align: justify">
                *This pie chart shows the number of dance moves the dancers are
                in sync for. Hover over the pink and blue in the pie chart to
                view the percentages.
              </p>
              <PieChartStatic
                :chartdata="getChartData(number)"
                :options="chartOptions"
              />
            </v-card>
          </v-row>
        </v-list>
      </template>
      <!-- if page is loaded and there is table data but no pie chart data, display table only -->
      <template v-else-if="loaded && haveTable && !havePie">
        <v-list v-for="(number, i) in danceSetArr" :key="number">
          <v-card width="100%">
            <v-card-title>
              Dance Set {{ number }}
              <br />
              {{ tableDate[i] }} {{ danceTimeArray[i] }}
              <v-spacer></v-spacer>
            </v-card-title>
            <v-data-table
              :headers="headersTableOnly"
              :items="getDancesTableOnly(number)"
            ></v-data-table>
          </v-card>
        </v-list>
      </template>
      <!-- if page is loaded and there is pie chart data but no table data, display pie chart -->
      <template v-else-if="loaded && havePie && !haveTable">
        <v-list v-for="(number, i) in danceSetArr" :key="number">
          <v-row>
            <v-card width="49%" class="mx-auto">
              <v-card-title>
                Sync Dance Set {{ number }}
                <br />
                {{ pieDate[i] }}
                <v-spacer />
              </v-card-title>
              <p style="font-size: 8px; color: grey; text-align: justify">
                *This pie chart shows the number of dance moves the dancers are
                in sync for. Hover over the pink and blue in the pie chart to
                view the percentages.
              </p>
              <PieChartStatic
                :chartdata="getChartData(number)"
                :options="chartOptions"
              />
            </v-card>
          </v-row>
        </v-list>
      </template>
      <!-- if page is loaded and there is no table and pie chart data, show no data available message -->
      <template v-else-if="loaded && !haveTable && !havePie">
        <v-card
          class="mx-auto"
          width="60%"
          height="160"
          color="#ECEFF1"
          rounded
        >
          <v-card-title>
            <v-row align="center" justify="center">
              <v-icon light large center>mdi-emoticon-sad</v-icon>
            </v-row>
          </v-card-title>
          <p class="text-center">
            What you are looking for cannot be found.
            <br />Sorry!
          </p>
        </v-card>
      </template>
      <template v-else>
        <v-row justify="center">
          <v-progress-circular
            indeterminate
            :size="70"
            :width="7"
            color="#FF9800"
          />
        </v-row>
      </template>
    </div>
  </v-container>
</template>

<script>
import axios from "axios";
import psnd from "./PersistentSideNavDrawer";
import Swal from "sweetalert2";
import PieChartStatic from "./Charts/PieChartStatic";

export default {
  name: "PastDanceSets",

  components: {
    psnd,
    PieChartStatic,
  },
  data: () => ({
    numDanceSet: null,
    search: null,
    selectedChart: null,
    selectedDancers: null,
    chartType: [
      { name: "Dance Table", value: "Table" },
      { name: "Sync Chart", value: "Pie" },
    ],
    dancers: [
      { name: "Jingxuan", value: "Jingxuan" },
      { name: "Karan", value: "Karan" },
      { name: "Kexin", value: "Kexin" },
      { name: "Sarah", value: "Sarah" },
      { name: "Tristy", value: "Tristy" },
      { name: "Yunhan", value: "Yunhan" },
    ],
    headers: [
      { text: "No.", value: "move_number" },
      { text: "Dance Move", value: "dance_move" },
      { text: "Left Dancer", value: "left_dancer" },
      { text: "Center Dancer", value: "center_dancer" },
      { text: "Right Dancer", value: "right_dancer" },
      {
        text: "Sync Delay (seconds)",
        value: "diff",
      },
      {
        text: "In Sync?",
        value: "sync",
      },
    ],
    headersTableOnly: [
      { text: "No.", value: "move_number" },
      { text: "Dance Move", value: "dance_move" },
      { text: "Time (Left)", value: "left_time" },
      { text: "Left Dancer", value: "left_dancer" },
      { text: "Time (Center)", value: "center_time" },
      { text: "Center Dancer", value: "center_dancer" },
      { text: "Time (Right)", value: "right_time" },
      { text: "Right Dancer", value: "right_dancer" },
      {
        text: "Sync Delay (seconds)",
        value: "diff",
      },
      {
        text: "In Sync?",
        value: "sync",
      },
    ],
    dances: [],
    loaded: false,
    danceSetNum: [],
    dateMenu: false,
    dateVal: null,
    getEndDate: new Date().toISOString().substr(0, 10),
    tableResponseLength: null,
    pieResponseLength: null,
    pie: [],
    pieDate: [],
    tableDate: [],
    danceSetArr: [],
    numOfRecords: null,
    danceTimeArray: [],
    startTime: null,
    endTime: null,
    havePie: true,
    haveTable: true,
    chartOptions: {
      legend: {
        display: true,
      },
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        datalabels: {
          color: "white",
          textAlign: "center",
          font: {
            weight: "bold",
            size: 16,
          },
        },
      },
      tooltips: {
        callbacks: {
          label: function (tooltipItem, data) {
            var allData = data.datasets[tooltipItem.datasetIndex].data;
            var tooltipLabel = data.labels[tooltipItem.index];
            var tooltipData = allData[tooltipItem.index];
            var total = 0;
            for (var i in allData) {
              total += allData[i];
            }
            var tooltipPercentage = Math.round((tooltipData / total) * 100);
            return (
              tooltipLabel +
              ": " +
              tooltipData +
              " (" +
              tooltipPercentage +
              "%)"
            );
          },
        },
      },
    },
  }),
  computed: {
    dateDisp() {
      return this.dateVal;
    },
  },
  methods: {
    clearCharts: function () {
      this.selectedChart = null;
    },
    selectChart: function () {
      if (this.selectedChart != null) {
        if (this.selectedChart === "Table") {
          console.log("get data from Dance");
        } else if (this.selectedChart === "Pie") {
          console.log("get data from Sync");
        }
      } else {
        console.log("display all dancers");
      }
    },
    clearDanceSet: function () {
      this.search = null;
    },
    selectDanceSet: function () {
      if (this.search != null && this.search.length > 0) {
        var length = this.search.length;
        for (var k = 0; k < length; k++) {
          console.log(this.search[k]);
        }
      } else {
        this.search = null;
      }
    },
    clearDancers: function () {
      this.selectedDancers = null;
    },
    selectDancers: function () {
      if (this.selectedDancers != null && this.selectedDancers.length > 0) {
        var length = this.selectedDancers.length;
        if (length > 3) {
          Swal.fire({
            icon: "error",
            title: "Oops...",
            text: "A maximum of 3 dancers are allowed!",
          });
          this.selectedDancers.pop();
        }
        for (var i = 0; i < this.selectedDancers.length; i++) {
          console.log(this.selectedDancers[i]);
        }
      } else {
        this.selectedDancers = null;
      }
    },
    clearDates: function () {
      this.dateVal = null;
    },
    selectDates: function () {
      if (this.dateVal != null) {
        console.log(this.dateVal.length);
        for (var j = 0; j < this.dateVal.length; j++) {
          console.log(this.dateVal[j]);
        }
      } else {
        console.log("display all dates");
      }
    },
    submit: function () {
      // data in selectedDancers are to be taken as AND i.e. the dance sets must contain the dancer names
      // data in dateVal is to be taken as OR
      // data in search is to be taken as OR
      // selectedChart refers to the DB Table (Table: Dance, Pie: Sync)
      // SELECT * FROM Dance/Sync WHERE (dancerNames='%this.selectedDancers%') i.e. Pattern Matching
      //  AND (this.dateVal) AND (this.search)

      console.log("Dancers: " + this.selectedDancers);
      if (this.selectedDancers != null) {
        this.selectedDancers = this.selectedDancers.sort();
        var dancers = '"';
        for (var i = 0; i < this.selectedDancers.length; i++) {
          dancers += this.selectedDancers[i] + ",";
        }
        dancers = dancers.slice(0, -1);
        dancers += '"';
      } else {
        dancers = null;
      }

      if (this.dateVal != null) {
        this.dateVal = this.dateVal.sort();
        var dates = '"';
        for (var j = 0; j < this.dateVal.length; j++) {
          dates += this.dateVal[j] + ",";
        }
        dates = dates.slice(0, -1);
        dates += '"';
      } else {
        dates = null;
      }

      if (this.search != null) {
        this.search = this.search.sort();
        var searchDanceSets = '"';
        for (var k = 0; k < this.search.length; k++) {
          searchDanceSets += this.search[k] + ",";
        }
        searchDanceSets = searchDanceSets.slice(0, -1);
        searchDanceSets += '"';
      } else {
        searchDanceSets = null;
      }

      const pastDataToSend =
        '{"chart":"' +
        this.selectedChart +
        '", ' +
        '"dancers":' +
        dancers +
        ', "dates":' +
        dates +
        ', "search":' +
        searchDanceSets +
        "}";
      // console.log(pastDataToSend);
      var jsonPastDataToSend = JSON.parse(pastDataToSend);
      console.log("Past Data To Send: " + JSON.stringify(jsonPastDataToSend));

      axios
        .post("/dashboard/past-data", {
          pastData: jsonPastDataToSend,
        })
        .then((response) => {
          this.dances = [];
          this.tableDate = [];
          this.danceSetArr = [];
          this.pie = [];
          this.pieDate = [];
          this.danceTimeArray = [];

          if (
            response.data.tableData.length > 0 &&
            (response.data.pieData.length == undefined ||
              response.data.pieData.length == 0)
          ) {
            // if have table data but no pie chart data, then display only table
            this.haveTable = true;
            this.havePie = false;
            this.tableResponseLength = response.data.tableData.length;

            for (var j = 0; j < this.tableResponseLength; j++) {
              var date_utc = new Date(response.data.tableData[j].dates);
              var date_convert_to_sgt = date_utc.toString();
              var split_sgt_date_by_space = date_convert_to_sgt.split(" ");
              var formatted_date =
                split_sgt_date_by_space[2] +
                " " +
                split_sgt_date_by_space[1] +
                " " +
                split_sgt_date_by_space[3];
              if (response.data.tableData[j].move_number == 1) {
                this.tableDate.push(formatted_date);
                this.danceSetArr.push(response.data.tableData[j].dance_set);
              }
              if (response.data.tableData[j].dance_move == "Start") {
                if (
                  response.data.tableData[j].left_time != null &&
                  response.data.tableData[j].center_time != null &&
                  response.data.tableData[j].right_time != null
                ) {
                  if (
                    response.data.tableData[j].left_time <=
                      response.data.tableData[j].center_time &&
                    response.data.tableData[j].left_time <=
                      response.data.tableData[j].right_time
                  ) {
                    this.startTime = response.data.tableData[j].left_time;
                  } else if (
                    response.data.tableData[j].center_time <=
                      response.data.tableData[j].left_time &&
                    response.data.tableData[j].center_time <=
                      response.data.tableData[j].right_time
                  ) {
                    this.startTime = response.data.tableData[j].center_time;
                  } else if (
                    response.data.tableData[j].right_time <=
                      response.data.tableData[j].left_time &&
                    response.data.tableData[j].right_time <=
                      response.data.tableData[j].center_time
                  ) {
                    this.startTime = response.data.tableData[j].right_time;
                  }
                } else {
                  if (
                    response.data.tableData[j].left_time != null &&
                    response.data.tableData[j].center_time != null
                  ) {
                    if (
                      response.data.tableData[j].left_time <=
                      response.data.tableData[j].center_time
                    ) {
                      this.startTime = response.data.tableData[j].left_time;
                    } else {
                      this.startTime = response.data.tableData[j].center_time;
                    }
                  } else if (
                    response.data.tableData[j].left_time != null &&
                    response.data.tableData[j].right_time != null
                  ) {
                    if (
                      response.data.tableData[j].left_time <=
                      response.data.tableData[j].right_time
                    ) {
                      this.startTime = response.data.tableData[j].left_time;
                    } else {
                      this.startTime = response.data.tableData[j].right_time;
                    }
                  } else if (
                    response.data.tableData[j].center_time != null &&
                    response.data.tableData[j].right_time != null
                  ) {
                    if (
                      response.data.tableData[j].center_time <=
                      response.data.tableData[j].right_time
                    ) {
                      this.startTime = response.data.tableData[j].center_time;
                    } else {
                      this.startTime = response.data.tableData[j].right_time;
                    }
                  } else if (response.data.tableData[j].left_time != null) {
                    this.startTime = response.data.tableData[j].left_time;
                  } else if (response.data.tableData[j].center_time != null) {
                    this.startTime = response.data.tableData[j].center_time;
                  } else if (response.data.tableData[j].right_time != null) {
                    this.startTime = response.data.tableData[j].right_time;
                  }
                }
                var startTime_split = this.startTime.split(":");
                if (startTime_split[0] == "24") {
                  startTime_split[0] == "00";
                }
                this.startTime = startTime_split[0] + ":" + startTime_split[1];
              } else if (response.data.tableData[j].dance_move == "End") {
                if (
                  response.data.tableData[j].left_time != null &&
                  response.data.tableData[j].center_time != null &&
                  response.data.tableData[j].right_time != null
                ) {
                  if (
                    response.data.tableData[j].left_time <=
                      response.data.tableData[j].center_time &&
                    response.data.tableData[j].left_time <=
                      response.data.tableData[j].right_time
                  ) {
                    this.endTime = response.data.tableData[j].left_time;
                  } else if (
                    response.data.tableData[j].center_time <=
                      response.data.tableData[j].left_time &&
                    response.data.tableData[j].center_time <=
                      response.data.tableData[j].right_time
                  ) {
                    this.endTime = response.data.tableData[j].center_time;
                  } else if (
                    response.data.tableData[j].right_time <=
                      response.data.tableData[j].left_time &&
                    response.data.tableData[j].right_time <=
                      response.data.tableData[j].center_time
                  ) {
                    this.endTime = response.data.tableData[j].right_time;
                  }
                } else {
                  if (
                    response.data.tableData[j].left_time != null &&
                    response.data.tableData[j].center_time != null
                  ) {
                    if (
                      response.data.tableData[j].left_time <=
                      response.data.tableData[j].center_time
                    ) {
                      this.endTime = response.data.tableData[j].left_time;
                    } else {
                      this.endTime = response.data.tableData[j].center_time;
                    }
                  } else if (
                    response.data.tableData[j].left_time != null &&
                    response.data.tableData[j].right_time != null
                  ) {
                    if (
                      response.data.tableData[j].left_time <=
                      response.data.tableData[j].right_time
                    ) {
                      this.endTime = response.data.tableData[j].left_time;
                    } else {
                      this.endTime = response.data.tableData[j].right_time;
                    }
                  } else if (
                    response.data.tableData[j].center_time != null &&
                    response.data.tableData[j].right_time != null
                  ) {
                    if (
                      response.data.tableData[j].center_time <=
                      response.data.tableData[j].right_time
                    ) {
                      this.endTime = response.data.tableData[j].center_time;
                    } else {
                      this.endTime = response.data.tableData[j].right_time;
                    }
                  } else if (response.data.tableData[j].left_time != null) {
                    this.endTime = response.data.tableData[j].left_time;
                  } else if (response.data.tableData[j].center_time != null) {
                    this.endTime = response.data.tableData[j].center_time;
                  } else if (response.data.tableData[j].right_time != null) {
                    this.endTime = response.data.tableData[j].right_time;
                  }
                }
                var endTime_split = this.endTime.split(":");
                if (endTime_split[0] == "24") {
                  endTime_split[0] == "00";
                }
                this.endTime = endTime_split[0] + ":" + endTime_split[1];
                var timeOfDance = this.startTime + " - " + this.endTime;
                this.danceTimeArray.push(timeOfDance);
              }

              if (response.data.tableData[j].left_time == null) {
                response.data.tableData[j].left_time = "-";
              }

              if (response.data.tableData[j].center_time == null) {
                response.data.tableData[j].center_time = "-";
              }

              if (response.data.tableData[j].right_time == null) {
                response.data.tableData[j].right_time = "-";
              }

              var danceArr = {
                dance_set: response.data.tableData[j].dance_set,
                move_number: response.data.tableData[j].move_number,
                date: formatted_date,
                dance_move: response.data.tableData[j].dance_move,
                left_time: response.data.tableData[j].left_time,
                left_dancer: response.data.tableData[j].left_dancer,
                center_time: response.data.tableData[j].center_time,
                center_dancer: response.data.tableData[j].center_dancer,
                right_time: response.data.tableData[j].right_time,
                right_dancer: response.data.tableData[j].right_dancer,
                diff: response.data.tableData[j].difference,
                sync: response.data.tableData[j].sync,
              };
              this.dances.push(danceArr);
            }
          } else if (
            response.data.pieData.length > 0 &&
            (response.data.tableData.length == undefined ||
              response.data.tableData.length == 0)
          ) {
            // if have only pie chart data and no table data, then display only pie charts
            this.havePie = true;
            this.haveTable = false;
            this.pieResponseLength = response.data.pieData.length;
            for (var k = 0; k < this.pieResponseLength; k++) {
              var pie_date = new Date(response.data.pieData[k].dates);
              var pie_date_sgt = pie_date.toString();
              var pie_date_split_by_space = pie_date_sgt.split(" ");
              var pie_date_split =
                pie_date_split_by_space[2] +
                " " +
                pie_date_split_by_space[1] +
                " " +
                pie_date_split_by_space[3];
              this.pieDate.push(pie_date_split);
              this.danceSetArr.push(response.data.pieData[k].dance_set);
              var pieArr = {
                dance_set: response.data.pieData[k].dance_set,
                date: pie_date_split,
                yes_sync: response.data.pieData[k].yes_sync,
                no_sync: response.data.pieData[k].no_sync,
              };
              this.pie.push(pieArr);
            }
            // console.log(this.pie);
          } else if (
            (response.data.pieData.length == undefined &&
              response.data.tableData.length == undefined) ||
            (response.data.pieData.length == 0 &&
              response.data.tableData.length == 0)
          ) {
            // if not table and no pie chart data, then set haveTable and havePie to false
            // to display no data available message
            this.haveTable = false;
            this.havePie = false;
          } else {
            // if have both table and pie chart data, then display both
            this.haveTable = true;
            this.havePie = true;
            this.tableResponseLength = response.data.tableData.length;
            for (var m = 0; m < this.tableResponseLength; m++) {
              var dates = new Date(response.data.tableData[m].dates);
              var sgt_date = dates.toString();
              var split_date_by_space = sgt_date.split(" ");
              var split_date =
                split_date_by_space[2] +
                " " +
                split_date_by_space[1] +
                " " +
                split_date_by_space[3];
              if (response.data.tableData[m].move_number == 1) {
                this.tableDate.push(split_date);
                this.danceSetArr.push(response.data.tableData[m].dance_set);
              }
              if (response.data.tableData[m].dance_move == "Start") {
                if (
                  response.data.tableData[m].left_time != null &&
                  response.data.tableData[m].center_time != null &&
                  response.data.tableData[m].right_time != null
                ) {
                  if (
                    response.data.tableData[m].left_time <=
                      response.data.tableData[m].center_time &&
                    response.data.tableData[m].left_time <=
                      response.data.tableData[m].right_time
                  ) {
                    this.startTime = response.data.tableData[m].left_time;
                  } else if (
                    response.data.tableData[m].center_time <=
                      response.data.tableData[m].left_time &&
                    response.data.tableData[m].center_time <=
                      response.data.tableData[m].right_time
                  ) {
                    this.startTime = response.data.tableData[m].center_time;
                  } else if (
                    response.data.tableData[m].right_time <=
                      response.data.tableData[m].left_time &&
                    response.data.tableData[m].right_time <=
                      response.data.tableData[m].center_time
                  ) {
                    this.startTime = response.data.tableData[m].right_time;
                  }
                } else {
                  if (
                    response.data.tableData[m].left_time != null &&
                    response.data.tableData[m].center_time != null
                  ) {
                    if (
                      response.data.tableData[m].left_time <=
                      response.data.tableData[m].center_time
                    ) {
                      this.startTime = response.data.tableData[m].left_time;
                    } else {
                      this.startTime = response.data.tableData[m].center_time;
                    }
                  } else if (
                    response.data.tableData[m].left_time != null &&
                    response.data.tableData[m].right_time != null
                  ) {
                    if (
                      response.data.tableData[m].left_time <=
                      response.data.tableData[m].right_time
                    ) {
                      this.startTime = response.data.tableData[m].left_time;
                    } else {
                      this.startTime = response.data.tableData[m].right_time;
                    }
                  } else if (
                    response.data.tableData[m].center_time != null &&
                    response.data.tableData[m].right_time != null
                  ) {
                    if (
                      response.data.tableData[m].center_time <=
                      response.data.tableData[m].right_time
                    ) {
                      this.startTime = response.data.tableData[m].center_time;
                    } else {
                      this.startTime = response.data.tableData[m].right_time;
                    }
                  } else if (response.data.tableData[m].left_time != null) {
                    this.startTime = response.data.tableData[m].left_time;
                  } else if (response.data.tableData[m].center_time != null) {
                    this.startTime = response.data.tableData[m].center_time;
                  } else if (response.data.tableData[m].right_time != null) {
                    this.startTime = response.data.tableData[m].right_time;
                  }
                }
                startTime_split = this.startTime.split(":");
                if (startTime_split[0] == "24") {
                  startTime_split[0] == "00";
                }
                this.startTime = startTime_split[0] + ":" + startTime_split[1];
              } else if (response.data.tableData[m].dance_move == "End") {
                if (
                  response.data.tableData[m].left_time != null &&
                  response.data.tableData[m].center_time != null &&
                  response.data.tableData[m].right_time != null
                ) {
                  if (
                    response.data.tableData[m].left_time <=
                      response.data.tableData[m].center_time &&
                    response.data.tableData[m].left_time <=
                      response.data.tableData[m].right_time
                  ) {
                    this.endTime = response.data.tableData[m].left_time;
                  } else if (
                    response.data.tableData[m].center_time <=
                      response.data.tableData[m].left_time &&
                    response.data.tableData[m].center_time <=
                      response.data.tableData[m].right_time
                  ) {
                    this.endTime = response.data.tableData[m].center_time;
                  } else if (
                    response.data.tableData[m].right_time <=
                      response.data.tableData[m].left_time &&
                    response.data.tableData[m].right_time <=
                      response.data.tableData[m].center_time
                  ) {
                    this.endTime = response.data.tableData[m].right_time;
                  }
                } else {
                  if (
                    response.data.tableData[m].left_time != null &&
                    response.data.tableData[m].center_time != null
                  ) {
                    if (
                      response.data.tableData[m].left_time <=
                      response.data.tableData[m].center_time
                    ) {
                      this.endTime = response.data.tableData[m].left_time;
                    } else {
                      this.endTime = response.data.tableData[m].center_time;
                    }
                  } else if (
                    response.data.tableData[m].left_time != null &&
                    response.data.tableData[m].right_time != null
                  ) {
                    if (
                      response.data.tableData[m].left_time <=
                      response.data.tableData[m].right_time
                    ) {
                      this.endTime = response.data.tableData[m].left_time;
                    } else {
                      this.endTime = response.data.tableData[m].right_time;
                    }
                  } else if (
                    response.data.tableData[m].center_time != null &&
                    response.data.tableData[m].right_time != null
                  ) {
                    if (
                      response.data.tableData[m].center_time <=
                      response.data.tableData[m].right_time
                    ) {
                      this.endTime = response.data.tableData[m].center_time;
                    } else {
                      this.endTime = response.data.tableData[m].right_time;
                    }
                  } else if (response.data.tableData[m].left_time != null) {
                    this.endTime = response.data.tableData[m].left_time;
                  } else if (response.data.tableData[m].center_time != null) {
                    this.endTime = response.data.tableData[m].center_time;
                  } else if (response.data.tableData[m].right_time != null) {
                    this.endTime = response.data.tableData[m].right_time;
                  }
                }
                endTime_split = this.endTime.split(":");
                if (endTime_split[0] == "24") {
                  endTime_split[0] == "00";
                }
                this.endTime = endTime_split[0] + ":" + endTime_split[1];
                timeOfDance = this.startTime + " - " + this.endTime;
                this.danceTimeArray.push(timeOfDance);
              }

              if (response.data.tableData[m].left_time == null) {
                response.data.tableData[m].left_time = "-";
              }

              if (response.data.tableData[m].center_time == null) {
                response.data.tableData[m].center_time = "-";
              }

              if (response.data.tableData[m].right_time == null) {
                response.data.tableData[m].right_time = "-";
              }
              var danceArray = {
                dance_set: response.data.tableData[m].dance_set,
                move_number: response.data.tableData[m].move_number,
                date: split_date,
                dance_move: response.data.tableData[m].dance_move,
                left_time: response.data.tableData[m].left_time,
                left_dancer: response.data.tableData[m].left_dancer,
                center_time: response.data.tableData[m].center_time,
                center_dancer: response.data.tableData[m].center_dancer,
                right_time: response.data.tableData[m].right_time,
                right_dancer: response.data.tableData[m].right_dancer,
                diff: response.data.tableData[m].difference,
                sync: response.data.tableData[m].sync,
              };
              this.dances.push(danceArray);
            }
            this.pieResponseLength = response.data.pieData.length;
            for (var n = 0; n < this.pieResponseLength; n++) {
              var date_pie = new Date(response.data.pieData[n].dates);
              var date_pie_sgt = date_pie.toString();
              var date_pie_split_by_space = date_pie_sgt.split(" ");
              var date_pie_split =
                date_pie_split_by_space[2] +
                " " +
                date_pie_split_by_space[1] +
                " " +
                date_pie_split_by_space[3];
              this.pieDate.push(date_pie_split);
              var pieArray = {
                dance_set: response.data.pieData[n].dance_set,
                date: date_pie_split,
                yes_sync: response.data.pieData[n].yes_sync,
                no_sync: response.data.pieData[n].no_sync,
              };
              this.pie.push(pieArray);
            }
          }
          this.numOfRecords = this.danceSetArr.length;
        });
    },
    getChartData: function (set_number) {
      // get the data for pie chart for each dance set
      for (let m = 0; m < this.pieResponseLength; m++) {
        if (this.pie[m].dance_set == set_number) {
          let yes = this.pie[m].yes_sync;
          let no = this.pie[m].no_sync;
          // console.log("Number: " + set_number);
          // console.log("Yes: " + yes + ", No: " + no);
          let pieChartArray = {
            labels: ["Yes", "No"],
            datasets: [
              {
                borderWidth: 1,
                borderColor: ["rgba(245, 66, 158, 1)", "rgba(66, 194, 245, 1)"],
                backgroundColor: [
                  "rgba(245, 66, 158, 1)",
                  "rgba(66, 194, 245, 1)",
                ],
                data: [yes, no],
              },
            ],
          };
          // console.log(pieChartArray);
          return pieChartArray;
        }
      }
    },
    getDances: function (set_number) {
      // if the chart type is not specified then get
      // move number, date, dance move, dancers in the 3 positions, difference in timing
      // between fastest and slowest dancer and whether the dancers are in sync
      // or not for each dance move
      var danceDataArray = [];
      for (var j = 0; j < this.tableResponseLength; j++) {
        if (this.dances[j].dance_set == set_number) {
          var danceData = {
            move_number: this.dances[j].move_number,
            date: this.dances[j].date,
            dance_move: this.dances[j].dance_move,
            left_dancer: this.dances[j].left_dancer,
            center_dancer: this.dances[j].center_dancer,
            right_dancer: this.dances[j].right_dancer,
            diff: this.dances[j].diff,
            sync: this.dances[j].sync,
          };
          danceDataArray.push(danceData);
        }
      }
      return danceDataArray;
    },
    getDancesTableOnly: function (set_number) {
      // if the chart type is specified to be table only then display additional information
      // time of each dancer for each move for the dance sets
      var danceDataArray = [];
      for (var j = 0; j < this.tableResponseLength; j++) {
        if (this.dances[j].dance_set == set_number) {
          if (this.dances[j].left_time == null) {
            this.dances[j].left_time = "-";
          }

          if (this.dances[j].center_time == null) {
            this.dances[j].center_time = "-";
          }

          if (this.dances[j].right_time == null) {
            this.dances[j].right_time = "-";
          }

          var danceData = {
            move_number: this.dances[j].move_number,
            date: this.dances[j].date,
            dance_move: this.dances[j].dance_move,
            left_time: this.dances[j].left_time,
            left_dancer: this.dances[j].left_dancer,
            center_time: this.dances[j].center_time,
            center_dancer: this.dances[j].center_dancer,
            right_time: this.dances[j].right_time,
            right_dancer: this.dances[j].right_dancer,
            diff: this.dances[j].diff,
            sync: this.dances[j].sync,
          };
          danceDataArray.push(danceData);
        }
      }
      return danceDataArray;
    },
    fetchData: async function () {
      // get all past dance sets data
      const response = await axios.get("/dashboard/past-data");
      this.numDanceSet = response.data.tableData[0].dance_set;
      // this loop is used to set the options users can select for the specific dance sets to view
      // in Dance Set(s) dropdown
      for (var i = 1; i <= this.numDanceSet; i++) {
        var arr = {
          name: i,
          value: i,
        };
        this.danceSetNum.push(arr);
      }
      this.tableResponseLength = response.data.tableData.length;
      for (var j = 0; j < this.tableResponseLength; j++) {
        // get the date of the move
        var date = new Date(response.data.tableData[j].dates);
        var date_sgt = date.toString();
        var date_split_by_space = date_sgt.split(" ");
        var date_split =
          date_split_by_space[2] +
          " " +
          date_split_by_space[1] +
          " " +
          date_split_by_space[3];
        if (response.data.tableData[j].move_number == 1) {
          this.tableDate.push(date_split);
          this.danceSetArr.push(response.data.tableData[j].dance_set);
        }

        // get the start time of the dance set (earliest time among the 3 dancers)
        if (response.data.tableData[j].dance_move == "Start") {
          if (
            response.data.tableData[j].left_time != null &&
            response.data.tableData[j].center_time != null &&
            response.data.tableData[j].right_time != null
          ) {
            if (
              response.data.tableData[j].left_time <=
                response.data.tableData[j].center_time &&
              response.data.tableData[j].left_time <=
                response.data.tableData[j].right_time
            ) {
              this.startTime = response.data.tableData[j].left_time;
            } else if (
              response.data.tableData[j].center_time <=
                response.data.tableData[j].left_time &&
              response.data.tableData[j].center_time <=
                response.data.tableData[j].right_time
            ) {
              this.startTime = response.data.tableData[j].center_time;
            } else if (
              response.data.tableData[j].right_time <=
                response.data.tableData[j].left_time &&
              response.data.tableData[j].right_time <=
                response.data.tableData[j].center_time
            ) {
              this.startTime = response.data.tableData[j].right_time;
            }
          } else {
            if (
              response.data.tableData[j].left_time != null &&
              response.data.tableData[j].center_time != null
            ) {
              if (
                response.data.tableData[j].left_time <=
                response.data.tableData[j].center_time
              ) {
                this.startTime = response.data.tableData[j].left_time;
              } else {
                this.startTime = response.data.tableData[j].center_time;
              }
            } else if (
              response.data.tableData[j].left_time != null &&
              response.data.tableData[j].right_time != null
            ) {
              if (
                response.data.tableData[j].left_time <=
                response.data.tableData[j].right_time
              ) {
                this.startTime = response.data.tableData[j].left_time;
              } else {
                this.startTime = response.data.tableData[j].right_time;
              }
            } else if (
              response.data.tableData[j].center_time != null &&
              response.data.tableData[j].right_time != null
            ) {
              if (
                response.data.tableData[j].center_time <=
                response.data.tableData[j].right_time
              ) {
                this.startTime = response.data.tableData[j].center_time;
              } else {
                this.startTime = response.data.tableData[j].right_time;
              }
            } else if (response.data.tableData[j].left_time != null) {
              this.startTime = response.data.tableData[j].left_time;
            } else if (response.data.tableData[j].center_time != null) {
              this.startTime = response.data.tableData[j].center_time;
            } else if (response.data.tableData[j].right_time != null) {
              this.startTime = response.data.tableData[j].right_time;
            }
          }

          console.log("START: " + this.startTime);
          var startTime_split = this.startTime.split(":");
          if (startTime_split[0] == "24") {
            startTime_split[0] == "00";
          }
          this.startTime = startTime_split[0] + ":" + startTime_split[1];
        } else if (response.data.tableData[j].dance_move == "End") {
          // get the end time of the dance set (latest time among the 3 dancers)
          if (
            response.data.tableData[j].left_time != null &&
            response.data.tableData[j].center_time != null &&
            response.data.tableData[j].right_time != null
          ) {
            if (
              response.data.tableData[j].left_time <=
                response.data.tableData[j].center_time &&
              response.data.tableData[j].left_time <=
                response.data.tableData[j].right_time
            ) {
              this.endTime = response.data.tableData[j].left_time;
            } else if (
              response.data.tableData[j].center_time <=
                response.data.tableData[j].left_time &&
              response.data.tableData[j].center_time <=
                response.data.tableData[j].right_time
            ) {
              this.endTime = response.data.tableData[j].center_time;
            } else if (
              response.data.tableData[j].right_time <=
                response.data.tableData[j].left_time &&
              response.data.tableData[j].right_time <=
                response.data.tableData[j].center_time
            ) {
              this.endTime = response.data.tableData[j].right_time;
            }
          } else {
            if (
              response.data.tableData[j].left_time != null &&
              response.data.tableData[j].center_time != null
            ) {
              if (
                response.data.tableData[j].left_time <=
                response.data.tableData[j].center_time
              ) {
                this.endTime = response.data.tableData[j].left_time;
              } else {
                this.endTime = response.data.tableData[j].center_time;
              }
            } else if (
              response.data.tableData[j].left_time != null &&
              response.data.tableData[j].right_time != null
            ) {
              if (
                response.data.tableData[j].left_time <=
                response.data.tableData[j].right_time
              ) {
                this.endTime = response.data.tableData[j].left_time;
              } else {
                this.endTime = response.data.tableData[j].right_time;
              }
            } else if (
              response.data.tableData[j].center_time != null &&
              response.data.tableData[j].right_time != null
            ) {
              if (
                response.data.tableData[j].center_time <=
                response.data.tableData[j].right_time
              ) {
                this.endTime = response.data.tableData[j].center_time;
              } else {
                this.endTime = response.data.tableData[j].right_time;
              }
            } else if (response.data.tableData[j].left_time != null) {
              this.endTime = response.data.tableData[j].left_time;
            } else if (response.data.tableData[j].center_time != null) {
              this.endTime = response.data.tableData[j].center_time;
            } else if (response.data.tableData[j].right_time != null) {
              this.endTime = response.data.tableData[j].right_time;
            }
          }
          var endTime_split = this.endTime.split(":");
          if (endTime_split[0] == "24") {
            endTime_split[0] == "00";
          }
          this.endTime = endTime_split[0] + ":" + endTime_split[1];
          var timeOfDance = this.startTime + " - " + this.endTime;
          this.danceTimeArray.push(timeOfDance);
        }
        var danceArr = {
          dance_set: response.data.tableData[j].dance_set,
          move_number: response.data.tableData[j].move_number,
          date: date_split,
          dance_move: response.data.tableData[j].dance_move,
          left_time: response.data.tableData[j].left_time,
          left_dancer: response.data.tableData[j].left_dancer,
          center_time: response.data.tableData[j].center_time,
          center_dancer: response.data.tableData[j].center_dancer,
          right_time: response.data.tableData[j].right_time,
          right_dancer: response.data.tableData[j].right_dancer,
          diff: response.data.tableData[j].difference,
          sync: response.data.tableData[j].sync,
        };
        // push the data for each dance move in the dances array
        this.dances.push(danceArr);
      }
      this.pieResponseLength = response.data.pieData.length;
      for (var k = 0; k < this.pieResponseLength; k++) {
        // get the date for pie data
        var pie_date = new Date(response.data.pieData[k].dates);
        var pie_date_sgt = pie_date.toString();
        var pie_date_split_by_space = pie_date_sgt.split(" ");
        var pie_date_split =
          pie_date_split_by_space[2] +
          " " +
          pie_date_split_by_space[1] +
          " " +
          pie_date_split_by_space[3];
        this.pieDate.push(pie_date_split);
        var pieArr = {
          dance_set: response.data.pieData[k].dance_set,
          date: pie_date_split,
          yes_sync: response.data.pieData[k].yes_sync,
          no_sync: response.data.pieData[k].no_sync,
        };
        // push the data for each dance set in the pie array
        this.pie.push(pieArr);
      }
      this.numOfRecords = this.danceSetArr.length;
    },
  },
  // used to send an HTTP request to fetch data that the component will then render
  async mounted() {
    this.loaded = false;
    console.log("Before: " + this.loaded);
    try {
      await this.fetchData();
      this.loaded = true;
      console.log("After: " + this.loaded);
    } catch (e) {
      console.error(e);
    }
  },
};
</script>
