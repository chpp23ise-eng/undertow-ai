from pathlib import Path
import inspect

import pandas as pd
import streamlit as st
import altair as alt


# =========================================================
# BACKEND IMPORTS
# =========================================================

from decision_engine import load_model, make_decision
from portfolio_optimizer import (
    optimize_portfolio,
    calculate_portfolio_metrics,
)
from agent_loop import run_agent
from recovery_service import load_outcomes


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Undertow | Revenue Recovery",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"

EVENTS_PATH = DATA_DIR / "experiment_test_events.csv"
DECISIONS_PATH = DATA_DIR / "experiment_decisions.csv"
OUTCOMES_PATH = DATA_DIR / "experiment_test_outcomes.csv"


# =========================================================
# THEME
# =========================================================

st.markdown(
    """
<style>
:root {
    --ut-bg:#F6F8FB;
    --ut-surface:#FFFFFF;
    --ut-border:#D9E1EC;
    --ut-text:#172033;
    --ut-muted:#5B6B82;
    --ut-primary:#2563EB;
    --ut-primary-hover:#1D4ED8;
    --ut-primary-soft:#EFF6FF;
    --ut-success:#16A34A;
    --ut-warning:#D97706;
    --ut-danger:#DC2626;
    --ut-purple:#7C3AED;
}

/* ---------- Global ---------- */
.stApp {
    background:var(--ut-bg) !important;
    color:var(--ut-text) !important;
}
.block-container {
    width: 100% !important;
    max-width: 1500px !important;
    padding: 1.25rem clamp(.75rem, 2vw, 2rem) 4rem !important;
    box-sizing: border-box !important;
    overflow-x: hidden !important;
}

[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main,
section.main {
    overflow-x: hidden !important;
}
html, body, [class*="css"] {
    font-family:Inter,ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
}
h1,h2,h3,h4,h5 {
    color:var(--ut-text) !important;
    letter-spacing:-.025em;
    max-width:100% !important;
    overflow-wrap:anywhere !important;
}
p, label, .stCaption {
    color:var(--ut-muted);
}


/* ---------- Responsive layout ---------- */
.topbar > div {
    min-width: 0 !important;
}
[data-testid="column"] {
    min-width: 0 !important;
}
.event-header,
.hero-title,
.hero-description,
.section-title,
.section-description {
    overflow-wrap: anywhere !important;
    word-break: normal !important;
}

/* ---------- Top navigation ---------- */
.topbar {
    border-bottom:1px solid var(--ut-border);
    padding-bottom:.8rem;
    margin-bottom:1.15rem;
}
.brand {
    font-size:1.65rem;
    font-weight:800;
    letter-spacing:-.04em;
    color:var(--ut-text);
}
.brand-sub {
    color:var(--ut-muted);
    font-size:.78rem;
    margin-top:.1rem;
}

/* ---------- Buttons: target Streamlit 1.62 DOM ---------- */
div[data-testid="stButton"] > button,
button[data-testid^="stBaseButton"] {
    width: 100% !important;
    max-width: 100% !important;
    border-radius:10px !important;
    min-height:42px !important;
    font-weight:650 !important;
    transition:all .15s ease !important;
}
div[data-testid="stButton"] > button:not([data-testid="stBaseButton-primary"]) {
    background:#FFFFFF !important;
    border:1px solid #CBD5E1 !important;
    color:#172033 !important;
}
div[data-testid="stButton"] > button:not([data-testid="stBaseButton-primary"]):hover {
    background:#EFF6FF !important;
    border-color:#2563EB !important;
    color:#1D4ED8 !important;
}
button[data-testid="stBaseButton-primary"],
div[data-testid="stButton"] > button[kind="primary"] {
    background:#2563EB !important;
    border:1px solid #2563EB !important;
    color:#FFFFFF !important;
    box-shadow:0 2px 5px rgba(37,99,235,.18) !important;
}
button[data-testid="stBaseButton-primary"] *,
div[data-testid="stButton"] > button[kind="primary"] * {
    color:#FFFFFF !important;
    fill:#FFFFFF !important;
}
button[data-testid="stBaseButton-primary"]:hover,
div[data-testid="stButton"] > button[kind="primary"]:hover {
    background:#1D4ED8 !important;
    border-color:#1D4ED8 !important;
}

/* ---------- Selectbox / BaseWeb ---------- */
div[data-testid="stSelectbox"] label {
    color:#475569 !important;
    font-weight:600 !important;
}
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background:#FFFFFF !important;
    border:1px solid #CBD5E1 !important;
    color:#172033 !important;
    border-radius:10px !important;
    min-height:42px !important;
}
div[data-testid="stSelectbox"] div[data-baseweb="select"] * {
    color:#172033 !important;
    fill:#172033 !important;
}
div[data-baseweb="popover"],
div[role="listbox"] {
    background:#FFFFFF !important;
    border:1px solid #CBD5E1 !important;
}
div[role="option"] {
    background:#FFFFFF !important;
    color:#172033 !important;
}
div[role="option"]:hover,
div[role="option"][aria-selected="true"] {
    background:#EFF6FF !important;
    color:#1D4ED8 !important;
}

/* ---------- Radio / slider / uploader ---------- */
div[data-testid="stRadio"] label,
div[data-testid="stFileUploader"] label,
div[data-testid="stSlider"] label {
    color:#475569 !important;
    font-weight:600 !important;
}
div[data-testid="stRadio"] div[role="radiogroup"] label p {
    color:#172033 !important;
}
div[data-testid="stSlider"] {
    color:#172033 !important;
}
div[data-testid="stFileUploader"] section {
    background:#FFFFFF !important;
    border:1px dashed #CBD5E1 !important;
    border-radius:12px !important;
}

/* ---------- Metrics ---------- */
div[data-testid="stMetric"] {
    background:#FFFFFF !important;
    border:1px solid var(--ut-border) !important;
    border-radius:14px !important;
    padding:1rem 1.1rem !important;
    box-shadow:0 1px 2px rgba(15,23,42,.04) !important;
}
div[data-testid="stMetricLabel"],
div[data-testid="stMetricLabel"] * {
    color:#64748B !important;
    font-weight:600 !important;
}
div[data-testid="stMetricValue"],
div[data-testid="stMetricValue"] * {
    color:#172033 !important;
    font-weight:800 !important;
}
div[data-testid="stMetricValue"] {
    font-size:1.75rem !important;
    line-height:1.15 !important;
}

/* ---------- Cards / containers ---------- */
.event-header {
    padding:1.35rem;
    border:1px solid var(--ut-border);
    border-radius:16px;
    background:#FFFFFF;
    box-shadow:0 1px 2px rgba(15,23,42,.04);
}
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-color:var(--ut-border) !important;
    border-radius:14px !important;
    background:#FFFFFF !important;
}

/* ---------- Alerts ---------- */
div[data-testid="stAlert"] {
    border-radius:12px !important;
    border:1px solid #D9E1EC !important;
}
div[data-testid="stAlert"] p,
div[data-testid="stAlert"] span {
    color:#172033 !important;
}
div[data-testid="stAlert"][kind="info"] {
    background:#EFF6FF !important;
    border-left:4px solid #2563EB !important;
}
div[data-testid="stAlert"][kind="success"] {
    background:#F0FDF4 !important;
    border-left:4px solid #16A34A !important;
}
div[data-testid="stAlert"][kind="warning"] {
    background:#FFFBEB !important;
    border-left:4px solid #D97706 !important;
}
div[data-testid="stAlert"][kind="error"] {
    background:#FEF2F2 !important;
    border-left:4px solid #DC2626 !important;
}

/* ---------- Tables ---------- */
div[data-testid="stDataFrame"] {
    border:1px solid var(--ut-border) !important;
    border-radius:12px !important;
    overflow:hidden !important;
    max-width:100% !important;
    background:#FFFFFF !important;
}
div[data-testid="stDataFrame"] iframe {
    background:#FFFFFF !important;
}

/* ---------- Code ---------- */
div[data-testid="stCodeBlock"] {
    border:1px solid var(--ut-border) !important;
    border-radius:12px !important;
}

/* ---------- Status text ---------- */
.status-allow { color:#16A34A !important; font-weight:800; }
.status-stop { color:#DC2626 !important; font-weight:800; }
.status-escalate { color:#D97706 !important; font-weight:800; }
.attempt-label { color:#64748B; font-size:.72rem; font-weight:800; letter-spacing:.12em; }
.attempt-action { color:#172033; font-size:1.35rem; font-weight:800; }

/* ---------- Misc ---------- */
hr { border-color:var(--ut-border) !important; }
.footer {
    margin-top:4rem;
    padding-top:1.5rem;
    border-top:1px solid var(--ut-border);
    text-align:center;
    color:var(--ut-muted);
}
</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# SESSION STATE
# =========================================================

if "page" not in st.session_state:
    st.session_state.page = "Home"

if "sample_seed" not in st.session_state:
    st.session_state.sample_seed = 42

if "batch_data" not in st.session_state:
    st.session_state.batch_data = pd.DataFrame()

if "batch_results" not in st.session_state:
    st.session_state.batch_results = pd.DataFrame()

if "agent_result" not in st.session_state:
    st.session_state.agent_result = None


# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_events():
    return pd.read_csv(EVENTS_PATH)


@st.cache_data
def load_decisions():
    return pd.read_csv(DECISIONS_PATH)


@st.cache_resource
def load_undertow_model():
    return load_model()


@st.cache_data
def load_recovery_outcomes():
    return load_outcomes()


events = load_events()
decisions = load_decisions()
model = load_undertow_model()
outcomes = load_recovery_outcomes()


# =========================================================
# EXPERIMENT METRICS
# =========================================================

HELD_OUT_EVENTS = 5000

UNDERTOW_RECOVERY = 42019293.0

ALWAYS_RETRY = 25017608.0

UPLIFT = (
    (UNDERTOW_RECOVERY - ALWAYS_RETRY)
    / ALWAYS_RETRY
) * 100


# =========================================================
# HELPERS
# =========================================================

def money(value, decimals=0):
    return f"₹{float(value):,.{decimals}f}"


def action_bar_chart(series):
    data = series.rename("count").reset_index()
    data.columns = ["intervention", "count"]
    chart = (alt.Chart(data).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
        .encode(x=alt.X("intervention:N", title=None, sort="-y", axis=alt.Axis(labelAngle=0)),
                y=alt.Y("count:Q", title="Events"),
                color=alt.Color("intervention:N", scale=alt.Scale(
                    domain=["ALTERNATE_PAYMENT","RETRY_PAYMENT","SEND_REMINDER","UNKNOWN"],
                    range=["#7C3AED","#2563EB","#F59E0B","#94A3B8"]), legend=None),
                tooltip=[alt.Tooltip("intervention:N", title="Action"), alt.Tooltip("count:Q", title="Events")])
        .properties(height=320))
    st.altair_chart(chart, width="stretch")


def recovery_comparison_chart(data):
    chart = (alt.Chart(data.reset_index()).mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8)
        .encode(x=alt.X("Strategy:N", title=None, axis=alt.Axis(labelAngle=0)),
                y=alt.Y("Recovered revenue:Q", title="Recovered revenue (₹)"),
                color=alt.Color("Strategy:N", scale=alt.Scale(domain=["Undertow","Always Retry"], range=["#2563EB","#94A3B8"]), legend=None),
                tooltip=[alt.Tooltip("Strategy:N", title="Strategy"), alt.Tooltip("Recovered revenue:Q", title="Recovered revenue", format=",.0f")])
        .properties(height=360))
    st.altair_chart(chart, width="stretch")


def set_page(page):
    st.session_state.page = page
    st.session_state.scroll_to_top = True
    st.rerun()


# =========================================================
# DECISION ENGINE COMPATIBILITY
# =========================================================

def call_decision_engine(event):
    """
    Calls the existing decision engine while allowing
    small differences in function parameter naming.
    """

    try:

        signature = inspect.signature(make_decision)

        params = signature.parameters

        kwargs = {}

        if "model" in params:
            kwargs["model"] = model

        if "event" in params:
            kwargs["event"] = event

        elif "row" in params:
            kwargs["row"] = event

        elif "transaction" in params:
            kwargs["transaction"] = event

        elif "data" in params:
            kwargs["data"] = event

        return make_decision(**kwargs)

    except Exception:

        # Most likely signature
        try:
            return make_decision(
                model=model,
                event=event,
            )

        except TypeError:

            return make_decision(
                model,
                event,
            )


# =========================================================
# AGENT COMPATIBILITY
# =========================================================

def call_agent(event):
    """
    Calls the existing agent loop without changing
    the backend implementation.
    """

    try:

        signature = inspect.signature(run_agent)

        params = signature.parameters

        kwargs = {}

        if "model" in params:
            kwargs["model"] = model

        if "outcomes" in params:
            kwargs["outcomes"] = outcomes

        if "event" in params:
            kwargs["event"] = event

        elif "row" in params:
            kwargs["row"] = event

        elif "event_id" in params:
            kwargs["event_id"] = event["event_id"]

        return run_agent(**kwargs)

    except Exception:

        try:

            return run_agent(
                model=model,
                outcomes=outcomes,
                event=event,
            )

        except TypeError:

            return run_agent(
                model,
                outcomes,
                event,
            )


# =========================================================
# RESULT NORMALIZATION
# =========================================================

def get_value(
    data,
    keys,
    default=None,
):

    if data is None:
        return default

    for key in keys:

        if isinstance(data, dict) and key in data:
            return data[key]

        if hasattr(data, key):
            return getattr(data, key)

    return default


def normalize_history(result):

    history = get_value(
        result,
        [
            "history",
            "attempt_history",
            "attempts",
        ],
        [],
    )

    if history is None:
        return []

    return history


# =========================================================
# TOP NAVIGATION
# =========================================================

st.markdown('<div class="topbar"></div>', unsafe_allow_html=True)

brand_col, nav1, nav2, nav3, nav4, nav5, nav6 = st.columns(
    [2.2, 0.95, 1.25, 1.0, 1.2, 0.95, 1.0]
)

with brand_col:
    st.markdown('<div class="brand">💰 Undertow</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="brand-sub">Governed AI Revenue Recovery</div>',
        unsafe_allow_html=True,
    )

with nav1:
    if st.button("Home", width="stretch",
                 type="primary" if st.session_state.page == "Home" else "secondary"):
        set_page("Home")
with nav2:
    if st.button("Batch Analysis", width="stretch",
                 type="primary" if st.session_state.page == "Batch Analysis" else "secondary"):
        set_page("Batch Analysis")

        if st.session_state.pop("scroll_to_top", False):
                    st.html(
                        """
                        <script>
                        setTimeout(() => {
                            window.scrollTo({
                                top: 0,
                                left: 0,
                                behavior: "instant"
                            });
                        }, 80);
                        </script>
                        """,
                        unsafe_allow_javascript=True,
                    )
with nav3:
    if st.button("Portfolio", width="stretch",
                 type="primary" if st.session_state.page == "Portfolio" else "secondary"):
        set_page("Portfolio")
with nav4:
    if st.button("Recovery Agent", width="stretch",
                 type="primary" if st.session_state.page == "Recovery Agent" else "secondary"):
        set_page("Recovery Agent")
with nav5:
    if st.button("Analytics", width="stretch",
                 type="primary" if st.session_state.page == "Analytics" else "secondary"):
        set_page("Analytics")
with nav6:
    if st.button("Overview", width="stretch",
                 type="primary" if st.session_state.page == "Overview" else "secondary"):
        set_page("Overview")

        # Scroll to the top after navigation.
        if st.session_state.pop("scroll_to_top", False):
            st.html(
                """
                <script>
                setTimeout(() => {
                    window.scrollTo({
                        top: 0,
                        left: 0,
                        behavior: "instant"
                    });
                }, 80);
                </script>
                """,
                unsafe_allow_javascript=True,
            )


# =========================================================
# HOME — PRODUCT LANDING PAGE
# =========================================================
# UNDERTOW_HOME_REDESIGN_V2

if st.session_state.page == "Home":

    st.write("")
    st.caption("GOVERNED AI REVENUE RECOVERY · PRODUCT OVERVIEW")

    st.markdown(
        """
        <div style="max-width:900px;padding:2.2rem 0 1.2rem 0;">
            <div style="
                font-size:clamp(2.4rem,5vw,4.4rem);
                line-height:1.02;font-weight:850;letter-spacing:-.055em;
                color:#172033;">
                Recover revenue that<br>
                would otherwise be lost.
            </div>
            <div style="
                margin-top:1.25rem;max-width:780px;font-size:1.08rem;
                line-height:1.7;color:#5B6B82;">
                Undertow finds revenue at risk across failed payments,
                abandoned checkouts, failed subscriptions and overdue
                receivables. It predicts the most promising recovery action,
                prioritizes opportunities by expected recovered revenue,
                and applies deterministic governance before execution.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # c1, c2, c3, c4 = st.columns(4)
    # c1.metric("Held-out events", f"{HELD_OUT_EVENTS:,}")
    # c2.metric("Undertow recovery", money(UNDERTOW_RECOVERY))
    # c3.metric("Always Retry", money(ALWAYS_RETRY))
    # c4.metric("Uplift vs baseline", f"+{UPLIFT:.2f}%")

    st.write("")
    st.divider()

    st.markdown('<div class="section-title">From revenue risk to recovery</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="section-description">'
        'Undertow closes the loop instead of stopping at prediction.'
        '</div>',
        unsafe_allow_html=True,
    )

    flow = [
        ("01", "Detect", "Find failed or at-risk revenue."),
        ("02", "Predict", "Estimate recovery probability and value."),
        ("03", "Prioritize", "Select the highest-value opportunities."),
        ("04", "Govern", "Apply deterministic action rules."),
        ("05", "Recover", "Run a bounded recovery workflow."),
    ]

    cols = st.columns(5)
    for col, (number, title, description) in zip(cols, flow):
        with col:
            st.markdown(
                f"""
                <div style="
                    background:#FFFFFF;border:1px solid #D9E1EC;
                    border-radius:14px;padding:1.2rem;min-height:155px;
                    box-shadow:0 1px 2px rgba(15,23,42,.04);">
                    <div style="font-size:.72rem;font-weight:800;
                                letter-spacing:.12em;color:#2563EB;">{number}</div>
                    <div style="margin-top:.55rem;font-size:1.08rem;
                                font-weight:800;color:#172033;">{title}</div>
                    <div style="margin-top:.45rem;font-size:.88rem;
                                line-height:1.5;color:#5B6B82;">{description}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")
    st.divider()

    left, right = st.columns([1.25, 1])

    with left:
        st.markdown('<div class="section-title">The key idea</div>',
                    unsafe_allow_html=True)
        st.markdown(
            """
            <div style="font-size:1.55rem;line-height:1.35;font-weight:800;
                        letter-spacing:-.025em;color:#172033;max-width:700px;">
                Most recovery systems optimize individual failures.
                Undertow optimizes the recovery portfolio.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write(
            "When recovery capacity is limited, Undertow ranks opportunities "
            "by expected recovered revenue instead of treating every failed "
            "payment equally."
        )

    with right:
        st.markdown('<div class="section-title">Controlled automation</div>',
                    unsafe_allow_html=True)
        st.write(
            "The prediction model estimates what is likely to work. "
            "A deterministic Governor separately decides whether the "
            "system is permitted to act."
        )
        st.success("ALLOW  ·  action satisfies recovery rules")
        st.warning("STOP  ·  expected recovery is too low")
        st.error("ESCALATE  ·  human review is required")

    st.divider()

    st.markdown('<div class="section-title">Explore Undertow</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="section-description">'
        'Inspect decisions, portfolio selection, agent behavior and measured results.'
        '</div>',
        unsafe_allow_html=True,
    )

    e1, e2, e3, e4 = st.columns(4)

    with e1:
        st.markdown("**Batch Analysis**")
        st.caption("Score a batch of revenue-loss events.")
        if st.button("Open Batch Analysis", key="home_batch", width="stretch"):
            set_page("Batch Analysis")

    with e2:
        st.markdown("**Portfolio**")
        st.caption("See how limited recovery capacity is allocated.")
        if st.button("Open Portfolio", key="home_portfolio", width="stretch"):
            set_page("Portfolio")

    with e3:
        st.markdown("**Recovery Agent**")
        st.caption("Run the bounded recovery loop on an event.")
        if st.button("Open Recovery Agent", key="home_agent", width="stretch"):
            set_page("Recovery Agent")

    with e4:
        st.markdown("**Analytics**")
        st.caption("Measure recovery against the baseline.")
        if st.button("Open Analytics", key="home_analytics", width="stretch"):
            set_page("Analytics")

    st.write("")
    st.caption(
        "Evaluation uses held-out events and simulated recovery outcomes. "
        "No real payment or messaging provider is connected."
    )

# =========================================================
# BATCH ANALYSIS
# =========================================================

elif st.session_state.page == "Batch Analysis":

    st.title(
        "Batch Recovery Analysis"
    )

    st.caption(
        "Score failed revenue events and identify the "
        "highest-value recovery opportunities."
    )

    # -----------------------------------------------------
    # INPUT
    # -----------------------------------------------------

    input_mode = st.radio(
        "Input source",
        [
            "Random sample",
            "Upload CSV",
        ],
        horizontal=True,
    )

    input_data = pd.DataFrame()

    if input_mode == "Random sample":

        c1, c2 = st.columns(
            [2, 1]
        )

        with c1:

            sample_size = st.selectbox(
                "Sample size",
                [
                    100,
                    500,
                    1000,
                    2500,
                    5000,
                ],
                index=1,
            )

        with c2:

            st.write("")

            if st.button(
                "🔄 New sample",
                width="stretch",
            ):

                st.session_state.sample_seed += 1

                st.session_state.batch_results = (
                    pd.DataFrame()
                )

                st.rerun()

        input_data = events.sample(
            n=min(
                sample_size,
                len(events),
            ),
            random_state=st.session_state.sample_seed,
        ).copy()

        st.caption(
            f"Sample #{st.session_state.sample_seed} "
            f"· {len(input_data):,} events"
        )

    else:

        uploaded = st.file_uploader(
            "Upload failed transaction CSV",
            type=["csv"],
        )

        if uploaded is not None:

            input_data = pd.read_csv(
                uploaded
            )

            st.success(
                f"{len(input_data):,} transactions loaded."
            )

    # -----------------------------------------------------
    # PREVIEW
    # -----------------------------------------------------

    if not input_data.empty:

        st.subheader(
            "Input preview"
        )

        st.dataframe(
            input_data.head(5),
            width="stretch",
            hide_index=True,
        )

        if st.button(
            "▶ Run Undertow",
            type="primary",
            width="stretch",
        ):

            results = []

            progress = st.progress(
                0
            )

            total = len(input_data)

            for index, (_, row) in enumerate(
                input_data.iterrows()
            ):

                event = row.to_dict()

                try:

                    decision = call_decision_engine(
                        event
                    )

                    action = get_value(
                        decision,
                        [
                            "recommended_action",
                            "action",
                            "intervention",
                        ],
                        "UNKNOWN",
                    )

                    probability = float(
                        get_value(
                            decision,
                            [
                                "recovery_probability",
                                "predicted_probability",
                                "probability",
                            ],
                            0,
                        )
                    )

                    expected = float(
                        get_value(
                            decision,
                            [
                                "expected_recovery",
                            ],
                            float(
                                event["amount"]
                            ) * probability,
                        )
                    )

                except Exception:

                    action = "UNKNOWN"

                    probability = 0.0

                    expected = 0.0

                results.append(
                    {
                        "event_id": event.get(
                            "event_id",
                            f"LIVE{index:05d}",
                        ),
                        "customer_id": event.get(
                            "customer_id",
                            "",
                        ),
                        "amount": float(
                            event["amount"]
                        ),
                        "event_type": event.get(
                            "event_type",
                            "",
                        ),
                        "bank": event.get(
                            "bank",
                            "",
                        ),
                        "error_code": event.get(
                            "error_code",
                            "",
                        ),
                        "intervention": action,
                        "recovery_probability": probability,
                        "expected_recovery": expected,
                    }
                )

                progress.progress(
                    (index + 1) / total
                )

            progress.empty()

            st.session_state.batch_data = (
                input_data
            )

            st.session_state.batch_results = (
                pd.DataFrame(results)
            )

            st.success(
                "Undertow analysis complete."
            )

    # -----------------------------------------------------
    # RESULTS
    # -----------------------------------------------------

    results = (
        st.session_state.batch_results
    )

    if not results.empty:

        st.divider()

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Transactions",
            f"{len(results):,}",
        )

        c2.metric(
            "Revenue at input",
            money(
                results["amount"].sum()
            ),
        )

        c3.metric(
            "Expected recovery",
            money(
                results["expected_recovery"].sum()
            ),
        )

        c1, c2 = st.columns(2)

        with c1:

            st.subheader(
                "Recommended actions"
            )

            action_bar_chart(results["intervention"].value_counts())

        with c2:

            st.subheader(
                "Top opportunities"
            )

            st.dataframe(
                results
                .sort_values(
                    "expected_recovery",
                    ascending=False,
                )
                .head(15),
                width="stretch",
                hide_index=True,
            )

        st.subheader(
            "Decision table"
        )

        st.dataframe(
            results,
            width="stretch",
            hide_index=True,
        )

        st.download_button(
            "Download Results CSV",
            data=results.to_csv(index=False),
            file_name="undertow_batch_results.csv",
            mime="text/csv",
            width="stretch",
        )


# =========================================================
# PORTFOLIO
# =========================================================

elif st.session_state.page == "Portfolio":

    st.title(
        "Portfolio Recovery"
    )

    st.caption(
        "Prioritize recovery opportunities when "
        "automated capacity is limited."
    )

    source = st.radio(
        "Opportunity source",
        [
            "Current batch",
            "Held-out experiment",
        ],
        horizontal=True,
    )

    if source == "Held-out experiment":

        portfolio_data = decisions.copy()

    else:

        portfolio_data = (
            st.session_state.batch_results.copy()
        )

    if portfolio_data.empty:

        st.info(
            "Run a batch analysis first."
        )

    else:

        capacity = st.slider(
            "Recovery capacity",
            min_value=1,
            max_value=len(portfolio_data),
            value=min(
                1000,
                len(portfolio_data),
            ),
            step=1,
        )

        selected, deferred = (
            optimize_portfolio(
                portfolio_data,
                capacity,
            )
        )

        portfolio_metrics = (
            calculate_portfolio_metrics(
                selected,
                deferred,
                portfolio_data,
            )
        )

        st.divider()

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Total opportunities",
            f"{portfolio_metrics['total_events']:,}",
        )

        c2.metric(
            "Selected",
            f"{portfolio_metrics['selected_events']:,}",
        )

        c3.metric(
            "Deferred",
            f"{portfolio_metrics['deferred_events']:,}",
        )

        c4.metric(
            "Expected recovery",
            money(
                portfolio_metrics[
                    "selected_expected_recovery"
                ]
            ),
        )

        captured = portfolio_metrics[
            "captured_percentage"
        ]

        st.progress(
            min(
                max(
                    captured,
                    0,
                ),
                1,
            )
        )

        st.caption(
            f"{captured:.2%} of the total expected "
            "recovery opportunity is captured by "
            "the selected portfolio."
        )

        c1, c2 = st.columns(2)

        with c1:

            st.subheader(
                "Selected action distribution"
            )

            action_bar_chart(selected["intervention"].value_counts())

        with c2:

            st.subheader(
                "Deferred opportunity"
            )

            st.metric(
                "Deferred expected recovery",
                money(
                    portfolio_metrics[
                        "deferred_expected_recovery"
                    ]
                ),
            )

        st.subheader(
            "Selected opportunities"
        )

        st.dataframe(
            selected,
            width="stretch",
            hide_index=True,
        )

        st.download_button(
            "Download Portfolio CSV",
            data=selected.to_csv(index=False),
            file_name="undertow_selected_portfolio.csv",
            mime="text/csv",
            width="stretch",
        )


