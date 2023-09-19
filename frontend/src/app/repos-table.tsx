"use client";
import { Repo, Dependency } from "@/lib/schemas";
import { search } from "@orama/orama";
import { SearchForm } from "./search-form";
import { columns } from "./columns";
import { DataTable } from "./data-table";
import { useReposOrama } from "@/lib/search";
import { useState } from "react";

export function ReposTable({
  repos,
  dependencies,
}: {
  repos: Repo[];
  dependencies: Dependency[];
}) {
  const reposOrama = useReposOrama();
  const [searchedRepos, setSearchedRepos] = useState<Repo[]>(repos);

  const onSearchSubmit = async ({
    search: description,
  }: {
    search: string;
  }) => {
    if (!reposOrama.isIndexed || !reposOrama.orama) {
      throw new Error("Repos Orama is not initialized");
    }
    const results = await search<Repo>(reposOrama.orama, {
      term: description,
      properties: ["description"],
      limit: repos.length,
    });
    setSearchedRepos(results.hits.map((hit) => hit.document as Repo));
  };

  return (
    <>
      <div className="container mb-4 max-w-xl">
        <SearchForm onSubmit={onSearchSubmit} dependencies={dependencies} />
      </div>
      <DataTable columns={columns} data={searchedRepos} />
    </>
  );
}
