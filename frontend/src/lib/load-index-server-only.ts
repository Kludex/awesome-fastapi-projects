import { cache } from "react";
import "server-only";
import * as fs from "fs";
import * as path from "path";
import { indexSchema } from "./schemas";
import { ZodError } from "zod";

// TODO: docstrings

export const INDEX_FILE_PATH = path.normalize(
  path.join(__dirname, "..", "..", "..", "..", "index.json"),
);

export const preload = () => {
  void loadIndexServerOnly();
};

// TODO: tests

export const loadIndexServerOnly = cache(async () => {
  try {
    const indexData = JSON.parse(
      await fs.promises.readFile(INDEX_FILE_PATH, "utf-8"),
    );
    return await indexSchema.parseAsync(indexData);
  } catch (err) {
    if (err instanceof ZodError) {
      throw new Error(
        `Failed to parse the repos index: ${JSON.stringify(err.format())}`,
      );
    }
    throw new Error(`Failed to load the repos index: ${err}`);
  }
});
