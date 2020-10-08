import Vue from "vue";
import VueRouter from "vue-router";
import vuetify from "./plugins/vuetify";
import socketio from "socket.io-client";
import VueSocketIO from "vue-socket.io";
import ChartJsPluginDataLabels from "chartjs-plugin-datalabels";
import Paginate from "vuejs-paginate";
import App from "./App";
import router from "./router";

const SocketInstance = socketio.connect("http://localhost:4000", {
  query: {
    token: window.localStorage.getItem("auth"),
  },
});

Vue.use(
  new VueSocketIO({
    debug: true,
    connection: SocketInstance,
  })
);

Vue.config.productionTip = false;
Vue.use(VueRouter);
Vue.component("paginate", Paginate);

new Vue({
  el: "#app",
  vuetify,
  router,
  ChartJsPluginDataLabels,
  icons: {
    iconfont: "mdiSvg", // "mdiSvg" || 'mdi' || 'mdiSvg' || 'md' || 'fa' || 'fa4' || 'faSvg'
  },
  render: (h) => h(App),
});
