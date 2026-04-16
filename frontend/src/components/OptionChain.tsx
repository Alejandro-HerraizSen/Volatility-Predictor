import { useState, useEffect } from 'react'
import Papa from 'papaparse'

interface RawRow {
  event_id: string
  underlying_ticker: string
  earnings_date: string
  expiration_date: string
  option_ticker: string
  strike: string
  contract_type: string
  bar_date: string
  relative_day: string
  open: string
  high: string
  low: string
  close: string
  volume: string
  vwap: string
  transactions: string
}

interface OptionRow {
  strike: number
  callClose: number
  callVwap: number
  callVolume: number
  putClose: number
  putVwap: number
  putVolume: number
}

interface EventOption {
  label: string
  file: string
}

const EVENTS: Record<string, EventOption[]> = {
  AAPL:  [
    { label: 'Q4 2024 – Nov 1, 2024',  file: 'options_AAPL_Q4_2024_2024-11-01_bars.csv' },
    { label: 'Q4 2025 – Oct 31, 2025', file: 'options_AAPL_Q4_2025_2025-10-31_bars.csv' },
  ],
  ADBE:  [
    { label: 'Q4 2024 – Jan 13, 2025', file: 'options_ADBE_Q4_2024_2025-01-13_bars.csv' },
    { label: 'Q4 2025 – Jan 15, 2026', file: 'options_ADBE_Q4_2025_2026-01-15_bars.csv' },
  ],
  AMD:   [
    { label: 'Q4 2024 – Feb 5, 2025',  file: 'options_AMD_Q4_2024_2025-02-05_bars.csv' },
    { label: 'Q4 2025 – Feb 4, 2026',  file: 'options_AMD_Q4_2025_2026-02-04_bars.csv' },
  ],
  AMZN:  [
    { label: 'Q4 2024 – Feb 7, 2025',  file: 'options_AMZN_Q4_2024_2025-02-07_bars.csv' },
    { label: 'Q4 2025 – Feb 6, 2026',  file: 'options_AMZN_Q4_2025_2026-02-06_bars.csv' },
  ],
  CRM:   [
    { label: 'Q4 2025 – Mar 5, 2025',  file: 'options_CRM_Q4_2025_2025-03-05_bars.csv' },
    { label: 'Q4 2026 – Mar 2, 2026',  file: 'options_CRM_Q4_2026_2026-03-02_bars.csv' },
  ],
  GOOGL: [
    { label: 'Q4 2024 – Feb 5, 2025',  file: 'options_GOOGL_Q4_2024_2025-02-05_bars.csv' },
    { label: 'Q4 2025 – Feb 5, 2026',  file: 'options_GOOGL_Q4_2025_2026-02-05_bars.csv' },
  ],
  MSFT:  [
    { label: 'Q4 2024 – Jul 30, 2024', file: 'options_MSFT_Q4_2024_2024-07-30_bars.csv' },
    { label: 'Q4 2025 – Jul 30, 2025', file: 'options_MSFT_Q4_2025_2025-07-30_bars.csv' },
  ],
  NFLX:  [
    { label: 'Q4 2025 – Jan 23, 2026', file: 'options_NFLX_Q4_2025_2026-01-23_bars.csv' },
  ],
  NVDA:  [
    { label: 'Q4 2025 – Feb 26, 2025', file: 'options_NVDA_Q4_2025_2025-02-26_bars.csv' },
    { label: 'Q4 2026 – Feb 25, 2026', file: 'options_NVDA_Q4_2026_2026-02-25_bars.csv' },
  ],
  TSLA:  [
    { label: 'Q4 2024 – Jan 30, 2025', file: 'options_TSLA_Q4_2024_2025-01-30_bars.csv' },
    { label: 'Q4 2025 – Jan 29, 2026', file: 'options_TSLA_Q4_2025_2026-01-29_bars.csv' },
  ],
}

const TICKERS = Object.keys(EVENTS)

