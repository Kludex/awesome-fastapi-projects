"use client";
import {
  createDependenciesOrama,
  prepareDependenciesOramaIndex,
  DependenciesOramaContext,
} from "@/lib/search";
import { PropsWithChildren } from "react";
import { SearchProvider } from "./search-provider";
import { DependenciesIndex } from "@/lib/schemas";

export function DependenciesSearchProvider({
  children,
  dependencies,
}: PropsWithChildren<{
  dependencies: DependenciesIndex["dependencies"];
}>) {
  const prepareOramaIndex = async () => {
    const orama = await createDependenciesOrama();
    await prepareDependenciesOramaIndex(orama, dependencies);
    return orama;
  };

  return (
    <SearchProvider
      createIndex={prepareOramaIndex}
      OramaContext={DependenciesOramaContext}
    >
      {children}
    </SearchProvider>
  );
}
