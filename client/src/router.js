import Vue from "vue";
import VueRouter from "vue-router";
import DancerInformation from "./components/DancerInformation.vue";
import PastDanceSets from "./components/PastDanceSets.vue";
import RealTimeDashboard from "./components/RealTimeDashboard.vue";
import HowToUse from "./components/HowToUse.vue";

Vue.use(VueRouter);

// application routes
// export router instance
export default new VueRouter({
  mode: "history",
  routes: [
    {
      path: "/",
      name: "dancerinformation",
      component: DancerInformation,
    },
    {
      path: "/dancer-information",
      name: "dancerinformation",
      component: DancerInformation,
    },
    {
      path: "/real-time-dashboard",
      name: "realtimedashboard",
      component: RealTimeDashboard,
    },
    {
      path: "/past-dance-sets",
      name: "pastdancesets",
      component: PastDanceSets,
    },
    {
      path: "/how-to-use",
      name: "howtouse",
      component: HowToUse,
    },
  ],
});
