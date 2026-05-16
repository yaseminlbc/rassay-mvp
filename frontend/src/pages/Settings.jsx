import { useState } from 'react'
import {
  Check,
  Copy,
  CreditCard,
  Database,
  Eye,
  EyeOff,
  KeyRound,
  MessageSquare,
  Moon,
  Save,
  ShieldCheck,
  Sun,
  User,
} from 'lucide-react'
import Header from '../components/Header'
import Sidebar from '../components/Sidebar'
import { useAuth } from '../context/AuthContext'
import { useTheme } from '../context/ThemeContext'

const INTEGRATIONS = [
  {
    id: 'stripe',
    icon: CreditCard,
    name: 'Stripe',
    description: 'Sync MRR, subscription lifecycle, and payment events into RASSAY.',
    label: 'Secret API Key',
    placeholder: 'sk_live_••••••••••••••••••••••••••',
    storageKey: 'rassay_stripe_key',
    accentLight: 'bg-blue-50 text-blue-700',
    accentDark: 'dark:bg-blue-500/10 dark:text-blue-400',
  },
  {
    id: 'slack',
    icon: MessageSquare,
    name: 'Slack',
    description: 'Push real-time churn alerts and daily digests to your workspace.',
    label: 'Incoming Webhook URL',
    placeholder: 'https://hooks.slack.com/services/T00/B00/XXXX',
    storageKey: 'rassay_slack_webhook',
    accentLight: 'bg-purple-50 text-purple-700',
    accentDark: 'dark:bg-purple-500/10 dark:text-purple-400',
  },
  {
    id: 'segment',
    icon: Database,
    name: 'Segment',
    description: 'Pipe behavioral events from Segment into the prediction pipeline.',
    label: 'Write Key',
    placeholder: 'seg_live_••••••••••••••••',
    storageKey: 'rassay_segment_key',
    accentLight: 'bg-emerald-50 text-emerald-700',
    accentDark: 'dark:bg-emerald-500/10 dark:text-emerald-400',
  },
]

