import { useState, useCallback } from 'react'
import axios from 'axios'
import { UploadCloud, FileText, AlertTriangle, CheckCircle, BarChart3, Clock, GraduationCap, User } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import './index.css'

function App() {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [isDragActive, setIsDragActive] = useState(false)

  const onDragOver = (e) => {
    e.preventDefault()
    setIsDragActive(true)
  }

  const onDragLeave = (e) => {
    e.preventDefault()
    setIsDragActive(false)
  }

  const onDrop = useCallback((e) => {
    e.preventDefault()
    setIsDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelect(e.dataTransfer.files[0])
    }
  }, [])

  const handleFileSelect = (selectedFile) => {
    if (selectedFile.type !== 'application/pdf') {
      setError('Please upload a PDF file.')
      return
    }
    setFile(selectedFile)
    setError(null)
    analyzeResume(selectedFile)
  }

  const analyzeResume = async (selectedFile) => {
    setLoading(true)
    setResult(null)
    
    const formData = new FormData()
    formData.append('resume', selectedFile)

    try {
      const response = await axios.post('http://localhost:5000/api/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      setResult(response.data)
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred during analysis.')
    } finally {
      setLoading(false)
    }
  }

  const chartData = result ? [
    { name: 'Biased Score', score: result.biased_score, color: '#ef4444' },
    { name: 'Fair Score', score: result.fair_score, color: '#10b981' }
  ] : []

  return (
    <div className="app-container">
      <header>
        <h1>BlindHire AI</h1>
        <p className="subtitle">Unbiased Resume Analyzer. See how identity factors silently inflate scores in automated hiring systems.</p>
      </header>

      {!result && !loading && (
        <div 
          className={`glass-panel upload-zone ${isDragActive ? 'drag-active' : ''}`}
          onDragOver={onDragOver}
          onDragLeave={onDragLeave}
          onDrop={onDrop}
          onClick={() => document.getElementById('file-upload').click()}
        >
          <UploadCloud className="upload-icon" size={64} />
          <h3 className="upload-text">Drag & Drop Resume</h3>
          <p className="upload-hint">Only PDF files are supported</p>
          <input 
            type="file" 
            id="file-upload" 
            accept=".pdf" 
            style={{ display: 'none' }}
            onChange={(e) => {
              if (e.target.files.length > 0) {
                handleFileSelect(e.target.files[0])
              }
            }}
          />
        </div>
      )}

      {error && (
        <div className="bias-alert" style={{ background: 'rgba(239, 68, 68, 0.1)', marginTop: '2rem' }}>
          <AlertTriangle color="#ef4444" />
          <div>
            <strong>Error:</strong> {error}
          </div>
        </div>
      )}

      {loading && (
        <div className="glass-panel loading-container">
          <div className="spinner"></div>
          <h3>Analyzing Resume...</h3>
          <p className="upload-hint">Extracting skills, experience, and evaluating fairness.</p>
        </div>
      )}

      {result && (
        <div className="results-view">
          <div className="glass-panel" style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <FileText size={32} color="#3b82f6" />
              <div>
                <h3 style={{ margin: 0 }}>{file?.name}</h3>
                <span className="upload-hint">Analysis Complete</span>
              </div>
            </div>
            <button 
              onClick={() => { setResult(null); setFile(null); }}
              style={{ padding: '0.5rem 1rem', borderRadius: '8px', border: '1px solid var(--border-color)', background: 'transparent', color: 'white', cursor: 'pointer' }}
            >
              Analyze Another
            </button>
          </div>

          <div className="dashboard-grid">
            <div className="glass-panel score-card">
              <h3 className="score-title">Biased Score</h3>
              <div className="score-value score-biased">{result.biased_score}</div>
              <p className="upload-hint" style={{ marginTop: '1rem' }}>Factors in skills, experience, and demographic proxies.</p>
            </div>
            
            <div className="glass-panel score-card">
              <h3 className="score-title">Fair Score</h3>
              <div className="score-value score-fair">{result.fair_score}</div>
              <p className="upload-hint" style={{ marginTop: '1rem' }}>Strictly evaluates skills and years of experience.</p>
            </div>
          </div>

          <div className={`bias-alert ${result.bias_detected ? '' : 'safe'}`}>
            {result.bias_detected ? <AlertTriangle size={32} color="#ef4444" /> : <CheckCircle size={32} color="#10b981" />}
            <div>
              <h3 style={{ margin: 0 }}>{result.bias_detected ? '⚠️ Significant Bias Detected' : '✅ Fair Assessment'}</h3>
              <p style={{ margin: 0, opacity: 0.8 }}>
                {result.bias_detected 
                  ? `The biased score is artificially inflated by ${Math.abs(result.biased_score - result.fair_score).toFixed(1)} points due to identity proxies.` 
                  : 'No significant difference between fair and biased scoring.'}
              </p>
            </div>
          </div>

          <div className="dashboard-grid" style={{ marginTop: '2rem' }}>
            <div className="glass-panel">
              <h3 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}><BarChart3 /> Score Comparison</h3>
              <div style={{ height: '300px' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis dataKey="name" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip cursor={{fill: 'rgba(255,255,255,0.05)'}} contentStyle={{ backgroundColor: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }} />
                    <Bar dataKey="score" radius={[4, 4, 0, 0]}>
                      {chartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="glass-panel">
              <h3 style={{ marginBottom: '1.5rem' }}>Extracted Entities</h3>
              <ul className="metric-list">
                <li className="metric-item">
                  <span className="metric-label"><Clock size={16} style={{display: 'inline', marginRight: '8px'}} />Experience</span>
                  <span className="metric-value">{result.experience_years} years</span>
                </li>
                <li className="metric-item">
                  <span className="metric-label"><GraduationCap size={16} style={{display: 'inline', marginRight: '8px'}} />Tier 1 College</span>
                  <span className="metric-value">{result.tier1_college ? 'Detected' : 'Not Detected'}</span>
                </li>
                <li className="metric-item">
                  <span className="metric-label"><User size={16} style={{display: 'inline', marginRight: '8px'}} />Gender Signal</span>
                  <span className="metric-value">{result.gender}</span>
                </li>
              </ul>

              <h4 style={{ marginTop: '1.5rem', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>Detected Skills</h4>
              <div className="skills-tags">
                {result.skills_found.length > 0 ? (
                  result.skills_found.map(skill => (
                    <span key={skill} className="tag">{skill}</span>
                  ))
                ) : (
                  <span className="upload-hint">No technical skills detected.</span>
                )}
              </div>

              {result.skill_recommendations.length > 0 && (
                <>
                  <h4 style={{ marginTop: '1.5rem', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>Recommended Skills to Add</h4>
                  <div className="skills-tags">
                    {result.skill_recommendations.map(skill => (
                      <span key={skill} className="tag recommendation">{skill}</span>
                    ))}
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
