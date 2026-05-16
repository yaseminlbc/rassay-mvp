const styles = {
  high: 'bg-rose-50 text-rose-700 ring-rose-200',
  medium: 'bg-amber-50 text-amber-700 ring-amber-200',
  low: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
}

export default function RiskBadge({ level }) {
  return (
    <span
      className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-semibold capitalize ring-1 ${styles[level] || styles.medium}`}
    >
      {level} risk
    </span>
  )
}
