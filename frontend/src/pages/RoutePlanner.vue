<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
import { levelLabel } from '../levels'
const stations = ref([])
const start = ref('A1')
const end = ref('B2')
const out = ref(null)
const nameOf = (code) => stations.value.find((s) => s.code === code)?.name ?? code
onMounted(async () => { stations.value = (await getJSON('/api/stations')).items })
const run = async () => { out.value = await postJSON('/api/quote', { start: start.value, end: end.value, persist: true }) }
</script>
<template>
  <div class="page"><h1>最短站数票价</h1>
    <div class="panel">
      <select v-model="start"><option v-for="s in stations" :key="s.code" :value="s.code">{{ s.name }}</option></select>
      →
      <select v-model="end"><option v-for="s in stations" :key="s.code" :value="s.code">{{ s.name }}</option></select>
      <button @click="run">试算</button>
    </div>
    <div v-if="out" class="panel">
      <p v-if="out.reachable">
        站数 {{ out.hops }} · 应付票价 <span class="hero-num">¥{{ out.payable }}</span>
      </p>
      <p v-else class="muted">不可达</p>
      <template v-if="out.reachable">
        <table>
          <tr><td>基础票价（分段）</td><td style="text-align:right">¥{{ out.base_fare }}</td></tr>
          <tr v-for="(e,i) in out.congestion_edges" :key="i">
            <td>{{ nameOf(e.a) }} — {{ nameOf(e.b) }} 拥挤附加（{{ levelLabel(e.level) }}）</td>
            <td style="text-align:right" class="amt">+¥{{ e.surcharge }}</td>
          </tr>
          <tr v-if="out.congestion_edges.length === 0"><td class="muted">无拥挤边，附加为零</td><td style="text-align:right">¥0.00</td></tr>
          <tr><td>附加合计</td><td style="text-align:right" class="amt">+¥{{ out.congestion_total }}</td></tr>
        </table>
      </template>
    </div>
  </div>
</template>
