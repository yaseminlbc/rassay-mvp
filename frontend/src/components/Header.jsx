import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Bell, LogOut, Search, X } from 'lucide-react'
import { getCommandCenterNotifications } from '../services/api'
import { useAuth } from '../context/AuthContext'

const TYPE_STYLES = {
  critical: 'bg-red-50 border-red-200 text-red-700',
  warning:  'bg-amber-50 border-amber-200 text-amber-700',
  info:     'bg-blue-50 border-blue-200 text-blue-700',
}

const BADGE_STYLES = {
  critical: 'bg-red-100 text-red-700',
  warning:  'bg-amber-100 text-amber-700',
  info:     'bg-blue-100 text-blue-700',
}

export default function Header({ title, subtitle }) {
  const [unreadCount, setUnreadCount] = useState(0)
  const [notifications, setNotifications] = useState([])
  const [open, setOpen] = useState(false)
  const panelRef = useRef(null)
  const { user, clearSession } = useAuth()
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

  return (
    <header className="flex flex-col gap-4 border-b border-slate-200 bg-white px-5 py-4 sm:flex-row sm:items-center sm:justify-between lg:px-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-950">{title}</h1>
        {subtitle ? <p className="mt-1 text-sm text-slate-500">{subtitle}</p> : null}
      </div>

      <div className="flex items-center gap-3">
        <label className="relative hidden sm:block">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            className="h-10 w-64 rounded-md border border-slate-200 bg-slate-50 pl-9 pr-3 text-sm outline-none transition focus:border-blue-400 focus:bg-white"
            placeholder="Search customers"
            type="search"
          />
        </label>

        {/* Notification bell */}
        <div className="relative" ref={panelRef}>
          <button
            className="relative inline-flex h-10 w-10 items-center justify-center rounded-md border border-slate-200 text-slate-600 hover:bg-slate-50"
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
            <div className="absolute right-0 top-12 z-50 w-80 rounded-lg border border-slate-200 bg-white shadow-lg">
              <div className="flex items-center justify-between border-b border-slate-100 px-4 py-3">
                <span className="text-sm font-semibold text-slate-800">Notifications</span>
                <button onClick={() => setOpen(false)} className="text-slate-400 hover:text-slate-600">
                  <X className="h-4 w-4" />
                </button>
              </div>

              {notifications.length === 0 ? (
                <p className="px-4 py-6 text-center text-sm text-slate-400">No notifications</p>
              ) : (
                <ul className="max-h-96 overflow-y-auto divide-y divide-slate-100">
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
          <div className="flex items-center gap-2 border-l border-slate-200 pl-3">
            <span className="hidden max-w-35 truncate text-xs text-slate-500 sm:block">
              {user.email}
            </span>
            <button
              type="button"
              onClick={handleLogout}
              className="inline-flex h-10 w-10 items-center justify-center rounded-md border border-slate-200 text-slate-500 transition hover:border-red-200 hover:bg-red-50 hover:text-red-600"
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