export default function Settings() {
  const { user } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const [toast, setToast] = useState('')

  function showToast(msg) {
    setToast(msg)
    setTimeout(() => setToast(''), 3000)
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-[#080c14] lg:flex">
      <Sidebar />
      <main className="min-w-0 flex-1">
        <Header
          title="Settings"
          subtitle="Manage your account, appearance, and workspace integrations."
        />

        <div className="mx-auto max-w-3xl space-y-8 px-5 py-8 lg:px-8">

          {/* ── 1. Profile ─────────────────────────────────────────────────── */}
          <Section
            icon={User}
            title="Profile"
            subtitle="Your account identity and security settings."
          >
            {/* Avatar + name row */}
            <div className="flex items-center gap-4 pb-6 border-b border-slate-100 dark:border-slate-800">
              <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-blue-500 text-xl font-bold text-white shadow-md shadow-blue-500/30">
                {(user?.email?.[0] ?? 'U').toUpperCase()}
              </div>
              <div>
                <p className="font-semibold text-slate-900 dark:text-white">
                  {user?.email ?? 'No account'}
                </p>
                <p className="text-sm text-slate-500 dark:text-slate-400">Administrator</p>
              </div>
            </div>

            {/* Read-only fields */}
            <div className="mt-5 space-y-4">
              <Field label="Email Address" value={user?.email ?? ''} readOnly />
              <Field label="Full Name" value={user?.full_name ?? 'Not set'} readOnly />
            </div>

            {/* Password change */}
            <PasswordSection showToast={showToast} />
          </Section>

          {/* ── 2. Appearance ─────────────────────────────────────────────── */}
          <Section
            icon={theme === 'dark' ? Moon : Sun}
            title="Appearance"
            subtitle="Customize how RASSAY looks across all your devices."
          >
            <div className="flex items-center justify-between gap-6">
              <div>
                <p className="font-medium text-slate-900 dark:text-white">Theme</p>
                <p className="mt-0.5 text-sm text-slate-500 dark:text-slate-400">
                  {theme === 'dark'
                    ? 'Dark mode active — deep-space palette with neon-green accents.'
                    : 'Light mode active — clean white surfaces with blue accents.'}
                </p>
              </div>

              {/* Toggle pill */}
              <button
                type="button"
                onClick={toggleTheme}
                className={`relative inline-flex h-8 w-16 shrink-0 cursor-pointer rounded-full border-2 transition-colors duration-300 focus:outline-none ${
                  theme === 'dark'
                    ? 'border-emerald-500 bg-emerald-500/20'
                    : 'border-slate-300 bg-slate-200'
                }`}
                aria-label="Toggle dark mode"
              >
                <span
                  className={`inline-flex h-6 w-6 transform items-center justify-center rounded-full shadow transition-transform duration-300 ${
                    theme === 'dark'
                      ? 'translate-x-8 bg-emerald-400 text-slate-900'
                      : 'translate-x-0 bg-white text-slate-600'
                  }`}
                >
                  {theme === 'dark'
                    ? <Moon className="h-3 w-3" />
                    : <Sun className="h-3 w-3" />}
                </span>
              </button>
            </div>

            {/* Mode preview pills */}
            <div className="mt-5 grid grid-cols-2 gap-3">
              <ModePill
                label="Light"
                icon={Sun}
                active={theme === 'light'}
                onClick={() => theme !== 'light' && toggleTheme()}
                preview="bg-white border-slate-200"
                dot="bg-blue-500"
              />
              <ModePill
                label="Dark"
                icon={Moon}
                active={theme === 'dark'}
                onClick={() => theme !== 'dark' && toggleTheme()}
                preview="bg-slate-900 border-slate-700"
                dot="bg-emerald-400"
              />
            </div>
          </Section>

          {/* ── 3. Integrations ──────────────────────────────────────────── */}
          <Section
            icon={ShieldCheck}
            title="Integrations"
            subtitle="Connect external services to enrich RASSAY's prediction data."
          >
            <div className="space-y-5">
              {INTEGRATIONS.map(intg => (
                <IntegrationRow key={intg.id} intg={intg} showToast={showToast} />
              ))}
            </div>
          </Section>

        </div>
      </main>

      {toast && (
        <div className="fixed bottom-6 right-6 z-50 flex items-center gap-2 rounded-xl bg-slate-900 dark:bg-slate-800 dark:border dark:border-emerald-800/60 px-5 py-3 text-sm font-semibold text-white shadow-xl">
          <Check className="h-4 w-4 text-emerald-400" />
          {toast}
        </div>
      )}
    </div>
  )
}

/* ── Sub-components ─────────────────────────────────────────────────────── */

function Section({ icon: Icon, title, subtitle, children }) {
  return (
    <section>
      <div className="mb-3 flex items-center gap-2">
        <Icon className="h-4 w-4 text-slate-400 dark:text-slate-500" />
        <h2 className="text-sm font-bold uppercase tracking-widest text-slate-400 dark:text-slate-500">
          {title}
        </h2>
      </div>
      {subtitle && (
        <p className="mb-4 text-sm text-slate-500 dark:text-slate-400">{subtitle}</p>
      )}
      <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 shadow-sm">
        {children}
      </div>
    </section>
  )
}

function Field({ label, value, readOnly = false }) {
  return (
    <div>
      <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-slate-400 dark:text-slate-500">
        {label}
      </label>
      <input
        type="text"
        defaultValue={value}
        readOnly={readOnly}
        className={`w-full rounded-lg border px-3 py-2.5 text-sm transition outline-none
          ${readOnly
            ? 'border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 text-slate-500 dark:text-slate-400 cursor-default'
            : 'border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:border-blue-400 dark:focus:border-emerald-500'
          }`}
      />
    </div>
  )
}

function PasswordSection({ showToast }) {
  const [current, setCurrent] = useState('')
  const [next, setNext] = useState('')
  const [show, setShow] = useState(false)

  function handleSubmit(e) {
    e.preventDefault()
    if (!current || !next) return
    showToast('Password updated successfully.')
    setCurrent('')
    setNext('')
  }

  const inputCls =
    'w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-3 py-2.5 pr-10 text-sm text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 outline-none transition focus:border-blue-400 dark:focus:border-emerald-500'

  return (
    <form onSubmit={handleSubmit} className="mt-6 space-y-4 pt-6 border-t border-slate-100 dark:border-slate-800">
      <p className="text-sm font-semibold text-slate-800 dark:text-slate-200 flex items-center gap-2">
        <KeyRound className="h-4 w-4 text-slate-400 dark:text-slate-500" />
        Change Password
      </p>
      <div className="grid gap-3 sm:grid-cols-2">
        <div className="relative">
          <input
            type={show ? 'text' : 'password'}
            placeholder="Current password"
            value={current}
            onChange={e => setCurrent(e.target.value)}
            autoComplete="current-password"
            className={inputCls}
          />
          <EyeToggle show={show} toggle={() => setShow(v => !v)} />
        </div>
        <div className="relative">
          <input
            type={show ? 'text' : 'password'}
            placeholder="New password"
            value={next}
            onChange={e => setNext(e.target.value)}
            autoComplete="new-password"
            className={inputCls}
          />
          <EyeToggle show={show} toggle={() => setShow(v => !v)} />
        </div>
      </div>
      <button
        type="submit"
        className="inline-flex items-center gap-2 rounded-lg bg-slate-900 dark:bg-emerald-500/20 dark:border dark:border-emerald-700 px-4 py-2 text-sm font-semibold text-white dark:text-emerald-400 transition hover:bg-slate-700 dark:hover:bg-emerald-500/30"
      >
        <Save className="h-4 w-4" />
        Update Password
      </button>
    </form>
  )
}

function EyeToggle({ show, toggle }) {
  return (
    <button
      type="button"
      onClick={toggle}
      tabIndex={-1}
      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
    >
      {show ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
    </button>
  )
}

function ModePill({ label, icon: Icon, active, onClick, preview, dot }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`flex items-center gap-3 rounded-lg border p-3 text-sm font-semibold transition ${
        active
          ? 'border-blue-400 dark:border-emerald-500 bg-blue-50 dark:bg-emerald-500/10 text-blue-700 dark:text-emerald-400'
          : 'border-slate-200 dark:border-slate-700 text-slate-500 dark:text-slate-400 hover:border-slate-300 dark:hover:border-slate-600'
      }`}
    >
      <span className={`h-8 w-8 rounded-md border ${preview} flex items-center justify-center`}>
        <span className={`h-2.5 w-2.5 rounded-full ${dot}`} />
      </span>
      <Icon className="h-4 w-4" />
      {label}
      {active && <Check className="ml-auto h-3.5 w-3.5" />}
    </button>
  )
}

