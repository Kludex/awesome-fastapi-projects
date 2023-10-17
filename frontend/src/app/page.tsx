import {
  loadDependenciesIndexServerOnly,
  loadReposIndexServerOnly,
} from "@/lib/indexes";
import { ReposTable } from "./repos-table";
import { ReposSearchProvider } from "./repos-search-provider";
import { DependenciesSearchProvider } from "./dependencies-search-provider";

export default async function Home() {
  const { repos } = await loadReposIndexServerOnly();
  const { dependencies } = await loadDependenciesIndexServerOnly();
  // refactor repos and dependencies to be loaded from the context
  return (
    <section className="py-10">
      <ReposSearchProvider repos={repos}>
        <DependenciesSearchProvider dependencies={dependencies}>
          <ReposTable repos={repos} dependencies={dependencies} />
        </DependenciesSearchProvider>
      </ReposSearchProvider>
    </section>
  );
}
