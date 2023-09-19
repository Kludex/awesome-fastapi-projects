import { z } from "zod";

export const dependencySchema = z.object({
  id: z.string(),
  name: z.string(),
});

export const repoSchema = z.object({
  id: z.string(),
  url: z.string(),
  description: z.string(),
  stars: z.number().min(0),
  source_graph_repo_id: z.string(),
  dependencies: z.array(dependencySchema),
  last_checked_revision: z.nullable(z.string()),
});

export const reposIndexSchema = z.object({
  repos: z.array(repoSchema),
});

export const dependenciesIndexSchema = z.object({
  dependencies: z.array(dependencySchema),
});

export type Dependency = z.infer<typeof dependencySchema>;
export type Repo = z.infer<typeof repoSchema>;
export type RepoIndex = z.infer<typeof reposIndexSchema>;
export type DependenciesIndex = z.infer<typeof dependenciesIndexSchema>;
