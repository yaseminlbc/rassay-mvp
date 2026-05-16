import { useEffect, useState } from 'react'
import {
  CheckCircle2,
  CircleAlert,
  Copy,
  Key,
  Lock,
  RefreshCw,
  RotateCw,
  Server,
  ShieldCheck,
  TestTube2,
  Database,
  ShieldAlert,
  Bot, // Hubot yerine Bot geldi
  CreditCard,
  Layers,
  MessageSquare
} from 'lucide-react'
import Header from '../components/Header'
import Sidebar from '../components/Sidebar'
import { getIntegrationStatus } from '../services/api'

export default function Integrations() {
  const [settings, setSettings] = useState(null)
  const [message, setMessage] = useState('')

  useEffect(() => {
    getIntegrationStatus().then(setSettings).catch(err => console.error("Entegrasyon verisi çekilemedi:", err))
  }, [])

  function showMockStatus(text) {
    setMessage(text)
    window.setTimeout(() => setMessage(''), 3200)
  }

  return (
    <div className="min-h-screen bg-slate-50 lg:flex">
      <Sidebar />
      <main className="min-w-0 flex-1">
        <Header
          title="Data Integration Settings"
          subtitle="Manage telemetry sources, API connections, prediction pipeline status, and secure data sync."
        />

        <div className="space-y-6 px-5 py-6 lg:px-8 max-w-400 mx-auto">
          {message && (
            <div className="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm font-medium text-emerald-800 animate-in fade-in slide-in-from-top-2">
              {message}
            </div>
          )}

          {/* 1. SYSTEM STATUS */}
          <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-base font-semibold text-slate-900 mb-5">System Status</h2>
            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
              <StatusCard
                icon={Server}
                label="API Connection Status"
                value={settings?.api_connection?.status || 'Connected'}
                detail="FastAPI telemetry endpoint reachable"
                isSuccess
              />
              <StatusCard
                icon={RefreshCw}
                label="Prediction Pipeline Status"
                value={settings?.prediction_pipeline?.status || 'Operational'}
                detail="Mock churn model scoring jobs are healthy"
                isSuccess
              />
              <StatusCard
                icon={CheckCircle2}
                label="Last Successful Sync"
                value={settings?.last_successful_sync || '2026-05-06 09:15'}
              />
              <StatusCard
                icon={RotateCw}
                label="Last Model Training Time"
                value={settings?.last_model_training_time || '2026-05-06 08:30'}
              />
              <StatusCard
                icon={ShieldCheck}
                label="Data Freshness Status"
                value={settings?.data_freshness_status || 'Fresh - synced 12m ago'}
                isSuccess
              />
            </div>
          </section>

          {/* 2. DATABASE & CREDENTIALS */}
          <section className="grid gap-6 xl:grid-cols-[1fr_380px]">
            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="text-base font-semibold text-slate-900 mb-5">Database Connections</h2>
              <div className="space-y-4">
                <DatabaseItem 
                  name="PostgreSQL Production Database" 
                  host="postgres.internal.rassay.local" 
                  status="Connected" 
                  lastChecked="2026-05-06 09:18" 
                />
                <DatabaseItem 
                  name="Analytics Warehouse / Usage Data Source" 
                  host="warehouse.internal.rassay.local" 
                  status="Connected" 
                  lastChecked="2026-05-06 09:16" 
                />
              </div>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="flex items-center gap-2 mb-5">
                <Key className="h-5 w-5 text-blue-600" />
                <h2 className="text-base font-semibold text-slate-900">REST API Credentials</h2>
              </div>
              <div className="space-y-4">
                <CredentialBox label="Production API Key" value={settings?.credentials?.production_api_key} />
                <CredentialBox label="Webhook Signing Secret" value={settings?.credentials?.webhook_signing_secret} />
                <div className="flex gap-3 mt-6">
                  <button onClick={() => showMockStatus('Key copied!')} className="flex-1 flex items-center justify-center gap-2 px-4 py-2 border border-slate-200 rounded-lg text-sm font-semibold text-slate-700 hover:bg-slate-50 transition">
                    <Copy className="h-4 w-4" /> Copy
                  </button>
                  <button onClick={() => showMockStatus('Rotation started...')} className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-slate-900 text-white rounded-lg text-sm font-semibold hover:bg-slate-800 transition">
                    <RotateCw className="h-4 w-4" /> Rotate Keys
                  </button>
                </div>
              </div>
            </div>
          </section>

          {/* 3. SECURITY & ACTIONS */}
          <section className="grid gap-6 xl:grid-cols-[380px_1fr]">
            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="flex items-center gap-2 mb-5">
                <Lock className="h-5 w-5 text-emerald-600" />
                <h2 className="text-base font-semibold text-slate-900">Security / Encryption</h2>
              </div>
              <div className="space-y-2">
                <SecurityRow label="Data encrypted at rest" active />
                <SecurityRow label="TLS encryption in transit" active />
                <SecurityRow label="KVKK / GDPR-aware demo notice" active />
                <SecurityRow label="No real customer data used" active />
                <SecurityRow label="Synthetic demo data only" active />
              </div>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="text-base font-semibold text-slate-900 mb-5">Connection Actions</h2>
              <div className="flex flex-wrap gap-4 mt-8">
                <ActionButton onClick={() => showMockStatus('Test successful!')} icon={TestTube2} label="Test Connection" />
                <ActionButton onClick={() => showMockStatus('Syncing...')} icon={RefreshCw} label="Sync Now" primary />
                <ActionButton onClick={() => showMockStatus('Policy loading...')} icon={ShieldCheck} label="View Security Policy" />
              </div>
            </div>
          </section>

          {/* 4. INTEGRATION SOURCES */}
          <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-base font-semibold text-slate-900 mb-5">Integration Sources</h2>
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              <SourceCard type="CRM Source" name="HubSpot CRM" status="Connected" time="2026-05-06 09:10" icon={Bot} /> {/* Hubot -> Bot */}
              <SourceCard type="Billing Source" name="Stripe Billing" status="Connected" time="2026-05-06 08:45" icon={CreditCard} />
              <SourceCard type="Product Analytics Source" name="Segment Product Analytics" status="Connected" time="2026-05-06 09:02" icon={Layers} />
              <SourceCard type="Support Desk Source" name="Zendesk Support Desk" status="Warning" time="2026-05-05 18:40" icon={MessageSquare} />
            </div>
          </section>
        </div>
      </main>
    </div>
  )
}

