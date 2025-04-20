<template>
  <v-card>
    <v-card-text> . </v-card-text>
    <v-card-title v-if="isStaff">
      <v-btn
        class="text-capitalize ms-2"
        color="primary"
        @click.stop="dialogCreate = true"
      >
        {{ $t('generic.create') }}
      </v-btn>
      <v-dialog v-model="dialogCreate" max-width="600px">
        <form-create @cancel="dialogCreate = false" @create="handleCreateSuccess" />
      </v-dialog>
      <v-btn
        class="text-capitalize ms-2"
        :disabled="!canDelete"
        outlined
        @click.stop="dialogDelete = true"
      >
        {{ $t('generic.delete') }}
      </v-btn>
      <v-dialog v-model="dialogDelete">
        <form-delete :selected="selected" @cancel="dialogDelete = false" @remove="remove" />
      </v-dialog>
    </v-card-title>

    <v-alert
      v-if="successMessage"
      type="success"
      dense
      outlined
      class="mx-4 mb-4"
      dismissible
      @input="successMessage = ''"
    >
      {{ successMessage }}
    </v-alert>

    <user-list
      v-model="selected"
      :items="users.items"
      :is-loading="isLoading"
      :total="users.count"
      @update:query="updateQuery"
    />
  </v-card>
</template>

<script lang="ts">
import _ from 'lodash'
import Vue from 'vue'
import { mapGetters } from 'vuex'
import UserList from '@/components/user/UserList.vue'
import { UserItem } from '~/domain/models/user/user'
import FormCreate from '~/components/user/FromCreate.vue'
import FormDelete from '~/components/user/FormDelete.vue'

export default Vue.extend({
  components: {
    FormDelete,
    FormCreate,
    UserList
  },
  layout: 'users',

  middleware: ['check-auth', 'auth'],

  data() {
    return {
      users: {
        items: [] as UserItem[],
        count: 0
      },
      selected: [] as UserItem[],
      dialogCreate: false,
      dialogDelete: false,
      isLoading: false,
      successMessage: ''
    }
  },

  async fetch() {
    this.isLoading = true
    try {
      const result = await this.$services.user.listAll()
      console.log('Utilizadores recebidos:', result)
      this.users = {
        items: result,
        count: result.length
      }
    } catch (error) {
      console.error('Erro ao obter utilizadores:', error)
    }
    this.isLoading = false
  },

  computed: {
    ...mapGetters('auth', ['isStaff']),
    canDelete(): boolean {
      return this.selected.length > 0
    },
  },

  watch: {
    '$route.query': _.debounce(function () {
      // @ts-ignore
      this.$fetch()
    }, 1000)
  },

  methods: {
    updateQuery(query: object) {
      this.$router.push(query)
    },
    debugClick() {
      console.log('Cliquei no botão!')
    },

    async handleCreateSuccess() {
      this.dialogCreate = false
      this.successMessage = this.$t('User created successfully') as string
      await this.$fetch()
    },

    async remove() {
      await this.$services.user.bulkDelete(this.selected)
      this.$fetch()
      this.dialogDelete = false
      this.selected = []
    },

  }
})
</script>

<style scoped>
::v-deep .v-dialog {
  width: 800px;
}
</style>
