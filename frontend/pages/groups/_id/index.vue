<template>
  <div class="group-details-page">
    <!-- Header com banner e ações principais -->
    <v-card class="group-header mb-6">
      <div class="group-banner" :style="bannerStyle">
        <div class="banner-overlay">
          <v-container>
            <div class="d-flex justify-space-between align-center">
              <div>
                <h1 class="white--text text-h3 font-weight-bold">
                  {{ group.name || 'Carregando...' }}
                </h1>
                <div class="white--text text-subtitle-1 mt-2">
                  <span>Criado por {{ group.created_by || 'Desconhecido' }}</span>
                  <span class="mx-2">•</span>
                  <span>{{ groupMembers.length }} membros</span>
                </div>
              </div>
              <div>
                <v-speed-dial
                  v-model="fab"
                  direction="left"
                  transition="slide-x-reverse-transition"
                >
                  <template #activator>
                    <v-btn
                      fab
                      large
                      color="primary"
                      dark
                    >
                      <v-icon v-if="fab">{{mdiClose}}</v-icon>
                      <v-icon v-else>{{mdiDotsVertical}}</v-icon>
                    </v-btn>
                  </template>
                  
                  <v-btn
                    fab
                    color="error"
                    dark
                    @click="confirmDelete = true"
                  >
                    <v-icon>{{mdiDelete}}</v-icon>
                  </v-btn>
                  
                  <v-btn
                    fab
                    color="indigo"
                    dark
                    @click="editMode = true"
                  >
                    <v-icon>{{mdiPencil}}</v-icon>
                  </v-btn>
                </v-speed-dial>
              </div>
            </div>
          </v-container>
        </div>
      </div>
    </v-card>

    <v-container>
      <!-- Mostrar notificação de carregamento -->
      <v-skeleton-loader
        v-if="loading"
        type="card, list-item-three-line, actions"
      ></v-skeleton-loader>

      <template v-else>
        <!-- Seção de visão geral -->
        <v-card class="mb-6 overflow-hidden">
          <v-card-title class="primary--text">
            <v-icon left color="primary">{{mdiInformationOutline}}</v-icon>
            Visão Geral
          </v-card-title>
          
          <v-divider></v-divider>
          
          <v-card-text class="py-4">
            <template v-if="!editMode">
              <p class="text-body-1">{{ group.description || 'Sem descrição' }}</p>
              <v-chip-group class="mt-4">
                <v-chip 
                  v-for="(permission, i) in permissions.slice(0, 5)" 
                  :key="i"
                  color="primary"
                  small
                  outlined
                >
                  {{ permission.name }}
                </v-chip>
                <v-chip
                  v-if="permissions.length > 5"
                  color="grey"
                  small
                >
                  +{{ permissions.length - 5 }} mais
                </v-chip>
              </v-chip-group>
            </template>
            
            <v-form v-else ref="form" v-model="valid">
              <v-text-field
                v-model="editedGroup.name"
                label="Nome do Grupo"
                :rules="[v => !!v || 'Nome é obrigatório']"
                outlined
                dense
              ></v-text-field>
              
              <v-textarea
                v-model="editedGroup.description"
                label="Descrição"
                outlined
                auto-grow
                rows="3"
                :rules="[v => !v ||
                v.length <= 20 || 
                'A descrição deve ter no máximo 20 caracteres']"
                :counter="20"
              ></v-textarea>
              
              <div class="d-flex justify-end mt-3">
                <v-btn
                  text
                  color="grey"
                  @click="cancelEdit"
                >
                  Cancelar
                </v-btn>
                <v-btn
                  color="primary"
                  class="ml-2"
                  :disabled="!valid || isSaving"
                  :loading="isSaving"
                  @click="saveGroupDetails"
                >
                  Salvar
                </v-btn>
              </div>
            </v-form>
          </v-card-text>
        </v-card>

        <!-- Seção de Membros e Permissões -->
        <v-card class="mb-6">
          <v-tabs
            v-model="activeTab"
            background-color="primary"
            dark
            grow
          >
            <v-tab>
              <v-icon left>{{mdiAccountGroup}}</v-icon>
              Membros
            </v-tab>
            <v-tab>
              <v-icon left>{{mdiShieldKey}}</v-icon>
              Permissões
            </v-tab>
          </v-tabs>

          <v-tabs-items v-model="activeTab">
            <!-- Aba de Membros -->
            <v-tab-item>
              <v-card flat>
                <v-card-title>
                  <v-text-field
                    v-model="memberSearch"
                    :append-icon="mdiMagnify"
                    label="Procurar membros"
                    single-line
                    hide-details
                    class="mr-4"
                  ></v-text-field>
                  <v-spacer></v-spacer>
                  <v-btn
                    color="primary"
                    @click="openMemberDialog"
                  >
                    <v-icon left>{{mdiPlus}}</v-icon>
                    Gerenciar Membros
                  </v-btn>
                </v-card-title>
                
                <v-data-table
                  :headers="memberHeaders"
                  :items="filteredMembers"
                  :loading="loading"
                  :items-per-page="10"
                  sort-by="username"
                  class="elevation-0"
                >
                  <template #[`item.avatar`]="{ item }">
                    <v-avatar color="primary" size="36">
                      <span class="white--text">{{ getInitials(item.username) }}</span>
                    </v-avatar>
                  </template>
                  
                  <template #no-data>
                    <div class="pa-6 text-center">
                      <v-icon 
                        color="grey lighten-1" 
                        size="64"
                        class="mb-4"
                      >
                        {{mdiAccountGroupOutline}}
                      </v-icon>
                      <p class="text-subtitle-1 grey--text">Nenhum membro encontrado</p>
                      <v-btn
                        color="primary"
                        @click="openMemberDialog"
                      >
                        Adicionar Membros
                      </v-btn>
                    </div>
                  </template>
                </v-data-table>
              </v-card>
            </v-tab-item>
            
            <!-- Aba de Permissões -->
            <v-tab-item>
              <v-card flat>
                <v-card-title>
                  <v-text-field
                    v-model="permissionSearch"
                    :append-icon="mdiMagnify"
                    label="Procurar permissões"
                    single-line
                    hide-details
                    class="mr-4"
                  ></v-text-field>
                  <v-spacer></v-spacer>
                  <v-btn
                    color="primary"
                    @click="openPermissionDialog"
                  >
                    <v-icon left>{{mdiShieldEdit}}</v-icon>
                    Gerenciar Permissões
                  </v-btn>
                </v-card-title>
                
                <v-data-table
                  :headers="permissionHeaders"
                  :items="filteredPermissions"
                  :loading="loading"
                  :items-per-page="10"
                  sort-by="name"
                  class="elevation-0"
                >
                  <template #[`item.icon`]>
                    <v-icon color="primary">{{mdiShieldKey}}</v-icon>
                  </template>
                  
                  <template #no-data>
                    <div class="pa-6 text-center">
                      <v-icon 
                        color="grey lighten-1" 
                        size="64"
                        class="mb-4"
                      >
                        {{mdiShieldOutline}}
                      </v-icon>
                      <p class="text-subtitle-1 grey--text">Nenhuma permissão encontrada</p>
                      <v-btn
                        color="primary"
                        @click="openPermissionDialog"
                      >
                        Adicionar Permissões
                      </v-btn>
                    </div>
                  </template>
                </v-data-table>
              </v-card>
            </v-tab-item>
          </v-tabs-items>
        </v-card>
      </template>
    </v-container>

    <!-- Diálogo para gerenciar membros -->
    <v-dialog
      v-model="memberDialog"
      max-width="800px"
      scrollable  
    >
      <v-card>
        <v-card-title class="primary white--text">
          <v-icon left dark>{{mdiAccountGroup}}</v-icon>
          Gerenciar Membros
          <v-spacer></v-spacer>
          <v-btn icon dark @click="memberDialog = false">
            <v-icon>{{mdiClose}}</v-icon>
          </v-btn>
        </v-card-title>

        <v-card-text class="pt-5">
          <v-row>
            <!-- Coluna esquerda: Usuários disponíveis -->
            <v-col cols="12" md="5">
              <v-card outlined class="member-card">
                <v-card-title class="subtitle-1 grey lighten-3">
                  Usuários Disponíveis
                  <v-spacer></v-spacer>
                  <v-text-field
                    v-model="availableSearch"
                    :append-icon="mdiMagnify"
                    label="Procurar"
                    hide-details
                    dense
                    single-line
                    class="ml-2"
                    style="max-width: 150px"
                  ></v-text-field>
                </v-card-title>
                
                <v-list dense height="350px" class="overflow-y-auto">
                  <v-list-item-group
                    v-model="selectedAvailableUsers"
                    multiple
                  >
                    <v-list-item
                      v-for="user in filteredAvailableUsers"
                      :key="user.id"
                      :value="user"
                      @dblclick="addToGroup([user])"
                    >
                      <v-list-item-avatar>
                        <v-avatar color="primary" size="36">
                          <span class="white--text">{{ getInitials(user.username) }}</span>
                        </v-avatar>
                      </v-list-item-avatar>
                      
                      <v-list-item-content>
                        <v-list-item-title>{{ user.username }}</v-list-item-title>
                        <v-list-item-subtitle>{{ user.email || 'Sem email' }}</v-list-item-subtitle>
                      </v-list-item-content>
                    </v-list-item>
                  </v-list-item-group>
                </v-list>
              </v-card>
            </v-col>

            <!-- Coluna do meio: Botões de ação -->
            <v-col cols="12" md="2" class="d-flex flex-column justify-center align-center">
              <v-btn
                fab
                small
                color="primary"
                class="mb-5"
                :disabled="!selectedAvailableUsers.length"
                @click="addToGroup(selectedAvailableUsers)"
              >
                <v-icon>{{mdiArrowRightBold}}</v-icon>
              </v-btn>
              
              <v-btn
                fab
                small
                color="grey"
                :disabled="!selectedGroupUsers.length"
                @click="removeFromGroup(selectedGroupUsers)"
              >
                <v-icon>{{mdiArrowLeftBold}}</v-icon>
              </v-btn>
            </v-col>

            <!-- Coluna direita: Membros do grupo -->
            <v-col cols="12" md="5">
              <v-card outlined class="member-card">
                <v-card-title class="subtitle-1 grey lighten-3">
                  Membros do Grupo
                  <v-spacer></v-spacer>
                  <v-text-field
                    v-model="groupSearch"
                    :append-icon="mdiMagnify"
                    label="Procurar"
                    hide-details
                    dense
                    single-line
                    class="ml-2"
                    style="max-width: 150px"
                  ></v-text-field>
                </v-card-title>
                
                <v-list dense height="350px" class="overflow-y-auto">
                  <v-list-item-group
                    v-model="selectedGroupUsers"
                    multiple
                  >
                    <v-list-item
                      v-for="user in filteredGroupUsers"
                      :key="user.id"
                      :value="user"
                      @dblclick="removeFromGroup([user])"
                    >
                      <v-list-item-avatar>
                        <v-avatar color="primary" size="36">
                          <span class="white--text">{{ getInitials(user.username) }}</span>
                        </v-avatar>
                      </v-list-item-avatar>
                      
                      <v-list-item-content>
                        <v-list-item-title>{{ user.username }}</v-list-item-title>
                        <v-list-item-subtitle>{{ user.email || 'Sem email' }}</v-list-item-subtitle>
                      </v-list-item-content>
                    </v-list-item>
                  </v-list-item-group>
                </v-list>
              </v-card>
            </v-col>
          </v-row>
        </v-card-text>
        
        <v-divider></v-divider>
      </v-card>
    </v-dialog>

    <!-- Diálogo para gerenciar permissões -->
    <v-dialog
      v-model="permissionDialog"
      max-width="600px"
    >
      <v-card>
        <v-card-title class="primary white--text">
          <v-icon left dark>{{mdiShieldKey}}</v-icon>
          Gerenciar Permissões
          <v-spacer></v-spacer>
          <v-btn icon dark @click="permissionDialog = false">
            <v-icon>{{mdiClose}}</v-icon>
          </v-btn>
        </v-card-title>
        
        <v-card-text class="pt-5">
          <v-autocomplete
            v-model="selectedPermissions"
            :items="availablePermissions"
            :loading="loadingPermissions"
            item-text="name"
            item-value="id"
            chips
            label="Selecionar Permissões"
            multiple
            outlined
            return-object
          >
            <template #selection="{ item, attrs, selected, disabled }">
              <v-chip
                :key="JSON.stringify(item)"
                v-bind="attrs"
                :input-value="selected"
                :disabled="disabled"
                close
                @click:close="removePermission(item)"
              >
                <v-icon left small>{{mdiShieldKey}}</v-icon>
                {{ item.name }}
              </v-chip>
            </template>
            <template #item="{ item }">
              <v-list-item-avatar>
                <v-icon>{{mdiShieldKey}}</v-icon>
              </v-list-item-avatar>
              <v-list-item-content>
                <v-list-item-title>{{ item.name }}</v-list-item-title>
                <v-list-item-subtitle>{{ item.codename }}</v-list-item-subtitle>
              </v-list-item-content>
            </template>
          </v-autocomplete>
        </v-card-text>
        
        <v-divider></v-divider>
        
        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn
            text
            @click="permissionDialog = false"
          >
            Cancelar
          </v-btn>
          <v-btn
            color="primary"
            :loading="isSaving"
            @click="savePermissions"
          >
            Salvar Permissões
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Diálogo de Confirmação de Exclusão -->
    <v-dialog
      v-model="confirmDelete"
      max-width="500"
    >
      <v-card>
        <v-card-title class="error white--text">
          <v-icon left dark>{{mdiAlertCircle}}</v-icon>
          Confirmar Exclusão
        </v-card-title>
        
        <v-card-text class="pt-4">
          <p class="text-body-1">
            Você tem certeza que deseja excluir o grupo <strong>{{ group.name }}</strong>?
          </p>
          <p class="text-body-2 mt-2">
            Esta ação não pode ser desfeita e todos os dados associados a este grupo serão perdidos.
          </p>
        </v-card-text>
        
        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn
            text
            @click="confirmDelete = false"
          >
            Cancelar
          </v-btn>
          <v-btn
            color="error"
            :loading="isSaving"
            @click="deleteGroup"
          >
            Excluir Grupo
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>

