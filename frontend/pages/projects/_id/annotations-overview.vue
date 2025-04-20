<template>
   <v-container>
     <v-card class="pa-4">
       <v-card-title>Comparar Anotações de Texto</v-card-title>
       <v-card-text>
         <v-select
           v-model="exampleId"
           :items="examples"
           item-value="id"
           item-text="text"
           label="Escolher Exemplo"
           outlined
           dense
           class="mb-4"
           :loading="loadingExamples"
           :disabled="loadingExamples"
           return-object
         />

         <v-btn
           color="primary"
           @click="fetchAnnotations"
           :loading="loading || !exampleId"
           :disabled="!exampleId"
         >
           Ver Anotações
         </v-btn>

         <v-divider class="my-4" />

         <div v-if="annotations">
           <p><strong>Texto:</strong> {{ annotations.text }}</p>
           <v-list>
             <v-list-item
               v-for="(annotation, index) in annotations.annotations"
               :key="index"
             >
               <v-list-item-content>
                 <v-chip color="primary" class="ma-1" text-color="white">
                   {{ annotation.user }}
                 </v-chip>
                 <v-chip color="indigo" class="ma-1" text-color="white">
                   {{ annotation.label }}
                 </v-chip>
               </v-list-item-content>
             </v-list-item>
           </v-list>
         </div>

         <v-alert v-else-if="hasSearched && !loading" type="info" class="mt-4">
           Nenhuma anotação encontrada para este exemplo.
         </v-alert>
       </v-card-text>
     </v-card>
   </v-container>
 </template>

 <script>
 import { ref, computed, useContext, onMounted } from "@nuxtjs/composition-api";
 import ApiService from "@/services/api.service";

 export default {
   layout: "project",
   middleware: ["check-auth", "auth", "setCurrentProject"],

   setup() {
     const { route } = useContext();
     const projectId = computed(() => route.value.params.id);

     const exampleId = ref(null);
     const examples = ref([]);
     const loadingExamples = ref(false);

     const annotations = ref(null);
     const loading = ref(false);
     const hasSearched = ref(false);

     const fetchExamples = async () => {
       loadingExamples.value = true;
       try {
         const response = await ApiService.get(`/projects/${projectId.value}/examples?limit=1000`);
         examples.value = response.data.results;
       } catch (e) {
         console.error("Erro ao obter exemplos:", e);
       } finally {
         loadingExamples.value = false;
       }
     };

     const fetchAnnotations = async () => {
       if (!exampleId.value) return;
       loading.value = true;
       hasSearched.value = true;
       annotations.value = null;

       try {
         const response = await ApiService.get(
             `/projects/${projectId.value}/examples/${exampleId.value.id}/annotations`
         );
         annotations.value = response.data;
       } catch (e) {
         console.error("Erro ao obter anotações:", e);
       } finally {
         loading.value = false;
       }
     };

     onMounted(fetchExamples);

     return {
       projectId,
       exampleId,
       examples,
       loadingExamples,
       annotations,
       fetchAnnotations,
       loading,
       hasSearched,
     };
   },
 };
 </script>