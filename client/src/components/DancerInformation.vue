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
        <v-col class="mx-auto" md="3">
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
        <v-col class="mx-auto" md="4">
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
                label="Choose a Range of Dates"
                :value="dateDisp"
                v-on="on"
                clearable
                background-color="#3DDBD8"
                prepend-icon="mdi-calendar"
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
              range
            />
          </v-menu>
        </v-col>
        <v-col class="mx-auto" md="1">
          <v-btn icon color="green" fab outlined @click="submit">
            <v-icon>mdi-check</v-icon>
          </v-btn>
        </v-col>
      </v-row>
      <!-- if page is loaded, have time spent, number of sets done and displaying current week data -->
      <template v-if="loaded && haveTime && haveSet && haveCurrentWeek">
        <v-row>
          <v-card width="49%" class="mx-auto">
            <v-card-title class="justify-center">
              Time Spent (Minutes) vs Dancers
            </v-card-title>
            <p align="center">{{ currentWeek }}</p>
            <BarChartTime :chartData="timeChartArray" />
          </v-card>
          <v-spacer />
          <v-card width="49%" class="mx-auto">
            <v-card-title class="justify-center">
              Number of Dance Sets vs Dancers
            </v-card-title>
            <p align="center">{{ currentWeek }}</p>
            <BarChartSet :chartData="setChartArray" />
          </v-card>
        </v-row>
      </template>
      <!-- if page is loaded, have time spent, number of sets done and not displaying current week data -->
      <template v-else-if="loaded && haveTime && haveSet && !haveCurrentWeek">
        <v-row>
          <v-card width="49%" class="mx-auto">
            <v-card-title class="justify-center"
              >Time Spent (Minutes) vs Dancers</v-card-title
            >
            <p align="center">{{ rangeOfDates }}</p>
            <BarChartTime :chartData="timeChartArray" />
          </v-card>
          <v-spacer />
          <v-card width="49%" class="mx-auto">
            <v-card-title class="justify-center"
              >Number of Dance Sets vs Dancers</v-card-title
            >
            <p align="center">{{ rangeOfDates }}</p>
            <BarChartSet :chartData="setChartArray" />
          </v-card>
        </v-row>
      </template>
      <!-- if page is loaded, have time spent, no number of sets data and displaying current week data -->
      <template v-else-if="loaded && haveTime && !haveSet && haveCurrentWeek">
        <v-row>
          <v-card width="100%" class="mx-auto">
            <v-card-title class="justify-center">
              Time Spent (Minutes) vs Dancers
            </v-card-title>
            <p align="center">{{ currentWeek }}</p>
            <BarChartTime :chartData="timeChartArray" />
          </v-card>
        </v-row>
      </template>
      <!-- if page is loaded, have time spent, no number of sets done and not displaying current week data -->
      <template v-else-if="loaded && haveTime && !haveSet && !haveCurrentWeek">
        <v-row>
          <v-card width="100%" class="mx-auto">
            <v-card-title class="justify-center"
              >Time Spent (Minutes) vs Dancers</v-card-title
            >
            <p align="center">{{ rangeOfDates }}</p>
            <BarChartTime :chartData="timeChartArray" />
          </v-card>
        </v-row>
      </template>
      <!-- if page is loaded, no time spent data, have number of sets done and displaying current week data -->
      <template v-else-if="loaded && !haveTime && haveSet && haveCurrentWeek">
        <v-row>
          <v-card width="100%" class="mx-auto">
            <v-card-title class="justify-center"
              >Number of Dance Sets vs Dancers
            </v-card-title>
            <p align="center">{{ currentWeek }}</p>
            <BarChartSet :chartData="setChartArray" />
          </v-card>
        </v-row>
      </template>
      <!-- if page is loaded, no time spent data, number of sets done and not displaying current week data -->
      <template v-else-if="loaded && !haveTime && haveSet && !haveCurrentWeek">
        <v-row>
          <v-card width="100%" class="mx-auto">
            <v-card-title class="justify-center"
              >Number of Dance Sets vs Dancers</v-card-title
            >
            <p align="center">{{ rangeOfDates }}</p>
            <BarChartSet :chartData="setChartArray" />
          </v-card>
        </v-row>
      </template>
      <!-- if page is loaded, no time spent and number of sets done data -->
      <template v-else-if="loaded && !haveTime && !haveSet">
        <v-row>
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
        </v-row>
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
      <br />
    </div>
  </v-container>
