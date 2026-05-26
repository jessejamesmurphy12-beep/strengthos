import streamlit as st
from database import init_db
from auth import login_page
from coach_dashboard import coach_dashboard
from athlete_dashboard import athlete_dashboard

st.set_page_config(
    page_title="StrengthOS",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject global CSS
st.markdown("""
<style>
    /* ── Global dark background ── */
    .stApp { background-color: #0a1628; }
    body, .stMarkdown, p, li, span, div { color: #f0f0f0; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] { background-color: #060e1a; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }

    /* ── Inputs & selects ── */
    input, textarea, select,
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea {
        background-color: #1a2e4a !important;
        color: #f0f0f0 !important;
        border: 1px solid #c9a84c !important;
        border-radius: 6px !important;
    }
    label, .stSelectbox label, .stTextInput label,
    .stTextArea label, .stNumberInput label {
        color: #c9a84c !important;
        font-weight: 600 !important;
    }

    /* ── Buttons ── */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
        color: #ffffff !important;
        background-color: #1a3a6b !important;
        border: 1px solid #c9a84c !important;
    }
    .stButton > button:hover {
        background-color: #c9a84c !important;
        color: #0a1628 !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab"] {
        color: #c9a84c !important;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        border-bottom: 3px solid #c9a84c !important;
        color: #ffffff !important;
    }

    /* ── Metric cards ── */
    .metric-card {
        background: #1a3a6b;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        border-left: 4px solid #c9a84c;
    }
    .metric-card div { color: #ffffff !important; }

    /* ── Section headers ── */
    .section-header {
        font-size: 1.1rem;
        font-weight: 700;
        color: #c9a84c;
        margin-bottom: 0.5rem;
        padding-bottom: 0.4rem;
        border-bottom: 2px solid #c9a84c;
    }

    /* ── Expanders ── */
    div[data-testid="stExpander"] {
        background-color: #112040 !important;
        border: 1px solid #c9a84c !important;
        border-radius: 10px;
    }
    div[data-testid="stExpander"] summary,
    div[data-testid="stExpander"] p,
    div[data-testid="stExpander"] span {
        color: #f0f0f0 !important;
    }

    /* ── Dataframes ── */
    [data-testid="stDataFrame"] { background-color: #112040; color: #f0f0f0; }

    /* ── Forms ── */
    [data-testid="stForm"] {
        background-color: #112040;
        border: 1px solid #1a3a6b;
        border-radius: 10px;
        padding: 1rem;
    }

    /* ── Info / success / warning boxes ── */
    .stAlert { background-color: #1a3a6b !important; color: #f0f0f0 !important; }
</style>
""", unsafe_allow_html=True)

init_db()

if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    login_page()
else:
    role = st.session_state.user["role"]
    if role == "coach":
        coach_dashboard()
    else:
        athlete_dashboard()
