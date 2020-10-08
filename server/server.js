const express = require("express");
const app = express();
const bodyParser = require("body-parser");
const cors = require("cors");
const PORT = 4000;
const RDS_HOSTNAME =
  "b07-dancedashboard.cx4zc3f2utdt.ap-southeast-1.rds.amazonaws.com";
const RDS_USERNAME = "b07admin";
const RDS_PASSWORD = "password";
const RDS_PORT = 5432;
const { Client } = require("pg");
var http = require("http");

app.use(function (req, res, next) {
  res.header(
    "Access-Control-Allow-Headers",
    "Origin, X-Requested-With, Content-Type, Accept"
  );
  next();
});

var server = http.createServer(app);
var io = require("socket.io")(server);

io.on("connection", (socket) => {
  console.log("This is the backend socket");
});

const client = new Client({
  user: RDS_USERNAME,
  host: RDS_HOSTNAME,
  database: "justdance",
  password: RDS_PASSWORD,
  port: RDS_PORT,
  table: "dancedata",
});

// connect to PostgreSQL on Amazon RDS
client
  .connect()
  .then(() => console.log("connected"))
  .catch((err) => console.error("connection error", err.stack));

var numOfRows = 0;
var getLastDanceID = 0;
var getLastMoveID = 0;

// wait for trigger
client.query("LISTEN new_data_in_dance");
// when data is entered into dancedata table
client.on("notification", async (data) => {
  // get the data that has been inserted
  const payload = JSON.parse(data.payload);
  console.log("row added!", payload);
  var dancersToSort = [];
  dancersToSort.push(dancer_1);
  dancersToSort.push(dancer_2);
  dancersToSort.push(dancer_3);
  // sort the dancer names in alphabetical order, to be inserted into the other tables,
  // used in searching for specific dancer information in Past Dance Sets page and
  // Dancer Information page
  dancersToSort = dancersToSort.sort();
  var dancers =
    "'" +
    dancersToSort[0] +
    "," +
    dancersToSort[1] +
    "," +
    dancersToSort[2] +
    "'";
  console.log("Dancers: " + dancers);

  try {
    // check if there is existing data
    await client.query("SELECT COUNT(*) FROM dance").then((res) => {
      let result = res.rows[0];
      numOfRows = result.count;
      console.log("Number: " + numOfRows);
    });
  } catch (err) {
    console.error(err.stack);
  }

  // if there is existing data
  if (numOfRows != 0) {
    try {
      // get the last dance set
      await client
        .query("SELECT dance_set FROM dance ORDER BY dance_set DESC LIMIT 1")
        .then((res) => {
          let result = res.rows[0];
          getLastDanceID = result.dance_set;
          console.log("getLastDanceID If: " + getLastDanceID);
        });
    } catch (err) {
      console.error(err.stack);
    }
  } else {
    // there are no past dance sets
    getLastDanceID = 0;
    console.log("getLastDanceID else: " + getLastDanceID);
  }

  // if the movement is "Start" i.e. starting movement
  if (payload.dance_move == "Start") {
    // first move of the dance set
    getLastMoveID = 0;
    console.log("getLastMoveID If: " + getLastMoveID);
  } else {
    try {
      // get the number of the last dance move
      getLastMoveIDQuery =
        "SELECT move_number FROM dance WHERE dance_set=" +
        getLastDanceID +
        " ORDER BY move_number DESC LIMIT 1";
      await client.query(getLastMoveIDQuery).then((res) => {
        let result = res.rows[0];
        getLastMoveID = result.move_number;
        console.log("getLastMoveID Else: " + getLastMoveID);
      });
    } catch (err) {
      console.error(err.stack);
    }
  }

  var move_id = getLastMoveID;
  var dance_id = getLastDanceID;
  var insertDanceQuery = "";
  var insertSyncQuery = "";
  var updateSyncQuery = "";
  var left_dancer = "";
  var center_dancer = "";
  var right_dancer = "";
  var sync_yes = 0;
  var sync_no = 0;
  var dancer1TimeStart = "";
  var dancer2TimeStart = "";
  var dancer3TimeStart = "";
  var dancer1TimeEnd = "";
  var dancer2TimeEnd = "";
  var dancer3TimeEnd = "";
  var dancer1_min_calculated = null;
  var dancer2_min_calculated = null;
  var dancer3_min_calculated = null;
  var left_time = "";
  var center_time = "";
  var right_time = "";

  if (payload.left_dancer != null) {
    if (payload.left_dancer == 1) {
      left_dancer = "'" + dancer_1 + "'";
    } else if (payload.left_dancer == 2) {
      left_dancer = "'" + dancer_2 + "'";
    } else if (payload.left_dancer == 3) {
      left_dancer = "'" + dancer_3 + "'";
    }
  } else {
    left_dancer = "'-'";
  }

  if (payload.center_dancer != null) {
    if (payload.center_dancer == 1) {
      center_dancer = "'" + dancer_1 + "'";
    } else if (payload.center_dancer == 2) {
      center_dancer = "'" + dancer_2 + "'";
    } else if (payload.center_dancer == 3) {
      center_dancer = "'" + dancer_3 + "'";
    }
  } else {
    center_dancer = "'-'";
  }

  if (payload.right_dancer != null) {
    if (payload.right_dancer == 1) {
      right_dancer = "'" + dancer_1 + "'";
    } else if (payload.right_dancer == 2) {
      right_dancer = "'" + dancer_2 + "'";
    } else if (payload.right_dancer == 3) {
      right_dancer = "'" + dancer_3 + "'";
    }
  } else {
    right_dancer = "'-'";
  }

  if (payload.left_time != null) {
    left_time = "'" + payload.left_time + "'";
  } else {
    left_time = null;
  }

  if (payload.center_time != null) {
    center_time = "'" + payload.center_time + "'";
  } else {
    center_time = null;
  }

  if (payload.right_time != null) {
    right_time = "'" + payload.right_time + "'";
  } else {
    right_time = null;
  }

  // Set dancer 1 name to the left, center or right dancer, depending on where dancer 1 is
  // this will be used in displaying the names of the dancers in accordance to their positions
  // in the real-time dashboard, and in the table showing the dance moves done so far
  // if (payload.left_dancer == 1) {
  //   left_dancer = dancer_1;
  // } else if (payload.center_dancer == 1) {
  //   center_dancer = dancer_1;
  // } else if (payload.right_dancer == 1) {
  //   right_dancer = dancer_1;
  // }

  // // set dancer 2 name to the left, center or right dancer, depending on where dancer 2 is
  // if (payload.left_dancer == 2) {
  //   left_dancer = dancer_2;
  // } else if (payload.center_dancer == 2) {
  //   center_dancer = dancer_2;
  // } else if (payload.right_dancer == 2) {
  //   right_dancer = dancer_2;
  // }

  // // set dancer 3 name to the left, center or right dancer, depending on where dancer 3 is
  // if (payload.left_dancer == 3) {
  //   left_dancer = dancer_3;
  // } else if (payload.center_dancer == 3) {
  //   center_dancer = dancer_3;
  // } else if (payload.right_dancer == 3) {
  //   right_dancer = dancer_3;
  // }

  // if the movement is "Start" i.e. starting movement
  if (payload.dance_move == "Start") {
    // first move of the dance set
    move_id = 1;
    // new dance set, so dance id is incremented by 1 from the last dance set id
    dance_id = getLastDanceID + 1;
    console.log("dance_id: " + dance_id);

    // query to insert the data into dance table,
    // which is the table from which some of the tables will get their data from
    insertDanceQuery =
      "INSERT INTO dance VALUES (" +
      dance_id +
      ",'" +
      payload.date +
      "'," +
      move_id +
      "," +
      dancers +
      ",'" +
      payload.dance_move +
      "'," +
      left_time +
      "," +
      left_dancer +
      "," +
      center_time +
      "," +
      center_dancer +
      "," +
      right_time +
      "," +
      right_dancer +
      "," +
      payload.difference +
      ",'" +
      payload.sync +
      "')";

    // console.log(insertDanceQuery);
    try {
      // insert into dance table
      await client.query(insertDanceQuery).then((res) => {
        console.log("Start Insertion OK");
      });
    } catch (err) {
      console.error(err.stack);
    }

    // increment sync_yes or sync_no counter depending on whether the dancers are in sync or not
    if (payload.sync == "Yes") {
      sync_yes += 1;
    } else {
      sync_no += 1;
    }

    // query to insert data into sync table
    insertSyncQuery =
      "INSERT INTO sync VALUES (" +
      dance_id +
      ",'" +
      payload.date +
      "'," +
      dancers +
      "," +
      sync_yes +
      "," +
      sync_no +
      ")";

    try {
      // insert into sync table
      client
        .query(insertSyncQuery)
        .then((res) => console.log("Sync Insertion OK"));
    } catch (err) {
      console.error(err.stack);
    }
  } else if (payload.dance_move != "Start") {
    // if move is not Start, that means that this move belongs to a
    // dance set that is ongoing, so increment the move id
    move_id += 1;

    // query to insert new data into dance table
    insertDanceQuery =
      "INSERT INTO dance VALUES (" +
      dance_id +
      ",'" +
      payload.date +
      "'," +
      move_id +
      "," +
      dancers +
      ",'" +
      payload.dance_move +
      "'," +
      left_time +
      "," +
      left_dancer +
      "," +
      center_time +
      "," +
      center_dancer +
      "," +
      right_time +
      "," +
      right_dancer +
      "," +
      payload.difference +
      ",'" +
      payload.sync +
      "')";

    try {
      // insert data into dance table
      await client.query(insertDanceQuery).then((res) => {
        console.log("Other dance move Insertion OK");
      });
    } catch (err) {
      console.error(err.stack);
    }

    // query to get the number of moves so far for which the dancers are in sync
    var getYesSyncNum = "SELECT yes_sync FROM sync WHERE dance_set=" + dance_id;
    try {
      await client.query(getYesSyncNum).then((res) => {
        let result = res.rows[0];
        sync_yes = result.yes_sync;
        console.log("result sync_yes: " + JSON.stringify(result));
        console.log("sync_yes: " + sync_yes);
      });
    } catch (err) {
      console.error(err.stack);
    }

    // query to get the number of moves so far for which the dancers are not in sync
    var getNoSyncNum = "SELECT no_sync FROM sync WHERE dance_set=" + dance_id;
    try {
      await client.query(getNoSyncNum).then((res) => {
        let result = res.rows[0];
        sync_no = result.no_sync;
        console.log("sync_no: " + sync_no);
      });
    } catch (err) {
      console.error(err.stack);
    }

    // if the dancers are in sync for newest dance move, inscrement sync_yes counter
    // else increment sync_no counter
    if (payload.sync == "Yes") {
      sync_yes += 1;
    } else {
      sync_no += 1;
    }

    // query to update sync table with updated data for the current dance set
    updateSyncQuery =
      "UPDATE sync SET yes_sync=" +
      sync_yes +
      ",no_sync=" +
      sync_no +
      "WHERE dance_set=" +
      dance_id;

    try {
      await client
        .query(updateSyncQuery)
        .then((res) => console.log("Sync Update OK"));
    } catch (err) {
      console.error(err.stack);
    }
  }

  var danceMove = payload.dance_move;
  var dancer_left = left_dancer.slice(1, -1);
  var dancer_center = center_dancer.slice(1, -1);
  var dancer_right = right_dancer.slice(1, -1);
  var diff = payload.difference;

  var predicted_data =
    danceMove +
    "." +
    dancer_left +
    "\xa0\xa0\xa0\xa0\xa0" +
    dancer_center +
    "\xa0\xa0\xa0\xa0\xa0" +
    dancer_right;

  var table_data =
    dance_id +
    "," +
    danceMove +
    "," +
    dancer_left +
    "," +
    dancer_center +
    "," +
    dancer_right +
    "," +
    diff.toString();

  var sync_data =
    dance_id + "," + sync_yes.toString() + "," + sync_no.toString();

  // send whether data is available or not (since have data, send false),
  // predicted data (dance move and dancers in the 3 positions)
  // data for table (dance set number, dance move, dancers in the 3 positions and difference in timing)
  // data for pie (dance set number, sync_yes, sync_no)
  io.sockets.emit("dataNotAvailable", false);
  io.sockets.emit("predictedData", predicted_data);
  io.sockets.emit("newTableData", table_data);
  io.sockets.emit("sendNewPieData", sync_data);

  // Modify this part to insert null values to dailytracker
  // If statements to check if any of the dancers are "-" or not
  // If "-", then do not run the queries, else run queries
  // Remember to set dancer1_min_calculated, dancer2_min_calculated
  // and dancer3_min_calculated to NULL before the If-statements
  // Modify dancedata, dance and dailytracker timestamps to accept NULL
  if (payload.dance_move == "End") {
    // send whether data is available or not
    // (since End move represents end of the dance set, send true),
    io.sockets.emit("dataNotAvailable", true);
    if (dancer_1 != "-") {
      // query to get the start time for dancer 1
      // i.e. the time at which dancer 1 started performing the Start move
      var getDancer1TimeStartQuery =
        "SELECT left_time AS dancer1_start FROM dance WHERE dance_move='Start' AND dance_set=" +
        dance_id +
        " AND left_dancer='" +
        dancer_1 +
        "' UNION SELECT center_time AS dancer1_start FROM dance WHERE dance_move='Start' AND dance_set=" +
        dance_id +
        " AND center_dancer='" +
        dancer_1 +
        "' UNION SELECT right_time AS dancer1_start FROM dance WHERE dance_move='Start' AND dance_set=" +
        dance_id +
        " AND right_dancer='" +
        dancer_1 +
        "'";

      // query to get the end time for dancer 1
      // i.e. the time at which dancer 1 started performing the End move
      var getDancer1TimeEndQuery =
        "SELECT left_time AS dancer1_end FROM dance WHERE dance_move='End' AND dance_set=" +
        dance_id +
        " AND left_dancer='" +
        dancer_1 +
        "' UNION SELECT center_time AS dancer1_end FROM dance WHERE dance_move='End' AND dance_set=" +
        dance_id +
        " AND center_dancer='" +
        dancer_1 +
        "' UNION SELECT right_time AS dancer1_end FROM dance WHERE dance_move='End' AND dance_set=" +
        dance_id +
        " AND right_dancer='" +
        dancer_1 +
        "'";

      try {
        // get start time for dancer 1
        await client.query(getDancer1TimeStartQuery).then((res) => {
          let result = res.rows[0];
          dancer1TimeStart = result.dancer1_start;
          console.log("getDancer1StartTime: " + dancer1TimeStart);
        });
      } catch (err) {
        console.error(err.stack);
      }

      try {
        // get end time for dancer 1
        await client.query(getDancer1TimeEndQuery).then((res) => {
          let result = res.rows[0];
          dancer1TimeEnd = result.dancer1_end;
          console.log("getDancer1EndTime: " + dancer1TimeEnd);
        });
      } catch (err) {
        console.error(err.stack);
      }

      // convert the start times for dancers 1, 2 and 3 into milliseconds for easy calculation
      // 1 s = 1000 ms
      // 1 min = 60 000 ms
      // 1 hour = 3 600 000 ms
      var dancer1TimeStartSplit = dancer1TimeStart.split(":");
      // to handle the case where the time is midnight/past midnight, due to 24 hour format
      if (dancer1TimeStartSplit[0] == "00") {
        var dancer1TimeStartHourInMilli = 24 * 3600000;
      } else {
        var dancer1TimeStartHourInMilli =
          parseInt(dancer1TimeStartSplit[0]) * 3600000;
      }
      var dancer1TimeStartMinInMilli =
        parseInt(dancer1TimeStartSplit[1]) * 60000;

      if (dancer1TimeStart.indexOf(".") > -1) {
        var dancer1TimeStartSecInMilli =
          parseInt(dancer1TimeStartSplit[2].split(".")[0]) * 1000;
        var dancer1TimeStartMilli = parseInt(
          dancer1TimeStartSplit[2].split(".")[1]
        );
        var dancer1TimeStartinMilli =
          dancer1TimeStartHourInMilli +
          dancer1TimeStartMinInMilli +
          dancer1TimeStartSecInMilli +
          dancer1TimeStartMilli;
      } else {
        var dancer1TimeStartSecInMilli =
          parseInt(dancer1TimeStartSplit[2]) * 1000;
        var dancer1TimeStartinMilli =
          dancer1TimeStartHourInMilli +
          dancer1TimeStartMinInMilli +
          dancer1TimeStartSecInMilli;
      }

      console.log("Dancer1 Time Start Milli: " + dancer1TimeStartinMilli);

      // convert the end times for dancers 1, 2 and 3 into milliseconds for easy calculation
      // 1 s = 1000 ms
      // 1 min = 60 000 ms
      // 1 hour = 3 600 000 ms
      var dancer1TimeEndSplit = dancer1TimeEnd.split(":");
      if (dancer1TimeEndSplit[0] == "00") {
        var dancer1TimeEndHourInMilli = 24 * 3600000;
      } else {
        var dancer1StartTimeHour = parseInt(dancer1TimeStartSplit[0]);
        var dancer1EndTimeHour = parseInt(dancer1TimeEndSplit[0]);
        if (dancer1StartTimeHour > dancer1EndTimeHour) {
          // add 1 day i.e. 24 hours
          dancer1EndTimeHour += 24;
        }
        var dancer1TimeEndHourInMilli = dancer1EndTimeHour * 3600000;
      }
      var dancer1TimeEndMinInMilli = parseInt(dancer1TimeEndSplit[1]) * 60000;

      if (dancer1TimeEnd.indexOf(".") > -1) {
        var dancer1TimeEndSecInMilli =
          parseInt(dancer1TimeEndSplit[2].split(".")[0]) * 1000;
        var dancer1TimeEndMilli = parseInt(
          dancer1TimeEndSplit[2].split(".")[1]
        );
        var dancer1TimeEndinMilli =
          dancer1TimeEndHourInMilli +
          dancer1TimeEndMinInMilli +
          dancer1TimeEndSecInMilli +
          dancer1TimeEndMilli;
      } else {
        var dancer1TimeEndSecInMilli = parseInt(dancer1TimeEndSplit[2]) * 1000;
        var dancer1TimeEndinMilli =
          dancer1TimeEndHourInMilli +
          dancer1TimeEndMinInMilli +
          dancer1TimeEndSecInMilli;
      }

      console.log("Dancer1 Time End Milli: " + dancer1TimeEndinMilli);

      // calculate the time dancers 1, 2 and 3 practiced for the dance set (in minutes)
      var dancer1_milli_calculated =
        dancer1TimeEndinMilli - dancer1TimeStartinMilli;
      dancer1_min_calculated = Math.trunc(dancer1_milli_calculated / 60000.0);
      console.log("Diff in time Dancer 1: " + dancer1_min_calculated);
    }

    if (dancer_2 != "-") {
      // query to get the start time for dancer 2
      // i.e. the time at which dancer 2 started performing the Start move
      var getDancer2TimeStartQuery =
        "SELECT left_time AS dancer2_start FROM dance WHERE dance_move='Start' AND dance_set=" +
        dance_id +
        " AND left_dancer='" +
        dancer_2 +
        "' UNION SELECT center_time AS dancer2_start FROM dance WHERE dance_move='Start' AND dance_set=" +
        dance_id +
        " AND center_dancer='" +
        dancer_2 +
        "' UNION SELECT right_time AS dancer2_start FROM dance WHERE dance_move='Start' AND dance_set=" +
        dance_id +
        " AND right_dancer='" +
        dancer_2 +
        "'";

      // query to get the end time for dancer 2
      // i.e. the time at which dancer 2 started performing the End move
      var getDancer2TimeEndQuery =
        "SELECT left_time AS dancer2_end FROM dance WHERE dance_move='End' AND dance_set=" +
        dance_id +
        " AND left_dancer='" +
        dancer_2 +
        "' UNION SELECT center_time AS dancer2_end FROM dance WHERE dance_move='End' AND dance_set=" +
        dance_id +
        " AND center_dancer='" +
        dancer_2 +
        "' UNION SELECT right_time AS dancer2_end FROM dance WHERE dance_move='End' AND dance_set=" +
        dance_id +
        " AND right_dancer='" +
        dancer_2 +
        "'";

      try {
        // get start time for dancer 2
        await client.query(getDancer2TimeStartQuery).then((res) => {
          let result = res.rows[0];
          dancer2TimeStart = result.dancer2_start;
          console.log("getDancer2StartTime: " + dancer2TimeStart);
        });
      } catch (err) {
        console.error(err.stack);
      }

      try {
        // get end time for dancer 2
        await client.query(getDancer2TimeEndQuery).then((res) => {
          let result = res.rows[0];
          dancer2TimeEnd = result.dancer2_end;
          console.log("getDancer2EndTime: " + dancer2TimeEnd);
        });
      } catch (err) {
        console.error(err.stack);
      }

      var dancer2TimeStartSplit = dancer2TimeStart.split(":");
      if (dancer2TimeStartSplit[0] == "00") {
        var dancer2TimeStartHourInMilli = 24 * 3600000;
      } else {
        var dancer2TimeStartHourInMilli =
          parseInt(dancer2TimeStartSplit[0]) * 3600000;
      }
      var dancer2TimeStartMinInMilli =
        parseInt(dancer2TimeStartSplit[1]) * 60000;

      if (dancer2TimeStart.indexOf(".") > -1) {
        var dancer2TimeStartSecInMilli =
          parseInt(dancer2TimeStartSplit[2].split(".")[0]) * 1000;
        var dancer2TimeStartMilli = parseInt(
          dancer2TimeStartSplit[2].split(".")[1]
        );
        var dancer2TimeStartinMilli =
          dancer2TimeStartHourInMilli +
          dancer2TimeStartMinInMilli +
          dancer2TimeStartSecInMilli +
          dancer2TimeStartMilli;
      } else {
        var dancer2TimeStartSecInMilli =
          parseInt(dancer2TimeStartSplit[2]) * 1000;
        var dancer2TimeStartinMilli =
          dancer2TimeStartHourInMilli +
          dancer2TimeStartMinInMilli +
          dancer2TimeStartSecInMilli;
      }

      console.log("Dancer2 Time Start Milli: " + dancer2TimeStartinMilli);

      var dancer2TimeEndSplit = dancer2TimeEnd.split(":");
      if (dancer2TimeEndSplit[0] == "00") {
        var dancer2TimeEndHourInMilli = 24 * 3600000;
      } else {
        var dancer2StartTimeHour = parseInt(dancer2TimeStartSplit[0]);
        var dancer2EndTimeHour = parseInt(dancer2TimeEndSplit[0]);
        if (dancer2StartTimeHour > dancer2EndTimeHour) {
          // add 1 day i.e. 24 hours
          dancer2EndTimeHour += 24;
        }
        var dancer2TimeEndHourInMilli = dancer2EndTimeHour * 3600000;
      }
      var dancer2TimeEndMinInMilli = parseInt(dancer2TimeEndSplit[1]) * 60000;

      if (dancer2TimeEnd.indexOf(".") > -1) {
        var dancer2TimeEndSecInMilli =
          parseInt(dancer2TimeEndSplit[2].split(".")[0]) * 1000;
        var dancer2TimeEndMilli = parseInt(
          dancer2TimeEndSplit[2].split(".")[1]
        );
        var dancer2TimeEndinMilli =
          dancer2TimeEndHourInMilli +
          dancer2TimeEndMinInMilli +
          dancer2TimeEndSecInMilli +
          dancer2TimeEndMilli;
      } else {
        var dancer2TimeEndSecInMilli = parseInt(dancer2TimeEndSplit[2]) * 1000;
        var dancer2TimeEndinMilli =
          dancer2TimeEndHourInMilli +
          dancer2TimeEndMinInMilli +
          dancer2TimeEndSecInMilli;
      }

      console.log("Dancer2 Time End Milli: " + dancer2TimeEndinMilli);

      var dancer2_milli_calculated =
        dancer2TimeEndinMilli - dancer2TimeStartinMilli;
      dancer2_min_calculated = Math.trunc(dancer2_milli_calculated / 60000.0);
      console.log("Diff in time Dancer 2: " + dancer2_min_calculated);
    }

    if (dancer_3 != "-") {
      // query to get the start time for dancer 3
      // i.e. the time at which dancer 3 started performing the Start move
      var getDancer3TimeStartQuery =
        "SELECT left_time AS dancer3_start FROM dance WHERE dance_move='Start' AND dance_set=" +
        dance_id +
        " AND left_dancer='" +
        dancer_3 +
        "' UNION SELECT center_time AS dancer3_start FROM dance WHERE dance_move='Start' AND dance_set=" +
        dance_id +
        " AND center_dancer='" +
        dancer_3 +
        "' UNION SELECT right_time AS dancer3_start FROM dance WHERE dance_move='Start' AND dance_set=" +
        dance_id +
        " AND right_dancer='" +
        dancer_3 +
        "'";

      // query to get the end time for dancer 3
      // i.e. the time at which dancer 3 started performing the End move
      var getDancer3TimeEndQuery =
        "SELECT left_time AS dancer3_end FROM dance WHERE dance_move='End' AND dance_set=" +
        dance_id +
        " AND left_dancer='" +
        dancer_3 +
        "' UNION SELECT center_time AS dancer3_end FROM dance WHERE dance_move='End' AND dance_set=" +
        dance_id +
        " AND center_dancer='" +
        dancer_3 +
        "' UNION SELECT right_time AS dancer3_end FROM dance WHERE dance_move='End' AND dance_set=" +
        dance_id +
        " AND right_dancer='" +
        dancer_3 +
        "'";

      try {
        // get start time for dancer 3
        await client.query(getDancer3TimeStartQuery).then((res) => {
          let result = res.rows[0];
          dancer3TimeStart = result.dancer3_start;
          console.log("getDancer3StartTime: " + dancer3TimeStart);
        });
      } catch (err) {
        console.error(err.stack);
      }

      try {
        // get end time for dancer 3
        await client.query(getDancer3TimeEndQuery).then((res) => {
          let result = res.rows[0];
          dancer3TimeEnd = result.dancer3_end;
          console.log("getDancer3EndTime: " + dancer3TimeEnd);
        });
      } catch (err) {
        console.error(err.stack);
      }

      var dancer3TimeStartSplit = dancer3TimeStart.split(":");
      if (dancer3TimeStartSplit[0] == "00") {
        var dancer3TimeStartHourInMilli = 24 * 3600000;
      } else {
        var dancer3TimeStartHourInMilli =
          parseInt(dancer3TimeStartSplit[0]) * 3600000;
      }
      var dancer3TimeStartMinInMilli =
        parseInt(dancer3TimeStartSplit[1]) * 60000;

      if (dancer3TimeStart.indexOf(".") > -1) {
        var dancer3TimeStartSecInMilli =
          parseInt(dancer3TimeStartSplit[2].split(".")[0]) * 1000;
        var dancer3TimeStartMilli = parseInt(
          dancer3TimeStartSplit[2].split(".")[1]
        );
        var dancer3TimeStartinMilli =
          dancer3TimeStartHourInMilli +
          dancer3TimeStartMinInMilli +
          dancer3TimeStartSecInMilli +
          dancer3TimeStartMilli;
      } else {
        var dancer3TimeStartSecInMilli =
          parseInt(dancer3TimeStartSplit[2]) * 1000;
        var dancer3TimeStartinMilli =
          dancer3TimeStartHourInMilli +
          dancer3TimeStartMinInMilli +
          dancer3TimeStartSecInMilli;
      }

      console.log("Dancer3 Time Start Milli: " + dancer3TimeStartinMilli);

      var dancer3TimeEndSplit = dancer3TimeEnd.split(":");
      if (dancer3TimeEndSplit[0] == "00") {
        var dancer3TimeEndHourInMilli = 24 * 3600000;
      } else {
        var dancer3StartTimeHour = parseInt(dancer3TimeStartSplit[0]);
        var dancer3EndTimeHour = parseInt(dancer3TimeEndSplit[0]);
        if (dancer3StartTimeHour > dancer3EndTimeHour) {
          // add 1 day i.e. 24 hours
          dancer3EndTimeHour += 24;
        }
        var dancer3TimeEndHourInMilli = dancer3EndTimeHour * 3600000;
      }
      var dancer3TimeEndMinInMilli = parseInt(dancer3TimeEndSplit[1]) * 60000;

      if (dancer3TimeEnd.indexOf(".") > -1) {
        var dancer3TimeEndSecInMilli =
          parseInt(dancer3TimeEndSplit[2].split(".")[0]) * 1000;
        var dancer3TimeEndMilli = parseInt(
          dancer3TimeEndSplit[2].split(".")[1]
        );
        var dancer3TimeEndinMilli =
          dancer3TimeEndHourInMilli +
          dancer3TimeEndMinInMilli +
          dancer3TimeEndSecInMilli +
          dancer3TimeEndMilli;
      } else {
        var dancer3TimeEndSecInMilli = parseInt(dancer3TimeEndSplit[2]) * 1000;
        var dancer3TimeEndinMilli =
          dancer3TimeEndHourInMilli +
          dancer3TimeEndMinInMilli +
          dancer3TimeEndSecInMilli;
      }
      console.log("Dancer3 Time End Milli: " + dancer3TimeEndinMilli);

      var dancer3_milli_calculated =
        dancer3TimeEndinMilli - dancer3TimeStartinMilli;
      dancer3_min_calculated = Math.trunc(dancer3_milli_calculated / 60000.0);
      console.log("Diff in time Dancer 3: " + dancer3_min_calculated);
    }

    // query to insert the data into dailytracker table
    var insertDailyTrackerQuery =
      "INSERT INTO dailytracker VALUES (" +
      dance_id +
      ",'" +
      payload.date +
      "','" +
      dancer_1 +
      "'," +
      dancer1_min_calculated +
      ",'" +
      dancer_2 +
      "'," +
      dancer2_min_calculated +
      ",'" +
      dancer_3 +
      "'," +
      dancer3_min_calculated +
      ")";

    try {
      // insert the data into dailytracker table
      await client
        .query(insertDailyTrackerQuery)
        .then((res) => console.log("DailyTracker Insertion OK"));
    } catch (err) {
      console.error(err.stack);
    }

    // query to insert the data into dailysets table
    // the dance set number, date and who participated in this dance set
    var insertDailySetsQuery =
      "INSERT INTO dailysets VALUES (" +
      dance_id +
      ",'" +
      payload.date +
      "'," +
      dancers +
      ")";

    try {
      // insert the data into dailysets table
      await client
        .query(insertDailySetsQuery)
        .then((res) => console.log("Dailysets Insertion OK"));
    } catch (err) {
      console.error(err.stack);
    }
  }
});

