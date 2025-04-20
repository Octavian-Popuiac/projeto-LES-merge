export interface CustomPermission {
  id: number;
  name: string;
  codename: string;
  description: string;
  category: string;
}

export class Permission implements CustomPermission {
  id: number;
  name: string;
  codename: string;
  description: string;
  category: string;

  constructor(data: CustomPermission) {
    this.id = data.id;
    this.name = data.name;
    this.codename = data.codename;
    this.description = data.description || '';
    this.category = data.category || 'Geral';
  }

  // Método para verificar se esta permissão corresponde a um determinado código
  hasCodename(codename: string): boolean {
    return this.codename === codename;
  }

  // Método para verificar se esta permissão pertence a uma determinada categoria
  isInCategory(category: string): boolean {
    return this.category.toLowerCase() === category.toLowerCase();
  }

  // Método estático para agrupar permissões por categoria
  static groupByCategory(permissions: Permission[]): Record<string, Permission[]> {
    return permissions.reduce((groups, permission) => {
      const category = permission.category || 'Geral';
      if (!groups[category]) {
        groups[category] = [];
      }
      groups[category].push(permission);
      return groups;
    }, {} as Record<string, Permission[]>);
  }

  // Método estático para filtrar permissões por texto de busca
  static filterBySearchText(permissions: Permission[], searchText: string): Permission[] {
    if (!searchText) return permissions;
    
    const search = searchText.toLowerCase();
    return permissions.filter(permission => 
      permission.name.toLowerCase().includes(search) ||
      permission.description.toLowerCase().includes(search) ||
      permission.codename.toLowerCase().includes(search) ||
      permission.category.toLowerCase().includes(search)
    );
  }
}