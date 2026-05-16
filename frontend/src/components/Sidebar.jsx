import { BarChart3, Link2, School, Settings, Upload } from 'lucide-react'
import { NavLink } from 'react-router-dom'

const navItems = [
  { to: '/',            label: 'Dashboard',   icon: BarChart3 },
  { to: '/import',      label: 'Data Import', icon: Upload    },
  { to: '/integrations',label: 'Integrations',icon: Link2     },
  { to: '/settings',    label: 'Settings',    icon: Settings  },
]

export default function Sidebar() {
  return (
    <aside className="hidden min-h-screen w-64 shrink-0 border-r border-slate-800 bg-slate-950 px-4 py-5 text-white lg:flex lg:flex-col">
      {/* Logo */}
      <div className="flex items-center gap-3 px-2">
        <div className="rounded-lg bg-blue-500 p-2 dark:bg-emerald-500/20 dark:ring-1 dark:ring-emerald-500/40">
          <School className="h-5 w-5 dark:text-emerald-400" aria-hidden="true" />
        </div>
        <div>
          <p className="text-lg font-bold tracking-tight">RASSAY</p>
          <p className="text-xs text-slate-400">Churn Intelligence</p>
        </div>
      </div>

      {/* Nav */}
      <nav className="mt-8 flex-1 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition ${
                isActive
                  ? 'bg-white text-slate-950 dark:bg-emerald-500/20 dark:text-emerald-400 dark:ring-1 dark:ring-emerald-500/30'
                  : 'text-slate-300 hover:bg-slate-800 dark:hover:bg-slate-800'
              }`
            }
          >
            <item.icon className="h-4 w-4 shrink-0" aria-hidden="true" />
            {item.label}
          </NavLink>
        ))}
      </nav>

      {/* Bottom label */}
      <p className="px-3 text-[10px] font-medium uppercase tracking-widest text-slate-600">
        v1.0 · RASSAY AI
      </p>
    </aside>
  )
}
