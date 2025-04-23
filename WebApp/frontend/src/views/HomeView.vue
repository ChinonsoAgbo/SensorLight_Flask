<template>
    <div>
      <h2>IMU Sensor Data</h2>
      <p>Acceleration: X={{ acc.x }}, Y={{ acc.y }}, Z={{ acc.z }}</p>
      <p>Rotation: Z={{ rotation.z }}</p>
      <p>Timestamp: {{ timestamp }}</p>
  
      <LiveChart ref="liveChart" />
    </div>
  </template>
  
  <script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { io } from 'socket.io-client'
import LiveChart from '@/components/LiveChart.vue'

const socket = io('http://localhost:5000')

const acc = ref({ x: 0, y: 0, z: 0 })
const rotation = ref({ z: 0 })
const timestamp = ref(0)

const liveChart = ref<InstanceType<typeof LiveChart>>() // Use InstanceType for better type hinting

function pushData(label: string, values: number[]) {
  const chart = liveChart.value!.chartData // Use non-null assertion as liveChart will be mounted

  // Add new time label
  chart.labels.push(label)
  if (chart.labels.length > 50) chart.labels.shift()

  // Update each dataset
  chart.datasets[0].data.push(values[0]) // Acc X
  chart.datasets[1].data.push(values[1]) // Acc Y
  chart.datasets[2].data.push(values[2]) // Acc Z
  chart.datasets[3].data.push(values[3]) // Rot Z

  // Keep data arrays limited
  chart.datasets.forEach(dataset => {
    if (dataset.data.length > 50) dataset.data.shift()
  })
  // Force chart re-render
  liveChart.value!.updateChart() // Use non-null assertion
}

onMounted(() => {
  socket.on('connect', () => {
    console.log('✅ Connected to WebSocket')
  })

  socket.on('imu_update', (data) => {
    acc.value = { ...data.acceleration } // Update acc reactively
    rotation.value = { ...data.rotation } // Update rotation reactively
    timestamp.value = data.timestampMillis

    pushData(
      new Date().toLocaleTimeString(),
      [data.acceleration.x, data.acceleration.y, data.acceleration.z, data.rotation.z]
    )
  })

  socket.on('disconnect', () => {
    console.log('❌ Disconnected from WebSocket')
  })
})

onBeforeUnmount(() => {
  socket.disconnect()
})
</script>