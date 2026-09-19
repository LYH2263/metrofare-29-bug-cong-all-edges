<script setup>
import { onMounted, ref } from 'vue'
import { deleteJSON, getJSON, putJSON } from '../api'
import { LEVELS, levelLabel } from '../levels'

const items = ref([])
const stations = ref([])
const error = ref('')

const nameOf = (code) => stations.value.find((s) => s.code === code)?.name ?? code
const levelText = (e) => (e.level ? levelLabel(e.level) : '畅通')

async function reload() {
  const [edgeData, stationData] = await Promise.all([
    getJSON('/api/edges'),
    getJSON('/api/stations'),
  ])
  stations.value = stationData.items
  items.value = edgeData.items.map((e) => ({
    ...e,
    draft: { level: e.level ?? 'light', surcharge: e.surcharge ?? 1 },
  }))
}

async function save(e) {
  error.value = ''
  try {
    const amount = Number(e.draft.surcharge)
    const saved = await putJSON('/api/congestion', {
      a: e.a,
      b: e.b,
      level: e.draft.level,
      surcharge: amount,
    })
    e.level = saved.level
    e.surcharge = saved.surcharge
  } catch (err) {
    error.value = `保存 ${e.a}—${e.b} 失败：${err.message}`
  }
}

async function clear(e) {
  error.value = ''
  try {
    await deleteJSON(`/api/congestion?a=${encodeURIComponent(e.a)}&b=${encodeURIComponent(e.b)}`)
    e.level = null
    e.surcharge = null
  } catch (err) {
    error.value = `清除 ${e.a}—${e.b} 失败：${err.message}`
  }
}

onMounted(reload)
</script>
<template>
  <div class="page"><h1>邻接区间</h1>
    <p v-if="error" class="muted">{{ error }}</p>
    <table>
      <tr>
        <th>区间</th><th>当前状态</th><th>拥挤等级</th><th>加价（元）</th><th></th>
      </tr>
      <tr v-for="(e,i) in items" :key="i">
        <td>{{ nameOf(e.a) }} — {{ nameOf(e.b) }}<div class="muted">{{ e.a }} — {{ e.b }}</div></td>
        <td>
          <span v-if="e.level">{{ levelText(e) }} · ¥{{ e.surcharge }}</span>
          <span v-else class="muted">畅通 · 无附加</span>
        </td>
        <td>
          <select v-model="e.draft.level">
            <option v-for="l in LEVELS" :key="l.value" :value="l.value">{{ l.label }}</option>
          </select>
        </td>
        <td><input v-model="e.draft.surcharge" type="number" min="0" step="0.5" style="width:5.5rem" /></td>
        <td>
          <button @click="save(e)">保存</button>
          <button class="btn-ghost" @click="clear(e)" :disabled="!e.level">清除</button>
        </td>
      </tr>
    </table>
  </div>
</template>
