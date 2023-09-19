import { cache } from "react";
import "server-only";
import * as fs from "fs";
import * as path from "path";
import { dependenciesIndexSchema, reposIndexSchema } from "./schemas";
import { ZodError } from "zod";

// TODO: docstrings

export const REPOS_INDEX_FILE_PATH = path.normalize(
  path.join(__dirname, "..", "..", "..", "..", "repos_index.json"),
);

export const DEPENDENCIES_INDEX_FILE_PATH = path.normalize(
  path.join(__dirname, "..", "..", "..", "..", "dependencies_index.json"),
);

export const preload = () => {
  void loadReposIndexServerOnly();
  void loadDependenciesIndexServerOnly();
};

// TODO: tests

export const loadReposIndexServerOnly = cache(async () => {
  try {
    const indexData = JSON.parse(
      await fs.promises.readFile(REPOS_INDEX_FILE_PATH, "utf-8"),
      (key, value) => {
        if (key === "id" || key === "source_graph_repo_id") {
          return String(value);
        }
        return value;
      },
    );
    return await reposIndexSchema.parseAsync(indexData);
  } catch (err) {
    if (err instanceof ZodError) {
      throw new Error(
        `Failed to parse the repos index: ${JSON.stringify(err.format())}`,
      );
    }
    throw new Error(`Failed to load the repos index: ${err}`);
  }
});

export const loadDependenciesIndexServerOnly = cache(async () => {
  try {
    const indexData = JSON.parse(
      await fs.promises.readFile(DEPENDENCIES_INDEX_FILE_PATH, "utf-8"),
      (key, value) => {
        if (key === "id") {
          return String(value);
        }
        return value;
      },
    );
    return await dependenciesIndexSchema.parseAsync(indexData);
  } catch (err) {
    if (err instanceof ZodError) {
      throw new Error(
        `Failed to parse the dependencies index: ${JSON.stringify(
          err.format(),
        )}`,
      );
    }
    throw new Error(`Failed to load the dependencies index: ${err}`);
  }
});
