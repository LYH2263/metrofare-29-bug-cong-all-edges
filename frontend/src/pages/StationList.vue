<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
onMounted(async () => { items.value = (await getJSON('/api/stations')).items })
</script>
<template>
  <div class="page"><h1>站点</h1>
    <table><tr v-for="s in items" :key="s.code"><td>{{ s.code }}</td><td>{{ s.name }}</td>
      <td><router-link :to="`/stations/${s.code}`">详情</router-link></td></tr></table>
  </div>
</template>