function buildChain(rows: RawRow[]): { chain: OptionRow[]; expiry: string; earningsDate: string } {
  const earningsDay = rows.filter((r) => r.relative_day === 'earnings_day')
  const expiry = rows[0]?.expiration_date ?? ''
  const earningsDate = rows[0]?.earnings_date ?? ''

  const calls: Record<number, RawRow> = {}
  const puts: Record<number, RawRow> = {}

  for (const row of earningsDay) {
    const strike = parseFloat(row.strike)
    if (row.contract_type === 'call') calls[strike] = row
    else if (row.contract_type === 'put') puts[strike] = row
  }

  const strikes = [...new Set([...Object.keys(calls), ...Object.keys(puts)].map(Number))].sort((a, b) => a - b)

  const chain: OptionRow[] = strikes.map((strike) => ({
    strike,
    callClose:  parseFloat(calls[strike]?.close  ?? '0'),
    callVwap:   parseFloat(calls[strike]?.vwap   ?? '0'),
    callVolume: parseInt(calls[strike]?.volume   ?? '0'),
    putClose:   parseFloat(puts[strike]?.close   ?? '0'),
    putVwap:    parseFloat(puts[strike]?.vwap    ?? '0'),
    putVolume:  parseInt(puts[strike]?.volume    ?? '0'),
  }))

  return { chain, expiry, earningsDate }
}

