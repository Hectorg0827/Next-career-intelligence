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
    <nav className="bg-gradient-to-r from-royal-navy via-royal-blue-deep to-royal-navy border-b border-white/10 sticky top-0 z-50 backdrop-blur-md bg-opacity-95">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex-shrink-0">
            <Logo size="sm" linkTo="/" />
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => {
              const isActive = pathname === item.href;
              const Icon = item.icon;
              
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`px-4 py-2 rounded-lg font-medium transition-all flex items-center gap-2 group relative ${
                    isActive
                      ? 'bg-white/10 text-white'
                      : 'text-white/70 hover:text-white hover:bg-white/5'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.name}</span>
                  {item.isPremium && !hasPremiumAccess && (
                    <Crown className="w-3 h-3 text-gold-primary" />
                  )}
                </Link>
              );
            })}
          </div>

          {/* Desktop User Menu */}
          <div className="hidden md:flex items-center gap-3">
            {isAuthenticated && user ? (
              <>
                {/* User Info */}
                <div className="flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-md rounded-full border border-white/20">
                  <User className="w-4 h-4 text-gold-primary" />
                  <span className="text-white text-sm font-medium max-w-[150px] truncate">
                    {user.name || user.email}
                  </span>
                  {hasPremiumAccess && <Crown className="w-4 h-4 text-gold-primary" />}
                </div>
                
                {/* Logout Button */}
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 backdrop-blur-md rounded-full border border-white/20 transition-all group"
                  aria-label="Log out"
                >
                  <LogOut className="w-4 h-4 text-white/70 group-hover:text-white" />
                  <span className="text-white/70 group-hover:text-white text-sm font-medium">Logout</span>
                </button>
              </>
            ) : (
              <Link
                href="/login"
                className="flex items-center gap-2 px-6 py-2.5 bg-gradient-to-r from-gold-primary to-gold-accent hover:from-gold-accent hover:to-gold-hover text-royal-navy font-semibold rounded-xl transition-all shadow-lg hover:shadow-xl"
              >
                <User className="w-4 h-4" />
                <span>Sign In</span>
              </Link>
            )}
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="p-2 rounded-lg text-white/70 hover:text-white hover:bg-white/10 transition-all"
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
        <div className="md:hidden border-t border-white/10 bg-royal-navy/95 backdrop-blur-md animate-fade-in">
          <div className="px-4 py-4 space-y-2">
            {/* Navigation Items */}
            {navItems.map((item) => {
              const isActive = pathname === item.href;
              const Icon = item.icon;
              
              return (
                <button
                  key={item.name}
                  onClick={() => handleNavClick(item.href)}
                  className={`w-full px-4 py-3 rounded-lg font-medium transition-all flex items-center gap-3 ${
                    isActive
                      ? 'bg-white/10 text-white'
                      : 'text-white/70 hover:text-white hover:bg-white/5'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="flex-1 text-left">{item.name}</span>
                  {item.isPremium && !hasPremiumAccess && (
                    <Crown className="w-4 h-4 text-gold-primary" />
                  )}
                </button>
              );
            })}

            {/* Divider */}
            <div className="h-px bg-white/10 my-4"></div>

            {/* User Section */}
            {isAuthenticated && user ? (
              <>
                <div className="px-4 py-2 bg-white/5 rounded-lg border border-white/10">
                  <div className="flex items-center gap-2 mb-1">
                    <User className="w-4 h-4 text-gold-primary" />
                    <span className="text-white text-sm font-medium truncate">
                      {user.name || user.email}
                    </span>
                    {hasPremiumAccess && <Crown className="w-4 h-4 text-gold-primary" />}
                  </div>
                  {hasPremiumAccess && (
                    <p className="text-xs text-white/60 ml-6">Premium Member</p>
                  )}
                </div>
                <button
                  onClick={handleLogout}
                  className="w-full px-4 py-3 bg-white/10 hover:bg-white/20 text-white font-medium rounded-lg transition-all flex items-center gap-3"
                  aria-label="Log out"
                >
                  <LogOut className="w-5 h-5" />
                  <span>Logout</span>
                </button>
              </>
            ) : (
              <button
                onClick={() => handleNavClick('/login')}
                className="w-full px-4 py-3 bg-gradient-to-r from-gold-primary to-gold-accent text-royal-navy font-semibold rounded-lg transition-all flex items-center justify-center gap-2 shadow-lg"
              >
                <User className="w-5 h-5" />
                <span>Sign In</span>
              </button>
            )}
          </div>
        </div>
      )}
    </nav>
  );
}
