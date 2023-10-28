"use client";
import { Repo, Dependency } from "@/lib/schemas";
import { search } from "@orama/orama";
import { SearchForm } from "./search-form";
import { columns } from "./columns";
import { DataTable } from "./data-table";
import { useReposOrama } from "@/lib/search";
import { useState } from "react";
import { useQuerySearchFormData } from "@/lib/hooks";
import React from "react";

export function ReposTable({
  repos,
  dependencies,
}: {
  repos: Repo[];
  dependencies: Dependency[];
}) {
  const reposOrama = useReposOrama();
  const [searchedRepos, setSearchedRepos] = useState<Repo[]>(repos);
  const { searchQueryFromQueryParam, dependenciesQueryFromQueryParam } =
    useQuerySearchFormData(dependencies);

  const onSearchSubmit = React.useCallback(
    async ({
      search: description,
      dependencies,
    }: {
      search: string;
      dependencies: Dependency[];
    }) => {
      if (!reposOrama.isIndexed || !reposOrama.orama) {
        throw new Error("Repos Orama is not initialized");
      }
      const results = await search<Repo>(reposOrama.orama, {
        term: description,
        properties: ["description"],
        limit: repos.length,
      });
      const searchedRepos = results.hits.map((hit) => hit.document as Repo);
      // Workaround because Orama doesn't support filtering by properties of objects in arrays
      const filteredRepos = searchedRepos.filter((repo) => {
        return dependencies.every((dependency) => {
          return repo.dependencies.some(
            (repoDependency) => repoDependency.id === dependency.id,
          );
        });
      });
      setSearchedRepos(filteredRepos);
    },
    [repos, reposOrama.isIndexed, reposOrama.orama],
  );

  const _ref = React.useCallback(
    (node: HTMLDivElement | null) => {
      if (node !== null) {
        if (reposOrama.isIndexed && reposOrama.orama) {
          onSearchSubmit({
            search: searchQueryFromQueryParam(),
            dependencies: dependenciesQueryFromQueryParam(),
          });
        }
      }
    },
    [
      dependenciesQueryFromQueryParam,
      onSearchSubmit,
      reposOrama.isIndexed,
      reposOrama.orama,
      searchQueryFromQueryParam,
    ],
  );

  return (
    <>
      <div className="container mb-4 max-w-xl" ref={_ref}>
        <SearchForm onSubmit={onSearchSubmit} dependencies={dependencies} />
      </div>
      <DataTable columns={columns} data={searchedRepos} />
    </>
  );
}
