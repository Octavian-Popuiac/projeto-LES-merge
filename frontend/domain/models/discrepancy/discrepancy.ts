export class Discrepancy {
  constructor(
    public id: number,
    public project: number,
    public example: number,
    public labels: { label: string; count: number }[],
    public status: string,
    public created_at: string
  ) {}
}
