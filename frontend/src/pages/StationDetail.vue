<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getJSON } from '../api'
const route = useRoute()
const st = ref(null)
const load = async () => { st.value = await getJSON(`/api/stations/${route.params.code}`) }
onMounted(load); watch(() => route.params.code, load)
</script>
<template>
  <div class="page" v-if="st"><h1>{{ st.name }}</h1><p class="muted">编码 {{ st.code }}</p></div>
</template>
