from models import VisualBriefing, DomainBriefing
from typing import Optional

def render_visual_briefing_html(briefing: VisualBriefing, selected_domain: str = "All") -> str:
    css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
        
        body {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: #0b0f17;
            color: #f1f5f9;
            margin: 0;
            padding: 12px;
        }
        .dashboard-container {
            max-width: 100%;
            margin: 0 auto;
        }
        .grid-3 {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 24px;
        }
        .domain-card {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.4) 0%, rgba(15, 23, 42, 0.6) 100%);
            border-radius: 16px;
            border: 1px solid #1e293b;
            padding: 20px;
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.3);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        /* Zoom and glow effects on hover */
        .domain-card:hover {
            transform: translateY(-4px);
            border-color: #3b82f6;
            box-shadow: 0 12px 24px -8px rgba(59, 130, 246, 0.3);
        }
        .domain-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; width: 4px; height: 100%;
        }
        /* Dynamic subtle side glows per direction status */
        .domain-card.direction-positive::before { background: #22c55e; }
        .domain-card.direction-negative::before { background: #ef4444; }
        .domain-card.direction-mixed::before { background: #f59e0b; }
        
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 14px;
        }
        .domain-title {
            font-size: 14px;
            font-weight: 800;
            color: #f8fafc;
            display: flex;
            align-items: center;
            gap: 8px;
            letter-spacing: 0.02em;
        }
        .badge {
            font-size: 9px;
            font-weight: 800;
            padding: 4px 10px;
            border-radius: 30px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .badge-positive { background-color: rgba(34, 197, 94, 0.1); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.2); }
        .badge-negative { background-color: rgba(239, 68, 68, 0.1); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.2); }
        .badge-mixed { background-color: rgba(245, 158, 11, 0.1); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.2); }
        
        .description-text {
            font-size: 12.5px;
            color: #94a3b8;
            line-height: 1.6;
            margin-bottom: 16px;
        }
        .impact-bar-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 11px;
            color: #64748b;
            background: rgba(15, 23, 42, 0.4);
            padding: 8px 12px;
            border-radius: 8px;
            border: 1px solid #1e293b;
        }
        .impact-dots {
            display: flex;
            gap: 4px;
        }
        .dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background-color: #334155;
            transition: all 0.3s ease;
        }
        .dot.active-negative { background-color: #ef4444; box-shadow: 0 0 8px #ef4444; }
        .dot.active-positive { background-color: #22c55e; box-shadow: 0 0 8px #22c55e; }
        .dot.active-mixed { background-color: #f59e0b; box-shadow: 0 0 8px #f59e0b; }
        
        .bottom-sections {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
        }
        @media (max-width: 900px) {
            .bottom-sections { grid-template-columns: 1fr; }
        }
        .callout-card {
            background: linear-gradient(180deg, #111827 0%, #030712 100%);
            border: 1px solid #1e293b;
            border-radius: 16px;
            padding: 24px;
            box-shadow: inset 0 1px 0 0 rgba(255, 255, 255, 0.05);
        }
        .callout-card h3 {
            margin: 0 0 16px 0;
            font-size: 12px;
            color: #3b82f6;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            font-weight: 800;
            border-left: 3px solid #3b82f6;
            padding-left: 10px;
        }
        .callout-title {
            font-size: 16px;
            font-weight: 800;
            color: #f8fafc;
            margin-bottom: 8px;
        }
        .callout-content {
            font-size: 13px;
            color: #cbd5e1;
            line-height: 1.6;
        }
        .gauge-container {
            display: inline-block;
            background: rgba(59, 130, 246, 0.1);
            color: #60a5fa;
            border: 1px solid rgba(59, 130, 246, 0.2);
            font-size: 10px;
            font-weight: 800;
            padding: 4px 10px;
            border-radius: 6px;
            margin-bottom: 12px;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }
    </style>
    """

    icons = {
        "Market/Financial": "💼",
        "Regulatory/Policy": "⚖️",
        "Geopolitical": "🌍",
        "Social/Public Sentiment": "👥",
        "Competitive/Industry": "⚔️",
        "Supply Chain": "🚚",
        "Technology": "💻"
    }

    def get_dots_html(score, direction):
        color_class = f"active-{direction}"
        dots = ""
        for idx in range(1, 6):
            active = f"dot {color_class}" if idx <= score else "dot"
            dots += f'<div class="{active}"></div>'
        return dots

    if selected_domain.lower() == "all":
        cards_html = ""
        for r in briefing.generic_top_ripples:
            icon = icons.get(r.domain, "🎯")
            badge_class = f"badge-{r.direction}"
            dots_html = get_dots_html(r.impact_score, r.direction)
            
            cards_html += f"""
            <div class="domain-card direction-{r.direction}">
                <div class="card-header">
                    <div class="domain-title">{icon} {r.domain}</div>
                    <span class="badge {badge_class}">{r.direction}</span>
                </div>
                <div class="description-text">{r.description}</div>
                <div class="impact-bar-container">
                    <span>Impact Severity:</span>
                    <div class="impact-dots">{dots_html}</div>
                    <span style="font-weight: 700; margin-left: 4px;">{r.impact_score}/5</span>
                </div>
            </div>
            """

        top_hist_html = "No analogue analyzed."
        if briefing.top_historical_analogue:
            h = briefing.top_historical_analogue
            top_hist_html = f"""
            <div class="callout-title">{h.historical_event.title} <span style="color: #60a5fa; font-size: 12px;">({h.historical_event.date})</span></div>
            <div class="gauge-container">Similarity Vector: {int(h.similarity_score * 100)}%</div>
            <div class="callout-content">
                <strong>Historical Impact:</strong> {h.historical_event.description}<br>
                <strong style="display:block; margin-top: 6px; color: #60a5fa;">Grounded Structural Match:</strong> {h.mapped_ripple_explanation}
            </div>
            """

        top_rec_html = "No recommendations generated."
        if briefing.top_recommendation:
            rec = briefing.top_recommendation
            top_rec_html = f"""
            <div class="callout-title">{rec.text}</div>
            <div class="gauge-container">Confidence Target: {rec.probability}</div>
            <div class="callout-content">
                <strong>Rationale:</strong> Validated by historical lessons from {rec.supporting_analogue}.
                <div style="margin-top: 6px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; text-align: center; font-size: 10px;">
                    <div style="background: rgba(34, 197, 94, 0.1); border: 1px solid rgba(34, 197, 94, 0.3); padding: 4px; border-radius: 4px;">
                        <span style="color: #4ade80; font-weight: 700; display:block;">BEST CASE</span>{rec.best_case}
                    </div>
                    <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); padding: 4px; border-radius: 4px;">
                        <span style="color: #fbbf24; font-weight: 700; display:block;">BASE CASE</span>{rec.base_case}
                    </div>
                    <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); padding: 4px; border-radius: 4px;">
                        <span style="color: #f87171; font-weight: 700; display:block;">WORST CASE</span>{rec.worst_case}
                    </div>
                </div>
            </div>
            """

        return f"""
        <!DOCTYPE html>
        <html>
        <head>{css}</head>
        <body>
            <div class="dashboard-container">
                <div class="grid-3">{cards_html}</div>
                <div class="bottom-sections">
                    <div class="callout-card">
                        <h3>Primary Historical Precedent</h3>
                        {top_hist_html}
                    </div>
                    <div class="callout-card">
                        <h3>Critical Strategic Path</h3>
                        {top_rec_html}
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

    else:
        domain_briefing = next((db for db in briefing.domains if db.domain.lower() == selected_domain.lower()), None)
        if not domain_briefing:
            return f"<h3 style='color:#ef4444;text-align:center;'>No structural forecasts computed for sphere: {selected_domain}</h3>"

        icon = icons.get(domain_briefing.domain, "🎯")
        ripples_html = ""
        for r in domain_briefing.ripple_effects:
            badge_class = f"badge-{r.direction}"
            dots_html = get_dots_html(r.impact_score, r.direction)
            ripples_html += f"""
            <div class="domain-card" style="margin-bottom: 12px;">
                <div class="card-header">
                    <div style="font-weight: 700; font-size: 13px; color: #94a3b8;">Horizon: {r.time_horizon.upper()} | Confidence: {r.confidence.upper()}</div>
                    <span class="badge {badge_class}">{r.direction}</span>
                </div>
                <div class="description-text">{r.description}</div>
                <div class="impact-bar-container">
                    <span>Severity Weight:</span>
                    <div class="impact-dots">{dots_html}</div>
                </div>
            </div>
            """

        hist_html = "No mapped historical match."
        if domain_briefing.top_historical_match:
            h = domain_briefing.top_historical_match
            hist_html = f"""
            <div class="callout-title">{h.historical_event.title} <span style="color: #3b82f6; font-size: 12px;">({h.historical_event.date})</span></div>
            <div class="gauge-container">Cosine Alignment: {int(h.similarity_score * 100)}%</div>
            <div class="callout-content">
                <strong>Event Synopsis:</strong> {h.historical_event.description}<br><br>
                <strong style="color: #60a5fa;">Structural Vector Mapping:</strong><br>{h.mapped_ripple_explanation}
            </div>
            """

        rec_html = "No target recommendation."
        if domain_briefing.top_recommendation:
            rec = domain_briefing.top_recommendation
            rec_html = f"""
            <div class="callout-title">{rec.text}</div>
            <div class="gauge-container">Success Likelihood: {rec.probability}</div>
            <div class="callout-content">
                <strong>Strategic Safeguard:</strong> Supported by outcomes of {rec.supporting_analogue}.<br><br>
                <div style="background: rgba(34, 197, 94, 0.1); border: 1px solid rgba(34, 197, 94, 0.3); padding: 6px; border-radius: 4px; margin-bottom: 6px;">
                    <span style="color: #4ade80; font-weight: 700; font-size: 10px;">OPTIMAL PATHWAY</span>{rec.best_case}
                </div>
                <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); padding: 6px; border-radius: 4px; margin-bottom: 6px;">
                    <span style="color: #fbbf24; font-weight: 700; font-size: 10px;">STANDARD FORECAST</span>{rec.base_case}
                </div>
                <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); padding: 6px; border-radius: 4px;">
                    <span style="color: #f87171; font-weight: 700; font-size: 10px;">SYSTEMIC LIMITS</span>{rec.worst_case}
                </div>
            </div>
            """

        return f"""
        <!DOCTYPE html>
        <html>
        <head>{css}</head>
        <body>
            <div class="dashboard-container">
                <div class="bottom-sections">
                    <div>{ripples_html}</div>
                    <div style="display: flex; flex-direction: column; gap: 16px;">
                        <div class="callout-card">
                            <h3>Domain Historical Precedent</h3>
                            {hist_html}
                        </div>
                        <div class="callout-card">
                            <h3>Target Operational Mitigation</h3>
                            {rec_html}
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """