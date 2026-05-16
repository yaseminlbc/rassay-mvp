import { useState, useEffect } from 'react'
import { ArrowUpRight, ChevronLeft, ChevronRight } from 'lucide-react'
import { Link } from 'react-router-dom'
import RiskBadge from './RiskBadge'

const PAGE_SIZE = 50

/** Normalise risk_score to a 0-100 float regardless of whether the backend
 *  sends 0-1 or 0-100, then format it as "98.9%" */
function fmtScore(score) {
  if (score == null) return '—'
  const pct = score <= 1 ? score * 100 : score
  return `${pct.toFixed(1)}%`
}

function scoreWidth(score) {
  if (score == null) return 0
  return Math.min(score <= 1 ? score * 100 : score, 100)
}

function scoreBand(score) {
  const pct = score <= 1 ? score * 100 : score
  if (pct >= 70) return 'bg-rose-500'
  if (pct >= 40) return 'bg-amber-400'
  return 'bg-emerald-500'
}

export default function RiskTable({ customers }) {
  const [page, setPage] = useState(1)

  // Reset to page 1 whenever the filtered list changes
  useEffect(() => { setPage(1) }, [customers])

  const total      = customers.length
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))
  const start      = (page - 1) * PAGE_SIZE
  const pageRows   = customers.slice(start, start + PAGE_SIZE)

  return (
    <div className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
      {/* Header */}
      <div className="border-b border-slate-200 px-5 py-4">
        <h2 className="text-base font-semibold text-slate-950">Customer Risk Register</h2>
        <p className="mt-1 text-sm text-slate-500">
          {total.toLocaleString()} accounts · sorted by risk score, highest first.
        </p>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
          <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-5 py-3 font-semibold">Company</th>
              <th className="px-5 py-3 font-semibold">Plan</th>
              <th className="px-5 py-3 font-semibold">Risk Score</th>
              <th className="px-5 py-3 font-semibold">Risk Level</th>
              <th className="px-5 py-3 font-semibold">Top Risk Factor</th>
              <th className="px-5 py-3 font-semibold">Account Owner</th>
              <th className="px-5 py-3 font-semibold">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {pageRows.map((customer) => (
              <tr key={customer.company_id} className="hover:bg-slate-50">
                {/* Company */}
                <td className="px-5 py-4">
                  <p className="font-semibold text-slate-950">
                    {customer.company_name || customer.company_id}
                  </p>
                  <p className="text-xs text-slate-400">{customer.company_id}</p>
                </td>

                {/* Plan */}
                <td className="px-5 py-4 text-slate-600">{customer.plan_type || '—'}</td>

                {/* Risk Score — percentage bar + label */}
                <td className="px-5 py-4">
                  <div className="flex items-center gap-3">
                    <div className="h-2 w-24 rounded-full bg-slate-100">
                      <div
                        className={`h-2 rounded-full transition-all ${scoreBand(customer.risk_score)}`}
                        style={{ width: `${scoreWidth(customer.risk_score)}%` }}
                      />
                    </div>
                    <span className="w-14 tabular-nums font-semibold text-slate-950">
                      {fmtScore(customer.risk_score)}
                    </span>
                  </div>
                </td>

                {/* Risk Level */}
                <td className="px-5 py-4">
                  <RiskBadge level={customer.risk_level} />
                </td>

                {/* Top Risk Factor */}
                <td className="max-w-xs px-5 py-4 text-slate-600">
                  {customer.top_risk_factor || '—'}
                </td>

                {/* Account Owner */}
                <td className="px-5 py-4 text-slate-600">
                  {customer.account_owner || 'Unassigned'}
                </td>

                {/* Action */}
                <td className="px-5 py-4">
                  <Link
                    className="inline-flex items-center gap-1 text-sm font-semibold text-blue-700 hover:text-blue-900"
                    to={`/customers/${customer.company_id}`}
                  >
                    View XAI
                    <ArrowUpRight className="h-4 w-4" aria-hidden="true" />
                  </Link>
                </td>
              </tr>
            ))}

            {total === 0 && (
              <tr>
                <td className="px-5 py-10 text-center text-sm text-slate-500" colSpan="7">
                  No customers match the current search and risk filter.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination footer — only shown when there is more than one page */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between border-t border-slate-100 px-5 py-3">
          <p className="text-xs text-slate-500">
            Showing&nbsp;
            <span className="font-semibold text-slate-700">{(start + 1).toLocaleString()}</span>
            &nbsp;–&nbsp;
            <span className="font-semibold text-slate-700">
              {Math.min(start + PAGE_SIZE, total).toLocaleString()}
            </span>
            &nbsp;of&nbsp;
            <span className="font-semibold text-slate-700">{total.toLocaleString()}</span>
          </p>

          <div className="flex items-center gap-1">
            <PageBtn
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              aria-label="Previous page"
            >
              <ChevronLeft className="h-4 w-4" />
            </PageBtn>

            {/* Sliding window of up to 5 page numbers */}
            {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
              const windowStart = Math.max(1, Math.min(totalPages - 4, page - 2))
              const p = windowStart + i
              return (
                <PageBtn key={p} onClick={() => setPage(p)} active={p === page}>
                  {p}
                </PageBtn>
              )
            })}

            <PageBtn
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              aria-label="Next page"
            >
              <ChevronRight className="h-4 w-4" />
            </PageBtn>
          </div>
        </div>
      )}
    </div>
  )
}

function PageBtn({ children, onClick, disabled, active, ...rest }) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className={`inline-flex h-8 min-w-[2rem] items-center justify-center rounded px-2 text-xs font-semibold transition
        ${active
          ? 'bg-slate-950 text-white'
          : disabled
          ? 'cursor-not-allowed text-slate-300'
          : 'text-slate-600 hover:bg-slate-100'
        }`}
      {...rest}
    >
      {children}
    </button>
  )
}
