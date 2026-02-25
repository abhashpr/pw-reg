<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup>
import { onBeforeMount } from 'vue'

onBeforeMount(() => {
  // Initialize app
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html,
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  color: #333;
}

#app {
  width: 100%;
  min-height: 100vh;
}
</style>
