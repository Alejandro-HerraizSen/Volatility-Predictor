import { useState, useEffect } from 'react'
import Papa from 'papaparse'

interface RawRow {
  timestamp: string
  text: string
  sent_score: string
}

interface FeedItem {
  id: number
  timestamp: string
  text: string
  score: number
  sentiment: 'positive' | 'negative' | 'neutral'
  confidence: number
}

function classifySentiment(score: number): 'positive' | 'negative' | 'neutral' {
  if (score >= 0.15) return 'positive'
  if (score <= -0.15) return 'negative'
  return 'neutral'
}

function deriveConfidence(score: number): number {
  return Math.min(99, Math.round(60 + Math.abs(score) * 38))
}

const sentimentConfig = {
  positive: { border: 'border-l-emerald-500', badge: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20', text: 'text-emerald-400', label: '↗ Positive' },
  negative: { border: 'border-l-red-500',     badge: 'bg-red-500/10 text-red-400 border-red-500/20',             text: 'text-red-400',     label: '↘ Negative' },
  neutral:  { border: 'border-l-slate-500',   badge: 'bg-slate-500/10 text-slate-400 border-slate-500/20',       text: 'text-slate-400',   label: '→ Neutral' },
}

function formatTime(ts: string) {
  try {
    return new Date(ts).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
  } catch {
    return ts
  }
}

export default function SentimentPanel() {
  const [feed, setFeed] = useState<FeedItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/data/social_scored.csv')
      .then((r) => r.text())
      .then((csv) => {
        const result = Papa.parse<RawRow>(csv, { header: true, skipEmptyLines: true })
        const items: FeedItem[] = result.data.map((row, i) => {
          const score = parseFloat(row.sent_score)
          return {
            id: i,
            timestamp: row.timestamp,
            text: row.text,
            score,
            sentiment: classifySentiment(score),
            confidence: deriveConfidence(score),
          }
        })
        setFeed(items)
        setLoading(false)
      })
  }, [])

  const avgScore = feed.length ? feed.reduce((s, i) => s + i.score, 0) / feed.length : 0
  const avgPct = Math.round((avgScore + 1) / 2 * 100)
  const avgColor = avgPct >= 55 ? 'text-emerald-400' : avgPct >= 45 ? 'text-amber-400' : 'text-red-400'

  return (
    <div className="bg-[#0d1526] border border-white/[0.07] rounded-xl overflow-hidden flex flex-col h-full">
      {/* Compact header */}
      <div className="px-4 py-2.5 flex items-center justify-between border-b border-white/[0.06] shrink-0">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-blue-500/20 flex items-center justify-center">
            <span className="text-blue-400 text-[10px]">≋</span>
          </div>
          <h2 className="text-white font-semibold text-sm">Sentiment Feed</h2>
          <div className="flex items-center gap-1 text-[10px] text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 rounded-full px-2 py-0.5">
            <span className="w-1 h-1 rounded-full bg-emerald-400 animate-pulse" />
            LIVE
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-slate-500 text-xs">Avg Sentiment:
            <span className={`ml-1.5 font-bold ${avgColor}`}>{avgPct}%</span>
          </span>
        </div>
      </div>

      {/* Horizontal scrolling card strip */}
      <div className="flex-1 overflow-x-auto overflow-y-hidden">
        <div className="flex gap-3 p-3 h-full" style={{ width: 'max-content' }}>
          {loading && (
            <div className="flex items-center text-slate-500 text-sm px-4">Loading sentiment data...</div>
          )}
          {!loading && feed.map((item) => {
            const sent = sentimentConfig[item.sentiment]
            return (
              <div
                key={item.id}
                className={`bg-[#080c15] border border-white/[0.06] border-l-2 ${sent.border} rounded-xl p-3 flex flex-col gap-2 hover:border-white/[0.12] transition-all duration-150 shrink-0`}
                style={{ width: '260px' }}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    <div className="w-5 h-5 rounded bg-violet-500/15 flex items-center justify-center text-violet-400 text-[10px] font-bold">𝕏</div>
                    <span className="text-white text-xs font-medium">Bluesky</span>
                  </div>
                  <span className="text-slate-600 text-[10px] font-mono">{formatTime(item.timestamp)}</span>
                </div>

                <p className="text-slate-300 text-xs leading-relaxed line-clamp-3">{item.text}</p>

                <div className="flex items-center gap-2 mt-auto">
                  <span className={`text-[10px] font-medium px-2 py-0.5 rounded border ${sent.badge}`}>{sent.label}</span>
                  <span className="text-slate-600 text-[10px]">
                    Score: <span className={`${sent.text} font-semibold`}>{item.score.toFixed(2)}</span>
                  </span>
                  <span className="text-slate-600 text-[10px]">{item.confidence}% conf</span>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
