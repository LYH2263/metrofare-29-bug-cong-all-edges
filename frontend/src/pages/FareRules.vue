<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
onMounted(async () => { items.value = (await getJSON('/api/fare-rules')).items })
</script>
<template>
  <div class="page"><h1>票价阶梯(按站数)</h1>
    <table><thead><tr><th>最多站数</th><th>票价</th></tr></thead>
      <tbody><tr v-for="r in items" :key="r.id"><td>{{ r.max_hops ?? '以上' }}</td><td>{{ r.price }}</td></tr></tbody></table>
  </div>
</template>
