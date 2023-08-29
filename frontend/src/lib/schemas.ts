import { z } from "zod";

export const dependencySchema = z.object({
  id: z.number().min(0),
  name: z.string(),
});

export const repoSchema = z.object({
  id: z.number().min(0),
  url: z.string(),
  description: z.string(),
  stars: z.number().min(0),
  source_graph_repo_id: z.number().min(0),
  dependencies: z.array(dependencySchema),
  last_checked_revision: z.nullable(z.string()),
});

export const indexSchema = z.object({
  repos: z.array(repoSchema),
});

export type Dependency = z.infer<typeof dependencySchema>;
export type Repo = z.infer<typeof repoSchema>;
export type Index = z.infer<typeof indexSchema>;
