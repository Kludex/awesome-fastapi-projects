import { loadIndexServerOnly } from "@/lib/load-index-server-only";
import { DataTable } from "./data-table";
import { columns } from "./columns";

export default async function Home() {
  const { repos } = await loadIndexServerOnly();
  return (
    <section className="py-10">
      <DataTable columns={columns} data={repos} />
    </section>
  );
}
