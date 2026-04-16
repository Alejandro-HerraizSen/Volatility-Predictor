import { useState, useEffect } from 'react'
import './index.css'
import SentimentPanel from './components/SentimentPanel'
import OptionChain from './components/OptionChain'
import RiskPredictor from './components/RiskPredictor'

function useClock() {
  const [time, setTime] = useState(new Date())
  useEffect(() => {
    const id = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(id)
  }, [])
  return time
}

export default function App() {
  const now = useClock()
  const timeStr = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  const dateStr = now.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })

  return (
    <div className="h-screen flex flex-col bg-[#06080f] text-[#f1f5f9] overflow-hidden">

      {/* Navbar */}
      <header className="shrink-0 relative border-b border-white/[0.06] bg-[#06080f] z-50">
        <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-blue-500 to-transparent opacity-60" />
        <div className="px-4 py-2.5 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <span className="text-white font-bold text-base tracking-tight bg-gradient-to-r from-blue-400 to-violet-400 bg-clip-text text-transparent">
              Earnings Call Risk & Confidence Analyzer
            </span>
          </div>

          <div className="flex items-center gap-4 text-xs">
            <span className="text-slate-600 hidden lg:block">
              Sources: <span className="text-slate-400">Bluesky · SEC Transcripts · Options Markets</span>
            </span>
            <div className="flex items-center gap-1.5 text-emerald-400">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Market Open
            </div>
            <span className="text-slate-600 font-mono">{dateStr} · {timeStr} ET</span>
          </div>
        </div>
      </header>

      {/* Body — TradingView style */}
      <div className="flex-1 flex overflow-hidden">

        {/* Main area — option chain top, sentiment feed bottom */}
        <div className="flex-1 flex flex-col overflow-hidden">

          {/* Top: Option chain — takes most of the height */}
          <div className="flex-1 overflow-hidden p-3 pb-1.5">
            <OptionChain />
          </div>

          {/* Bottom: Sentiment feed — fixed height strip */}
          <div className="h-[280px] shrink-0 p-3 pt-1.5">
            <SentimentPanel />
          </div>
        </div>

        {/* Right sidebar — Risk predictor */}
        <div className="w-[300px] shrink-0 border-l border-white/[0.06] overflow-y-auto">
          <RiskPredictor />
        </div>

      </div>
    </div>
  )
}
