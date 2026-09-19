<template>
  <div class="metro-shell">
    <header class="line-bar">
      <span class="line-a">1号线</span>
      <span class="line-b">支线</span>
      <span class="brand">Metrofare</span>
    </header>
    <nav class="tab-nav">
      <router-link to="/">线网</router-link>
      <router-link to="/stations">站点</router-link>
      <router-link to="/planner">票价试算</router-link>
      <router-link to="/fares">规则</router-link>
      <router-link to="/network">邻接</router-link>
      <router-link to="/history">记录</router-link>
      <router-link to="/settings">设置</router-link>
    </nav>
    <router-view />
  </div>
</template>
