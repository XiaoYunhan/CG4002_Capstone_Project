<script>
import { Pie } from "vue-chartjs";

// Pie Chart that gets data from information obtained from server
export default {
  extends: Pie,
  props: {
    chartdata: {
      type: Object,
      default: null,
    },
    options: {
      type: Object,
      default: null,
    },
  },
  mounted() {
    this.renderChart(this.chartdata, this.options);
  },
};
</script>
