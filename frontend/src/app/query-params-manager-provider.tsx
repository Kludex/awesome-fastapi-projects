"use client";
import { QueryParamsManagerContext } from "@/lib/hooks";
import { QueryParamsManager } from "@/lib/query-params";
import { useSearchParams, usePathname, useRouter } from "next/navigation";
import React from "react";

export function QueryParamsManagerProvider({
  children,
}: React.PropsWithChildren<{}>) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const queryParamsManager = React.useMemo(() => {
    const params = new URLSearchParams(searchParams);
    return new QueryParamsManager(router, pathname, params);
  }, [router, pathname, searchParams]);
  return (
    <QueryParamsManagerContext.Provider value={queryParamsManager}>
      {children}
    </QueryParamsManagerContext.Provider>
  );
}
