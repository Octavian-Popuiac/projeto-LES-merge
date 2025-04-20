<template>
  <v-container class="mt-10 pt-10">
    <v-card>
      <v-card-title>
        <h1 class="text-h4">Grupos</h1>
        <v-spacer></v-spacer>
        <v-btn 
          color="primary" 
          @click="openCreateDialog()"
        >
          <v-icon left>{{ mdiPlus }}</v-icon>
          Criar Novo Grupo
        </v-btn>
      </v-card-title>
      <v-divider></v-divider>
      
      <v-card-text>
        <v-data-table
          :headers="headers"
          :items="groups"
          :loading="loading"
          sort-by="name"
          class="elevation-1"
        >
          <template #[`item.actions`]="{ item }">
            <v-btn color="primary" icon small @click="viewGroup(item)">
              <v-icon small>{{ mdiEye }}</v-icon>
            </v-btn>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <!-- Diálogo de criação de grupo -->
    <v-dialog v-model="dialog" max-width="800px" persistent>
      <v-card>
        <v-card-title class="headline primary white--text">
          Criar Novo Grupo
          <v-spacer></v-spacer>
          <v-btn icon dark @click="closeDialog">
            <v-icon>{{ mdiClose }}</v-icon>
          </v-btn>
        </v-card-title>
        
        <v-form ref="form" v-model="valid" lazy-validation @submit.prevent="saveGroup">
          <v-card-text class="pt-4">
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="editedItem.name"
                  label="Nome do Grupo"
                  :rules="nameRules"
                  outlined
                  required
                  autofocus
                  :loading="checkingName"
                  :error-messages="nameError"
                  @input="checkDuplicateName"
                ></v-text-field>
              </v-col>
            </v-row>
            
            <v-row>
              <v-col cols="12">
                <v-textarea
                  v-model="editedItem.description"
                  label="Descrição"
                  outlined
                  rows="3"
                  :rules="descriptionRules"
                  hint="Resumir as permissões do grupo (máximo 20 caracteres)"
                  persistent-hint
                  counter="20"
                >
                </v-textarea>
              </v-col>
            </v-row>

            
            <!-- Seleção de Membros -->
            <v-row>
              <v-col cols="12">
                <v-autocomplete
                  v-model="selectedMembers"
                  :items="availableUsers"
                  item-text="username"
                  item-value="id"
                  label="Selecionar Membros (opcional)"
                  multiple
                  chips
                  small-chips
                  outlined
                  :loading="loadingUsers"
                >
                  <template #selection="{ item, index }">
                    <v-chip v-if="index < 3" small>
                      {{ item.username || item.email || `Usuário ${item.id}` }}
                    </v-chip>
                    <span v-if="index === 3" class="grey--text text-caption">
                      (+{{ selectedMembers.length - 3 }} mais)
                    </span>
                  </template>
                </v-autocomplete>
              </v-col>
            </v-row>
            
            <!-- Seleção de Permissões -->
            <v-row>
              <v-col cols="12">
                <v-autocomplete
                  v-model="selectedPermissions"
                  :items="availablePermissions"
                  item-text="name"
                  item-value="id"
                  label="Selecionar Permissões (opcional)"
                  multiple
                  chips
                  small-chips
                  outlined
                  :loading="loadingPermissions"
                >
                  <template #item="{ item }">
                    <v-list-item-content>
                      <v-list-item-title>{{ item.name }}</v-list-item-title>
                      <v-list-item-subtitle>{{ item.codename }}</v-list-item-subtitle>
                    </v-list-item-content>
                  </template>
                </v-autocomplete>
              </v-col>
            </v-row>
          </v-card-text>
          
          <v-divider></v-divider>
          
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn text @click="closeDialog">Cancelar</v-btn>
            <v-btn 
              color="primary" 
              :loading="saving" 
              type="submit"
            >
              Salvar
            </v-btn>
          </v-card-actions>
        </v-form>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import { mdiPlus, mdiEye, mdiPencil, mdiClose } from '@mdi/js'
import { debounce } from 'lodash'

