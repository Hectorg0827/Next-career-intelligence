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
    <footer className="relative mt-20 border-t border-white/5 bg-black/40 backdrop-blur-xl">
      {/* Background Glow */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute bottom-0 left-1/4 w-[500px] h-[500px] bg-royal-blue/10 rounded-full blur-[100px]" />
        <div className="absolute top-0 right-1/4 w-[500px] h-[500px] bg-gold-primary/5 rounded-full blur-[100px]" />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        {/* Main Footer Content */}
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-12 mb-16">
          {/* Brand Column */}
          <div className="col-span-2 md:col-span-4 lg:col-span-1 space-y-6">
            <Logo size="md" linkTo="/" />
            <p className="text-white/60 text-sm leading-relaxed max-w-xs">
              AI-powered career intelligence platform helping professionals future-proof their careers in the age of automation.
            </p>

            {/* Social Links */}
            <div className="flex items-center gap-4">
              {socialLinks.map((social) => {
                const Icon = social.icon;
                return (
                  <a
                    key={social.name}
                    href={social.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={`p-2 rounded-lg bg-white/5 hover:bg-white/10 text-white/60 ${social.color} transition-all duration-300 hover:scale-110`}
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
            <h3 className="text-white font-semibold mb-6 text-sm uppercase tracking-widest text-transparent bg-clip-text bg-gradient-to-r from-white to-white/70">Product</h3>
            <ul className="space-y-4">
              {footerLinks.product.map((link) => (
                <li key={link.name}>
                  <Link
                    href={link.href}
                    className="text-white/60 hover:text-gold-primary transition-colors text-sm font-medium flex items-center gap-2 group"
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-gold-primary/0 group-hover:bg-gold-primary transition-all duration-300" />
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Company Links */}
          <div>
            <h3 className="text-white font-semibold mb-6 text-sm uppercase tracking-widest text-transparent bg-clip-text bg-gradient-to-r from-white to-white/70">Company</h3>
            <ul className="space-y-4">
              {footerLinks.company.map((link) => (
                <li key={link.name}>
                  <Link
                    href={link.href}
                    className="text-white/60 hover:text-gold-primary transition-colors text-sm font-medium flex items-center gap-2 group"
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-gold-primary/0 group-hover:bg-gold-primary transition-all duration-300" />
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Resources Links */}
          <div>
            <h3 className="text-white font-semibold mb-6 text-sm uppercase tracking-widest text-transparent bg-clip-text bg-gradient-to-r from-white to-white/70">Resources</h3>
            <ul className="space-y-4">
              {footerLinks.resources.map((link) => (
                <li key={link.name}>
                  <Link
                    href={link.href}
                    className="text-white/60 hover:text-gold-primary transition-colors text-sm font-medium flex items-center gap-2 group"
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-gold-primary/0 group-hover:bg-gold-primary transition-all duration-300" />
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Legal Links */}
          <div>
            <h3 className="text-white font-semibold mb-6 text-sm uppercase tracking-widest text-transparent bg-clip-text bg-gradient-to-r from-white to-white/70">Legal</h3>
            <ul className="space-y-4">
              {footerLinks.legal.map((link) => (
                <li key={link.name}>
                  <Link
                    href={link.href}
                    className="text-white/60 hover:text-gold-primary transition-colors text-sm font-medium flex items-center gap-2 group"
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-gold-primary/0 group-hover:bg-gold-primary transition-all duration-300" />
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-8 border-t border-white/10">
          <div className="flex flex-col md:flex-row justify-between items-center gap-6">
            {/* Copyright */}
            <p className="text-white/40 text-sm font-medium">
              © {currentYear} NEXT Career Intelligence. All rights reserved.
            </p>

            {/* Built with Love */}
            <div className="flex items-center gap-6">
              <p className="text-white/40 text-sm font-medium flex items-center gap-2">
                Built for <span className="text-gold-primary">career resilience</span>
              </p>

              {/* Trust Badge */}
              <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-green-500/10 border border-green-500/20 text-green-400 text-xs font-medium">
                <div className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse" />
                <span>Systems Operational</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
