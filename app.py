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
