'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  TrendingUp,
  BarChart3,
  Briefcase,
  Cpu,
  Settings,
  LogOut,
} from 'lucide-react';
import { Button, buttonVariants } from '@/components/ui/button';

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Predictions', href: '/predictions', icon: TrendingUp },
  { name: 'Analysis', href: '/analysis', icon: BarChart3 },
  { name: 'Portfolio', href: '/portfolio', icon: Briefcase },
  { name: 'Agents', href: '/agents', icon: Cpu },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="fixed left-0 top-0 h-screen w-64 bg-card border-r border-border flex flex-col">
      <div className="p-6 border-b border-border">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 rounded-lg bg-primary flex items-center justify-center">
            <Cpu className="w-6 h-6 text-primary-foreground" />
          </div>
          <div>
            <h1 className="font-bold text-foreground">Hermes</h1>
            <p className="text-xs text-muted-foreground">Crypto Predictor</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 overflow-y-auto px-4 py-6 space-y-2">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={buttonVariants({
                variant: isActive ? 'default' : 'ghost',
                className: `w-full justify-start gap-3 ${
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'text-foreground hover:bg-border'
                }`
              })}
            >
              <item.icon className="w-5 h-5" />
              {item.name}
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-border space-y-2">
        <Button variant="ghost" className="w-full justify-start gap-3 text-muted-foreground hover:text-foreground">
          <LogOut className="w-5 h-5" />
          Logout
        </Button>
      </div>
    </div>
  );
}
