<template>
  <div>
    <h1>IMU Sensor Data (Accelerometer)</h1>
    <p>Timestamp: <span>{{ timestamp }}</span></p>
    <p>X: <span>{{ x }}</span></p>
    <p>Y: <span>{{ y }}</span></p>
    <p>Z: <span>{{ z }}</span></p>

    <!-- Chart.js container -->
    <canvas id="imuChart" ref="imuChart"></canvas>
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted, ref } from 'vue';
import { io } from 'socket.io-client';
import Chart from 'chart.js/auto';

export default defineComponent({
  name: 'ImuChart',
  setup() {
    const imuChartRef = ref<HTMLCanvasElement | null>(null);
    const timestamp = ref<number>(0);
    const x = ref<number>(0);
    const y = ref<number>(0);
    const z = ref<number>(0);

    let imuChart: Chart | null = null;

    // WebSocket client setup
    const socket = io('http://localhost:5000'); // Change the server URL if needed

    // Setup Chart.js
    const setupChart = () => {
      const ctx = imuChartRef.value?.getContext('2d');
      if (ctx) {
        imuChart = new Chart(ctx, {
          type: 'line',
          data: {
            labels: [], // Time labels
            datasets: [
              {
                label: 'X-Axis Acceleration',
                data: [],
                borderColor: 'red',
                backgroundColor: 'rgba(255, 0, 0, 0.1)',
                borderWidth: 2
              },
              {
                label: 'Y-Axis Acceleration',
                data: [],
                borderColor: 'green',
                backgroundColor: 'rgba(0, 255, 0, 0.1)',
                borderWidth: 2
              },
              {
                label: 'Z-Axis Acceleration',
                data: [],
                borderColor: 'blue',
                backgroundColor: 'rgba(0, 0, 255, 0.1)',
                borderWidth: 2
              }
            ]
          },
          options: {
            responsive: true,
            scales: {
              x: { title: { display: true, text: 'Time' } },
              y: { title: { display: true, text: 'Acceleration (m/s²)' }, beginAtZero: false }
            }
          }
        });
      }
    };

    // Handle incoming IMU data
    const handleImuUpdate = (data: any) => {
      const receivedTimestamp = parseInt(data.timestampMillis);
      const receivedX = parseFloat(data.accelerationInGs.x) || 0;
      const receivedY = parseFloat(data.accelerationInGs.y) || 0;
      const receivedZ = parseFloat(data.accelerationInGs.z) || 0;

      // Update UI with latest data
      timestamp.value = receivedTimestamp;
      x.value = receivedX;
      y.value = receivedY;
      z.value = receivedZ;

      // Update chart with new data
      if (imuChart) {
        imuChart.data.labels.push(receivedTimestamp);
        imuChart.data.datasets[0].data.push(receivedX);
        imuChart.data.datasets[1].data.push(receivedY);
        imuChart.data.datasets[2].data.push(receivedZ);

        // Keep only the last 200 data points
        if (imuChart.data.labels.length > 200) {
          imuChart.data.labels.shift();
          imuChart.data.datasets[0].data.shift();
          imuChart.data.datasets[1].data.shift();
          imuChart.data.datasets[2].data.shift();
        }

        imuChart.update();
      }
    };

    // Connect to WebSocket and listen for IMU updates
    onMounted(() => {
      socket.on('imu_update', handleImuUpdate);
      setupChart();
    });

    return {
      timestamp,
      x,
      y,
      z,
      imuChartRef
    };
  }
});
</script>

<style scoped>
/* Add some styling to center and size the chart */
#imuChart {
  width: 100%;
  height: 400px;
}
</style>
