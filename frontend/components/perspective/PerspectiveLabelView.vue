<template>
    <v-card class="mt-4" outlined>
      <v-card-title>Label Perspectives</v-card-title>
      <v-divider />
      <v-card-text>
        <v-list v-if="perspectives.length">
          <v-list-item v-for="(perspective, index) in perspectives" :key="index">
            <v-list-item-content>
              <v-chip class="ma-1" color="primary">
                {{ perspective.label }} - {{ perspective.user }}
              </v-chip>
              <v-list dense>
                <v-list-item-group v-for="(qa, i) in perspective.question_answers" :key="i">
                  <v-list-item>
                    <v-list-item-content>
                      <v-list-item-title>{{ qa.question }}</v-list-item-title>
                      <v-list-item-subtitle>{{ qa.answer }}</v-list-item-subtitle>
                    </v-list-item-content>
                  </v-list-item>
                </v-list-item-group>
              </v-list>
            </v-list-item-content>
          </v-list-item>
        </v-list>
      </v-card-text>
    </v-card>
  </template>
  
  <script>
  import { ref, watch, onMounted } from '@nuxtjs/composition-api'
  import { APIPerspectiveRepository } from '@/repositories/perspective/apiPerspectiveRepository'
  
  export default {
    props: {
      projectId: {
        type: String,
        required: true,
      },
      exampleId: {
        type: Number,
        required: true,
      },
    },
  
    setup(props) {
      const perspectives = ref([])
  
      const repository = new APIPerspectiveRepository()
  
      const fetchLabelPerspectives = async () => {
        if (!props.projectId) return
        try {
          const rawPerspectives = await repository.getLabelPerspectives(
            Number(props.projectId), 
            props.exampleId
        )
  
          perspectives.value = rawPerspectives.map((item) => ({
            label: item.label,
            user: item.user,
            question_answers: item.question_answers
          }))
        } catch (error) {
          console.error('Error fetching label perspectives:', error)
        }
      }
  
      onMounted(fetchLabelPerspectives)
  
      watch(() => props.exampleId, fetchLabelPerspectives)
  
      return {
        perspectives,
      }
    },
  }
  </script>