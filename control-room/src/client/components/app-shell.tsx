import {
  LayoutDashboard,
  ShoppingCart,
  Cpu,
  Code,
  Smartphone,
  Car,
  Box,
  FolderOpen,
  Clock,
  Settings,
} from 'lucide-react';
import type { ReactNode } from 'react';

const NAV_ITEMS = [
  { id: 'mission-control', label: 'Mission Control', icon: LayoutDashboard },
  { id: 'ordering', label: 'Rev2 Ordering', icon: ShoppingCart },
  { id: 'hardware', label: 'Hardware', icon: Cpu },
  { id: 'firmware', label: 'Firmware', icon: Code },
  { id: 'mobile', label: 'Mobile App', icon: Smartphone },
  { id: 'automotive', label: 'Automotive System', icon: Car },
  { id: '3d-viewer', label: '3D Board Viewer', icon: Box },
  { id: 'files', label: 'Files & Documents', icon: FolderOpen },
  { id: 'activity', label: 'Activity History', icon: Clock },
  { id: 'settings', label: 'Settings', icon: Settings },
] as const;

export type PageId = (typeof NAV_ITEMS)[number]['id'];

interface AppShellProps {
  active: PageId;
  onNavigate: (page: PageId) => void;
  children: ReactNode;
}

export function AppShell({ active, onNavigate, children }: AppShellProps) {
  return (
    <div className="app-layout">
      <nav className="sidebar" aria-label="Main navigation">
        <div className="sidebar-brand">
          <h1>SafeSwitch</h1>
          <p>Control Room</p>
        </div>
        {NAV_ITEMS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            className="nav-btn"
            aria-current={active === id ? 'true' : undefined}
            onClick={() => onNavigate(id)}
          >
            <Icon size={16} />
            {label}
          </button>
        ))}
      </nav>
      <main className="main-content">{children}</main>
    </div>
  );
}
