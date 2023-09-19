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
import { Dependency } from "@/lib/schemas";

const FormSchema = z.object({
  search: z
    .string()
    .min(0)
    .max(256, { message: "Search must be less than 256 characters" })
    .default(""),
  dependencies: z.array(z.string()).default(() => []),
});

export interface SearchFormProps {
  onSubmit: (data: z.infer<typeof FormSchema>) => void;
  dependencies: Dependency[];
}

export function SearchForm({ onSubmit, dependencies }: SearchFormProps) {
  const form = useForm<z.infer<typeof FormSchema>>({
    resolver: zodResolver(FormSchema),
  });

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
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
