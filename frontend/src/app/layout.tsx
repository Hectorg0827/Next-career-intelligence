import type { Metadata } from "next";
import "./globals.css";
import Navigation from "@/components/Navigation";
import { Providers } from "@/components/Providers";

export const metadata: Metadata = {
  title: "NEXT | Adaptive Career Intelligence",
  description: "AI-powered career resilience platform - Analyze your AI displacement risk and discover future-proof career pathways",
  keywords: ["career", "AI", "automation", "jobs", "reskilling", "career transition"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="font-sans">
        <Providers>
          <Navigation />
          {children}
        </Providers>
      </body>
    </html>
  );
}