# =========================================================
# RECOVERY AGENT
# =========================================================

elif st.session_state.page == "Recovery Agent":

    st.title(
        "Recovery Agent"
    )

    st.caption(
        "Run Undertow's bounded, stateful recovery workflow "
        "against an actual event."
    )

    st.info(
        "The agent selects actions from the selected event's "
        "data and adapts after unsuccessful attempts."
    )

    # -----------------------------------------------------
    # EVENT SOURCE
    # -----------------------------------------------------

    source = st.radio(
        "Event source",
        [
            "Current batch",
            "Experiment dataset",
        ],
        horizontal=True,
    )

    available_events = (
        st.session_state.batch_data
        if source == "Current batch"
        else events
    )

    selected_event = None

    if available_events.empty:

        st.warning(
            "No current batch exists. "
            "Switch to Experiment dataset or run Batch Analysis first."
        )

    else:

        event_ids = (
            available_events[
                "event_id"
            ]
            .astype(str)
            .tolist()
        )

        selected_id = st.selectbox(
            "Select revenue-loss event",
            event_ids,
        )

        matching = available_events[
            available_events[
                "event_id"
            ].astype(str)
            == selected_id
        ]

        if not matching.empty:

            selected_event = (
                matching.iloc[0]
                .to_dict()
            )

    # -----------------------------------------------------
    # EVENT DETAILS
    # -----------------------------------------------------

    if selected_event:

        st.divider()

        st.markdown(
            '<div class="event-header">',
            unsafe_allow_html=True,
        )

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Event",
            selected_event[
                "event_id"
            ],
        )

        c2.metric(
            "Amount",
            money(
                selected_event[
                    "amount"
                ],
                2,
            ),
        )

        c3.metric(
            "Event type",
            selected_event[
                "event_type"
            ],
        )

        c4.metric(
            "Bank",
            selected_event[
                "bank"
            ],
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )

        st.write("")

        c1, c2, c3 = st.columns(3)

        c1.write(
            f"**Customer:** "
            f"{selected_event.get('customer_id', '-')}"
        )

        c2.write(
            f"**Error:** "
            f"{selected_event.get('error_code', '-')}"
        )

        c3.write(
            f"**Payment method:** "
            f"{selected_event.get('payment_method', '-')}"
        )

        st.write("")

        if st.button(
            "▶ Run Recovery Agent",
            type="primary",
            width="stretch",
        ):

            with st.spinner(
                "Undertow is running the recovery loop..."
            ):

                try:

                    st.session_state.agent_result = (
                        call_agent(
                            selected_event
                        )
                    )

                except Exception as error:

                    st.session_state.agent_result = {
                        "error": str(error)
                    }

    # -----------------------------------------------------
    # AGENT RESULT
    # -----------------------------------------------------

    result = (
        st.session_state.agent_result
    )

    if result:

        st.divider()

        if isinstance(
            result,
            dict
        ) and "error" in result:

            st.error(
                "Recovery Agent error"
            )

            st.code(
                result["error"]
            )

        else:

            final_status = get_value(
                result,
                [
                    "final_status",
                    "status",
                    "actual_status",
                ],
                "UNKNOWN",
            )

            attempts = get_value(
                result,
                [
                    "contact_count",
                    "attempts",
                ],
                len(
                    normalize_history(result)
                ),
            )

            recovered = get_value(
                result,
                [
                    "amount_recovered",
                    "recovered_amount",
                ],
                0,
            )

            st.subheader(
                "Agent Result"
            )

            st.caption(
                "Demo mode: recovery execution and outcomes are simulated. "
                "No real payment or messaging provider is connected."
            )

            if final_status == "RECOVERED":

                st.success(
                    "🧪 SIMULATED RECOVERY SUCCESSFUL"
                )

            elif final_status == "RECOVERY_STOPPED":

                st.warning(
                    "⏹ RECOVERY STOPPED"
                )

            elif final_status in [
                "ESCALATED",
                "HUMAN_REVIEW_REQUIRED",
            ]:

                st.error(
                    "⚠️ HUMAN REVIEW REQUIRED"
                )

            else:

                st.warning(
                    f"Final status: {final_status}"
                )

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Final status",
                str(final_status),
            )

            c2.metric(
                "Attempts",
                str(attempts),
            )

            c3.metric(
                "Simulated amount recovered",
                money(
                    recovered,
                    2,
                ),
            )

            # -------------------------------------------------
            # ATTEMPT HISTORY
            # -------------------------------------------------

            history = normalize_history(
                result
            )

            st.subheader(
                "Attempt History"
            )

            if not history:

                st.info(
                    "No recovery attempts were executed."
                )

            else:

                for index, attempt in enumerate(
                    history,
                    start=1,
                ):

                    action = get_value(
                        attempt,
                        [
                            "action",
                            "intervention",
                            "recommended_action",
                        ],
                        "UNKNOWN",
                    )

                    probability = float(
                        get_value(
                            attempt,
                            [
                                "predicted_probability",
                                "recovery_probability",
                                "probability",
                            ],
                            0,
                        )
                    )

                    expected = float(
                        get_value(
                            attempt,
                            [
                                "expected_recovery",
                            ],
                            0,
                        )
                    )

                    actual = get_value(
                        attempt,
                        [
                            "actual_status",
                            "actual_outcome",
                            "status",
                        ],
                        "UNKNOWN",
                    )

                    recovered_amount = float(
                        get_value(
                            attempt,
                            [
                                "amount_recovered",
                                "recovered_amount",
                            ],
                            0,
                        )
                    )

                    governor = get_value(
                        attempt,
                        [
                            "governor_decision",
                            "decision",
                        ],
                        "",
                    )

                    execution = get_value(
                        attempt,
                        [
                            "execution_status",
                            "execution",
                        ],
                        "",
                    )

                    with st.container(
                        border=True
                    ):

                        left, right = st.columns(
                            [1, 6]
                        )

                        with left:

                            st.markdown(
                                '<div class="attempt-label">'
                                'ATTEMPT'
                                '</div>',
                                unsafe_allow_html=True,
                            )

                            st.markdown(
                                f"## {index}"
                            )

                        with right:

                            st.markdown(
                                f'<div class="attempt-action">'
                                f'{action}'
                                f'</div>',
                                unsafe_allow_html=True,
                            )

                            c1, c2, c3 = st.columns(
                                3
                            )

                            c1.metric(
                                "Predicted probability",
                                f"{probability:.2%}",
                            )

                            c2.metric(
                                "Expected recovery",
                                money(
                                    expected,
                                    2,
                                ),
                            )

                            c3.metric(
                                "Amount recovered",
                                money(
                                    recovered_amount,
                                    2,
                                ),
                            )

                            c1, c2, c3 = st.columns(
                                3
                            )

                            c1.write(
                                f"**Governor:** "
                                f"{governor or '—'}"
                            )

                            c2.write(
                                f"**Execution:** "
                                f"{execution or '—'}"
                            )

                            c3.write(
                                f"**Actual:** "
                                f"{actual}"
                            )

                history_df = pd.DataFrame(history)

                st.download_button(
                    "Download Recovery History CSV",
                    data=history_df.to_csv(index=False),
                    file_name="undertow_recovery_history.csv",
                    mime="text/csv",
                    width="stretch",
                    key="recovery_history_download",
                    )    

            # -------------------------------------------------
            # FINAL GOVERNANCE
            # -------------------------------------------------

            st.subheader(
                "Decision & Governance"
            )

            governor_decision = get_value(
                result,
                [
                    "governor_decision",
                    "decision",
                ],
                "—",
            )

            governor_reason = get_value(
                result,
                [
                    "governor_reason",
                    "reason",
                ],
                "—",
            )

            execution_status = get_value(
                result,
                [
                    "execution_status",
                    "execution",
                ],
                "—",
            )

            actual_status = get_value(
                result,
                [
                    "actual_status",
                    "status",
                ],
                final_status,
            )

            c1, c2 = st.columns(2)

            with c1:

                st.write(
                    f"**Governor decision:** "
                    f"`{governor_decision}`"
                )

                st.write(
                    f"**Governor reason:** "
                    f"{governor_reason}"
                )

            with c2:

                st.write(
                    f"**Execution status:** "
                    f"`{execution_status}`"
                )

                st.write(
                    f"**Actual status:** "
                    f"`{actual_status}`"
                )


