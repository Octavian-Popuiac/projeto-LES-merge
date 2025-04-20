<template>
  <v-container>
    <!-- Discrepâncias Detetadas -->
    <v-card class="mb-6">
      <v-card-title class="d-flex justify-space-between align-center">
        <span class="text-h6">Discrepâncias Detetadas (em tempo real)</span>
        <v-btn
          class="text-capitalize"
          :disabled="!canSave"
          color="primary"
          @click="saveSelected"
        >
          Guardar Selecionadas
        </v-btn>
      </v-card-title>

      <v-card-text>
        <discrepancy-list
          v-model="selected"
          :items="annotationStats"
          :headers="detectHeaders"
          :is-loading="isLoading"
          :show-select="true"
          @save-single="saveSingle"
        />
      </v-card-text>
    </v-card>

    <!-- Discrepâncias Guardadas -->
    <v-card>
      <v-card-title class="d-flex justify-space-between align-center">
        <span class="text-h6">Discrepâncias Guardadas (base de dados)</span>
        <v-switch
          v-model="showOnlyLatest"
          label="Mostrar apenas a mais recente por exemplo"
          inset
        />
      </v-card-title>

      <v-card-text>
        <discrepancy-list
          :value="[]"
          :items="filteredSavedDiscrepancies"
          :headers="savedHeaders"
          :is-loading="isLoading"
          :show-select="false" 
          @resolve="markAsResolved"
          @delete="deleteDiscrepancy"
        />
      </v-card-text>
    </v-card>

    <!-- Comparação Lado a Lado -->
    <v-card class="mt-6">
      <v-card-title>
        <span class="text-h6">Comparação Lado a Lado</span>
      </v-card-title>
      <v-card-text>
        <v-simple-table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Texto</th>
              <th>Discrepância</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredSavedDiscrepancies" :key="item.id">
              <td>{{ item.id }}</td>
              <td>{{ item.example }}</td>
              <td>
                <div class="mb-2 text-caption grey--text">
                  Total de votos: {{ getTotalVotes(item.labels) }}
                </div>
                <v-simple-table dense class="inner-label-table">
                  <thead>
                    <tr>
                      <th>Label</th>
                      <th>Contagem</th>
                      <th>Percentagem</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="label in item.labels"
                      :key="label.label"
                      :class="{ 'highlight-label': isTopLabel(label, item.labels) }"
                    >
                      <td>
                        <v-chip :color="label.color || '#2196f3'" dark class="ma-1">
                          {{ label.label }}
                        </v-chip>
                      </td>
                      <td>
                        {{ label.count }}
                        <v-icon
                          v-if="isTopLabel(label, item.labels)"
                          small
                          color="amber"
                          class="ml-1"
                        >mdi-star</v-icon>
                      </td>
                      <td>
                        <div class="d-flex align-center">
                          {{ calculatePercentage(label.count, item.labels) }}%
                          <v-progress-linear
                            :value="calculatePercentage(label.count, item.labels)"
                            :color="label.color"
                            height="6"
                            class="ml-2 flex-grow-1"
                            style="width: 100px"
                          />
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </v-simple-table>
              </td>
            </tr>
          </tbody>
        </v-simple-table>
      </v-card-text>
    </v-card>
    <v-dialog v-model="confirmDeleteDialog" max-width="400px">
      <v-card>
        <v-card-title class="headline">Confirmar Eliminação</v-card-title>
        <v-card-text>
          Tem certeza que deseja eliminar esta discrepância?
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey darken-1" text @click="confirmDeleteDialog = false">
            Cancelar
          </v-btn>
          <v-btn color="error" @click="confirmDeleteAction">
            Eliminar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import DiscrepancyList from '~/components/discrepancy/DiscrepancyList.vue'

