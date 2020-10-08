<script>
import { Bar, mixins } from "vue-chartjs";

// Bar Chart for time spent practicing that may change based on what information user would like to see
// in dancer information
export default {
  extends: Bar,
  mixins: [mixins.reactiveProp],
  data() {
    return {
      options: {
        scales: {
          yAxes: [
            {
              ticks: {
                beginAtZero: true,
              },
              gridLines: {
                display: true,
              },
            },
          ],
          xAxes: [
            {
              gridLines: {
                display: false,
              },
            },
          ],
        },
        plugins: {
          datalabels: {
            color: "black",
            textAlign: "center",
            font: {
              weight: "bold",
              size: 16,
            },
          },
        },
        legend: {
          display: false,
        },
        responsive: true,
        maintainAspectRatio: false,
      },
    };
  },
  // watcher to check if chart data and/or labels have changed
  // if there is a change, rerender chart
  watch: {
    chartData() {
      this.$data._chart.update();
    },
  },
  mounted() {
    this.renderChart(this.chartData, this.options);
  },
};
</script>
