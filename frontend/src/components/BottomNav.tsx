'use client';

import { usePathname, useRouter } from 'next/navigation';
import { HomeIcon, ChartBarIcon, BriefcaseIcon, UserIcon } from '@heroicons/react/24/outline';
import { HomeIcon as HomeIconSolid, ChartBarIcon as ChartBarIconSolid, BriefcaseIcon as BriefcaseIconSolid, UserIcon as UserIconSolid } from '@heroicons/react/24/solid';

interface TabItem {
  name: string;
  path: string;
  icon: React.ComponentType<{ className?: string }>;
  iconSolid: React.ComponentType<{ className?: string }>;
}

const tabs: TabItem[] = [
  { name: 'Home', path: '/', icon: HomeIcon, iconSolid: HomeIconSolid },
  { name: 'Health', path: '/career-radar', icon: ChartBarIcon, iconSolid: ChartBarIconSolid },
  { name: 'Jobs', path: '/jobs', icon: BriefcaseIcon, iconSolid: BriefcaseIconSolid },
  { name: 'Profile', path: '/settings', icon: UserIcon, iconSolid: UserIconSolid },
];

export default function BottomNav() {
  const pathname = usePathname();
  const router = useRouter();

  const isActive = (path: string) => {
    if (path === '/') return pathname === '/';
    return pathname.startsWith(path);
  };

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 md:hidden">
      <div className="glass-card border-t border-glass-line rounded-none">
        <div className="flex h-16">
          {tabs.map((tab) => {
            const active = isActive(tab.path);
            const Icon = active ? tab.iconSolid : tab.icon;

            return (
              <button
                key={tab.path}
                onClick={() => router.push(tab.path)}
                className={`flex flex-col items-center justify-center flex-1 transition-colors ${
                  active ? 'text-primary-500' : 'text-ink-400 hover:text-white'
                }`}
                aria-label={`Navigate to ${tab.name}`}
                aria-current={active ? 'page' : undefined}
              >
                <Icon className="w-6 h-6" />
                <span className="text-xs mt-1 font-medium">{tab.name}</span>
              </button>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
