import { useState } from 'react'

type Source = 'social' | 'earnings' | 'news'
type Sentiment = 'positive' | 'negative' | 'neutral'
type Impact = 'high' | 'medium' | 'low'

interface FeedItem {
  id: number
  source: Source
  handle: string
  time: string
  text: string
  sentiment: Sentiment
  score: number
  confidence: number
  impact: Impact
}

// Placeholder — replace with live WebSocket feed
const mockFeed: FeedItem[] = [
  { id: 1, source: 'earnings', handle: 'CEO – Tim Cook', time: '10:05:12 AM', text: 'We are incredibly confident in our Q3 pipeline. Services revenue hit an all-time high this quarter.', sentiment: 'positive', score: 78.4, confidence: 91, impact: 'high' },
  { id: 2, source: 'social', handle: '@trader3294', time: '10:04:47 AM', text: 'Stock price reaction seems overdone, fundamentals still strong.', sentiment: 'positive', score: 67.0, confidence: 74, impact: 'medium' },
  { id: 3, source: 'earnings', handle: 'CFO – Luca Maestri', time: '10:03:30 AM', text: 'Supply chain headwinds remain a concern heading into Q4. Margins may compress slightly.', sentiment: 'negative', score: 38.2, confidence: 85, impact: 'high' },
  { id: 4, source: 'news', handle: 'Reuters', time: '10:02:55 AM', text: 'Apple beats EPS estimates by $0.12 but guidance falls short of Wall Street expectations.', sentiment: 'neutral', score: 51.0, confidence: 68, impact: 'medium' },
  { id: 5, source: 'social', handle: '@trader2768', time: '10:01:33 AM', text: 'Love the transparency in this call, very bullish signal on services.', sentiment: 'positive', score: 58.5, confidence: 86, impact: 'medium' },
  { id: 6, source: 'earnings', handle: 'CEO – Tim Cook', time: '9:59:10 AM', text: 'We do not provide forward guidance on unit sales. That practice will not change.', sentiment: 'negative', score: 32.1, confidence: 77, impact: 'low' },
  { id: 7, source: 'news', handle: 'Bloomberg', time: '9:57:40 AM', text: 'AAPL shares dip 2% in after-hours trading following muted Q4 revenue outlook.', sentiment: 'negative', score: 29.5, confidence: 89, impact: 'high' },
]

const avgSentiment = Math.round(mockFeed.reduce((s, i) => s + i.score, 0) / mockFeed.length)

const sourceConfig: Record<Source, { label: string; icon: string; bg: string; text: string }> = {
  social:   { label: 'Social',        icon: '𝕏',  bg: 'bg-violet-500/15', text: 'text-violet-400' },
  earnings: { label: 'Earnings Call', icon: 'EC', bg: 'bg-blue-500/15',   text: 'text-blue-400' },
  news:     { label: 'News',          icon: 'NW', bg: 'bg-orange-500/15', text: 'text-orange-400' },
}

