<script>
import { Pie, mixins } from "vue-chartjs";
const { reactiveProp } = mixins;

// Pie Chart that is constantly updated in real-time dashboard,
// uses a watcher in reactiveProp to rerender chart if there are changes to the data
export default {
  extends: Pie,
  mixins: [reactiveProp],
  data() {
    return {
      options: {
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
    };
  },
  mounted() {
    this.renderChart(this.chartData, this.options);
  },
};
</script>
