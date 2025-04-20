<template>
  <base-card
    :title="$t('user.deleteUserTitle')"
    :agree-text="$t('generic.yes')"
    :cancel-text="$t('generic.cancel')"
    @agree="attemptRemove"
    @cancel="$emit('cancel')"
  >
    <template #content>
      {{ $t('user.deleteUserMessage') }}
      <v-list dense>
        <v-list-item v-for="(item, i) in selected" :key="i">
          <v-list-item-content>
            <v-list-item-title>{{ item.username }}</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
    </template>
  </base-card>
</template>

<script lang="ts">
import {mapGetters} from 'vuex'
import type { PropType } from 'vue'
import Vue from 'vue'
import BaseCard from '@/components/utils/BaseCard.vue'
import { UserItem } from '~/domain/models/user/user'


export default Vue.extend({
  components: {
    BaseCard
  },

  props: {
    selected: {
      type: Array as PropType<UserItem[]>,
      default: () => []
    }
  },

  data() {
    return {
      errorMessage: ''
    };
  },

  computed: {
    ...mapGetters('auth', ['getUserId']),
  },

  methods: {
    attemptRemove(){
      if(this.selected.some(user => user.id === this.getUserId)){
        this.errorMessage = "You can't delete yourself!";
      }
      else{
        this.errorMessage = '';
        this.$emit('remove');
      }
    }
  }

})
</script>

<style scoped>
.error-message {
  color: red;
  font-size: 1.2em;
  font-weight: bold;
}
</style>