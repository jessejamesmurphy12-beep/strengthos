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
    [data-testid="stSidebar"] { background-color: #0f172a; }
    [data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }
    .metric-card {
        background: #1e293b;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        color: white;
    }
    .section-header {
        font-size: 1.1rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.5rem;
        padding-bottom: 0.4rem;
        border-bottom: 2px solid #3b82f6;
    }
    div[data-testid="stExpander"] {
        border: 1px solid #e2e8f0;
        border-radius: 10px;
    }
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
