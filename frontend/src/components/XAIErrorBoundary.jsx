import { Component } from 'react'
import { ShieldQuestion } from 'lucide-react'

/**
 * React Error Boundary for the XAI bar chart section.
 *
 * Catches render-time errors thrown by Recharts or by unexpected shapes in the
 * SHAP payload (e.g. null impact_value, missing feature_name) without letting
 * the crash propagate up and unmount the entire CompanyDetail page.
 */
export default class XAIErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  componentDidCatch(error, info) {
    console.error('[XAIErrorBoundary] XAI render failed:', error, info.componentStack)
  }

  handleRetry = () => {
    this.setState({ hasError: false })
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center h-64 bg-slate-50 rounded-xl border border-dashed border-slate-200">
          <ShieldQuestion className="h-10 w-10 text-slate-300 mb-3" />
          <p className="text-sm font-semibold text-slate-700">XAI analysis unavailable</p>
          <p className="text-xs text-slate-500 mt-1 text-center max-w-xs">
            The AI explanation engine returned unexpected data. Run the prediction pipeline to refresh.
          </p>
          <button
            type="button"
            onClick={this.handleRetry}
            className="mt-4 text-xs font-semibold text-blue-600 hover:text-blue-800 hover:underline"
          >
            Retry
          </button>
        </div>
      )
    }

    return this.props.children
  }
}
