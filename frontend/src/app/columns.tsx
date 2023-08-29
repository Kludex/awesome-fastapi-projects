import { Repo } from "@/lib/schemas";
import { ColumnDef } from "@tanstack/react-table";

export const columns: ColumnDef<Repo>[] = [
  {
    accessorKey: "url",
    header: "Link",
  },
  {
    accessorKey: "description",
    header: "Description",
  },
  {
    accessorKey: "stars",
    header: "Stars",
  },
];
