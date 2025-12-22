'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';
import { Menu, X, User, LogOut, Crown, Briefcase, MessageSquare, Target, Home } from 'lucide-react';
import Logo from './Logo';
import { useAuth } from '@/contexts/AuthContext';
import { motion } from 'framer-motion';

export default function Navigation() {
  const router = useRouter();
  const pathname = usePathname();
  const { user, isAuthenticated, hasPremiumAccess, logout } = useAuth();
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

  return (
    <nav className="fixed top-0 left-0 right-0 z-[100] bg-premium-bg/80 backdrop-blur-xl border-b border-premium-accent/10 py-4">
      <div className="max-w-7xl mx-auto px-6 flex justify-between items-center">
        {/* Logo */}
        <Logo size="sm" linkTo="/" />

        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center gap-8">
          <Link href="/#features" className="text-sm font-medium text-premium-text hover:text-premium-accent transition-colors">Platform</Link>
          <Link href="/#how-it-works" className="text-sm font-medium text-premium-text hover:text-premium-accent transition-colors">How It Works</Link>
          <Link href="/#testimonials" className="text-sm font-medium text-premium-text hover:text-premium-accent transition-colors">Success Stories</Link>
          <Link href="/pricing" className="text-sm font-medium text-premium-text hover:text-premium-accent transition-colors">Pricing</Link>
          
          {isAuthenticated ? (
            <div className="flex items-center gap-4 ml-4">
              <Link href="/dashboard" className="text-sm font-bold text-premium-accent flex items-center gap-2">
                Dashboard
                {hasPremiumAccess && <Crown className="w-4 h-4" />}
              </Link>
              <button 
                onClick={handleLogout}
                className="p-2 text-premium-text-muted hover:text-white transition-colors"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-6 ml-4">
              <Link href="/login" className="text-sm font-medium text-premium-text hover:text-premium-accent transition-colors">Sign In</Link>
              <Link 
                href="/#analyze" 
                className="bg-gradient-to-br from-premium-accent to-[#0099CC] text-premium-primary px-6 py-2.5 rounded-lg font-bold text-sm transition-all hover:-translate-y-0.5 hover:shadow-[0_10px_30px_rgba(0,217,255,0.3)]"
              >
                Get Analysis
              </Link>
            </div>
          )}
        </div>

        {/* Mobile Menu Toggle */}
        <button 
          className="md:hidden text-premium-text"
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
        >
          {isMobileMenuOpen ? <X /> : <Menu />}
        </button>
      </div>

      {/* Mobile Menu */}
      {isMobileMenuOpen && (
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="md:hidden absolute top-full left-0 right-0 bg-premium-bg border-b border-premium-accent/10 p-6 flex flex-col gap-6"
        >
          <Link href="/#features" onClick={() => setIsMobileMenuOpen(false)} className="text-lg font-medium">Platform</Link>
          <Link href="/#how-it-works" onClick={() => setIsMobileMenuOpen(false)} className="text-lg font-medium">How It Works</Link>
          <Link href="/#testimonials" onClick={() => setIsMobileMenuOpen(false)} className="text-lg font-medium">Success Stories</Link>
          <Link href="/pricing" onClick={() => setIsMobileMenuOpen(false)} className="text-lg font-medium">Pricing</Link>
          <hr className="border-premium-accent/10" />
          {isAuthenticated ? (
            <Link href="/dashboard" onClick={() => setIsMobileMenuOpen(false)} className="text-lg font-bold text-premium-accent">Dashboard</Link>
          ) : (
            <>
              <Link href="/login" onClick={() => setIsMobileMenuOpen(false)} className="text-lg font-medium">Sign In</Link>
              <Link href="/#analyze" onClick={() => setIsMobileMenuOpen(false)} className="premium-btn-primary text-center">Get Analysis</Link>
            </>
          )}
        </motion.div>
      )}
    </nav>
  );
}
