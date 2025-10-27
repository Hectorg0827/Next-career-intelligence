'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import Logo from './Logo';
import { Menu, X } from 'lucide-react';
import { useState } from 'react';

export default function Navigation() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Don't show navigation on landing page
  if (pathname === '/') {
    return null;
  }

  const navLinks = [
    { href: '/dashboard', label: 'Dashboard' },
    { href: '/career-radar', label: '🎯 Career Radar' },
    { href: '/analyze', label: 'Analyze' },
    { href: '/coach', label: 'AI Coach' },
    { href: '/interviewer', label: 'Interview Prep' },
    { href: '/resume-studio', label: 'Resume Studio' },
    { href: '/marketplace', label: 'Jobs' },
  ];

  return (
    <nav className="sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex-shrink-0">
            <Logo size="sm" linkTo="/dashboard" />
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-6">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={`text-sm font-medium transition-colors ${
                  pathname.startsWith(link.href)
                    ? 'text-royal-blue border-b-2 border-gold-primary'
                    : 'text-gray-600 hover:text-royal-blue'
                }`}
              >
                {link.label}
              </Link>
            ))}
            
            <Link
              href="/settings"
              className="text-sm font-medium text-gray-600 hover:text-royal-blue transition-colors"
            >
              Settings
            </Link>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="text-gray-600 hover:text-royal-blue"
            >
              {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-white border-t border-gray-200">
          <div className="px-2 pt-2 pb-3 space-y-1">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setMobileMenuOpen(false)}
                className={`block px-3 py-2 rounded-md text-base font-medium ${
                  pathname.startsWith(link.href)
                    ? 'bg-royal-blue/10 text-royal-blue'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-royal-blue'
                }`}
              >
                {link.label}
              </Link>
            ))}
            <Link
              href="/settings"
              onClick={() => setMobileMenuOpen(false)}
              className="block px-3 py-2 rounded-md text-base font-medium text-gray-600 hover:bg-gray-50 hover:text-royal-blue"
            >
              Settings
            </Link>
          </div>
        </div>
      )}
    </nav>
  );
}
