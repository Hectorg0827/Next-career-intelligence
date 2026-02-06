import type { Metadata } from "next";
import "./globals.css";
import Navigation from "@/components/Navigation";
import BottomNav from "@/components/BottomNav";
import Footer from "@/components/Footer";
import { Providers } from "@/components/Providers";
import { Analytics } from "@vercel/analytics/react";
import { AuthProvider } from "@/contexts/AuthContext";
import ErrorBoundary from "@/components/ErrorBoundary";
import { CookieConsentBanner } from "@/components/CookieConsentBanner";

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
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="font-sans bg-nci-bg text-white min-h-screen flex flex-col">
        <ErrorBoundary>
          <Providers>
            <AuthProvider>
              <Navigation />
              <main className="flex-grow pb-24 md:pb-0">{children}</main>
              <Footer />
              <BottomNav />
              <CookieConsentBanner />
            </AuthProvider>
          </Providers>
        </ErrorBoundary>
        <Analytics />
      </body>
    </html>
  );
}
