'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';
import { Menu, X, User, LogOut, Sparkles, LogIn } from 'lucide-react';
import Logo from './Logo';
import { useAuth } from '@/contexts/AuthContext';

export default function Navigation() {
  const router = useRouter();
  const pathname = usePathname();
  const { user, isAuthenticated, logout } = useAuth();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const handleLogout = async () => {
    try {
      await logout();
      setIsMobileMenuOpen(false);
      router.push('/');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const scrollToFunnel = () => {
    if (pathname !== '/') {
      router.push('/#funnel');
    } else {
      const element = document.getElementById('job-title-input');
      element?.focus();
      element?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    setIsMobileMenuOpen(false);
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 h-20 bg-nci-bg/80 backdrop-blur-xl border-b border-white/5">
      <div className="max-w-7xl mx-auto px-6 h-full flex items-center justify-between">
        {/* Logo */}
        <Logo size="sm" linkTo="/" className="hover:opacity-80 transition-opacity" />

        {/* Action Buttons (Desktop) */}
        <div className="hidden md:flex items-center gap-4">
          <button
            onClick={scrollToFunnel}
            className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-nci-primary text-white text-[13px] font-bold shadow-glow-blue hover:scale-[1.02] transition-all"
          >
            <Sparkles className="w-4 h-4" />
            Analyze My Career
          </button>

          {isAuthenticated ? (
            <div className="flex items-center gap-3">
              <button
                onClick={() => router.push('/dashboard')}
                className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white text-[13px] font-bold hover:bg-white/10 transition-all"
              >
                <User className="w-4 h-4" />
                Dashboard
              </button>
              <button
                onClick={handleLogout}
                className="p-2.5 rounded-xl bg-white/5 border border-white/10 text-g-400 hover:text-white hover:border-white/20 transition-all"
                title="Logout"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <button
              onClick={() => router.push('/login')}
              className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white text-[13px] font-bold hover:bg-white/10 transition-all"
            >
              <LogIn className="w-4 h-4" />
              Sign In / Up
            </button>
          )}
        </div>

        {/* Mobile Menu Button */}
        <div className="md:hidden">
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="p-2 text-g-400 hover:text-white transition-colors"
          >
            {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Menu Overlay */}
      {isMobileMenuOpen && (
        <div className="md:hidden absolute top-20 left-0 w-full bg-nci-bg border-b border-white/5 p-6 flex flex-col gap-4 animate-in fade-in slide-in-from-top-4">
          <button
            onClick={scrollToFunnel}
            className="w-full h-12 rounded-xl bg-nci-primary text-white font-bold flex items-center justify-center gap-2"
          >
            <Sparkles className="w-4 h-4" />
            Analyze My Career
          </button>
          {isAuthenticated ? (
            <>
              <button
                onClick={() => { router.push('/dashboard'); setIsMobileMenuOpen(false); }}
                className="w-full h-12 rounded-xl bg-white/5 border border-white/10 text-white font-bold"
              >
                Dashboard
              </button>
              <button
                onClick={handleLogout}
                className="w-full h-12 rounded-xl bg-white/5 border border-white/10 text-g-400 font-bold"
              >
                Logout
              </button>
            </>
          ) : (
            <button
              onClick={() => { router.push('/login'); setIsMobileMenuOpen(false); }}
              className="w-full h-12 rounded-xl bg-white/5 border border-white/10 text-white font-bold"
            >
              Sign In / Up
            </button>
          )}
        </div>
      )}
    </nav>
  );
}
