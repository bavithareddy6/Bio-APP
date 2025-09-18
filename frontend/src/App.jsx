import React, { useMemo, useRef, useState } from 'react'
import Plot from 'react-plotly.js'
import './styles.css'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

function App() {
  const [genes, setGenes] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [heatmap, setHeatmap] = useState(null)
  const [notFound, setNotFound] = useState([])
  const [ext, setExt] = useState('fasta')
  const [wrap, setWrap] = useState(0)
  const inputRef = useRef(null)

  const remaining = Math.max(0, 10 - genes.length)

  const normalize = (arr) => arr.map(g => g.trim()).filter(Boolean)

  const addFromText = (text) => {
    const tokens = normalize(text.split(/[\s,]+/))
    if (tokens.length === 0) return
    setGenes(prev => normalize([...prev, ...tokens]).slice(0, 10))
    setInput('')
  }

  const onKeyDown = (e) => {
    if (e.key === 'Enter' || e.key === ',' ) {
      e.preventDefault()
      addFromText(input)
    }
  }

  const removeGene = (idx) => {
    setGenes(prev => prev.filter((_, i) => i !== idx))
  }

  const downloadFASTA = async () => {
    setError('')
    if (genes.length === 0) { setError('Enter up to 10 genes'); return }
    const url = `${API_BASE}/api/sequences/download?genes=${encodeURIComponent(genes.join(','))}&ext=${ext}&wrap=${wrap||0}`
    const res = await fetch(url)
    if (!res.ok) { setError('Download failed'); return }
    const blob = await res.blob()
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = `sequences.${ext}`
    document.body.appendChild(a)
    a.click()
    a.remove()
  }

  const downloadTSV = async () => {
    setError('')
    if (genes.length === 0) { setError('Enter up to 10 genes'); return }
    const url = `${API_BASE}/api/expressions/download?genes=${encodeURIComponent(genes.join(','))}`
    const res = await fetch(url)
    if (!res.ok) { setError('Download failed'); return }
    const blob = await res.blob()
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = 'expressions.tsv'
    document.body.appendChild(a)
    a.click()
    a.remove()
  }

  const viewHeatmap = async () => {
    setError('')
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/api/expressions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ genes })
      })
      if (!res.ok) throw new Error('API error')
      const data = await res.json()
      const z = data.rows.map(r => r.values)
      const y = data.rows.map(r => r.gene)
      setNotFound(data.not_found || [])
      setHeatmap({ x: data.samples, y, z, rows: data.rows })
    } catch (e) {
      setError('Failed to load heatmap')
    } finally {
      setLoading(false)
    }
  }

  const canAdd = remaining > 0

  return (
    <>
      <div className="topbar">
        <div className="topbar-inner">
          <div className="logo">🫐</div>
          <strong>Blueberry Breeding Program</strong>
        </div>
      </div>
      <div className="container">
      <header className="header">
        <h2>Blueberry breeding program task</h2>
        <p>Enter up to 10 gene names. Press Enter or comma to add.</p>
      </header>

      <div className="card">
        <div className="chips">
          {genes.map((g, i) => (
            <span key={`${g}-${i}`} className="chip">
              {g}
              <button className="chip-x" onClick={() => removeGene(i)} aria-label={`Remove ${g}`}>×</button>
            </span>
          ))}
          {canAdd && (
            <input
              ref={inputRef}
              className="chip-input"
              placeholder={genes.length === 0 ? 'GeneA, GeneB, ...' : ''}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={onKeyDown}
              onBlur={() => addFromText(input)}
            />
          )}
        </div>
        <div className="hint">Remaining: {remaining}</div>

        <div className="controls">
          <div className="control">
            <label>FASTA ext</label>
            <select value={ext} onChange={e => setExt(e.target.value)}>
              <option value="fasta">.fasta</option>
              <option value="fa">.fa</option>
            </select>
          </div>
          <div className="control">
            <label>Wrap width</label>
            <select value={wrap} onChange={e => setWrap(parseInt(e.target.value))}>
              <option value={0}>single line</option>
              <option value={60}>60</option>
              <option value={80}>80</option>
            </select>
          </div>
          <div className="spacer" />
          <button className="btn" onClick={downloadFASTA} disabled={genes.length===0}>Download FASTA</button>
          <button className="btn primary" onClick={viewHeatmap} disabled={loading || genes.length===0}>{loading ? 'Loading…' : 'View Heatmap'}</button>
          <button className="btn" onClick={downloadTSV} disabled={genes.length===0}>Download TSV</button>
        </div>

        {error && <div className="error">{error}</div>}
        {notFound.length > 0 && (
          <div className="warn">Missing genes: {notFound.join(', ')}</div>
        )}
      </div>

      {heatmap && (
        <div className="panel">
          <Plot
            data={[{
              type: 'heatmap',
              x: heatmap.x,
              y: heatmap.y,
              z: heatmap.z,
              colorscale: 'Viridis',
              hovertemplate: 'Gene: %{y}<br>Sample: %{x}<br>Value: %{z}<extra></extra>'
            }]}
            layout={{
              autosize: true,
              height: Math.max(320, 28 * heatmap.y.length),
              margin: { l: 180, r: 20, t: 40, b: 60 },
              title: 'Expression Heatmap',
              yaxis: { automargin: true, tickfont: { size: 10 } },
              xaxis: { automargin: true, tickangle: -45, tickfont: { size: 10 } }
            }}
            config={{ responsive: true, displayModeBar: false }}
            useResizeHandler
            style={{ width: '100%', height: Math.max(320, 28 * heatmap.y.length) }}
          />
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Gene</th>
                  {heatmap.x.map((s, i) => <th key={`h-${i}`}>{s}</th>)}
                </tr>
              </thead>
              <tbody>
                {heatmap.rows.map((r, i) => (
                  <tr key={`r-${i}`}>
                    <td>{r.gene}</td>
                    {r.values.map((v, j) => <td key={`c-${i}-${j}`}>{v}</td>)}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
      <div className="footer">© Blueberry breeding program task</div>
    </div>
    </>
  )
}

export default App
