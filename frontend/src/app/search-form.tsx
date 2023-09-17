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

const FormSchema = z.object({
  search: z
    .string()
    .max(1024, { message: "Search must be less than 1024 characters" }),
});

export interface SearchFormProps {
  onSubmit: (data: z.infer<typeof FormSchema>) => void;
}

export function SearchForm({ onSubmit }: SearchFormProps) {
  const form = useForm<z.infer<typeof FormSchema>>({
    resolver: zodResolver(FormSchema),
  });

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="w-2/3 space-y-6">
        <FormField
          control={form.control}
          name="search"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Search for a repository</FormLabel>
              <FormControl>
                <Input placeholder="fastapi" {...field} />
              </FormControl>
              <FormDescription>
                The search is performed on the repository description.
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
