import type { Metadata } from "next";
import "./globals.css";
import Navigation from "@/components/Navigation";
import BottomNav from "@/components/BottomNav";
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
      <body className="font-sans">
        <ErrorBoundary>
          <Providers>
            <AuthProvider>
              <Navigation />
              <div className="pb-16 md:pb-0">{children}</div>
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
