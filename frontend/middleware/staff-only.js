export default function({ store, redirect }) {
  // Verificar se o usuário está autenticado
  if (!store.getters['auth/isAuthenticated']) {
    return redirect('/login')
  }
  
  // Verificar se o usuário tem status de staff
  if (!store.getters['auth/isStaff']) {
    return redirect('/projects')
  }
}