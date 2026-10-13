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
    --card-border: #1F2937;
    --accent-cyan: #0EA5E9;
    --accent-glow: rgba(14, 165, 233, 0.25);
    --compliant-green: #10B981;
    --partial-amber: #F59E0B;
    --non-compliant-red: #EF4444;
    --text-primary: #F9FAFB;
    --text-secondary: #94A3B8;
}

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--text-primary);
}

.stApp {
    background-color: var(--bg-dark);
}

/* Header Banner */
.header-container {
    background: linear-gradient(135deg, #111827 0%, #1E293B 100%);
    border: 1px solid var(--card-border);
    border-radius: 14px;
    padding: 24px 28px;
    margin-bottom: 24px;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
}

.header-title {
    font-size: 2.1rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    background: linear-gradient(90deg, #38BDF8 0%, #818CF8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}

.header-subtitle {
    font-size: 0.95rem;
    color: var(--text-secondary);
    margin-top: 6px;
    margin-bottom: 0;
}

/* Metric Cards */
.metric-card {
    background-color: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.25);
    text-align: center;
    transition: transform 0.2s ease, border-color 0.2s ease;
}

.metric-card:hover {
    border-color: var(--accent-cyan);
    transform: translateY(-2px);
}

.metric-val {
    font-size: 2rem;
    font-weight: 700;
    line-height: 1.1;
    margin: 4px 0;
}

.metric-label {
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-secondary);
}

/* Audit Finding Card */
.finding-card {
    background-color: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
    transition: all 0.2s ease-in-out;
}

.finding-card:hover {
    border-color: rgba(56, 189, 248, 0.4);
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.35);
}

.badge-compliant {
    background-color: rgba(16, 185, 129, 0.15);
    color: #34D399;
    border: 1px solid rgba(16, 185, 129, 0.4);
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 600;
}

.badge-partial {
    background-color: rgba(245, 158, 11, 0.15);
    color: #FBBF24;
    border: 1px solid rgba(245, 158, 11, 0.4);
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 600;
}

.badge-non-compliant {
    background-color: rgba(239, 68, 68, 0.15);
    color: #F87171;
    border: 1px solid rgba(239, 68, 68, 0.4);
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 600;
}

.badge-risk {
    background-color: #1F2937;
    color: #E2E8F0;
    border: 1px solid #374151;
    padding: 4px 8px;
    border-radius: 6px;
    font-size: 0.72rem;
    font-weight: 500;
    font-family: 'JetBrains Mono', monospace;
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
}
</style>
"""
