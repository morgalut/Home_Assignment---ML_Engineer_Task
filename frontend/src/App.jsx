import React, { useState } from 'react'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const riskColorMap = {
  Low: '#16a34a',
  Medium: '#f97316',
  High: '#dc2626',
  unknown: '#6b7280'
}

function App() {
  const [ip, setIp] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)
  const [showRaw, setShowRaw] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setResult(null)

    const trimmed = ip.trim()
    if (!trimmed) {
      setError('Please enter an IP address.')
      return
    }

    setLoading(true)
    try {
      const resp = await fetch(
        `${API_BASE_URL}/api/analyze-ip?ip=${encodeURIComponent(trimmed)}`
      )

      if (!resp.ok) {
        const data = await resp.json().catch(() => ({}))
        throw new Error(data.detail || `Request failed with status ${resp.status}`)
      }

      const data = await resp.json()
      setResult(data)
    } catch (err) {
      console.error(err)
      setError(err.message || 'Unexpected error while calling backend.')
    } finally {
      setLoading(false)
    }
  }

  const renderSummary = () => {
    if (!result) return null

    const {
      ip,
      hostname,
      isp,
      country,
      abuse_score,
      recent_reports,
      vpn_proxy,
      fraud_score
    } = result

    return (
      <section style={sectionStyle}>
        <h2 style={sectionTitleStyle}>Summary</h2>
        <div style={gridStyle}>
          <InfoItem label="IP Address" value={ip} />
          <InfoItem label="Hostname" value={hostname || 'N/A'} />
          <InfoItem label="ISP" value={isp || 'N/A'} />
          <InfoItem label="Country" value={country || 'N/A'} />
          <InfoItem label="Abuse Score (AbuseIPDB)" value={abuse_score ?? 'N/A'} />
          <InfoItem label="Recent Reports" value={recent_reports ?? 'N/A'} />
          <InfoItem label="VPN/Proxy" value={vpn_proxy ? 'Yes' : 'No'} />
          <InfoItem label="Fraud Score (IPQS)" value={fraud_score ?? 'N/A'} />
        </div>
      </section>
    )
  }

  const renderRisk = () => {
    if (!result) return null

    const {
      risk_level = 'unknown',
      risk_analysis,
      recommendations = [],
      model_used,
      confidence
    } = result

    const color = riskColorMap[risk_level] || riskColorMap.unknown

    return (
      <section style={sectionStyle}>
        <h2 style={sectionTitleStyle}>AI Risk Assessment</h2>

        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
          <div
            style={{
              padding: '0.5rem 1rem',
              borderRadius: '999px',
              backgroundColor: color,
              color: 'white',
              fontWeight: 600
            }}
          >
            Risk Level: {risk_level}
          </div>
          {typeof confidence === 'number' && (
            <span style={{ fontSize: '0.9rem', color: '#4b5563' }}>
              Confidence: {(confidence * 100).toFixed(1)}%
            </span>
          )}
          {model_used && (
            <span
              style={{
                fontSize: '0.8rem',
                padding: '0.25rem 0.75rem',
                borderRadius: '999px',
                backgroundColor: '#e5e7eb',
                color: '#374151'
              }}
            >
              Model: {model_used}
            </span>
          )}
        </div>

        {risk_analysis && (
          <p style={{ marginTop: '1rem', lineHeight: 1.5 }}>{risk_analysis}</p>
        )}

        {recommendations.length > 0 && (
          <div style={{ marginTop: '1rem' }}>
            <h3 style={{ margin: '0 0 0.5rem 0', fontSize: '1rem' }}>Recommendations</h3>
            <ul style={{ paddingLeft: '1.25rem', margin: 0 }}>
              {recommendations.map((rec, idx) => (
                <li key={idx} style={{ marginBottom: '0.25rem' }}>
                  {rec}
                </li>
              ))}
            </ul>
          </div>
        )}
      </section>
    )
  }

  const renderRawSources = () => {
    if (!result || !result.raw_sources) return null

    return (
      <section style={sectionStyle}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2 style={sectionTitleStyle}>Raw Threat Intelligence</h2>
          <button
            type="button"
            onClick={() => setShowRaw((v) => !v)}
            style={secondaryButtonStyle}
          >
            {showRaw ? 'Hide raw JSON' : 'Show raw JSON'}
          </button>
        </div>

        {showRaw && (
          <pre
            style={{
              marginTop: '0.75rem',
              padding: '0.75rem',
              backgroundColor: '#0f172a',
              color: '#e5e7eb',
              borderRadius: '0.5rem',
              maxHeight: '400px',
              overflow: 'auto',
              fontSize: '0.8rem'
            }}
          >
            {JSON.stringify(result.raw_sources, null, 2)}
          </pre>
        )}
      </section>
    )
  }

  return (
    <div style={pageStyle}>
      <header style={headerStyle}>
        <h1 style={{ margin: 0, fontSize: '1.75rem' }}>IP Threat Intelligence</h1>
        <p style={{ marginTop: '0.5rem', color: '#6b7280', fontSize: '0.95rem' }}>
          Enter an IP address to aggregate threat-intel data and get an AI-powered risk
          assessment.
        </p>
      </header>

      <main style={mainStyle}>
        <form onSubmit={handleSubmit} style={formStyle}>
          <label
            htmlFor="ip"
            style={{
              display: 'block',
              fontSize: '0.9rem',
              fontWeight: 500,
              marginBottom: '0.25rem'
            }}
          >
            IP Address
          </label>
          <input
            id="ip"
            type="text"
            placeholder="e.g. 8.8.8.8"
            value={ip}
            onChange={(e) => setIp(e.target.value)}
            style={inputStyle}
          />
          <button type="submit" style={primaryButtonStyle} disabled={loading}>
            {loading ? 'Analyzing…' : 'Analyze IP'}
          </button>
        </form>

        {error && (
          <div style={errorStyle}>
            {error}
          </div>
        )}

        {renderSummary()}
        {renderRisk()}
        {renderRawSources()}
      </main>
    </div>
  )
}