export default function OptionChain() {
  const [ticker, setTicker] = useState('AAPL')
  const [eventIdx, setEventIdx] = useState(0)
  const [chain, setChain] = useState<OptionRow[]>([])
  const [meta, setMeta] = useState({ expiry: '', earningsDate: '' })
  const [loading, setLoading] = useState(true)

  const events = EVENTS[ticker]

  useEffect(() => {
    setEventIdx(0)
  }, [ticker])

  useEffect(() => {
    setLoading(true)
    const file = EVENTS[ticker][eventIdx]?.file
    if (!file) return
    fetch(`/data/${file}`)
      .then((r) => r.text())
      .then((csv) => {
        const result = Papa.parse<RawRow>(csv, { header: true, skipEmptyLines: true })
        const { chain, expiry, earningsDate } = buildChain(result.data)
        setChain(chain)
        setMeta({ expiry, earningsDate })
        setLoading(false)
      })
  }, [ticker, eventIdx])

  const maxVol = chain.length ? Math.max(...chain.flatMap((r) => [r.callVolume, r.putVolume])) : 1
  const atmStrike = chain.length ? chain[Math.floor(chain.length / 2)]?.strike : null

  return (
    <div className="bg-[#0d1526] border border-white/[0.07] rounded-2xl overflow-hidden flex flex-col h-full">
      {/* Header */}
      <div className="px-5 py-4 border-b border-white/[0.06] flex flex-wrap items-center gap-4 justify-between">
        <div className="flex items-center gap-2">
          <div className="w-5 h-5 rounded bg-violet-500/20 flex items-center justify-center">
            <span className="text-violet-400 text-xs">⊞</span>
          </div>
          <h2 className="text-white font-semibold text-base">Option Chain</h2>
          <span className="text-[10px] text-slate-500 bg-[#080c15] border border-white/[0.06] rounded-full px-2 py-0.5 ml-1">Earnings Day</span>
        </div>

        {/* Selectors */}
        <div className="flex items-center gap-2">
          {/* Ticker pills */}
          <div className="flex items-center gap-1 bg-[#080c15] border border-white/[0.06] rounded-lg p-1">
            {TICKERS.map((t) => (
              <button
                key={t}
                onClick={() => setTicker(t)}
                className={`px-2.5 py-1 rounded-md text-xs font-medium transition-all ${
                  ticker === t
                    ? 'bg-blue-600/80 text-white shadow'
                    : 'text-slate-500 hover:text-slate-300'
                }`}
              >
                {t}
              </button>
            ))}
          </div>

          {/* Event dropdown */}
          <select
            value={eventIdx}
            onChange={(e) => setEventIdx(Number(e.target.value))}
            className="bg-[#080c15] border border-white/[0.08] rounded-lg px-3 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-blue-500/50"
          >
            {events.map((ev, i) => (
              <option key={i} value={i}>{ev.label}</option>
            ))}
          </select>

          {/* Meta */}
          {!loading && (
            <span className="text-xs text-slate-600">
              Expiry: <span className="text-slate-400">{meta.expiry}</span>
            </span>
          )}
        </div>
      </div>

      {loading ? (
        <div className="text-slate-500 text-sm text-center py-16">Loading options data...</div>
      ) : (
        <div className="overflow-auto flex-1">
          <table className="w-full text-xs">
            <thead>
              <tr>
                <th colSpan={4} className="py-2.5 text-center text-emerald-400 font-semibold text-xs uppercase tracking-wider bg-emerald-500/5 border-b border-emerald-500/10">
                  Calls
                </th>
                <th className="py-2.5 bg-[#080c15] border-b border-white/[0.06]" />
                <th colSpan={4} className="py-2.5 text-center text-red-400 font-semibold text-xs uppercase tracking-wider bg-red-500/5 border-b border-red-500/10">
                  Puts
                </th>
              </tr>
              <tr className="text-slate-500 border-b border-white/[0.06]">
                <th className="py-2 px-4 text-left font-normal">Volume</th>
                <th className="py-2 px-4 font-normal">VWAP</th>
                <th className="py-2 px-4 font-normal">Close</th>
                <th className="py-2 px-4 font-normal">Vol Bar</th>
                <th className="py-2 px-4 text-center font-semibold text-slate-300 bg-[#080c15]">Strike</th>
                <th className="py-2 px-4 font-normal">Vol Bar</th>
                <th className="py-2 px-4 font-normal">Close</th>
                <th className="py-2 px-4 font-normal">VWAP</th>
                <th className="py-2 px-4 text-right font-normal">Volume</th>
              </tr>
            </thead>
            <tbody>
              {chain.map((row) => {
                const isATM = row.strike === atmStrike
                const callBarW = Math.round((row.callVolume / maxVol) * 100)
                const putBarW  = Math.round((row.putVolume  / maxVol) * 100)
                return (
                  <tr
                    key={row.strike}
                    className={`border-b border-white/[0.04] transition-colors ${isATM ? 'bg-amber-500/5 border-amber-500/10' : 'hover:bg-white/[0.02]'}`}
                  >
                    <td className="py-3 px-4 text-left text-slate-400 font-mono">{row.callVolume.toLocaleString()}</td>
                    <td className="py-3 px-4 text-center text-slate-400 font-mono">${row.callVwap.toFixed(2)}</td>
                    <td className="py-3 px-4 text-center text-emerald-400 font-mono font-medium">${row.callClose.toFixed(2)}</td>
                    <td className="py-3 px-4">
                      <div className="flex justify-end">
                        <div className="w-20 h-1.5 bg-white/[0.05] rounded-full overflow-hidden">
                          <div className="h-full bg-emerald-500/50 rounded-full" style={{ width: `${callBarW}%` }} />
                        </div>
                      </div>
                    </td>
                    <td className={`py-3 px-4 text-center font-bold bg-[#080c15] ${isATM ? 'text-amber-400' : 'text-white'}`}>
                      {row.strike}
                      {isATM && (
                        <span className="ml-1.5 text-[9px] bg-amber-500/15 text-amber-400 border border-amber-500/25 rounded px-1 py-0.5 font-semibold">ATM</span>
                      )}
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex justify-start">
                        <div className="w-20 h-1.5 bg-white/[0.05] rounded-full overflow-hidden">
                          <div className="h-full bg-red-500/50 rounded-full" style={{ width: `${putBarW}%` }} />
                        </div>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-center text-red-400 font-mono font-medium">${row.putClose.toFixed(2)}</td>
                    <td className="py-3 px-4 text-center text-slate-400 font-mono">${row.putVwap.toFixed(2)}</td>
                    <td className="py-3 px-4 text-right text-slate-400 font-mono">{row.putVolume.toLocaleString()}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
