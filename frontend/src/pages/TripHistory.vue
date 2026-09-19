<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
import { levelLabel } from '../levels'
const items = ref([])
const openId = ref('')
const detail = ref(null)
const error = ref('')
const stationMap = ref({})

const nameOf = (code) => stationMap.value[code] ?? code
const asResult = (row) => {
  if (!row) return null
  const r = JSON.parse(row.result_json)
  // 兼容模块上线前生成的旧记录：快照里没有拥挤字段，按原样视为无拥挤边
  return {
    ...r,
    base_fare: r.base_fare ?? r.fare,
    congestion_edges: r.congestion_edges ?? [],
    congestion_total: r.congestion_total ?? 0,
    payable: r.payable ?? r.fare,
  }
}
const asInput = (row) => JSON.parse(row.input_json)

async function openById() {
  error.value = ''
  detail.value = null
  const id = String(openId.value).trim()
  if (!id) return
  try {
    const row = await getJSON(`/api/history/${encodeURIComponent(id)}`)
    detail.value = { ...row, input: asInput(row), result: asResult(row) }
  } catch (err) {
    error.value = `打开记录 #${id} 失败：${err.message}`
  }
}

async function openRow(row) {
  openId.value = row.id
  detail.value = { ...row, input: asInput(row), result: asResult(row) }
  error.value = ''
}

onMounted(async () => {
  const [history, stations] = await Promise.all([getJSON('/api/history'), getJSON('/api/stations')])
  items.value = history.items
  stationMap.value = Object.fromEntries(stations.items.map((s) => [s.code, s.name]))
})
</script>
<template>
  <div class="page"><h1>试算记录</h1>
    <div class="panel">
      按编号打开
      <input v-model="openId" type="number" min="1" style="width:6rem" @keyup.enter="openById" />
      <button @click="openById">打开</button>
      <span v-if="error" class="muted">{{ error }}</span>
    </div>
    <table>
      <tr v-for="h in items" :key="h.id"
          :style="detail && detail.id === h.id ? 'background:#1d2c52' : ''"
          style="cursor:pointer" @click="openRow(h)">
        <td>#{{ h.id }}</td><td>{{ h.created_at }}</td><td>{{ h.kind }}</td>
      </tr>
    </table>
    <div v-if="detail" class="panel">
      <h3>记录 #{{ detail.id }} 的冻结快照</h3>
      <p class="muted">{{ detail.created_at }} · 拥挤附加只按当时途经边累计，后续清除不影响本记录</p>
      <template v-if="detail.result.reachable">
        <p>
          {{ nameOf(detail.input.start) }} → {{ nameOf(detail.result.end) }} · 站数 {{ detail.result.hops }}
          · 应付 <span class="hero-num">¥{{ detail.result.payable }}</span>
        </p>
        <table>
          <tr><td>基础票价（分段）</td><td style="text-align:right">¥{{ detail.result.base_fare }}</td></tr>
          <tr v-for="(e,i) in detail.result.congestion_edges" :key="i">
            <td>{{ nameOf(e.a) }} — {{ nameOf(e.b) }} 拥挤附加（{{ levelLabel(e.level) }}）</td>
            <td style="text-align:right" class="amt">+¥{{ e.surcharge }}</td>
          </tr>
          <tr v-if="detail.result.congestion_edges.length === 0">
            <td class="muted">当时无拥挤边，附加为零</td><td style="text-align:right">¥0.00</td>
          </tr>
          <tr><td>附加合计</td><td style="text-align:right" class="amt">+¥{{ detail.result.congestion_total }}</td></tr>
        </table>
      </template>
      <p v-else class="muted">该询价不可达。</p>
    </div>
  </div>
</template>
