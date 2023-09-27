import { cn } from "@/lib/utils";
import "./globals.css";
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { buttonVariants } from "@/components/ui/button";
import { Icons } from "@/components/ui/icons";
import Link from "next/link";

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
                  List of FastAPI projects! 😎 🚀
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
      </body>
    </html>
  );
}
// TODO: add a footer with tech stack
