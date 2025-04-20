<template>
    <v-card class="mt-4" outlined>
      <v-card-title>Discrepancies</v-card-title>
      <v-divider />
      <v-card-text>
        <v-list v-if="filteredDiscrepancies.length">
          <v-alert type="warning">Discrepancies found.</v-alert>
          <v-list-item v-for="discrepancy in filteredDiscrepancies" :key="discrepancy.id">
            <v-list-item-content>
              <v-chip 
                v-for="label in discrepancy.labelStats" 
                :key="label.label" 
                class="ma-1"
                
                >
                  {{ label.label }}: {{ label.count }} ({{ label.percentage }}%)
              </v-chip>
            </v-list-item-content>
          </v-list-item>
        </v-list>
        <v-alert v-else type="info">No discrepancies found.</v-alert>
      </v-card-text>
    </v-card>
  </template>
  
  <script>
  import { ref, computed, onMounted, watch } from "@nuxtjs/composition-api";
  import { APIDiscrepancyRepository } from "@/repositories/discrepancy/apiDiscrepancyRepository";
  
  export default {
    props: {
      projectId: {
        type: String,
        required: true,
      },
      exampleId: {
        type: Number,
        required: true,
      }
    },
    setup(props) {
      const discrepancies = ref([]);
      const repository = new APIDiscrepancyRepository();
  
      const fetchDiscrepancies = async () => {
        if (!props.projectId) return;
        try {
          const raw = await repository.detect(Number(props.projectId));
          discrepancies.value = raw.map(item => {
            const total = item.label_stats.reduce((sum, l) => sum + l.count, 0);
            const labelStats = item.label_stats.map(l => ({
              ...l,
              percentage: total > 0 ? Math.round((l.count / total) * 100) : 0
            }));
            return {
              ...item,
              labelStats
            };
          });
        } catch (error) {
          console.error("Error fetching discrepancies:", error);
        }
      };
  
      onMounted(fetchDiscrepancies);
      
      // Watch for changes in projectId to fetch discrepancies when it updates
      watch(() => props.projectId, fetchDiscrepancies, { immediate: true });
  
      const filteredDiscrepancies = computed(() => {
        return discrepancies.value.filter(d => d.example_id === props.exampleId);
      });
  
      return { filteredDiscrepancies, fetchDiscrepancies };
    },
  };
  </script>
