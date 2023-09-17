"use client";
import { IOramaContext } from "@/lib/search";
import { Context, PropsWithChildren, useEffect, useState } from "react";

import { Orama, ProvidedTypes as OramaProvidedTypes } from "@orama/orama";

export type SearchProviderProps<
  OramaParameters extends Partial<OramaProvidedTypes> = any,
> = PropsWithChildren<{
  OramaContext: Context<IOramaContext<OramaParameters>>;
  createIndex: () => Promise<Orama<OramaParameters>>;
}>;

export function SearchProvider<
  OramaParameters extends Partial<OramaProvidedTypes>,
>({
  children,
  OramaContext,
  createIndex,
}: SearchProviderProps<OramaParameters>) {
  const [orama, setOrama] = useState<Orama<OramaParameters> | null>(null);
  const [isIndexed, setIsIndexed] = useState(false);

  useEffect(() => {
    async function initializeOrama() {
      setIsIndexed(false);
      await createIndex().then(setOrama);
      setIsIndexed(true);
    }
    initializeOrama();
  }, [createIndex]);

  return (
    <OramaContext.Provider value={{ orama, isIndexed }}>
      {children}
    </OramaContext.Provider>
  );
}
