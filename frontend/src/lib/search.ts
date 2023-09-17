import {
  Orama,
  ProvidedTypes as OramaProvidedTypes,
  create,
  insertMultiple,
} from "@orama/orama";
import { Index } from "./schemas";
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
    id: "index",
  });
  return orama;
}

export async function prepareReposOramaIndex(
  orama: ReposOrama,
  data: Index["repos"],
): Promise<Orama<{ Index: { description: string } }>> {
  await insertMultiple(orama, data, 100);
  return orama;
}

export const ReposOramaContext = createOramaContext<ReposOramaParameters>();
ReposOramaContext.displayName = "ReposOramaContext";

export const useReposOrama = () => {
  return useContext(ReposOramaContext);
};
