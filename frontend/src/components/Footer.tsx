'use client';

import Link from 'next/link';
import { Github, Twitter, Linkedin, Mail, ArrowRight } from 'lucide-react';
import Logo from '@/components/Logo';

const footerLinks = {
  platform: [
    { name: 'Career Analysis', href: '/#analyze' },
    { name: 'Market Intelligence', href: '/dashboard' },
    { name: 'AI Career Coach', href: '/coach/chat' },
    { name: 'Skill Gap Analysis', href: '/dashboard' },
  ],
  company: [
    { name: 'About NextCI', href: '/about' },
    { name: 'Methodology', href: '/methodology' },
    { name: 'Success Stories', href: '/#testimonials' },
    { name: 'Pricing', href: '/pricing' },
  ],
  legal: [
    { name: 'Privacy Policy', href: '/privacy' },
    { name: 'Terms of Service', href: '/terms' },
    { name: 'Security', href: '/security' },
  ],
};

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-premium-bg border-t border-premium-accent/10 pt-20 pb-10">
      <div className="max-w-7xl mx-auto px-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-12 mb-20">
          {/* Brand & Newsletter */}
          <div className="lg:col-span-2">
            <Logo size="md" linkTo="/" />
            <p className="mt-6 text-premium-text-muted max-w-sm leading-relaxed">
              The world's first AI-driven career intelligence engine. We help elite professionals navigate the future of work with precision and data-backed confidence.
            </p>
            
            <div className="mt-8">
              <h4 className="text-white font-bold mb-4">Stay ahead of the curve</h4>
              <div className="flex gap-2 max-w-md">
                <input 
                  type="email" 
                  placeholder="Email address" 
                  className="bg-white/5 border border-white/10 rounded-lg px-4 py-2 flex-1 text-sm focus:outline-none focus:border-premium-accent transition-colors"
                />
                <button className="bg-premium-accent text-premium-primary px-4 py-2 rounded-lg font-bold text-sm hover:bg-white transition-colors">
                  Join
                </button>
              </div>
            </div>
          </div>

          {/* Links */}
          <div>
            <h4 className="text-white font-bold mb-6">Platform</h4>
            <ul className="space-y-4">
              {footerLinks.platform.map((link) => (
                <li key={link.name}>
                  <Link href={link.href} className="text-premium-text-muted hover:text-premium-accent transition-colors text-sm">
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h4 className="text-white font-bold mb-6">Company</h4>
            <ul className="space-y-4">
              {footerLinks.company.map((link) => (
                <li key={link.name}>
                  <Link href={link.href} className="text-premium-text-muted hover:text-premium-accent transition-colors text-sm">
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h4 className="text-white font-bold mb-6">Legal</h4>
            <ul className="space-y-4">
              {footerLinks.legal.map((link) => (
                <li key={link.name}>
                  <Link href={link.href} className="text-premium-text-muted hover:text-premium-accent transition-colors text-sm">
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-10 border-t border-white/5 flex flex-col md:flex-row justify-between items-center gap-6">
          <p className="text-premium-text-muted text-xs">
            © {currentYear} NextCI Intelligence Systems. All rights reserved.
          </p>
          
          <div className="flex items-center gap-6">
            <a href="#" className="text-premium-text-muted hover:text-white transition-colors">
              <Twitter className="w-5 h-5" />
            </a>
            <a href="#" className="text-premium-text-muted hover:text-white transition-colors">
              <Linkedin className="w-5 h-5" />
            </a>
            <a href="#" className="text-premium-text-muted hover:text-white transition-colors">
              <Github className="w-5 h-5" />
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
