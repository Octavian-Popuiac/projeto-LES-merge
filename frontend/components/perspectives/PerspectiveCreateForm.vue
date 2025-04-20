<template>
  <v-container>
    <v-card class="pa-4">
      <v-card-title>
        {{ perspectiveExists ? 'Perspetiva do Projeto' : 'Criar Perspetiva' }}
        <v-spacer />
        <v-btn
          v-if="perspectiveExists"
          color="error"
          small
          @click="deleteProjectPerspective"
        >
          Eliminar Perspetiva
        </v-btn>
      </v-card-title>

      <v-card-subtitle>
        {{
          perspectiveExists
            ? 'Perguntas definidas pelo admin para este projeto. Responde abaixo.'
            : 'Define aqui as perguntas que queres que os anotadores respondam.'
        }}
      </v-card-subtitle>

      <v-card-text v-if="!perspectiveExists">
        <v-alert v-if="questions.length === 0" type="info">
          Adiciona pelo menos uma pergunta à perspetiva.
        </v-alert>

        <v-text-field
          v-for="(q, index) in questions"
          :key="index"
          v-model="questions[index]"
          class="mb-3"
          dense
          outlined
          :placeholder="'Pergunta #' + (index + 1)"
          label="Texto da Pergunta"
        />

        <v-btn small color="primary" @click="addQuestion">
          Adicionar Pergunta
        </v-btn>
      </v-card-text>

      <v-card-text v-else>
        <v-text-field
          v-for="(q, index) in answeredQuestions"
          :key="index"
          v-model="answeredQuestions[index].answer"
          class="mb-3"
          dense
          outlined
          :label="q.question"
          :readonly="hasAnswered"
        />
        <v-alert v-if="hasAnswered" type="success" class="mt-2">
          Já respondeste a esta perspetiva.
        </v-alert>
      </v-card-text>

      <v-divider class="my-4" />

      <v-card-actions v-if="!perspectiveExists">
        <v-btn
          color="success"
          :disabled="questions.length === 0"
          :loading="loading"
          @click="submit"
        >
          Criar Perspetiva
        </v-btn>
      </v-card-actions>

      <v-card-actions v-else-if="!hasAnswered">
        <v-btn color="success" :loading="loading" @click="submitAnswers">
          Submeter Respostas
        </v-btn>
      </v-card-actions>
    </v-card>

    <v-card v-if="perspectiveExists && memberData.length" class="pa-4 mt-6">
      <v-card-title>Perspetivas dos Membros</v-card-title>
      <v-card-text>
        <v-expansion-panels accordion>
          <v-expansion-panel
            v-for="(member, index) in memberData"
            :key="index"
          >
            <v-expansion-panel-header>
              {{ member.user }} — {{ member.labels.length }} label(s)
              <v-spacer />
              <v-menu offset-y>
                <template #activator="{ on, attrs }">
                  <v-btn icon v-bind="attrs" v-on="on"> Opções
                    <v-icon>mdi-dots-vertical</v-icon>
                  </v-btn>
                </template>
                <v-list>
                  <v-list-item @click="deleteUserPerspective(member.user_id)">
                    <v-list-item-title>Eliminar Perspetiva do Utilizador</v-list-item-title>
                  </v-list-item>
                </v-list>
              </v-menu>
            </v-expansion-panel-header>

            <v-expansion-panel-content>
              <h4 class="subtitle-2 mb-2">Respostas à perspetiva:</h4>
              <v-list dense>
                <v-list-item
                  v-for="(qa, i) in member.question_answers"
                  :key="i"
                >
                  <v-list-item-content>
                    <strong>{{ qa.question }}</strong>: {{ qa.answer }}
                  </v-list-item-content>
                </v-list-item>
              </v-list>

              <h4 class="subtitle-2 mt-4 mb-2">Labels anotadas:</h4>
              <v-chip-group column>
                <v-chip
                  v-for="(label, i) in member.labels"
                  :key="i"
                  class="ma-1"
                  color="primary"
                  text-color="white"
                  small
                >
                  {{ label }}
                </v-chip>
              </v-chip-group>
            </v-expansion-panel-content>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script>
import ApiService from '@/services/api.service'

export default {
  props: {
    projectId: {
      type: [String, Number],
      required: true
    }
  },

  data() {
    return {
      questions: [],
      memberData: [],
      perspectiveExists: false,
      perspectiveId: null,
      answeredQuestions: [],
      hasAnswered: false,
      loading: false
    }
  },

  async mounted() {
    await this.fetchPerspective()
    if (this.perspectiveExists) {
      this.fetchMemberData()
    }
  },

  methods: {
    addQuestion() {
      this.questions.push('')
    },

    async fetchPerspective() {
      try {
        const res = await ApiService.get(`/perspectives/projects/${this.projectId}/`)
        this.perspectiveExists = true
        this.perspectiveId = res.data.id
        this.answeredQuestions = res.data.questions.map((q) => ({
          question_id: q.id,
          question: q.question.question_text,
          answer: ''
        }))
      } catch (e) {
        this.perspectiveExists = false
      }
    },

    async fetchMemberData() {
      try {
        const res = await ApiService.get(`/perspectives/projects/${this.projectId}/member-data/`)
        this.memberData = res.data
      } catch (err) {
        console.error('Erro ao buscar dados dos membros:', err)
      }
    },

    async submit() {
      this.loading = true
      try {
        const payload = {
          project: parseInt(this.projectId),
          questions: this.questions.map((q) => ({
            question: { question_text: q }
          }))
        }

        await ApiService.post('/perspectives/create/', payload)
        await this.fetchPerspective()  // atualiza o estado da página
        await this.fetchMemberData()
      } catch (err) {
        console.error('Erro ao criar perspetiva:', err)
        alert('Erro ao criar perspetiva.')
      } finally {
        this.loading = false
      }
    },

    async submitAnswers() {
      this.loading = true
      try {
        const payload = {
          perspective: this.perspectiveId,
          answers: this.answeredQuestions.map((q) => ({
            question_id: q.question_id,
            value: q.answer
          }))
        }

        await ApiService.post('/perspectives/answers/submit/', payload)
        this.hasAnswered = true
        await this.fetchMemberData()
      } catch (err) {
        console.error('Erro ao submeter respostas:', err)
        alert('Erro ao submeter respostas.')
      } finally {
        this.loading = false
      }
    },

    async deleteProjectPerspective() {
      if (!confirm("Tens a certeza que queres eliminar a perspetiva deste projeto?")) return
      try {
        await ApiService.delete(`/perspectives/projects/${this.projectId}/delete/`)
        this.perspectiveExists = false
        this.memberData = []
        this.questions = []
      } catch (err) {
        console.error("Erro ao eliminar perspetiva do projeto:", err)
        alert("Erro ao eliminar perspetiva.")
      }
    },

    async deleteUserPerspective(userId) {
      console.log("userId recebido:", userId);
      if (!confirm("Eliminar perspetiva deste utilizador?")) return
      try {
        await ApiService.delete(`/perspectives/projects/${this.projectId}/users/${userId}/delete/`)
        await this.fetchMemberData()
      } catch (err) {
        console.error("Erro ao eliminar perspetiva do utilizador:", err)
        alert("Erro ao eliminar perspetiva do utilizador.")
      }
    }
  }
}
</script>
