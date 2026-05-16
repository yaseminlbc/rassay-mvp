import { ArrowUpRight } from 'lucide-react'
import { Link } from 'react-router-dom'
import RiskBadge from './RiskBadge'

export default function RiskTable({ customers }) {
  return (
    <div className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-200 px-5 py-4">
        <h2 className="text-base font-semibold text-slate-950">Customer Risk Register</h2>
        <p className="mt-1 text-sm text-slate-500">Accounts sorted by risk score, highest first.</p>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
          <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-5 py-3 font-semibold">Company Name</th>
              <th className="px-5 py-3 font-semibold">Plan</th>
              <th className="px-5 py-3 font-semibold">Risk Score</th>
              <th className="px-5 py-3 font-semibold">Risk Level</th>
              <th className="px-5 py-3 font-semibold">Top Risk Factor</th>
              <th className="px-5 py-3 font-semibold">Account Owner</th>
              <th className="px-5 py-3 font-semibold">Last Login</th>
              <th className="px-5 py-3 font-semibold">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {customers.map((customer) => (
              <tr key={customer.company_id} className="hover:bg-slate-50">
                <td className="px-5 py-4">
                  <p className="font-semibold text-slate-950">{customer.company_name}</p>
                  <p className="text-xs text-slate-500">{customer.industry}</p>
                </td>
                <td className="px-5 py-4 text-slate-600">{customer.plan_type}</td>
                <td className="px-5 py-4">
                  <div className="flex items-center gap-3">
                    <div className="h-2 w-24 rounded-full bg-slate-100">
                      <div
                        className="h-2 rounded-full bg-blue-500"
                        style={{ width: `${customer.risk_score}%` }}
                      />
                    </div>
                    <span className="font-semibold text-slate-950">{customer.risk_score}</span>
                  </div>
                </td>
                <td className="px-5 py-4">
                  <RiskBadge level={customer.risk_level} />
                </td>
                <td className="max-w-xs px-5 py-4 text-slate-600">{customer.top_risk_factor}</td>
                <td className="px-5 py-4 text-slate-600">{customer.account_owner}</td>
                <td className="px-5 py-4 text-slate-600">{customer.last_login}</td>
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
            {customers.length === 0 ? (
              <tr>
                <td className="px-5 py-8 text-center text-sm text-slate-500" colSpan="8">
                  No customers match the current search and risk filter.
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </div>
  )
}
