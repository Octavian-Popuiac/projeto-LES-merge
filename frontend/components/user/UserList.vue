<template>
  <div>
    <v-data-table
      :value="value.filter(user => user.id !== getUserId)"
      :headers="headers"
      :items="filteredItems"
      :options.sync="options"
      :server-items-length="total"
      :search="search"
      :loading="isLoading"
      :loading-text="$t('generic.loading')"
      :no-data-text="$t('vuetify.noDataAvailable')"
      :footer-props="{
        showFirstLastPage: true,
        'items-per-page-options': [10, 50, 100],
        'items-per-page-text': $t('vuetify.itemsPerPageText'),
        'page-text': $t('dataset.pageText')
      }"
      item-key="id"
      show-select
      show-expand
      :item-class="itemClass"
      class="elevation-1"
      @input="$emit('input', $event)"
    >
      <template #top>
        <v-text-field
          v-model="search"
          :prepend-inner-icon="mdiMagnify"
          :label="$t('generic.search')"
          single-line
          hide-details
          filled
          class="mx-4"
        />
      </template>

      <!-- Username como texto em negrito -->
      <template #[`item.username`]="{ item }">
        <span class="font-weight-bold">{{ item.username }}</span>
      </template>

      <!-- Chip booleano para isStaff -->
      <template #[`item.isStaff`]="{ item }">
        <v-chip :color="item.isStaff ? 'green' : 'red'" dark small>
          {{ item.isStaff ? 'True' : 'False' }}
        </v-chip>
      </template>

      <!-- Chip booleano para isSuperuser -->
      <template #[`item.isSuperuser`]="{ item }">
        <v-chip :color="item.isSuperuser ? 'green' : 'red'" dark small>
          {{ item.isSuperuser ? 'True' : 'False' }}
        </v-chip>
      </template>

      <!-- Linha expandida com detalhes -->
      <template #[`expanded-item`]="{ item }">
        <td :colspan="headers.length">
          <v-card class="mx-4 my-2" outlined elevation="1">
            <v-card-title class="font-weight-medium grey--text text--darken-2">
              Detalhes do Utilizador
            </v-card-title>
            <v-divider></v-divider>
            <v-card-text class="py-4">
              <v-row>
                <v-col cols="12" sm="6">
                  <strong>ID:</strong> <span class="font-weight-bold">{{ item.id }}</span>
                </v-col>
                <v-col cols="12" sm="6">
                  <strong>Username:</strong> 
                  <span class="font-weight-bold">{{ item.username }}</span>
                </v-col>
                <v-col cols="12" sm="6">
                  <strong>Staff:</strong> {{ item.isStaff ? 'Sim' : 'Não' }}
                </v-col>
                <v-col cols="12" sm="6">
                  <strong>Superuser:</strong> {{ item.isSuperuser ? 'Sim' : 'Não' }}
                </v-col>
                <v-col cols="12" sm="6">
                  <strong>Email:</strong> {{ item.email || 'N/A' }}
                </v-col>
                <v-col cols="12" sm="6">
                  <strong>Data de criação:</strong>
                  {{ item.date_joined ? new Date(item.date_joined).toLocaleString('pt-PT', {
                    day: '2-digit',
                    month: '2-digit',
                    year: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  }) : 'N/A' }}
                </v-col>
                <v-col v-if="isStaff && item.id !== getUserId" cols="12" sm="6">
                    <!--Delete Button-->
                    <v-btn 
                      color="red" 
                      dark 
                      @click.stop=openDeleteDialog(item)
                    > 
                      {{ $t('generic.delete') }}
                    </v-btn>    
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </td>
      </template>
    </v-data-table>
    <v-dialog v-model="dialogDelete">
          <form-delete :selected="selectedUser" @cancel="dialogDelete = false" @remove="remove" />
    </v-dialog>
  </div>
</template>

<script lang="ts">
import { mapGetters } from 'vuex'
import { mdiMagnify } from '@mdi/js'
import Vue from 'vue'
import type { PropType } from 'vue'
import { DataOptions } from 'vuetify/types'
import { UserItem } from '~/domain/models/user/user'
import FormDelete from '~/components/user/FormDelete.vue'

export default Vue.extend({

  components: {
    FormDelete,
  },

  props: {
    isLoading: { type: Boolean, default: false, required: true },
    items: { type: Array as PropType<UserItem[]>, default: () => [], required: true },
    value: { type: Array as PropType<UserItem[]>, default: () => [], required: true },
    total: { type: Number, default: 0, required: true }
  },

  data() {
    return {
      search: this.$route.query.q || '',
      options: {} as DataOptions,
      mdiMagnify,
      dialogDelete: false, 
      selectedUser: [] as UserItem[],
    }
  },

  computed: {
    ...mapGetters('auth', ['isStaff','getUserId']),
    headers(): { text: any; value: string; sortable?: boolean }[] {
      return [
        { text: 'ID', value: 'id' },
        { text: this.$t('generic.username'), value: 'username' },
        { text: 'Staff', value: 'isStaff' },
        { text: 'Superuser', value: 'isSuperuser' }
      ]
    },

    filteredItems(): UserItem[] {
        const searchQuery = typeof this.search === 'string' ? this.search.toLowerCase() : ''
        if (!searchQuery) return this.items

        return this.items.filter(item =>
          item.username.toLowerCase().includes(searchQuery)
      )
    }
  },

  watch: {
    options: {
      handler() {
        this.updateQuery({
          query: {
            limit: this.options.itemsPerPage?.toString() || '10',
            offset: ((this.options.page - 1) * this.options.itemsPerPage).toString(),
            q: this.search
          }
        })
      },
      deep: true
    },
    search() {
      this.options.page = 1
      this.updateQuery({
        query: {
          limit: this.options.itemsPerPage?.toString() || '10',
          offset: '0',
          q: this.search
        }
      })
    }
  },

  methods: {
    updateQuery(payload: any) {
      const { sortBy, sortDesc } = this.options
      if (sortBy?.length === 1 && sortDesc?.length === 1) {
        payload.query.sortBy = sortBy[0]
        payload.query.sortDesc = sortDesc[0]
      } else {
        payload.query.sortBy = 'createdAt'
        payload.query.sortDesc = true
      }
      this.$emit('update:query', payload)
    },

    openDeleteDialog(user: UserItem) {
      this.selectedUser = [user];
      this.dialogDelete = true;
      console.log(this.dialogDelete);
    },

    async remove() { 
      if (this.selectedUser) {
        await this.$services.user.delete(this.selectedUser[0]);
      }
      this.dialogDelete = false;
      this.$router.push("/users");
    },

    itemClass(item: UserItem) {
      return item.isSuperuser ? 'superuser-row' : ''
    }
  }
})
</script>

<style scoped>
.superuser-row {
  background-color: #e8f5e9 !important;
}
</style>