app.use(cors());
// to support JSON-encoded bodies
app.use(bodyParser.json());

app.use(
  bodyParser.urlencoded({
    // to support URL-encoded bodies
    extended: false,
  })
);

// to support JSON-encoded bodies
app.use(express.json());

// to support URL-encoded bodies
app.use(express.urlencoded({ extended: true }));

// get all past dance sets data that are available (both table and pie chart data) to send to client
app.get("/dashboard/past-data", async function (req, res) {
  // get the data for table ordered by dance set number in descending order
  // and move number in ascending order
  const sendAllTableData =
    "SELECT dance_set,dates,move_number,dance_move,left_time,left_dancer,center_time,center_dancer,right_time,right_dancer,difference,sync FROM dance ORDER BY dance_set DESC, move_number ASC";

  // get the data for pie ordered by dance set number in descending order
  const sendAllPieData =
    "SELECT dance_set,dates,yes_sync,no_sync FROM sync ORDER BY dance_set DESC";

  // to package the data in one JSON object to send to client
  var dataObject = { tableData: {}, pieData: {} };

  try {
    // get table data from query and push into an array arr
    // then insert it into tableData of dataObject
    await client.query(sendAllTableData).then((resp) => {
      let arr = [];
      let len = resp.rows.length;
      for (var i = 0; i < len; i++) {
        let result = resp.rows[i];
        arr.push(result);
      }
      dataObject.tableData = arr;
    });
  } catch (err) {
    console.error(err.stack);
  }

  try {
    // get pie data from query and push into an array pieArr
    // then insert it into pieData of dataObject
    // then send the JSON Object to client
    await client.query(sendAllPieData).then((resp) => {
      let pieArr = [];
      let pieLen = resp.rows.length;
      for (var i = 0; i < pieLen; i++) {
        let result = resp.rows[i];
        pieArr.push(result);
      }
      dataObject.pieData = pieArr;
      res.send(JSON.stringify(dataObject));
    });
  } catch (err) {
    console.error(err.stack);
  }
});

