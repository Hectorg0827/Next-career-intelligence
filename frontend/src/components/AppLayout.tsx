'use client';

import { ReactNode } from 'react';
import Navigation from '@/components/Navigation';
import Footer from '@/components/Footer';

interface AppLayoutProps {
  children: ReactNode;
  showNav?: boolean;
  showFooter?: boolean;
}

export default function AppLayout({ 
  children, 
  showNav = true, 
  showFooter = true 
}: AppLayoutProps) {
  return (
    <div className="flex flex-col min-h-screen">
      {showNav && <Navigation />}
      
      <main className="flex-1">
        {children}
      </main>
      
      {showFooter && <Footer />}
    </div>
  );
}
