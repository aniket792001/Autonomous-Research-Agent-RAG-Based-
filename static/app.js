/**
 * AegisAudit AI - High-Performance Interactive Application Engine.
 * Features: Spacious & View-Friendly Layout, Executive KPI Banner,
 * Option A Slate Dark & Executive Light Dual Theme, High-Contrast Cards,
 * SVG Health Donut Gauge, Auditor Action Workflow, Document Highlighting & One-Click Exports.
 */

(function () {
  const API_BASE = window.location.origin;

  // Initialize Theme from localStorage (defaults to dark - Option A)
  const currentTheme = localStorage.getItem('aegis_theme') || 'dark';
  document.documentElement.setAttribute('data-theme', currentTheme);

  // Initial State Store
  const state = {
    theme: currentTheme,
    token: localStorage.getItem('aegis_token') || '',
    user: {
      full_name: 'Lead Security Auditor',
      email: 'admin@aegisaudit.com',
      role: 'admin'
    },
    report: {
      audit_id: 'AUDIT-ISO27001-DEMO',
      standard_name: 'ISO_27001_Framework.pdf',
      policy_name: 'Enterprise_Security_Policy.pdf',
      timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19),
      summary: {
        overall_compliance_percentage: 78.5,
        total_clauses_audited: 8,
        compliant_count: 5,
        partially_compliant_count: 1,
        non_compliant_count: 2,
        risk_breakdown: { Critical: 1, High: 1, Medium: 1, Low: 5 },
        executive_overview: 'Overall security compliance posture is sound (78.5%), however critical vulnerabilities were identified in Administrative Access Controls (ISO-A.9.2.1) and Multi-Factor Authentication enforcement for infrastructure access.'
      },
      findings: [
        {
          clause_id: 'ISO-A.9.2.1',
          clause_title: 'User Registration & Deregistration',
          requirement_summary: 'A formal user registration and de-registration process must be implemented to enable assignment of access rights.',
          status: 'Non-Compliant',
          risk_level: 'Critical',
          approved: false,
          auditor_note: '',
          citations: [{ document_name: 'Enterprise_Security_Policy.pdf', page_number: 14 }],
          evidence_found: 'Section 4.1 outlines that accounts are requested via email or ticketing, but <mark class="doc-highlight">lacks formalized de-provisioning timelines and audit recertification protocols</mark>.',
          gap_analysis: 'No documented SLA exists for de-registering departed personnel within 24 hours. Orphaned accounts were detected.',
          remediation_recommendation: 'Implement automated SCIM identity synchronization between HR systems (Workday) and SSO Identity Provider (Okta/Azure AD).'
        },
        {
          clause_id: 'ISO-A.10.1.1',
          clause_title: 'Cryptographic Controls & Key Management',
          requirement_summary: 'A policy on the use of cryptographic controls for protection of information must be developed and implemented.',
          status: 'Compliant',
          risk_level: 'Low',
          approved: true,
          auditor_note: 'Verified during AWS infrastructure review.',
          citations: [{ document_name: 'Enterprise_Security_Policy.pdf', page_number: 22 }],
          evidence_found: 'Policy Chapter 7 mandates <mark class="doc-highlight">AES-256 for all S3 buckets and RDS databases, with TLS 1.3 enforced</mark> for in-transit communication.',
          gap_analysis: 'Controls satisfy standard requirements completely.',
          remediation_recommendation: 'Maintain continuous automated compliance monitoring via AWS Config / CloudTrail.'
        },
        {
          clause_id: 'GDPR-Art.32',
          clause_title: 'Security of Processing & Data Protection',
          requirement_summary: 'The controller and processor shall implement appropriate technical and organisational measures to ensure a level of security appropriate to the risk.',
          status: 'Partially Compliant',
          risk_level: 'Medium',
          approved: false,
          auditor_note: '',
          citations: [{ document_name: 'Enterprise_Security_Policy.pdf', page_number: 29 }],
          evidence_found: 'Policy mentions pseudonymisation in staging environments, but <mark class="doc-highlight">does not formalize regular testing and effectiveness evaluations</mark>.',
          gap_analysis: 'Annual penetration testing exists, but specific data protection drills are undocumented.',
          remediation_recommendation: 'Schedule bi-annual simulated data breach exercises and document recovery time objectives.'
        },
        {
          clause_id: 'ISO-A.12.4.1',
          clause_title: 'Event Logging & Audit Trails',
          requirement_summary: 'Event logs recording user activities, exceptions, faults and information security events shall be produced, kept and regularly reviewed.',
          status: 'Compliant',
          risk_level: 'Low',
          approved: true,
          auditor_note: 'Splunk WORM retention validated.',
          citations: [{ document_name: 'Enterprise_Security_Policy.pdf', page_number: 37 }],
          evidence_found: 'Centralized Splunk SIEM collects server and database audit trails with <mark class="doc-highlight">365-day immutable WORM retention</mark>.',
          gap_analysis: 'Fully meets regulatory mandate.',
          remediation_recommendation: 'Conduct quarterly log integrity and tamper-proof verification checks.'
        }
      ]
    },
    selectedFinding: null,
    filter: 'ALL',
    search: '',
    pastAudits: [],
    showNewAuditModal: false,
    showAuthModal: false,
    authMode: 'login',
    authEmail: 'admin@aegisaudit.com',
    authPass: 'AdminPass123!',
    authName: 'Security Officer',
    drawerOpen: false,
    agentLogs: [],
    isSubmitting: false,
    jobProgress: 0
  };

  // Set default selected finding
  if (state.report && state.report.findings && state.report.findings.length > 0) {
    state.selectedFinding = state.report.findings[0];
  }

  // Theme Switch Handler
  function toggleTheme() {
    const nextTheme = state.theme === 'dark' ? 'light' : 'dark';
    state.theme = nextTheme;
    localStorage.setItem('aegis_theme', nextTheme);
    document.documentElement.setAttribute('data-theme', nextTheme);
    render();
  }

  // Pure ES6 Reactive Renderer
  function render() {
    const root = document.getElementById('app');
    if (!root) return;

    const allFindings = state.report?.findings || [];
    
    // Counts for filter pills
    const countTotal = allFindings.length;
    const countGaps = allFindings.filter(f => f.status === 'Non-Compliant').length;
    const countPartial = allFindings.filter(f => f.status === 'Partially Compliant').length;
    const countCompliant = allFindings.filter(f => f.status === 'Compliant').length;

    // Filtered findings
    const findings = allFindings.filter(f => {
      if (state.filter === 'NON_COMPLIANT' && f.status !== 'Non-Compliant') return false;
      if (state.filter === 'PARTIAL' && f.status !== 'Partially Compliant') return false;
      if (state.filter === 'COMPLIANT' && f.status !== 'Compliant') return false;
      if (state.search) {
        const q = state.search.toLowerCase();
        return f.clause_id.toLowerCase().includes(q) ||
               f.clause_title.toLowerCase().includes(q) ||
               f.requirement_summary.toLowerCase().includes(q);
      }
      return true;
    });

    const rep = state.report;
    const score = rep?.summary?.overall_compliance_percentage || 0;
    const scoreColor = score >= 75 ? 'var(--status-compliant)' : score >= 50 ? 'var(--status-partial)' : 'var(--status-non-compliant)';
    const circumference = 2 * Math.PI * 24;
    const strokeDash = (score / 100) * circumference;

    root.innerHTML = `
      <div class="app-container">
        <!-- Top Sticky Navigation Bar -->
        <nav class="navbar">
          <div class="nav-brand">
            <div class="nav-logo-icon">🛡️</div>
            <div class="nav-title-group">
              <div style="display: flex; align-items: center;">
                <span class="nav-title">AegisAudit AI</span>
                <span class="nav-badge">Enterprise Edition</span>
              </div>
              <span class="nav-subtitle">Autonomous Regulatory & Compliance Intelligence</span>
            </div>
          </div>

          <div class="nav-controls">
            <!-- Dual Theme Switcher -->
            <button class="theme-toggle-btn" id="btn-theme-toggle" title="Toggle Light/Dark Theme">
              ${state.theme === 'dark' ? '☀️ Light' : '🌙 Dark'}
            </button>

            <!-- Export Actions -->
            <button class="btn btn-secondary" id="btn-export-csv" title="Export CSV Audit Matrix">
              📊 Export CSV
            </button>

            <!-- Launch Audit Action -->
            <button class="btn btn-primary" id="btn-launch-modal">
              ⚡ Launch Audit
            </button>

            ${state.pastAudits.length > 0 ? `
              <select class="search-input" id="select-history" style="width: 200px;">
                ${state.pastAudits.map(a => `
                  <option value="${a.audit_id}" ${rep && rep.audit_id === a.audit_id ? 'selected' : ''}>
                    ${a.audit_id} (${a.compliance_pct}%)
                  </option>
                `).join('')}
              </select>
            ` : ''}

            ${state.user ? `
              <div class="user-pill">
                <span>👤 ${escapeHtml(state.user.full_name)}</span>
                <span class="role-tag role-${state.user.role}">${state.user.role}</span>
                <button class="btn btn-ghost" id="btn-logout" style="padding: 2px 6px; font-size: 0.75rem;">Logout</button>
              </div>
            ` : `
              <button class="btn btn-secondary" id="btn-open-login">Sign In</button>
            `}
          </div>
        </nav>

        <!-- Main Spacious Layout Wrapper -->
        <main class="main-content">

          <!-- Executive KPI & Compliance Health Banner -->
          ${rep ? `
            <section class="executive-banner">
              <div class="banner-context">
                <div class="banner-framework-tag">
                  <span>🏛️ ${escapeHtml(rep.standard_name)}</span>
                  <span style="color: var(--text-dim);">vs</span>
                  <span>📄 ${escapeHtml(rep.policy_name)}</span>
                </div>
                <div class="banner-narrative">
                  ${escapeHtml(rep.summary.executive_overview || 'Automated multi-agent regulatory compliance audit completed.')}
                </div>
              </div>

              <div class="banner-metrics-group">
                <!-- Health Score Donut -->
                <div class="metric-card metric-gauge-card">
                  <svg class="donut-svg" viewBox="0 0 64 64">
                    <circle class="donut-meter" cx="32" cy="32" r="24" />
                    <circle class="donut-value" cx="32" cy="32" r="24" 
                      stroke-dasharray="${strokeDash} ${circumference}"
                      style="stroke: ${scoreColor};"
                    />
                  </svg>
                  <div class="metric-content">
                    <div class="metric-label">Compliance Score</div>
                    <div class="metric-value" style="color: ${scoreColor};">${score}%</div>
                  </div>
                </div>

                <!-- Compliant Controls -->
                <div class="metric-card">
                  <div class="metric-content">
                    <div class="metric-label">Compliant Controls</div>
                    <div class="metric-value" style="color: var(--status-compliant);">${rep.summary.compliant_count}</div>
                  </div>
                </div>

                <!-- Partially Compliant -->
                <div class="metric-card">
                  <div class="metric-content">
                    <div class="metric-label">Partial / Ambiguous</div>
                    <div class="metric-value" style="color: var(--status-partial);">${rep.summary.partially_compliant_count}</div>
                  </div>
                </div>

                <!-- Identified Gaps -->
                <div class="metric-card">
                  <div class="metric-content">
                    <div class="metric-label">Identified Gaps</div>
                    <div class="metric-value" style="color: var(--status-non-compliant);">${rep.summary.non_compliant_count}</div>
                  </div>
                </div>
              </div>
            </section>
          ` : ''}

          <!-- Main Split 2-Pane Workspace -->
          <div class="workspace">

            <!-- Left Panel: Compliance Matrix -->
            <section class="matrix-panel">
              <div class="panel-header">
                <div class="panel-title">
                  <span>📋</span> Compliance Matrix
                  <span class="panel-badge">${findings.length} clauses</span>
                </div>
                <span style="font-size: 0.78rem; color: var(--text-muted); font-family: var(--font-mono);">
                  ID: ${escapeHtml(rep?.audit_id || 'ACTIVE')}
                </span>
              </div>

              <!-- Filter & Search Bar -->
              <div class="filter-bar">
                <input 
                  type="text" 
                  id="search-input"
                  class="search-input" 
                  placeholder="🔍 Search clauses, requirements, or keywords..."
                  value="${escapeHtml(state.search)}"
                />
                <div class="filter-btn-group">
                  <button class="filter-btn ${state.filter === 'ALL' ? 'active' : ''}" data-filter="ALL">
                    All (${countTotal})
                  </button>
                  <button class="filter-btn ${state.filter === 'NON_COMPLIANT' ? 'active' : ''}" data-filter="NON_COMPLIANT">
                    🔴 Gaps (${countGaps})
                  </button>
                  <button class="filter-btn ${state.filter === 'PARTIAL' ? 'active' : ''}" data-filter="PARTIAL">
                    🟡 Partial (${countPartial})
                  </button>
                  <button class="filter-btn ${state.filter === 'COMPLIANT' ? 'active' : ''}" data-filter="COMPLIANT">
                    🟢 Compliant (${countCompliant})
                  </button>
                </div>
              </div>

              <!-- Findings List -->
              <div class="findings-list">
                ${findings.length === 0 ? `
                  <div style="color: var(--text-muted); text-align: center; padding: 60px 20px;">
                    <div style="font-size: 2rem; margin-bottom: 10px;">🔍</div>
                    <div style="font-weight: 600;">No matching compliance clauses found</div>
                    <div style="font-size: 0.82rem; margin-top: 4px;">Try modifying your search or resetting filter pills.</div>
                  </div>
                ` : findings.map(f => {
                  const isSelected = state.selectedFinding && state.selectedFinding.clause_id === f.clause_id;
                  const badgeClass = f.status === 'Compliant' ? 'badge-compliant' :
                                     f.status === 'Partially Compliant' ? 'badge-partial' : 'badge-non-compliant';
                  const riskClass = f.risk_level === 'Critical' ? 'risk-critical' :
                                    f.risk_level === 'High' ? 'risk-high' :
                                    f.risk_level === 'Medium' ? 'risk-medium' : 'risk-low';
                  return `
                    <div class="finding-row ${isSelected ? 'selected' : ''}" data-clause="${f.clause_id}">
                      <div class="finding-header-row">
                        <div style="display: flex; align-items: center;">
                          <span class="clause-tag-pill">${escapeHtml(f.clause_id)}</span>
                          <span class="risk-tag ${riskClass}">${escapeHtml(f.risk_level)} Risk</span>
                        </div>
                        <span class="badge ${badgeClass}">${f.status}</span>
                      </div>

                      <div class="finding-title">
                        ${f.approved ? '✅ ' : ''}${escapeHtml(f.clause_title)}
                      </div>

                      <div class="finding-req">${escapeHtml(f.requirement_summary)}</div>

                      <div class="finding-footer-row">
                        <div style="display: flex; gap: 8px; align-items: center;">
                          ${(f.citations || []).map(c => `
                            <span class="citation-chip">📄 Page ${c.page_number}</span>
                          `).join('')}
                          ${f.auditor_note ? `<span style="font-size: 0.72rem; color: var(--accent-cyan-light); font-weight: 600;">💬 Note attached</span>` : ''}
                        </div>
                        <span class="inspect-chevron">View Evidence →</span>
                      </div>
                    </div>
                  `;
                }).join('')}
              </div>
            </section>

            <!-- Right Panel: Synchronized Evidence & Remediation Inspector -->
            <section class="evidence-panel">
              <div class="panel-header">
                <div class="panel-title">
                  <span>🔍</span> Evidence & Gap Inspector
                </div>
                ${state.selectedFinding ? `
                  <div style="display: flex; align-items: center; gap: 8px;">
                    <span class="badge ${state.selectedFinding.status === 'Compliant' ? 'badge-compliant' : state.selectedFinding.status === 'Partially Compliant' ? 'badge-partial' : 'badge-non-compliant'}">
                      ${state.selectedFinding.status}
                    </span>
                    <span class="panel-badge">Risk: ${state.selectedFinding.risk_level}</span>
                  </div>
                ` : ''}
              </div>

              <div class="evidence-content">
                ${state.selectedFinding ? `
                  <!-- Clause Header Details -->
                  <div class="clause-detail-header">
                    <div class="clause-detail-code">
                      <span>MANDATE CODE: ${escapeHtml(state.selectedFinding.clause_id)}</span>
                    </div>
                    <div class="clause-detail-title">
                      ${escapeHtml(state.selectedFinding.clause_title)}
                    </div>
                    <div class="clause-detail-mandate">
                      ${escapeHtml(state.selectedFinding.requirement_summary)}
                    </div>
                  </div>

                  <!-- Document Excerpt Card with Highlighted Sentence -->
                  <div class="doc-quote-card">
                    <div class="doc-quote-meta">
                      <span>📄 FOUND POLICY EXCERPT | ${escapeHtml(state.selectedFinding.citations?.[0]?.document_name || 'Policy Doc')} (Page ${state.selectedFinding.citations?.[0]?.page_number || 'N/A'})</span>
                      <span style="color: var(--accent-cyan-light); font-weight: 600;">✓ RAG Verified</span>
                    </div>
                    <div class="doc-quote-text">
                      "${state.selectedFinding.evidence_found || 'No formal policy statements detected in document.'}"
                    </div>
                  </div>

                  <!-- Identified Gap Card -->
                  <div class="gap-box">
                    <div class="gap-title">⚠️ Identified Compliance Gap / Ambiguity</div>
                    <div style="font-size: 0.88rem; color: var(--text-main); line-height: 1.6;">
                      ${escapeHtml(state.selectedFinding.gap_analysis || 'No gaps identified.')}
                    </div>
                  </div>

                  <!-- Prescribed Remediation Card -->
                  <div class="fix-box">
                    <div class="fix-title">💡 Prescribed Engineering Remediation Plan</div>
                    <div style="font-size: 0.88rem; color: var(--text-main); line-height: 1.6;">
                      ${escapeHtml(state.selectedFinding.remediation_recommendation || 'Maintain operational controls.')}
                    </div>
                  </div>

                  <!-- Auditor Human-in-the-Loop Action Bar -->
                  <div class="auditor-action-bar">
                    <div class="auditor-action-title">🧑‍💼 Auditor Workflow & Governance</div>
                    <div class="auditor-btn-group">
                      <button class="auditor-btn ${state.selectedFinding.approved ? 'approved' : ''}" id="btn-approve-finding">
                        ${state.selectedFinding.approved ? '✓ Approved by Auditor' : '✓ Approve Finding'}
                      </button>
                      <button class="auditor-btn" id="btn-accept-risk">
                        ⚠️ Accept Risk / Exception
                      </button>
                    </div>
                    <div style="display: flex; flex-direction: column; gap: 8px;">
                      <textarea 
                        id="auditor-note-input"
                        class="form-input" 
                        rows="2" 
                        placeholder="Attach internal auditor note or remediation Jira ticket #..."
                        style="font-size: 0.84rem; resize: none;"
                      >${escapeHtml(state.selectedFinding.auditor_note || '')}</textarea>
                      <button class="btn btn-secondary" id="btn-save-note" style="align-self: flex-start; padding: 6px 14px; font-size: 0.78rem;">
                        💾 Save Note
                      </button>
                    </div>
                  </div>
                ` : `
                  <!-- Polished Empty State -->
                  <div class="inspector-empty-state">
                    <div class="empty-state-icon">🛡️</div>
                    <div class="empty-state-title">Select a Regulatory Clause</div>
                    <div class="empty-state-desc">
                      Choose any clause from the Compliance Matrix on the left to inspect grounded policy evidence, RAG citations, and auditor remediation workflows.
                    </div>
                  </div>
                `}
              </div>
            </section>
          </div>
        </main>

        <!-- Floating Agent Execution Console (Drawer) -->
        <div class="agent-drawer" style="transform: ${state.drawerOpen ? 'translateY(0)' : 'translateY(calc(100% - 44px))'};">
          <div class="agent-drawer-bar" id="drawer-toggle">
            <div>
              <span class="agent-pulse"></span>
              <strong>Autonomous Multi-Agent Core:</strong> ${state.isSubmitting ? 'Audit Execution Active' : 'Ready'}
              ${state.isSubmitting ? ` (${state.jobProgress}%)` : ''}
            </div>
            <div style="font-size: 0.8rem; color: var(--accent-cyan-light); font-weight: 600;">
              ${state.drawerOpen ? '▼ Minimize Drawer' : '▲ Open Live Agent Traces'}
            </div>
          </div>

          <div class="agent-log-window">
            ${state.agentLogs.length === 0 ? `
              <div style="color: var(--text-dim)">Autonomous Multi-Agent Core ready. Launch an audit to observe real-time agent execution traces (Clause Extractor ➔ Evidence Hunter ➔ Compliance Auditor ➔ Matrix Generator).</div>
            ` : state.agentLogs.map(log => `
              <div class="log-entry">
                <span class="log-time">[${escapeHtml(log.timestamp)}]</span>
                <span class="log-agent">${escapeHtml(log.agent_name)}:</span>
                <span class="log-msg">${escapeHtml(log.message)}</span>
              </div>
            `).join('')}
          </div>
        </div>

        <!-- Launch New Audit Modal -->
        ${state.showNewAuditModal ? `
          <div class="modal-overlay" id="modal-audit-overlay">
            <div class="modal-dialog">
              <div class="modal-header">
                <h3 style="font-size: 1.15rem; font-weight: 700;">⚡ Launch Autonomous Multi-Agent Audit</h3>
                <button class="btn btn-ghost" id="btn-close-audit-modal">✕</button>
              </div>
              <div class="modal-body">
                <div class="form-group">
                  <label class="form-label">Regulatory Standard Framework Document</label>
                  <input type="text" class="form-input" id="input-standard" value="sample.pdf" placeholder="e.g. sample.pdf or iso27001.pdf" />
                </div>

                <div class="form-group">
                  <label class="form-label">Company Policy Document</label>
                  <input type="text" class="form-input" id="input-policy" value="sample.pdf" placeholder="e.g. sample.pdf or policy.pdf" />
                </div>

                <div class="form-group">
                  <label class="form-label">Audit Depth (Max Clauses): <span id="clauses-val" style="color: var(--accent-cyan-light); font-weight: 700;">10</span></label>
                  <input type="range" id="input-max-clauses" min="3" max="25" value="10" />
                </div>

                <button class="btn btn-primary" id="btn-confirm-audit" style="width: 100%; justify-content: center; margin-top: 10px; padding: 12px;">
                  ${state.isSubmitting ? 'Starting Background Worker...' : 'Initiate Autonomous Audit'}
                </button>
              </div>
            </div>
          </div>
        ` : ''}

        <!-- Auth Modal -->
        ${state.showAuthModal ? `
          <div class="modal-overlay" id="modal-auth-overlay">
            <div class="modal-dialog">
              <div class="modal-header">
                <h3 style="font-size: 1.15rem; font-weight: 700;">
                  ${state.authMode === 'login' ? '🔐 Sign In to AegisAudit' : '📝 Create Organization Account'}
                </h3>
                <button class="btn btn-ghost" id="btn-close-auth-modal">✕</button>
              </div>
              <div class="modal-body">
                ${state.authMode === 'register' ? `
                  <div class="form-group">
                    <label class="form-label">Full Name</label>
                    <input type="text" class="form-input" id="auth-name" value="${escapeHtml(state.authName)}" />
                  </div>
                ` : ''}
                <div class="form-group">
                  <label class="form-label">Work Email</label>
                  <input type="email" class="form-input" id="auth-email" value="${escapeHtml(state.authEmail)}" />
                </div>
                <div class="form-group">
                  <label class="form-label">Password</label>
                  <input type="password" class="form-input" id="auth-pass" value="${escapeHtml(state.authPass)}" />
                </div>

                <button class="btn btn-primary" id="btn-submit-auth" style="justify-content: center; padding: 12px;">
                  ${state.authMode === 'login' ? 'Sign In' : 'Create Account'}
                </button>

                <div style="text-align: center; font-size: 0.82rem; color: var(--text-muted); margin-top: 6px;">
                  ${state.authMode === 'login' ? `
                    <span>Need an account? <a href="#" id="toggle-auth-reg" style="color: var(--accent-cyan-light); font-weight: 600;">Register</a></span>
                  ` : `
                    <span>Already have an account? <a href="#" id="toggle-auth-login" style="color: var(--accent-cyan-light); font-weight: 600;">Sign In</a></span>
                  `}
                </div>
              </div>
            </div>
          </div>
        ` : ''}
      </div>
    `;

    bindEvents();
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // Event Handlers
  function bindEvents() {
    // Theme Switcher
    const btnTheme = document.getElementById('btn-theme-toggle');
    if (btnTheme) btnTheme.onclick = toggleTheme;

    // Export CSV
    const btnExport = document.getElementById('btn-export-csv');
    if (btnExport) {
      btnExport.onclick = () => {
        if (!state.report) return;
        let csv = 'Clause ID,Title,Requirement,Status,Risk Level,Gap Analysis,Remediation\n';
        state.report.findings.forEach(f => {
          csv += `"${f.clause_id}","${f.clause_title}","${f.requirement_summary}","${f.status}","${f.risk_level}","${f.gap_analysis}","${f.remediation_recommendation}"\n`;
        });
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${state.report.audit_id}_matrix.csv`;
        a.click();
      };
    }

    // Auditor Approval & Notes
    const btnApprove = document.getElementById('btn-approve-finding');
    if (btnApprove && state.selectedFinding) {
      btnApprove.onclick = () => {
        state.selectedFinding.approved = !state.selectedFinding.approved;
        render();
      };
    }

    const btnRisk = document.getElementById('btn-accept-risk');
    if (btnRisk && state.selectedFinding) {
      btnRisk.onclick = () => {
        state.selectedFinding.status = 'Partially Compliant';
        state.selectedFinding.risk_level = 'Low';
        state.selectedFinding.auditor_note = (state.selectedFinding.auditor_note || '') + ' [Auditor Accepted Exception]';
        render();
      };
    }

    const btnSaveNote = document.getElementById('btn-save-note');
    if (btnSaveNote && state.selectedFinding) {
      btnSaveNote.onclick = () => {
        const noteInput = document.getElementById('auditor-note-input');
        if (noteInput) {
          state.selectedFinding.auditor_note = noteInput.value.trim();
          alert('Note saved to finding!');
          render();
        }
      };
    }

    // Launch Audit Modal
    const btnLaunch = document.getElementById('btn-launch-modal');
    if (btnLaunch) {
      btnLaunch.onclick = () => {
        state.showNewAuditModal = true;
        render();
      };
    }

    const btnCloseAudit = document.getElementById('btn-close-audit-modal');
    if (btnCloseAudit) {
      btnCloseAudit.onclick = () => {
        state.showNewAuditModal = false;
        render();
      };
    }

    const rangeSlider = document.getElementById('input-max-clauses');
    if (rangeSlider) {
      rangeSlider.oninput = (e) => {
        const valSpan = document.getElementById('clauses-val');
        if (valSpan) valSpan.innerText = e.target.value;
      };
    }

    const btnConfirmAudit = document.getElementById('btn-confirm-audit');
    if (btnConfirmAudit) {
      btnConfirmAudit.onclick = () => {
        const stdInput = document.getElementById('input-standard');
        const polInput = document.getElementById('input-policy');
        const clausesInput = document.getElementById('input-max-clauses');

        const std = stdInput ? stdInput.value.trim() : 'sample.pdf';
        const pol = polInput ? polInput.value.trim() : 'sample.pdf';
        const maxC = clausesInput ? parseInt(clausesInput.value) : 10;

        startAudit(std, pol, maxC);
      };
    }

    // Auth Modals
    const btnOpenLogin = document.getElementById('btn-open-login');
    if (btnOpenLogin) {
      btnOpenLogin.onclick = () => {
        state.showAuthModal = true;
        state.authMode = 'login';
        render();
      };
    }

    const btnCloseAuth = document.getElementById('btn-close-auth-modal');
    if (btnCloseAuth) {
      btnCloseAuth.onclick = () => {
        state.showAuthModal = false;
        render();
      };
    }

    const toggleAuthReg = document.getElementById('toggle-auth-reg');
    if (toggleAuthReg) {
      toggleAuthReg.onclick = (e) => {
        e.preventDefault();
        state.authMode = 'register';
        render();
      };
    }

    const toggleAuthLogin = document.getElementById('toggle-auth-login');
    if (toggleAuthLogin) {
      toggleAuthLogin.onclick = (e) => {
        e.preventDefault();
        state.authMode = 'login';
        render();
      };
    }

    const btnSubmitAuth = document.getElementById('btn-submit-auth');
    if (btnSubmitAuth) {
      btnSubmitAuth.onclick = async () => {
        const emailInput = document.getElementById('auth-email');
        const passInput = document.getElementById('auth-pass');
        const nameInput = document.getElementById('auth-name');

        const email = emailInput ? emailInput.value.trim() : '';
        const pass = passInput ? passInput.value.trim() : '';
        const name = nameInput ? nameInput.value.trim() : 'Security Officer';

        if (!email || !pass) {
          alert('Please enter email and password');
          return;
        }

        try {
          if (state.authMode === 'login') {
            const formData = new URLSearchParams();
            formData.append('username', email);
            formData.append('password', pass);

            const res = await fetch(`${API_BASE}/api/auth/token`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
              body: formData
            });

            if (!res.ok) throw new Error('Invalid email or password');
            const data = await res.json();
            state.token = data.access_token;
            localStorage.setItem('aegis_token', data.access_token);

            // Fetch user profile
            const meRes = await fetch(`${API_BASE}/api/auth/me`, {
              headers: { 'Authorization': `Bearer ${data.access_token}` }
            });
            if (meRes.ok) {
              state.user = await meRes.json();
            }
            state.showAuthModal = false;
            render();
          } else {
            const res = await fetch(`${API_BASE}/api/auth/register`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ email, password: pass, full_name: name, role: 'auditor' })
            });

            if (!res.ok) throw new Error('Registration failed');
            alert('Registration successful! Please sign in.');
            state.authMode = 'login';
            render();
          }
        } catch (err) {
          alert(err.message);
        }
      };
    }

    const btnLogout = document.getElementById('btn-logout');
    if (btnLogout) {
      btnLogout.onclick = () => {
        state.token = '';
        state.user = null;
        localStorage.removeItem('aegis_token');
        render();
      };
    }

    // Finding Row Clicks
    const rows = document.querySelectorAll('.finding-row');
    rows.forEach(row => {
      row.onclick = () => {
        const cid = row.getAttribute('data-clause');
        const found = (state.report?.findings || []).find(f => f.clause_id === cid);
        if (found) {
          state.selectedFinding = found;
          render();
        }
      };
    });

    // Filter Buttons
    const filterBtns = document.querySelectorAll('.filter-btn');
    filterBtns.forEach(btn => {
      btn.onclick = () => {
        state.filter = btn.getAttribute('data-filter');
        render();
      };
    });

    // Search Input
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
      searchInput.oninput = (e) => {
        state.search = e.target.value;
        render();
        const newSearch = document.getElementById('search-input');
        if (newSearch) {
          newSearch.focus();
          newSearch.setSelectionRange(newSearch.value.length, newSearch.value.length);
        }
      };
    }

    // Drawer Toggle
    const drawerToggle = document.getElementById('drawer-toggle');
    if (drawerToggle) {
      drawerToggle.onclick = () => {
        state.drawerOpen = !state.drawerOpen;
        render();
      };
    }

    // History Dropdown
    const selectHistory = document.getElementById('select-history');
    if (selectHistory) {
      selectHistory.onchange = (e) => {
        const auditId = e.target.value;
        fetch(`${API_BASE}/api/audit/${auditId}`, {
          headers: state.token ? { 'Authorization': `Bearer ${state.token}` } : {}
        })
        .then(r => r.ok ? r.json() : null)
        .then(rep => {
          if (rep) {
            state.report = rep;
            state.selectedFinding = rep.findings?.[0] || null;
            render();
          }
        });
      };
    }
  }

  // Launch Audit Action
  async function startAudit(std, pol, maxC) {
    state.isSubmitting = true;
    state.drawerOpen = true;
    state.showNewAuditModal = false;
    state.agentLogs = [{
      timestamp: new Date().toLocaleTimeString(),
      agent_name: 'AuditOrchestrator',
      message: `Dispatching audit job for '${std}' vs '${pol}' (Max clauses: ${maxC})...`,
      progress_pct: 5
    }];
    render();

    try {
      const res = await fetch(`${API_BASE}/api/audit/jobs/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': state.token ? `Bearer ${state.token}` : ''
        },
        body: JSON.stringify({
          standard_filename: std,
          policy_filename: pol,
          max_clauses: maxC
        })
      });

      if (!res.ok) throw new Error('API server returned error');
      const jobData = await res.json();

      const eventSource = new EventSource(`${API_BASE}/api/audit/jobs/${jobData.job_id}/stream`);
      eventSource.onmessage = (e) => {
        try {
          const log = JSON.parse(e.data);
          state.agentLogs.push(log);
          if (log.progress_pct) state.jobProgress = log.progress_pct;
          render();
        } catch(err) {}
      };

      eventSource.addEventListener('end', () => {
        eventSource.close();
        state.isSubmitting = false;

        fetch(`${API_BASE}/api/audit/jobs/${jobData.job_id}/status`, {
          headers: state.token ? { 'Authorization': `Bearer ${state.token}` } : {}
        })
        .then(r => r.json())
        .then(doneJob => {
          if (doneJob.result) {
            state.report = doneJob.result;
            state.selectedFinding = doneJob.result.findings?.[0] || null;
            render();
          }
        });
      });

      eventSource.onerror = () => {
        eventSource.close();
        state.isSubmitting = false;
        render();
      };

    } catch (e) {
      state.isSubmitting = false;
      alert(`Could not dispatch audit: ${e.message}`);
      render();
    }
  }

  // Initial Data Fetch
  function initData() {
    fetch(`${API_BASE}/api/audit/history`, {
      headers: state.token ? { 'Authorization': `Bearer ${state.token}` } : {}
    })
    .then(r => r.ok ? r.json() : [])
    .then(list => {
      if (Array.isArray(list) && list.length > 0) {
        state.pastAudits = list;
        fetch(`${API_BASE}/api/audit/${list[0].audit_id}`, {
          headers: state.token ? { 'Authorization': `Bearer ${state.token}` } : {}
        })
        .then(r => r.ok ? r.json() : null)
        .then(rep => {
          if (rep) {
            state.report = rep;
            state.selectedFinding = rep.findings?.[0] || null;
            render();
          }
        });
      }
    })
    .catch(() => {});
  }

  // Initial mount
  render();
  initData();
})();
