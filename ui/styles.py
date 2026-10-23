"""
UI Styles and Theme System for AegisAudit AI.
Obsidian Slate & Cyber Cobalt Palette with High-Contrast Risk Accents.
"""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --bg-dark: #0B0F19;
    --card-bg: #111827;
    --card-surface: #1E293B;
    --card-border: #1F2937;
    --card-border-hover: #38BDF8;
    --accent-cyan: #0EA5E9;
    --accent-glow: rgba(14, 165, 233, 0.25);
    --compliant-green: #10B981;
    --partial-amber: #F59E0B;
    --non-compliant-red: #EF4444;
    --text-primary: #F9FAFB;
    --text-secondary: #94A3B8;
    --text-muted: #64748B;
}

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--text-primary);
}

.stApp {
    background-color: var(--bg-dark);
}

/* Remove excessive Streamlit padding */
.block-container {
    padding-top: 1.8rem;
    padding-bottom: 2.5rem;
    padding-left: 2.5rem;
    padding-right: 2.5rem;
    max-width: 95%;
}

/* Top Application Header */
.app-header {
    background: linear-gradient(135deg, rgba(17, 24, 39, 0.95) 0%, rgba(30, 41, 59, 0.85) 100%);
    border: 1px solid var(--card-border);
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 20px;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.header-brand {
    display: flex;
    align-items: center;
    gap: 14px;
}

.header-title {
    font-size: 1.8rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    background: linear-gradient(90deg, #38BDF8 0%, #818CF8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}

.header-subtitle {
    font-size: 0.85rem;
    color: var(--text-secondary);
    margin: 2px 0 0 0;
}

.header-badge {
    background: rgba(14, 165, 233, 0.12);
    border: 1px solid rgba(14, 165, 233, 0.35);
    color: #38BDF8;
    padding: 6px 14px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* Navigation / Sidebar Customization */
section[data-testid="stSidebar"] {
    background-color: #070B14;
    border-right: 1px solid var(--card-border);
}

.sidebar-profile-card {
    background: rgba(17, 24, 39, 0.7);
    border: 1px solid var(--card-border);
    border-radius: 10px;
    padding: 14px;
    margin-bottom: 16px;
}

/* Metric KPI Cards */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 24px;
}

.metric-card {
    background: linear-gradient(180deg, rgba(30, 41, 59, 0.5) 0%, rgba(17, 24, 39, 0.9) 100%);
    border: 1px solid var(--card-border);
    border-radius: 12px;
    padding: 18px 20px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    text-align: left;
    transition: all 0.25s ease;
    position: relative;
    overflow: hidden;
}

.metric-card:hover {
    border-color: var(--card-border-hover);
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(14, 165, 233, 0.15);
}

.metric-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #38BDF8, #818CF8);
}

.metric-card.compliant::before {
    background: #10B981;
}

.metric-card.partial::before {
    background: #F59E0B;
}

.metric-card.non-compliant::before {
    background: #EF4444;
}

.metric-val {
    font-size: 2.2rem;
    font-weight: 800;
    line-height: 1.1;
    margin: 8px 0 4px 0;
}

.metric-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-secondary);
    font-weight: 600;
}

.metric-sub {
    font-size: 0.78rem;
    color: var(--text-muted);
}

/* Two-Pane Explorer Layout */
.explorer-header {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 10px;
    padding: 12px 18px;
    margin-bottom: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.clause-item-card {
    background: rgba(17, 24, 39, 0.85);
    border: 1px solid var(--card-border);
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 10px;
    cursor: pointer;
    transition: all 0.2s ease;
}

.clause-item-card:hover {
    border-color: var(--accent-cyan);
    background: rgba(30, 41, 59, 0.7);
    transform: translateX(3px);
}

.clause-item-card.active {
    border-color: #38BDF8;
    background: rgba(14, 165, 233, 0.12);
    box-shadow: 0 0 15px rgba(14, 165, 233, 0.2);
}

/* Inspector Panel */
.inspector-card {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 14px;
    padding: 24px;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
    min-height: 550px;
}

.inspector-section {
    margin-bottom: 20px;
}

.inspector-title {
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text-muted);
    font-weight: 700;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 6px;
}

.inspector-box-mandate {
    background: rgba(30, 41, 59, 0.6);
    border-left: 3px solid #818CF8;
    padding: 14px 16px;
    border-radius: 6px;
    font-size: 0.92rem;
    line-height: 1.5;
    color: #F1F5F9;
}

.inspector-box-evidence {
    background: rgba(15, 23, 42, 0.8);
    border-left: 3px solid #0EA5E9;
    padding: 14px 16px;
    border-radius: 6px;
    font-size: 0.9rem;
    line-height: 1.5;
    color: #CBD5E1;
}

.inspector-box-gap {
    background: rgba(239, 68, 68, 0.08);
    border-left: 3px solid #EF4444;
    padding: 14px 16px;
    border-radius: 6px;
    font-size: 0.9rem;
    line-height: 1.5;
    color: #FCA5A5;
}

.inspector-box-remediation {
    background: rgba(16, 185, 129, 0.08);
    border-left: 3px solid #10B981;
    padding: 14px 16px;
    border-radius: 6px;
    font-size: 0.9rem;
    line-height: 1.5;
    color: #A7F3D0;
}

/* Badges */
.badge-compliant {
    background-color: rgba(16, 185, 129, 0.15);
    color: #34D399;
    border: 1px solid rgba(16, 185, 129, 0.4);
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 0.74rem;
    font-weight: 600;
    display: inline-block;
}

.badge-partial {
    background-color: rgba(245, 158, 11, 0.15);
    color: #FBBF24;
    border: 1px solid rgba(245, 158, 11, 0.4);
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 0.74rem;
    font-weight: 600;
    display: inline-block;
}

.badge-non-compliant {
    background-color: rgba(239, 68, 68, 0.15);
    color: #F87171;
    border: 1px solid rgba(239, 68, 68, 0.4);
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 0.74rem;
    font-weight: 600;
    display: inline-block;
}

.badge-risk {
    background-color: #1F2937;
    color: #E2E8F0;
    border: 1px solid #374151;
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 0.72rem;
    font-weight: 500;
    font-family: 'JetBrains Mono', monospace;
    display: inline-block;
}

.badge-verified {
    background-color: rgba(14, 165, 233, 0.15);
    color: #38BDF8;
    border: 1px solid rgba(14, 165, 233, 0.5);
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 0.72rem;
    font-weight: 600;
    display: inline-block;
}

.citation-chip {
    background-color: rgba(56, 189, 248, 0.1);
    color: #7DD3FC;
    border: 1px solid rgba(56, 189, 248, 0.25);
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 0.72rem;
    font-family: 'JetBrains Mono', monospace;
    display: inline-block;
    margin-right: 6px;
    margin-bottom: 4px;
}

/* Wizard Cards */
.wizard-step-card {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 12px;
    padding: 22px;
    margin-bottom: 18px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
}

.wizard-step-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 14px;
}

.wizard-step-num {
    background: linear-gradient(135deg, #0EA5E9, #6366F1);
    color: white;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.85rem;
}

.wizard-step-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
}

/* Standards Library Cards */
.standard-card {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
    transition: all 0.2s ease;
}

.standard-card:hover {
    border-color: var(--accent-cyan);
    transform: translateY(-2px);
    box-shadow: 0 6px 25px rgba(0, 0, 0, 0.35);
}
</style>
"""
