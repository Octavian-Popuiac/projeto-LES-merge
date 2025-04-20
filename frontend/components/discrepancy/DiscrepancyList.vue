<template>
  <v-data-table
    v-model="selected"
    :headers="computedHeaders"
    :items="items"
    :loading="isLoading"
    :item-value="itemValue"
    :show-select="showSelect"
    disable-pagination
    hide-default-footer
  >
    <!-- Coluna de Labels -->
    <template #[`item.labels`]="{ item }">
      <div class="d-flex flex-wrap" style="gap: 6px;">
        <v-chip
          v-for="label in item.labels"
          :key="label.label"
          :color="label.color"
          dark
          small
          class="ma-1"
        >
          {{ label.label }} — {{ label.count }} ({{ label.percentage.toFixed(1) }}%)
        </v-chip>
      </div>
    </template>


    <!-- Coluna de Estado com Cor -->
    <template #[`item.status`]="{ item }">
      <v-chip
        :color="item.status === 'resolved' ? 'green' : 'orange darken-2'"
        dark
        small
      >
        {{ item.status === 'resolved' ? 'Resolvida' : 'Por Resolver' }}
      </v-chip>
    </template>

    <!-- Coluna de Ações -->
    <template #[`item.actions`]="{ item }">
      <div class="d-flex">
        <v-btn
          small
          color="primary"
          text
          @click="openResolveDialog(item)"
          v-if="item.status === 'unresolved'"
          class="mr-2"
        >
          Resolver
        </v-btn>
        <v-btn
          small
          color="error"
          text
          @click="$emit('delete', item)"
        >
          Eliminar
        </v-btn>
        <v-chip v-if="item.status === 'resolved'" color="green" small>Resolvida</v-chip>
      </div>
    </template>

    <!-- Coluna de Data -->
    <template #[`item.created_at`]="{ item }">
      <span v-if="item.created_at">
        {{ formatDate(item.created_at) }}
      </span>
      <span v-else>-</span>
    </template>
  </v-data-table>
</template>

<script lang="ts">
import Vue from 'vue'
import type { PropType } from 'vue'

interface LabelStat {
  label: string
  count: number
  percentage: number
}

interface DiscrepancyEntry {
  id?: number
  example: number
  example_text?: string
  example_preview?: string
  labels: LabelStat[]
  status?: string
  created_at?: string
}

export default Vue.extend({
  props: {
    value: {
      type: Array as PropType<DiscrepancyEntry[]>,
      required: true
    },
    items: {
      type: Array as PropType<DiscrepancyEntry[]>,
      required: true
    },
    isLoading: {
      type: Boolean,
      default: false
    },
    headers: {
      type: Array as PropType<any[]>,
      default: () => []
    },
    showSelect: {  
      type: Boolean,
      default: true 
    }
  },

  data() {
    return {
      itemValue: 'example'
    }
  },

  computed: {
    selected: {
      get(): DiscrepancyEntry[] {
        return this.value
      },
      set(val: DiscrepancyEntry[]) {
        this.$emit('input', val)
      }
    },
    computedHeaders(): any[] {
      return this.headers.length > 0
        ? this.headers
        : [
            { text: 'Texto', value: 'example_preview' },
            { text: 'Labels', value: 'labels' },
            { text: 'Estado', value: 'status' },
            { text: 'Criado em', value: 'created_at' }
          ]
    }
  },

  methods: {
    formatDate(date: string): string {
      const d = new Date(date)
      return d.toLocaleString('pt-PT', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
  }
})
</script>