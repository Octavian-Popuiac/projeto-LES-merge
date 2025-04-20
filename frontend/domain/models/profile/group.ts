export class Group {
  constructor(
    public id: number,
    public name: string,
    public permissions: GroupPermission[]
  ) {}
}

export class GroupPermission {
  constructor(
    public id: number,
    public name: string,
    public codename: string,
    public appLabel: string,
    public model: string,
    public verbose: string
  ) {}
}
