"use client";
import {
  createReposOrama,
  prepareReposOramaIndex,
  ReposOramaContext,
} from "@/lib/search";
import { PropsWithChildren } from "react";
import { SearchProvider } from "./search-provider";
import { RepoIndex } from "@/lib/schemas";

export function ReposSearchProvider({
  children,
  repos,
}: PropsWithChildren<{
  repos: RepoIndex["repos"];
}>) {
  const prepareOramaIndex = async () => {
    const orama = await createReposOrama();
    await prepareReposOramaIndex(orama, repos);
    return orama;
  };

  return (
    <SearchProvider
      createIndex={prepareOramaIndex}
      OramaContext={ReposOramaContext}
    >
      {children}
    </SearchProvider>
  );
}
