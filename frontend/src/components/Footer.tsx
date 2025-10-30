'use client';

import Link from 'next/link';
import { Github, Twitter, Linkedin, Mail } from 'lucide-react';
import Logo from '@/components/Logo';

const footerLinks = {
  product: [
    { name: 'Career Analysis', href: '/' },
    { name: 'Dashboard', href: '/dashboard' },
    { name: 'AI Coach', href: '/coach/chat' },
    { name: 'Interview Prep', href: '/interviewer/practice' },
  ],
  company: [
    { name: 'About Us', href: '/about' },
    { name: 'How It Works', href: '/#how-it-works' },
    { name: 'Success Stories', href: '/success-stories' },
    { name: 'Pricing', href: '/pricing' },
  ],
  resources: [
    { name: 'Blog', href: '/blog' },
    { name: 'Career Guides', href: '/guides' },
    { name: 'API Documentation', href: '/docs' },
    { name: 'Help Center', href: '/help' },
  ],
  legal: [
    { name: 'Privacy Policy', href: '/privacy' },
    { name: 'Terms of Service', href: '/terms' },
    { name: 'Cookie Policy', href: '/cookies' },
    { name: 'GDPR', href: '/gdpr' },
  ],
};

const socialLinks = [
  { name: 'Twitter', icon: Twitter, href: 'https://twitter.com/nextci', color: 'hover:text-blue-400' },
  { name: 'LinkedIn', icon: Linkedin, href: 'https://linkedin.com/company/nextci', color: 'hover:text-blue-600' },
  { name: 'GitHub', icon: Github, href: 'https://github.com/nextci', color: 'hover:text-gray-400' },
  { name: 'Email', icon: Mail, href: 'mailto:hello@nextci.net', color: 'hover:text-gold-primary' },
];

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gradient-to-br from-royal-navy via-royal-blue-deep to-royal-navy border-t border-white/10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Main Footer Content */}
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-8 mb-12">
          {/* Brand Column */}
          <div className="col-span-2 md:col-span-4 lg:col-span-1">
            <Logo size="md" linkTo="/" />
            <p className="mt-4 text-white/70 text-sm leading-relaxed">
              AI-powered career intelligence platform helping professionals future-proof their careers.
            </p>
            
            {/* Social Links */}
            <div className="flex items-center gap-4 mt-6">
              {socialLinks.map((social) => {
                const Icon = social.icon;
                return (
                  <a
                    key={social.name}
                    href={social.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={`text-white/60 ${social.color} transition-colors`}
                    aria-label={social.name}
                  >
                    <Icon className="w-5 h-5" />
                  </a>
                );
              })}
            </div>
          </div>

          {/* Product Links */}
          <div>
            <h3 className="text-white font-semibold mb-4 text-sm uppercase tracking-wider">Product</h3>
            <ul className="space-y-3">
              {footerLinks.product.map((link) => (
                <li key={link.name}>
                  <Link
                    href={link.href}
                    className="text-white/70 hover:text-gold-primary transition-colors text-sm"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Company Links */}
          <div>
            <h3 className="text-white font-semibold mb-4 text-sm uppercase tracking-wider">Company</h3>
            <ul className="space-y-3">
              {footerLinks.company.map((link) => (
                <li key={link.name}>
                  <Link
                    href={link.href}
                    className="text-white/70 hover:text-gold-primary transition-colors text-sm"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Resources Links */}
          <div>
            <h3 className="text-white font-semibold mb-4 text-sm uppercase tracking-wider">Resources</h3>
            <ul className="space-y-3">
              {footerLinks.resources.map((link) => (
                <li key={link.name}>
                  <Link
                    href={link.href}
                    className="text-white/70 hover:text-gold-primary transition-colors text-sm"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Legal Links */}
          <div>
            <h3 className="text-white font-semibold mb-4 text-sm uppercase tracking-wider">Legal</h3>
            <ul className="space-y-3">
              {footerLinks.legal.map((link) => (
                <li key={link.name}>
                  <Link
                    href={link.href}
                    className="text-white/70 hover:text-gold-primary transition-colors text-sm"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-8 border-t border-white/10">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            {/* Copyright */}
            <p className="text-white/60 text-sm">
              © {currentYear} NEXT Career Intelligence. All rights reserved.
            </p>

            {/* Built with Love */}
            <p className="text-white/60 text-sm flex items-center gap-2">
              Built with <span className="text-red-400">❤️</span> for career resilience
            </p>

            {/* Trust Badge */}
            <div className="flex items-center gap-2 text-white/60 text-xs">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span>Trusted by 15,000+ professionals</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
