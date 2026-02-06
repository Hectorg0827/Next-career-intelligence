'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';
import { Menu, X, User, LogOut, Crown, Briefcase, MessageSquare, Target, Home } from 'lucide-react';
import Logo from './Logo';
import { useAuth } from '@/contexts/AuthContext';

interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  isPremium?: boolean;
}

const navItems: NavItem[] = [
  { name: 'Home', href: '/', icon: Home },
  { name: 'Dashboard', href: '/dashboard', icon: Target, isPremium: true },
  { name: 'Opportunities', href: '/jobs', icon: Briefcase, isPremium: true },
  { name: 'Career Coach', href: '/coach/chat', icon: MessageSquare, isPremium: true },
];

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

  const handleNavClick = (href: string) => {
    setIsMobileMenuOpen(false);
    router.push(href);
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 h-16 nav-glass">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex-shrink-0">
            <Logo size="sm" linkTo="/" />
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-2">
            {navItems.map((item) => {
              const isActive = pathname === item.href;
              const Icon = item.icon;

              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`px-4 py-2 rounded-xl font-medium transition-all duration-200 flex items-center gap-2 text-[13px] group ${
                    isActive
                      ? 'bg-nci-primary-dim text-nci-primary'
                      : 'text-g-400 hover:text-white hover:bg-white/5'
                  }`}
                >
                  <Icon className="w-4 h-4 transition-transform group-hover:scale-110" />
                  <span>{item.name}</span>
                  {item.isPremium && !hasPremiumAccess && (
                    <Crown className="w-3 h-3 text-nci-amber animate-pulse" />
                  )}
                </Link>
              );
            })}
          </div>

          {/* Desktop User Menu */}
          <div className="hidden md:flex items-center gap-3">
            {isAuthenticated && user ? (
              <>
                <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/[0.04] border border-nci-border">
                  <User className="w-4 h-4 text-nci-primary" />
                  <span className="text-g-300 text-[13px] font-medium max-w-[140px] truncate">
                    {user.name || user.email}
                  </span>
                  {hasPremiumAccess && <Crown className="w-3.5 h-3.5 text-nci-amber" />}
                </div>
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/[0.04] border border-nci-border hover:border-nci-border-hover transition-all duration-200 group"
                  aria-label="Log out"
                >
                  <LogOut className="w-4 h-4 text-g-400 group-hover:text-white transition-colors" />
                  <span className="text-g-400 group-hover:text-white text-[13px] font-medium transition-colors">Logout</span>
                </button>
              </>
            ) : (
              <button
                onClick={() => router.push('/login')}
                className="px-5 py-2 rounded-xl bg-nci-primary text-white text-[13px] font-semibold shadow-glow-blue hover:bg-primary-600 transition-all duration-200"
              >
                Get Started →
              </button>
            )}
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="p-2 rounded-xl text-g-400 hover:text-white hover:bg-white/5 transition-all duration-200"
              aria-label="Toggle menu"
            >
              {isMobileMenuOpen ? (
                <X className="w-6 h-6" />
              ) : (
                <Menu className="w-6 h-6" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden border-t border-nci-border nav-glass animate-fade-in-up">
          <div className="px-4 py-6 space-y-2">
            {navItems.map((item) => {
              const isActive = pathname === item.href;
              const Icon = item.icon;

              return (
                <button
                  key={item.name}
                  onClick={() => handleNavClick(item.href)}
                  className={`w-full px-4 py-3 rounded-xl font-medium transition-all duration-200 flex items-center gap-3 ${
                    isActive
                      ? 'bg-nci-primary-dim text-nci-primary'
                      : 'text-g-400 hover:text-white hover:bg-white/5'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="flex-1 text-left">{item.name}</span>
                  {item.isPremium && !hasPremiumAccess && (
                    <Crown className="w-4 h-4 text-nci-amber animate-pulse" />
                  )}
                </button>
              );
            })}

            <div className="glass-divider my-4"></div>

            {isAuthenticated && user ? (
              <>
                <div className="px-4 py-3 glass-card-enhanced">
                  <div className="flex items-center gap-2 mb-1">
                    <User className="w-4 h-4 text-nci-primary" />
                    <span className="text-white text-sm font-medium truncate flex-1">
                      {user.name || user.email}
                    </span>
                    {hasPremiumAccess && <Crown className="w-4 h-4 text-nci-amber" />}
                  </div>
                  {hasPremiumAccess && (
                    <p className="text-xs text-g-500 ml-6">Premium Member</p>
                  )}
                </div>
                <button
                  onClick={handleLogout}
                  className="w-full px-4 py-3 btn-secondary flex items-center gap-3 justify-center"
                  aria-label="Log out"
                >
                  <LogOut className="w-5 h-5" />
                  <span>Logout</span>
                </button>
              </>
            ) : (
              <button
                onClick={() => handleNavClick('/login')}
                className="w-full btn-primary flex items-center justify-center gap-2"
              >
                <User className="w-5 h-5" />
                <span>Get Started</span>
              </button>
            )}
          </div>
        </div>
      )}
    </nav>
  );
}