export default Vue.extend({
  components: {
    DiscrepancyList
  },

  layout: 'project',
  middleware: ['check-auth', 'auth', 'setCurrentProject'],

  data() {
    return {
      confirmDeleteDialog: false,
      itemToDelete: null,
      isLoading: false,
      savedDiscrepancies: [] as any[],
      annotationStats: [] as any[],
      selected: [] as any[],
      showOnlyLatest: true,
      detectHeaders: [
        { text: 'ID', value: 'id' },
        { text: 'Texto', value: 'example_preview' },
        { text: 'Labels', value: 'labels' }
      ],
      savedHeaders: [
        { text: 'ID', value: 'id' },
        { text: 'Exemplo', value: 'example' },
        { text: 'Labels', value: 'labels' },
        { text: 'Estado', value: 'status' },
        { text: 'Criado em', value: 'created_at' },
        { text: 'Ações', value: 'actions', sortable: false }
      ]
    }
  },

  computed: {
    projectId(): number {
      return Number(this.$route.params.id)
    },
    canSave(): boolean {
      return this.selected.length > 0
    },
    filteredSavedDiscrepancies(): any[] {
      if (!this.showOnlyLatest) return this.savedDiscrepancies

      const latestByExample = new Map()
      for (const d of this.savedDiscrepancies) {
        const current = latestByExample.get(d.example)
        if (!current || new Date(d.created_at) > new Date(current.created_at)) {
          latestByExample.set(d.example, d)
        }
      }
      return Array.from(latestByExample.values())
    }
  },

  async fetch() {
    this.isLoading = true
    try {
      const [discrepancies, stats, labelTypes] = await Promise.all([
        this.$repositories.discrepancy.list(this.projectId),
        this.$repositories.discrepancy.detect(this.projectId),
        this.$services.categoryType.list(this.projectId.toString())
      ])

      const colorMap = Object.fromEntries(
        labelTypes.map((label: any) => [label.text, label.backgroundColor])
      )

      this.savedDiscrepancies = discrepancies.map((item: any) => ({
        ...item,
        labels: item.labels.map((label: any) => ({
          ...label,
          color: colorMap[label.label] || '#cccccc'
        }))
      }))

      this.annotationStats = stats.map((item: any) => ({
        ...item,
        id: item.example_id,
        example: item.example_id,
        example_text: item.example_text,
        example_preview: item.example_text.slice(0, 120) + '...',
        labels: item.label_stats.map((label: any) => ({
          ...label,
          color: colorMap[label.label] || '#cccccc'
        })),
        created_at: null,
        status: null
      }))
    } catch (e) {
      console.error('Erro ao carregar discrepâncias:', e)
    } finally {
      this.isLoading = false
    }
  },

  methods: {
    async saveSingle(item: any) {
      try {
        await this.$repositories.discrepancy.save(
          this.projectId,
          item.example_id,
          item.labels
        )
        this.$fetch()
      } catch (e) {
        console.error('Erro ao guardar discrepância:', e)
      }
    },

    async saveSelected() {
      try {
        for (const item of this.selected) {
          await this.$repositories.discrepancy.save(
            this.projectId,
            item.example_id,
            item.labels
          )
        }
        this.selected = []
        this.$fetch()
      } catch (e) {
        console.error('Erro ao guardar discrepâncias selecionadas:', e)
      }
    },

    async markAsResolved(item: any) {
      try {
        await this.$repositories.discrepancy.updateStatus(item.id, 'resolved')
        this.$fetch()
      } catch (e) {
        console.error('Erro ao marcar como resolvida:', e)
      }
    },

    calculatePercentage(count: number, labels: any[]): number {
      const total = labels.reduce((sum, l) => sum + l.count, 0)
      return total > 0 ? parseFloat(((count / total) * 100).toFixed(0)) : 0
    },

    getTotalVotes(labels: any[]): number {
      return labels.reduce((sum, l) => sum + l.count, 0)
    },

    isTopLabel(label: any, labels: any[]): boolean {
      const max = Math.max(...labels.map(l => l.count))
      return label.count === max && max > 0
    },

    deleteDiscrepancy(item: any) {
      this.itemToDelete = item;
      this.confirmDeleteDialog = true;
    },
    
    async confirmDeleteAction() {
      try {
        if (!this.itemToDelete) return;
        
        await this.$repositories.discrepancy.delete(this.itemToDelete.id);
        this.$fetch(); // Recarregar dados
        
        // Limpa o estado e fecha o diálogo
        this.confirmDeleteDialog = false;
        this.itemToDelete = null;
      } catch (e) {
        console.error('Erro ao eliminar discrepância:', e);
        this.$store.dispatch('notification/error', 'Erro ao eliminar discrepância');
      }
    }
  }
})
</script>

<style scoped>
th {
  white-space: nowrap;
}
td {
  vertical-align: top;
}
.inner-label-table {
  margin-top: 10px;
  background-color: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
}
.highlight-label {
  font-weight: bold;
}
</style>