import { mdiArrowRightBold, mdiArrowLeftBold, mdiShieldKey, mdiClose, mdiDotsVertical, mdiDelete, mdiPencil, mdiInformationOutline, mdiAccountGroup, mdiMagnify, mdiAccountGroupOutline, mdiShieldEdit, mdiShieldOutline, mdiAlertCircle, mdiPlus} from '@mdi/js'
export default {
  name: 'GroupDetailsPage',
  middleware: ['check-auth', 'auth', 'staff-only'],
  
  data() {
    return {
      // MDI icons
      mdiArrowLeftBold,
      mdiArrowRightBold,
      mdiShieldKey,
      mdiClose,
      mdiDotsVertical,
      mdiDelete,
      mdiPencil,
      mdiInformationOutline,
      mdiAccountGroup,
      mdiMagnify,
      mdiAccountGroupOutline,
      mdiShieldEdit,
      mdiShieldOutline,
      mdiAlertCircle,
      mdiPlus,

      // Dados principais
      group: {},
      groupMembers: [],
      originalMemberIds: [],
      permissions: [],
      availablePermissions: [],
      allUsers: [],
      
      // UI controls
      loading: true,
      isSaving: false,
      activeTab: 0,
      fab: false,
      editMode: false,
      confirmDelete: false,
      
      // Diálogos
      memberDialog: false,
      permissionDialog: false,
      loadingPermissions: false,
      
      // Pesquisa e filtragem
      memberSearch: '',
      permissionSearch: '',
      availableSearch: '',
      groupSearch: '',
      
      // Seleção de itens
      selectedAvailableUsers: [],
      selectedGroupUsers: [],
      selectedPermissions: [],
      
      // Form validation
      valid: true,
      editedGroup: {
        name: '',
        description: ''
      },
      
      // Headers para tabelas
      memberHeaders: [
        { text: '', value: 'avatar', sortable: false, width: '60px' },
        { text: 'Usuário', value: 'username' },
        { text: 'Email', value: 'email' },
      ],
      permissionHeaders: [
        { text: '', value: 'icon', sortable: false, width: '60px' },
        { text: 'Nome', value: 'name' },
        { text: 'Código', value: 'codename' }
      ],
      
      // Feedback
      snackbar: {
        show: false,
        text: '',
        color: 'success',
        timeout: 3000
      }
    }
  },
  
  async fetch() {
    try {
      this.loading = true
      await this.loadGroupData()
    } catch (error) {
      console.error('Erro ao carregar dados:', error)
      this.showMessage('Erro ao carregar dados do grupo', 'error')
    } finally {
      this.loading = false
    }
  },
  
  computed: {
    // Banner dinâmico baseado no nome do grupo
    bannerStyle() {
      const colors = ['#1976D2', '#4CAF50', '#FF9800', '#9C27B0', '#607D8B']
      const randomColor = colors[this.group.id % colors.length || 0]
      return {
        background: `linear-gradient(to right, ${randomColor}, ${this.darkenColor(randomColor)})`,
        height: '200px',
        position: 'relative'
      }
    },
    
    // Filtros para membros e permissões
    filteredMembers() {
      if (!this.memberSearch) return this.groupMembers
      
      const search = this.memberSearch.toLowerCase()
      return this.groupMembers.filter(member => 
        member.username.toLowerCase().includes(search) || 
        (member.email && member.email.toLowerCase().includes(search))
      )
    },
    
    filteredPermissions() {
      if (!this.permissionSearch) return this.permissions
      
      const search = this.permissionSearch.toLowerCase()
      return this.permissions.filter(permission => 
        permission.name.toLowerCase().includes(search) || 
        permission.codename.toLowerCase().includes(search)
      )
    },
    
    // Lista filtrada de usuários disponíveis
    filteredAvailableUsers() {
      const groupMemberIds = this.groupMembers.map(member => member.id)
      let available = this.allUsers.filter(user => !groupMemberIds.includes(user.id))
      
      if (this.availableSearch) {
        const search = this.availableSearch.toLowerCase()
        available = available.filter(user => 
          user.username.toLowerCase().includes(search) || 
          (user.email && user.email.toLowerCase().includes(search))
        )
      }
      
      return available
    },
    
    // Lista filtrada de usuários do grupo
    filteredGroupUsers() {
      if (!this.groupSearch) return this.groupMembers
      
      const search = this.groupSearch.toLowerCase()
      return this.groupMembers.filter(user => 
        user.username.toLowerCase().includes(search) || 
        (user.email && user.email.toLowerCase().includes(search))
      )
    },
    
    // Verifica se há alterações pendentes
    hasChanges() {
      const currentIds = this.groupMembers.map(user => user.id).sort()
      const originalIds = [...this.originalMemberIds].sort()
      
      if (currentIds.length !== originalIds.length) return true
      
      for (let i = 0; i < currentIds.length; i++) {
        if (currentIds[i] !== originalIds[i]) return true
      }
      
      return false
    }
  },
  
  methods: {
    // Carrega todos os dados do grupo
    async loadGroupData() {
      const groupId = this.$route.params.id
      
      try {
        // Carrega detalhes do grupo
        const group = await this.$services.group.getGroup(groupId)
        this.group = group
        this.editedGroup = {
          name: group.name,
          description: group.description
        }
        
        // Carrega membros do grupo
        if (group.users && Array.isArray(group.users)) {
          this.groupMembers = group.users
        } else {
          // const members = await this.$axios.$get(`/groups/${groupId}/users/`)
          const members = await this.$services.group.getGroupMembers(groupId)
          this.groupMembers = Array.isArray(members) ? members : []
        }
        this.originalMemberIds = this.groupMembers.map(user => user.id)
        
        // Carrega permissões
        // const permissions = await this.$axios.$get(`/groups/${groupId}/group_permissions/`)
        const permissions = await this.$services.group.getGroupPermissions(groupId)
        this.permissions = Array.isArray(permissions) ? permissions : []
        
        // Carrega todos os usuários
        const users = await this.$services.user.listAll()
        this.allUsers = Array.isArray(users) ? users : []
      } catch (error) {
        console.error('Erro ao carregar dados do grupo:', error)
        throw error
      }
    },
    
    // Abre o diálogo de membros
    openMemberDialog() {
      this.memberDialog = true
      this.selectedAvailableUsers = []
      this.selectedGroupUsers = []
    },
    
    // Abre o diálogo de permissões
    async openPermissionDialog() {
      this.permissionDialog = true
      this.loadingPermissions = true
      
      try {
        // Carrega todas as permissões disponíveis
        // const allPermissions = await this.$axios.$get('/groups/all_permissions/')
        const allPermissions = await this.$services.group.getAllPermissions()
        this.availablePermissions = Array.isArray(allPermissions) ? allPermissions : []
        
        // Seleciona as permissões atuais
        this.selectedPermissions = [...this.permissions]
      } catch (error) {
        console.error('Erro ao carregar permissões:', error)
        this.showMessage('Erro ao carregar permissões', 'error')
      } finally {
        this.loadingPermissions = false
      }
    },
    
    // Adicionar usuários ao grupo
    addToGroup(users) {
      if (!users || !users.length) return
      
      // Filtra apenas usuários que não estão no grupo
      const groupUserIds = this.groupMembers.map(u => u.id)
      const usersToAdd = users.filter(u => !groupUserIds.includes(u.id))
      
      if (usersToAdd.length === 0) return
      
      // Adiciona usuários ao grupo
      this.groupMembers = [...this.groupMembers, ...usersToAdd]
      this.selectedAvailableUsers = []
    },
    
    // Remover usuários do grupo
    removeFromGroup(users) {
      if (!users || !users.length) return
      
      // Remove usuários do grupo
      const userIdsToRemove = users.map(user => user.id)
      this.groupMembers = this.groupMembers.filter(user => !userIdsToRemove.includes(user.id))
      this.selectedGroupUsers = []
    },
    
    // Remove um membro específico
    removeMember(member) {
      this.removeFromGroup([member])
      this.saveMembers()
    },
    
    // Remove uma permissão da seleção
    removePermission(permission) {
      this.selectedPermissions = this.selectedPermissions.filter(p => p.id !== permission.id)
    },
    
    // Salva as alterações nos membros
    async saveMembers() {
      this.isSaving = true
      
      try {
        const groupId = this.group.id
        const userIds = this.groupMembers.map(user => user.id)
        
        /*
        await this.$axios.put(`/groups/${groupId}/users/`, {
          users_ids: userIds
        })
        */

       await this.$services.group.updateGroupMembers(groupId, {
          users_ids: userIds
        })

        
        
        this.originalMemberIds = [...userIds]
        this.memberDialog = false
        this.showMessage('Membros atualizados com sucesso')
      } catch (error) {
        console.error('Erro ao salvar membros:', error)
        this.showMessage('Erro ao atualizar membros', 'error')
      } finally {
        this.isSaving = false
      }
    },
    
    // Salva as alterações nas permissões
    async savePermissions() {
      this.isSaving = true
      
      try {
        const groupId = this.group.id
        const permissionIds = this.selectedPermissions.map(p => p.id)
        
        /*
        await this.$axios.post(`/groups/${groupId}/permissions/`, {
          permissions: permissionIds
        })
        */

        await this.$services.group.updateGroupPermissions(groupId, {
          permissions: permissionIds
        })
        
        // Atualiza a lista local de permissões
        this.permissions = [...this.selectedPermissions]
        this.permissionDialog = false
        this.showMessage('Permissões atualizadas com sucesso')
      } catch (error) {
        console.error('Erro ao salvar permissões:', error)
        this.showMessage('Erro ao atualizar permissões', 'error')
      } finally {
        this.isSaving = false
      }
    },
    
    // Salva os detalhes básicos do grupo
    async saveGroupDetails() {
      if (!this.valid) return
      
      this.isSaving = true
      
      try {
        const groupId = this.group.id
        if (!this.editedGroup.name.trim()) {
          throw new Error('O nome do grupo não pode estar vazio');
        }
        if (this.editedGroup.description && this.editedGroup.description.length > 20) {
          throw new Error('A descrição deve ter no máximo 20 caracteres');
        }
        await this.$services.group.updateGroup(groupId, {
          name: this.editedGroup.name,
          description: this.editedGroup.description || ''
        })
        
        // Atualiza o grupo local
        this.group = {
          ...this.group,
          name: this.editedGroup.name,
          description: this.editedGroup.description
        }
        
        this.editMode = false
        this.showMessage('Grupo atualizado com sucesso')
      } catch (error) {
        console.error('Erro ao atualizar grupo:', error)
        this.showMessage('Erro ao atualizar grupo', 'error')
      } finally {
        this.isSaving = false
      }
    },
    
    // Cancela a edição de detalhes
    cancelEdit() {
      this.editedGroup = {
        name: this.group.name,
        description: this.group.description
      }
      this.editMode = false
    },
    
    // Exclui o grupo
    async deleteGroup() {
      this.isSaving = true
      
      try {
        const groupId = this.group.id
        await this.$services.group.deleteGroup(groupId)
        
        this.confirmDelete = false
        this.showMessage('Grupo excluído com sucesso')
        
        // Redireciona para a lista de grupos
        this.$router.push('/groups')
      } catch (error) {
        console.error('Erro ao excluir grupo:', error)
        this.showMessage('Erro ao excluir grupo', 'error')
      } finally {
        this.isSaving = false
      }
    },
    
    // Utilitários
    getInitials(name) {
      if (!name) return '??'
      return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase()
    },
    
    darkenColor(color) {
      // Simple function to darken a hex color
      color = color.replace('#', '')
      const r = parseInt(color.substr(0, 2), 16)
      const g = parseInt(color.substr(2, 2), 16)
      const b = parseInt(color.substr(4, 2), 16)
      
      const darkenAmount = 0.2
      const newR = Math.round(r * (1 - darkenAmount))
      const newG = Math.round(g * (1 - darkenAmount))
      const newB = Math.round(b * (1 - darkenAmount))
      
      return `#${newR.toString(16).padStart(2, '0')}${newG.toString(16).padStart(2, '0')}${newB.toString(16).padStart(2, '0')}`
    },
    
    // Exibe uma mensagem de feedback
    showMessage(text, color = 'success') {
      this.snackbar = {
        show: true,
        text,
        color,
        timeout: color === 'error' ? 6000 : 3000
      }
    }
  }
}
</script>

<style scoped>
.group-details-page {
  position: relative;
  padding-bottom: 40px;
  padding-top: 40px;
}

.group-banner {
  position: relative;
  height: 200px;
  background-size: cover;
  background-position: center;
}

.banner-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
}

.member-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.overflow-y-auto {
  overflow-y: auto;
}

/* Animações */
.v-enter-active, .v-leave-active {
  transition: opacity 0.3s;
}
.v-enter, .v-leave-to {
  opacity: 0;
}
</style>