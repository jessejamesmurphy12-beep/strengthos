import streamlit as st
from database import init_db
from auth import login_page
from coach_dashboard import coach_dashboard
from athlete_dashboard import athlete_dashboard

st.set_page_config(
    page_title="StrengthOS | Athlete Performance",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# StrengthOS visual system: navy surfaces, restrained gold accents,
# consistent controls, and responsive spacing.
st.markdown(
    """
    <style>
    :root {
        --sos-bg: #08111f;
        --sos-sidebar: #060d18;
        --sos-panel: #101d30;
        --sos-panel-raised: #152640;
        --sos-border: #263852;
        --sos-gold: #d2b15c;
        --sos-gold-soft: #f0d98d;
        --sos-text: #f3f6fb;
        --sos-muted: #a7b4c7;
        --sos-radius: 14px;
    }

    /* App canvas and main content */
    .stApp {
        background:
            radial-gradient(ellipse at 50% -20%, rgba(34, 69, 115, .22), transparent 55%),
            var(--sos-bg);
        color: var(--sos-text);
    }
    [data-testid="stAppViewContainer"] > .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }
    [data-testid="stHeader"] {
        background: rgba(8, 17, 31, .88);
    }
    [data-testid="stMainBlockContainer"] {
        color: var(--sos-text);
    }

    /* Typography: avoid forcing colors on every div/span so widgets remain legible */
    h1, h2, h3, h4 {
        color: var(--sos-text);
        letter-spacing: -0.025em;
    }
    p, li, .stMarkdown, [data-testid="stCaptionContainer"] {
        color: var(--sos-text);
    }
    [data-testid="stCaptionContainer"] {
        color: var(--sos-muted);
    }
    hr {
        border-color: var(--sos-border);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #070f1c 0%, var(--sos-sidebar) 100%);
        border-right: 1px solid #1c2b40;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.1rem;
    }
    [data-testid="stSidebar"] * {
        color: var(--sos-text);
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        border-radius: 9px;
        padding: .35rem .5rem;
    }

    /* Buttons */
    .stButton > button,
    .stDownloadButton > button,
    .stFormSubmitButton > button {
        min-height: 2.55rem;
        border-radius: 9px;
        border: 1px solid #3b5270;
        background: #172944;
        color: var(--sos-text);
        font-weight: 650;
        transition: border-color .15s ease, background .15s ease, transform .15s ease;
    }
    .stButton > button:hover,
    .stDownloadButton > button:hover,
    .stFormSubmitButton > button:hover {
        border-color: var(--sos-gold);
        background: #203653;
        color: #fff;
    }
    .stButton > button:focus,
    .stDownloadButton > button:focus,
    .stFormSubmitButton > button:focus {
        box-shadow: 0 0 0 .15rem rgba(210, 177, 92, .22);
        border-color: var(--sos-gold);
    }
    button[kind="primary"] {
        background: var(--sos-gold) !important;
        border-color: var(--sos-gold) !important;
        color: #101827 !important;
    }
    button[kind="primary"]:hover {
        background: var(--sos-gold-soft) !important;
        color: #101827 !important;
    }

    /* Inputs */
    [data-baseweb="input"] > div,
    [data-baseweb="textarea"] > div,
    [data-baseweb="select"] > div,
    [data-testid="stNumberInput"] [data-baseweb="input"] > div {
        background: #0d192a !important;
        border: 1px solid #30435d !important;
        border-radius: 9px !important;
    }
    [data-baseweb="input"] input,
    [data-baseweb="textarea"] textarea,
    [data-baseweb="select"] input {
        color: var(--sos-text) !important;
        background: transparent !important;
    }
    [data-baseweb="input"] > div:focus-within,
    [data-baseweb="textarea"] > div:focus-within,
    [data-baseweb="select"] > div:focus-within {
        border-color: var(--sos-gold) !important;
        box-shadow: 0 0 0 1px rgba(210, 177, 92, .18);
    }
    label, [data-testid="stWidgetLabel"] p {
        color: #d9c27e !important;
        font-weight: 600 !important;
    }
    [data-baseweb="select"] span {
        color: var(--sos-text);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: .4rem;
        border-bottom: 1px solid var(--sos-border);
        padding: .25rem .25rem 0;
    }
    .stTabs [data-baseweb="tab"] {
        min-height: 2.7rem;
        padding: .55rem 1rem;
        border-radius: 9px 9px 0 0;
        color: var(--sos-muted);
        font-weight: 650;
        background: transparent;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--sos-text);
        background: rgba(255, 255, 255, .035);
    }
    .stTabs [aria-selected="true"] {
        color: var(--sos-gold-soft) !important;
        border-bottom: 3px solid var(--sos-gold) !important;
        background: rgba(210, 177, 92, .07) !important;
    }
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 1.15rem;
    }

    /* Cards used by existing dashboard HTML */
    .metric-card {
        background: linear-gradient(145deg, #172b47, #101e32);
        border: 1px solid #2a405d;
        border-left: 4px solid var(--sos-gold);
        border-radius: var(--sos-radius);
        padding: 1.25rem 1.4rem;
        box-shadow: 0 8px 22px rgba(0, 0, 0, .12);
    }
    .metric-card div {
        color: var(--sos-text) !important;
    }
    .section-header {
        font-size: 1.02rem;
        font-weight: 750;
        color: var(--sos-gold-soft);
        margin: .25rem 0 .8rem;
        padding-bottom: .65rem;
        border-bottom: 1px solid var(--sos-border);
        letter-spacing: .01em;
    }

    /* Expanders and forms */
    [data-testid="stExpander"] {
        background: rgba(16, 29, 48, .78);
        border: 1px solid var(--sos-border);
        border-radius: 12px;
        overflow: hidden;
    }
    [data-testid="stExpander"] summary {
        font-weight: 650;
    }
    [data-testid="stExpander"] summary:hover {
        color: var(--sos-gold-soft);
    }
    [data-testid="stForm"] {
        background: rgba(16, 29, 48, .72);
        border: 1px solid var(--sos-border);
        border-radius: 12px;
        padding: 1rem 1.1rem;
    }

    /* Tables and dataframes */
    [data-testid="stDataFrame"],
    [data-testid="stTable"] {
        border: 1px solid var(--sos-border);
        border-radius: 10px;
        overflow: hidden;
    }

    /* Alerts */
    [data-testid="stAlert"] {
        border-radius: 10px;
        border: 1px solid var(--sos-border);
    }

    /* Dividers and progress indicators */
    [data-testid="stProgress"] > div > div {
        background-color: var(--sos-gold);
    }

    /* Compact mobile layout */
    @media (max-width: 768px) {
        [data-testid="stAppViewContainer"] > .main .block-container {
            padding: 1.1rem .8rem 2rem;
        }
        .stTabs [data-baseweb="tab"] {
            padding: .45rem .6rem;
            font-size: .88rem;
        }
        .metric-card {
            padding: 1rem;
        }
    }


    /* StrengthOS premium product shell */
    .sos-page-kicker { color: var(--sos-gold); text-transform: uppercase; letter-spacing: .16em; font-size: .72rem; font-weight: 800; margin-bottom: .45rem; }
    .sos-page-title { font-size: clamp(1.8rem, 3vw, 2.55rem); line-height: 1.08; font-weight: 850; letter-spacing: -.045em; color: #f7f9fc; margin: 0; }
    .sos-page-subtitle { color: #9eafc5; font-size: .96rem; margin-top: .55rem; margin-bottom: 1.5rem; }
    .sos-panel { background: linear-gradient(145deg, rgba(19,35,57,.98), rgba(12,24,41,.98)); border: 1px solid #263b56; border-radius: 16px; padding: 1.15rem 1.25rem; box-shadow: 0 12px 32px rgba(0,0,0,.12); }
    .sos-panel-label { font-size: .72rem; color: #9fb0c5; text-transform: uppercase; letter-spacing: .12em; font-weight: 750; }
    .sos-panel-title { color: #f5f7fb; font-size: 1.05rem; font-weight: 780; margin-top: .4rem; }
    .sos-panel-copy { color: #9eafc5; font-size: .86rem; margin-top: .25rem; }
    .sos-stat { min-height: 142px; position: relative; overflow: hidden; background: linear-gradient(145deg,#152944,#0f1c2f); border: 1px solid #2b405c; border-radius: 16px; padding: 1.2rem 1.25rem; }
    .sos-stat:after { content: ''; position: absolute; width: 100px; height: 100px; border-radius: 50%; right: -36px; top: -40px; border: 1px solid rgba(210,177,92,.20); box-shadow: 0 0 0 14px rgba(210,177,92,.025), 0 0 0 28px rgba(210,177,92,.02); }
    .sos-stat-top { color: #a7b7cb; font-size: .78rem; font-weight: 700; letter-spacing: .03em; }
    .sos-stat-value { color: #fff; font-size: 2.1rem; font-weight: 850; line-height: 1.2; margin: .55rem 0 .35rem; letter-spacing: -.04em; }
    .sos-stat-foot { color: #d4b965; font-size: .78rem; font-weight: 650; }
    .sos-list-row { display: flex; justify-content: space-between; align-items: center; gap: 1rem; padding: .85rem 0; border-bottom: 1px solid rgba(47,67,93,.7); }
    .sos-list-row:last-child { border-bottom: 0; }
    .sos-list-name { color: #f3f6fb; font-size: .93rem; font-weight: 750; }
    .sos-list-meta { color: #9eafc5; font-size: .78rem; margin-top: .18rem; }
    .sos-pill { display: inline-block; border: 1px solid rgba(210,177,92,.4); background: rgba(210,177,92,.1); color: #e5cb7a; padding: .22rem .55rem; border-radius: 99px; font-size: .68rem; font-weight: 800; white-space: nowrap; }
    .sos-auth-brand { text-align: center; padding: 1.5rem 0 1rem; }
    .sos-auth-mark { display: inline-flex; align-items: center; justify-content: center; width: 58px; height: 58px; border-radius: 17px; color: #101827; background: linear-gradient(145deg,#f0d98d,#c7a447); font-size: 1.7rem; box-shadow: 0 10px 25px rgba(210,177,92,.18); }
    .sos-auth-title { color: #f7f9fc; font-size: 2rem; font-weight: 900; letter-spacing: -.05em; margin-top: .65rem; }
    .sos-auth-subtitle { color: #9eafc5; font-size: .7rem; font-weight: 800; letter-spacing: .18em; margin-top: .25rem; }
    .sos-auth-note { border: 1px solid #293d58; border-radius: 12px; padding: .9rem 1rem; margin-top: 1rem; background: rgba(15,29,48,.8); }
    .sos-auth-note strong { display:block; color:#e4c875; font-size:.85rem; margin-bottom:.2rem; }
    .sos-auth-note span { color:#9eafc5; font-size:.8rem; }
    [data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] { gap: .3rem; }
    [data-testid="stSidebar"] [data-testid="stRadio"] label { border: 1px solid transparent; padding: .55rem .7rem; border-radius: 10px; transition: all .15s ease; }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) { background: rgba(210,177,92,.11); border-color: rgba(210,177,92,.3); }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p { color: #f0d98d !important; font-weight: 800; }
    [data-testid="stMetric"] { background: linear-gradient(145deg,#152944,#0f1c2f); border: 1px solid #2b405c; padding: 1rem 1.1rem; border-radius: 14px; }
    [data-testid="stMetricLabel"] { color: #a7b7cb !important; }
    [data-testid="stMetricValue"] { color: #fff !important; }
    [data-testid="stVerticalBlockBorderWrapper"] { border-color: #2a405d !important; border-radius: 14px !important; background: rgba(16,29,48,.58); }

    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize the existing database and preserve the current login/session flow.
init_db()

if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    login_page()
else:
    role = st.session_state.user.get("role")
    if role == "coach":
        coach_dashboard()
    elif role == "athlete":
        athlete_dashboard()
    else:
        st.session_state.user = None
        st.warning("Your session role could not be recognized. Please sign in again.")
        st.rerun()