// -------- Small presentation helpers --------

const pageStyle = {
  minHeight: '100vh',
  backgroundColor: '#f3f4f6',
  padding: '2rem 1rem'
}

const headerStyle = {
  maxWidth: '900px',
  margin: '0 auto 1.5rem auto'
}

const mainStyle = {
  maxWidth: '900px',
  margin: '0 auto'
}

const formStyle = {
  display: 'flex',
  flexWrap: 'wrap',
  gap: '0.5rem',
  alignItems: 'center',
  padding: '1rem',
  backgroundColor: 'white',
  borderRadius: '0.75rem',
  boxShadow: '0 1px 3px rgba(0,0,0,0.06)'
}

const inputStyle = {
  flex: '1 1 200px',
  padding: '0.5rem 0.75rem',
  borderRadius: '0.5rem',
  border: '1px solid #d1d5db',
  fontSize: '0.95rem'
}

const primaryButtonStyle = {
  padding: '0.6rem 1.2rem',
  borderRadius: '999px',
  border: 'none',
  backgroundColor: '#2563eb',
  color: 'white',
  fontWeight: 600,
  cursor: 'pointer'
}

const secondaryButtonStyle = {
  padding: '0.35rem 0.9rem',
  borderRadius: '999px',
  border: '1px solid #9ca3af',
  backgroundColor: 'white',
  color: '#374151',
  fontSize: '0.8rem',
  cursor: 'pointer'
}

const sectionStyle = {
  marginTop: '1.5rem',
  padding: '1rem',
  backgroundColor: 'white',
  borderRadius: '0.75rem',
  boxShadow: '0 1px 3px rgba(0,0,0,0.06)'
}

const sectionTitleStyle = {
  margin: 0,
  fontSize: '1.1rem',
  fontWeight: 600
}

const gridStyle = {
  marginTop: '0.75rem',
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
  gap: '0.75rem'
}

const errorStyle = {
  marginTop: '1rem',
  padding: '0.75rem 1rem',
  backgroundColor: '#fee2e2',
  borderRadius: '0.5rem',
  color: '#b91c1c',
  fontSize: '0.9rem'
}

function InfoItem({ label, value }) {
  return (
    <div>
      <div style={{ fontSize: '0.75rem', color: '#6b7280', textTransform: 'uppercase' }}>
        {label}
      </div>
      <div style={{ fontSize: '0.95rem', fontWeight: 500 }}>{String(value)}</div>
    </div>
  )
}

export default App