// receive data regarding what information users would like to observe
app.post("/dashboard/past-data", async function (req, res) {
  console.log("Received Past Data request: ", req.body);
  var chartsRequired = req.body.pastData.chart,
    dancerNames = req.body.pastData.dancers,
    datesRequired = req.body.pastData.dates,
    searchCharts = req.body.pastData.search;

  console.log(chartsRequired);
  console.log(dancerNames);
  console.log(datesRequired);
  console.log(searchCharts);

  var completeRequestPastData = "";
  var completeRequestPastData1 = "";
  var baseRequest = "";
  if (dancerNames != null) {
    var dancerQueryString = dancerNames.replace(/,/g, "%");
  }

  // to package the data into one JSON Object to send to client
  var dataObj = { tableData: {}, pieData: {} };

  if (datesRequired == null && dancerNames == null && searchCharts == null) {
    if (chartsRequired === "Table") {
      // if no specific dates, dancers or dance sets are provided and chart type is table
      // get data in descending order of dance set number because showing latest set information first
      completeRequestPastData =
        "SELECT dance_set,dates,move_number,dance_move,left_time,left_dancer,center_time,center_dancer,right_time,right_dancer,difference,sync FROM dance ORDER BY dance_set DESC, move_number ASC";

      try {
        // get the table data from dance and send it to client
        await client.query(completeRequestPastData).then((resp) => {
          let onlyTableData = [];
          let len = resp.rows.length;
          for (var i = 0; i < len; i++) {
            let result = resp.rows[i];
            onlyTableData.push(result);
          }
          dataObj.tableData = onlyTableData;
          res.send(JSON.stringify(dataObj));
        });
      } catch (err) {
        console.error(err.stack);
      }
    } else if (chartsRequired === "Pie") {
      // else if no specific dates, dancers or dance sets are provided and chart type is pie
      // get data in descending order of dance set number because showing latest set information first
      completeRequestPastData =
        "SELECT dance_set,dates,yes_sync,no_sync FROM sync ORDER BY dance_set DESC";
      try {
        // get pie chart data from sync and send it to client
        await client.query(completeRequestPastData).then((resp) => {
          let onlyPieData = [];
          let len = resp.rows.length;
          for (var i = 0; i < len; i++) {
            let result = resp.rows[i];
            onlyPieData.push(result);
          }
          dataObj.pieData = onlyPieData;
          res.send(JSON.stringify(dataObj));
        });
      } catch (err) {
        console.error(err.stack);
      }
    } else {
      // if no specific dates, dancers, dance sets or chart types are provided
      // get data in descending order of dance set number because showing latest set information first
      completeRequestPastData =
        "SELECT dance_set,dates,move_number,dance_move,left_time,left_dancer,center_time,center_dancer,right_time,right_dancer,difference,sync FROM dance ORDER BY dance_set DESC, move_number ASC";
      completeRequestPastData1 =
        "SELECT dance_set,dates,yes_sync,no_sync FROM sync ORDER BY dance_set DESC";

      try {
        // get table data from dance and insert it into tableData of JSON Object
        await client.query(completeRequestPastData).then((resp) => {
          let arr = [];
          let len = resp.rows.length;
          for (var i = 0; i < len; i++) {
            let result = resp.rows[i];
            arr.push(result);
          }
          dataObj.tableData = arr;
        });
      } catch (err) {
        console.error(err.stack);
      }

      try {
        // get pie data from sync and insert it into pieData of JSON Object
        // send the JSON Object to client
        await client.query(completeRequestPastData1).then((resp) => {
          let pieArr = [];
          let pieLen = resp.rows.length;
          for (var i = 0; i < pieLen; i++) {
            let result = resp.rows[i];
            pieArr.push(result);
          }
          dataObj.pieData = pieArr;
          res.send(JSON.stringify(dataObj));
        });
      } catch (err) {
        console.error(err.stack);
      }
    }
  } else {
    if (chartsRequired === "Table") {
      // if specific dates and/or dancers and/or dance sets are provided
      // and chart type is table
      // SELECT query that will be used as the base before adding all the conditions for WHERE
      baseRequest =
        "SELECT dance_set,dates,move_number,dance_move,left_time,left_dancer,center_time,center_dancer,right_time,right_dancer,difference,sync FROM dance WHERE ";

      // if dancer names are provided, include them in the query using pattern matching
      if (dancerNames != null) {
        var dancers = "(dancers LIKE '%" + dancerQueryString + "%')";
        baseRequest += dancers;
      }

      // if specific dates are provided
      if (datesRequired != null) {
        // if there are dancer names provided then add AND to query
        if (baseRequest[baseRequest.length - 1] == ")") {
          baseRequest += " AND ";
        }
        // add the dates to query using OR for each date
        var dates = " (dates='";
        datesRequired = datesRequired.replace(/,/g, "' OR dates='");
        dates += datesRequired + "')";
        baseRequest += dates;
      }

      // if specific dance sets are provided
      if (searchCharts != null) {
        // if there are other conditions before this add AND to query
        if (baseRequest[baseRequest.length - 1] == ")") {
          baseRequest += " AND ";
        }

        // add the specific dance sets to the query using OR for each dance set
        var danceSet = " (dance_set=";
        searchCharts = searchCharts.replace(/,/g, " OR dance_set=");
        danceSet += searchCharts + ")";
        baseRequest += danceSet;
      }

      completeRequestPastData =
        baseRequest + " ORDER BY dance_set DESC, move_number ASC";
      // console.log(completeRequestPastData);
      try {
        // get the table data fitting the conditions in the query,
        // insert into tableData of JSON Object and send it back to client
        await client.query(completeRequestPastData).then((resp) => {
          let onlyTableData = [];
          let len = resp.rows.length;
          for (var i = 0; i < len; i++) {
            let result = resp.rows[i];
            onlyTableData.push(result);
          }
          dataObj.tableData = onlyTableData;
          res.send(JSON.stringify(dataObj));
        });
      } catch (err) {
        console.error(err.stack);
      }
    } else if (chartsRequired === "Pie") {
      // if specific dates and/or dancers and/or dance sets are provided
      // and chart type is pie
      // SELECT query that will be used as the base before adding all the conditions for WHERE
      baseRequest = "SELECT dance_set,dates,yes_sync,no_sync FROM sync WHERE";

      // if dancer names are provided, include them in the query using pattern matching
      if (dancerNames != null) {
        var dancers = "(dancers LIKE '%" + dancerQueryString + "%')";
        baseRequest += dancers;
      }

      // if specific dates are provided
      if (datesRequired != null) {
        // if there are dancer names provided then add AND to query
        if (baseRequest[baseRequest.length - 1] == ")") {
          baseRequest += " AND ";
        }
        // add the dates to query using OR for each date
        var dates = " (dates='";
        datesRequired = datesRequired.replace(/,/g, "' OR dates='");
        dates += datesRequired + "')";
        baseRequest += dates;
      }

      // if specific dance sets are provided
      if (searchCharts != null) {
        // if there are other conditions before this add AND to query
        if (baseRequest[baseRequest.length - 1] == ")") {
          baseRequest += " AND ";
        }
        // add the specific dance sets to the query using OR for each dance set
        var danceSet = " (dance_set=";
        searchCharts = searchCharts.replace(/,/g, " OR dance_set=");
        danceSet += searchCharts + ")";
        baseRequest += danceSet;
      }

      completeRequestPastData = baseRequest + " ORDER BY dance_set DESC";
      // console.log(completeRequestPastData);
      try {
        await client.query(completeRequestPastData).then((resp) => {
          let onlyPieData = [];
          let len = resp.rows.length;
          for (var i = 0; i < len; i++) {
            let result = resp.rows[i];
            onlyPieData.push(result);
          }
          dataObj.pieData = onlyPieData;
          res.send(JSON.stringify(dataObj));
        });
      } catch (err) {
        console.error(err.stack);
      }
    } else {
      // if specific dates and/or dancers and/or dance sets are provided
      // and chart type is not provided i.e. provide data for both table and pie chart
      // SELECT queries that will be used as the base before adding all the conditions for WHERE
      var baseRequestDance =
        "SELECT dance_set,dates,move_number,dance_move,left_time,left_dancer,center_time,center_dancer,right_time,right_dancer,difference,sync FROM dance WHERE";
      var baseRequestSync =
        "SELECT dance_set,dates,yes_sync,no_sync FROM sync WHERE";

      // if dancer names are provided, include them in the queries using pattern matching
      if (dancerNames != null) {
        var dancers = " (dancers LIKE '%" + dancerQueryString + "%')";
        baseRequestDance += dancers;
        baseRequestSync += dancers;
      }

      // if specific dates are provided
      if (datesRequired != null) {
        // if there are other conditions before this add AND to queries
        if (baseRequestDance[baseRequestDance.length - 1] == ")") {
          baseRequestDance += " AND ";
        }
        if (baseRequestSync[baseRequestSync.length - 1] == ")") {
          baseRequestSync += " AND ";
        }
        // add the dates to queries using OR for each date
        var dates = " (dates='";
        datesRequired = datesRequired.replace(/,/g, "' OR dates='");
        dates += datesRequired + "')";
        baseRequestDance += dates;
        baseRequestSync += dates;
      }

      // if specific dance sets are provided
      if (searchCharts != null) {
        // if there are other conditions before this add AND to queries
        if (baseRequestDance[baseRequestDance.length - 1] == ")") {
          baseRequestDance += " AND ";
        }
        if (baseRequestSync[baseRequestSync.length - 1] == ")") {
          baseRequestSync += " AND ";
        }
        // add the specific dance sets to the queries using OR for each dance set
        var danceSet = " (dance_set=";
        searchCharts = searchCharts.replace(/,/g, " OR dance_set=");
        danceSet += searchCharts + ")";
        baseRequestDance += danceSet;
        baseRequestSync += danceSet;
      }
      completeRequestPastData =
        baseRequestDance + " ORDER BY dance_set DESC, move_number ASC";
      completeRequestPastData1 = baseRequestSync + " ORDER BY dance_set DESC";
      // console.log(completeRequestPastData);
      // console.log(completeRequestPastData1);
      try {
        // get the table data from dance fitting the conditions in the query
        // and insert into tableData of JSON Object
        await client.query(completeRequestPastData).then((resp) => {
          let arr = [];
          let len = resp.rows.length;
          for (var i = 0; i < len; i++) {
            let result = resp.rows[i];
            arr.push(result);
          }
          dataObj.tableData = arr;
        });
      } catch (err) {
        console.error(err.stack);
      }

      try {
        // get the pie data from sync fitting the conditions in the query
        // and insert it into pieData of JSON Object
        // send the JSON Object to client
        await client.query(completeRequestPastData1).then((resp) => {
          let pieArr = [];
          let pieLen = resp.rows.length;
          for (var i = 0; i < pieLen; i++) {
            let result = resp.rows[i];
            pieArr.push(result);
          }
          dataObj.pieData = pieArr;
          res.send(JSON.stringify(dataObj));
        });
      } catch (err) {
        console.error(err.stack);
      }
    }
  }
});

