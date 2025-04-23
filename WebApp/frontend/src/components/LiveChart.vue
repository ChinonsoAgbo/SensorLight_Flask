<template>
    <Line :data="chartData" :options="chartOptions" />
  </template>
  
  <script setup lang="ts">
  import { Line } from 'vue-chartjs'
  import {
    Chart as ChartJS,
    Title,
    Tooltip,
    Legend,
    LineElement,
    PointElement,
    LinearScale,
    CategoryScale
  } from 'chart.js'
  import { ref, reactive } from 'vue'
  
  const chartRef = ref()
  ChartJS.register(Title, Tooltip, Legend, LineElement, PointElement, LinearScale, CategoryScale)
  
  const MAX_POINTS = 100 // Limit to last 50 points for clarity
  
  const chartData = reactive({
    labels: [] as string[],
    datasets: [
      {
        label: 'Accel X',
        data: [] as number[],
        borderColor: 'rgb(255, 99, 132)',
        tension: 0.1
      },
      {
        label: 'Accel Y',
        data: [] as number[],
        borderColor: 'rgb(54, 162, 235)',
        tension: 0.1
      },
      {
        label: 'Accel Z',
        data: [] as number[],
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1
      },
      {
        label: 'Rotation Z',
        data: [] as number[],
        borderColor: 'rgb(255, 206, 86)',
        tension: 0.1
      }
    ]
  })
  
  const chartOptions = {
    responsive: true,
    animation: false,
    scales: {
      y: {
        beginAtZero: true
      }
    }
  }
  
  // Expose chartData for parent to update
  defineExpose({ chartData , 
    updateChart: () => chartRef.value?.chart?.update()
  })
  </script>
  