function IntegrationRow({ intg, showToast }) {
  const { icon: Icon, name, description, label, placeholder, storageKey, accentLight, accentDark } = intg
  const [value, setValue] = useState(() => localStorage.getItem(storageKey) || '')
  const [masked, setMasked] = useState(true)
  const [copied, setCopied] = useState(false)
  const [saved, setSaved] = useState(false)

  function handleSave() {
    localStorage.setItem(storageKey, value)
    setSaved(true)
    showToast(`${name} configuration saved.`)
    setTimeout(() => setSaved(false), 2000)
  }

  function handleCopy() {
    if (!value) return
    navigator.clipboard.writeText(value).catch(() => {})
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const displayValue = masked && value ? value.slice(0, 4) + '•'.repeat(Math.max(0, value.length - 4)) : value

  return (
    <div className="rounded-lg border border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/40 p-4">
      <div className="flex items-start gap-3">
        <div className={`rounded-lg p-2 ${accentLight} ${accentDark}`}>
          <Icon className="h-4 w-4" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="font-semibold text-slate-900 dark:text-white text-sm">{name}</p>
          <p className="mt-0.5 text-xs text-slate-500 dark:text-slate-400 leading-relaxed">{description}</p>

          <div className="mt-3">
            <label className="mb-1 block text-[10px] font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500">
              {label}
            </label>
            <div className="flex gap-2">
              <div className="relative flex-1">
                <input
                  type="text"
                  value={displayValue}
                  onChange={e => {
                    setMasked(false)
                    setValue(e.target.value)
                  }}
                  onFocus={() => setMasked(false)}
                  onBlur={() => setMasked(true)}
                  placeholder={placeholder}
                  className="w-full rounded-md border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-3 py-2 text-xs font-mono text-slate-700 dark:text-slate-300 placeholder-slate-300 dark:placeholder-slate-600 outline-none transition focus:border-blue-400 dark:focus:border-emerald-500"
                  spellCheck={false}
                />
              </div>
              <button
                type="button"
                onClick={handleCopy}
                title="Copy to clipboard"
                className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-500 dark:text-slate-400 transition hover:bg-slate-100 dark:hover:bg-slate-700"
              >
                {copied ? <Check className="h-3.5 w-3.5 text-emerald-500" /> : <Copy className="h-3.5 w-3.5" />}
              </button>
              <button
                type="button"
                onClick={handleSave}
                className="inline-flex h-9 items-center gap-1.5 rounded-md bg-slate-900 dark:bg-emerald-500/20 dark:border dark:border-emerald-700 px-3 text-xs font-semibold text-white dark:text-emerald-400 transition hover:bg-slate-700 dark:hover:bg-emerald-500/30"
              >
                {saved ? <Check className="h-3.5 w-3.5" /> : <Save className="h-3.5 w-3.5" />}
                {saved ? 'Saved' : 'Save'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