// send all information regarding the dancers
// time spent by each dancer for the current week so far
// number of dance sets completed by each dancer for the current week so far
app.get("/dashboard/dancers", async function (req, res) {
  // get the date of Monday and Sunday of current week
  var date = new Date();
  var diff = date.getDate() - date.getDay() + (date.getDay() === 0 ? -6 : 1);
  var mondayDate = new Date(date.setDate(diff));
  mondayDate = mondayDate.toString();
  mondayDate = new Date(mondayDate);
  var sundayDate = new Date(date.setDate(diff + 6));
  sundayDate = sundayDate.toString();
  console.log(sundayDate);
  sundayDate = new Date(sundayDate);

  mondayDate = mondayDate.toISOString().substr(0, 10);
  sundayDate = sundayDate.toISOString().substr(0, 10);
  var sundayDateCheckDD = sundayDate.split("-")[2];
  var mondayDateCheckDD = mondayDate.split("-")[2];
  if (sundayDateCheckDD < mondayDateCheckDD) {
    var sundayDateCheckMM = parseInt(sundayDate.split("-")[1]) + 1;
    sundayDateCheckDD = parseInt(sundayDate.split("-")[2]) + 1;
    if (sundayDateCheckDD.length < 2) {
      sundayDateCheckDD = "0" + sundayDateCheckDD.toString();
    } else {
      sundayDateCheckDD = sundayDateCheckDD.toString();
    }

    if (sundayDateCheckMM.length < 2) {
      sundayDateCheckMM = "0" + sundayDateCheckMM.toString();
    } else {
      sundayDateCheckMM = sundayDateCheckMM.toString();
    }
    sundayDate =
      sundayDate.split("-")[0] +
      "-" +
      sundayDateCheckMM +
      "-" +
      sundayDateCheckDD;

    // sundayDate = new Date(sundayDate);
    console.log("Monday date: " + mondayDate);
    console.log("sunday date: " + sundayDate);
  }
  // console.log("Monday: " + mondayDate.toISOString().substr(0, 10));
  // console.log("Sunday: " + sundayDate.toISOString().substr(0, 10));
  const datesQuery =
    "(date BETWEEN '" + mondayDate + "' AND '" + sundayDate + "')";
  // console.log(datesQuery);

  // query for each of the dancers to get the total time they have practiced for
  // in the current week so far
  const jingxuanTimeQuery =
    "SELECT SUM(sumofminutes.jingxuantime) FROM (SELECT SUM(dancer1_minutes) AS jingxuantime FROM dailytracker WHERE dancer1='Jingxuan' AND " +
    datesQuery +
    " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Jingxuan' AND " +
    datesQuery +
    " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Jingxuan' AND " +
    datesQuery +
    ") AS sumofminutes";

  const karanTimeQuery =
    "SELECT SUM(sumofminutes.karantime) FROM (SELECT SUM(dancer1_minutes) AS karantime FROM dailytracker WHERE dancer1='Karan' AND " +
    datesQuery +
    " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Karan' AND " +
    datesQuery +
    " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Karan' AND " +
    datesQuery +
    ") AS sumofminutes";

  const kexinTimeQuery =
    "SELECT SUM(sumofminutes.kexintime) FROM (SELECT SUM(dancer1_minutes) AS kexintime FROM dailytracker WHERE dancer1='Kexin' AND " +
    datesQuery +
    " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Kexin' AND " +
    datesQuery +
    " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Kexin' AND " +
    datesQuery +
    ") AS sumofminutes";

  const sarahTimeQuery =
    "SELECT SUM(sumofminutes.sarahtime) FROM (SELECT SUM(dancer1_minutes) AS sarahtime FROM dailytracker WHERE dancer1='Sarah' AND " +
    datesQuery +
    " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Sarah' AND " +
    datesQuery +
    " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Sarah' AND " +
    datesQuery +
    ") AS sumofminutes";

  const tristyTimeQuery =
    "SELECT SUM(sumofminutes.tristytime) FROM (SELECT SUM(dancer1_minutes) AS tristytime FROM dailytracker WHERE dancer1='Tristy' AND " +
    datesQuery +
    " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Tristy' AND " +
    datesQuery +
    " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Tristy' AND " +
    datesQuery +
    ") AS sumofminutes";

  const yunhanTimeQuery =
    "SELECT SUM(sumofminutes.yunhantime) FROM (SELECT SUM(dancer1_minutes) AS yunhantime FROM dailytracker WHERE dancer1='Yunhan' AND " +
    datesQuery +
    " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Yunhan' AND " +
    datesQuery +
    " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Yunhan' AND " +
    datesQuery +
    ") AS sumofminutes";

  // query for each of the dancers to get the total number of sets they have participated
  // in the current week so far
  const jingxuanSetsQuery =
    "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Jingxuan%' AND " +
    datesQuery;

  const karanSetsQuery =
    "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Karan%' AND " +
    datesQuery;

  const kexinSetsQuery =
    "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Kexin%' AND " +
    datesQuery;

  const sarahSetsQuery =
    "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Sarah%' AND " +
    datesQuery;

  const tristySetsQuery =
    "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Tristy%' AND " +
    datesQuery;

  const yunhanSetsQuery =
    "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Yunhan%' AND " +
    datesQuery;

  // to package the data into one JSON Object to send to client
  var dataObject = { timeData: {}, setData: {} };
  var arrTime = [];
  var arrSets = [];

  // get the time spent dancing by each dancer for the current week so far and push into array
  try {
    await client.query(jingxuanTimeQuery).then((resp) => {
      let result = resp.rows[0];
      arrTime.push(result);
    });
  } catch (err) {
    console.error(err.stack);
  }

  try {
    await client.query(karanTimeQuery).then((resp) => {
      let result = resp.rows[0];
      arrTime.push(result);
    });
  } catch (err) {
    console.error(err.stack);
  }

  try {
    await client.query(kexinTimeQuery).then((resp) => {
      let result = resp.rows[0];
      arrTime.push(result);
    });
  } catch (err) {
    console.error(err.stack);
  }

  try {
    await client.query(sarahTimeQuery).then((resp) => {
      let result = resp.rows[0];
      arrTime.push(result);
    });
  } catch (err) {
    console.error(err.stack);
  }

  try {
    await client.query(tristyTimeQuery).then((resp) => {
      let result = resp.rows[0];
      arrTime.push(result);
    });
  } catch (err) {
    console.error(err.stack);
  }

  try {
    await client.query(yunhanTimeQuery).then((resp) => {
      let result = resp.rows[0];
      arrTime.push(result);
      dataObject.timeData = arrTime;
    });
  } catch (err) {
    console.error(err.stack);
  }

  // get the number of sets each dancer participated in for the current week so far
  // and push into array
  try {
    await client.query(jingxuanSetsQuery).then((resp) => {
      let result = resp.rows[0];
      arrSets.push(result);
    });
  } catch (err) {
    console.error(err.stack);
  }

  try {
    await client.query(karanSetsQuery).then((resp) => {
      let result = resp.rows[0];
      arrSets.push(result);
    });
  } catch (err) {
    console.error(err.stack);
  }

  try {
    await client.query(kexinSetsQuery).then((resp) => {
      let result = resp.rows[0];
      arrSets.push(result);
    });
  } catch (err) {
    console.error(err.stack);
  }

  try {
    await client.query(sarahSetsQuery).then((resp) => {
      let result = resp.rows[0];
      arrSets.push(result);
    });
  } catch (err) {
    console.error(err.stack);
  }

  try {
    await client.query(tristySetsQuery).then((resp) => {
      let result = resp.rows[0];
      arrSets.push(result);
    });
  } catch (err) {
    console.error(err.stack);
  }

  // send the JSON Object to client
  try {
    await client.query(yunhanSetsQuery).then((resp) => {
      let result = resp.rows[0];
      arrSets.push(result);
      dataObject.setData = arrSets;
      res.send(JSON.stringify(dataObject));
    });
  } catch (err) {
    console.error(err.stack);
  }
});

