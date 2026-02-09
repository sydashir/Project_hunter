#!/usr/bin/env python3
"""
Project Hunter - Professional Dashboard
Modern, sleek interface for competitor intelligence
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import requests
from pathlib import Path
from collections import Counter
import sys

sys.path.append(str(Path(__file__).parent))

# Page config - must be first
st.set_page_config(
    page_title="Project Hunter",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Modern dark theme CSS
st.markdown("""
<style>
    /* Import Inter font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global styles */
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
        font-family: 'Inter', sans-serif;
    }

    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Main header */
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 2rem;
    }

    .sub-header {
        color: #a0aec0;
        text-align: center;
        font-size: 1rem;
        margin-top: -1.5rem;
        margin-bottom: 2rem;
    }

    /* Metric cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        backdrop-filter: blur(10px);
        transition: transform 0.2s, box-shadow 0.2s;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.2);
    }

    .metric-value {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .metric-label {
        color: #a0aec0;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.5rem;
    }

    /* Status indicator */
    .status-online {
        display: inline-flex;
        align-items: center;
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: #10b981;
        padding: 0.5rem 1rem;
        border-radius: 50px;
        font-size: 0.85rem;
        font-weight: 500;
    }

    .status-offline {
        display: inline-flex;
        align-items: center;
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.3);
        color: #ef4444;
        padding: 0.5rem 1rem;
        border-radius: 50px;
        font-size: 0.85rem;
        font-weight: 500;
    }

    .pulse {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #10b981;
        margin-right: 8px;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }

    /* Section headers */
    .section-header {
        color: #e2e8f0;
        font-size: 1.25rem;
        font-weight: 600;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(102, 126, 234, 0.3);
    }

    /* Domain list */
    .domain-item {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: background 0.2s;
    }

    .domain-item:hover {
        background: rgba(255, 255, 255, 0.08);
    }

    .domain-name {
        color: #e2e8f0;
        font-weight: 500;
    }

    .domain-position {
        color: #667eea;
        font-size: 0.85rem;
        font-weight: 600;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: transform 0.2s, box-shadow 0.2s;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
    }

    /* Data table */
    .dataframe {
        background: rgba(255, 255, 255, 0.02) !important;
        border-radius: 12px !important;
    }

    .dataframe th {
        background: rgba(102, 126, 234, 0.2) !important;
        color: #e2e8f0 !important;
        font-weight: 600 !important;
    }

    .dataframe td {
        color: #cbd5e0 !important;
        border-color: rgba(255, 255, 255, 0.05) !important;
    }

    /* Progress bar */
    .progress-container {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 50px;
        height: 12px;
        overflow: hidden;
        margin: 1rem 0;
    }

    .progress-bar {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        height: 100%;
        border-radius: 50px;
        transition: width 0.5s ease;
    }

    /* Info box */
    .info-box {
        background: rgba(102, 126, 234, 0.1);
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 12px;
        padding: 1.5rem;
        color: #e2e8f0;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        color: #a0aec0;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# API Functions
def get_api_status():
    try:
        response = requests.get("http://localhost:8000/api/discover/stats", timeout=2)
        if response.status_code == 200:
            return True, response.json()
        return False, {"total_domains": 0, "domains": []}
    except:
        return False, {"total_domains": 0, "domains": []}

def reset_api():
    try:
        requests.post("http://localhost:8000/api/discover/reset", timeout=2)
        return True
    except:
        return False

def load_competitors():
    try:
        from core.persistence.database import Database
        db = Database()
        return db.load_competitors()
    except:
        return []

# Header
st.markdown('<div class="main-header">🎯 Project Hunter</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Google Discover Competitor Intelligence</div>', unsafe_allow_html=True)

# Get data
api_online, api_data = get_api_status()
total_domains = api_data.get("total_domains", 0)
domains = api_data.get("domains", [])
competitors = load_competitors()

# Status bar
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if api_online:
        st.markdown('''
            <div style="text-align: center;">
                <span class="status-online">
                    <span class="pulse"></span>
                    API Server Online
                </span>
            </div>
        ''', unsafe_allow_html=True)
    else:
        st.markdown('''
            <div style="text-align: center;">
                <span class="status-offline">
                    ⚠ API Server Offline
                </span>
            </div>
        ''', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Main metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value">{total_domains}</div>
            <div class="metric-label">Domains Captured</div>
        </div>
    ''', unsafe_allow_html=True)

with col2:
    st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value">{len(competitors)}</div>
            <div class="metric-label">Stored in DB</div>
        </div>
    ''', unsafe_allow_html=True)

with col3:
    target = 100
    progress_pct = min(int((total_domains / target) * 100), 100)
    st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value">{progress_pct}%</div>
            <div class="metric-label">Target Progress</div>
        </div>
    ''', unsafe_allow_html=True)

with col4:
    unique_tlds = len(set([d.split('.')[-1] if '.' in d else d for d in domains]))
    st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value">{unique_tlds}</div>
            <div class="metric-label">Unique TLDs</div>
        </div>
    ''', unsafe_allow_html=True)

# Progress bar
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(f'''
    <div class="progress-container">
        <div class="progress-bar" style="width: {progress_pct}%;"></div>
    </div>
    <p style="color: #a0aec0; text-align: center; font-size: 0.85rem;">
        {total_domains} of {target} domains captured
    </p>
''', unsafe_allow_html=True)

# Tabs
st.markdown("<br>", unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["📡 Live Capture", "📊 Analytics", "⚙️ Controls"])