# =========================================================
# ANALYTICS
# =========================================================

elif st.session_state.page == "Analytics":

    st.title(
        "Analytics"
    )

    st.caption(
        "Measure Undertow's recovery strategy against "
        "the Always Retry baseline."
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Held-out events",
        f"{HELD_OUT_EVENTS:,}",
    )

    c2.metric(
        "Undertow recovery",
        money(
            UNDERTOW_RECOVERY
        ),
    )

    c3.metric(
        "Uplift",
        f"+{UPLIFT:.2f}%",
    )

    st.divider()

    st.subheader(
        "Undertow vs Always Retry"
    )

    comparison = pd.DataFrame(
        {
            "Strategy": [
                "Undertow",
                "Always Retry",
            ],
            "Recovered revenue": [
                UNDERTOW_RECOVERY,
                ALWAYS_RETRY,
            ],
        }
    ).set_index(
        "Strategy"
    )

    recovery_comparison_chart(comparison)

    st.subheader(
        "Decision distribution"
    )

    action_bar_chart(decisions["intervention"].value_counts())

    st.subheader(
        "Top recovery opportunities"
    )

    st.dataframe(
        decisions
        .sort_values(
            "expected_recovery",
            ascending=False,
        )
        .head(20),
        width="stretch",
        hide_index=True,
    )

    st.download_button(
        "Download Analytics CSV",
        data=decisions.to_csv(index=False),
        file_name="undertow_analytics_decisions.csv",
        mime="text/csv",
        width="stretch",
    )