// receive data regarding what information users would like to observe
app.post("/dashboard/dancers", async function (req, res) {
  console.log("Received Dancer request: ", req.body);
  // get what charts, dancers and dates are required
  var chartsRequired = req.body.dancerData.chart,
    dancerNames = req.body.dancerData.dancers,
    datesRequired = req.body.dancerData.dates;

  console.log(chartsRequired);
  console.log(dancerNames);
  console.log(datesRequired);
  // res.sendStatus(200);

  var jingxuanTimeQuery = "";
  var karanTimeQuery = "";
  var kexinTimeQuery = "";
  var sarahTimeQuery = "";
  var tristyTimeQuery = "";
  var yunhanTimeQuery = "";
  var jingxuanSetsQuery = "";
  var karanSetsQuery = "";
  var kexinSetsQuery = "";
  var sarahSetsQuery = "";
  var tristySetsQuery = "";
  var yunhanSetsQuery = "";
  var dancerDataObject = { timeData: {}, setData: {} };
  var timeArray = [];
  var setArray = [];

  // get date of Monday and Sunday of current week and use it for the query
  var date = new Date();
  var diff = date.getDate() - date.getDay() + (date.getDay() === 0 ? -6 : 1);
  var mondayDate = new Date(date.setDate(diff));
  mondayDate = mondayDate.toString();
  mondayDate = new Date(mondayDate);
  var sundayDate = new Date(date.setDate(diff + 6));
  sundayDate = sundayDate.toString();
  console.log(sundayDate);
  sundayDate = new Date(sundayDate);

  mondayDate = mondayDate.toISOString().substr(0, 10);
  sundayDate = sundayDate.toISOString().substr(0, 10);
  var sundayDateCheckDD = sundayDate.split("-")[2];
  var mondayDateCheckDD = mondayDate.split("-")[2];
  if (sundayDateCheckDD < mondayDateCheckDD) {
    var sundayDateCheckMM = parseInt(sundayDate.split("-")[1]) + 1;
    sundayDateCheckDD = parseInt(sundayDate.split("-")[2]) + 1;
    if (sundayDateCheckDD.length < 2) {
      sundayDateCheckDD = "0" + sundayDateCheckDD.toString();
    } else {
      sundayDateCheckDD = sundayDateCheckDD.toString();
    }

    if (sundayDateCheckMM.length < 2) {
      sundayDateCheckMM = "0" + sundayDateCheckMM.toString();
    } else {
      sundayDateCheckMM = sundayDateCheckMM.toString();
    }
    sundayDate =
      sundayDate.split("-")[0] +
      "-" +
      sundayDateCheckMM +
      "-" +
      sundayDateCheckDD;

    // sundayDate = new Date(sundayDate);
    console.log("Monday date: " + mondayDate);
    console.log("sunday date: " + sundayDate);
  }
  // console.log("Monday: " + mondayDate.toISOString().substr(0, 10));
  // console.log("Sunday: " + sundayDate.toISOString().substr(0, 10));
  const datesQuery =
    "(date BETWEEN '" + mondayDate + "' AND '" + sundayDate + "')";

  if (datesRequired == null && dancerNames == null) {
    if (chartsRequired === "Time Bar") {
      // if no dates and dancers are given and chart needed is bar chart for time spent

      // queries to get the time spent dancing for each dancer for the current week so far
      jingxuanTimeQuery =
        "SELECT SUM(sumofminutes.jingxuantime) FROM (SELECT SUM(dancer1_minutes) AS jingxuantime FROM dailytracker WHERE dancer1='Jingxuan' AND " +
        datesQuery +
        " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Jingxuan' AND " +
        datesQuery +
        " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Jingxuan' AND " +
        datesQuery +
        ") AS sumofminutes";

      karanTimeQuery =
        "SELECT SUM(sumofminutes.karantime) FROM (SELECT SUM(dancer1_minutes) AS karantime FROM dailytracker WHERE dancer1='Karan' AND " +
        datesQuery +
        " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Karan' AND " +
        datesQuery +
        " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Karan' AND " +
        datesQuery +
        ") AS sumofminutes";

      kexinTimeQuery =
        "SELECT SUM(sumofminutes.kexintime) FROM (SELECT SUM(dancer1_minutes) AS kexintime FROM dailytracker WHERE dancer1='Kexin' AND " +
        datesQuery +
        " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Kexin' AND " +
        datesQuery +
        " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Kexin' AND " +
        datesQuery +
        ") AS sumofminutes";

      sarahTimeQuery =
        "SELECT SUM(sumofminutes.sarahtime) FROM (SELECT SUM(dancer1_minutes) AS sarahtime FROM dailytracker WHERE dancer1='Sarah' AND " +
        datesQuery +
        " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Sarah' AND " +
        datesQuery +
        " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Sarah' AND " +
        datesQuery +
        ") AS sumofminutes";

      tristyTimeQuery =
        "SELECT SUM(sumofminutes.tristytime) FROM (SELECT SUM(dancer1_minutes) AS tristytime FROM dailytracker WHERE dancer1='Tristy' AND " +
        datesQuery +
        " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Tristy' AND " +
        datesQuery +
        " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Tristy' AND " +
        datesQuery +
        ") AS sumofminutes";

      yunhanTimeQuery =
        "SELECT SUM(sumofminutes.yunhantime) FROM (SELECT SUM(dancer1_minutes) AS yunhantime FROM dailytracker WHERE dancer1='Yunhan' AND " +
        datesQuery +
        " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Yunhan' AND " +
        datesQuery +
        " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Yunhan' AND " +
        datesQuery +
        ") AS sumofminutes";

      // get the data for each dancer and push it into the array for time spent
      // after getting data for all dancers in the array
      // insert array into timeData for JSON Object and send the Object to client
      try {
        await client.query(jingxuanTimeQuery).then((resp) => {
          let result = resp.rows[0];
          timeArray.push(result);
        });
      } catch (err) {
        console.error(err.stack);
      }

      try {
        await client.query(karanTimeQuery).then((resp) => {
          let result = resp.rows[0];
          timeArray.push(result);
        });
      } catch (err) {
        console.error(err.stack);
      }

      try {
        await client.query(kexinTimeQuery).then((resp) => {
          let result = resp.rows[0];
          timeArray.push(result);
        });
      } catch (err) {
        console.error(err.stack);
      }

      try {
        await client.query(sarahTimeQuery).then((resp) => {
          let result = resp.rows[0];
          timeArray.push(result);
        });
      } catch (err) {
        console.error(err.stack);
      }

      try {
        await client.query(tristyTimeQuery).then((resp) => {
          let result = resp.rows[0];
          timeArray.push(result);
        });
      } catch (err) {
        console.error(err.stack);
      }

      try {
        await client.query(yunhanTimeQuery).then((resp) => {
          let result = resp.rows[0];
          timeArray.push(result);
          dancerDataObject.timeData = timeArray;
          res.send(JSON.stringify(dancerDataObject));
        });
      } catch (err) {
        console.error(err.stack);
      }
    } else if (chartsRequired === "Set Bar") {
      // if no dates and dancers are given and chart needed is bar chart for number of sets done

      // queries to get number of sets done by each dancer for the current week so far
      // and insert the data into array for number of sets done
      // after getting all the data, insert the array for number of sets to setData of JSON Object
      // and send Object to client
      jingxuanSetsQuery =
        "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Jingxuan%' AND " +
        datesQuery;

      karanSetsQuery =
        "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Karan%' AND " +
        datesQuery;

      kexinSetsQuery =
        "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Kexin%' AND " +
        datesQuery;

      sarahSetsQuery =
        "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Sarah%' AND " +
        datesQuery;

      tristySetsQuery =
        "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Tristy%' AND " +
        datesQuery;

      yunhanSetsQuery =
        "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Yunhan%' AND " +
        datesQuery;

      try {
        await client.query(jingxuanSetsQuery).then((resp) => {
          let result = resp.rows[0];
          setArray.push(result);
        });
      } catch (err) {
        console.error(err.stack);
      }

      try {
        await client.query(karanSetsQuery).then((resp) => {
          let result = resp.rows[0];
          setArray.push(result);
        });
      } catch (err) {
        console.error(err.stack);
      }

      try {
        await client.query(kexinSetsQuery).then((resp) => {
          let result = resp.rows[0];
          setArray.push(result);
        });
      } catch (err) {
        console.error(err.stack);
      }

      try {
        await client.query(sarahSetsQuery).then((resp) => {
          let result = resp.rows[0];
          setArray.push(result);
        });
      } catch (err) {
        console.error(err.stack);
      }

      try {
        await client.query(tristySetsQuery).then((resp) => {
          let result = resp.rows[0];
          setArray.push(result);
        });
      } catch (err) {
        console.error(err.stack);
      }

      try {
        await client.query(yunhanSetsQuery).then((resp) => {
          let result = resp.rows[0];
          setArray.push(result);
          dancerDataObject.setData = setArray;
          res.send(JSON.stringify(dancerDataObject));
        });
      } catch (err) {
        console.error(err.stack);
      }
    } else {
      // if no dates, dancers and chart type are given

      // queries for time spent and number of sets for each dancer
      jingxuanTimeQuery =
        "SELECT SUM(sumofminutes.jingxuantime) FROM (SELECT SUM(dancer1_minutes) AS jingxuantime FROM dailytracker WHERE dancer1='Jingxuan' AND " +
        datesQuery +
        " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Jingxuan' AND " +
        datesQuery +
        " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Jingxuan' AND " +
        datesQuery +
        ") AS sumofminutes";

      karanTimeQuery =
        "SELECT SUM(sumofminutes.karantime) FROM (SELECT SUM(dancer1_minutes) AS karantime FROM dailytracker WHERE dancer1='Karan' AND " +
        datesQuery +
        " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Karan' AND " +
        datesQuery +
        " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Karan' AND " +
        datesQuery +
        ") AS sumofminutes";

      kexinTimeQuery =
        "SELECT SUM(sumofminutes.kexintime) FROM (SELECT SUM(dancer1_minutes) AS kexintime FROM dailytracker WHERE dancer1='Kexin' AND " +
        datesQuery +
        " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Kexin' AND " +
        datesQuery +
        " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Kexin' AND " +
        datesQuery +
        ") AS sumofminutes";

      sarahTimeQuery =
        "SELECT SUM(sumofminutes.sarahtime) FROM (SELECT SUM(dancer1_minutes) AS sarahtime FROM dailytracker WHERE dancer1='Sarah' AND " +
        datesQuery +
        " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Sarah' AND " +
        datesQuery +
        " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Sarah' AND " +
        datesQuery +
        ") AS sumofminutes";

      tristyTimeQuery =
        "SELECT SUM(sumofminutes.tristytime) FROM (SELECT SUM(dancer1_minutes) AS tristytime FROM dailytracker WHERE dancer1='Tristy' AND " +
        datesQuery +
        " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Tristy' AND " +
        datesQuery +
        " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Tristy' AND " +
        datesQuery +
        ") AS sumofminutes";

      yunhanTimeQuery =
        "SELECT SUM(sumofminutes.yunhantime) FROM (SELECT SUM(dancer1_minutes) AS yunhantime FROM dailytracker WHERE dancer1='Yunhan' AND " +
        datesQuery +
        " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Yunhan' AND " +
        datesQuery +
        " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Yunhan' AND " +
        datesQuery +
        ") AS sumofminutes";

      jingxuanSetsQuery =
        "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Jingxuan%' AND " +
        datesQuery;

      karanSetsQuery =
        "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Karan%' AND " +
        datesQuery;

      kexinSetsQuery =
        "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Kexin%' AND " +
        datesQuery;

      sarahSetsQuery =
        "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Sarah%' AND " +
        datesQuery;

      tristySetsQuery =
        "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Tristy%' AND " +
        datesQuery;

      yunhanSetsQuery =
        "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Yunhan%' AND " +
        datesQuery;

      // get the data,
      // for time spent, push data into array for time
      // after getting all data, insert array into timeData of JSON Object
      // for number of sets, push data into array for sets
      // after getting all data, insert array into setData of JSON Object
      // send the Object to client
      try {
        await client.query(jingxuanTimeQuery).then((resp) => {
          let result = resp.rows[0];
          timeArray.push(result);
        });
      } catch (err) {
        console.error(err.stack);
      }

      try {
        await client.query(karanTimeQuery).then((resp) => {
          let result = resp.rows[0];
          timeArray.push(result);
        });
      } catch (err) {
        console.error(err.stack);
      }

      try {
        await client.query(kexinTimeQuery).then((resp) => {
          let result = resp.rows[0];
          timeArray.push(result);
        });
      } catch (err) {
        console.error(err.stack);
      }

      try {
        await client.query(sarahTimeQuery).then((resp) => {
          let result = resp.rows[0];
          timeArray.push(result);
        });
      } catch (err) {
        console.error(err.stack);
      }

      try {
        await client.query(tristyTimeQuery).then((resp) => {
          let result = resp.rows[0];
          timeArray.push(result);
        });
      } catch (err) {
        console.error(err.stack);
      }

      try {
        await client.query(yunhanTimeQuery).then((resp) => {
          let result = resp.rows[0];
          timeArray.push(result);
          dancerDataObject.timeData = timeArray;
        });
      } catch (err) {
        console.error(err.stack);
      }

      try {
        await client.query(jingxuanSetsQuery).then((resp) => {
          let result = resp.rows[0];
          setArray.push(result);
        });
      } catch (err) {
        console.error(err.stack);
      }

      try {
        await client.query(karanSetsQuery).then((resp) => {
          let result = resp.rows[0];
          setArray.push(result);
        });
      } catch (err) {
        console.error(err.stack);
      }

      try {
        await client.query(kexinSetsQuery).then((resp) => {
          let result = resp.rows[0];
          setArray.push(result);
        });
      } catch (err) {
        console.error(err.stack);
      }

      try {
        await client.query(sarahSetsQuery).then((resp) => {
          let result = resp.rows[0];
          setArray.push(result);
        });
      } catch (err) {
        console.error(err.stack);
      }

      try {
        await client.query(tristySetsQuery).then((resp) => {
          let result = resp.rows[0];
          setArray.push(result);
        });
      } catch (err) {
        console.error(err.stack);
      }

      try {
        await client.query(yunhanSetsQuery).then((resp) => {
          let result = resp.rows[0];
          setArray.push(result);
          dancerDataObject.setData = setArray;
          res.send(JSON.stringify(dancerDataObject));
        });
      } catch (err) {
        console.error(err.stack);
      }
    }
  } else {
    if (chartsRequired === "Time Bar") {
      if (dancerNames != null && datesRequired == null) {
        // if specific dancers are given and chart needed is bar chart for time spent
        // and no dates are given

        // queries for time spent for each dancer for the current week so far
        jingxuanTimeQuery =
          "SELECT SUM(sumofminutes.jingxuantime) FROM (SELECT SUM(dancer1_minutes) AS jingxuantime FROM dailytracker WHERE dancer1='Jingxuan' AND " +
          datesQuery +
          " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Jingxuan' AND " +
          datesQuery +
          " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Jingxuan' AND " +
          datesQuery +
          ") AS sumofminutes";

        karanTimeQuery =
          "SELECT SUM(sumofminutes.karantime) FROM (SELECT SUM(dancer1_minutes) AS karantime FROM dailytracker WHERE dancer1='Karan' AND " +
          datesQuery +
          " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Karan' AND " +
          datesQuery +
          " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Karan' AND " +
          datesQuery +
          ") AS sumofminutes";

        kexinTimeQuery =
          "SELECT SUM(sumofminutes.kexintime) FROM (SELECT SUM(dancer1_minutes) AS kexintime FROM dailytracker WHERE dancer1='Kexin' AND " +
          datesQuery +
          " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Kexin' AND " +
          datesQuery +
          " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Kexin' AND " +
          datesQuery +
          ") AS sumofminutes";

        sarahTimeQuery =
          "SELECT SUM(sumofminutes.sarahtime) FROM (SELECT SUM(dancer1_minutes) AS sarahtime FROM dailytracker WHERE dancer1='Sarah' AND " +
          datesQuery +
          " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Sarah' AND " +
          datesQuery +
          " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Sarah' AND " +
          datesQuery +
          ") AS sumofminutes";

        tristyTimeQuery =
          "SELECT SUM(sumofminutes.tristytime) FROM (SELECT SUM(dancer1_minutes) AS tristytime FROM dailytracker WHERE dancer1='Tristy' AND " +
          datesQuery +
          " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Tristy' AND " +
          datesQuery +
          " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Tristy' AND " +
          datesQuery +
          ") AS sumofminutes";

        yunhanTimeQuery =
          "SELECT SUM(sumofminutes.yunhantime) FROM (SELECT SUM(dancer1_minutes) AS yunhantime FROM dailytracker WHERE dancer1='Yunhan' AND " +
          datesQuery +
          " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Yunhan' AND " +
          datesQuery +
          " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Yunhan' AND " +
          datesQuery +
          ") AS sumofminutes";

        if (dancerNames.includes(",")) {
          // if more than 1 dancer is provided then loop through the names
          // run the corresponding query and push the result into the array for time spent
          // then insert the array to timeData of JSON Object and send Object to client
          try {
            dancerNames = dancerNames.split(",");
            for (var m = 0; m < dancerNames.length; m++) {
              if (dancerNames[m] == "Jingxuan") {
                try {
                  await client.query(jingxuanTimeQuery).then((resp) => {
                    let result = resp.rows[0];
                    timeArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }
              } else if (dancerNames[m] == "Karan") {
                try {
                  await client.query(karanTimeQuery).then((resp) => {
                    let result = resp.rows[0];
                    timeArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }
              } else if (dancerNames[m] == "Kexin") {
                try {
                  await client.query(kexinTimeQuery).then((resp) => {
                    let result = resp.rows[0];
                    timeArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }
              } else if (dancerNames[m] == "Sarah") {
                try {
                  await client.query(sarahTimeQuery).then((resp) => {
                    let result = resp.rows[0];
                    timeArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }
              } else if (dancerNames[m] == "Tristy") {
                try {
                  await client.query(tristyTimeQuery).then((resp) => {
                    let result = resp.rows[0];
                    timeArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }
              } else if (dancerNames[m] == "Yunhan") {
                try {
                  await client.query(yunhanTimeQuery).then((resp) => {
                    let result = resp.rows[0];
                    timeArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }
              }
            }
            dancerDataObject.timeData = timeArray;
            res.send(JSON.stringify(dancerDataObject));
          } catch (err) {
            console.error(err.stack);
          }
        } else {
          // if there is only 1 name, run the corresponding query
          // push result into array for time spent
          // insert the array into timeData of JSON Object and send the Object to client
          if (dancerNames == "Jingxuan") {
            try {
              await client.query(jingxuanTimeQuery).then((resp) => {
                let result = resp.rows[0];
                timeArray.push(result);
                dancerDataObject.timeData = timeArray;
                res.send(JSON.stringify(dancerDataObject));
              });
            } catch (err) {
              console.error(err.stack);
            }
          } else if (dancerNames == "Karan") {
            try {
              await client.query(karanTimeQuery).then((resp) => {
                let result = resp.rows[0];
                timeArray.push(result);
                dancerDataObject.timeData = timeArray;
                res.send(JSON.stringify(dancerDataObject));
              });
            } catch (err) {
              console.error(err.stack);
            }
          } else if (dancerNames == "Kexin") {
            try {
              await client.query(kexinTimeQuery).then((resp) => {
                let result = resp.rows[0];
                timeArray.push(result);
                dancerDataObject.timeData = timeArray;
                res.send(JSON.stringify(dancerDataObject));
              });
            } catch (err) {
              console.error(err.stack);
            }
          } else if (dancerNames == "Sarah") {
            try {
              await client.query(sarahTimeQuery).then((resp) => {
                let result = resp.rows[0];
                timeArray.push(result);
                dancerDataObject.timeData = timeArray;
                res.send(JSON.stringify(dancerDataObject));
              });
            } catch (err) {
              console.error(err.stack);
            }
          } else if (dancerNames == "Tristy") {
            try {
              await client.query(tristyTimeQuery).then((resp) => {
                let result = resp.rows[0];
                timeArray.push(result);
                dancerDataObject.timeData = timeArray;
                res.send(JSON.stringify(dancerDataObject));
              });
            } catch (err) {
              console.error(err.stack);
            }
          } else if (dancerNames == "Yunhan") {
            try {
              await client.query(yunhanTimeQuery).then((resp) => {
                let result = resp.rows[0];
                timeArray.push(result);
                dancerDataObject.timeData = timeArray;
                res.send(JSON.stringify(dancerDataObject));
              });
            } catch (err) {
              console.error(err.stack);
            }
          }
        }
      }
      if (datesRequired != null && dancerNames == null) {
        // if no dancers are given but range of dates are given
        // and chart needed is bar chart for time spent
        datesRequired = "(date BETWEEN '" + datesRequired;
        datesRequired = datesRequired.replace(/,/g, "' AND '");
        datesRequired += "')";
        console.log(datesRequired);

        // queries for each dancer for time spent for the range of dates provided
        jingxuanTimeQuery =
          "SELECT SUM(sumofminutes.jingxuantime) FROM (SELECT SUM(dancer1_minutes) AS jingxuantime FROM dailytracker WHERE dancer1='Jingxuan' AND " +
          datesRequired +
          " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Jingxuan' AND " +
          datesRequired +
          " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Jingxuan' AND " +
          datesRequired +
          ") AS sumofminutes";

        karanTimeQuery =
          "SELECT SUM(sumofminutes.karantime) FROM (SELECT SUM(dancer1_minutes) AS karantime FROM dailytracker WHERE dancer1='Karan' AND " +
          datesRequired +
          " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Karan' AND " +
          datesRequired +
          " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Karan' AND " +
          datesRequired +
          ") AS sumofminutes";

        kexinTimeQuery =
          "SELECT SUM(sumofminutes.kexintime) FROM (SELECT SUM(dancer1_minutes) AS kexintime FROM dailytracker WHERE dancer1='Kexin' AND " +
          datesRequired +
          " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Kexin' AND " +
          datesRequired +
          " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Kexin' AND " +
          datesRequired +
          ") AS sumofminutes";

        sarahTimeQuery =
          "SELECT SUM(sumofminutes.sarahtime) FROM (SELECT SUM(dancer1_minutes) AS sarahtime FROM dailytracker WHERE dancer1='Sarah' AND " +
          datesRequired +
          " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Sarah' AND " +
          datesRequired +
          " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Sarah' AND " +
          datesRequired +
          ") AS sumofminutes";

        tristyTimeQuery =
          "SELECT SUM(sumofminutes.tristytime) FROM (SELECT SUM(dancer1_minutes) AS tristytime FROM dailytracker WHERE dancer1='Tristy' AND " +
          datesRequired +
          " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Tristy' AND " +
          datesRequired +
          " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Tristy' AND " +
          datesRequired +
          ") AS sumofminutes";

        yunhanTimeQuery =
          "SELECT SUM(sumofminutes.yunhantime) FROM (SELECT SUM(dancer1_minutes) AS yunhantime FROM dailytracker WHERE dancer1='Yunhan' AND " +
          datesRequired +
          " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Yunhan' AND " +
          datesRequired +
          " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Yunhan' AND " +
          datesRequired +
          ") AS sumofminutes";

        try {
          await client.query(jingxuanTimeQuery).then((resp) => {
            let result = resp.rows[0];
            timeArray.push(result);
          });
        } catch (err) {
          console.error(err.stack);
        }

        try {
          await client.query(karanTimeQuery).then((resp) => {
            let result = resp.rows[0];
            timeArray.push(result);
          });
        } catch (err) {
          console.error(err.stack);
        }

        try {
          await client.query(kexinTimeQuery).then((resp) => {
            let result = resp.rows[0];
            timeArray.push(result);
          });
        } catch (err) {
          console.error(err.stack);
        }

        try {
          await client.query(sarahTimeQuery).then((resp) => {
            let result = resp.rows[0];
            timeArray.push(result);
          });
        } catch (err) {
          console.error(err.stack);
        }

        try {
          await client.query(tristyTimeQuery).then((resp) => {
            let result = resp.rows[0];
            timeArray.push(result);
          });
        } catch (err) {
          console.error(err.stack);
        }

        try {
          await client.query(yunhanTimeQuery).then((resp) => {
            let result = resp.rows[0];
            timeArray.push(result);
            dancerDataObject.timeData = timeArray;
            console.dir(dancerDataObject);
            res.send(JSON.stringify(dancerDataObject));
          });
        } catch (err) {
          console.error(err.stack);
        }
      } else if (dancerNames != null && datesRequired != null) {
        // if specific dancers, range of dates are given and chart needed is bar chart for time spent
        datesRequired = "(date BETWEEN '" + datesRequired;
        datesRequired = datesRequired.replace(/,/g, "' AND '");
        datesRequired += "')";

        jingxuanTimeQuery =
          "SELECT SUM(sumofminutes.jingxuantime) FROM (SELECT SUM(dancer1_minutes) AS jingxuantime FROM dailytracker WHERE dancer1='Jingxuan' AND " +
          datesRequired +
          " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Jingxuan' AND " +
          datesRequired +
          " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Jingxuan' AND " +
          datesRequired +
          ") AS sumofminutes";

        karanTimeQuery =
          "SELECT SUM(sumofminutes.karantime) FROM (SELECT SUM(dancer1_minutes) AS karantime FROM dailytracker WHERE dancer1='Karan' AND " +
          datesRequired +
          " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Karan' AND " +
          datesRequired +
          " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Karan' AND " +
          datesRequired +
          ") AS sumofminutes";

        kexinTimeQuery =
          "SELECT SUM(sumofminutes.kexintime) FROM (SELECT SUM(dancer1_minutes) AS kexintime FROM dailytracker WHERE dancer1='Kexin' AND " +
          datesRequired +
          " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Kexin' AND " +
          datesRequired +
          " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Kexin' AND " +
          datesRequired +
          ") AS sumofminutes";

        sarahTimeQuery =
          "SELECT SUM(sumofminutes.sarahtime) FROM (SELECT SUM(dancer1_minutes) AS sarahtime FROM dailytracker WHERE dancer1='Sarah' AND " +
          datesRequired +
          " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Sarah' AND " +
          datesRequired +
          " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Sarah' AND " +
          datesRequired +
          ") AS sumofminutes";

        tristyTimeQuery =
          "SELECT SUM(sumofminutes.tristytime) FROM (SELECT SUM(dancer1_minutes) AS tristytime FROM dailytracker WHERE dancer1='Tristy' AND " +
          datesRequired +
          " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Tristy' AND " +
          datesRequired +
          " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Tristy' AND " +
          datesRequired +
          ") AS sumofminutes";

        yunhanTimeQuery =
          "SELECT SUM(sumofminutes.yunhantime) FROM (SELECT SUM(dancer1_minutes) AS yunhantime FROM dailytracker WHERE dancer1='Yunhan' AND " +
          datesRequired +
          " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Yunhan' AND " +
          datesRequired +
          " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Yunhan' AND " +
          datesRequired +
          ") AS sumofminutes";

        if (dancerNames.includes(",")) {
          try {
            // if have multiple names, loop through and run the corresponding query
            // after getting the necessary data, send the Object to client
            dancerNames = dancerNames.split(",");
            for (var m = 0; m < dancerNames.length; m++) {
              if (dancerNames[m] == "Jingxuan") {
                try {
                  await client.query(jingxuanTimeQuery).then((resp) => {
                    let result = resp.rows[0];
                    timeArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }
              } else if (dancerNames[m] == "Karan") {
                try {
                  await client.query(karanTimeQuery).then((resp) => {
                    let result = resp.rows[0];
                    timeArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }
              } else if (dancerNames[m] == "Kexin") {
                try {
                  await client.query(kexinTimeQuery).then((resp) => {
                    let result = resp.rows[0];
                    timeArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }
              } else if (dancerNames[m] == "Sarah") {
                try {
                  await client.query(sarahTimeQuery).then((resp) => {
                    let result = resp.rows[0];
                    timeArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }
              } else if (dancerNames[m] == "Tristy") {
                try {
                  await client.query(tristyTimeQuery).then((resp) => {
                    let result = resp.rows[0];
                    timeArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }
              } else if (dancerNames[m] == "Yunhan") {
                try {
                  await client.query(yunhanTimeQuery).then((resp) => {
                    let result = resp.rows[0];
                    timeArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }
              }
            }
            dancerDataObject.timeData = timeArray;
            console.dir(dancerDataObject);
            res.send(JSON.stringify(dancerDataObject));
          } catch (err) {
            console.error(err.stack);
          }
        } else {
          // only 1 name specified, get the data after running the qeury and send the Object
          // to client
          if (dancerNames == "Jingxuan") {
            try {
              await client.query(jingxuanTimeQuery).then((resp) => {
                let result = resp.rows[0];
                timeArray.push(result);
                dancerDataObject.timeData = timeArray;
                res.send(JSON.stringify(dancerDataObject));
              });
            } catch (err) {
              console.error(err.stack);
            }
          } else if (dancerNames == "Karan") {
            try {
              await client.query(karanTimeQuery).then((resp) => {
                let result = resp.rows[0];
                timeArray.push(result);
                dancerDataObject.timeData = timeArray;
                res.send(JSON.stringify(dancerDataObject));
              });
            } catch (err) {
              console.error(err.stack);
            }
          } else if (dancerNames == "Kexin") {
            try {
              await client.query(kexinTimeQuery).then((resp) => {
                let result = resp.rows[0];
                timeArray.push(result);
                dancerDataObject.timeData = timeArray;
                res.send(JSON.stringify(dancerDataObject));
              });
            } catch (err) {
              console.error(err.stack);
            }
          } else if (dancerNames == "Sarah") {
            try {
              await client.query(sarahTimeQuery).then((resp) => {
                let result = resp.rows[0];
                timeArray.push(result);
                dancerDataObject.timeData = timeArray;
                res.send(JSON.stringify(dancerDataObject));
              });
            } catch (err) {
              console.error(err.stack);
            }
          } else if (dancerNames == "Tristy") {
            try {
              await client.query(tristyTimeQuery).then((resp) => {
                let result = resp.rows[0];
                timeArray.push(result);
                dancerDataObject.timeData = timeArray;
                console.dir(dancerDataObject);
                res.send(JSON.stringify(dancerDataObject));
              });
            } catch (err) {
              console.error(err.stack);
            }
          } else if (dancerNames == "Yunhan") {
            try {
              await client.query(yunhanTimeQuery).then((resp) => {
                let result = resp.rows[0];
                timeArray.push(result);
                dancerDataObject.timeData = timeArray;
                res.send(JSON.stringify(dancerDataObject));
              });
            } catch (err) {
              console.error(err.stack);
            }
          }
        }
      }
    } else if (chartsRequired === "Set Bar") {
      if (dancerNames != null && datesRequired == null) {
        // if specific dancers are given and chart needed is bar chart for number of sets done
        // and no dates are given

        jingxuanSetsQuery =
          "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Jingxuan%' AND " +
          datesQuery;

        karanSetsQuery =
          "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Karan%' AND " +
          datesQuery;

        kexinSetsQuery =
          "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Kexin%' AND " +
          datesQuery;

        sarahSetsQuery =
          "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Sarah%' AND " +
          datesQuery;

        tristySetsQuery =
          "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Tristy%' AND " +
          datesQuery;

        yunhanSetsQuery =
          "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Yunhan%' AND " +
          datesQuery;

        if (dancerNames.includes(",")) {
          try {
            // if have multiple names, loop through and run the corresponding query
            // after getting the necessary data, send the Object to client
            dancerNames = dancerNames.split(",");
            for (var m = 0; m < dancerNames.length; m++) {
              if (dancerNames[m] == "Jingxuan") {
                try {
                  await client.query(jingxuanSetsQuery).then((resp) => {
                    let result = resp.rows[0];
                    setArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }
              } else if (dancerNames[m] == "Karan") {
                try {
                  await client.query(karanSetsQuery).then((resp) => {
                    let result = resp.rows[0];
                    setArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }
              } else if (dancerNames[m] == "Kexin") {
                try {
                  await client.query(kexinSetsQuery).then((resp) => {
                    let result = resp.rows[0];
                    setArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }
              } else if (dancerNames[m] == "Sarah") {
                try {
                  await client.query(sarahSetsQuery).then((resp) => {
                    let result = resp.rows[0];
                    setArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }
              } else if (dancerNames[m] == "Tristy") {
                try {
                  await client.query(tristySetsQuery).then((resp) => {
                    let result = resp.rows[0];
                    setArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }
              } else if (dancerNames[m] == "Yunhan") {
                try {
                  await client.query(yunhanSetsQuery).then((resp) => {
                    let result = resp.rows[0];
                    setArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }
              }
            }
            console.dir(setArray);
            dancerDataObject.setData = setArray;
            res.send(JSON.stringify(dancerDataObject));
          } catch (err) {
            console.error(err.stack);
          }
        } else {
          // only 1 name specified, get the data after running the qeury and send the Object
          // to client
          if (dancerNames == "Jingxuan") {
            try {
              await client.query(jingxuanSetsQuery).then((resp) => {
                let result = resp.rows[0];
                setArray.push(result);
                dancerDataObject.setData = setArray;
                res.send(JSON.stringify(dancerDataObject));
              });
            } catch (err) {
              console.error(err.stack);
            }
          } else if (dancerNames == "Karan") {
            try {
              await client.query(karanSetsQuery).then((resp) => {
                let result = resp.rows[0];
                setArray.push(result);
                dancerDataObject.setData = setArray;
                res.send(JSON.stringify(dancerDataObject));
              });
            } catch (err) {
              console.error(err.stack);
            }
          } else if (dancerNames == "Kexin") {
            try {
              await client.query(kexinSetsQuery).then((resp) => {
                let result = resp.rows[0];
                setArray.push(result);
                dancerDataObject.setData = setArray;
                res.send(JSON.stringify(dancerDataObject));
              });
            } catch (err) {
              console.error(err.stack);
            }
          } else if (dancerNames == "Sarah") {
            try {
              await client.query(sarahSetsQuery).then((resp) => {
                let result = resp.rows[0];
                setArray.push(result);
                dancerDataObject.setData = setArray;
                res.send(JSON.stringify(dancerDataObject));
              });
            } catch (err) {
              console.error(err.stack);
            }
          } else if (dancerNames == "Tristy") {
            try {
              await client.query(tristySetsQuery).then((resp) => {
                let result = resp.rows[0];
                setArray.push(result);
                dancerDataObject.setData = setArray;
                res.send(JSON.stringify(dancerDataObject));
              });
            } catch (err) {
              console.error(err.stack);
            }
          } else if (dancerNames == "Yunhan") {
            try {
              await client.query(yunhanSetsQuery).then((resp) => {
                let result = resp.rows[0];
                setArray.push(result);
                dancerDataObject.setData = setArray;
                res.send(JSON.stringify(dancerDataObject));
              });
            } catch (err) {
              console.error(err.stack);
            }
          }
        }
      } else if (dancerNames == null && datesRequired != null) {
        // if specific dancers are not given and chart needed is bar chart for number of sets done
        // and range of dates are given
        datesRequired = "(date BETWEEN '" + datesRequired;
        datesRequired = datesRequired.replace(/,/g, "' AND '");
        datesRequired += "')";

        jingxuanSetsQuery =
          "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Jingxuan%' AND " +
          datesRequired;

        karanSetsQuery =
          "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Karan%' AND " +
          datesRequired;

        kexinSetsQuery =
          "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Kexin%' AND " +
          datesRequired;

        sarahSetsQuery =
          "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Sarah%' AND " +
          datesRequired;

        tristySetsQuery =
          "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Tristy%' AND " +
          datesRequired;

        yunhanSetsQuery =
          "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Yunhan%' AND " +
          datesRequired;

        // get data for all dancers and send the Object to client
        try {
          await client.query(jingxuanSetsQuery).then((resp) => {
            let result = resp.rows[0];
            setArray.push(result);
          });
        } catch (err) {
          console.error(err.stack);
        }

        try {
          await client.query(karanSetsQuery).then((resp) => {
            let result = resp.rows[0];
            setArray.push(result);
          });
        } catch (err) {
          console.error(err.stack);
        }

        try {
          await client.query(kexinSetsQuery).then((resp) => {
            let result = resp.rows[0];
            setArray.push(result);
          });
        } catch (err) {
          console.error(err.stack);
        }

        try {
          await client.query(sarahSetsQuery).then((resp) => {
            let result = resp.rows[0];
            setArray.push(result);
          });
        } catch (err) {
          console.error(err.stack);
        }

        try {
          await client.query(tristySetsQuery).then((resp) => {
            let result = resp.rows[0];
            setArray.push(result);
          });
        } catch (err) {
          console.error(err.stack);
        }

        try {
          await client.query(yunhanSetsQuery).then((resp) => {
            let result = resp.rows[0];
            setArray.push(result);
            dancerDataObject.setData = setArray;
            res.send(JSON.stringify(dancerDataObject));
          });
        } catch (err) {
          console.error(err.stack);
        }
      } else {
        // if specific dancers and range of dates are given
        // and chart needed is bar chart for number of sets done
        datesRequired = "(date BETWEEN '" + datesRequired;
        datesRequired = datesRequired.replace(/,/g, "' AND '");
        datesRequired += "')";

        jingxuanSetsQuery =
          "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Jingxuan%' AND " +
          datesRequired;

        karanSetsQuery =
          "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Karan%' AND " +
          datesRequired;

        kexinSetsQuery =
          "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Kexin%' AND " +
          datesRequired;

        sarahSetsQuery =
          "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Sarah%' AND " +
          datesRequired;

        tristySetsQuery =
          "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Tristy%' AND " +
          datesRequired;

        yunhanSetsQuery =
          "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Yunhan%' AND " +
          datesRequired;

        if (dancerNames.includes(",")) {
          try {
            // if there are multiple dancers, loop through the names and run the corresponding query
            // get all the data and send the Object to client
            dancerNames = dancerNames.split(",");
            for (var m = 0; m < dancerNames.length; m++) {
              if (dancerNames[m] == "Jingxuan") {
                try {
                  await client.query(jingxuanSetsQuery).then((resp) => {
                    let result = resp.rows[0];
                    setArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }
              } else if (dancerNames[m] == "Karan") {
                try {
                  await client.query(karanSetsQuery).then((resp) => {
                    let result = resp.rows[0];
                    setArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }
              } else if (dancerNames[m] == "Kexin") {
                try {
                  await client.query(kexinSetsQuery).then((resp) => {
                    let result = resp.rows[0];
                    setArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }
              } else if (dancerNames[m] == "Sarah") {
                try {
                  await client.query(sarahSetsQuery).then((resp) => {
                    let result = resp.rows[0];
                    setArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }
              } else if (dancerNames[m] == "Tristy") {
                try {
                  await client.query(tristySetsQuery).then((resp) => {
                    let result = resp.rows[0];
                    setArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }
              } else if (dancerNames[m] == "Yunhan") {
                try {
                  await client.query(yunhanSetsQuery).then((resp) => {
                    let result = resp.rows[0];
                    setArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }
              }
            }
            console.dir(setArray);
            dancerDataObject.setData = setArray;
            res.send(JSON.stringify(dancerDataObject));
          } catch (err) {
            console.error(err.stack);
          }
        } else {
          // if 1 name is given, run the corresponding query
          // and send the Object containing the data to client
          if (dancerNames == "Jingxuan") {
            try {
              await client.query(jingxuanSetsQuery).then((resp) => {
                let result = resp.rows[0];
                setArray.push(result);
                dancerDataObject.setData = setArray;
                res.send(JSON.stringify(dancerDataObject));
              });
            } catch (err) {
              console.error(err.stack);
            }
          } else if (dancerNames == "Karan") {
            try {
              await client.query(karanSetsQuery).then((resp) => {
                let result = resp.rows[0];
                setArray.push(result);
                dancerDataObject.setData = setArray;
                res.send(JSON.stringify(dancerDataObject));
              });
            } catch (err) {
              console.error(err.stack);
            }
          } else if (dancerNames == "Kexin") {
            try {
              await client.query(kexinSetsQuery).then((resp) => {
                let result = resp.rows[0];
                setArray.push(result);
                dancerDataObject.setData = setArray;
                res.send(JSON.stringify(dancerDataObject));
              });
            } catch (err) {
              console.error(err.stack);
            }
          } else if (dancerNames == "Sarah") {
            try {
              await client.query(sarahSetsQuery).then((resp) => {
                let result = resp.rows[0];
                setArray.push(result);
                dancerDataObject.setData = setArray;
                res.send(JSON.stringify(dancerDataObject));
              });
            } catch (err) {
              console.error(err.stack);
            }
          } else if (dancerNames == "Tristy") {
            try {
              await client.query(tristySetsQuery).then((resp) => {
                let result = resp.rows[0];
                setArray.push(result);
                dancerDataObject.setData = setArray;
                res.send(JSON.stringify(dancerDataObject));
              });
            } catch (err) {
              console.error(err.stack);
            }
          } else if (dancerNames == "Yunhan") {
            try {
              await client.query(yunhanSetsQuery).then((resp) => {
                let result = resp.rows[0];
                setArray.push(result);
                dancerDataObject.setData = setArray;
                res.send(JSON.stringify(dancerDataObject));
              });
            } catch (err) {
              console.error(err.stack);
            }
          }
        }
      }
    } else {
      if (dancerNames != null && datesRequired == null) {
        // if specific dancers are given, but dates needed and chart types are not given
        jingxuanSetsQuery =
          "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Jingxuan%' AND " +
          datesQuery;

        karanSetsQuery =
          "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Karan%' AND " +
          datesQuery;

        kexinSetsQuery =
          "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Kexin%' AND " +
          datesQuery;

        sarahSetsQuery =
          "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Sarah%' AND " +
          datesQuery;

        tristySetsQuery =
          "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Tristy%' AND " +
          datesQuery;

        yunhanSetsQuery =
          "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Yunhan%' AND " +
          datesQuery;

        jingxuanTimeQuery =
          "SELECT SUM(sumofminutes.jingxuantime) FROM (SELECT SUM(dancer1_minutes) AS jingxuantime FROM dailytracker WHERE dancer1='Jingxuan' AND " +
          datesQuery +
          " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Jingxuan' AND " +
          datesQuery +
          " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Jingxuan' AND " +
          datesQuery +
          ") AS sumofminutes";

        karanTimeQuery =
          "SELECT SUM(sumofminutes.karantime) FROM (SELECT SUM(dancer1_minutes) AS karantime FROM dailytracker WHERE dancer1='Karan' AND " +
          datesQuery +
          " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Karan' AND " +
          datesQuery +
          " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Karan' AND " +
          datesQuery +
          ") AS sumofminutes";

        kexinTimeQuery =
          "SELECT SUM(sumofminutes.kexintime) FROM (SELECT SUM(dancer1_minutes) AS kexintime FROM dailytracker WHERE dancer1='Kexin' AND " +
          datesQuery +
          " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Kexin' AND " +
          datesQuery +
          " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Kexin' AND " +
          datesQuery +
          ") AS sumofminutes";

        sarahTimeQuery =
          "SELECT SUM(sumofminutes.sarahtime) FROM (SELECT SUM(dancer1_minutes) AS sarahtime FROM dailytracker WHERE dancer1='Sarah' AND " +
          datesQuery +
          " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Sarah' AND " +
          datesQuery +
          " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Sarah' AND " +
          datesQuery +
          ") AS sumofminutes";

        tristyTimeQuery =
          "SELECT SUM(sumofminutes.tristytime) FROM (SELECT SUM(dancer1_minutes) AS tristytime FROM dailytracker WHERE dancer1='Tristy' AND " +
          datesQuery +
          " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Tristy' AND " +
          datesQuery +
          " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Tristy' AND " +
          datesQuery +
          ") AS sumofminutes";

        yunhanTimeQuery =
          "SELECT SUM(sumofminutes.yunhantime) FROM (SELECT SUM(dancer1_minutes) AS yunhantime FROM dailytracker WHERE dancer1='Yunhan' AND " +
          datesQuery +
          " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Yunhan' AND " +
          datesQuery +
          " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Yunhan' AND " +
          datesQuery +
          ") AS sumofminutes";

        // if there is more than 1 name, loop through the names, run both queries
        // (time spent and set done) with the dates of the current week
        // after getting all the data, send the Object to the client
        // if there is only 1 name, then run both queries for that name and send the Object to client
        if (dancerNames.includes(",")) {
          try {
            dancerNames = dancerNames.split(",");
            for (var m = 0; m < dancerNames.length; m++) {
              if (dancerNames[m] == "Jingxuan") {
                try {
                  await client.query(jingxuanSetsQuery).then((resp) => {
                    let result = resp.rows[0];
                    setArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }

                try {
                  await client.query(jingxuanTimeQuery).then((resp) => {
                    let result = resp.rows[0];
                    timeArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }
              } else if (dancerNames[m] == "Karan") {
                try {
                  await client.query(karanSetsQuery).then((resp) => {
                    let result = resp.rows[0];
                    setArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }

                try {
                  await client.query(karanTimeQuery).then((resp) => {
                    let result = resp.rows[0];
                    timeArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }
              } else if (dancerNames[m] == "Kexin") {
                try {
                  await client.query(kexinSetsQuery).then((resp) => {
                    let result = resp.rows[0];
                    setArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }

                try {
                  await client.query(kexinTimeQuery).then((resp) => {
                    let result = resp.rows[0];
                    timeArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }
              } else if (dancerNames[m] == "Sarah") {
                try {
                  await client.query(sarahSetsQuery).then((resp) => {
                    let result = resp.rows[0];
                    setArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }

                try {
                  await client.query(sarahTimeQuery).then((resp) => {
                    let result = resp.rows[0];
                    timeArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }
              } else if (dancerNames[m] == "Tristy") {
                try {
                  await client.query(tristySetsQuery).then((resp) => {
                    let result = resp.rows[0];
                    setArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }

                try {
                  await client.query(tristyTimeQuery).then((resp) => {
                    let result = resp.rows[0];
                    timeArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }
              } else if (dancerNames[m] == "Yunhan") {
                try {
                  await client.query(yunhanSetsQuery).then((resp) => {
                    let result = resp.rows[0];
                    setArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }

                try {
                  await client.query(yunhanTimeQuery).then((resp) => {
                    let result = resp.rows[0];
                    timeArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }
              }
            }
            // console.dir(setArray);
            dancerDataObject.setData = setArray;
            dancerDataObject.timeData = timeArray;
            res.send(JSON.stringify(dancerDataObject));
          } catch (err) {
            console.error(err.stack);
          }
        } else {
          if (dancerNames == "Jingxuan") {
            try {
              await client.query(jingxuanSetsQuery).then((resp) => {
                let result = resp.rows[0];
                setArray.push(result);
                dancerDataObject.setData = setArray;
              });
            } catch (err) {
              console.error(err.stack);
            }

            try {
              await client.query(jingxuanTimeQuery).then((resp) => {
                let result = resp.rows[0];
                timeArray.push(result);
                dancerDataObject.timeData = timeArray;
                res.send(JSON.stringify(dancerDataObject));
              });
            } catch (err) {
              console.error(err.stack);
            }
          } else if (dancerNames == "Karan") {
            try {
              await client.query(karanSetsQuery).then((resp) => {
                let result = resp.rows[0];
                setArray.push(result);
                dancerDataObject.setData = setArray;
              });
            } catch (err) {
              console.error(err.stack);
            }

            try {
              await client.query(karanTimeQuery).then((resp) => {
                let result = resp.rows[0];
                timeArray.push(result);
                dancerDataObject.timeData = timeArray;
                res.send(JSON.stringify(dancerDataObject));
              });
            } catch (err) {
              console.error(err.stack);
            }
          } else if (dancerNames == "Kexin") {
            try {
              await client.query(kexinSetsQuery).then((resp) => {
                let result = resp.rows[0];
                setArray.push(result);
                dancerDataObject.setData = setArray;
              });
            } catch (err) {
              console.error(err.stack);
            }

            try {
              await client.query(kexinTimeQuery).then((resp) => {
                let result = resp.rows[0];
                timeArray.push(result);
                dancerDataObject.timeData = timeArray;
                res.send(JSON.stringify(dancerDataObject));
              });
            } catch (err) {
              console.error(err.stack);
            }
          } else if (dancerNames == "Sarah") {
            try {
              await client.query(sarahSetsQuery).then((resp) => {
                let result = resp.rows[0];
                setArray.push(result);
                dancerDataObject.setData = setArray;
              });
            } catch (err) {
              console.error(err.stack);
            }

            try {
              await client.query(sarahTimeQuery).then((resp) => {
                let result = resp.rows[0];
                timeArray.push(result);
                dancerDataObject.timeData = timeArray;
                res.send(JSON.stringify(dancerDataObject));
              });
            } catch (err) {
              console.error(err.stack);
            }
          } else if (dancerNames == "Tristy") {
            try {
              await client.query(tristySetsQuery).then((resp) => {
                let result = resp.rows[0];
                setArray.push(result);
                dancerDataObject.setData = setArray;
              });
            } catch (err) {
              console.error(err.stack);
            }

            try {
              await client.query(tristyTimeQuery).then((resp) => {
                let result = resp.rows[0];
                timeArray.push(result);
                dancerDataObject.timeData = timeArray;
                res.send(JSON.stringify(dancerDataObject));
              });
            } catch (err) {
              console.error(err.stack);
            }
          } else if (dancerNames == "Yunhan") {
            try {
              await client.query(yunhanSetsQuery).then((resp) => {
                let result = resp.rows[0];
                setArray.push(result);
                dancerDataObject.setData = setArray;
              });
            } catch (err) {
              console.error(err.stack);
            }

            try {
              await client.query(yunhanTimeQuery).then((resp) => {
                let result = resp.rows[0];
                timeArray.push(result);
                dancerDataObject.timeData = timeArray;
                res.send(JSON.stringify(dancerDataObject));
              });
            } catch (err) {
              console.error(err.stack);
            }
          }
        }
      } else if (dancerNames == null && datesRequired != null) {
        // if specific dancers and chart types are not given, but range of dates given
        datesRequired = "(date BETWEEN '" + datesRequired;
        datesRequired = datesRequired.replace(/,/g, "' AND '");
        datesRequired += "')";

        jingxuanSetsQuery =
          "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Jingxuan%' AND " +
          datesRequired;

        karanSetsQuery =
          "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Karan%' AND " +
          datesRequired;

        kexinSetsQuery =
          "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Kexin%' AND " +
          datesRequired;

        sarahSetsQuery =
          "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Sarah%' AND " +
          datesRequired;

        tristySetsQuery =
          "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Tristy%' AND " +
          datesRequired;

        yunhanSetsQuery =
          "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Yunhan%' AND " +
          datesRequired;

        jingxuanTimeQuery =
          "SELECT SUM(sumofminutes.jingxuantime) FROM (SELECT SUM(dancer1_minutes) AS jingxuantime FROM dailytracker WHERE dancer1='Jingxuan' AND " +
          datesRequired +
          " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Jingxuan' AND " +
          datesRequired +
          " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Jingxuan' AND " +
          datesRequired +
          ") AS sumofminutes";

        karanTimeQuery =
          "SELECT SUM(sumofminutes.karantime) FROM (SELECT SUM(dancer1_minutes) AS karantime FROM dailytracker WHERE dancer1='Karan' AND " +
          datesRequired +
          " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Karan' AND " +
          datesRequired +
          " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Karan' AND " +
          datesRequired +
          ") AS sumofminutes";

        kexinTimeQuery =
          "SELECT SUM(sumofminutes.kexintime) FROM (SELECT SUM(dancer1_minutes) AS kexintime FROM dailytracker WHERE dancer1='Kexin' AND " +
          datesRequired +
          " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Kexin' AND " +
          datesRequired +
          " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Kexin' AND " +
          datesRequired +
          ") AS sumofminutes";

        sarahTimeQuery =
          "SELECT SUM(sumofminutes.sarahtime) FROM (SELECT SUM(dancer1_minutes) AS sarahtime FROM dailytracker WHERE dancer1='Sarah' AND " +
          datesRequired +
          " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Sarah' AND " +
          datesRequired +
          " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Sarah' AND " +
          datesRequired +
          ") AS sumofminutes";

        tristyTimeQuery =
          "SELECT SUM(sumofminutes.tristytime) FROM (SELECT SUM(dancer1_minutes) AS tristytime FROM dailytracker WHERE dancer1='Tristy' AND " +
          datesRequired +
          " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Tristy' AND " +
          datesRequired +
          " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Tristy' AND " +
          datesRequired +
          ") AS sumofminutes";

        yunhanTimeQuery =
          "SELECT SUM(sumofminutes.yunhantime) FROM (SELECT SUM(dancer1_minutes) AS yunhantime FROM dailytracker WHERE dancer1='Yunhan' AND " +
          datesRequired +
          " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Yunhan' AND " +
          datesRequired +
          " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Yunhan' AND " +
          datesRequired +
          ") AS sumofminutes";

        // run both queries (time spent and number of sets done) for each dancer for the range of dates
        // given and after getting all the data, send the Object to client
        try {
          await client.query(jingxuanTimeQuery).then((resp) => {
            let result = resp.rows[0];
            timeArray.push(result);
          });
        } catch (err) {
          console.error(err.stack);
        }

        try {
          await client.query(karanTimeQuery).then((resp) => {
            let result = resp.rows[0];
            timeArray.push(result);
          });
        } catch (err) {
          console.error(err.stack);
        }

        try {
          await client.query(kexinTimeQuery).then((resp) => {
            let result = resp.rows[0];
            timeArray.push(result);
          });
        } catch (err) {
          console.error(err.stack);
        }

        try {
          await client.query(sarahTimeQuery).then((resp) => {
            let result = resp.rows[0];
            timeArray.push(result);
          });
        } catch (err) {
          console.error(err.stack);
        }

        try {
          await client.query(tristyTimeQuery).then((resp) => {
            let result = resp.rows[0];
            timeArray.push(result);
          });
        } catch (err) {
          console.error(err.stack);
        }

        try {
          await client.query(yunhanTimeQuery).then((resp) => {
            let result = resp.rows[0];
            timeArray.push(result);
            dancerDataObject.timeData = timeArray;
          });
        } catch (err) {
          console.error(err.stack);
        }

        try {
          await client.query(jingxuanSetsQuery).then((resp) => {
            let result = resp.rows[0];
            setArray.push(result);
          });
        } catch (err) {
          console.error(err.stack);
        }

        try {
          await client.query(karanSetsQuery).then((resp) => {
            let result = resp.rows[0];
            setArray.push(result);
          });
        } catch (err) {
          console.error(err.stack);
        }

        try {
          await client.query(kexinSetsQuery).then((resp) => {
            let result = resp.rows[0];
            setArray.push(result);
          });
        } catch (err) {
          console.error(err.stack);
        }

        try {
          await client.query(sarahSetsQuery).then((resp) => {
            let result = resp.rows[0];
            setArray.push(result);
          });
        } catch (err) {
          console.error(err.stack);
        }

        try {
          await client.query(tristySetsQuery).then((resp) => {
            let result = resp.rows[0];
            setArray.push(result);
          });
        } catch (err) {
          console.error(err.stack);
        }

        try {
          await client.query(yunhanSetsQuery).then((resp) => {
            let result = resp.rows[0];
            setArray.push(result);
            dancerDataObject.setData = setArray;
            res.send(JSON.stringify(dancerDataObject));
          });
        } catch (err) {
          console.error(err.stack);
        }
      } else {
        // if specific dancers and range of dates are given, but chart type is not given
        datesQuery = "(date BETWEEN '" + datesRequired;
        datesQuery = datesQuery.replace(/,/g, "' AND '");
        datesQuery += "')";

        jingxuanSetsQuery =
          "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Jingxuan%' AND " +
          datesQuery;

        karanSetsQuery =
          "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Karan%' AND " +
          datesQuery;

        kexinSetsQuery =
          "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Kexin%' AND " +
          datesQuery;

        sarahSetsQuery =
          "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Sarah%' AND " +
          datesQuery;

        tristySetsQuery =
          "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Tristy%' AND " +
          datesQuery;

        yunhanSetsQuery =
          "SELECT COUNT(*) FROM dailysets WHERE dancers LIKE '%Yunhan%' AND " +
          datesQuery;

        jingxuanTimeQuery =
          "SELECT SUM(sumofminutes.jingxuantime) FROM (SELECT SUM(dancer1_minutes) AS jingxuantime FROM dailytracker WHERE dancer1='Jingxuan' AND " +
          datesQuery +
          " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Jingxuan' AND " +
          datesQuery +
          " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Jingxuan' AND " +
          datesQuery +
          ") AS sumofminutes";

        karanTimeQuery =
          "SELECT SUM(sumofminutes.karantime) FROM (SELECT SUM(dancer1_minutes) AS karantime FROM dailytracker WHERE dancer1='Karan' AND " +
          datesQuery +
          " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Karan' AND " +
          datesQuery +
          " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Karan' AND " +
          datesQuery +
          ") AS sumofminutes";

        kexinTimeQuery =
          "SELECT SUM(sumofminutes.kexintime) FROM (SELECT SUM(dancer1_minutes) AS kexintime FROM dailytracker WHERE dancer1='Kexin' AND " +
          datesQuery +
          " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Kexin' AND " +
          datesQuery +
          " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Kexin' AND " +
          datesQuery +
          ") AS sumofminutes";

        sarahTimeQuery =
          "SELECT SUM(sumofminutes.sarahtime) FROM (SELECT SUM(dancer1_minutes) AS sarahtime FROM dailytracker WHERE dancer1='Sarah' AND " +
          datesQuery +
          " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Sarah' AND " +
          datesQuery +
          " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Sarah' AND " +
          datesQuery +
          ") AS sumofminutes";

        tristyTimeQuery =
          "SELECT SUM(sumofminutes.tristytime) FROM (SELECT SUM(dancer1_minutes) AS tristytime FROM dailytracker WHERE dancer1='Tristy' AND " +
          datesQuery +
          " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Tristy' AND " +
          datesQuery +
          " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Tristy' AND " +
          datesQuery +
          ") AS sumofminutes";

        yunhanTimeQuery =
          "SELECT SUM(sumofminutes.yunhantime) FROM (SELECT SUM(dancer1_minutes) AS yunhantime FROM dailytracker WHERE dancer1='Yunhan' AND " +
          datesQuery +
          " UNION ALL SELECT SUM(dancer2_minutes) FROM dailytracker WHERE dancer2='Yunhan' AND " +
          datesQuery +
          " UNION ALL SELECT SUM(dancer3_minutes) FROM dailytracker WHERE dancer3='Yunhan' AND " +
          datesQuery +
          ") AS sumofminutes";

        // if there is more than 1 name, loop through the names, run both queries
        // (time spent and set done) with the range of dates given
        // after getting all the data, send the Object to the client
        // if there is only 1 name, then run both queries for that name and send the Object to client
        if (dancerNames.includes(",")) {
          try {
            dancerNames = dancerNames.split(",");
            for (var m = 0; m < dancerNames.length; m++) {
              if (dancerNames[m] == "Jingxuan") {
                try {
                  await client.query(jingxuanSetsQuery).then((resp) => {
                    let result = resp.rows[0];
                    setArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }

                try {
                  await client.query(jingxuanTimeQuery).then((resp) => {
                    let result = resp.rows[0];
                    timeArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }
              } else if (dancerNames[m] == "Karan") {
                try {
                  await client.query(karanSetsQuery).then((resp) => {
                    let result = resp.rows[0];
                    setArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }

                try {
                  await client.query(karanTimeQuery).then((resp) => {
                    let result = resp.rows[0];
                    timeArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }
              } else if (dancerNames[m] == "Kexin") {
                try {
                  await client.query(kexinSetsQuery).then((resp) => {
                    let result = resp.rows[0];
                    setArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }

                try {
                  await client.query(kexinTimeQuery).then((resp) => {
                    let result = resp.rows[0];
                    timeArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }
              } else if (dancerNames[m] == "Sarah") {
                try {
                  await client.query(sarahSetsQuery).then((resp) => {
                    let result = resp.rows[0];
                    setArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }

                try {
                  await client.query(sarahTimeQuery).then((resp) => {
                    let result = resp.rows[0];
                    timeArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }
              } else if (dancerNames[m] == "Tristy") {
                try {
                  await client.query(tristySetsQuery).then((resp) => {
                    let result = resp.rows[0];
                    setArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }

                try {
                  await client.query(tristyTimeQuery).then((resp) => {
                    let result = resp.rows[0];
                    timeArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }
              } else if (dancerNames[m] == "Yunhan") {
                try {
                  await client.query(yunhanSetsQuery).then((resp) => {
                    let result = resp.rows[0];
                    setArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }

                try {
                  await client.query(yunhanTimeQuery).then((resp) => {
                    let result = resp.rows[0];
                    timeArray.push(result);
                  });
                } catch (err) {
                  console.error(err.stack);
                }
              }
            }
            // console.dir(setArray);
            dancerDataObject.setData = setArray;
            dancerDataObject.timeData = timeArray;
            res.send(JSON.stringify(dancerDataObject));
          } catch (err) {
            console.error(err.stack);
          }
        } else {
          if (dancerNames == "Jingxuan") {
            try {
              await client.query(jingxuanSetsQuery).then((resp) => {
                let result = resp.rows[0];
                setArray.push(result);
                dancerDataObject.setData = setArray;
              });
            } catch (err) {
              console.error(err.stack);
            }

            try {
              await client.query(jingxuanTimeQuery).then((resp) => {
                let result = resp.rows[0];
                timeArray.push(result);
                dancerDataObject.timeData = timeArray;
                res.send(JSON.stringify(dancerDataObject));
              });
            } catch (err) {
              console.error(err.stack);
            }
          } else if (dancerNames == "Karan") {
            try {
              await client.query(karanSetsQuery).then((resp) => {
                let result = resp.rows[0];
                setArray.push(result);
                dancerDataObject.setData = setArray;
              });
            } catch (err) {
              console.error(err.stack);
            }

            try {
              await client.query(karanTimeQuery).then((resp) => {
                let result = resp.rows[0];
                timeArray.push(result);
                dancerDataObject.timeData = timeArray;
                res.send(JSON.stringify(dancerDataObject));
              });
            } catch (err) {
              console.error(err.stack);
            }
          } else if (dancerNames == "Kexin") {
            try {
              await client.query(kexinSetsQuery).then((resp) => {
                let result = resp.rows[0];
                setArray.push(result);
                dancerDataObject.setData = setArray;
              });
            } catch (err) {
              console.error(err.stack);
            }

            try {
              await client.query(kexinTimeQuery).then((resp) => {
                let result = resp.rows[0];
                timeArray.push(result);
                dancerDataObject.timeData = timeArray;
                res.send(JSON.stringify(dancerDataObject));
              });
            } catch (err) {
              console.error(err.stack);
            }
          } else if (dancerNames == "Sarah") {
            try {
              await client.query(sarahSetsQuery).then((resp) => {
                let result = resp.rows[0];
                setArray.push(result);
                dancerDataObject.setData = setArray;
              });
            } catch (err) {
              console.error(err.stack);
            }

            try {
              await client.query(sarahTimeQuery).then((resp) => {
                let result = resp.rows[0];
                timeArray.push(result);
                dancerDataObject.timeData = timeArray;
                res.send(JSON.stringify(dancerDataObject));
              });
            } catch (err) {
              console.error(err.stack);
            }
          } else if (dancerNames == "Tristy") {
            try {
              await client.query(tristySetsQuery).then((resp) => {
                let result = resp.rows[0];
                setArray.push(result);
                dancerDataObject.setData = setArray;
              });
            } catch (err) {
              console.error(err.stack);
            }

            try {
              await client.query(tristyTimeQuery).then((resp) => {
                let result = resp.rows[0];
                timeArray.push(result);
                dancerDataObject.timeData = timeArray;
                res.send(JSON.stringify(dancerDataObject));
              });
            } catch (err) {
              console.error(err.stack);
            }
          } else if (dancerNames == "Yunhan") {
            try {
              await client.query(yunhanSetsQuery).then((resp) => {
                let result = resp.rows[0];
                setArray.push(result);
                dancerDataObject.setData = setArray;
              });
            } catch (err) {
              console.error(err.stack);
            }

            try {
              await client.query(yunhanTimeQuery).then((resp) => {
                let result = resp.rows[0];
                timeArray.push(result);
                dancerDataObject.timeData = timeArray;
                res.send(JSON.stringify(dancerDataObject));
              });
            } catch (err) {
              console.error(err.stack);
            }
          }
        }
      }
    }
  }
});

// receive the names of dancers 1, 2 and 3 from client
app.post("/dashboard/real-time-dashboard", function (req, res) {
  console.log("Received Real-Time Dashboard request: ", req.body);
  dancer_1 = req.body.realTimeDashboard.dancer1;
  dancer_2 = req.body.realTimeDashboard.dancer2;
  dancer_3 = req.body.realTimeDashboard.dancer3;

  console.log(dancer_1);
  console.log(dancer_2);
  console.log(dancer_3);
  res.sendStatus(200);
});

server.listen(PORT, function () {
  console.log("Server is running on Port: " + PORT);
});
