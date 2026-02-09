import React, { useState } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8001';

const defaultValues = {
  profile_pic: 1,
  nums_length_username: 0,
  fullname_words: 2,
  nums_length_fullname: 0,
  name_eq_username: 0,
  description_length: 50,
  external_url: 0,
  private: 0,
  posts: 30,
  followers: 500,
  following: 300,
};

const fieldLabels = {
  profile_pic: { label: 'Has Profile Picture', type: 'toggle' },
  nums_length_username: { label: 'Username Digit Ratio', type: 'range', min: 0, max: 1, step: 0.01 },
  fullname_words: { label: 'Full Name Word Count', type: 'number', min: 0, max: 20 },
  nums_length_fullname: { label: 'Full Name Digit Ratio', type: 'range', min: 0, max: 1, step: 0.01 },
  name_eq_username: { label: 'Name = Username', type: 'toggle' },
  description_length: { label: 'Bio Length (chars)', type: 'number', min: 0, max: 500 },
  external_url: { label: 'Has External URL', type: 'toggle' },
  private: { label: 'Private Account', type: 'toggle' },
  posts: { label: 'Number of Posts', type: 'number', min: 0, max: 100000 },
  followers: { label: 'Followers', type: 'number', min: 0, max: 100000000 },
  following: { label: 'Following', type: 'number', min: 0, max: 100000000 },
};

