import { loadIndexServerOnly } from "@/lib/repos-index";
import { ReposTable } from "./repos-table";
import { ReposSearchProvider } from "./repos-search-provider";

export default async function Home() {
  const { repos } = await loadIndexServerOnly();

  return (
    <section className="py-10">
      <ReposSearchProvider repos={repos}>
        <ReposTable repos={repos} />
      </ReposSearchProvider>
    </section>
  );
}
