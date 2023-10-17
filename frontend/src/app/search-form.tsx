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
import { useQueryParamState, useQueryParamsManager } from "@/lib/hooks";

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
  const queryParamsManager = useQueryParamsManager();
  const [searchQuery, setSearchQuery] = useQueryParamState({
    initialValue: "",
    paramName: "search",
    toQueryParam: (value) => encodeURIComponent(value),
    fromQueryParam: (value) => {
      if (!value) {
        return "";
      }
      return decodeURIComponent(value);
    },
  });
  const [dependenciesQuery, setDependenciesQuery] = useQueryParamState<
    Dependency[]
  >({
    initialValue: [],
    paramName: "dependencies",
    toQueryParam: function encodeDependenciesArray(value) {
      if (!value) {
        return "";
      }
      // join dependencies names with `~`
      let encodedArray = value.map((dependency) => dependency.name).join(",");
      // double encode `~` to avoid conflicts with the separator
      encodedArray = encodedArray.replaceAll(",", ",,");
      // URL encode the string
      return encodeURIComponent(encodedArray);
    },
    fromQueryParam: function decodeDependenciesArray(value) {
      if (!value) {
        return [];
      }
      // URL decode the string
      let decodedArray = decodeURIComponent(value);
      // double decode `~` to avoid conflicts with the separator
      decodedArray = decodedArray.replaceAll(",,", ",");
      // split dependencies names with `~`
      const dependenciesNames = decodedArray.split(",");
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
            dependencies.find(
              (dependency) => dependency.name === dependencyName,
            ),
          )
          // filter out undefined values
          .filter(Boolean) as Dependency[]
      );
    },
  });
  const form = useForm<z.infer<typeof FormSchema>>({
    resolver: zodResolver(FormSchema),
    defaultValues: {
      search: searchQuery ?? "",
      dependencies: dependenciesQuery ?? [],
    },
  });

  const onSubmitWrapper = (data: z.infer<typeof FormSchema>) => {
    onSubmit(data);
    queryParamsManager.commit();
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
                <Input
                  placeholder="Search..."
                  {...field}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                    setSearchQuery(e.target.value);
                    field.onChange(e);
                  }}
                />
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
                <MultiSelect
                  data={dependencies}
                  onChange={(dependencies) => {
                    setDependenciesQuery(dependencies);
                    field.onChange(dependencies);
                  }}
                  value={field.value}
                />
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