function App() {
  const [formData, setFormData] = useState(defaultValues);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [useGemini, setUseGemini] = useState(true);

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const endpoint = useGemini ? '/predict' : '/predict/quick';
      const response = await axios.post(`${API_URL}${endpoint}`, formData);
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to connect to API. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFormData(defaultValues);
    setResult(null);
    setError(null);
  };

  const loadFakeExample = () => {
    setFormData({
      profile_pic: 0,
      nums_length_username: 0.55,
      fullname_words: 1,
      nums_length_fullname: 0.4,
      name_eq_username: 1,
      description_length: 0,
      external_url: 0,
      private: 0,
      posts: 2,
      followers: 15,
      following: 1500,
    });
    setResult(null);
  };

  const loadRealExample = () => {
    setFormData({
      profile_pic: 1,
      nums_length_username: 0,
      fullname_words: 2,
      nums_length_fullname: 0,
      name_eq_username: 0,
      description_length: 85,
      external_url: 1,
      private: 0,
      posts: 350,
      followers: 12000,
      following: 800,
    });
    setResult(null);
  };

  const getRiskColor = (score) => {
    if (score >= 0.7) return '#ef4444';
    if (score >= 0.5) return '#f59e0b';
    if (score >= 0.3) return '#3b82f6';
    return '#22c55e';
  };

  return (
    <div style={styles.app}>
      <header style={styles.header}>
        <h1 style={styles.title}>🔍 Fake Account Detector</h1>
        <p style={styles.subtitle}>Hybrid AI System — XGBoost + Gemini 2.5</p>
      </header>

      <main style={styles.main}>
        <div style={styles.grid}>
          {/* Input Form */}
          <div style={styles.card}>
            <h2 style={styles.cardTitle}>Account Features</h2>
            <div style={styles.presets}>
              <button onClick={loadFakeExample} style={{ ...styles.presetBtn, ...styles.presetFake }}>
                Load Fake Example
              </button>
              <button onClick={loadRealExample} style={{ ...styles.presetBtn, ...styles.presetReal }}>
                Load Real Example
              </button>
            </div>

            <form onSubmit={handleSubmit}>
              {Object.entries(fieldLabels).map(([key, cfg]) => (
                <div key={key} style={styles.field}>
                  <label style={styles.label}>
                    {cfg.label}
                    {cfg.type === 'range' && (
                      <span style={styles.rangeValue}>{Number(formData[key]).toFixed(2)}</span>
                    )}
                  </label>
                  {cfg.type === 'toggle' ? (
                    <div
                      onClick={() => handleChange(key, formData[key] === 1 ? 0 : 1)}
                      style={{
                        ...styles.toggle,
                        backgroundColor: formData[key] === 1 ? '#3b82f6' : '#374151',
                      }}
                    >
                      <div style={{
                        ...styles.toggleKnob,
                        transform: formData[key] === 1 ? 'translateX(22px)' : 'translateX(2px)',
                      }} />
                      <span style={styles.toggleLabel}>{formData[key] === 1 ? 'Yes' : 'No'}</span>
                    </div>
                  ) : cfg.type === 'range' ? (
                    <input
                      type="range"
                      min={cfg.min}
                      max={cfg.max}
                      step={cfg.step}
                      value={formData[key]}
                      onChange={e => handleChange(key, parseFloat(e.target.value))}
                      style={styles.rangeInput}
                    />
                  ) : (
                    <input
                      type="number"
                      min={cfg.min}
                      max={cfg.max}
                      value={formData[key]}
                      onChange={e => handleChange(key, parseInt(e.target.value) || 0)}
                      style={styles.input}
                    />
                  )}
                </div>
              ))}

              <div style={styles.field}>
                <label style={styles.label}>
                  <input
                    type="checkbox"
                    checked={useGemini}
                    onChange={e => setUseGemini(e.target.checked)}
                    style={{ marginRight: 8 }}
                  />
                  Include Gemini AI Analysis
                </label>
              </div>

              <div style={styles.buttonRow}>
                <button type="submit" disabled={loading} style={styles.submitBtn}>
                  {loading ? '⏳ Analyzing...' : '🔍 Analyze Account'}
                </button>
                <button type="button" onClick={handleReset} style={styles.resetBtn}>
                  Reset
                </button>
              </div>
            </form>
          </div>

          {/* Results */}
          <div style={styles.card}>
            <h2 style={styles.cardTitle}>Analysis Results</h2>

            {error && <div style={styles.error}>{error}</div>}

            {!result && !error && !loading && (
              <div style={styles.placeholder}>
                <p style={{ fontSize: 48 }}>🛡️</p>
                <p>Enter account features and click Analyze to see results</p>
              </div>
            )}

            {loading && (
              <div style={styles.placeholder}>
                <div style={styles.spinner} />
                <p>Running analysis{useGemini ? ' with Gemini AI' : ''}...</p>
              </div>
            )}

            {result && (
              <div>
                {/* Prediction Badge */}
                <div style={{
                  ...styles.predictionBadge,
                  backgroundColor: result.prediction === 'Fake Account' ? '#fef2f2' : '#f0fdf4',
                  borderColor: result.prediction === 'Fake Account' ? '#fca5a5' : '#86efac',
                  color: result.prediction === 'Fake Account' ? '#dc2626' : '#16a34a',
                }}>
                  <span style={{ fontSize: 32 }}>
                    {result.prediction === 'Fake Account' ? '🚨' : '✅'}
                  </span>
                  <h3 style={{ margin: '8px 0 4px' }}>{result.prediction}</h3>
                  <p style={{ margin: 0, fontSize: 14 }}>Confidence: {result.confidence}</p>
                </div>

                {/* Risk Score */}
                <div style={styles.riskSection}>
                  <h4 style={styles.sectionTitle}>Risk Score</h4>
                  <div style={styles.riskBarBg}>
                    <div style={{
                      ...styles.riskBarFill,
                      width: `${result.risk_score * 100}%`,
                      backgroundColor: getRiskColor(result.risk_score),
                    }} />
                  </div>
                  <p style={{
                    ...styles.riskScoreText,
                    color: getRiskColor(result.risk_score),
                  }}>
                    {(result.risk_score * 100).toFixed(1)}%
                  </p>
                </div>

                {/* Risk Factors */}
                <div style={styles.riskSection}>
                  <h4 style={styles.sectionTitle}>Risk Factors</h4>
                  {result.risk_factors.map((factor, i) => (
                    <div key={i} style={styles.riskFactor}>
                      <span>⚠️</span>
                      <span>{factor}</span>
                    </div>
                  ))}
                </div>

                {/* Gemini Analysis */}
                {result.gemini_analysis && (
                  <div style={styles.geminiSection}>
                    <h4 style={styles.sectionTitle}>🤖 Gemini AI Analysis</h4>
                    <p style={styles.geminiText}>{result.gemini_analysis}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </main>

      <footer style={styles.footer}>
        <p>Built by Rajesh S — AI & Data Science | XGBoost + FastAPI + React + Gemini 2.5</p>
      </footer>
    </div>
  );
}

const styles = {
  app: {
    minHeight: '100vh',
    backgroundColor: '#0f172a',
    color: '#e2e8f0',
    fontFamily: "'Segoe UI', system-ui, -apple-system, sans-serif",
  },
  header: {
    textAlign: 'center',
    padding: '32px 16px 16px',
    borderBottom: '1px solid #1e293b',
  },
  title: {
    fontSize: 28,
    fontWeight: 700,
    margin: 0,
    background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
  },
  subtitle: {
    color: '#94a3b8',
    margin: '8px 0 0',
    fontSize: 14,
  },
  main: {
    maxWidth: 1100,
    margin: '0 auto',
    padding: 24,
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: 24,
  },
  card: {
    backgroundColor: '#1e293b',
    borderRadius: 12,
    padding: 24,
    border: '1px solid #334155',
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 600,
    marginTop: 0,
    marginBottom: 20,
    color: '#f1f5f9',
  },
  presets: {
    display: 'flex',
    gap: 8,
    marginBottom: 16,
  },
  presetBtn: {
    flex: 1,
    padding: '8px 12px',
    borderRadius: 8,
    border: 'none',
    cursor: 'pointer',
    fontSize: 12,
    fontWeight: 600,
  },
  presetFake: {
    backgroundColor: '#7f1d1d',
    color: '#fca5a5',
  },
  presetReal: {
    backgroundColor: '#14532d',
    color: '#86efac',
  },
  field: {
    marginBottom: 14,
  },
  label: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    fontSize: 13,
    color: '#94a3b8',
    marginBottom: 6,
  },
  rangeValue: {
    color: '#3b82f6',
    fontWeight: 600,
  },
  input: {
    width: '100%',
    padding: '8px 12px',
    borderRadius: 8,
    border: '1px solid #334155',
    backgroundColor: '#0f172a',
    color: '#e2e8f0',
    fontSize: 14,
    boxSizing: 'border-box',
  },
  rangeInput: {
    width: '100%',
    accentColor: '#3b82f6',
  },
  toggle: {
    width: 50,
    height: 26,
    borderRadius: 13,
    position: 'relative',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    transition: 'background-color 0.2s',
  },
  toggleKnob: {
    width: 22,
    height: 22,
    borderRadius: '50%',
    backgroundColor: '#fff',
    transition: 'transform 0.2s',
    position: 'absolute',
  },
  toggleLabel: {
    marginLeft: 60,
    fontSize: 13,
    color: '#94a3b8',
  },
  buttonRow: {
    display: 'flex',
    gap: 12,
    marginTop: 20,
  },
  submitBtn: {
    flex: 1,
    padding: '12px',
    borderRadius: 10,
    border: 'none',
    backgroundColor: '#3b82f6',
    color: '#fff',
    fontSize: 15,
    fontWeight: 600,
    cursor: 'pointer',
  },
  resetBtn: {
    padding: '12px 20px',
    borderRadius: 10,
    border: '1px solid #334155',
    backgroundColor: 'transparent',
    color: '#94a3b8',
    fontSize: 14,
    cursor: 'pointer',
  },
  placeholder: {
    textAlign: 'center',
    padding: '60px 20px',
    color: '#64748b',
  },
  error: {
    backgroundColor: '#7f1d1d',
    color: '#fca5a5',
    padding: 16,
    borderRadius: 8,
    marginBottom: 16,
  },
  predictionBadge: {
    textAlign: 'center',
    padding: 20,
    borderRadius: 12,
    border: '2px solid',
    marginBottom: 20,
  },
  riskSection: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: 600,
    color: '#94a3b8',
    marginBottom: 10,
    marginTop: 0,
  },
  riskBarBg: {
    height: 10,
    backgroundColor: '#334155',
    borderRadius: 5,
    overflow: 'hidden',
  },
  riskBarFill: {
    height: '100%',
    borderRadius: 5,
    transition: 'width 0.5s ease',
  },
  riskScoreText: {
    fontSize: 28,
    fontWeight: 700,
    margin: '8px 0 0',
  },
  riskFactor: {
    display: 'flex',
    gap: 8,
    alignItems: 'flex-start',
    padding: '8px 12px',
    backgroundColor: '#0f172a',
    borderRadius: 8,
    marginBottom: 6,
    fontSize: 13,
  },
  geminiSection: {
    backgroundColor: '#1a1a2e',
    border: '1px solid #312e81',
    borderRadius: 10,
    padding: 16,
  },
  geminiText: {
    fontSize: 14,
    lineHeight: 1.6,
    color: '#c7d2fe',
    margin: 0,
  },
  spinner: {
    width: 40,
    height: 40,
    border: '4px solid #334155',
    borderTopColor: '#3b82f6',
    borderRadius: '50%',
    animation: 'spin 0.8s linear infinite',
    margin: '0 auto 16px',
  },
  footer: {
    textAlign: 'center',
    padding: 20,
    color: '#475569',
    fontSize: 13,
    borderTop: '1px solid #1e293b',
  },
};

// Inject keyframe animation
const styleSheet = document.createElement('style');
styleSheet.textContent = `
  @keyframes spin { to { transform: rotate(360deg); } }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { margin: 0; }
  input[type="number"]::-webkit-inner-spin-button { opacity: 1; }
  @media (max-width: 768px) {
    .grid { grid-template-columns: 1fr !important; }
  }
`;
document.head.appendChild(styleSheet);

export default App;
