<template>
  <v-app>
    <v-main class="pa-5">
      <PartManager />
    </v-main>
  </v-app>
</template>

<script>
import PartManager from '../src/components/PartManager.vue'

export default {
  name: 'App',
  components: {
    PartManager
  }
}
</script>