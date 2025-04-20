<template>
  <v-data-table
    v-model="selected"
    :headers="headers"
    :items="items"
    :loading="isLoading"
    item-value="id"
    show-select
    :items-per-page="10"
    disable-pagination
    hide-default-footer
  >
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #item.permissions="{ item }">
      <ul class="ma-0 pa-0">
        <li v-for="perm in item.permissions" :key="perm.id">
          {{ perm.verbose }}
        </li>
      </ul>
    </template>
  </v-data-table>
</template>

<script lang="ts">
import Vue from 'vue'
import { Group } from '~/domain/models/profile/group'

export default Vue.extend({
  props: {
    value: {
      type: Array as () => Group[],
      required: true
    },
    items: {
      type: Array as () => Group[],
      required: true
    },
    total: {
      type: Number,
      required: false,
      default: 0
    },
    isLoading: {
      type: Boolean,
      required: true
    }
  },

  computed: {
    selected: {
      get(): Group[] {
        return this.value
      },
      set(val: Group[]) {
        this.$emit('input', val)
      }
    },
    headers(): object[] {
      return [
        { text: 'ID', value: 'id' },
        { text: 'Name', value: 'name' },
        { text: 'Permissions', value: 'permissions' }
      ]
    }
  }
})
</script>
