<template>
  <v-container>
    <PerspectiveCreateForm :project-id="projectId" @created="handleCreated" />
  </v-container>
</template>

<script>
import PerspectiveCreateForm from "@/components/perspectives/PerspectiveCreateForm.vue";

export default {
  layout: "project",
  middleware: ["check-auth", "auth", "setCurrentProject"],

  components: {
    PerspectiveCreateForm,
  },

  computed: {
    projectId() {
      return this.$route.params.id;
    },
  },

  methods: {
    handleCreated() {
      // Podes adicionar um toast/snackbar aqui se quiseres dar feedback
      console.log("Perspetiva criada com sucesso!");
    },
  },
};
</script>
