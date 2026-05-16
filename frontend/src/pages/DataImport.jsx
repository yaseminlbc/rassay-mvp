import { useCallback, useRef, useState } from 'react'
import {
  AlertCircle,
  CheckCircle2,
  CloudUpload,
  FileSpreadsheet,
  Loader2,
  TrendingDown,
  TrendingUp,
  Users,
  X,
} from 'lucide-react'
import Header from '../components/Header'
import Sidebar from '../components/Sidebar'
import { uploadCsvFile } from '../services/api'

const ACCEPTED = ['.csv', '.xlsx', '.xls']

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
}

export default function DataImport() {
  const [file, setFile] = useState(null)
  const [dragging, setDragging] = useState(false)
  const [status, setStatus] = useState('idle') // idle | uploading | success | error
  const [result, setResult] = useState(null)
  const [errorMsg, setErrorMsg] = useState('')
  const inputRef = useRef(null)

  const pickFile = useCallback((picked) => {
    if (!picked) return
    const ext = picked.name.toLowerCase().slice(picked.name.lastIndexOf('.'))
    if (!ACCEPTED.includes(ext)) {
      setErrorMsg(`Unsupported file type "${ext}". Please upload a .csv, .xlsx, or .xls file.`)
      setStatus('error')
      return
    }
    setFile(picked)
    setStatus('idle')
    setResult(null)
    setErrorMsg('')
  }, [])

  const onDrop = useCallback((e) => {
    e.preventDefault()
    setDragging(false)
    const dropped = e.dataTransfer.files?.[0]
    pickFile(dropped)
  }, [pickFile])

  const onDragOver = (e) => { e.preventDefault(); setDragging(true) }
  const onDragLeave = () => setDragging(false)

  const reset = () => {
    setFile(null)
    setStatus('idle')
    setResult(null)
    setErrorMsg('')
    if (inputRef.current) inputRef.current.value = ''
  }

  const handleUpload = async () => {
    if (!file) return
    setStatus('uploading')
    setResult(null)
    setErrorMsg('')
    try {
      const data = await uploadCsvFile(file)
      setResult(data)
      setStatus('success')
    } catch (err) {
      setErrorMsg(err.message || 'Upload failed.')
      setStatus('error')
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 lg:flex">
      <Sidebar />
      <main className="min-w-0 flex-1">
        <Header
          title="Data Import"
          subtitle="Upload a CSV or Excel file to bulk-import customers and run XGBoost churn predictions instantly."
        />

        <div className="mx-auto max-w-3xl space-y-6 px-5 py-6 lg:px-8">

          {/* Drop Zone */}
          <section className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
            <h2 className="mb-1 text-base font-semibold text-slate-900">Upload File</h2>
            <p className="mb-6 text-sm text-slate-500">
              Accepted formats: <span className="font-medium text-slate-700">.csv · .xlsx · .xls</span>.
              Required columns: <span className="font-mono text-xs text-blue-700">company_id, mrr_value, plan_type</span>.
            </p>

            {/* Drag area */}
            <div
              onDrop={onDrop}
              onDragOver={onDragOver}
              onDragLeave={onDragLeave}
              onClick={() => inputRef.current?.click()}
              className={`flex cursor-pointer flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed py-14 transition select-none
                ${dragging
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-slate-300 bg-slate-50 hover:border-blue-400 hover:bg-blue-50/40'
                }`}
            >
              <CloudUpload className={`h-10 w-10 ${dragging ? 'text-blue-500' : 'text-slate-400'}`} />
              <p className="text-sm font-semibold text-slate-700">
                {dragging ? 'Drop it here!' : 'Drag & drop your file here'}
              </p>
              <p className="text-xs text-slate-500">or click to browse</p>
            </div>

            <input
              ref={inputRef}
              type="file"
              accept=".csv,.xlsx,.xls"
              className="hidden"
              onChange={(e) => pickFile(e.target.files?.[0])}
            />

            {/* Selected file info */}
            {file && (
              <div className="mt-4 flex items-center justify-between rounded-lg border border-slate-200 bg-slate-50 px-4 py-3">
                <div className="flex items-center gap-3">
                  <FileSpreadsheet className="h-5 w-5 text-blue-600 shrink-0" />
                  <div>
                    <p className="text-sm font-semibold text-slate-800">{file.name}</p>
                    <p className="text-xs text-slate-500">{formatBytes(file.size)}</p>
                  </div>
                </div>
                <button
                  onClick={(e) => { e.stopPropagation(); reset() }}
                  className="rounded p-1 text-slate-400 hover:bg-slate-200 hover:text-slate-700 transition"
                  aria-label="Remove file"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            )}

            {/* Upload button */}
            <button
              onClick={handleUpload}
              disabled={!file || status === 'uploading'}
              className="mt-5 flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 py-3 text-sm font-bold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-40"
            >
              {status === 'uploading' ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Processing…
                </>
              ) : (
                <>
                  <CloudUpload className="h-4 w-4" />
                  Upload & Predict
                </>
              )}
            </button>
          </section>

          {/* Error banner */}
          {status === 'error' && errorMsg && (
            <div className="flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 px-5 py-4 shadow-sm">
              <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-red-500" />
              <div>
                <p className="text-sm font-semibold text-red-800">Upload failed</p>
                <p className="mt-1 text-xs text-red-700">{errorMsg}</p>
              </div>
            </div>
          )}

          {/* Success results */}
          {status === 'success' && result && (
            <section className="rounded-xl border border-emerald-200 bg-white shadow-sm">
              <div className="flex items-center gap-3 border-b border-slate-100 px-6 py-4">
                <CheckCircle2 className="h-5 w-5 text-emerald-500" />
                <h2 className="text-base font-semibold text-slate-900">Import Complete</h2>
                <span className="ml-auto rounded-full bg-emerald-50 px-3 py-0.5 text-xs font-bold text-emerald-700 ring-1 ring-emerald-200">
                  {result.total_processed} rows processed
                </span>
              </div>

              <div className="grid grid-cols-2 gap-px bg-slate-100 sm:grid-cols-3 lg:grid-cols-5">
                <StatCell label="Inserted" value={result.inserted} color="text-blue-700" />
                <StatCell label="Updated" value={result.updated} color="text-slate-700" />
                <StatCell label="High Risk" value={result.high_risk} color="text-red-600" icon={<TrendingUp className="h-4 w-4 text-red-400" />} />
                <StatCell label="Medium Risk" value={result.medium_risk} color="text-amber-600" icon={<Users className="h-4 w-4 text-amber-400" />} />
                <StatCell label="Low Risk" value={result.low_risk} color="text-emerald-600" icon={<TrendingDown className="h-4 w-4 text-emerald-400" />} />
              </div>

              {result.errors > 0 && (
                <div className="border-t border-slate-100 px-6 py-4">
                  <p className="mb-2 text-xs font-bold uppercase tracking-wide text-amber-700">
                    {result.errors} row{result.errors !== 1 ? 's' : ''} skipped
                  </p>
                  <ul className="space-y-1">
                    {result.error_details.map((msg, i) => (
                      <li key={i} className="rounded bg-amber-50 px-3 py-1.5 font-mono text-[11px] text-amber-800">
                        {msg}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="border-t border-slate-100 px-6 py-3">
                <button
                  onClick={reset}
                  className="text-xs font-semibold text-blue-600 hover:underline"
                >
                  Upload another file
                </button>
              </div>
            </section>
          )}

          {/* Column guide */}
          <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-base font-semibold text-slate-900">Column Reference</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-100">
                    <th className="pb-2 text-left text-xs font-bold uppercase tracking-wide text-slate-500">Column</th>
                    <th className="pb-2 text-left text-xs font-bold uppercase tracking-wide text-slate-500">Required</th>
                    <th className="pb-2 text-left text-xs font-bold uppercase tracking-wide text-slate-500">Example</th>
                    <th className="pb-2 text-left text-xs font-bold uppercase tracking-wide text-slate-500">Notes</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-50">
                  {COLUMN_GUIDE.map((col) => (
                    <tr key={col.name} className="hover:bg-slate-50">
                      <td className="py-2.5 font-mono text-xs font-semibold text-blue-700">{col.name}</td>
                      <td className="py-2.5">
                        {col.required
                          ? <span className="rounded bg-red-50 px-2 py-0.5 text-[10px] font-bold text-red-700 ring-1 ring-red-200">Required</span>
                          : <span className="rounded bg-slate-100 px-2 py-0.5 text-[10px] font-bold text-slate-500">Optional</span>
                        }
                      </td>
                      <td className="py-2.5 font-mono text-xs text-slate-600">{col.example}</td>
                      <td className="py-2.5 text-xs text-slate-500">{col.notes}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

        </div>
      </main>
    </div>
  )
}

function StatCell({ label, value, color, icon }) {
  return (
    <div className="flex flex-col items-center gap-1 bg-white px-4 py-5">
      {icon}
      <span className={`text-2xl font-bold ${color}`}>{value}</span>
      <span className="text-xs text-slate-500">{label}</span>
    </div>
  )
}

const COLUMN_GUIDE = [
  { name: 'company_id',          required: true,  example: '9444-JTXHZ', notes: 'Unique customer identifier (string)' },
  { name: 'mrr_value',           required: true,  example: '1299.00',    notes: 'Monthly recurring revenue (float)' },
  { name: 'plan_type',           required: true,  example: 'Month-to-month', notes: 'One of: Month-to-month · One year · Two year' },
  { name: 'account_age_months',  required: false, example: '24',         notes: 'Months since account creation' },
  { name: 'support_tickets',     required: false, example: '3',          notes: 'Open or total support tickets' },
  { name: 'login_count',         required: false, example: '42',         notes: 'Logins in last 30 days' },
  { name: 'churn_status',        required: false, example: '0',          notes: '0 = active, 1 = churned (for training)' },
]
