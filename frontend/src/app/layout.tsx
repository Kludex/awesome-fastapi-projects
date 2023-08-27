import "./globals.css";
import type { Metadata } from "next";
import { Inter } from "next/font/google";

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
