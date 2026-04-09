// Placeholder data — replace with live options API feed
const mockOptions = [
  { strike: 180, callBid: 5.20, callAsk: 5.40, callIV: 0.32, callOI: 1200, putBid: 2.10, putAsk: 2.25, putIV: 0.35, putOI: 980 },
  { strike: 185, callBid: 3.10, callAsk: 3.30, callIV: 0.29, callOI: 3400, putBid: 4.00, putAsk: 4.20, putIV: 0.33, putOI: 2100 },
  { strike: 190, callBid: 1.50, callAsk: 1.65, callIV: 0.27, callOI: 5100, putBid: 6.80, putAsk: 7.00, putIV: 0.31, putOI: 4200 },
  { strike: 195, callBid: 0.60, callAsk: 0.70, callIV: 0.26, callOI: 2800, putBid: 10.20, putAsk: 10.50, putIV: 0.30, putOI: 1800 },
  { strike: 200, callBid: 0.20, callAsk: 0.28, callIV: 0.25, callOI: 900,  putBid: 14.50, putAsk: 14.80, putIV: 0.29, putOI: 700 },
]

const ATM_STRIKE = 190

const maxOI = Math.max(...mockOptions.flatMap((r) => [r.callOI, r.putOI]))

export default function OptionChain() {
  return (
    <div className="bg-[#0d1526] border border-white/[0.07] rounded-2xl overflow-hidden">
      {/* Header */}
      <div className="px-5 py-4 border-b border-white/[0.06] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-5 h-5 rounded bg-violet-500/20 flex items-center justify-center">
            <span className="text-violet-400 text-xs">⊞</span>
          </div>
          <h2 className="text-white font-semibold text-base">Option Chain</h2>
        </div>
        <div className="flex items-center gap-4 text-xs text-slate-500">
          <span>Expiry: <span className="text-slate-300 font-medium">Apr 18, 2026</span></span>
          <span className="w-px h-3 bg-white/[0.08]" />
          <span>Underlying: <span className="text-white font-semibold">$187.42</span></span>
          <span className="w-px h-3 bg-white/[0.08]" />
          <span>DTE: <span className="text-amber-400 font-medium">9</span></span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          {/* Group headers */}
          <thead>
            <tr>
              <th colSpan={5} className="py-2.5 text-center text-emerald-400 font-semibold text-xs uppercase tracking-wider bg-emerald-500/5 border-b border-emerald-500/10">
                Calls
              </th>
              <th className="py-2.5 bg-[#080c15] border-b border-white/[0.06]" />
              <th colSpan={5} className="py-2.5 text-center text-red-400 font-semibold text-xs uppercase tracking-wider bg-red-500/5 border-b border-red-500/10">
                Puts
              </th>
            </tr>
            <tr className="text-slate-500 border-b border-white/[0.06]">
              <th className="py-2 px-4 text-left font-normal">OI</th>
              <th className="py-2 px-4 font-normal">IV</th>
              <th className="py-2 px-4 font-normal">Bid</th>
              <th className="py-2 px-4 font-normal">Ask</th>
              <th className="py-2 px-4 font-normal">OI Bar</th>
              <th className="py-2 px-4 text-center font-semibold text-slate-300 bg-[#080c15]">Strike</th>
              <th className="py-2 px-4 font-normal">OI Bar</th>
              <th className="py-2 px-4 font-normal">Bid</th>
              <th className="py-2 px-4 font-normal">Ask</th>
              <th className="py-2 px-4 font-normal">IV</th>
              <th className="py-2 px-4 text-right font-normal">OI</th>
            </tr>
          </thead>

          <tbody>
            {mockOptions.map((row) => {
              const isATM = row.strike === ATM_STRIKE
              const callBarW = Math.round((row.callOI / maxOI) * 100)
              const putBarW = Math.round((row.putOI / maxOI) * 100)
              return (
                <tr
                  key={row.strike}
                  className={`border-b border-white/[0.04] transition-colors ${
                    isATM
                      ? 'bg-amber-500/5 border-amber-500/10'
                      : 'hover:bg-white/[0.02]'
                  }`}
                >
                  {/* Call OI */}
                  <td className="py-3 px-4 text-left text-slate-400 font-mono">{row.callOI.toLocaleString()}</td>
                  {/* Call IV */}
                  <td className="py-3 px-4 text-center text-slate-400 font-mono">{(row.callIV * 100).toFixed(0)}%</td>
                  {/* Call Bid */}
                  <td className="py-3 px-4 text-center text-emerald-400 font-mono font-medium">{row.callBid.toFixed(2)}</td>
                  {/* Call Ask */}
                  <td className="py-3 px-4 text-center text-emerald-300 font-mono">{row.callAsk.toFixed(2)}</td>
                  {/* Call OI bar — right aligned */}
                  <td className="py-3 px-4">
                    <div className="flex items-center justify-end">
                      <div className="w-20 h-1.5 bg-white/[0.05] rounded-full overflow-hidden">
                        <div
                          className="h-full bg-emerald-500/50 rounded-full"
                          style={{ width: `${callBarW}%` }}
                        />
                      </div>
                    </div>
                  </td>

                  {/* Strike — center divider */}
                  <td className={`py-3 px-4 text-center font-bold bg-[#080c15] ${isATM ? 'text-amber-400' : 'text-white'}`}>
                    {row.strike}
                    {isATM && (
                      <span className="ml-1.5 text-[9px] bg-amber-500/15 text-amber-400 border border-amber-500/25 rounded px-1 py-0.5 font-semibold">
                        ATM
                      </span>
                    )}
                  </td>

                  {/* Put OI bar — left aligned */}
                  <td className="py-3 px-4">
                    <div className="flex items-center justify-start">
                      <div className="w-20 h-1.5 bg-white/[0.05] rounded-full overflow-hidden">
                        <div
                          className="h-full bg-red-500/50 rounded-full"
                          style={{ width: `${putBarW}%` }}
                        />
                      </div>
                    </div>
                  </td>

                  {/* Put Bid */}
                  <td className="py-3 px-4 text-center text-red-400 font-mono font-medium">{row.putBid.toFixed(2)}</td>
                  {/* Put Ask */}
                  <td className="py-3 px-4 text-center text-red-300 font-mono">{row.putAsk.toFixed(2)}</td>
                  {/* Put IV */}
                  <td className="py-3 px-4 text-center text-slate-400 font-mono">{(row.putIV * 100).toFixed(0)}%</td>
                  {/* Put OI */}
                  <td className="py-3 px-4 text-right text-slate-400 font-mono">{row.putOI.toLocaleString()}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