export default {
  name: 'GroupsIndex',
  middleware: ['check-auth','auth', 'staff-only'],
  
  data() {
    return {
      mdiPlus,
      mdiEye,
      mdiPencil,
      mdiClose,
      loading: false,
      saving: false,
      dialog: false,
      valid: true,
      nameError: '',
      checkingName: false,
      loadingUsers: false,
      loadingPermissions: false,
      groups: [],
      headers: [
        { text: 'Nome', value: 'name' },
        { text: 'Descrição', value: 'description' },
        { text: 'Criado por', value: 'created_by' },
        { text: 'Membros', value: 'member_count' },
        { text: 'Ações', value: 'actions', sortable: false }
      ],
      nameRules: [
        v => !!v || 'Nome é obrigatório',
        v => (v && v.length >= 3) || 'Nome deve ter pelo menos 3 caracteres'
      ],
      descriptionRules: [
        v => !v || v.length <= 20 || 'Máximo de 20 caracteres permitido'
      ],
      editedItem: {
        name: '',
        description: ''
      },
      defaultItem: {
        name: '',
        description: ''
      },
      availableUsers: [],
      selectedMembers: [],
      availablePermissions: [],
      selectedPermissions: [],
    }
  },
  async fetch() {
    this.loading = true
    try {
      const response = await this.$services.group.getGroups() // Corrigido para "groups" (plural)
      console.log('Resposta da API:', response)
      
      // Lógica melhorada para processar a resposta
      if (Array.isArray(response)) {
        this.groups = response
      } else if (response && Array.isArray(response.results)) {
        this.groups = response.results
      } else if (response && Array.isArray(response.data)) {
        this.groups = response.data
      } else {
        console.log('Formato de resposta não reconhecido:', response)
        const possibleArrays = Object.values(response || {}).filter(val => Array.isArray(val))
        if (possibleArrays.length > 0) {
          this.groups = possibleArrays[0]
        } else {
          this.groups = []
        }
      }
    } catch (error) {
      console.error('Erro ao carregar grupos:', error)
      this.groups = []
    } finally {
      this.loading = false
    }
  },

  created() {
    // Cria uma versão "debounced" da função para evitar muitas chamadas
    this.checkDuplicateName = debounce(this.checkDuplicateName, 500)
  },

  methods: {
    // Função para visualizar detalhes de um grupo
    viewGroup(group) {
      console.log('Visualizando grupo:', group)
      this.$router.push(`/groups/${group.id}`)
    },
    
    // Função para abrir diálogo de criação (implementação futura)
    // Abre dialogo
    openCreateDialog() {
      this.editedItem = Object.assign({}, this.defaultItem)
      this.selectedMembers = []
      this.selectedPermissions = []
      this.nameError = ''
      this.dialog = true
      
      this.$nextTick(() => {
    if (this.$refs.form) {
      this.$refs.form.resetValidation()
      // Quando o próximo ciclo de renderização terminar, validar o formulário
      this.$nextTick(() => {
        // Iniciar com um formulário válido
        this.valid = true
      })
    }
  })

      this.loadUsers()
      this.loadPermissions()
    },
    // Carrega utilizadores disponíveis
    async loadUsers() {
      this.loadingUsers = true
      try {
        // Verifique se o serviço de usuários existe e o método correto
        const users = await this.$services.user.listAll()
        if (Array.isArray(users)) {
          this.availableUsers = users
        } else {
          // Dados fictícios para teste
          this.availableUsers = [
            { id: 1, username: 'admin', email: 'admin@example.com' },
            { id: 2, username: 'user1', email: 'user1@example.com' },
            { id: 3, username: 'user2', email: 'user2@example.com' }
          ]
          console.warn('Usando dados fictícios para usuários. Implemente o serviço users.getUsers()')
        }
      } catch (error) {
        console.error('Erro ao carregar usuários:', error)
        this.availableUsers = []
      } finally {
        this.loadingUsers = false
      }
    },
    // Carrega a lista de permissões disponíveis
    async loadPermissions() {
      this.loadingPermissions = true
      try {
        const permissions = await this.$services.group.getAllPermissions()
        this.availablePermissions = permissions
      } catch (error) {
        console.error('Erro ao carregar permissões:', error)
        // Dados fictícios para teste
        this.availablePermissions = [
          { id: 1, name: 'Visualizar usuários', codename: 'view_user' },
          { id: 2, name: 'Editar usuários', codename: 'edit_user' },
          { id: 3, name: 'Excluir usuários', codename: 'delete_user' }
        ]
      } finally {
        this.loadingPermissions = false
      }
    },
    // Verifica se o nome do grupo já existe
    async checkDuplicateName() {
      const name = this.editedItem.name
      
      // Limpar erro existente
      this.nameError = ''
      console.log('Verificando nome:', name)
      
      // Verificar se há algo para checar
      if (!name || name.length < 3){
        console.log('Nome muito curto, ignorando verificação');
        return;
      }
      
      this.checkingName = true
      
      try {
        // Verificar nos grupos locais primeiro
        const duplicate = this.groups.find(g => 
          g.name.toLowerCase() === name.toLowerCase()
        );
        
        if (duplicate) {
          console.log('Nome duplicado encontrado localmente:', duplicate.name);
          this.nameError = 'Este nome de grupo já existe';
          return;
        }
        
        // Verificar no servidor
        console.log('Verificando no servidor...');
        const exists = await this.$services.group.checkGroupNameExists(name);
        console.log('Resposta do servidor:', exists);
        
        if (exists) {
          this.nameError = 'Este nome de grupo já existe';
        }
      } catch (error) {
        console.error('Erro ao verificar nome de grupo:', error);
      } finally {
        this.checkingName = false;
      }
    },
    // Contar palavras em um texto
    countLetters(text) {
      if (!text) return 0;
      return text.length; // Simplesmente retorna o comprimento da string
    },
    // Fecha dialogo
    closeDialog() {
      this.dialog = false
      this.$nextTick(() => {
        this.editedItem = Object.assign({}, this.defaultItem)
        this.selectedMembers = []
        this.selectedPermissions = []
        this.nameError = ''
      })
    },
    // Salva novo grupo
    async saveGroup(){
      console.log('saveGroup chamado');
      
      // Validar formulário manualmente
      const isFormValid = this.$refs.form.validate();
      console.log('Resultado da validação do formulário:', isFormValid);
      
      if (!isFormValid) {
        console.log('Formulário inválido, abortando salvamento');
        return;
      }
      
      if (this.nameError) {
        console.log('Erro no nome, abortando salvamento:', this.nameError);
        return;
      }
      
      // Verificar explicitamente o tamanho da descrição
      const description = this.editedItem.description || ''
      const charCount = description.length
      console.log('Número de palavras na descrição:', charCount)
      
      if (charCount > 20) {
        console.error(`Descrição excede limite: ${wordCount} caracteres`);
        alert(`A descrição possui ${wordCount} palavras, mas o limite é 20 caracteres.`);
        return;
      }

      this.saving = true;
      try {
        console.log('Enviando dados para criação:', {
          name: this.editedItem.name,
          description: this.editedItem.description
        });
        
        const newGroup = await this.$services.group.createGroup(
          this.editedItem.name,
          this.editedItem.description
        );
        
        console.log('Grupo criado com sucesso:', newGroup);



        // Processar membros (se selecionados)
        if (this.selectedMembers.length > 0) {
          try {
            await this.$services.group.addUsersToGroup(
              newGroup.id, 
              this.selectedMembers
            );
            this.$set(newGroup, 'member_count', this.selectedMembers.length);
            console.log('Membros adicionados:', this.selectedMembers.length);
            console.log('Grupo atualizado:', newGroup);
          } catch (memberError) {
            console.error('Erro ao adicionar membros:', memberError);
          }
        }

        this.$nextTick(() => {
          // Adicionar uma cópia do objeto para evitar problemas de referência
          this.groups.push({...newGroup});
          
          // Forçar atualização da tabela
          this.$forceUpdate();
          
          console.log('Grupo adicionado à lista, membros:', newGroup.member_count);
        });

        // Processar permissões (se selecionadas)
        if (this.selectedPermissions.length > 0) {
          try {
            await this.$services.group.updateGroupPermissions(
              newGroup.id, 
              this.selectedPermissions
            );
          } catch (permError) {
            console.error('Erro ao atualizar permissões:', permError);
          }
        }


        this.closeDialog()
      } catch(error) {
        console.error('Erro ao criar grupo:', error);
        
        // Mostrar mensagem de erro detalhada
        const errorMessage = error.response && error.response.data 
          ? `Erro: ${JSON.stringify(error.response.data)}`
          : 'Erro ao criar grupo';
          
        if (this.$store.hasModule('notification')) {
          this.$store.dispatch('notification/add', {
            type: 'error',
            message: errorMessage
          });
        } else {
          alert(errorMessage);
        }
      } finally {
        this.saving = false;
      }
    }
  }
}
</script>