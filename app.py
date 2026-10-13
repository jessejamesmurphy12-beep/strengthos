        import streamlit as st
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
