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
    <nav className="bg-white/80 backdrop-blur-md border-b border-gray-100 sticky top-0 z-50">
      <div className="max-w-container container-padding">
        <div className="flex justify-between items-center py-5">
          {/* Logo */}
          <div className="flex-shrink-0">
            <Logo size="md" linkTo="/" />
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-8">
            {navItems.map((item) => {
              const isActive = pathname === item.href;
              const Icon = item.icon;

              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`px-5 py-2.5 rounded-xl font-medium transition-colors duration-200 flex items-center gap-2 group relative ${isActive
                      ? 'text-blue-600'
                      : 'text-slate-600 hover:text-slate-900'
                    }`}
                >
                  <Icon className="w-4.5 h-4.5 transition-transform group-hover:scale-110" />
                  <span className="text-base font-medium">{item.name}</span>
                  {item.isPremium && !hasPremiumAccess && (
                    <Crown className="w-3.5 h-3.5 text-blue-500" />
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
                <div className="flex items-center gap-2.5 px-5 py-2.5 text-slate-700">
                  <User className="w-4.5 h-4.5 text-slate-500" />
                  <span className="text-white text-sm font-medium max-w-[160px] truncate">
                    {user.name || user.email}
                  </span>
                  {hasPremiumAccess && <Crown className="w-4 h-4 text-blue-500" />}
                </div>

                {/* Logout Button */}
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-2 px-5 py-2.5 text-slate-600 hover:text-slate-900 transition-colors duration-200 group"
                  aria-label="Log out"
                >
                  <LogOut className="w-4.5 h-4.5 group-hover:text-slate-900 transition-colors" />
                  <span className="group-hover:text-slate-900 text-sm font-medium transition-colors">Logout</span>
                </button>
              </>
            ) : (
              <Link
                href="/login"
                className="flex items-center gap-2.5 px-8 py-3.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl transition-all duration-200 shadow-md hover:shadow-lg"
              >
                <User className="w-5 h-5 text-white" />
                <span className="text-base">Sign In</span>
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
        <div className="md:hidden border-t border-gray-100 bg-white animate-fade-in-up">
          <div className="container-padding py-6 space-y-3">
            {/* Navigation Items */}
            {navItems.map((item) => {
              const isActive = pathname === item.href;
              const Icon = item.icon;

              return (
                <button
                  key={item.name}
                  onClick={() => handleNavClick(item.href)}
                  className={`w-full px-5 py-3.5 rounded-xl font-medium transition-colors duration-200 flex items-center gap-3 ${isActive
                      ? 'text-blue-600'
                      : 'text-slate-600 hover:text-slate-900'
                    }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="flex-1 text-left">{item.name}</span>
                  {item.isPremium && !hasPremiumAccess && (
                    <Crown className="w-4.5 h-4.5 text-blue-500" />
                  )}
                </button>
              );
            })}

            {/* Divider */}
            <div className="border-t border-gray-100 my-4"></div>

            {/* User Section */}
            {isAuthenticated && user ? (
              <>
                <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-5">
                  <div className="flex items-center gap-2.5 mb-1.5">
                    <User className="w-4.5 h-4.5 text-slate-500" />
                    <span className="text-slate-700 text-sm font-medium truncate flex-1">
                      {user.name || user.email}
                    </span>
                    {hasPremiumAccess && <Crown className="w-4.5 h-4.5 text-blue-500" />}
                  </div>
                  {hasPremiumAccess && (
                    <p className="text-xs text-slate-500 ml-7">Premium Member</p>
                  )}
                </div>
                <button
                  onClick={handleLogout}
                  className="w-full px-5 py-3.5 text-slate-600 hover:text-slate-900 flex items-center gap-3 justify-center transition-colors duration-200"
                  aria-label="Log out"
                >
                  <LogOut className="w-5 h-5" />
                  <span>Logout</span>
                </button>
              </>
            ) : (
              <button
                onClick={() => handleNavClick('/login')}
                className="w-full px-8 py-3.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl shadow-md hover:shadow-lg flex items-center justify-center gap-2.5 transition-all duration-200"
              >
                <User className="w-5 h-5 text-white" />
                <span>Sign In</span>
              </button>
            )}
          </div>
        </div>
      )}
    </nav>
  );
}