// Yardımcı bileşenler (StatusCard, DatabaseItem, vb.) aynı kalıyor...
function StatusCard({ icon: Icon, label, value, detail, isSuccess }) {
  return (
    <div className="bg-slate-50 border border-slate-200 rounded-lg p-5">
      <div className="flex items-start justify-between mb-2">
        <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">{label}</p>
        <Icon className={`h-5 w-5 ${isSuccess ? 'text-blue-600' : 'text-slate-400'}`} />
      </div>
      <p className="text-lg font-bold text-slate-900">{value}</p>
      {detail && <p className="mt-2 text-[11px] text-slate-500 leading-tight">{detail}</p>}
    </div>
  )
}

function DatabaseItem({ name, host, status, lastChecked }) {
  return (
    <div className="flex items-center justify-between p-4 border border-slate-100 rounded-lg bg-white hover:border-slate-300 transition">
      <div>
        <h4 className="text-sm font-semibold text-slate-900">{name}</h4>
        <p className="text-xs text-slate-500 mt-0.5">{host}</p>
        <p className="text-[10px] text-slate-400 mt-2">Last checked: {lastChecked}</p>
      </div>
      <Badge status={status} />
    </div>
  )
}

function CredentialBox({ label, value = '********************' }) {
  return (
    <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
      <p className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter mb-2">{label}</p>
      <p className="font-mono text-xs font-semibold text-slate-700 tracking-widest">{value || '********************'}</p>
    </div>
  )
}

function SecurityRow({ label, active }) {
  return (
    <div className="flex items-center gap-3 p-2.5 bg-slate-50 rounded-lg border border-slate-100">
      <CheckCircle2 className={`h-4 w-4 ${active ? 'text-emerald-500' : 'text-slate-300'}`} />
      <span className="text-xs text-slate-600 font-medium">{label}</span>
    </div>
  )
}

function ActionButton({ icon: Icon, label, primary, onClick }) {
  return (
    <button 
      onClick={onClick}
      className={`inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-bold transition shadow-sm ${
        primary 
          ? 'bg-blue-600 text-white hover:bg-blue-700' 
          : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-50'
      }`}
    >
      <Icon className="h-4 w-4" /> {label}
    </button>
  )
}

function SourceCard({ type, name, status, time, icon: Icon }) {
  const isWarning = status === 'Warning'
  return (
    <div className="p-5 border border-slate-200 rounded-xl bg-white shadow-sm hover:border-slate-400 transition group">
      <div className="flex justify-between items-start mb-4">
        <div>
          <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest">{type}</p>
          <h4 className="text-sm font-bold text-slate-900 mt-1">{name}</h4>
        </div>
        <div className={`p-2 rounded-lg ${isWarning ? 'bg-amber-50 text-amber-500' : 'bg-emerald-50 text-emerald-500'}`}>
          <Icon className="h-5 w-5" />
        </div>
      </div>
      <div className="flex items-center justify-between mt-6">
        <Badge status={status} />
        <span className="text-[10px] text-slate-400 font-medium">{time}</span>
      </div>
    </div>
  )
}

function Badge({ status }) {
  const isOk = status === 'Connected' || status === 'Operational' || status === 'Active'
  const isWarning = status === 'Warning'

  return (
    <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-tight ring-1 ring-inset ${
      isOk ? 'bg-emerald-50 text-emerald-700 ring-emerald-200' : 
      isWarning ? 'bg-amber-50 text-amber-700 ring-amber-200' : 
      'bg-slate-100 text-slate-600 ring-slate-200'
    }`}>
      {status}
    </span>
  )
}