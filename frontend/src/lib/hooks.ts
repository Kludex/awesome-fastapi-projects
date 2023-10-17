import { createContext, useContext, useEffect } from "react";
import { QueryParamsManagerInterface } from "./query-params";
import { useSearchParams } from "next/navigation";
import React from "react";

export const QueryParamsManagerContext =
  createContext<QueryParamsManagerInterface>({
    requestQueryUpdate: () => {},
    requestQueryDelete: () => {},
    requestQueryClear: () => {},
    commit: () => {},
  });
QueryParamsManagerContext.displayName = "QueryParamsManagerContext";

export const useQueryParamsManager = () => {
  return useContext(QueryParamsManagerContext);
};

export const useQueryParamState = <T>({
  initialValue,
  paramName,
  toQueryParam,
  fromQueryParam,
}: {
  initialValue: T | null;
  paramName: string;
  toQueryParam: (value: T) => string;
  fromQueryParam: (value: string | null) => T | null;
}): [T | null, (value: T) => void] => {
  const queryParamsManager = useQueryParamsManager();
  const searchParams = useSearchParams();

  const [value, setValue] = React.useState<T | null>(initialValue);

  const updateQueryParamState = React.useCallback(
    (value: T) => {
      queryParamsManager.requestQueryUpdate(paramName, toQueryParam(value));
      setValue(value);
    },
    [queryParamsManager, paramName, toQueryParam, setValue],
  );

  useEffect(() => {
    const params = new URLSearchParams(searchParams);
    const valueFromQuery = fromQueryParam(params.get(paramName));
    if (valueFromQuery === null && initialValue !== null) {
      setValue(initialValue);
    }
    return;
  }, [
    initialValue,
    paramName,
    fromQueryParam,
    setValue,
    searchParams,
    queryParamsManager,
  ]);
  return [value, updateQueryParamState];
};
