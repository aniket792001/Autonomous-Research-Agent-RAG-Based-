import React, { useState, useEffect } from 'react';

const API_BASE = window.location.origin;

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('aegis_token') || '');
  const [user, setUser] = useState(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState('login');
  const [authEmail, setAuthEmail] = useState('admin@aegisaudit.com');
  const [authPass, setAuthPass] = useState('AdminPass123!');
  const [authName, setAuthName] = useState('Lead Auditor');

  const [report, setReport] = useState(null);
  const [selectedFinding, setSelectedFinding] = useState(null);
  const [filter, setFilter] = useState('ALL');
  const [search, setSearch] = useState('');
  const [pastAudits, setPastAudits] = useState([]);

  const [showNewAuditModal, setShowNewAuditModal] = useState(false);
  const [standardName, setStandardName] = useState('sample.pdf');
  const [policyName, setPolicyName] = useState('sample.pdf');
  const [maxClauses, setMaxClauses] = useState(10);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [drawerOpen, setDrawerOpen] = useState(false);
  const [agentLogs, setAgentLogs] = useState([]);
  const [jobProgress, setJobProgress] = useState(0);

  useEffect(() => {
    if (token) {
      fetch(`${API_BASE}/api/auth/me`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      .then(res => res.ok ? res.json() : null)
      .then(u => {
        if (u) setUser(u);
        else logout();
      })
      .catch(() => logout());
    } else {
      handleLogin('admin@aegisaudit.com', 'AdminPass123!');
    }
    loadAuditHistory();
  }, [token]);

  const loadAuditHistory = () => {
    fetch(`${API_BASE}/api/audit/history`, {
      headers: token ? { 'Authorization': `Bearer ${token}` } : {}
    })
    .then(res => res.ok ? res.json() : [])
    .then(list => {
      setPastAudits(list);
      if (list.length > 0 && !report) {
        loadReport(list[0].audit_id);
      }
    })
    .catch(err => console.error(err));
  };

  const loadReport = (auditId) => {
    fetch(`${API_BASE}/api/audit/${auditId}`, {
      headers: token ? { 'Authorization': `Bearer ${token}` } : {}
    })
    .then(res => res.json())
    .then(data => {
      setReport(data);
      if (data.findings && data.findings.length > 0) {
        setSelectedFinding(data.findings[0]);
      }
    });
  };

  const handleLogin = async (email, pass) => {
    try {
      const res = await fetch(`${API_BASE}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password: pass })
      });
      if (res.ok) {
        const data = await res.json();
        setToken(data.access_token);
        localStorage.setItem('aegis_token', data.access_token);
        setUser(data.user);
        setShowAuthModal(false);
        loadAuditHistory();
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleRegister = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: authEmail, password: authPass, full_name: authName, role: 'auditor' })
      });
      if (res.ok) {
        const data = await res.json();
        setToken(data.access_token);
        localStorage.setItem('aegis_token', data.access_token);
        setUser(data.user);
        setShowAuthModal(false);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const logout = () => {
    setToken('');
    localStorage.removeItem('aegis_token');
    setUser(null);
  };

  const startAudit = async () => {
    setIsSubmitting(true);
    setDrawerOpen(true);
    setAgentLogs([{
      timestamp: new Date().toLocaleTimeString(),
      agent_name: 'Orchestrator',
      message: 'Dispatching audit job to background worker...',
      progress_pct: 5
    }]);

    try {
      const res = await fetch(`${API_BASE}/api/audit/jobs/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          standard_filename: standardName,
          policy_filename: policyName,
          max_clauses: maxClauses
        })
      });

      if (!res.ok) throw new Error('Failed to launch audit');
      const jobData = await res.json();
      setShowNewAuditModal(false);

      const eventSource = new EventSource(`${API_BASE}/api/audit/jobs/${jobData.job_id}/stream`);
      eventSource.onmessage = (e) => {
        try {
          const log = JSON.parse(e.data);
          setAgentLogs(prev => [...prev, log]);
          if (log.progress_pct) setJobProgress(log.progress_pct);
        } catch(err) {}
      };

      eventSource.addEventListener('end', () => {
        eventSource.close();
        setIsSubmitting(false);
        fetch(`${API_BASE}/api/audit/jobs/${jobData.job_id}/status`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        .then(r => r.json())
        .then(doneJob => {
          if (doneJob.result) {
            setReport(doneJob.result);
            if (doneJob.result.findings?.length > 0) {
              setSelectedFinding(doneJob.result.findings[0]);
            }
            loadAuditHistory();
          }
        });
      });

      eventSource.onerror = () => {
        eventSource.close();
        setIsSubmitting(false);
      };
    } catch (err) {
      alert(`Error starting audit: ${err.message}`);
      setIsSubmitting(false);
    }
  };

  const findings = (report?.findings || []).filter(f => {
    if (filter === 'NON_COMPLIANT' && f.status !== 'Non-Compliant') return false;
    if (filter === 'PARTIAL' && f.status !== 'Partially Compliant') return false;
    if (filter === 'COMPLIANT' && f.status !== 'Compliant') return false;
    if (search) {
      const q = search.toLowerCase();
      return f.clause_id.toLowerCase().includes(q) ||
             f.clause_title.toLowerCase().includes(q) ||
             f.requirement_summary.toLowerCase().includes(q);
    }
    return true;
  });

  return (
    <div className="app-container">
      <nav className="navbar">
        <div className="nav-brand">
          <span className="nav-logo">🛡️</span>
          <span className="nav-title">AegisAudit AI</span>
          <span className="nav-badge">Enterprise Edition</span>
        </div>

        <div className="nav-controls">
          <button 
            className="btn btn-primary" 
            onClick={() => setShowNewAuditModal(true)}
            disabled={user?.role === 'viewer'}
          >
            ⚡ Launch Audit
          </button>

          {pastAudits.length > 0 && (
            <select 
              className="search-input" 
              style={{ width: '220px' }}
              onChange={(e) => loadReport(e.target.value)}
              value={report?.audit_id || ''}
            >
              {pastAudits.map(a => (
                <option key={a.audit_id} value={a.audit_id}>
                  {a.audit_id} ({a.compliance_pct}%)
                </option>
              ))}
            </select>
          )}

          {user ? (
            <div className="user-pill">
              <span>👤 {user.full_name}</span>
              <span className={`role-tag role-${user.role}`}>{user.role}</span>
              <button className="btn btn-ghost" onClick={logout} style={{ padding: '2px 6px', fontSize: '0.75rem' }}>Logout</button>
            </div>
          ) : (
            <button className="btn btn-secondary" onClick={() => setShowAuthModal(true)}>Sign In</button>
          )}
        </div>
      </nav>

      {report && (
        <div className="kpi-container">
          <div className="kpi-card">
            <div className="kpi-label">Overall Compliance</div>
            <div className="kpi-value" style={{ 
              color: report.summary.overall_compliance_percentage >= 75 ? 'var(--status-compliant)' :
                     report.summary.overall_compliance_percentage >= 50 ? 'var(--status-partial)' : 'var(--status-non-compliant)' 
            }}>
              {report.summary.overall_compliance_percentage}%
            </div>
          </div>
          <div className="kpi-card">
            <div className="kpi-label">Compliant Controls</div>
            <div className="kpi-value" style={{ color: 'var(--status-compliant)' }}>
              {report.summary.compliant_count}
            </div>
          </div>
          <div className="kpi-card">
            <div className="kpi-label">Ambiguous / Partial</div>
            <div className="kpi-value" style={{ color: 'var(--status-partial)' }}>
              {report.summary.partially_compliant_count}
            </div>
          </div>
          <div className="kpi-card">
            <div className="kpi-label">Identified Gaps</div>
            <div className="kpi-value" style={{ color: 'var(--status-non-compliant)' }}>
              {report.summary.non_compliant_count}
            </div>
          </div>
        </div>
      )}

      <div className="workspace">
        <div className="matrix-panel">
          <div className="panel-header">
            <div className="panel-title">
              <span>📋</span> Compliance Matrix ({findings.length})
            </div>
            {report && (
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Auditing: <strong>{report.standard_name}</strong> vs <strong>{report.policy_name}</strong>
              </span>
            )}
          </div>

          <div className="filter-bar">
            <input 
              type="text" 
              className="search-input" 
              placeholder="Search clauses, keywords, or mandates..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            <button className={`filter-btn ${filter === 'ALL' ? 'active' : ''}`} onClick={() => setFilter('ALL')}>All</button>
            <button className={`filter-btn ${filter === 'NON_COMPLIANT' ? 'active' : ''}`} onClick={() => setFilter('NON_COMPLIANT')}>🔴 Gaps</button>
            <button className={`filter-btn ${filter === 'PARTIAL' ? 'active' : ''}`} onClick={() => setFilter('PARTIAL')}>🟡 Partial</button>
            <button className={`filter-btn ${filter === 'COMPLIANT' ? 'active' : ''}`} onClick={() => setFilter('COMPLIANT')}>🟢 Compliant</button>
          </div>

          <div className="findings-list">
            {findings.map(f => {
              const isSelected = selectedFinding?.clause_id === f.clause_id;
              const badgeClass = f.status === 'Compliant' ? 'badge-compliant' :
                                 f.status === 'Partially Compliant' ? 'badge-partial' : 'badge-non-compliant';
              return (
                <div 
                  key={f.clause_id} 
                  className={`finding-row ${isSelected ? 'selected' : ''}`}
                  onClick={() => setSelectedFinding(f)}
                >
                  <div className="finding-top">
                    <span className="clause-tag">{f.clause_id}: {f.clause_title}</span>
                    <span className={`badge ${badgeClass}`}>{f.status}</span>
                  </div>
                  <div className="finding-req">{f.requirement_summary}</div>
                  <div style={{ display: 'flex', gap: '6px' }}>
                    {(f.citations || []).map((c, i) => (
                      <span key={i} className="citation-chip">
                        📄 Page {c.page_number}
                      </span>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="evidence-panel">
          <div className="panel-header">
            <div className="panel-title">
              <span>🔍</span> Evidence & Gap Inspector
            </div>
            {selectedFinding && (
              <span className="badge" style={{ background: '#1F2937', color: '#94A3B8' }}>
                Risk Level: {selectedFinding.risk_level}
              </span>
            )}
          </div>

          <div className="evidence-content">
            {selectedFinding ? (
              <>
                <div className="doc-quote-card">
                  <div className="doc-quote-meta">
                    FOUND POLICY EVIDENCE | CITATION: {selectedFinding.citations?.[0]?.document_name || 'Policy Doc'} 
                    (Page {selectedFinding.citations?.[0]?.page_number || 'N/A'})
                  </div>
                  <div className="doc-quote-text">
                    "{selectedFinding.evidence_found || 'No formal policy statements detected in document.'}"
                  </div>
                </div>

                <div className="gap-box">
                  <div className="gap-title">⚠️ Identified Compliance Gap / Ambiguity</div>
                  <div style={{ fontSize: '0.88rem', color: '#FECACA' }}>
                    {selectedFinding.gap_analysis}
                  </div>
                </div>

                <div className="fix-box">
                  <div className="fix-title">💡 Prescribed Engineering Remediation</div>
                  <div style={{ fontSize: '0.88rem', color: '#D1FAE5' }}>
                    {selectedFinding.remediation_recommendation}
                  </div>
                </div>
              </>
            ) : (
              <div style={{ color: 'var(--text-muted)', textAlign: 'center', marginTop: '40px' }}>
                Select a clause on the left to inspect evidence and remediation.
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="agent-drawer" style={{ transform: drawerOpen ? 'translateY(0)' : 'translateY(calc(100% - 42px))' }}>
        <div className="agent-drawer-bar" onClick={() => setDrawerOpen(!drawerOpen)}>
          <div>
            <span className="agent-pulse"></span>
            <strong>Autonomous Multi-Agent Core:</strong> {isSubmitting ? 'Audit Execution Active' : 'Idle'} 
            {isSubmitting && ` (${jobProgress}%)`}
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--accent-cyan-light)' }}>
            {drawerOpen ? '▼ Minimize Drawer' : '▲ Open Live Agent Stream'}
          </div>
        </div>

        <div className="agent-log-window">
          {agentLogs.length === 0 ? (
            <div style={{ color: 'var(--text-dim)' }}>No active execution. Launch an audit to see real-time agent thoughts.</div>
          ) : (
            agentLogs.map((log, i) => (
              <div key={i} className="log-entry">
                <span className="log-time">[{log.timestamp}]</span>
                <span className="log-agent">{log.agent_name}:</span>
                <span className="log-msg">{log.message}</span>
              </div>
            ))
          )}
        </div>
      </div>

      {showNewAuditModal && (
        <div className="modal-overlay" onClick={() => setShowNewAuditModal(false)}>
          <div className="modal-dialog" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>⚡ Launch Autonomous Multi-Agent Audit</h3>
              <button className="btn btn-ghost" onClick={() => setShowNewAuditModal(false)}>✕</button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label className="form-label">Regulatory Standard Framework</label>
                <input 
                  type="text" 
                  className="form-input" 
                  value={standardName} 
                  onChange={e => setStandardName(e.target.value)}
                  placeholder="e.g. sample.pdf or iso27001.pdf"
                />
              </div>

              <div className="form-group">
                <label className="form-label">Company Policy Document</label>
                <input 
                  type="text" 
                  className="form-input" 
                  value={policyName} 
                  onChange={e => setPolicyName(e.target.value)}
                  placeholder="e.g. sample.pdf or security_policy.pdf"
                />
              </div>

              <div className="form-group">
                <label className="form-label">Max Clauses to Audit: {maxClauses}</label>
                <input 
                  type="range" 
                  min="3" 
                  max="25" 
                  value={maxClauses} 
                  onChange={e => setMaxClauses(parseInt(e.target.value))}
                />
              </div>

              <button 
                className="btn btn-primary" 
                style={{ width: '100%', justifyContent: 'center', marginTop: '10px' }}
                onClick={startAudit}
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Starting Background Worker...' : 'Initiate Autonomous Audit'}
              </button>
            </div>
          </div>
        </div>
      )}

      {showAuthModal && (
        <div className="modal-overlay" onClick={() => setShowAuthModal(false)}>
          <div className="modal-dialog" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>
                {authMode === 'login' ? '🔐 Sign In to AegisAudit' : '📝 Create Organization Account'}
              </h3>
              <button className="btn btn-ghost" onClick={() => setShowAuthModal(false)}>✕</button>
            </div>
            <div className="modal-body">
              {authMode === 'register' && (
                <div className="form-group">
                  <label className="form-label">Full Name</label>
                  <input type="text" className="form-input" value={authName} onChange={e => setAuthName(e.target.value)} />
                </div>
              )}
              <div className="form-group">
                <label className="form-label">Work Email</label>
                <input type="email" className="form-input" value={authEmail} onChange={e => setAuthEmail(e.target.value)} />
              </div>
              <div className="form-group">
                <label className="form-label">Password</label>
                <input type="password" className="form-input" value={authPass} onChange={e => setAuthPass(e.target.value)} />
              </div>

              {authMode === 'login' ? (
                <button className="btn btn-primary" style={{ justifyContent: 'center' }} onClick={() => handleLogin(authEmail, authPass)}>
                  Sign In
                </button>
              ) : (
                <button className="btn btn-primary" style={{ justifyContent: 'center' }} onClick={handleRegister}>
                  Create Account
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
