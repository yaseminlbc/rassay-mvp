export default function KpiCard({ title, value, detail, icon: Icon, tone = 'blue' }) {
  const tones = {
    blue:  'bg-blue-50 text-blue-700 dark:bg-blue-500/10 dark:text-blue-400',
    red:   'bg-red-50 text-red-700 dark:bg-red-500/10 dark:text-red-400',
    green: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-400',
    amber: 'bg-amber-50 text-amber-700 dark:bg-amber-500/10 dark:text-amber-400',
  }

  return (
    <div className="rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{title}</p>
          <p className="mt-3 text-2xl font-bold text-slate-950 dark:text-white">{value}</p>
        </div>
        {Icon ? (
          <div className={`rounded-lg p-2 ${tones[tone] || tones.blue}`}>
            <Icon className="h-5 w-5" aria-hidden="true" />
          </div>
        ) : null}
      </div>
      {detail ? <p className="mt-3 text-sm text-slate-500 dark:text-slate-400">{detail}</p> : null}
    </div>
  )
}
