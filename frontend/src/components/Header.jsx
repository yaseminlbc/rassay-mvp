import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Bell, LogOut, Moon, Search, Sun, X } from 'lucide-react'
import { getCommandCenterNotifications } from '../services/api'
import { useAuth } from '../context/AuthContext'
import { useTheme } from '../context/ThemeContext'

const TYPE_STYLES = {
  critical: 'bg-red-50 dark:bg-red-950/50 border-red-200 dark:border-red-800 text-red-700 dark:text-red-400',
  warning:  'bg-amber-50 dark:bg-amber-950/50 border-amber-200 dark:border-amber-800 text-amber-700 dark:text-amber-400',
  info:     'bg-blue-50 dark:bg-blue-950/50 border-blue-200 dark:border-blue-800 text-blue-700 dark:text-blue-400',
}

const BADGE_STYLES = {
  critical: 'bg-red-100 dark:bg-red-900/60 text-red-700 dark:text-red-400',
  warning:  'bg-amber-100 dark:bg-amber-900/60 text-amber-700 dark:text-amber-400',
  info:     'bg-blue-100 dark:bg-blue-900/60 text-blue-700 dark:text-blue-400',
}

export default function Header({ title, subtitle }) {
  const [unreadCount, setUnreadCount] = useState(0)
  const [notifications, setNotifications] = useState([])
  const [open, setOpen] = useState(false)
  const panelRef = useRef(null)
  const { user, clearSession } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const navigate = useNavigate()

  useEffect(() => {
    getCommandCenterNotifications()
      .then(res => {
        setUnreadCount(res.unread_count || 0)
        setNotifications(res.notifications || [])
      })
      .catch(() => {})
  }, [])

  useEffect(() => {
    if (!open) return
    function handleClick(e) {
      if (panelRef.current && !panelRef.current.contains(e.target)) setOpen(false)
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [open])

  function handleLogout() {
    clearSession()
    navigate('/login', { replace: true })
  }

  const iconBtn =
    'relative inline-flex h-10 w-10 items-center justify-center rounded-md border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 transition hover:bg-slate-50 dark:hover:bg-slate-800'

  return (
    <header className="flex flex-col gap-4 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-5 py-4 sm:flex-row sm:items-center sm:justify-between lg:px-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-950 dark:text-white">{title}</h1>
        {subtitle
          ? <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{subtitle}</p>
          : null}
      </div>

      <div className="flex items-center gap-2">
        {/* Search */}
        <label className="relative hidden sm:block">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            className="h-10 w-56 rounded-md border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 pl-9 pr-3 text-sm text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 outline-none transition focus:border-blue-400 dark:focus:border-emerald-500 focus:bg-white dark:focus:bg-slate-800"
            placeholder="Search customers"
            type="search"
          />
        </label>

        {/* Dark / Light toggle */}
        <button
          type="button"
          onClick={toggleTheme}
          className={iconBtn}
          aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
          title={theme === 'dark' ? 'Light mode' : 'Dark mode'}
        >
          {theme === 'dark'
            ? <Sun className="h-4 w-4 text-emerald-400" aria-hidden="true" />
            : <Moon className="h-4 w-4" aria-hidden="true" />}
        </button>

        {/* Notification bell */}
        <div className="relative" ref={panelRef}>
          <button
            className={iconBtn}
            type="button"
            aria-label="Notifications"
            onClick={() => setOpen(o => !o)}
          >
            <Bell className="h-4 w-4" aria-hidden="true" />
            {unreadCount > 0 && (
              <span className="absolute -right-1 -top-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white">
                {unreadCount > 9 ? '9+' : unreadCount}
              </span>
            )}
          </button>

          {open && (
            <div className="absolute right-0 top-12 z-50 w-80 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 shadow-lg dark:shadow-black/40">
              <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 px-4 py-3">
                <span className="text-sm font-semibold text-slate-800 dark:text-slate-100">Notifications</span>
                <button onClick={() => setOpen(false)} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">
                  <X className="h-4 w-4" />
                </button>
              </div>

              {notifications.length === 0 ? (
                <p className="px-4 py-6 text-center text-sm text-slate-400">No notifications</p>
              ) : (
                <ul className="max-h-96 divide-y divide-slate-100 dark:divide-slate-800 overflow-y-auto">
                  {notifications.map(n => (
                    <li key={n.id} className={`border-l-4 px-4 py-3 ${TYPE_STYLES[n.type] ?? TYPE_STYLES.info}`}>
                      <div className="flex items-center gap-2">
                        <span className={`rounded px-1.5 py-0.5 text-[10px] font-semibold uppercase ${BADGE_STYLES[n.type] ?? BADGE_STYLES.info}`}>
                          {n.type}
                        </span>
                        <p className="text-xs font-semibold">{n.title}</p>
                      </div>
                      <p className="mt-1 text-xs leading-relaxed opacity-80">{n.message}</p>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </div>

        {/* User + Logout */}
        {user && (
          <div className="flex items-center gap-2 border-l border-slate-200 dark:border-slate-700 pl-2">
            <span className="hidden max-w-36 truncate text-xs text-slate-500 dark:text-slate-400 sm:block">
              {user.email}
            </span>
            <button
              type="button"
              onClick={handleLogout}
              className="inline-flex h-10 w-10 items-center justify-center rounded-md border border-slate-200 dark:border-slate-700 text-slate-500 dark:text-slate-400 transition hover:border-red-200 dark:hover:border-red-800 hover:bg-red-50 dark:hover:bg-red-950/40 hover:text-red-600 dark:hover:text-red-400"
              aria-label="Sign out"
              title="Sign out"
            >
              <LogOut className="h-4 w-4" aria-hidden="true" />
            </button>
          </div>
        )}
      </div>
    </header>
  )
}
