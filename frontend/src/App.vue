<template>
  <router-view />
</template>

<script setup>
// 使用 Vue Router 来管理页面
</script>

<style>
/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #E6E8EA;
  background-color: #111111; /* Mixpanel app base */
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #111111;
}

::-webkit-scrollbar-thumb {
  background: #2A2A2A;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #444444;
}

/* 全局按钮样式 */
button {
  font-family: inherit;
  cursor: pointer;
}

/* Utilities */
.mono {
  font-family: 'JetBrains Mono', monospace;
}
</style>
