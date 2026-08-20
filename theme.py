# pyrefly: ignore [missing-import]
import streamlit as st

def apply_custom_theme():
    """
    Injects ultra-clean, modern, attractive styling for ClearPolicy AI.
    Designed for high legibility, fresh look, and crisp corporate SaaS aesthetics.
    """
    st.markdown("""
        <style>
        /* Import Corporate Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap');

        /* Main App Background & Typography */
        .stApp {
            background-color: #0F172A;
            color: #F8FAFC;
            font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, sans-serif;
        }

        /* Hide Default Header Elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* Headings */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            letter-spacing: -0.02em;
            color: #F8FAFC;
        }
        
        .main-title {
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 2.2rem;
            font-weight: 800;
            color: #F8FAFC;
            margin-bottom: 0.2rem;
        }

        .sub-title {
            color: #38BDF8;
            font-size: 1.05rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
        }

        /* Clean Enterprise Cards */
        .clean-card {
            background: #1E293B;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 1.25rem;
            margin-bottom: 1rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        }

        /* Verdict Banners */
        .verdict-safe {
            background: rgba(16, 185, 129, 0.12);
            border: 1.5px solid #10B981;
            border-radius: 10px;
            padding: 1.2rem;
            color: #D1FAE5;
            margin-bottom: 1.2rem;
        }

        .verdict-caution {
            background: rgba(245, 158, 11, 0.12);
            border: 1.5px solid #F59E0B;
            border-radius: 10px;
            padding: 1.2rem;
            color: #FEF3C7;
            margin-bottom: 1.2rem;
        }

        .verdict-unsafe {
            background: rgba(239, 68, 68, 0.12);
            border: 1.5px solid #EF4444;
            border-radius: 10px;
            padding: 1.2rem;
            color: #FEE2E2;
            margin-bottom: 1.2rem;
        }

        /* Badges */
        .badge-critical {
            background: #7F1D1D;
            color: #FCA5A5;
            border: 1px solid #EF4444;
            padding: 0.2rem 0.65rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            display: inline-block;
        }

        .badge-warning {
            background: #78350F;
            color: #FDE047;
            border: 1px solid #F59E0B;
            padding: 0.2rem 0.65rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            display: inline-block;
        }

        .badge-low {
            background: #064E3B;
            color: #6EE7B7;
            border: 1px solid #10B981;
            padding: 0.2rem 0.65rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            display: inline-block;
        }

        /* Metric KPI Container */
        .kpi-container {
            background: #1E293B;
            border: 1px solid #334155;
            border-radius: 10px;
            padding: 1rem;
            text-align: center;
        }

        .kpi-val {
            font-size: 1.8rem;
            font-weight: 800;
            color: #F8FAFC;
        }

        .kpi-lbl {
            font-size: 0.8rem;
            color: #94A3B8;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #0B1120 !important;
            border-right: 1px solid #1E293B;
        }

        /* Primary Button */
        .stButton>button {
            background-color: #2563EB;
            color: #FFFFFF;
            font-weight: 600;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1.2rem;
            transition: background 0.15s ease;
        }

        .stButton>button:hover {
            background-color: #1D4ED8;
            color: #FFFFFF;
        }

        /* Tabs Navigation */
        .stTabs [data-baseweb="tab-list"] {
            background-color: #1E293B;
            border-radius: 8px;
            padding: 4px;
            gap: 6px;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 6px;
            color: #94A3B8;
            font-weight: 500;
        }

        .stTabs [aria-selected="true"] {
            background-color: #2563EB !important;
            color: #FFFFFF !important;
        }
        </style>
    """, unsafe_allow_html=True)
