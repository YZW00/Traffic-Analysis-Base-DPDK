<template>
    <div id="app">
      <Navigator></Navigator>
      <!-- <router-view></router-view> -->
    </div>
  </template>

<script>
import Navigator from "../components/Navigator.vue"
export default{
  name: "App",
  comments: { Navigator },
  components: { Navigator }
}
</script>