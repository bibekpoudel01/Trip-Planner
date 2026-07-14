import html
import streamlit as st

# ---------------------------------------------------------------------------
# Adjust this import to match where TravelPlanner actually lives
# ---------------------------------------------------------------------------
from src.core.planner import TravelPlanner  # noqa: E402
import logfire

logfire.configure(service_name="wanderly")
logfire.instrument_pydantic()  # auto-validates TravelPlan, etc.
logfire.instrument_psycopg()   # if you want DB spans from the checkpointer pool
st.set_page_config(
    page_title="Wanderly · AI Trip Planner",
    page_icon="🧭",
    layout="wide",
)

# ---------------------------------------------------------------------------
# STYLE
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .stApp { background: linear-gradient(180deg, #0f1720 0%, #14202b 100%); }

    section[data-testid="stSidebar"] {
        background: #0b1119;
        border-right: 1px solid rgba(255,255,255,0.06);
    }

    h1, h2, h3 { color: #eef4f8 !important; letter-spacing: -0.01em; }
    p, li, span, label, div { color: #d7e1ea; }

    .hero {
        padding: 1.4rem 1.6rem;
        border-radius: 16px;
        background: radial-gradient(120% 160% at 0% 0%, rgba(56,189,248,0.18) 0%, rgba(20,32,43,0) 60%),
                    linear-gradient(135deg, rgba(30,58,74,0.9), rgba(15,23,32,0.9));
        border: 1px solid rgba(148,197,220,0.18);
        margin-bottom: 1.2rem;
        animation: fadeIn 0.5s ease-out;
    }
    .hero h1 { margin: 0; font-size: 1.9rem; }
    .hero p { margin: 0.3rem 0 0 0; color: #9db3c2; }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-6px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes popIn {
        from { opacity: 0; transform: scale(0.97); }
        to { opacity: 1; transform: scale(1); }
    }

    .card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 1.1rem 1.3rem;
        margin-bottom: 0.9rem;
        animation: popIn 0.3s ease-out;
    }
    .day-badge {
        display: inline-block;
        background: linear-gradient(135deg, #38bdf8, #6366f1);
        color: white;
        font-weight: 700;
        font-size: 0.78rem;
        padding: 0.18rem 0.65rem;
        border-radius: 999px;
        margin-bottom: 0.5rem;
    }
    .theme-title { font-size: 1.15rem; font-weight: 700; color: #f2f7fb; margin: 0.1rem 0 0.6rem 0; }
    .activity-row {
        display: flex; gap: 0.6rem; padding: 0.35rem 0;
        border-bottom: 1px dashed rgba(255,255,255,0.06);
    }
    .activity-time {
        min-width: 84px; font-weight: 600; color: #7dd3fc; font-size: 0.85rem;
    }
    .activity-loc { color: #9db3c2; font-size: 0.82rem; }

    .pill {
        display: inline-block; padding: 0.15rem 0.6rem; border-radius: 999px;
        background: rgba(99,102,241,0.15); border: 1px solid rgba(99,102,241,0.35);
        font-size: 0.75rem; color: #c7d2fe; margin: 0.15rem 0.25rem 0.15rem 0;
    }
    .tool-chip {
        display: inline-block; padding: 0.15rem 0.55rem; border-radius: 8px;
        background: rgba(56,189,248,0.10); border: 1px solid rgba(56,189,248,0.3);
        font-size: 0.72rem; color: #7dd3fc; margin: 0.15rem 0.25rem 0.15rem 0;
        font-family: monospace;
    }
    .side-panel {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 1rem 1.15rem;
        margin-bottom: 0.9rem;
    }
    .side-panel h4 {
        margin: 0 0 0.5rem 0;
        font-size: 0.95rem;
        color: #7dd3fc;
    }

    /* Currency */
    .currency-ticker {
        background: rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.25);
        color: #6ee7b7;
        padding: 0.6rem 0.8rem;
        border-radius: 8px;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-top: 0.4rem;
        font-family: monospace;
        font-size: 0.9rem;
    }

    .rec-card {
        background: rgba(99,102,241,0.08);
        border: 1px solid rgba(99,102,241,0.25);
        border-left: 3px solid #6366f1;
        border-radius: 10px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.6rem;
    }
    .warning-card {
        background: rgba(248,113,113,0.08);
        border: 1px solid rgba(248,113,113,0.25);
        border-left: 3px solid #f87171;
        border-radius: 10px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.6rem;
    }
    .hotel-row {
        display: flex; justify-content: space-between; align-items: center;
        padding: 0.45rem 0; border-bottom: 1px dashed rgba(255,255,255,0.06);
        font-size: 0.88rem;
    }
    .hotel-price { color: #7dd3fc; font-weight: 700; }

    .stButton>button {
        background: linear-gradient(135deg, #38bdf8, #6366f1);
        color: white; border: none; border-radius: 10px; font-weight: 600;
        padding: 0.55rem 1.1rem;
        transition: filter 0.15s ease, transform 0.1s ease;
    }
    .stButton>button:hover { filter: brightness(1.08); transform: translateY(-1px); }

    .day-chip-row { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-bottom: 1rem; }

    .stat-strip {
        display: flex; gap: 0.8rem; flex-wrap: wrap; margin-bottom: 1rem;
    }
    .stat-box {
        flex: 1; min-width: 140px;
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 0.8rem 1rem;
        text-align: center;
    }
    .stat-box .num { font-size: 1.3rem; font-weight: 800; color: #7dd3fc; }
    .stat-box .lbl { font-size: 0.72rem; color: #9db3c2; text-transform: uppercase; letter-spacing: 0.04em; }

    @media print {
        section[data-testid="stSidebar"] { display: none !important; }
        .stButton, .stDownloadButton { display: none !important; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def esc(text) -> str:
    if text is None:
        return ""
    return html.escape(str(text))


# ---------------------------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------------------------
for key, default in [("plan", None), ("tool_calls", []), ("thread_id", None), ("title", None)]:
    if key not in st.session_state:
        st.session_state[key] = default

# ---------------------------------------------------------------------------
# HERO
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="hero">
      <h1>🧭 {esc(st.session_state.get("title") or "Wanderly")}</h1>
      <p>Your AI-powered day-by-day trip planner</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# SIDEBAR — TRIP INPUT FORM
# ---------------------------------------------------------------------------
MONTHS = [
    "Any", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

ALL_INTERESTS = [
    "Anything / Surprise Me", "Culture & History", "Food & Culinary",
    "Nature", "Adventure", "Nightlife", "Shopping", "Relaxation & Spa",
    "Art & Museums", "Photography", "Architecture", "Hidden Gems", "Theme Parks"
]

with st.sidebar:
    st.markdown("### ✈️ Plan your trip")
    city = st.text_input("Destination city", placeholder="e.g. Kyoto, Japan")
    days = st.number_input("Number of days", min_value=1, max_value=30, value=4, step=1)

    # Calculate max allowed interests based on days
    if days <= 3:
        max_interests = 2
    elif days <= 7:
        max_interests = 3
    elif days <= 14:
        max_interests = 5
    else:
        max_interests = None  # None means no limit for Streamlit

    interest_label = f"Interests (Pick up to {max_interests})" if max_interests else "Interests"

    interests = st.multiselect(
        interest_label,
        ALL_INTERESTS,
        default=["Culture & History", "Food & Culinary"],
        max_selections=max_interests
    )

    style = st.selectbox("Travel style", ["Budget", "Mid-range", "Luxury"])
    pace = st.selectbox("Pace", ["Relaxed", "Moderate", "Packed"])
    month = st.selectbox("Month of travel", MONTHS)
    currency = st.selectbox(
        "Currency reference (for conversion only)",
        ["USD", "EUR", "GBP", "INR", "NPR", "JPY", "AUD"],
        help="Shows a quick '1000 USD ≈ ...' conversion.",
    )
    extra_info = st.text_area(
        "Anything else we should know?",
        placeholder="Dietary needs, mobility limits, budget cap, must-see spots...",
    )
    submitted = st.button("✨ Generate itinerary", use_container_width=True)

# ---------------------------------------------------------------------------
# GENERATE
# ---------------------------------------------------------------------------
if submitted:
    if not city.strip():
        st.sidebar.error("Please enter a destination city.")
    else:
        with st.spinner(f"Researching your trip to {city}..."):
            try:
                planner = TravelPlanner()
                # Default to "Anything" if they clear the box
                final_interests = interests if interests else ["Anything / Surprise Me"]

                # app.py, inside the `submitted` block
                result = planner.create_itinerary(
                    city=city,
                    days=int(days),
                    interests=final_interests,
                    style=style,
                    pace=pace,
                    month=None if month == "Any" else month,
                    extra_info=extra_info or None,
                    thread_id=None,   # <-- always fresh, don't reuse st.session_state.thread_id
                    currency=currency,
                )
                st.session_state.plan = result["itinerary"]
                st.session_state.title = result.get("title")
                st.session_state.tool_calls = result.get("tool_calls", [])
                st.session_state.thread_id = result.get("thread_id")
                st.toast("Itinerary ready!", icon="✅")
                st.rerun()
            except Exception as e:
                st.error(f"Something went wrong while planning your trip: {e}")

plan = st.session_state.plan

# ---------------------------------------------------------------------------
# EMPTY STATE
# ---------------------------------------------------------------------------
if plan is None:
    st.info("Fill in your trip details on the left and hit **Generate itinerary** to get started.")
    st.stop()

# ---------------------------------------------------------------------------
# STAT STRIP
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="stat-strip">
      <div class="stat-box"><div class="num">{esc(plan.total_days)}</div><div class="lbl">Days</div></div>
      <div class="stat-box"><div class="num">{esc(plan.city)}</div><div class="lbl">Destination</div></div>
      <div class="stat-box"><div class="num">{esc(plan.estimated_budget_category)}</div><div class="lbl">Budget</div></div>
    </div>
    """,
    unsafe_allow_html=True,
)

main_col, side_col = st.columns([2.2, 1])

# ---------------------------------------------------------------------------
# MAIN COLUMN
# ---------------------------------------------------------------------------
with main_col:
    if plan.weather_summary:
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f"**📅 Weather:** {esc(plan.weather_summary)}")
            st.markdown("</div>", unsafe_allow_html=True)

    chip_html = "".join(f'<span class="pill">Day {esc(d.day_number)}</span>' for d in plan.itinerary)
    st.markdown(f'<div class="day-chip-row">{chip_html}</div>', unsafe_allow_html=True)

    for day in plan.itinerary:
        weather_line = (
            f'<p style="margin:0 0 0.6rem 0; color:#9db3c2; font-size:0.85rem;">🌤 {esc(day.weather)}</p>'
            if day.weather else ""
        )

        activities_html = "".join(
            f"""
            <div class="activity-row">
              <div class="activity-time">{esc(a.time)}</div>
              <div>
                <div>{esc(a.description)}</div>
                <div class="activity-loc">📍 {esc(a.location)}</div>
              </div>
            </div>
            """
            for a in day.activities
        )

        # Dining recommendations now come as structured objects
        # (restaurant_name, meal, famous_dishes) instead of plain strings.
        dining_html = "".join(
            f"""
            <div class="activity-row">
              <div class="activity-time">{esc(d.meal)}</div>
              <div>
                <div>🍽 {esc(d.restaurant_name)}</div>
                <div class="activity-loc">{esc(', '.join(d.famous_dishes))}</div>
              </div>
            </div>
            """
            for d in day.dining_recommendations
        )

        transport_html = "".join(f'<span class="pill">🚕 {esc(t)}</span>' for t in day.transportation)

        extras_html = ""
        if dining_html:
            extras_html += f'<div style="margin-top:0.7rem;">{dining_html}</div>'
        if transport_html:
            extras_html += f'<div style="margin-top:0.35rem;">{transport_html}</div>'

        st.markdown(
            f"""
            <div class="card">
              <span class="day-badge">Day {esc(day.day_number)}</span>
              <div class="theme-title">{esc(day.theme)}</div>
              {weather_line}
              {activities_html}
              {extras_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------------
# SIDE COLUMN
# ---------------------------------------------------------------------------
with side_col:
    if plan.hotel_options:
        hotel_row_parts = []
        for h in plan.hotel_options:
            price_str = f"USD {h.price_per_night:,.0f}/night" if h.price_per_night else "—"
            rating_str = f' <span style="color:#facc15;">★ {h.rating:.1f}</span>' if h.rating else ""
            hotel_row_parts.append(
                f'<div class="hotel-row"><span>🏨 {esc(h.name)}{rating_str}</span>'
                f'<span class="hotel-price">{price_str}</span></div>'
            )
        hotel_rows = "".join(hotel_row_parts)
        st.markdown(
            f'<div class="side-panel"><h4>Hotel options</h4>{hotel_rows}</div>',
            unsafe_allow_html=True,
        )

    if plan.transportation_options:
        transport_pills = "".join(f'<span class="pill">{esc(t)}</span>' for t in plan.transportation_options)
        st.markdown(
            f'<div class="side-panel"><h4>Getting around</h4>{transport_pills}</div>',
            unsafe_allow_html=True,
        )

    if plan.currency_note:
        st.markdown(
            f"""
            <div class="side-panel">
              <h4>Currency reference</h4>
              <div class="currency-ticker">
                <span>💱</span> {esc(plan.currency_note)}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if plan.travel_warnings:
        warning_cards = "".join(
            f'<div class="warning-card">⚠️ {esc(w)}</div>' for w in plan.travel_warnings
        )
        st.markdown(
            f'<div class="side-panel"><h4>Travel warnings</h4>{warning_cards}</div>',
            unsafe_allow_html=True,
        )

    if plan.final_recommendations:
        rec_cards = "".join(
            f'<div class="rec-card">{esc(r)}</div>' for r in plan.final_recommendations
        )
        st.markdown(
            f'<div class="side-panel"><h4>Final recommendations</h4>{rec_cards}</div>',
            unsafe_allow_html=True,
        )

    if st.session_state.tool_calls:
        with st.expander("🔧 Research tools used"):
            chips = "".join(
                f'<span class="tool-chip">{esc(tc["name"])}</span>' for tc in st.session_state.tool_calls
            )
            st.markdown(chips, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# DOWNLOAD
# ---------------------------------------------------------------------------
st.divider()
lines = [f"# {st.session_state.title or plan.city} — {plan.total_days}-day itinerary", ""]
if plan.weather_summary:
    lines.append(f"**Weather:** {plan.weather_summary}")
lines.append("")
for day in plan.itinerary:
    lines.append(f"## Day {day.day_number} — {day.theme}")
    if day.weather:
        lines.append(f"Weather: {day.weather}")
    for a in day.activities:
        lines.append(f"- **{a.time}**: {a.description} ({a.location})")
    if day.dining_recommendations:
        dining_lines = "; ".join(
            f"{d.meal}: {d.restaurant_name} ({', '.join(d.famous_dishes)})"
            for d in day.dining_recommendations
        )
        lines.append(f"Food: {dining_lines}")
    if day.transportation:
        lines.append(f"Transport: {', '.join(day.transportation)}")
    lines.append("")
if plan.hotel_options:
    lines.append("## Hotel options")
    for h in plan.hotel_options:
        price = f"USD {h.price_per_night:,.0f}/night" if h.price_per_night else "—"
        rating = f" (★ {h.rating:.1f})" if h.rating else ""
        lines.append(f"- {h.name}{rating}: {price}")
    lines.append("")
if plan.currency_note:
    lines.append(f"## Currency reference\n{plan.currency_note}\n")
if plan.travel_warnings:
    lines.append("## Travel warnings")
    for w in plan.travel_warnings:
        lines.append(f"- ⚠️ {w}")
    lines.append("")
if plan.final_recommendations:
    lines.append("## Final recommendations")
    for r in plan.final_recommendations:
        lines.append(f"- {r}")

st.download_button(
    "⬇️ Download itinerary (Markdown)",
    data="\n".join(lines),
    file_name=f"{plan.city.replace(' ', '_').lower()}_itinerary.md",
    mime="text/markdown",
    use_container_width=True,
)