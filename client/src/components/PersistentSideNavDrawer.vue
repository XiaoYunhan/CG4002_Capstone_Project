<template>
  <v-app>
    <v-container fill-height>
      <v-navigation-drawer
        height="100%"
        width="250"
        class="dashboard"
        color="#FF9800"
        fixed
        dark
        permanent
      >
        <div id="logo">
          <img
            :src="require('../assets/DanceDancev2.png')"
            height="100px"
            width="256px"
          />
          <h2
            style="
              color: white;
              font-family: courier;
              text-align: center;
              font-size: 20px;
              font-weight: bold;
            "
          >
            Dance Tracker
          </h2>
        </div>

        <v-list nav>
          <v-list-item-group>
            <v-list-item
              v-for="item in items"
              :key="item.title"
              :to="item.route"
              :disabled="haveData"
            >
              <v-list-item-icon>
                <v-icon>{{ item.icon }}</v-icon>
              </v-list-item-icon>

              <v-list-item-content>
                <v-list-item-title>{{ item.title }}</v-list-item-title>
              </v-list-item-content>
            </v-list-item>
          </v-list-item-group>
        </v-list>
      </v-navigation-drawer>
    </v-container>
  </v-app>
</template>

<script>
import {
  mdiDatabase,
  mdiAccountQuestion,
  mdiAccountGroup,
  mdiChartTree,
} from "@mdi/js";

export default {
  name: "PersistentSideNavDrawer",

  sockets: {
    dataNotAvailable(data) {
      // data is false for movements not the End move
      // so haveData set to true to disable side nav to prevent users from leaving the page
      // and potentially losing access to real-time data.
      // if End move, data is true, so haveData set to false to enable side nav
      this.haveData = !data;
      console.log("haveData: " + this.haveData);
    },
  },
  data() {
    return {
      items: [
        {
          title: "Dancer Information",
          icon: mdiAccountGroup,
          route: "/dancer-information",
        },
        {
          title: "Real-Time Dashboard",
          icon: mdiChartTree,
          route: "/real-time-dashboard",
        },
        {
          title: "Past Dance Sets",
          icon: mdiDatabase,
          route: "/past-dance-sets",
        },
        {
          title: "How To Use",
          icon: mdiAccountQuestion,
          route: "/how-to-use",
        },
      ],
      haveData: false,
    };
  },
};
</script>
