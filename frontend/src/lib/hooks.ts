import { usePathname, useSearchParams, useRouter } from "next/navigation";
import React from "react";
import { Dependency } from "./schemas";

export const useQuerySearchFormData = (dependencies: Dependency[]) => {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const searchQueryToQueryParam = React.useCallback(
    (searchQueryValue: string) => {
      if (!searchQueryValue) {
        return "";
      }
      return encodeURIComponent(searchQueryValue);
    },
    [],
  );

  const searchQueryFromQueryParam = React.useCallback(() => {
    if (!searchParams.has("search")) {
      return "";
    }
    return decodeURIComponent(searchParams.get("search") ?? "");
  }, [searchParams]);

  const dependenciesQueryToQueryParam = React.useCallback(
    (dependenciesQueryValue: Dependency[]) => {
      if (!dependenciesQueryValue) {
        return "";
      }
      // join dependencies names with `~`
      let encodedArray = dependenciesQueryValue.map(
        (dependency) => dependency.name,
      );
      // join the names with `~`
      let encodedArrayValue = encodedArray.join("~");
      // URL encode the string
      return encodeURIComponent(encodedArrayValue);
    },
    [],
  );

  const dependenciesQueryFromQueryParam = React.useCallback(() => {
    if (!searchParams.has("dependencies")) {
      return [];
    }
    // URL decode the string
    let decodedArray = decodeURIComponent(
      searchParams.get("dependencies") ?? "",
    );
    // split dependencies names with `~`
    const dependenciesNames = decodedArray.split("~");
    // deduplicate dependencies names
    const uniqueDependenciesNames = new Set(dependenciesNames).values();
    // filter out empty strings
    const filteredDependenciesNames = Array.from(
      uniqueDependenciesNames,
    ).filter((dependencyName) => dependencyName !== "");
    // return dependencies objects
    return (
      filteredDependenciesNames
        .map((dependencyName) =>
          dependencies.find((dependency) => dependency.name === dependencyName),
        )
        // filter out undefined values
        .filter(Boolean) as Dependency[]
    );
  }, [searchParams, dependencies]);

  return {
    searchQueryToQueryParam,
    searchQueryFromQueryParam,
    dependenciesQueryToQueryParam,
    dependenciesQueryFromQueryParam,
  };
};
