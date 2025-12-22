import type { Metadata } from "next";
import { Inter, Outfit, Crimson_Pro, DM_Sans } from "next/font/google";
import "./globals.css";
import Navigation from "@/components/Navigation";
import BottomNav from "@/components/BottomNav";
import Footer from "@/components/Footer";
import { Providers } from "@/components/Providers";
import { Analytics } from "@vercel/analytics/react";
import { AuthProvider } from "@/contexts/AuthContext";
import ErrorBoundary from "@/components/ErrorBoundary";
import { CookieConsentBanner } from "@/components/CookieConsentBanner";

const inter = Inter({
  subsets: ["latin"],
  variable: '--font-inter',
  display: 'swap',
});

const outfit = Outfit({
  subsets: ["latin"],
  variable: '--font-outfit',
  display: 'swap',
});

const crimsonPro = Crimson_Pro({
  subsets: ["latin"],
  variable: '--font-crimson-pro',
  display: 'swap',
});

const dmSans = DM_Sans({
  subsets: ["latin"],
  variable: '--font-dm-sans',
  display: 'swap',
});

export const metadata: Metadata = {
  title: "NextCI | AI-Powered Career Intelligence Platform",
  description: "Enterprise-grade AI career analysis platform. Get data-driven insights on automation risk, skill gaps, and career trajectory.",
  keywords: ["career", "AI", "automation", "jobs", "reskilling", "career transition", "career intelligence"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} ${outfit.variable} ${crimsonPro.variable} ${dmSans.variable}`}>
      <body className="font-sans bg-dark min-h-screen flex flex-col">
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
