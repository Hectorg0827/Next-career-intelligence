import React from 'react';
import Link from 'next/link';
import { ArrowRight, Sparkles, TrendingUp, ShieldCheck } from 'lucide-react';
import { Button } from '@/components/ui/button';

export const EnhancedHeroSection = () => {
  return (
    <div className="relative overflow-hidden bg-white dark:bg-slate-950 pt-24 pb-32">
      {/* Subtle Background Pattern (Optional, keeps it clean) */}
      <div className="absolute inset-0 -z-10 h-full w-full bg-[linear-gradient(to_right,#f0f0f0_1px,transparent_1px),linear-gradient(to_bottom,#f0f0f0_1px,transparent_1px)] bg-[size:6rem_4rem] opacity-[0.4] dark:opacity-[0.1]" />
      
      <div className="container px-4 md:px-6 mx-auto max-w-6xl">
        <div className="flex flex-col items-center text-center space-y-8">
          
          {/* Badge */}
          <div className="inline-flex items-center rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-sm font-medium text-slate-800 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-200">
            <span className="flex h-2 w-2 rounded-full bg-blue-600 mr-2"></span>
            Now with AI Agent Support
          </div>

          {/* Headline - Clean & Huge */}
          <h1 className="text-4xl font-bold tracking-tight text-slate-900 sm:text-6xl dark:text-white max-w-4xl">
            Master Your Career <br className="hidden md:block" />
            <span className="text-blue-600">With Real-Time Intelligence</span>
          </h1>

          {/* Subheadline - Readable Gray */}
          <p className="max-w-2xl text-xl text-slate-600 dark:text-slate-400">
            Stop guessing. NextCI analyzes real-time market data to protect your role, predict trends, and guide your next promotion.
          </p>

          {/* Action Buttons - Solid Colors */}
          <div className="flex flex-col sm:flex-row gap-4 w-full justify-center pt-4">
            <Link href="/auth/signup">
              <Button size="lg" className="w-full sm:w-auto h-12 px-8 text-base bg-blue-600 hover:bg-blue-700 text-white shadow-lg shadow-blue-600/20">
                Get Started Free <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
            <Link href="/about">
              <Button variant="outline" size="lg" className="w-full sm:w-auto h-12 px-8 text-base border-slate-200 hover:bg-slate-50">
                View Live Demo
              </Button>
            </Link>
          </div>

          {/* Social Proof / Stats - Clean Row */}
          <div className="pt-12 grid grid-cols-1 gap-8 sm:grid-cols-3 text-left w-full max-w-3xl border-t border-slate-100 mt-12 dark:border-slate-800">
            <div className="flex items-center gap-4">
              <div className="p-2 bg-blue-50 rounded-lg text-blue-600 dark:bg-blue-900/20"><TrendingUp size={24} /></div>
              <div>
                <p className="font-bold text-2xl text-slate-900 dark:text-white">94%</p>
                <p className="text-sm text-slate-500">Accuracy Rate</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="p-2 bg-purple-50 rounded-lg text-purple-600 dark:bg-purple-900/20"><Sparkles size={24} /></div>
              <div>
                <p className="font-bold text-2xl text-slate-900 dark:text-white">24/7</p>
                <p className="text-sm text-slate-500">AI Career Monitoring</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="p-2 bg-green-50 rounded-lg text-green-600 dark:bg-green-900/20"><ShieldCheck size={24} /></div>
              <div>
                <p className="font-bold text-2xl text-slate-900 dark:text-white">100k+</p>
                <p className="text-sm text-slate-500">Jobs Analyzed</p>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};