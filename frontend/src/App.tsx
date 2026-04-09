import './index.css'
import SentimentPanel from './components/SentimentPanel'
import OptionChain from './components/OptionChain'
import RiskPredictor from './components/RiskPredictor'

const stats = [
  { label: 'Underlying', value: '$187.42', sub: 'AAPL', color: 'text-white' },
  { label: 'Change', value: '-2.14%', sub: '↓ $4.09', color: 'text-red-400' },
  { label: 'IV Rank', value: '73.4', sub: '30-day', color: 'text-amber-400' },
  { label: 'Put/Call Ratio', value: '1.24', sub: 'Bearish skew', color: 'text-red-400' },
  { label: 'Avg Sentiment', value: '62.1%', sub: 'Bullish', color: 'text-emerald-400' },
  { label: 'VIX', value: '21.8', sub: 'Elevated', color: 'text-amber-400' },
]

export default function App() {
  return (
    <div className="min-h-screen bg-[#06080f] text-[#f1f5f9]">

      {/* Navbar */}
      <header className="relative border-b border-white/[0.06] bg-[#06080f]/90 backdrop-blur-sm sticky top-0 z-50">
        {/* Gradient accent line at top */}
        <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-blue-500 to-transparent opacity-60" />

        <div className="max-w-[1440px] mx-auto px-6 py-3.5 flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center text-white font-bold text-sm shadow-lg shadow-blue-500/20">
              V
            </div>
            <div>
              <span className="text-white font-semibold text-base tracking-tight">Earnings Call Risk & Confidence Analyzer</span>
              <span className="ml-2 text-[10px] text-blue-400 bg-blue-500/10 border border-blue-500/20 rounded-full px-2 py-0.5 font-medium">
                BETA
              </span>
            </div>
          </div>

          {/* Center — active earnings call */}
          <div className="flex items-center gap-2 bg-white/[0.04] border border-white/[0.08] rounded-lg px-4 py-2">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-slate-400 text-sm">Live:</span>
            <span className="text-white text-sm font-medium">AAPL Q2 2026 Earnings Call</span>
          </div>

          {/* Right — market status */}
          <div className="flex items-center gap-5 text-sm text-slate-500">
            <span>NYSE</span>
            <div className="flex items-center gap-1.5 text-emerald-400">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Market Open
            </div>
            <span className="text-slate-600">Apr 9, 2026 · 10:07 AM ET</span>
          </div>
        </div>
      </header>

      {/* Stats bar */}
      <div className="border-b border-white/[0.06] bg-[#080c15]">
        <div className="max-w-[1440px] mx-auto px-6 py-2.5 flex items-center gap-8 overflow-x-auto">
          {stats.map((s) => (
            <div key={s.label} className="flex items-center gap-3 shrink-0">
              <div>
                <p className="text-[10px] text-slate-500 uppercase tracking-wider leading-none mb-1">{s.label}</p>
                <p className={`text-sm font-semibold ${s.color} leading-none`}>{s.value}</p>
              </div>
              <p className="text-xs text-slate-600">{s.sub}</p>
              <div className="w-px h-6 bg-white/[0.06]" />
            </div>
          ))}
        </div>
      </div>

      {/* Main grid */}
      <main className="max-w-[1440px] mx-auto p-6 grid grid-cols-1 xl:grid-cols-3 gap-5">
        <div className="xl:col-span-2">
          <SentimentPanel />
        </div>
        <div>
          <RiskPredictor />
        </div>
        <div className="xl:col-span-3">
          <OptionChain />
        </div>
      </main>
    </div>
  )
}
