const styles = {
  high:   'bg-rose-50 text-rose-700 ring-rose-200 dark:bg-rose-500/10 dark:text-rose-400 dark:ring-rose-500/20',
  medium: 'bg-amber-50 text-amber-700 ring-amber-200 dark:bg-amber-500/10 dark:text-amber-400 dark:ring-amber-500/20',
  low:    'bg-emerald-50 text-emerald-700 ring-emerald-200 dark:bg-emerald-500/10 dark:text-emerald-400 dark:ring-emerald-500/20',
}

export default function RiskBadge({ level }) {
  const key = (level || '').toLowerCase()
  return (
    <span
      className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-semibold capitalize ring-1 ${styles[key] || styles.medium}`}
    >
      {level} risk
    </span>
  )
}
