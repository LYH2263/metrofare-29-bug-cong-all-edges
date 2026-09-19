<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const d = ref(null)
onMounted(async () => { d.value = await getJSON('/api/dashboard') })
</script>
<template>
  <div class="page"><h1>线网概览</h1>
    <div v-if="d" class="panel">
      <p>站点 {{ d.station_count }} · 区间 {{ d.edge_count }}</p>
      <p>正常 {{ d.clean_stations }} · 种子 {{ d.dirty_stations }}</p>
    </div>
  </div>
</template>