const sentimentConfig: Record<Sentiment, { border: string; badge: string; text: string; label: string; dot: string }> = {
  positive: { border: 'border-l-emerald-500', badge: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20', text: 'text-emerald-400', label: '↗ Positive', dot: 'bg-emerald-400' },
  negative: { border: 'border-l-red-500',     badge: 'bg-red-500/10 text-red-400 border-red-500/20',             text: 'text-red-400',     label: '↘ Negative', dot: 'bg-red-400' },
  neutral:  { border: 'border-l-slate-500',   badge: 'bg-slate-500/10 text-slate-400 border-slate-500/20',       text: 'text-slate-400',   label: '→ Neutral',  dot: 'bg-slate-400' },
}

const impactConfig: Record<Impact, string> = {
  high:   'text-red-400 border-red-500/30 bg-red-500/5',
  medium: 'text-amber-400 border-amber-500/30 bg-amber-500/5',
  low:    'text-slate-500 border-slate-500/30 bg-slate-500/5',
}

export default function SentimentPanel() {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="bg-[#0d1526] border border-white/[0.07] rounded-2xl overflow-hidden flex flex-col">
      {/* Header */}
      <div className="px-5 pt-5 pb-4 flex items-start justify-between border-b border-white/[0.06]">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <div className="w-5 h-5 rounded bg-blue-500/20 flex items-center justify-center">
              <span className="text-blue-400 text-xs">≋</span>
            </div>
            <h2 className="text-white font-semibold text-base">Live Sentiment Feed</h2>
          </div>
          <p className="text-slate-500 text-xs">Real-time analysis from earnings calls, social media, and news</p>
        </div>

        <div className="flex items-center gap-3">
          {/* Avg sentiment pill */}
          <div className="bg-[#080c15] border border-white/[0.07] rounded-xl px-4 py-2 text-center">
            <p className="text-slate-500 text-[10px] uppercase tracking-wider mb-0.5">Avg Sentiment</p>
            <p className={`text-xl font-bold ${avgSentiment >= 55 ? 'text-emerald-400' : avgSentiment >= 40 ? 'text-amber-400' : 'text-red-400'}`}>
              {avgSentiment}%
            </p>
          </div>
          <div className="flex items-center gap-1.5 text-xs text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 rounded-full px-2.5 py-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            LIVE
          </div>
        </div>
      </div>

      {/* Info accordion */}
      <div className="mx-5 mt-4 rounded-xl overflow-hidden border border-blue-500/15 bg-blue-500/5">
        <button
          onClick={() => setExpanded(!expanded)}
          className="w-full flex items-center justify-between px-4 py-2.5 text-xs text-blue-400 font-medium"
        >
          <span className="flex items-center gap-2">
            <span className="w-4 h-4 rounded-full border border-blue-500/40 flex items-center justify-center text-[10px]">i</span>
            Understanding Sentiment Metrics
          </span>
          <span className={`text-slate-500 transition-transform duration-200 ${expanded ? 'rotate-180' : ''}`}>▾</span>
        </button>
        {expanded && (
          <div className="px-4 pb-3 pt-0 text-xs text-slate-500 flex flex-col gap-1.5 border-t border-blue-500/10">
            <p><span className="text-slate-300">Score</span> — raw sentiment 0 (bearish) to 100 (bullish).</p>
            <p><span className="text-slate-300">Confidence</span> — model certainty in the classification.</p>
            <p><span className="text-slate-300">Impact</span> — estimated influence on implied volatility.</p>
          </div>
        )}
      </div>

      {/* Feed */}
      <div className="flex flex-col gap-3 p-5 max-h-[560px] overflow-y-auto">
        {mockFeed.map((item) => {
          const src = sourceConfig[item.source]
          const sent = sentimentConfig[item.sentiment]
          return (
            <div
              key={item.id}
              className={`bg-[#080c15] border border-white/[0.06] border-l-2 ${sent.border} rounded-xl p-4 flex flex-col gap-3 hover:border-white/[0.12] hover:border-l-current transition-all duration-150`}
            >
              {/* Top row */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <div className={`w-8 h-8 rounded-lg ${src.bg} flex items-center justify-center ${src.text} text-xs font-bold`}>
                    {src.icon}
                  </div>
                  <div>
                    <p className="text-white text-sm font-medium leading-none mb-0.5">{src.label}</p>
                    <p className="text-slate-500 text-xs">{item.handle}</p>
                  </div>
                </div>
                <span className="text-slate-600 text-xs font-mono">{item.time}</span>
              </div>

              {/* Text */}
              <p className="text-slate-300 text-sm leading-relaxed">{item.text}</p>

              {/* Bottom row */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <span className={`text-xs font-medium px-2.5 py-0.5 rounded-md border ${sent.badge}`}>
                    {sent.label}
                  </span>
                  <span className="text-slate-600 text-xs">
                    Score: <span className={`${sent.text} font-semibold`}>{item.score.toFixed(1)}</span>
                  </span>
                  <span className="text-slate-600 text-xs">
                    Confidence: <span className="text-slate-300 font-semibold">{item.confidence}%</span>
                  </span>
                </div>
                <span className={`text-xs border rounded-full px-2.5 py-0.5 font-medium ${impactConfig[item.impact]}`}>
                  {item.impact} impact
                </span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
