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
    <nav className="nav-glass sticky top-0 z-50">
      <div className="max-w-container container-padding">
        <div className="flex justify-between items-center h-20">
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
                  className={`px-5 py-2.5 rounded-xl font-medium transition-all duration-200 flex items-center gap-2 group relative ${
                    isActive
                      ? 'bg-white/15 text-white shadow-lg'
                      : 'text-white/70 hover:text-white hover:bg-white/10'
                  }`}
                >
                  <Icon className="w-4.5 h-4.5 transition-transform group-hover:scale-110" />
                  <span className="text-sm">{item.name}</span>
                  {item.isPremium && !hasPremiumAccess && (
                    <Crown className="w-3.5 h-3.5 text-gold-primary animate-pulse" />
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
                <div className="flex items-center gap-2.5 px-5 py-2.5 bg-white/10 backdrop-blur-md rounded-full border border-white/20 shadow-lg">
                  <User className="w-4.5 h-4.5 text-primary-500" />
                  <span className="text-white text-sm font-medium max-w-[160px] truncate">
                    {user.name || user.email}
                  </span>
                  {hasPremiumAccess && <Crown className="w-4 h-4 text-gold-primary animate-pulse" />}
                </div>

                {/* Logout Button */}
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-2 px-5 py-2.5 bg-white/10 hover:bg-white/15 backdrop-blur-md rounded-full border border-white/20 transition-all duration-200 group shadow-lg hover:shadow-xl"
                  aria-label="Log out"
                >
                  <LogOut className="w-4.5 h-4.5 text-white/70 group-hover:text-white transition-colors" />
                  <span className="text-white/70 group-hover:text-white text-sm font-medium transition-colors">Logout</span>
                </button>
              </>
            ) : (
              <Link
                href="/login"
                className="btn-primary flex items-center gap-2"
              >
                <User className="w-4.5 h-4.5" />
                <span>Sign In</span>
              </Link>
            )}
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="p-2.5 rounded-xl text-white/70 hover:text-white hover:bg-white/10 transition-all duration-200"
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
        <div className="md:hidden border-t border-glass nav-glass animate-fade-in-up">
          <div className="container-padding py-6 space-y-3">
            {/* Navigation Items */}
            {navItems.map((item) => {
              const isActive = pathname === item.href;
              const Icon = item.icon;

              return (
                <button
                  key={item.name}
                  onClick={() => handleNavClick(item.href)}
                  className={`w-full px-5 py-3.5 rounded-xl font-medium transition-all duration-200 flex items-center gap-3 ${
                    isActive
                      ? 'bg-white/15 text-white shadow-lg'
                      : 'text-white/70 hover:text-white hover:bg-white/10'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="flex-1 text-left">{item.name}</span>
                  {item.isPremium && !hasPremiumAccess && (
                    <Crown className="w-4.5 h-4.5 text-gold-primary animate-pulse" />
                  )}
                </button>
              );
            })}

            {/* Divider */}
            <div className="glass-divider my-4"></div>

            {/* User Section */}
            {isAuthenticated && user ? (
              <>
                <div className="px-5 py-3.5 glass-card-enhanced">
                  <div className="flex items-center gap-2.5 mb-1.5">
                    <User className="w-4.5 h-4.5 text-primary-500" />
                    <span className="text-white text-sm font-medium truncate flex-1">
                      {user.name || user.email}
                    </span>
                    {hasPremiumAccess && <Crown className="w-4.5 h-4.5 text-gold-primary animate-pulse" />}
                  </div>
                  {hasPremiumAccess && (
                    <p className="text-xs text-white/60 ml-7">Premium Member</p>
                  )}
                </div>
                <button
                  onClick={handleLogout}
                  className="w-full px-5 py-3.5 btn-secondary flex items-center gap-3 justify-center"
                  aria-label="Log out"
                >
                  <LogOut className="w-5 h-5" />
                  <span>Logout</span>
                </button>
              </>
            ) : (
              <button
                onClick={() => handleNavClick('/login')}
                className="w-full btn-primary flex items-center justify-center gap-2.5"
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
