"""HTML snippet builders — clean card-based headers for the off-white theme."""

def page_header_html(title: str, subtitle: str = "", icon: str = "", section: str = "Analytics") -> str:
    return f"""
    <div class="sk-header">
        <div class="sk-header-icon">{icon}</div>
        <div>
            <div class="sk-header-label">{section}</div>
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
    </div>
    """

def kpi_card_html(label: str, value: str, icon: str = "", sub: str = "") -> str:
    sub_html = f'<div class="sk-kpi-sub">{sub}</div>' if sub else ""
    return f"""
    <div class="sk-kpi">
        <div class="sk-kpi-icon">{icon}</div>
        <div class="sk-kpi-label">{label}</div>
        <div class="sk-kpi-value">{value}</div>
        {sub_html}
    </div>
    """

def badge_html(text: str, style: str = "gray") -> str:
    return f'<span class="sk-badge sk-badge-{style}">{text}</span>'

def section_title_html(text: str, icon: str = "") -> str:
    return f'<div class="sk-card-title">{icon} {text}</div>'

def status_html(message: str, kind: str = "sample") -> str:
    icons = {"api": "🟢", "sample": "🟡", "upload": "🟣", "error": "🔴"}
    icon = icons.get(kind, "⚪")
    return f'<div class="sk-status sk-status-{kind}">{icon} {message}</div>'

def footer_html(year: int) -> str:
    return f'<div class="sk-footer">© {year} SkillScope — Job Market Analyzer &nbsp;·&nbsp; Built with Streamlit &amp; Plotly</div>'
