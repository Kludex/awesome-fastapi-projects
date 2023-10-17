import { cn } from "@/lib/utils";
import "./globals.css";
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { buttonVariants } from "@/components/ui/button";
import { Icons } from "@/components/ui/icons";
import Link from "next/link";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { FolderGit, Rocket } from "lucide-react";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Awesome FastAPI projects",
  description: "An automatically generated list of awesome FastAPI projects",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="hidden flex-col md:flex">
          <div className="border-b">
            <div className="w-full flex h-16 items-center justify-center px-4">
              <nav className="container flex items-center justify-between space-x-4 lg:space-x-6 mx-6">
                <p className="text-md font-medium transition-colors">
                  A list of FastAPI projects! 😎 🚀
                </p>
                <Link
                  target="_blank"
                  rel="noreferrer"
                  href="https://github.com/vladfedoriuk/awesome-fastapi-projects/tree/vladfedoriuk_web_app"
                  className={cn(
                    buttonVariants({ variant: "ghost" }),
                    "h-6 w-6 flex items-center justify-center p-0 rounded-full",
                  )}
                >
                  <Icons.gitHub className="h-6 w-6" />
                </Link>
              </nav>
            </div>
          </div>
        </div>
        <main className="container">
          <h1 className="scroll-m-20 text-4xl font-extrabold tracking-tight lg:text-5xl text-center mt-8">
            Awesome FastAPI projects{" "}
            <span role="img" aria-label="party">
              🎉
            </span>
          </h1>
          {children}
        </main>
        <div className="border-t">
          <footer className="bg-white dark:bg-gray-900">
            <div className="w-full max-w-screen-xl mx-auto p-4 md:py-8">
              <div className="sm:flex sm:items-center sm:justify-between gap-4">
                <div className="grid gap-4 md:grid-cols-1 lg:grid-cols-2">
                  <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                      <CardTitle className="text-sm font-medium">
                        Revision
                      </CardTitle>
                      <FolderGit className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                      <div className="text-xl font-bold">
                        {process.env.commitHash}
                      </div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 space-x-4 pb-2">
                      <CardTitle className="text-sm font-medium">
                        Application Version
                      </CardTitle>
                      <Rocket className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                      <div className="text-xl font-bold">
                        {process.env.frontentAppVersion}
                      </div>
                    </CardContent>
                  </Card>
                </div>
                <div className="flex flex-col mt-4 sm:mt-0 sm:flex-row sm:items-center sm:justify-between">
                  <p className="text-sm leading-7 [&:not(:first-child)]:mt-6">
                    This project wouldn&apos;t be possible without{" "}
                    <a
                      href="https://nextjs.org/"
                      className="font-bold hover:underline"
                      target="_blank"
                      rel="noreferrer"
                    >
                      Next.js
                    </a>
                    ,{" "}
                    <a
                      href="https://ui.shadcn.com/"
                      className="font-bold hover:underline"
                      target="_blank"
                      rel="noreferrer"
                    >
                      Shadcn UI
                    </a>
                    ,{" "}
                    <a
                      href="https://tailwindcss.com/"
                      className="font-bold hover:underline"
                      target="_blank"
                      rel="noreferrer"
                    >
                      Tailwind CSS
                    </a>
                    ,{" "}
                    <a
                      href="https://react.dev/"
                      className="font-bold hover:underline"
                      target="_blank"
                      rel="noreferrer"
                    >
                      React
                    </a>{" "}
                    and{" "}
                    <a
                      href="https://www.oramasearch.com/"
                      className="font-bold hover:underline"
                      target="_blank"
                      rel="noreferrer"
                    >
                      Orama Search
                    </a>
                  </p>
                </div>
              </div>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
// TODO: make a lnk to the github repo configurable via env variable
// TODO: sync form state with the URL
// TODO: improve pagination - sync with the URL, add a "go to page" input
// TODO: refactor the layout and the components
