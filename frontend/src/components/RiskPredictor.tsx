import { useState } from 'react'

interface PredictionResult {
  predictedIV: number
  riskScore: number
  recommendation: string
}

const getRiskLabel = (score: number) => {
  if (score >= 7) return { label: 'High Risk', color: 'text-red-400', bg: 'bg-red-500/10', border: 'border-red-500/25', bar: 'bg-red-500' }
  if (score >= 4) return { label: 'Medium Risk', color: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/25', bar: 'bg-amber-500' }
  return { label: 'Low Risk', color: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/25', bar: 'bg-emerald-500' }
}

export default function RiskPredictor() {
  const [ticker, setTicker] = useState('')
  const [strike, setStrike] = useState('')
  const [expiry, setExpiry] = useState('')
  const [optionType, setOptionType] = useState<'call' | 'put'>('call')
  const [result, setResult] = useState<PredictionResult | null>(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: { preventDefault(): void }) => {
    e.preventDefault()
    setLoading(true)
    setResult(null)

    // TODO: replace with real API call to your model backend
    await new Promise((r) => setTimeout(r, 1200))
    setResult({
      predictedIV: 0.42,
      riskScore: 7.3,
      recommendation: 'High earnings risk detected. Implied volatility likely to spike post-announcement.',
    })
    setLoading(false)
  }

  const risk = result ? getRiskLabel(result.riskScore) : null

  return (
    <div className="bg-[#0d1526] border border-white/[0.07] rounded-2xl overflow-hidden flex flex-col">
      {/* Header */}
      <div className="px-5 py-4 border-b border-white/[0.06] flex items-center gap-2">
        <div className="w-5 h-5 rounded bg-blue-500/20 flex items-center justify-center">
          <span className="text-blue-400 text-xs">◎</span>
        </div>
        <h2 className="text-white font-semibold text-base">Risk Predictor</h2>
      </div>

      <div className="p-5 flex flex-col gap-5">
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          {/* Ticker + Strike */}
          <div className="grid grid-cols-2 gap-3">
            <div className="flex flex-col gap-1.5">
              <label className="text-[11px] text-slate-500 uppercase tracking-wider font-medium">Ticker</label>
              <input
                type="text"
                value={ticker}
                onChange={(e) => setTicker(e.target.value.toUpperCase())}
                placeholder="AAPL"
                required
                maxLength={5}
                className="bg-[#080c15] border border-white/[0.08] rounded-lg px-3 py-2.5 text-white text-sm font-mono focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/20 placeholder:text-slate-700 transition-all"
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="text-[11px] text-slate-500 uppercase tracking-wider font-medium">Strike</label>
              <input
                type="number"
                value={strike}
                onChange={(e) => setStrike(e.target.value)}
                placeholder="190"
                required
                className="bg-[#080c15] border border-white/[0.08] rounded-lg px-3 py-2.5 text-white text-sm font-mono focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/20 placeholder:text-slate-700 transition-all"
              />
            </div>
          </div>

          {/* Expiry */}
          <div className="flex flex-col gap-1.5">
            <label className="text-[11px] text-slate-500 uppercase tracking-wider font-medium">Expiry Date</label>
            <input
              type="date"
              value={expiry}
              onChange={(e) => setExpiry(e.target.value)}
              required
              className="bg-[#080c15] border border-white/[0.08] rounded-lg px-3 py-2.5 text-white text-sm focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/20 transition-all"
            />
          </div>

          {/* Option type toggle */}
          <div className="flex flex-col gap-1.5">
            <label className="text-[11px] text-slate-500 uppercase tracking-wider font-medium">Option Type</label>
            <div className="grid grid-cols-2 gap-1.5 p-1 bg-[#080c15] border border-white/[0.08] rounded-lg">
              <button
                type="button"
                onClick={() => setOptionType('call')}
                className={`py-2 rounded-md text-sm font-medium transition-all duration-150 ${
                  optionType === 'call'
                    ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/25 shadow-sm'
                    : 'text-slate-500 hover:text-slate-300'
                }`}
              >
                ↗ Call
              </button>
              <button
                type="button"
                onClick={() => setOptionType('put')}
                className={`py-2 rounded-md text-sm font-medium transition-all duration-150 ${
                  optionType === 'put'
                    ? 'bg-red-500/20 text-red-400 border border-red-500/25 shadow-sm'
                    : 'text-slate-500 hover:text-slate-300'
                }`}
              >
                ↘ Put
              </button>
            </div>
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
            className="relative overflow-hidden bg-gradient-to-r from-blue-600 to-violet-600 hover:from-blue-500 hover:to-violet-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-xl text-sm transition-all duration-150 shadow-lg shadow-blue-500/20"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Running model...
              </span>
            ) : (
              'Predict Risk'
            )}
          </button>
        </form>

        {/* Result */}
        {result && risk && (
          <div className={`border rounded-xl p-4 flex flex-col gap-4 ${risk.bg} ${risk.border}`}>
            {/* Risk score bar */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-slate-400 uppercase tracking-wider font-medium">Risk Score</span>
                <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${risk.bg} ${risk.color} border ${risk.border}`}>
                  {risk.label}
                </span>
              </div>
              <div className="flex items-end gap-3 mb-2">
                <span className={`text-3xl font-bold ${risk.color}`}>{result.riskScore.toFixed(1)}</span>
                <span className="text-slate-600 text-sm mb-1">/ 10</span>
              </div>
              <div className="w-full h-2 bg-white/[0.05] rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-700 ${risk.bar}`}
                  style={{ width: `${(result.riskScore / 10) * 100}%` }}
                />
              </div>
            </div>

            {/* Predicted IV */}
            <div className="bg-[#080c15]/60 rounded-lg px-3 py-2.5 flex items-center justify-between">
              <span className="text-xs text-slate-500 uppercase tracking-wider font-medium">Predicted IV</span>
              <span className="text-blue-400 font-bold text-lg font-mono">{(result.predictedIV * 100).toFixed(1)}%</span>
            </div>

            {/* Recommendation */}
            <p className="text-xs text-slate-400 leading-relaxed border-t border-white/[0.05] pt-3">
              {result.recommendation}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
