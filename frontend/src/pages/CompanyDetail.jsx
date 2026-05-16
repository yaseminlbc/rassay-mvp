import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import {
  ArrowLeft,
  Download,
  LineChart as LineChartIcon,
  PhoneCall,
  RefreshCw,
  ShieldQuestion,
  BrainCircuit,
  Activity,
  Calendar,
  User,
  Layout
} from 'lucide-react'
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  BarChart,
  Bar,
  Cell
} from 'recharts'
import Header from '../components/Header'
import RiskBadge from '../components/RiskBadge'
import Sidebar from '../components/Sidebar'
import { getCustomerById, getCustomerUsageTrend, getCustomerXai } from '../services/api'

const formatCurrency = (value) =>
  new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(value || 0)

const riskCopy = {
  'High': 'This account is currently classified as High Risk based on recent usage and subscription signals.',
  'Medium': 'This account is currently classified as Medium Risk and should stay on the customer success watchlist.',
  'Low': 'This account is currently classified as Low Risk with generally healthy engagement signals.',
}

export default function CompanyDetail() {
  const { id } = useParams() // company_id (örn: '9444-JTXHZ')
  const [customer, setCustomer] = useState(null)
  const [xai, setXai] = useState(null)
  const [usageTrend, setUsageTrend] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadAllData() {
      setLoading(true)
      try {
        // Dashboard'daki gibi bağımsız yükleme mantığı: Bir hata diğerini bozmasın.
        getCustomerById(id)
          .then(res => setCustomer(res))
          .catch(err => console.error("Müşteri detay hatası:", err));

        getCustomerXai(id)
          .then(res => setXai(res))
          .catch(err => console.error("XAI verisi çekilemedi:", err));

        getCustomerUsageTrend(id)
          .then(res => setUsageTrend(Array.isArray(res?.points) ? res.points : []))
          .catch(err => console.error("Usage trend hatası:", err));

      } finally {
        // Verilerin ilk yükleme anındaki titremesini önlemek için küçük bir gecikme
        setTimeout(() => setLoading(false), 300)
      }
    }

    loadAllData()
  }, [id])

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 lg:flex">
        <Sidebar />
        <main className="flex-1 flex items-center justify-center">
           <div className="text-center">
              <RefreshCw className="h-10 w-10 text-blue-600 animate-spin mx-auto mb-4" />
              <p className="text-slate-500 font-medium">Rassay AI is analyzing account data...</p>
           </div>
        </main>
      </div>
    )
  }

  if (!customer) {
    return (
      <div className="min-h-screen bg-slate-50 lg:flex">
        <Sidebar />
        <main className="flex-1">
          <Header title="Account Not Found" subtitle="The requested company ID does not exist in the database." />
          <div className="p-8 text-center">
            <Link className="inline-flex items-center gap-2 font-semibold text-blue-700 bg-blue-50 px-4 py-2 rounded-lg" to="/">
              <ArrowLeft className="h-4 w-4" /> Back to Dashboard
            </Link>
          </div>
        </main>
      </div>
    )
  }

  // XAI Faktörlerini işleme (Backend'den gelen listeyi alıyoruz)
  const xaiFactors = xai?.factors || []

  return (
    <div className="min-h-screen bg-slate-50 lg:flex">
      <Sidebar />
      <main className="min-w-0 flex-1">
        <Header
          title={customer.company_name || id}
          subtitle="Deep-dive churn risk analysis and explainable AI insights."
        />

        <div className="space-y-6 px-5 py-6 lg:px-8 max-w-350">
          {/* ÜST BİLGİ KARTI */}
          <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <Link className="inline-flex items-center gap-2 text-sm font-semibold text-blue-700 mb-6" to="/">
              <ArrowLeft className="h-4 w-4" /> Back to dashboard
            </Link>
            
            <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
              <HeaderFact icon={Layout} label="Current Plan" value={customer.plan_type || 'Enterprise'} />
              <HeaderFact icon={User} label="Account Owner" value={customer.account_owner || 'Unassigned'} />
              <HeaderFact icon={Calendar} label="Renewal Status" value={`${customer.renewal_days || 'N/A'} days remaining`} />
              <div className="flex flex-col justify-center">
                <p className="text-xs font-bold uppercase text-slate-400 tracking-wider">Risk Status</p>
                <div className="mt-2">
                  <RiskBadge level={customer.risk_level || 'Low'} />
                </div>
              </div>
            </div>
          </section>

          {/* RİSK SKORU VE TREND GRAFİĞİ */}
          <section className="grid gap-6 xl:grid-cols-[380px_1fr]">
            {/* Risk Score Gauge */}
            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm flex flex-col justify-between">
              <div>
                <p className="text-sm font-bold text-slate-500 uppercase tracking-tight">AI Risk Probability</p>
                <div className="mt-6 flex items-baseline gap-2">
                  <span className="text-7xl font-black text-slate-900">{(customer.risk_score * 100).toFixed(0)}</span>
                  <span className="text-2xl font-bold text-slate-300">%</span>
                </div>
                <div className="mt-6 h-4 rounded-full bg-slate-100 overflow-hidden">
                  <div
                    className={`h-full transition-all duration-1000 ${customer.risk_score > 0.7 ? 'bg-rose-500' : 'bg-blue-500'}`}
                    style={{ width: `${customer.risk_score * 100}%` }}
                  />
                </div>
              </div>
              
              <div className="mt-8 p-4 bg-slate-50 rounded-lg border border-slate-100">
                 <p className="text-sm font-bold text-slate-900 mb-1">AI Verdict:</p>
                 <p className="text-sm leading-relaxed text-slate-600">
                    {riskCopy[customer.risk_level] || 'Signals are stable.'}
                 </p>
              </div>
            </div>

            {/* Usage Trend Line Chart */}
            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-2">
                  <Activity className="h-5 w-5 text-blue-600" />
                  <h2 className="text-base font-bold text-slate-900">Engagement History</h2>
                </div>
              </div>
              <div className="h-80 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={usageTrend}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                    <XAxis dataKey="label" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                    <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                    <Tooltip 
                      contentStyle={{borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)'}}
                    />
                    <Line type="monotone" dataKey="value" stroke="#2563eb" strokeWidth={3} dot={{r: 4, fill: '#2563eb'}} activeDot={{r: 6}} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </section>

          {/* XAI INSIGHTS - BAR CHART GÖRÜNÜMÜ */}
          <section className="grid gap-6 xl:grid-cols-[1fr_360px]">
            <div className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
              <div className="flex items-center gap-2 mb-6">
                <BrainCircuit className="h-6 w-6 text-indigo-600" />
                <h2 className="text-lg font-bold text-slate-900">Explainable AI (XAI) Risk Factors</h2>
              </div>
              
              {xaiFactors.length > 0 ? (
                <div className="h-100 w-full">
                   <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={xaiFactors} layout="vertical" margin={{ left: 40, right: 40 }}>
                        <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
                        <XAxis type="number" hide />
                        <YAxis dataKey="feature_name" type="category" width={150} fontSize={12} fontWeight={600} stroke="#475569" />
                        <Tooltip 
                          cursor={{fill: '#f8fafc'}}
                          content={({ active, payload }) => {
                            if (active && payload && payload.length) {
                              const data = payload[0].payload;
                              return (
                                <div className="bg-slate-900 text-white p-3 rounded-lg shadow-xl border border-slate-700 text-xs">
                                  <p className="font-bold mb-1">{data.feature_name}</p>
                                  <p>Impact Score: {data.impact_value.toFixed(4)}</p>
                                </div>
                              )
                            }
                            return null;
                          }}
                        />
                        <Bar dataKey="impact_value" radius={[0, 4, 4, 0]} barSize={24}>
                          {xaiFactors.map((entry, index) => (
                            <Cell 
                              key={`cell-${index}`} 
                              fill={entry.impact_value > 0 ? '#e11d48' : '#059669'} 
                            />
                          ))}
                        </Bar>
                      </BarChart>
                   </ResponsiveContainer>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-64 bg-slate-50 rounded-xl border border-dashed border-slate-200">
                   <ShieldQuestion className="h-10 w-10 text-slate-300 mb-2" />
                   <p className="text-sm text-slate-500">Not enough telemetry data for XAI modeling.</p>
                </div>
              )}
            </div>

            {/* RETENTION ACTIONS */}
            <aside className="space-y-4">
               <h2 className="text-base font-bold text-slate-950 px-1">Retention Playbook</h2>
               <div className="grid gap-3">
                  <ActionButton icon={PhoneCall} label="Schedule Success Call" />
                  <ActionButton icon={RefreshCw} label="Trigger Re-onboarding" />
                  <ActionButton icon={Download} label="Download XAI Report (PDF)" />
                  <div className="p-4 bg-amber-50 border border-amber-100 rounded-xl mt-4">
                     <p className="text-xs font-bold text-amber-800 uppercase mb-2">CSM Tip</p>
                     <p className="text-xs text-amber-700 leading-relaxed">
                        The primary churn driver is usage decline. Focus on the last 14 days of activity during the call.
                     </p>
                  </div>
               </div>
            </aside>
          </section>
        </div>
      </main>
    </div>
  )
}

function HeaderFact({ icon: Icon, label, value }) {
  return (
    <div className="flex items-center gap-3">
      <div className="p-2 bg-slate-50 rounded-lg">
        <Icon className="h-5 w-5 text-slate-400" />
      </div>
      <div>
        <p className="text-[10px] font-bold uppercase text-slate-400 tracking-wider">{label}</p>
        <p className="text-sm font-bold text-slate-700">{value || 'N/A'}</p>
      </div>
    </div>
  )
}

function ActionButton({ icon: Icon, label }) {
  return (
    <button
      className="flex w-full items-center gap-3 rounded-xl border border-slate-200 bg-white px-4 py-4 text-left text-sm font-bold text-slate-700 transition hover:border-blue-300 hover:bg-blue-50 hover:text-blue-700 shadow-sm"
      type="button"
    >
      <Icon className="h-4 w-4" />
      {label}
    </button>
  )
}
