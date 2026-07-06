import streamlit as st
import requests
import os
from dotenv import load_dotenv
from datetime import date

load_dotenv()

st.set_page_config(
    page_title="DE-INTEL | Decision Intelligence Platform",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Core layout styling adjustments
st.markdown("""
<style>
    .metric-card {
        background-color: #1e293b;
        border-radius: 8px;
        padding: 14px;
        border: 1px solid #334155;
        margin-bottom: 12px;
    }
    .recom-card {
        border-left: 4px solid #3b82f6;
        background-color: #1e293b;
        border-radius: 6px;
        padding: 16px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")

# Connection Health Check
try:
    # Increased timeout to 15s to handle potential Cloud Run cold starts
    health_resp = requests.get(f"{BACKEND_URL}/health", timeout=15)
    backend_online = health_resp.status_code == 200
    error_msg = f"Status Code: {health_resp.status_code}" if not backend_online else ""
except Exception as e:
    error_msg = str(e)
    backend_online = False

if not backend_online:
    st.error(f"⚠️ Unable to connect to the Backend API at {BACKEND_URL}")
    st.caption(f"Error details: {error_msg}")
    st.info("💡 Tip: Check if 'Allow unauthenticated' is enabled on your Cloud Run backend service.")
    st.stop()

# Sidebar Configuration
st.sidebar.image("https://img.icons8.com/nolan/128/artificial-intelligence.png", width=70)
st.sidebar.title("DE-INTEL Control Panel")
categories = ["World", "Business", "Technology", "Politics", "Health", "Science", "Sports", "Entertainment"]
selected_category = st.sidebar.selectbox("Active Sphere Horizon", categories)

# Get current date and format it (e.g., "July 05, 2026")
today_formatted = date.today().strftime("%B %d, %Y")
st.title("🎯 DE-INTEL")
st.subheader("Decision Intelligence & Systemic Predictive Risk Engine")
st.markdown(f"**Core Date Target:** Today, {today_formatted} | **Primary Sourcing:** Google Search Grounded Gemini Node")
# Load category headlines
with st.spinner(f"Surface scanning '{selected_category}' active news registries..."):
    try:
        resp = requests.get(f"{BACKEND_URL}/news/headlines?category={selected_category}")
        if resp.status_code == 200:
            headlines = resp.json()
        else:
            headlines = []
            st.warning("Empty ground matrix response for category.")
    except Exception as e:
        headlines = []
        st.error(f"Failed connection mapping on headline parsing: {e}")

if headlines:
    st.write("---")
    st.markdown("### 📰 Today's Surface Scanning")
    for art in headlines:
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            st.markdown(f"**{art['title']}**")
            st.markdown(f"*Source: {art['source']} | Published: {art['published_at']}*")
            st.write(art['short_summary'])
        with col2:
            st.write("")
            if st.button("Deep Scan Headline", key=art['id']):
                st.session_state["selected_article"] = art
                st.session_state["analysis_report"] = None
                st.rerun()
else:
    st.info("No surface registries located for category.")

if "selected_article" in st.session_state:
    selected_art = st.session_state["selected_article"]
    st.write("---")
    st.markdown(f"## 🔎 Deep-Dive Analysis: *{selected_art['title']}*")
    
    # ----------------------------------------------------
    # 1. RUN PIPELINE IF NOT YET ANALYZED
    # ----------------------------------------------------
    if st.session_state.get("analysis_report") is None:
        with st.status("Initializing Decision Intelligence Core...", expanded=True) as status:
            try:
                # Phase 1: Deep scan & connected events
                status.write("Phase 1/5: Extracting entities & same-day connected events...")
                resp = requests.post(f"{BACKEND_URL}/news/analyze", json={"article": selected_art})
                if resp.status_code != 200:
                    raise Exception(f"Deep scan: {resp.text}")
                
                article_id = selected_art["id"]
                
                # Phase 2: Predict Systemic Ripples
                status.write("Phase 2/5: Modeling multi-domain systemic ripple effects...")
                resp = requests.post(f"{BACKEND_URL}/ripple/predict", json={"article_id": article_id})
                if resp.status_code != 200:
                    raise Exception(f"Ripple mapping: {resp.text}")
                
                # Phase 3: Historical Matching
                status.write("Phase 3/5: Querying Bigquery for historical analogues...")
                resp = requests.post(f"{BACKEND_URL}/history/similar", json={"article_id": article_id})
                if resp.status_code != 200:
                    raise Exception(f"Vector search: {resp.text}")
                
                # Phase 4: Explanation Mapping
                status.write("Phase 4/5: Reconstructing historical pattern comparisons...")
                resp = requests.post(f"{BACKEND_URL}/history/explain", json={"article_id": article_id})
                if resp.status_code != 200:
                    raise Exception(f"Historical comparison core: {resp.text}")
                
                # Phase 5: Recommendation Modeling
                status.write("Phase 5/5: Modeling probabilistic actionable recommendations...")
                resp = requests.post(f"{BACKEND_URL}/recommendations/generate", json={"article_id": article_id})
                if resp.status_code != 200:
                    raise Exception(f"Recommendation generation: {resp.text}")
                
                status.update(label="System Analysis Complete!", state="complete", expanded=False)
                
                final_briefing_resp = requests.get(f"{BACKEND_URL}/briefing/visual?article_id={article_id}&domain=All")
                st.session_state["analysis_report"] = final_briefing_resp.json()
                st.session_state["available_domains"] = final_briefing_resp.json().get("available_domains", [])
            except Exception as e:
                status.update(label="Analysis Block Collapsed!", state="error")
                st.error(f"Mapping pipeline breakdown: {e}")
                st.stop()
                
    # ----------------------------------------------------
    # 2. RENDER THE ANALYSIS ONCE DATA IS AVAILABLE
    # ----------------------------------------------------
    if st.session_state.get("analysis_report"):
        report = st.session_state["analysis_report"]
        available_domains = st.session_state.get("available_domains", [])
        article_id = selected_art["id"]
        
        # --- CRITICAL FIX: Fetch report_data immediately so it's defined for all blocks ---
        report_data_resp = requests.get(f"{BACKEND_URL}/news/article/{article_id}")
        if report_data_resp.status_code == 200:
            report_data = report_data_resp.json()
        else:
            st.error("Failed to retrieve the detailed structural report data.")
            st.stop()
            
        # ----------------------------------------------------
        # 2a. EXECUTIVE KPI BAR (Using newly defined report_data safely)
        # ----------------------------------------------------
        max_impact = max([r["impact_score"] for r in report_data["ripple_effects"]]) if report_data.get("ripple_effects") else 0
        risk_color = "#ef4444" if max_impact >= 4 else ("#f59e0b" if max_impact >= 3 else "#22c55e")
        top_domain = report_data["ripple_effects"][0]["domain"] if report_data.get("ripple_effects") else "N/A"
        align_score = int(report_data['historical_matches'][0]['similarity_score'] * 100) if report_data.get('historical_matches') else 0
        top_rec_prob = report_data['recommendations'][0]['probability'] if report_data.get('recommendations') else 'N/A'

        st.markdown(f"""
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px;">
            <div style="background: rgba(30, 41, 59, 0.4); border-left: 4px solid {risk_color}; padding: 16px; border-radius: 12px; border-top: 1px solid #334155; border-right: 1px solid #334155; border-bottom: 1px solid #334155; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                <span style="font-size: 11px; text-transform: uppercase; color: #94a3b8; letter-spacing: 0.05em; font-weight: 700;">Systemic Risk Index</span>
                <div style="font-size: 24px; font-weight: 800; color: {risk_color}; margin-top: 4px;">{max_impact * 20}% Threat</div>
            </div>
            <div style="background: rgba(30, 41, 59, 0.4); border-left: 4px solid #3b82f6; padding: 16px; border-radius: 12px; border-top: 1px solid #334155; border-right: 1px solid #334155; border-bottom: 1px solid #334155; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                <span style="font-size: 11px; text-transform: uppercase; color: #94a3b8; letter-spacing: 0.05em; font-weight: 700;">Critical Domain Node</span>
                <div style="font-size: 18px; font-weight: 800; color: #f8fafc; margin-top: 8px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{top_domain}</div>
            </div>
            <div style="background: rgba(30, 41, 59, 0.4); border-left: 4px solid #a855f7; padding: 16px; border-radius: 12px; border-top: 1px solid #334155; border-right: 1px solid #334155; border-bottom: 1px solid #334155; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                <span style="font-size: 11px; text-transform: uppercase; color: #94a3b8; letter-spacing: 0.05em; font-weight: 700;">Historical Confidence</span>
                <div style="font-size: 24px; font-weight: 800; color: #c084fc; margin-top: 4px;">{align_score}% Align</div>
            </div>
            <div style="background: rgba(30, 41, 59, 0.4); border-left: 4px solid #22c55e; padding: 16px; border-radius: 12px; border-top: 1px solid #334155; border-right: 1px solid #334155; border-bottom: 1px solid #334155; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                <span style="font-size: 11px; text-transform: uppercase; color: #94a3b8; letter-spacing: 0.05em; font-weight: 700;">Top Rec Confidence</span>
                <div style="font-size: 24px; font-weight: 800; color: #4ade80; margin-top: 4px;">{top_rec_prob} Match</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ----------------------------------------------------
        # 2b. VISUAL DASHBOARD (HTML iframe component)
        # ----------------------------------------------------
        st.write("")
        st.markdown("### 📊 Interactive Visual At-a-Glance Briefing")
        
        domain_options = ["All Domains"] + available_domains
        selected_domain = st.selectbox("Intelligence Focus Filter (re-renders briefing below instantly)", domain_options)
        
        domain_param = "All" if selected_domain == "All Domains" else selected_domain
        
        briefing_resp = requests.get(f"{BACKEND_URL}/briefing/visual?article_id={article_id}&domain={domain_param}")
        if briefing_resp.status_code == 200:
            html_content = briefing_resp.json().get("html", "")
            st.components.v1.html(html_content, height=600, scrolling=True)
            
        # ----------------------------------------------------
        # 2c. DETAIL SUB-PANELS (Expanders using pre-fetched report_data)
        # ----------------------------------------------------
        st.write("")
        st.markdown("### 🔍 Granular Intelligence Sub-Panels")
        
        with st.expander("🔗 Deep Summary & Connected Events", expanded=True):
            st.markdown("#### Detailed Executive Summary")
            st.write(report_data["detailed_summary"])
            
            st.markdown("#### Key Entities Involved")
            st.write(", ".join(report_data["entities"]))
            
            st.markdown("#### Connected Same-Day Events")
            for item in report_data["connected_events"]:
                st.markdown(f"""
                <div class="metric-card">
                    <strong><a href="{item['url']}" target="_blank">{item['title']}</a></strong> ({item['source']})<br>
                    <span style="color:#94a3b8; font-size:12px;">Connection Rationale:</span> {item['rationale']}
                </div>
                """, unsafe_allow_html=True)
                
        with st.expander("🌊 Predicted Systemic Ripple Effects", expanded=False):
            col_left, col_right = st.columns(2)
            for idx, ripple in enumerate(report_data["ripple_effects"]):
                badge_color = "🔴" if ripple["direction"] == "negative" else "🟢" if ripple["direction"] == "positive" else "🟡"
                panel = col_left if idx % 2 == 0 else col_right
                with panel:
                    panel.markdown(f"""
                    <div class="metric-card">
                        <span style="font-size:16px;">{badge_color}</span> <strong>{ripple['domain']}</strong><br>
                        <span style="font-size:11px; color:#94a3b8;">Horizon: {ripple['time_horizon'].upper()} | Confidence: {ripple['confidence'].upper()}</span><br>
                        <p style="margin: 6px 0 0 0; font-size:13px; color:#cbd5e1;">{ripple['description']}</p>
                        <strong style="font-size:11px; color:#ef4444;">Impact Weight: {ripple['impact_score']}/5</strong>
                    </div>
                    """, unsafe_allow_html=True)
                    
        with st.expander("📚 Similar Historical Match Cases", expanded=False):
            for match in report_data["historical_matches"]:
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.markdown(f"""
                    <div style="background: rgba(30, 41, 59, 0.3); border: 1px solid #1e293b; padding: 16px; border-radius: 8px; min-height: 200px;">
                        <span style="font-size:11px; text-transform:uppercase; color:#3b82f6; font-weight:700;">📜 Past Precedent</span>
                        <h4 style="margin:4px 0 8px 0; color:#f8fafc;">{match['historical_event']['title']} <span style="font-size:12px; color:#64748b;">({match['historical_event']['date']})</span></h4>
                        <p style="margin:0; font-size:13px; color:#cbd5e1; line-height:1.5;">{match['historical_event']['description']}</p>
                        <div style="margin-top:12px; font-size:12px; color: #a855f7;"><strong>Outcome:</strong> {match['historical_event']['outcome']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div style="background: rgba(59, 130, 246, 0.03); border: 1px dashed #3b82f6; padding: 16px; border-radius: 8px; min-height: 200px;">
                        <span style="font-size:11px; text-transform:uppercase; color:#4ade80; font-weight:700;">🔄 Modern Day System Alignment</span>
                        <div style="margin-top: 4px; margin-bottom: 8px;">
                            <span style="background:#1e1b4b; border: 1px solid #4338ca; color:#818cf8; padding:2px 8px; border-radius:12px; font-size:11px; font-weight:700;">
                                Similarity Metric: {int(match['similarity_score'] * 100)}% Match
                            </span>
                        </div>
                        <p style="margin:0; font-size:13px; color:#cbd5e1; line-height:1.5; font-style:italic;">
                            "{match['mapped_ripple_explanation']}"
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                st.write("")
                
        with st.expander("💡 Executive Strategic Recommendations", expanded=False):
            for idx, rec in enumerate(report_data["recommendations"]):
                st.markdown(f"""
                <div style="background: #111827; border: 1px solid #1e293b; border-radius: 12px; padding: 20px; margin-bottom: 20px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                        <div style="font-size: 16px; font-weight: 800; color: #f8fafc;">📍 REC {idx+1}: {rec['text']}</div>
                        <span style="background: rgba(34, 197, 94, 0.1); border: 1px solid #22c55e; color: #4ade80; padding: 4px 12px; border-radius: 30px; font-size: 12px; font-weight: 800;">
                            {rec['probability']} Target
                        </span>
                    </div>
                    <p style="font-size: 12px; color: #64748b; margin-top: -6px; margin-bottom: 16px;">
                        Validated by pattern evidence from: <strong>{rec['supporting_analogue']}</strong>
                    </p>
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;">
                        <div style="background: rgba(34, 197, 94, 0.05); border: 1px solid rgba(34, 197, 94, 0.2); border-radius: 8px; padding: 12px;">
                            <span style="color: #4ade80; font-size: 10px; font-weight: 800; letter-spacing: 0.05em; display: block; margin-bottom: 4px;">🟢 OPTIMAL PATHWAY</span>
                            <span style="font-size: 12.5px; color: #cbd5e1; line-height: 1.4;">{rec['best_case']}</span>
                        </div>
                        <div style="background: rgba(245, 158, 11, 0.05); border: 1px solid rgba(245, 158, 11, 0.2); border-radius: 8px; padding: 12px;">
                            <span style="color: #fbbf24; font-size: 10px; font-weight: 800; letter-spacing: 0.05em; display: block; margin-bottom: 4px;">🟡 STANDARD FORECAST</span>
                            <span style="font-size: 12.5px; color: #cbd5e1; line-height: 1.4;">{rec['base_case']}</span>
                        </div>
                        <div style="background: rgba(239, 68, 68, 0.05); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 8px; padding: 12px;">
                            <span style="color: #f87171; font-size: 10px; font-weight: 800; letter-spacing: 0.05em; display: block; margin-bottom: 4px;">🔴 SYSTEMIC FAILURE RISK</span>
                            <span style="font-size: 12.5px; color: #cbd5e1; line-height: 1.4;">{rec['worst_case']}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        # ----------------------------------------------------
        # 2d. CONVERSATIONAL ANALYST AGENT (Streamlit Chat Interface)
        # ----------------------------------------------------
        st.write("---")
        st.markdown("### 💬 Interrogate the intelligence Report")
        st.caption("Ask our AI Lead Analyst follow-up questions, request specific contingencies, or test scenario models.")

        # Initialize local chat history session variable
        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = []

        # Display historical conversation messages
        for msg in st.session_state["chat_history"]:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        # Chat Input Area
        user_input = st.chat_input("Ask about threat timelines, historical comparisons, or mitigation strategies...")

        if user_input:
            # Render user query instantly
            with st.chat_message("user"):
                st.write(user_input)
            st.session_state["chat_history"].append({"role": "user", "content": user_input})

            with st.spinner("Analyzing operational directives..."):
                try:
                    payload = {
                        "article_id": article_id,
                        "message": user_input,
                        "history": st.session_state["chat_history"][:-1]  # Pass previous conversation window
                    }
                    resp = requests.post(f"{BACKEND_URL}/news/chat", json=payload)
                    
                    if resp.status_code == 200:
                        agent_reply = resp.json().get("response", "")
                        # Render agent answer
                        with st.chat_message("assistant", avatar="🎯"):
                            st.write(agent_reply)
                        st.session_state["chat_history"].append({"role": "assistant", "content": agent_reply})
                    else:
                        st.error(f"Error calling Analyst backend: {resp.text}")
                except Exception as ex:
                    st.error(f"Connection failed to Conversational Agent: {ex}")
