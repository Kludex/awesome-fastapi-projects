"use client";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import * as z from "zod";

import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { MultiSelect } from "@/components/ui/multiselect";
import { Dependency, dependencySchema } from "@/lib/schemas";
import { useSearchParams, useRouter, usePathname } from "next/navigation";
import React from "react";
import { useQuerySearchFormData } from "@/lib/hooks";

const FormSchema = z.object({
  search: z
    .string()
    .min(0)
    .max(256, { message: "Search must be less than 256 characters" })
    .default(""),
  dependencies: z.array(dependencySchema).default(() => []),
});

export interface SearchFormProps {
  onSubmit: (data: z.infer<typeof FormSchema>) => void;
  dependencies: Dependency[];
}

export function SearchForm({ onSubmit, dependencies }: SearchFormProps) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const {
    searchQueryFromQueryParam,
    searchQueryToQueryParam,
    dependenciesQueryFromQueryParam,
    dependenciesQueryToQueryParam,
  } = useQuerySearchFormData(dependencies);

  const form = useForm<z.infer<typeof FormSchema>>({
    resolver: zodResolver(FormSchema),
    defaultValues: {
      search: searchQueryFromQueryParam(),
      dependencies: dependenciesQueryFromQueryParam(),
    },
  });

  const createQueryString = React.useCallback(
    ({
      searchQueryValue,
      dependenciesQueryValue,
    }: {
      searchQueryValue: string;
      dependenciesQueryValue: Dependency[];
    }) => {
      const params = new URLSearchParams(searchParams);
      params.set("search", searchQueryToQueryParam(searchQueryValue));
      params.set(
        "dependencies",
        dependenciesQueryToQueryParam(dependenciesQueryValue),
      );

      return params.toString();
    },
    [dependenciesQueryToQueryParam, searchParams, searchQueryToQueryParam],
  );

  const onSubmitWrapper = (data: z.infer<typeof FormSchema>) => {
    onSubmit(data);
    // update URL search params
    const queryString = createQueryString({
      searchQueryValue: data.search,
      dependenciesQueryValue: data.dependencies,
    });
    router.replace(`${pathname}?${queryString}`);
  };
  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmitWrapper)} className="space-y-6">
        <FormField
          control={form.control}
          name="search"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Search for a repository</FormLabel>
              <FormControl>
                <Input placeholder="Search..." {...field} />
              </FormControl>
              <FormDescription>
                The search is performed on the repository description.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="dependencies"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Dependencies</FormLabel>
              <FormControl>
                <MultiSelect data={dependencies} {...field} />
              </FormControl>
              <FormDescription>
                Filter by dependencies used in the repository.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit">Search</Button>
      </form>
    </Form>
  );
}