with tab1:
    st.markdown('<div class="section-header">Recently Captured Domains</div>', unsafe_allow_html=True)

    if domains:
        # Show last 20 domains
        recent = domains[-20:][::-1]

        for i, domain in enumerate(recent):
            position = len(domains) - i
            st.markdown(f'''
                <div class="domain-item">
                    <span class="domain-name">{domain}</span>
                    <span class="domain-position">#{position}</span>
                </div>
            ''', unsafe_allow_html=True)

        if len(domains) > 20:
            st.markdown(f'''
                <p style="color: #a0aec0; text-align: center; margin-top: 1rem;">
                    Showing 20 of {len(domains)} domains
                </p>
            ''', unsafe_allow_html=True)
    else:
        st.markdown('''
            <div class="info-box">
                <h4 style="margin: 0 0 0.5rem 0;">👋 No domains captured yet</h4>
                <p style="margin: 0; opacity: 0.8;">
                    Start browsing Google Discover with the Chrome extension to capture competitor domains.
                </p>
            </div>
        ''', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="section-header">Domain Analytics</div>', unsafe_allow_html=True)

    if domains:
        col1, col2 = st.columns(2)

        with col1:
            # TLD distribution
            tlds = [d.split('.')[-1] if '.' in d else 'other' for d in domains]
            tld_counts = pd.Series(tlds).value_counts().head(10)

            fig = go.Figure(data=[go.Pie(
                labels=tld_counts.index,
                values=tld_counts.values,
                hole=0.6,
                marker_colors=px.colors.sequential.Purples_r
            )])
            fig.update_layout(
                title="Domain TLDs",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#e2e8f0',
                showlegend=True,
                legend=dict(font=dict(color='#a0aec0')),
                margin=dict(t=50, b=20, l=20, r=20)
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Capture timeline (simulated based on position)
            positions = list(range(1, len(domains) + 1))

            fig = go.Figure(data=[go.Scatter(
                x=positions,
                y=list(range(1, len(domains) + 1)),
                mode='lines+markers',
                line=dict(color='#667eea', width=2),
                marker=dict(size=4, color='#764ba2'),
                fill='tozeroy',
                fillcolor='rgba(102, 126, 234, 0.1)'
            )])
            fig.update_layout(
                title="Capture Progress",
                xaxis_title="Capture Order",
                yaxis_title="Total Domains",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#e2e8f0',
                xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                margin=dict(t=50, b=50, l=50, r=20)
            )
            st.plotly_chart(fig, use_container_width=True)

        # Domain table
        st.markdown('<div class="section-header">All Captured Domains</div>', unsafe_allow_html=True)

        df = pd.DataFrame({
            'Position': range(1, len(domains) + 1),
            'Domain': domains,
            'TLD': [d.split('.')[-1] if '.' in d else '-' for d in domains]
        })

        st.dataframe(
            df,
            use_container_width=True,
            height=400,
            hide_index=True
        )

        # Export
        csv = df.to_csv(index=False)
        st.download_button(
            "📥 Export to CSV",
            csv,
            f"discover_domains_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            "text/csv"
        )
    else:
        st.info("No data to analyze yet. Start capturing domains first.")

with tab3:
    st.markdown('<div class="section-header">System Controls</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()

    with col2:
        if st.button("🗑️ Reset Counter", use_container_width=True):
            if reset_api():
                st.success("Counter reset!")
                st.rerun()
            else:
                st.error("Failed to reset")

    with col3:
        if st.button("📊 Clear Cache", use_container_width=True):
            st.cache_data.clear()
            st.success("Cache cleared!")

    st.markdown("<br>", unsafe_allow_html=True)

    # Instructions
    st.markdown('''
        <div class="info-box">
            <h4 style="margin: 0 0 1rem 0;">📋 Quick Start Guide</h4>
            <ol style="margin: 0; padding-left: 1.5rem; line-height: 2;">
                <li>Start API server: <code>python api/discover_api.py</code></li>
                <li>Install Chrome extension from <code>chrome_extension/</code></li>
                <li>Open Chrome DevTools → Enable mobile emulation</li>
                <li>Browse <code>google.com</code> and scroll through Discover</li>
                <li>Watch the counter increase as domains are captured</li>
            </ol>
        </div>
    ''', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # System info
    st.markdown('<div class="section-header">System Status</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f'''
            <div class="domain-item">
                <span class="domain-name">API Server</span>
                <span class="domain-position">{"✓ Online" if api_online else "✗ Offline"}</span>
            </div>
            <div class="domain-item">
                <span class="domain-name">Database</span>
                <span class="domain-position">{len(competitors)} records</span>
            </div>
        ''', unsafe_allow_html=True)

    with col2:
        st.markdown(f'''
            <div class="domain-item">
                <span class="domain-name">Last Update</span>
                <span class="domain-position">{datetime.now().strftime("%H:%M:%S")}</span>
            </div>
            <div class="domain-item">
                <span class="domain-name">Target</span>
                <span class="domain-position">{target} domains</span>
            </div>
        ''', unsafe_allow_html=True)

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown('''
    <div style="text-align: center; color: #4a5568; font-size: 0.8rem; padding: 1rem;">
        Project Hunter • Google Discover Intelligence Platform
    </div>
''', unsafe_allow_html=True)

# Auto-refresh every 5 seconds
st.markdown('''
    <script>
        setTimeout(function() {
            window.location.reload();
        }, 10000);
    </script>
''', unsafe_allow_html=True)
