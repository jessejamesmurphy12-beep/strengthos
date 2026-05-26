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
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #0a1628; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }

    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
        color: #ffffff !important;
        background-color: #1a3a6b;
        border: 1px solid #c9a84c;
    }
    .stButton > button:hover {
        background-color: #c9a84c !important;
        color: #0a1628 !important;
    }

    /* Metric cards — navy bg, white text, gold accent */
    .metric-card {
        background: #1a3a6b;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        color: #ffffff;
        border-left: 4px solid #c9a84c;
    }
    .metric-card div { color: #ffffff !important; }

    /* Section headers */
    .section-header {
        font-size: 1.1rem;
        font-weight: 700;
        color: #0a1628;
        margin-bottom: 0.5rem;
        padding-bottom: 0.4rem;
        border-bottom: 3px solid #c9a84c;
    }

    /* Expanders */
    div[data-testid="stExpander"] {
        border: 1px solid #1a3a6b;
        border-radius: 10px;
    }

    /* General text visibility */
    body, .stMarkdown, p, li, label { color: #0a1628; }
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