# =========================================================
# OVERVIEW
# =========================================================

elif st.session_state.page == "Overview":

    st.caption(
        "SYSTEM OVERVIEW"
    )

    st.markdown(
        """
<div class="hero-title">
How Undertow turns revenue risk into governed recovery.
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div class="hero-description">
This technical view explains Undertow's recovery pipeline:
prediction, portfolio optimization, deterministic governance,
and bounded recovery execution.
</div>
""",
        unsafe_allow_html=True,
    )

    st.write("")

    # -----------------------------------------------------
    # KPI
    # -----------------------------------------------------

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Held-out events",
        f"{HELD_OUT_EVENTS:,}",
    )

    c2.metric(
        "Undertow recovery",
        money(UNDERTOW_RECOVERY),
    )

    c3.metric(
        "Always Retry",
        money(ALWAYS_RETRY),
    )

    c4.metric(
        "Uplift",
        f"+{UPLIFT:.2f}%",
    )

    st.divider()

    # -----------------------------------------------------
    # WORKFLOW
    # -----------------------------------------------------

    st.markdown(
        '<div class="section-title">How Undertow works</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-description">'
        'From failed revenue event to governed recovery.'
        '</div>',
        unsafe_allow_html=True,
    )

    workflow = [
        "Failed Event",
        "Decision Engine",
        "Best Action",
        "Portfolio",
        "Governor",
        "Recovery",
        "Outcome",
    ]

    cols = st.columns(len(workflow))

    for col, item in zip(cols, workflow):

        with col:

            st.info(item)

    st.divider()

    # -----------------------------------------------------
    # CORE PRINCIPLES
    # -----------------------------------------------------

    st.markdown(
        '<div class="section-title">What makes Undertow different</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.subheader(
            "🎯 Revenue-aware"
        )

        st.write(
            "Actions are ranked using recovery probability "
            "and transaction value rather than blindly "
            "retrying every failed payment."
        )

    with c2:

        st.subheader(
            "📦 Capacity-aware"
        )

        st.write(
            "When recovery capacity is limited, Undertow "
            "prioritizes the opportunities with the highest "
            "expected recovered revenue."
        )

    with c3:

        st.subheader(
            "🛡️ Governed"
        )

        st.write(
            "A deterministic governor can ALLOW, STOP or "
            "ESCALATE an action before execution."
        )

    st.divider()

    # -----------------------------------------------------
    # GOVERNOR
    # -----------------------------------------------------

    st.markdown(
        '<div class="section-title">Governance</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.success(
            "🟢 ALLOW\n\n"
            "Action satisfies current recovery rules."
        )

    with c2:

        st.warning(
            "🟠 STOP\n\n"
            "Expected recovery is below the minimum threshold."
        )

    with c3:

        st.error(
            "🔴 ESCALATE\n\n"
            "Maximum automated contact limit has been reached."
        )




# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
<div class="footer">
Undertow · Governed AI Revenue Recovery
</div>
""",
    unsafe_allow_html=True,
)