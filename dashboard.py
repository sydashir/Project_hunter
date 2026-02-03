#!/usr/bin/env python3
"""
Project Hunter - Real-Time Dashboard

Streamlit dashboard for monitoring competitor discovery and intelligence analysis.
Run with: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import sqlite3
import requests
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent))

from core.persistence.database import Database
from core.persistence.models import CompetitorSite

# Page configuration
st.set_page_config(
    page_title="Project Hunter Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🎯 Project Hunter Dashboard</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/150x150.png?text=🎯", width=150)
    st.title("Navigation")

    page = st.radio(
        "Select View",
        ["📊 Overview", "🔍 Competitor Discovery", "📈 Intelligence Analysis", "⚙️ Settings"]
    )

    st.markdown("---")
    st.subheader("System Status")

    # Check API status
    try:
        response = requests.get("http://localhost:8000/api/discover/stats", timeout=2)
        if response.status_code == 200:
            st.success("✓ API Server Online")
            api_online = True
        else:
            st.error("✗ API Server Error")
            api_online = False
    except:
        st.warning("⚠ API Server Offline")
        api_online = False

    # Database status
    db = Database()
    competitors = db.load_competitors()
    st.info(f"📁 {len(competitors)} Competitors Loaded")

    st.markdown("---")
    st.caption("Last updated: " + datetime.now().strftime("%H:%M:%S"))

    if st.button("🔄 Refresh Data"):
        st.rerun()

# Helper functions
@st.cache_data(ttl=5)
def get_api_stats():
    """Get stats from API server"""
    try:
        response = requests.get("http://localhost:8000/api/discover/stats", timeout=2)
        if response.status_code == 200:
            return response.json()
        return {"total_domains": 0, "domains": []}
    except:
        return {"total_domains": 0, "domains": []}

@st.cache_data(ttl=10)
def load_competitors():
    """Load competitors from database"""
    db = Database()
    return db.load_competitors()

@st.cache_data(ttl=10)
def load_articles():
    """Load articles from SQLite database"""
    db_path = Path("data/articles/articles.db")
    if not db_path.exists():
        return pd.DataFrame()

    conn = sqlite3.connect(db_path)
    query = "SELECT * FROM articles ORDER BY publish_date DESC LIMIT 1000"
    try:
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except:
        conn.close()
        return pd.DataFrame()

def load_intelligence():
    """Load intelligence reports"""
    intel_path = Path("data/intelligence")

    data = {
        "niche_scores": {},
        "patterns": {},
        "title_formulas": [],
        "timing_insights": {}
    }

    if intel_path.exists():
        for file in ["niche_scores.json", "patterns.json", "title_formulas.json", "timing_insights.json"]:
            file_path = intel_path / file
            if file_path.exists():
                with open(file_path, 'r') as f:
                    key = file.replace('.json', '')
                    data[key] = json.load(f)

    return data

# ==================== OVERVIEW PAGE ====================
if page == "📊 Overview":
    st.header("System Overview")

    # Top metrics
    col1, col2, col3, col4 = st.columns(4)

    api_stats = get_api_stats()
    competitors = load_competitors()
    articles_df = load_articles()

    with col1:
        st.metric(
            label="🔍 Domains Captured",
            value=api_stats.get("total_domains", 0),
            delta="Live from extension"
        )

    with col2:
        st.metric(
            label="🎯 Competitors Stored",
            value=len(competitors),
            delta=f"{len([c for c in competitors if c.discovery_source == 'chrome_extension'])} from extension"
        )

    with col3:
        st.metric(
            label="📰 Articles Monitored",
            value=len(articles_df) if not articles_df.empty else 0,
            delta="Total articles"
        )

    with col4:
        extension_comps = [c for c in competitors if c.discovery_source == 'chrome_extension']
        if extension_comps:
            niches = set([c.niche for c in extension_comps])
            st.metric(
                label="📊 Niches Discovered",
                value=len(niches),
                delta="Active niches"
            )
        else:
            st.metric(label="📊 Niches Discovered", value=0)

    st.markdown("---")

    # Real-time capture visualization
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📡 Real-Time Domain Capture")

        if api_stats.get("total_domains", 0) > 0:
            domains = api_stats.get("domains", [])
            recent_domains = domains[-20:]  # Last 20

            df_recent = pd.DataFrame({
                'Domain': recent_domains,
                'Position': list(range(len(recent_domains)))
            })

            fig = px.bar(
                df_recent,
                x='Position',
                y=[1] * len(recent_domains),
                text='Domain',
                title="Recently Captured Domains",
                labels={'y': 'Captured'},
                color_discrete_sequence=['#1f77b4']
            )
            fig.update_traces(textposition='outside', textangle=45)
            fig.update_layout(showlegend=False, height=300)
            st.plotly_chart(fig, use_container_width=True)

            st.caption(f"Showing last {len(recent_domains)} of {len(domains)} captured domains")
        else:
            st.info("⏳ No domains captured yet. Start browsing Google Discover with the extension!")

    with col2:
        st.subheader("🎯 Extension Status")

        if api_stats.get("total_domains", 0) > 0:
            st.success("✓ Extension Active")
            st.metric("Domains in Memory", api_stats.get("total_domains"))

            # Progress to target
            target = 150
            progress = min(api_stats.get("total_domains", 0) / target, 1.0)
            st.progress(progress)
            st.caption(f"Target: {target} domains")
        else:
            st.warning("⚠ No Data Yet")
            st.info("""
            **To start capturing:**
            1. Install Chrome extension
            2. Start API server
            3. Browse Google Discover
            """)

    st.markdown("---")

    # Competitor overview
    if competitors:
        st.subheader("🏆 Competitor Overview")

        col1, col2 = st.columns(2)

        with col1:
            # By niche
            niche_counts = {}
            for comp in competitors:
                niche_counts[comp.niche] = niche_counts.get(comp.niche, 0) + 1

            df_niches = pd.DataFrame(list(niche_counts.items()), columns=['Niche', 'Count'])
            df_niches = df_niches.sort_values('Count', ascending=False)

            fig = px.pie(
                df_niches,
                values='Count',
                names='Niche',
                title='Competitors by Niche',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # By discovery source
            source_counts = {}
            for comp in competitors:
                source_counts[comp.discovery_source] = source_counts.get(comp.discovery_source, 0) + 1

            df_sources = pd.DataFrame(list(source_counts.items()), columns=['Source', 'Count'])

            fig = px.bar(
                df_sources,
                x='Source',
                y='Count',
                title='Discovery Sources',
                color='Source',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig, use_container_width=True)

    # Articles timeline
    if not articles_df.empty and 'publish_date' in articles_df.columns:
        st.subheader("📈 Article Timeline")

        articles_df['publish_date'] = pd.to_datetime(articles_df['publish_date'])
        articles_df['date'] = articles_df['publish_date'].dt.date

        daily_counts = articles_df.groupby('date').size().reset_index(name='count')

        fig = px.line(
            daily_counts,
            x='date',
            y='count',
            title='Articles Monitored Over Time',
            labels={'date': 'Date', 'count': 'Articles'},
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)

# ==================== COMPETITOR DISCOVERY PAGE ====================
elif page == "🔍 Competitor Discovery":
    st.header("Competitor Discovery")

    competitors = load_competitors()

    if not competitors:
        st.warning("⚠ No competitors discovered yet")
        st.info("""
        **Get started:**
        1. Install Chrome extension
        2. Start API server: `python api/discover_api.py`
        3. Browse Google Discover for 30-60 minutes
        4. Run: `python scripts/run_discovery.py`
        """)
    else:
        # Filters
        col1, col2, col3 = st.columns(3)

        with col1:
            all_niches = sorted(list(set([c.niche for c in competitors])))
            selected_niches = st.multiselect("Filter by Niche", all_niches, default=all_niches)

        with col2:
            all_sources = sorted(list(set([c.discovery_source for c in competitors])))
            selected_sources = st.multiselect("Filter by Source", all_sources, default=all_sources)

        with col3:
            min_score = st.slider("Minimum Authority Score", 0, 100, 0)

        # Filter competitors
        filtered = [
            c for c in competitors
            if c.niche in selected_niches
            and c.discovery_source in selected_sources
            and c.authority_score >= min_score
        ]

        st.metric("Filtered Competitors", len(filtered))

        # Sort options
        sort_by = st.selectbox("Sort by", ["Authority Score", "Domain", "Niche", "Discovery Date"])

        if sort_by == "Authority Score":
            filtered = sorted(filtered, key=lambda x: x.authority_score, reverse=True)
        elif sort_by == "Domain":
            filtered = sorted(filtered, key=lambda x: x.domain)
        elif sort_by == "Niche":
            filtered = sorted(filtered, key=lambda x: x.niche)
        else:
            filtered = sorted(filtered, key=lambda x: x.discovery_date, reverse=True)

        # Display as table
        st.subheader(f"📋 Competitors ({len(filtered)})")

        # Convert to DataFrame
        data = []
        for comp in filtered:
            position = comp.metadata.get('discover_position', 'N/A') if comp.metadata else 'N/A'
            sample_title = comp.metadata.get('sample_title', '') if comp.metadata else ''

            data.append({
                'Domain': comp.domain,
                'Niche': comp.niche,
                'Authority': f"{comp.authority_score:.0f}",
                'Position': position,
                'Source': comp.discovery_source,
                'RSS Feeds': len(comp.rss_feeds),
                'Sample Title': sample_title[:50] + '...' if len(sample_title) > 50 else sample_title
            })

        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, height=500)

        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"competitors_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

        # Top performers
        st.subheader("🏆 Top 10 Performers")

        top_10 = sorted(competitors, key=lambda x: x.authority_score, reverse=True)[:10]

        col1, col2 = st.columns([1, 2])

        with col1:
            for i, comp in enumerate(top_10, 1):
                st.metric(
                    label=f"{i}. {comp.domain}",
                    value=f"{comp.authority_score:.0f}",
                    delta=comp.niche
                )

        with col2:
            df_top = pd.DataFrame([
                {'Domain': c.domain, 'Authority Score': c.authority_score, 'Niche': c.niche}
                for c in top_10
            ])

            fig = px.bar(
                df_top,
                x='Authority Score',
                y='Domain',
                color='Niche',
                orientation='h',
                title='Top 10 Competitors by Authority Score'
            )
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)

# ==================== INTELLIGENCE ANALYSIS PAGE ====================
elif page == "📈 Intelligence Analysis":
    st.header("Intelligence Analysis")

    intel = load_intelligence()
    articles_df = load_articles()

    if not intel.get("niche_scores"):
        st.warning("⚠ No intelligence data yet")
        st.info("""
        **Generate intelligence:**
        1. Complete competitor discovery
        2. Run monitoring: `python scripts/run_monitor.py --cycles 5`
        3. Generate report: `python scripts/generate_report.py`
        """)
    else:
        # Niche scores
        st.subheader("🔥 Niche Performance")

        niche_scores = intel.get("niche_scores", {})

        if niche_scores:
            # Create DataFrame
            df_niches = pd.DataFrame([
                {
                    'Niche': niche,
                    'Score': data.get('score', 0),
                    'Articles': data.get('article_count', 0),
                    'Velocity': data.get('velocity', 0),
                    'Rating': data.get('rating', 'UNKNOWN')
                }
                for niche, data in niche_scores.items()
            ]).sort_values('Score', ascending=False)

            # Display metrics
            col1, col2, col3 = st.columns(3)

            if not df_niches.empty:
                winner = df_niches.iloc[0]

                with col1:
                    st.metric(
                        label="🏆 Winning Niche",
                        value=winner['Niche'].upper(),
                        delta=f"Score: {winner['Score']}/100"
                    )

                with col2:
                    st.metric(
                        label="📰 Total Articles",
                        value=int(df_niches['Articles'].sum()),
                        delta=f"{winner['Articles']} in winning niche"
                    )

                with col3:
                    st.metric(
                        label="⚡ Avg Velocity",
                        value=f"{df_niches['Velocity'].mean():.1f}/day",
                        delta=f"{winner['Velocity']:.1f}/day for winner"
                    )

            # Charts
            col1, col2 = st.columns(2)

            with col1:
                fig = px.bar(
                    df_niches,
                    x='Niche',
                    y='Score',
                    color='Rating',
                    title='Niche Scores (0-100)',
                    color_discrete_map={
                        'HOT': '#ff4444',
                        'WARM': '#ff9944',
                        'MODERATE': '#ffdd44',
                        'COLD': '#4444ff'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                fig = px.scatter(
                    df_niches,
                    x='Articles',
                    y='Velocity',
                    size='Score',
                    color='Niche',
                    title='Articles vs Velocity (size = score)',
                    hover_data=['Rating']
                )
                st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Structural patterns
        st.subheader("📐 Structural Blueprint")

        patterns = intel.get("patterns", {})

        if patterns:
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                wc = patterns.get("word_count", {})
                st.metric(
                    "📝 Word Count",
                    f"{wc.get('optimal', 'N/A')}",
                    delta=f"Avg: {wc.get('average', 0):.0f}"
                )

            with col2:
                img = patterns.get("images", {})
                st.metric(
                    "🖼 Images",
                    f"{img.get('optimal', 'N/A')}",
                    delta=f"Avg: {img.get('average', 0):.1f}"
                )

            with col3:
                schema = patterns.get("schema_usage", {})
                article_pct = schema.get("article", 0) * 100
                st.metric(
                    "📋 Schema Usage",
                    f"{article_pct:.0f}%",
                    delta="Article schema"
                )

            with col4:
                st.metric(
                    "🏗 Structure",
                    "H1→H2→H3",
                    delta="Standard hierarchy"
                )

        st.markdown("---")

        # Title formulas
        st.subheader("💡 Title Formulas")

        title_formulas = intel.get("title_formulas", [])

        if title_formulas:
            for i, formula in enumerate(title_formulas[:5], 1):
                with st.expander(f"Formula {i}: {formula.get('formula', 'N/A')}"):
                    st.write(f"**Success Rate:** {formula.get('success_rate', 0)*100:.0f}%")
                    st.write(f"**Frequency:** {formula.get('frequency', 0)} occurrences")

                    examples = formula.get('examples', [])
                    if examples:
                        st.write("**Examples:**")
                        for ex in examples[:3]:
                            st.write(f"- {ex}")

        st.markdown("---")

        # Timing insights
        st.subheader("⏰ Timing Strategy")

        timing = intel.get("timing_insights", {})

        if timing:
            col1, col2 = st.columns(2)

            with col1:
                best_hours = timing.get("best_hours", [])
                if best_hours:
                    st.write("**Best Publishing Times:**")
                    for hour in best_hours:
                        st.write(f"- {hour:02d}:00 (Peak engagement)")

                best_days = timing.get("best_days", [])
                if best_days:
                    st.write("**Best Days:**")
                    for day in best_days:
                        st.write(f"- {day}")

            with col2:
                worst_days = timing.get("worst_days", [])
                if worst_days:
                    st.write("**Avoid Publishing On:**")
                    for day in worst_days:
                        st.write(f"- {day} (Low engagement)")

                avg_time = timing.get("average_publish_time", "N/A")
                st.write(f"**Average Publish Time:** {avg_time}")

# ==================== SETTINGS PAGE ====================
elif page == "⚙️ Settings":
    st.header("Settings & Configuration")

    st.subheader("🔧 System Configuration")

    # API settings
    with st.expander("API Server Settings"):
        api_host = st.text_input("API Host", "localhost")
        api_port = st.number_input("API Port", 1000, 65535, 8000)

        if st.button("Test Connection"):
            try:
                response = requests.get(f"http://{api_host}:{api_port}/api/discover/stats", timeout=2)
                if response.status_code == 200:
                    st.success("✓ Connected successfully!")
                    st.json(response.json())
                else:
                    st.error(f"✗ Error: Status {response.status_code}")
            except Exception as e:
                st.error(f"✗ Connection failed: {e}")

    # Database settings
    with st.expander("Database Settings"):
        st.info("Database location: data/")

        if st.button("Check Database Files"):
            data_path = Path("data")
            if data_path.exists():
                files = list(data_path.rglob("*.*"))
                st.write(f"Found {len(files)} files:")
                for file in files[:20]:
                    size = file.stat().st_size
                    st.write(f"- {file.relative_to(data_path)} ({size:,} bytes)")
            else:
                st.warning("Data directory not found")

    # Extension settings
    with st.expander("Chrome Extension"):
        st.markdown("""
        **Installation:**
        1. Open Chrome
        2. Go to `chrome://extensions/`
        3. Enable "Developer mode"
        4. Click "Load unpacked"
        5. Select `chrome_extension/` folder

        **Extension Location:** `chrome_extension/`
        """)

        if st.button("View Extension Files"):
            ext_path = Path("chrome_extension")
            if ext_path.exists():
                files = list(ext_path.glob("*"))
                st.write(f"Extension files ({len(files)}):")
                for file in files:
                    st.write(f"- {file.name}")
            else:
                st.error("Extension directory not found")

    # Data management
    st.subheader("📁 Data Management")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔄 Reload All Data"):
            st.cache_data.clear()
            st.success("Data reloaded!")
            st.rerun()

    with col2:
        if st.button("📊 Export Reports"):
            st.info("Export functionality coming soon")

    with col3:
        if st.button("🗑 Clear Cache"):
            st.cache_data.clear()
            st.success("Cache cleared!")

# Footer
st.markdown("---")
st.caption("Project Hunter Dashboard | Real-time competitor intelligence for Google Discover")
