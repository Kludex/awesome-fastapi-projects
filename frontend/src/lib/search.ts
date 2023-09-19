import {
  Orama,
  ProvidedTypes as OramaProvidedTypes,
  create,
  insertMultiple,
} from "@orama/orama";
import { DependenciesIndex, RepoIndex } from "./schemas";
import { Context, createContext, useContext } from "react";

export interface IOramaContext<
  OramaParameters extends Partial<OramaProvidedTypes> = any,
> {
  isIndexed: boolean;
  orama: Orama<OramaParameters> | null;
}

export function createOramaContext<
  OramaParameters extends Partial<OramaProvidedTypes>,
>(): Context<IOramaContext<OramaParameters>> {
  return createContext<IOramaContext<OramaParameters>>({
    isIndexed: false,
    orama: null,
  });
}

export interface ReposOramaParameters extends Partial<OramaProvidedTypes> {
  Index: { description: string };
}

export type ReposOrama = Orama<ReposOramaParameters>;

export async function createReposOrama(): Promise<ReposOrama> {
  const orama = await create({
    schema: {
      description: "string",
    },
    id: "repos-index",
  });
  return orama;
}

export async function prepareReposOramaIndex(
  orama: ReposOrama,
  data: RepoIndex["repos"],
): Promise<ReposOrama> {
  await insertMultiple(orama, data, 100);
  return orama;
}

export const ReposOramaContext = createOramaContext<ReposOramaParameters>();
ReposOramaContext.displayName = "ReposOramaContext";

export const useReposOrama = () => {
  return useContext(ReposOramaContext);
};

export interface DependenciesOramaParameters
  extends Partial<OramaProvidedTypes> {
  Index: { name: string };
}

export type DependenciesOrama = Orama<DependenciesOramaParameters>;

export async function createDependenciesOrama(): Promise<DependenciesOrama> {
  const orama = await create({
    schema: {
      name: "string",
    },
    id: "dependencies-index",
  });
  return orama;
}

export async function prepareDependenciesOramaIndex(
  orama: DependenciesOrama,
  data: DependenciesIndex["dependencies"],
): Promise<DependenciesOrama> {
  await insertMultiple(orama, data, 100);
  return orama;
}

export const DependenciesOramaContext =
  createOramaContext<DependenciesOramaParameters>();
DependenciesOramaContext.displayName = "DependenciesOramaContext";

export const useDependenciesOrama = () => {
  return useContext(DependenciesOramaContext);
};
