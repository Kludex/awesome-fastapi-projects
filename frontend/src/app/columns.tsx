"use client";
import { Badge } from "@/components/ui/badge";
import { Repo } from "@/lib/schemas";
import { ColumnDef } from "@tanstack/react-table";

export const columns: ColumnDef<Repo>[] = [
  {
    accessorKey: "url",
    header: function () {
      return (
        <div>
          Project
          <span role="img" aria-label="rocket" className="ml-1">
            🚀
          </span>
        </div>
      );
    },
  },
  {
    accessorKey: "description",
    header: function () {
      return (
        <div>
          Description
          <span role="img" aria-label="writing" className="ml-1">
            ✍️
          </span>
        </div>
      );
    },
    cell: function ({ row }) {
      return (
        <p className="max-w-md truncate hover:overflow-visible hover:whitespace-normal leading-7 [&:not(:first-child)]:mt-6">
          {row.getValue<string>("description") || "No description"}
        </p>
      );
    },
  },
  {
    accessorKey: "stars",
    header: function () {
      return (
        <div className="text-center">
          Stars
          <span role="img" aria-label="star" className="ml-1">
            ⭐
          </span>
        </div>
      );
    },
    cell: function ({ row }) {
      return (
        <Badge variant="outline">
          {row.getValue<number>("stars").toLocaleString("en-US")}
        </Badge>
      );
    },
  },
];
