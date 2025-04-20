<template>
  <base-card
    :title="$t('Criar Utilizador')"
    :agree-text="$t('generic.create')"
    :cancel-text="$t('generic.cancel')"
    @agree="onCreate"
    @cancel="$emit('cancel')"
  >
    <template #content>
      <v-alert
        v-if="errors.length"
        type="error"
        dense
        outlined
        class="mb-4"
        dismissible
        @input="errors = []"
      >
        <ul class="ma-0 pa-0">
          <li v-for="(error, index) in errors" :key="index">{{ error }}</li>
        </ul>
      </v-alert>

      <v-form ref="form" v-model="valid">
        <v-text-field
          v-model="user.username"
          :label="$t('generic.username')"
          :rules="[required]"
          required
        />

        <v-text-field
          v-model="user.first_name"
          :label="$t('generic.firstname')"
          :rules="[required]"
          required
        />

        <v-text-field
          v-model="user.last_name"
          :label="$t('generic.lastname')"
          :rules="[required]"
          required
        />

        <v-text-field
          v-model="user.password1"
          :label="$t('Password')"
          type="password"
          :rules="[required]"
          required
        />

        <v-text-field
          v-model="user.password2"
          :label="$t('ConfirmPassword')"
          type="password"
          :rules="[required, confirmPasswordRule]"
          required
        />

        <v-text-field
          v-model="user.email"
          :label="$t('Email')"
          type="email"
          :rules="[required, confirmEmail]"
          required
        />


      </v-form>
    </template>

  </base-card>
</template>

<script lang="ts">
import Vue from 'vue'
import BaseCard from '@/components/utils/BaseCard.vue'

export default Vue.extend({
  components: {
    BaseCard
  },

  data() {
    return {
      valid: false,
      user: {
        username: '',
        first_name: '',
        last_name: '',
        password1: '',
        password2: '',
        email: ''
      },
      errors: [] as string[] // <- Novo array de mensagens de erro
    }
  },

  methods: {
    required(value: string) {
      return !!value || this.$t('Field required')
    },

    confirmPasswordRule(value: string) {
      return value === this.user.password1 || 'Passwords do not match.'
    },

    confirmEmail(value: string) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return emailRegex.test(value) || this.$t('Invalid email address')
    },


    async onCreate() {
      if (!this.valid) return
      try {
        await this.$services.user.create({
          username: this.user.username,
          first_name: this.user.first_name,
          last_name: this.user.last_name,
          password1: this.user.password1,
          password2: this.user.password2,
          email: this.user.email
        })
        this.$emit('create') // comunica ao pai que foi criado com sucesso
      } catch (e) {
        const errorData = e.response?.data || { detail: 'Erro desconhecido.' }
        this.errors = []

        for (const key in errorData) {
          const value = errorData[key]
          if (Array.isArray(value)) {
            this.errors.push(...value)
          } else {
            this.errors.push(String(value))
          }
        }

        this.$emit('error', errorData)
      }


    }
  }
})
</script>