</template>

<script>
import axios from "axios";
import psnd from "./PersistentSideNavDrawer";
import Swal from "sweetalert2";
import BarChartSet from "./Charts/BarChartSet";
import BarChartTime from "./Charts/BarChartTime";

export default {
  name: "Dancers",

  components: {
    psnd,
    BarChartSet,
    BarChartTime,
  },

  data: () => ({
    selectedChart: null,
    chartType: [
      { name: "Time Spent", value: "Time Bar" },
      { name: "Sets Done", value: "Set Bar" },
    ],
    selectedDancers: null,
    dancers: [
      { name: "Jingxuan", value: "Jingxuan" },
      { name: "Karan", value: "Karan" },
      { name: "Kexin", value: "Kexin" },
      { name: "Sarah", value: "Sarah" },
      { name: "Tristy", value: "Tristy" },
      { name: "Yunhan", value: "Yunhan" },
    ],
    dateMenu: false,
    dateVal: null,
    getEndDate: new Date().toISOString().substr(0, 10),
    haveTime: true,
    haveSet: true,
    timeChartArray: {
      labels: [],
      datasets: [
        {
          label: "Time Spent",
          borderWidth: 1,
          backgroundColor: [
            "rgba(255, 99, 132, 1)",
            "rgba(255, 159, 64, 1)",
            "rgba(255, 206, 86, 1)",
            "rgba(54, 162, 235, 1)",
            "rgba(75, 192, 192, 1)",
            "rgba(153, 102, 255, 1)",
          ],
          borderColor: [
            "rgba(255, 99, 132, 1)",
            "rgba(255, 159, 64, 1)",
            "rgba(255, 206, 86, 1)",
            "rgba(54, 162, 235, 1)",
            "rgba(75, 192, 192, 1)",
            "rgba(153, 102, 255, 1)",
          ],
          pointBorderColor: "#2554FF",
          data: null,
        },
      ],
    },
    currentWeek: null,
    haveCurrentWeek: false,
    rangeOfDates: null,
    setChartArray: {
      labels: [],
      datasets: [
        {
          label: "Number of Sets",
          borderWidth: 1,
          backgroundColor: [
            "rgba(255, 99, 132, 1)",
            "rgba(255, 159, 64, 1)",
            "rgba(255, 206, 86, 1)",
            "rgba(54, 162, 235, 1)",
            "rgba(75, 192, 192, 1)",
            "rgba(153, 102, 255, 1)",
          ],
          borderColor: [
            "rgba(255, 99, 132, 1)",
            "rgba(255, 159, 64, 1)",
            "rgba(255, 206, 86, 1)",
            "rgba(54, 162, 235, 1)",
            "rgba(75, 192, 192, 1)",
            "rgba(153, 102, 255, 1)",
          ],
          pointBorderColor: "#2554FF",
          data: null,
        },
      ],
    },
    loaded: false,
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
        console.log("get data from Dance and Sync");
      }
    },
    clearDancers: function () {
      this.selectedDancers = null;
    },
    selectDancers: function () {
      if (this.selectedDancers != null && this.selectedDancers.length > 0) {
        console.log(this.selectedDancers.length);
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
      // data in selectedDancers are to be taken as OR
      // data in dateVal is to be taken as OR
      // selectedChart refers to the DB Table (Time Bar: DailyTracker, Set Bar: DailySet)
      // SELECT * FROM DailyTracker/DailySet WHERE (this.selectedDancers) AND (this.dateVal)
      let checkCorrectData = 1;
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
        if (this.dateVal.length == 1) {
          // no range of dates provided, show error message
          checkCorrectData = 0;
          Swal.fire({
            icon: "error",
            title: "Oops...",
            text: "Please provide a range of dates (minimum 5 days).",
          });
          this.clearDates();
        } else {
          console.log(this.dateVal);
          this.dateVal = this.dateVal.sort();
          let startDate = new Date(this.dateVal[0]);
          let endDate = new Date(this.dateVal[1]);
          let diff = endDate - startDate;

          console.log("Diff: " + diff);
          // if range of dates is less than 5 days, show error message
          if (diff < 345600000) {
            checkCorrectData = 0;
            Swal.fire({
              icon: "error",
              title: "Oops...",
              text: "The range of dates should have a minimum of 5 days.",
            });
            this.clearDates();
          } else {
            var dates = '"' + this.dateVal[0] + "," + this.dateVal[1] + '"';
          }
        }
      } else {
        dates = null;
      }

      // if all data entered (if any) are correct, then post data to server
      if (checkCorrectData == 1) {
        const dancerDataToSend =
          '{"chart":"' +
          this.selectedChart +
          '", ' +
          '"dancers":' +
          dancers +
          ', "dates":' +
          dates +
          "}";
        // console.log(dancerDataToSend);
        var jsonDancerDataToSend = JSON.parse(dancerDataToSend);
        console.log(
          "Dancer Data To Send: " + JSON.stringify(jsonDancerDataToSend)
        );

        axios
          .post("/dashboard/dancers", {
            dancerData: jsonDancerDataToSend,
          })
          .then((response) => {
            console.log("Time length: " + response.data.timeData.length);
            console.log("Set length: " + response.data.setData.length);
            this.haveTime = false;
            this.haveSet = false;
            this.loaded = false;
            this.timeChartArray = {};
            this.setChartArray = {};
            let labelForCharts = [];

            if (this.dateVal == null) {
              // no dates selected means show current week
              this.haveCurrentWeek = true;
            } else {
              // show data for specific range of dates
              this.haveCurrentWeek = false;
              let startDate = new Date(this.dateVal[0]);
              let startDate_split = startDate.toString().split(" ");
              startDate =
                startDate_split[2] +
                " " +
                startDate_split[1] +
                " " +
                startDate_split[3];
              let endDate = new Date(this.dateVal[1]);
              let endDate_split = endDate.toString().split(" ");
              endDate =
                endDate_split[2] +
                " " +
                endDate_split[1] +
                " " +
                endDate_split[3];
              this.rangeOfDates = startDate + " - " + endDate;
            }

            // if have specific dancers selected, then labels must change accordingly
            // to show only those dancers' names
            if (this.selectedDancers != null) {
              for (let i = 0; i < this.selectedDancers.length; i++) {
                labelForCharts.push(this.selectedDancers[i]);
              }
            } else {
              // show all names
              labelForCharts = [
                "Jingxuan",
                "Karan",
                "Kexin",
                "Sarah",
                "Tristy",
                "Yunhan",
              ];
            }
            if (
              response.data.timeData.length != undefined &&
              response.data.setData.length != undefined
            ) {
              // have both time spent and number of sets data, then set the data for both
              // in timeChartArray and setChartArray
              let timeChartData = [];
              for (let j = 0; j < response.data.timeData.length; j++) {
                // null means no data available for that person
                if (response.data.timeData[j].sum == null) {
                  timeChartData.push(0);
                } else {
                  timeChartData.push(parseInt(response.data.timeData[j].sum));
                }
              }
              // check if all data for time is 0
              let countTime = 0;
              for (let k = 0; k < timeChartData.length; k++) {
                if (timeChartData[k] == 0) {
                  countTime++;
                }
              }

              let setChartData = [];
              for (let k = 0; k < response.data.setData.length; k++) {
                setChartData.push(parseInt(response.data.setData[k].count));
              }

              // check if all data for number of sets is 0
              let countSet = 0;
              for (let j = 0; j < setChartData.length; j++) {
                if (setChartData[j] == 0) {
                  countSet++;
                }
              }
              if (countTime == timeChartData.length) {
                // if all 0, then that means no data available for what was requested
                this.haveTime = false;
              } else {
                this.haveTime = true;
                let chartArrayTime = {
                  labels: labelForCharts,
                  datasets: [
                    {
                      label: "Time Spent",
                      borderWidth: 1,
                      backgroundColor: [
                        "rgba(255, 99, 132, 1)",
                        "rgba(255, 159, 64, 1)",
                        "rgba(255, 206, 86, 1)",
                        "rgba(54, 162, 235, 1)",
                        "rgba(75, 192, 192, 1)",
                        "rgba(153, 102, 255, 1)",
                      ],
                      borderColor: [
                        "rgba(255, 99, 132, 1)",
                        "rgba(255, 159, 64, 1)",
                        "rgba(255, 206, 86, 1)",
                        "rgba(54, 162, 235, 1)",
                        "rgba(75, 192, 192, 1)",
                        "rgba(153, 102, 255, 1)",
                      ],
                      pointBorderColor: "#2554FF",
                      data: timeChartData,
                    },
                  ],
                };
                this.timeChartArray = chartArrayTime;
              }

              if (countSet == setChartData.length) {
                // if all 0, then that means no data available for what was requested
                this.haveSet = false;
              } else {
                this.haveSet = true;
                let chartArraySet = {
                  labels: labelForCharts,
                  datasets: [
                    {
                      label: "Number of Sets",
                      borderWidth: 1,
                      backgroundColor: [
                        "rgba(255, 99, 132, 1)",
                        "rgba(255, 159, 64, 1)",
                        "rgba(255, 206, 86, 1)",
                        "rgba(54, 162, 235, 1)",
                        "rgba(75, 192, 192, 1)",
                        "rgba(153, 102, 255, 1)",
                      ],
                      borderColor: [
                        "rgba(255, 99, 132, 1)",
                        "rgba(255, 159, 64, 1)",
                        "rgba(255, 206, 86, 1)",
                        "rgba(54, 162, 235, 1)",
                        "rgba(75, 192, 192, 1)",
                        "rgba(153, 102, 255, 1)",
                      ],
                      pointBorderColor: "#2554FF",
                      data: setChartData,
                    },
                  ],
                };
                this.setChartArray = chartArraySet;
              }
              this.loaded = true;
            } else if (
              response.data.timeData.length != undefined &&
              response.data.setData.length == undefined
            ) {
              let timeChartData = [];
              for (let j = 0; j < response.data.timeData.length; j++) {
                if (response.data.timeData[j].sum == null) {
                  timeChartData.push(0);
                } else {
                  timeChartData.push(parseInt(response.data.timeData[j].sum));
                }
              }
              let countTime = 0;
              for (let k = 0; k < timeChartData.length; k++) {
                if (timeChartData[k] == 0) {
                  countTime++;
                }
              }
              console.log("Label: " + labelForCharts);
              console.log("Time: " + timeChartData);
              let chartArrayTime = {
                labels: labelForCharts,
                datasets: [
                  {
                    label: "Time Spent",
                    borderWidth: 1,
                    backgroundColor: [
                      "rgba(255, 99, 132, 1)",
                      "rgba(255, 159, 64, 1)",
                      "rgba(255, 206, 86, 1)",
                      "rgba(54, 162, 235, 1)",
                      "rgba(75, 192, 192, 1)",
                      "rgba(153, 102, 255, 1)",
                    ],
                    borderColor: [
                      "rgba(255, 99, 132, 1)",
                      "rgba(255, 159, 64, 1)",
                      "rgba(255, 206, 86, 1)",
                      "rgba(54, 162, 235, 1)",
                      "rgba(75, 192, 192, 1)",
                      "rgba(153, 102, 255, 1)",
                    ],
                    pointBorderColor: "#2554FF",
                    data: timeChartData,
                  },
                ],
              };
              this.timeChartArray = chartArrayTime;
              if (countTime == timeChartData.length) {
                this.haveTime = false;
              } else {
                this.haveTime = true;
              }
              this.haveSet = false;
              this.loaded = true;
            } else if (
              response.data.timeData.length == undefined &&
              response.data.setData.length != undefined
            ) {
              // have number of sets done data only
              let setChartData = [];
              for (let k = 0; k < response.data.setData.length; k++) {
                setChartData.push(parseInt(response.data.setData[k].count));
              }
              // check if all data is 0
              let countSet = 0;
              for (let j = 0; j < setChartData.length; j++) {
                if (setChartData[j] == 0) {
                  countSet++;
                }
              }

              this.haveTime = false;

              if (countSet == setChartData.length) {
                // if all data is 0, taken to be no data available for the conditions given
                this.haveSet = false;
              } else {
                this.haveSet = true;
                let chartArraySet = {
                  labels: labelForCharts,
                  datasets: [
                    {
                      label: "Number of Sets",
                      borderWidth: 1,
                      backgroundColor: [
                        "rgba(255, 99, 132, 1)",
                        "rgba(255, 159, 64, 1)",
                        "rgba(255, 206, 86, 1)",
                        "rgba(54, 162, 235, 1)",
                        "rgba(75, 192, 192, 1)",
                        "rgba(153, 102, 255, 1)",
                      ],
                      borderColor: [
                        "rgba(255, 99, 132, 1)",
                        "rgba(255, 159, 64, 1)",
                        "rgba(255, 206, 86, 1)",
                        "rgba(54, 162, 235, 1)",
                        "rgba(75, 192, 192, 1)",
                        "rgba(153, 102, 255, 1)",
                      ],
                      pointBorderColor: "#2554FF",
                      data: setChartData,
                    },
                  ],
                };
                this.setChartArray = chartArraySet;
              }
              this.loaded = true;
            } else {
              // no time spent or number of sets done data available
              this.haveTime = false;
              this.haveSet = false;
              this.loaded = true;
            }
            console.log("Have Time: " + this.haveTime);
            console.log("Have Set: " + this.haveSet);
            console.dir(this.timeChartArray);
            console.dir(this.setChartArray);
          });
      }
    },
    fetchSetData: async function () {
      // get number of sets done data for each of the dancers for the current week
      const response = await axios.get("/dashboard/dancers");
      console.log(response.data.timeData);
      console.log(response.data.setData);
      let setChartData = [];
      for (let i = 0; i < response.data.setData.length; i++) {
        setChartData.push(parseInt(response.data.setData[i].count));
      }
      console.log(setChartData);
      let chartArraySet = {
        labels: ["Jingxuan", "Karan", "Kexin", "Sarah", "Tristy", "Yunhan"],
        datasets: [
          {
            label: "Number of Sets",
            borderWidth: 1,
            backgroundColor: [
              "rgba(255, 99, 132, 1)",
              "rgba(255, 159, 64, 1)",
              "rgba(255, 206, 86, 1)",
              "rgba(54, 162, 235, 1)",
              "rgba(75, 192, 192, 1)",
              "rgba(153, 102, 255, 1)",
            ],
            borderColor: [
              "rgba(255, 99, 132, 1)",
              "rgba(255, 159, 64, 1)",
              "rgba(255, 206, 86, 1)",
              "rgba(54, 162, 235, 1)",
              "rgba(75, 192, 192, 1)",
              "rgba(153, 102, 255, 1)",
            ],
            pointBorderColor: "#2554FF",
            data: setChartData,
          },
        ],
      };
      return chartArraySet;
    },
    fetchTimeData: async function () {
      // get time spent dancing data for each of the dancers for the current week
      const response = await axios.get("/dashboard/dancers");
      console.log(response.data.timeData);
      let timeChartData = [];
      for (let i = 0; i < response.data.timeData.length; i++) {
        if (response.data.timeData[i].sum == null) {
          timeChartData.push(0);
        } else {
          timeChartData.push(parseInt(response.data.timeData[i].sum));
        }
      }
      console.log(timeChartData);
      let chartArrayTime = {
        labels: ["Jingxuan", "Karan", "Kexin", "Sarah", "Tristy", "Yunhan"],
        datasets: [
          {
            label: "Time Spent",
            borderWidth: 1,
            backgroundColor: [
              "rgba(255, 99, 132, 1)",
              "rgba(255, 159, 64, 1)",
              "rgba(255, 206, 86, 1)",
              "rgba(54, 162, 235, 1)",
              "rgba(75, 192, 192, 1)",
              "rgba(153, 102, 255, 1)",
            ],
            borderColor: [
              "rgba(255, 99, 132, 1)",
              "rgba(255, 159, 64, 1)",
              "rgba(255, 206, 86, 1)",
              "rgba(54, 162, 235, 1)",
              "rgba(75, 192, 192, 1)",
              "rgba(153, 102, 255, 1)",
            ],
            pointBorderColor: "#2554FF",
            data: timeChartData,
          },
        ],
      };
      return chartArrayTime;
    },
  },
  // used to send an HTTP request to fetch data that the component will then render
  async mounted() {
    this.loaded = false;
    try {
      // get number of sets data for each dancer for the current week
      const setData = await this.fetchSetData();
      this.setChartArray = setData;
    } catch (e) {
      console.error(e);
    }

    try {
      // get time spent practicing data for each dancer for the current week
      const timeData = await this.fetchTimeData();
      this.timeChartArray = timeData;
      this.loaded = true;
    } catch (e) {
      console.error(e);
    }

    // get the dates for Monday and Sunday of the current week in DD Month name YYYY format
    // for readability purpose e.g 28 Sep 2020
    // store the current week information in this.currentWeek and set this.haveCurrentWeek to true
    var date = new Date();
    var diff = date.getDate() - date.getDay() + (date.getDay() === 0 ? -6 : 1);
    var mondayDate = new Date(date.setDate(diff));
    mondayDate = mondayDate.toString();
    mondayDate = new Date(mondayDate);
    // console.log("MON DATE: " + mondayDate);
    var sundayDate = new Date(date.setDate(diff + 6));
    sundayDate = sundayDate.toString();
    sundayDate = new Date(sundayDate);
    // console.log("SUN DATE: " + sundayDate);

    let mondayDate_split = mondayDate.toString().split(" ");
    mondayDate =
      mondayDate_split[2] +
      " " +
      mondayDate_split[1] +
      " " +
      mondayDate_split[3];

    let sundayDate_split = sundayDate.toString().split(" ");
    sundayDate =
      sundayDate_split[2] +
      " " +
      sundayDate_split[1] +
      " " +
      sundayDate_split[3];

    var sundayDateCheckDD = sundayDate_split[2];
    var mondayDateCheckDD = mondayDate_split[2];
    if (parseInt(sundayDateCheckDD) < parseInt(mondayDateCheckDD)) {
      var sundayDateCheckMM = sundayDate_split[1];
      var sundayDateCheckYYYY = parseInt(sundayDate_split[3]);

      if (sundayDateCheckMM == "Jan") sundayDateCheckMM = "Feb";
      else if (sundayDateCheckMM == "Feb") sundayDateCheckMM = "Mar";
      else if (sundayDateCheckMM == "Mar") sundayDateCheckMM = "Apr";
      else if (sundayDateCheckMM == "Apr") sundayDateCheckMM = "May";
      else if (sundayDateCheckMM == "May") sundayDateCheckMM = "Jun";
      else if (sundayDateCheckMM == "Jun") sundayDateCheckMM = "Jul";
      else if (sundayDateCheckMM == "Jul") sundayDateCheckMM = "Aug";
      else if (sundayDateCheckMM == "Aug") sundayDateCheckMM = "Sep";
      else if (sundayDateCheckMM == "Sep") sundayDateCheckMM = "Oct";
      else if (sundayDateCheckMM == "Oct") sundayDateCheckMM = "Nov";
      else if (sundayDateCheckMM == "Nov") sundayDateCheckMM = "Dec";
      else if (sundayDateCheckMM == "Dec") {
        sundayDateCheckMM = "Jan";
        sundayDateCheckYYYY += 1;
      }

      sundayDate =
        sundayDateCheckDD + " " + sundayDateCheckMM + " " + sundayDateCheckYYYY;
    }
    console.log("Monday Date: " + mondayDate);
    console.log("Sunday Date: " + sundayDate);
    this.currentWeek = mondayDate + " - " + sundayDate;
    this.haveCurrentWeek = true;
  },
};
</script>
