import { BarChart3, Link2, School, Upload } from 'lucide-react'
import { NavLink } from 'react-router-dom'

const navItems = [
  { to: '/', label: 'Dashboard', icon: BarChart3 },
  { to: '/import', label: 'Data Import', icon: Upload },
  { to: '/integrations', label: 'Integrations', icon: Link2 },
]

export default function Sidebar() {
  return (
    <aside className="hidden min-h-screen w-64 border-r border-slate-200 bg-slate-950 px-4 py-5 text-white lg:block">
      <div className="flex items-center gap-3 px-2">
        <div className="rounded-lg bg-blue-500 p-2">
          <School className="h-5 w-5" aria-hidden="true" />
        </div>
        <div>
          <p className="text-lg font-bold">RASSAY</p>
          <p className="text-xs text-slate-400">Churn Intelligence</p>
        </div>
      </div>

      <nav className="mt-8 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition ${
                isActive ? 'bg-white text-slate-950' : 'text-slate-300 hover:bg-slate-800'
              }`
            }
          >
            <item.icon className="h-4 w-4" aria-hidden="true" />
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
