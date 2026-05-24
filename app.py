"""
dashboard/app.py — Vision 2050 Interactive Dashboard

Launch with:
    streamlit run dashboard/app.py
"""

import os
import sys
import json
import glob
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# ── Path setup ─────────────────────────────────────────────────────────────────
DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR      = os.path.dirname(DASHBOARD_DIR)
SRC_DIR       = os.path.join(ROOT_DIR, "src")
sys.path.insert(0, SRC_DIR)

from config import COUNTRIES, WDI_INDICATORS, SDG_LABELS, PROCESSED_DIR, WDI_DIR, OUTPUTS_DIR

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Vision 2050 | National Development Plan Analyzer",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
h1, h2, h3 { font-family: 'Syne', sans-serif !important; }

.main { background: #0a0f1e; }
.block-container { padding-top: 2rem; }

.metric-card {
    background: linear-gradient(135deg, #111827 0%, #1a2235 100%);
    border: 1px solid rgba(99,179,237,0.15);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 0.75rem;
}
.metric-card h3 {
    font-size: 0.7rem !important;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #64748b;
    margin: 0 0 0.3rem 0;
}
.metric-card .value {
    font-family: 'Syne', sans-serif;
    font-size: 2.2rem;
    font-weight: 800;
    color: #e2e8f0;
    line-height: 1;
}
.metric-card .sub {
    font-size: 0.75rem;
    color: #94a3b8;
    margin-top: 0.3rem;
}

.status-pill {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.on-track  { background: rgba(34,197,94,0.15);  color: #4ade80; border: 1px solid rgba(34,197,94,0.3); }
.at-risk   { background: rgba(245,158,11,0.15); color: #fbbf24; border: 1px solid rgba(245,158,11,0.3); }
.off-track { background: rgba(239,68,68,0.15);  color: #f87171; border: 1px solid rgba(239,68,68,0.3); }
.no-data   { background: rgba(148,163,184,0.1); color: #94a3b8; border: 1px solid rgba(148,163,184,0.2); }

.country-header {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: #e2e8f0;
}
.plan-subtitle {
    color: #63b3ed;
    font-size: 0.9rem;
    font-weight: 500;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

.section-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: #475569;
    margin-bottom: 0.75rem;
}

div[data-testid="stSidebar"] {
    background: #070d1a;
    border-right: 1px solid rgba(99,179,237,0.1);
}
</style>
""", unsafe_allow_html=True)


# ── Data loaders ───────────────────────────────────────────────────────────────

@st.cache_data
def load_comparison_table():
    path = os.path.join(OUTPUTS_DIR, "country_comparison.json")
    if os.path.exists(path):
        return pd.read_json(path)
    return pd.DataFrame()


@st.cache_data
def load_scored_profile(country_code: str):
    path = os.path.join(PROCESSED_DIR, f"{country_code}_scored.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None


@st.cache_data
def load_wdi_data(country_code: str):
    path = os.path.join(WDI_DIR, f"{country_code}_wdi.json")
    if os.path.exists(path):
        with open(path) as f:
            d = json.load(f)
        return pd.DataFrame(d["records"])
    return pd.DataFrame()


@st.cache_data
def load_trends(country_code: str):
    path = os.path.join(WDI_DIR, f"{country_code}_trends.json")
    if os.path.exists(path):
        return pd.read_json(path)
    return pd.DataFrame()


def get_available_countries():
    """Return countries that have at least a scored profile."""
    available = []
    for code in COUNTRIES:
        if os.path.exists(os.path.join(PROCESSED_DIR, f"{code}_scored.json")):
            available.append(code)
    return available


# ── Demo data (runs without real pipeline output) ──────────────────────────────

def generate_demo_data():
    """Generate realistic-looking demo data for all 11 countries."""
    import random
    random.seed(42)

    demo_scores = {
        "RWA": {"composite_score": 71.2, "overall_progress": 0.68, "overall_ambition_score": 0.82,
                "sdg_coverage_score": 0.76, "on_track": 4, "at_risk": 2, "off_track": 1, "no_data": 1,
                "plan_summary": "Rwanda's Vision 2050 targets transformation into an upper-middle income country through knowledge-based economy, with strong emphasis on digital innovation, universal healthcare, and regional integration.",
                "priority_sectors": ["Digital Economy", "Agriculture", "Health", "Education", "Energy"],
                "key_themes": ["Knowledge economy", "Regional hub", "Self-reliance", "Green growth"],
                "sdg_coverage": [1,2,3,4,5,7,8,9,10,13,16],
                "top_targets": [
                    {"sector":"Economy","description":"Reach upper-middle income status","target_value":4000,"target_year":2035,"wdi_indicator":"NY.GDP.PCAP.CD","track_status":"on_track","track_label":"On Track","progress_ratio":0.78,"current_value":930,"projected_value":3200},
                    {"sector":"Health","description":"Reduce child mortality","target_value":20,"target_year":2035,"wdi_indicator":"SH.DYN.MORT","track_status":"on_track","track_label":"On Track","progress_ratio":0.81,"current_value":35,"projected_value":22},
                    {"sector":"Energy","description":"Universal electricity access","target_value":100,"target_year":2030,"wdi_indicator":"EG.ELC.ACCS.ZS","track_status":"at_risk","track_label":"At Risk","progress_ratio":0.64,"current_value":53,"projected_value":78},
                    {"sector":"Education","description":"Universal secondary enrollment","target_value":90,"target_year":2035,"wdi_indicator":"SE.PRM.CMPT.ZS","track_status":"on_track","track_label":"On Track","progress_ratio":0.77,"current_value":72,"projected_value":85},
                    {"sector":"Poverty","description":"End extreme poverty","target_value":5,"target_year":2050,"wdi_indicator":"SI.POV.DDAY","track_status":"at_risk","track_label":"At Risk","progress_ratio":0.52,"current_value":52,"projected_value":28},
                ]},
        "GHA": {"composite_score": 58.4, "overall_progress": 0.54, "overall_ambition_score": 0.70,
                "sdg_coverage_score": 0.71, "on_track": 3, "at_risk": 3, "off_track": 2, "no_data": 0,
                "plan_summary": "Ghana Beyond Aid envisions a self-reliant, inclusive, and prosperous nation by reducing aid dependency through industrialization, export diversification, and domestic resource mobilization.",
                "priority_sectors": ["Agriculture", "Industry", "Oil & Gas", "Tourism", "Education"],
                "key_themes": ["Aid independence", "Industrialization", "Resource mobilization", "Governance"],
                "sdg_coverage": [1,2,3,4,7,8,9,10,12,13,16,17],
                "top_targets": [
                    {"sector":"Economy","description":"Become upper-middle income","target_value":3500,"target_year":2030,"wdi_indicator":"NY.GDP.PCAP.CD","track_status":"at_risk","track_label":"At Risk","progress_ratio":0.61,"current_value":2200,"projected_value":2900},
                    {"sector":"Energy","description":"Universal electricity access","target_value":100,"target_year":2030,"wdi_indicator":"EG.ELC.ACCS.ZS","track_status":"on_track","track_label":"On Track","progress_ratio":0.82,"current_value":84,"projected_value":95},
                    {"sector":"Health","description":"Reduce maternal mortality","target_value":70,"target_year":2030,"wdi_indicator":"SH.STA.MMRT","track_status":"off_track","track_label":"Off Track","progress_ratio":0.28,"current_value":310,"projected_value":245},
                    {"sector":"Water","description":"Universal clean water","target_value":100,"target_year":2030,"wdi_indicator":"SH.H2O.BASW.ZS","track_status":"at_risk","track_label":"At Risk","progress_ratio":0.58,"current_value":79,"projected_value":88},
                    {"sector":"Education","description":"Universal literacy","target_value":99,"target_year":2030,"wdi_indicator":"SE.ADT.LITR.ZS","track_status":"on_track","track_label":"On Track","progress_ratio":0.76,"current_value":79,"projected_value":92},
                ]},
        "PAK": {"composite_score": 44.1, "overall_progress": 0.39, "overall_ambition_score": 0.65,
                "sdg_coverage_score": 0.65, "on_track": 2, "at_risk": 2, "off_track": 4, "no_data": 0,
                "plan_summary": "Pakistan Vision 2025 aims to join the top 25 economies through energy security, water management, knowledge economy, and democratic governance — though progress has been constrained by fiscal instability.",
                "priority_sectors": ["Energy", "Water", "Industry", "Agriculture", "Governance"],
                "key_themes": ["Energy security", "Knowledge economy", "Institutional reform", "Regional connectivity"],
                "sdg_coverage": [1,3,4,6,7,8,9,11,13,16],
                "top_targets": [
                    {"sector":"Economy","description":"Top 25 global economies","target_value":6000,"target_year":2025,"wdi_indicator":"NY.GDP.PCAP.CD","track_status":"off_track","track_label":"Off Track","progress_ratio":0.22,"current_value":1400,"projected_value":1700},
                    {"sector":"Energy","description":"End load-shedding","target_value":100,"target_year":2025,"wdi_indicator":"EG.ELC.ACCS.ZS","track_status":"at_risk","track_label":"At Risk","progress_ratio":0.61,"current_value":73,"projected_value":81},
                    {"sector":"Education","description":"100% primary literacy","target_value":100,"target_year":2025,"wdi_indicator":"SE.ADT.LITR.ZS","track_status":"off_track","track_label":"Off Track","progress_ratio":0.31,"current_value":58,"projected_value":64},
                    {"sector":"Health","description":"Reduce child mortality","target_value":40,"target_year":2025,"wdi_indicator":"SH.DYN.MORT","track_status":"at_risk","track_label":"At Risk","progress_ratio":0.55,"current_value":62,"projected_value":53},
                    {"sector":"Water","description":"Universal water access","target_value":100,"target_year":2025,"wdi_indicator":"SH.H2O.BASW.ZS","track_status":"off_track","track_label":"Off Track","progress_ratio":0.35,"current_value":71,"projected_value":78},
                ]},
        "KEN": {"composite_score": 62.8, "overall_progress": 0.59, "overall_ambition_score": 0.74,
                "sdg_coverage_score": 0.76, "on_track": 4, "at_risk": 3, "off_track": 1, "no_data": 0,
                "plan_summary": "Kenya Vision 2030 targets a globally competitive middle-income economy with high quality of life through three pillars: economic, social, and political transformation, anchored by flagship infrastructure projects.",
                "priority_sectors": ["Tourism", "Agriculture", "Manufacturing", "ICT", "Financial Services"],
                "key_themes": ["Middle income status", "Infrastructure", "Innovation hub", "Social equity"],
                "sdg_coverage": [1,2,3,4,5,6,7,8,9,10,11,13,16],
                "top_targets": [
                    {"sector":"Economy","description":"Middle income GDP per capita","target_value":3000,"target_year":2030,"wdi_indicator":"NY.GDP.PCAP.CD","track_status":"on_track","track_label":"On Track","progress_ratio":0.79,"current_value":2100,"projected_value":2700},
                    {"sector":"Education","description":"Universal primary completion","target_value":100,"target_year":2030,"wdi_indicator":"SE.PRM.CMPT.ZS","track_status":"on_track","track_label":"On Track","progress_ratio":0.81,"current_value":85,"projected_value":93},
                    {"sector":"Health","description":"Universal health coverage","target_value":100,"target_year":2030,"wdi_indicator":"SH.H2O.BASW.ZS","track_status":"at_risk","track_label":"At Risk","progress_ratio":0.63,"current_value":63,"projected_value":75},
                    {"sector":"Energy","description":"Geothermal-led clean energy","target_value":85,"target_year":2030,"wdi_indicator":"EG.FEC.RNEW.ZS","track_status":"at_risk","track_label":"At Risk","progress_ratio":0.66,"current_value":75,"projected_value":80},
                    {"sector":"Connectivity","description":"Universal internet access","target_value":80,"target_year":2030,"wdi_indicator":"IT.NET.USER.ZS","track_status":"on_track","track_label":"On Track","progress_ratio":0.77,"current_value":42,"projected_value":64},
                ]},
        "NGA": {"composite_score": 36.5, "overall_progress": 0.31, "overall_ambition_score": 0.72,
                "sdg_coverage_score": 0.71, "on_track": 1, "at_risk": 3, "off_track": 4, "no_data": 0,
                "plan_summary": "Nigeria Agenda 2050 envisions Africa's largest economy becoming a trillion-dollar powerhouse through diversification away from oil, massive infrastructure investment, and human capital development — though structural challenges remain severe.",
                "priority_sectors": ["Oil & Gas", "Agriculture", "Manufacturing", "Infrastructure", "Technology"],
                "key_themes": ["Economic diversification", "Youth dividend", "Industrialization", "Sovereignty"],
                "sdg_coverage": [1,2,3,4,7,8,9,10,11,13,16,17],
                "top_targets": [
                    {"sector":"Economy","description":"Trillion dollar GDP","target_value":9200,"target_year":2050,"wdi_indicator":"NY.GDP.PCAP.CD","track_status":"off_track","track_label":"Off Track","progress_ratio":0.18,"current_value":2200,"projected_value":2900},
                    {"sector":"Energy","description":"Universal electricity","target_value":100,"target_year":2030,"wdi_indicator":"EG.ELC.ACCS.ZS","track_status":"off_track","track_label":"Off Track","progress_ratio":0.24,"current_value":55,"projected_value":62},
                    {"sector":"Poverty","description":"End extreme poverty","target_value":5,"target_year":2050,"wdi_indicator":"SI.POV.DDAY","track_status":"at_risk","track_label":"At Risk","progress_ratio":0.42,"current_value":40,"projected_value":27},
                    {"sector":"Health","description":"Universal health access","target_value":50,"target_year":2030,"wdi_indicator":"SH.DYN.MORT","track_status":"at_risk","track_label":"At Risk","progress_ratio":0.51,"current_value":95,"projected_value":75},
                    {"sector":"Education","description":"Universal basic education","target_value":100,"target_year":2030,"wdi_indicator":"SE.PRM.CMPT.ZS","track_status":"at_risk","track_label":"At Risk","progress_ratio":0.44,"current_value":62,"projected_value":71},
                ]},
        "BGD": {"composite_score": 66.7, "overall_progress": 0.63, "overall_ambition_score": 0.76,
                "sdg_coverage_score": 0.71, "on_track": 4, "at_risk": 3, "off_track": 1, "no_data": 0,
                "plan_summary": "Bangladesh Perspective Plan 2041 targets graduation from LDC to developed country status through manufacturing diversification, digital transformation, and universal social protection — building on the remarkable 'development surprise' of recent decades.",
                "priority_sectors": ["RMG/Manufacturing", "Agriculture", "Digital Economy", "Health", "Infrastructure"],
                "key_themes": ["LDC graduation", "Delta management", "Digital Bangladesh", "Social protection"],
                "sdg_coverage": [1,2,3,4,5,6,7,8,9,10,11,13],
                "top_targets": [
                    {"sector":"Economy","description":"Developed country GDP","target_value":12500,"target_year":2041,"wdi_indicator":"NY.GDP.PCAP.CD","track_status":"on_track","track_label":"On Track","progress_ratio":0.74,"current_value":2700,"projected_value":7200},
                    {"sector":"Poverty","description":"Eliminate extreme poverty","target_value":0,"target_year":2031,"wdi_indicator":"SI.POV.DDAY","track_status":"on_track","track_label":"On Track","progress_ratio":0.82,"current_value":5,"projected_value":1},
                    {"sector":"Health","description":"Reduce child mortality to 25","target_value":25,"target_year":2030,"wdi_indicator":"SH.DYN.MORT","track_status":"on_track","track_label":"On Track","progress_ratio":0.79,"current_value":30,"projected_value":23},
                    {"sector":"Energy","description":"Universal electricity","target_value":100,"target_year":2030,"wdi_indicator":"EG.ELC.ACCS.ZS","track_status":"at_risk","track_label":"At Risk","progress_ratio":0.67,"current_value":90,"projected_value":96},
                    {"sector":"Climate","description":"Reduce per capita emissions","target_value":0.5,"target_year":2041,"wdi_indicator":"EN.ATM.CO2E.PC","track_status":"off_track","track_label":"Off Track","progress_ratio":0.21,"current_value":0.61,"projected_value":0.72},
                ]},
        "IND": {"composite_score": 68.3, "overall_progress": 0.65, "overall_ambition_score": 0.79,
                "sdg_coverage_score": 0.82, "on_track": 5, "at_risk": 2, "off_track": 1, "no_data": 0,
                "plan_summary": "India's Viksit Bharat@2047 vision targets a developed nation status by independence centenary through advanced manufacturing, technology leadership, universal infrastructure, and social equity — leveraging the demographic dividend.",
                "priority_sectors": ["Manufacturing", "Technology", "Infrastructure", "Agriculture", "Services"],
                "key_themes": ["Developed nation by 2047", "Digital economy", "Manufacturing hub", "Green transition"],
                "sdg_coverage": [1,2,3,4,5,6,7,8,9,10,11,12,13,15,16],
                "top_targets": [
                    {"sector":"Economy","description":"$30 trillion GDP economy","target_value":20000,"target_year":2047,"wdi_indicator":"NY.GDP.PCAP.CD","track_status":"on_track","track_label":"On Track","progress_ratio":0.73,"current_value":2500,"projected_value":9800},
                    {"sector":"Energy","description":"500GW renewable energy","target_value":85,"target_year":2030,"wdi_indicator":"EG.FEC.RNEW.ZS","track_status":"on_track","track_label":"On Track","progress_ratio":0.78,"current_value":42,"projected_value":65},
                    {"sector":"Health","description":"Reduce child mortality to 20","target_value":20,"target_year":2030,"wdi_indicator":"SH.DYN.MORT","track_status":"on_track","track_label":"On Track","progress_ratio":0.81,"current_value":31,"projected_value":22},
                    {"sector":"Education","description":"Universal higher education","target_value":60,"target_year":2035,"wdi_indicator":"SE.TER.ENRR","track_status":"at_risk","track_label":"At Risk","progress_ratio":0.55,"current_value":29,"projected_value":40},
                    {"sector":"Digital","description":"Universal internet access","target_value":100,"target_year":2030,"wdi_indicator":"IT.NET.USER.ZS","track_status":"on_track","track_label":"On Track","progress_ratio":0.76,"current_value":55,"projected_value":78},
                ]},
        "ETH": {"composite_score": 49.2, "overall_progress": 0.45, "overall_ambition_score": 0.68,
                "sdg_coverage_score": 0.65, "on_track": 2, "at_risk": 3, "off_track": 3, "no_data": 0,
                "plan_summary": "Ethiopia's Ten Year Development Plan 2030 targets lower-middle income status through agricultural transformation, industrial parks, tourism, and digital economy — hindered in recent years by Tigray conflict impacts.",
                "priority_sectors": ["Agriculture", "Manufacturing", "Tourism", "Energy", "Mining"],
                "key_themes": ["Agricultural transformation", "Industrialization", "Peace dividend", "Export growth"],
                "sdg_coverage": [1,2,3,4,6,7,8,9,10,13],
                "top_targets": [
                    {"sector":"Economy","description":"Lower-middle income status","target_value":1200,"target_year":2030,"wdi_indicator":"NY.GDP.PCAP.CD","track_status":"at_risk","track_label":"At Risk","progress_ratio":0.52,"current_value":1020,"projected_value":1100},
                    {"sector":"Poverty","description":"Cut poverty rate to 10%","target_value":10,"target_year":2030,"wdi_indicator":"SI.POV.DDAY","track_status":"off_track","track_label":"Off Track","progress_ratio":0.29,"current_value":23,"projected_value":19},
                    {"sector":"Energy","description":"Universal electricity","target_value":100,"target_year":2030,"wdi_indicator":"EG.ELC.ACCS.ZS","track_status":"at_risk","track_label":"At Risk","progress_ratio":0.58,"current_value":44,"projected_value":66},
                    {"sector":"Health","description":"Reduce child mortality","target_value":35,"target_year":2030,"wdi_indicator":"SH.DYN.MORT","track_status":"at_risk","track_label":"At Risk","progress_ratio":0.61,"current_value":41,"projected_value":36},
                    {"sector":"Water","description":"Universal safe water","target_value":100,"target_year":2030,"wdi_indicator":"SH.H2O.BASW.ZS","track_status":"off_track","track_label":"Off Track","progress_ratio":0.32,"current_value":57,"projected_value":67},
                ]},
        "TZA": {"composite_score": 55.6, "overall_progress": 0.52, "overall_ambition_score": 0.70,
                "sdg_coverage_score": 0.71, "on_track": 3, "at_risk": 3, "off_track": 2, "no_data": 0,
                "plan_summary": "Tanzania Development Vision 2050 targets a semi-industrialized, middle-income country leveraging natural resources, blue economy, and strategic location — with focus on industrialization and natural gas development.",
                "priority_sectors": ["Agriculture", "Mining", "Tourism", "Manufacturing", "Energy"],
                "key_themes": ["Industrialization", "Blue economy", "Resource wealth", "East Africa hub"],
                "sdg_coverage": [1,2,3,4,6,7,8,9,10,11,13,14],
                "top_targets": [
                    {"sector":"Economy","description":"Middle income status","target_value":3000,"target_year":2050,"wdi_indicator":"NY.GDP.PCAP.CD","track_status":"on_track","track_label":"On Track","progress_ratio":0.77,"current_value":1100,"projected_value":2400},
                    {"sector":"Poverty","description":"Near-zero extreme poverty","target_value":3,"target_year":2050,"wdi_indicator":"SI.POV.DDAY","track_status":"at_risk","track_label":"At Risk","progress_ratio":0.48,"current_value":44,"projected_value":22},
                    {"sector":"Energy","description":"Universal electricity","target_value":100,"target_year":2030,"wdi_indicator":"EG.ELC.ACCS.ZS","track_status":"off_track","track_label":"Off Track","progress_ratio":0.27,"current_value":38,"projected_value":51},
                    {"sector":"Health","description":"Universal health coverage","target_value":75,"target_year":2030,"wdi_indicator":"SH.H2O.BASW.ZS","track_status":"on_track","track_label":"On Track","progress_ratio":0.74,"current_value":59,"projected_value":70},
                    {"sector":"Education","description":"Universal literacy","target_value":99,"target_year":2035,"wdi_indicator":"SE.ADT.LITR.ZS","track_status":"at_risk","track_label":"At Risk","progress_ratio":0.53,"current_value":78,"projected_value":87},
                ]},
        "MYS": {"composite_score": 76.4, "overall_progress": 0.73, "overall_ambition_score": 0.71,
                "sdg_coverage_score": 0.82, "on_track": 6, "at_risk": 1, "off_track": 1, "no_data": 0,
                "plan_summary": "Malaysia's Shared Prosperity Vision 2030 targets shared, sustainable, and responsible prosperity with a focus on reducing inequality between communities, regions, and income groups while maintaining high growth.",
                "priority_sectors": ["Technology", "Services", "Manufacturing", "Agriculture", "Digital Economy"],
                "key_themes": ["Shared prosperity", "Inequality reduction", "Digital economy", "Green growth"],
                "sdg_coverage": [1,3,4,5,7,8,9,10,11,12,13,15,16,17],
                "top_targets": [
                    {"sector":"Economy","description":"High income nation","target_value":15000,"target_year":2030,"wdi_indicator":"NY.GDP.PCAP.CD","track_status":"on_track","track_label":"On Track","progress_ratio":0.84,"current_value":11400,"projected_value":13800},
                    {"sector":"Digital","description":"Digital economy 22.6% of GDP","target_value":100,"target_year":2030,"wdi_indicator":"IT.NET.USER.ZS","track_status":"on_track","track_label":"On Track","progress_ratio":0.88,"current_value":89,"projected_value":95},
                    {"sector":"Energy","description":"31% renewable energy mix","target_value":31,"target_year":2030,"wdi_indicator":"EG.FEC.RNEW.ZS","track_status":"on_track","track_label":"On Track","progress_ratio":0.78,"current_value":21,"projected_value":27},
                    {"sector":"Inequality","description":"Reduce Gini below 0.40","target_value":40,"target_year":2030,"wdi_indicator":"SI.POV.GINI","track_status":"at_risk","track_label":"At Risk","progress_ratio":0.61,"current_value":41.1,"projected_value":40.4},
                    {"sector":"Emissions","description":"45% carbon intensity reduction","target_value":0.3,"target_year":2030,"wdi_indicator":"EN.ATM.CO2E.PC","track_status":"off_track","track_label":"Off Track","progress_ratio":0.24,"current_value":7.2,"projected_value":6.8},
                ]},
        "MNG": {"composite_score": 53.1, "overall_progress": 0.49, "overall_ambition_score": 0.73,
                "sdg_coverage_score": 0.65, "on_track": 3, "at_risk": 3, "off_track": 2, "no_data": 0,
                "plan_summary": "Mongolia's Vision 2050 aims to transform from a mining-dependent economy into a prosperous, knowledge-based nation — leveraging mineral wealth for diversification while addressing urban-rural inequality and environmental challenges.",
                "priority_sectors": ["Mining", "Agriculture", "Tourism", "Technology", "Renewable Energy"],
                "key_themes": ["Resource curse avoidance", "Diversification", "Nomadic heritage", "Steppe ecosystem"],
                "sdg_coverage": [1,2,3,4,7,8,9,10,13,15,16],
                "top_targets": [
                    {"sector":"Economy","description":"Upper-middle income by 2030","target_value":6000,"target_year":2030,"wdi_indicator":"NY.GDP.PCAP.CD","track_status":"at_risk","track_label":"At Risk","progress_ratio":0.61,"current_value":4200,"projected_value":5100},
                    {"sector":"Energy","description":"30% renewable energy","target_value":30,"target_year":2030,"wdi_indicator":"EG.FEC.RNEW.ZS","track_status":"on_track","track_label":"On Track","progress_ratio":0.78,"current_value":9,"projected_value":22},
                    {"sector":"Poverty","description":"Halve poverty to 10%","target_value":10,"target_year":2030,"wdi_indicator":"SI.POV.DDAY","track_status":"off_track","track_label":"Off Track","progress_ratio":0.33,"current_value":27,"projected_value":22},
                    {"sector":"Governance","description":"Improve anti-corruption index","target_value":0.5,"target_year":2030,"wdi_indicator":"CC.EST","track_status":"at_risk","track_label":"At Risk","progress_ratio":0.55,"current_value":-0.3,"projected_value":0.1},
                    {"sector":"Digital","description":"80% internet penetration","target_value":80,"target_year":2030,"wdi_indicator":"IT.NET.USER.ZS","track_status":"on_track","track_label":"On Track","progress_ratio":0.81,"current_value":68,"projected_value":76},
                ]},
    }

    # Build comparison table
    rows = []
    for code, d in demo_scores.items():
        c = COUNTRIES[code]
        rows.append({
            "country_code": code,
            "country_name": c["name"],
            "plan": c["plan"],
            "plan_end": c["plan_period"][1],
            "region": c["region"],
            "income_group": c["income_group"],
            "composite_score": d["composite_score"],
            "overall_progress": d["overall_progress"],
            "ambition_score": d["overall_ambition_score"],
            "sdg_coverage_score": d["sdg_coverage_score"],
            "sdg_count": int(d["sdg_coverage_score"] * 17),
            "targets_total": d["on_track"] + d["at_risk"] + d["off_track"] + d["no_data"],
            "on_track": d["on_track"],
            "at_risk": d["at_risk"],
            "off_track": d["off_track"],
            "no_data": d.get("no_data", 0),
            "priority_sectors": ", ".join(d["priority_sectors"][:4]),
            "key_themes": ", ".join(d["key_themes"][:3]),
            "plan_summary": d["plan_summary"],
        })

    return pd.DataFrame(rows), demo_scores


# ── Chart helpers ──────────────────────────────────────────────────────────────

DARK_BG    = "#0a0f1e"
CARD_BG    = "#111827"
ACCENT     = "#63b3ed"
TEXT_COLOR = "#e2e8f0"
GRID_COLOR = "rgba(255,255,255,0.06)"

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color=TEXT_COLOR, size=12),
    margin=dict(l=10, r=10, t=40, b=10),
)

STATUS_COLORS = {
    "on_track":  "#22c55e",
    "at_risk":   "#f59e0b",
    "off_track": "#ef4444",
    "no_data":   "#64748b",
}


def score_color(score):
    if score is None:
        return "#64748b"
    if score >= 65:
        return "#22c55e"
    elif score >= 50:
        return "#f59e0b"
    return "#ef4444"


# ── Pages ──────────────────────────────────────────────────────────────────────

def page_overview(df: pd.DataFrame, demo_scores: dict):
    st.markdown("## 🌍 National Development Plans — At a Glance")
    st.markdown(
        "<p style='color:#64748b;font-size:0.9rem'>Comparing 11 developing countries' Vision 2050-era policies against World Bank WDI outcome data</p>",
        unsafe_allow_html=True,
    )

    # Top KPI row
    c1, c2, c3, c4 = st.columns(4)
    avg_score = df["composite_score"].mean()
    on_track_pct = df["on_track"].sum() / df["targets_total"].sum() * 100
    avg_sdg = df["sdg_count"].mean()

    with c1:
        st.markdown(f"""<div class='metric-card'>
            <h3>Countries Analyzed</h3>
            <div class='value'>11</div>
            <div class='sub'>4 regions · 3 income groups</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class='metric-card'>
            <h3>Avg. Composite Score</h3>
            <div class='value' style='color:{score_color(avg_score)}'>{avg_score:.0f}<span style='font-size:1rem;color:#64748b'>/100</span></div>
            <div class='sub'>Progress × Ambition × SDG breadth</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class='metric-card'>
            <h3>Targets On Track</h3>
            <div class='value' style='color:#22c55e'>{on_track_pct:.0f}<span style='font-size:1rem;color:#64748b'>%</span></div>
            <div class='sub'>{df['on_track'].sum()} of {df['targets_total'].sum()} scored targets</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class='metric-card'>
            <h3>Avg SDGs Covered</h3>
            <div class='value'>{avg_sdg:.0f}<span style='font-size:1rem;color:#64748b'>/17</span></div>
            <div class='sub'>Malaysia & India lead with 14</div>
        </div>""", unsafe_allow_html=True)

    st.divider()

    # Rankings bar chart
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("#### Composite Score Rankings")
        df_sorted = df.sort_values("composite_score", ascending=True)
        colors = [score_color(s) for s in df_sorted["composite_score"]]

        fig = go.Figure(go.Bar(
            x=df_sorted["composite_score"],
            y=df_sorted["country_name"],
            orientation="h",
            marker=dict(color=colors, opacity=0.85),
            text=df_sorted["composite_score"].round(1),
            textposition="outside",
            textfont=dict(color=TEXT_COLOR, size=11),
            hovertemplate="<b>%{y}</b><br>Score: %{x:.1f}/100<extra></extra>",
        ))
        fig.update_layout(**PLOTLY_LAYOUT, height=420,
            xaxis=dict(range=[0,105], gridcolor=GRID_COLOR, tickfont=dict(size=10)),
            yaxis=dict(gridcolor=GRID_COLOR),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown("#### Track Status Distribution")
        # Stacked bar by country
        df_sorted2 = df.sort_values("composite_score", ascending=False)
        fig2 = go.Figure()
        for status, color, label in [
            ("on_track", "#22c55e", "On Track"),
            ("at_risk",  "#f59e0b", "At Risk"),
            ("off_track","#ef4444","Off Track"),
            ("no_data",  "#475569","No Data"),
        ]:
            fig2.add_trace(go.Bar(
                name=label,
                x=df_sorted2["country_name"],
                y=df_sorted2[status],
                marker_color=color,
                opacity=0.85,
            ))
        fig2.update_layout(
            **PLOTLY_LAYOUT, barmode="stack", height=420,
            legend=dict(orientation="h", y=-0.15, font=dict(size=10)),
            xaxis=dict(tickangle=-35, tickfont=dict(size=9)),
            yaxis=dict(gridcolor=GRID_COLOR),
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Scatter: Ambition vs Progress
    st.markdown("#### Ambition vs. Actual Progress")
    fig3 = px.scatter(
        df,
        x="ambition_score", y="overall_progress",
        size="sdg_count", color="region",
        hover_name="country_name",
        hover_data={"composite_score": True, "plan": True, "ambition_score": ":.2f", "overall_progress": ":.2f"},
        labels={"ambition_score": "Plan Ambition Score", "overall_progress": "Actual Progress Ratio"},
        color_discrete_sequence=px.colors.qualitative.Set2,
        size_max=25,
    )
    fig3.add_shape(type="line", x0=0.4, y0=0.4, x1=0.9, y1=0.9,
                   line=dict(color="#475569", dash="dot", width=1))
    fig3.add_annotation(x=0.82, y=0.78, text="Ambition = Progress", showarrow=False,
                         font=dict(color="#475569", size=10))
    fig3.update_layout(**PLOTLY_LAYOUT, height=380,
        xaxis=dict(gridcolor=GRID_COLOR), yaxis=dict(gridcolor=GRID_COLOR))
    st.plotly_chart(fig3, use_container_width=True)

    # SDG heatmap
    st.markdown("#### SDG Coverage Heatmap")
    sdg_matrix = []
    for _, row in df.iterrows():
        code = row["country_code"]
        profile = demo_scores.get(code, {})
        covered = set(profile.get("sdg_coverage", []))
        for sdg_num in range(1, 18):
            sdg_matrix.append({
                "Country": row["country_name"],
                "SDG": f"SDG {sdg_num}: {SDG_LABELS.get(sdg_num,'')[:18]}",
                "Covered": 1 if sdg_num in covered else 0,
                "sdg_num": sdg_num,
            })
    sdg_df = pd.DataFrame(sdg_matrix)
    pivot = sdg_df.pivot(index="Country", columns="SDG", values="Covered")
    # Sort columns numerically
    cols = sorted(pivot.columns, key=lambda x: int(x.split(":")[0].replace("SDG ", "")))
    pivot = pivot[cols]

    fig4 = go.Figure(go.Heatmap(
        z=pivot.values,
        x=[c.split(":")[0] for c in pivot.columns],
        y=pivot.index.tolist(),
        colorscale=[[0, "#1a2235"], [1, "#22c55e"]],
        showscale=False,
        hovertemplate="%{y}<br>%{x}<br>%{z}<extra></extra>",
    ))
    fig4.update_layout(**PLOTLY_LAYOUT, height=360,
        xaxis=dict(tickfont=dict(size=9), tickangle=-45),
        yaxis=dict(tickfont=dict(size=10)),
    )
    st.plotly_chart(fig4, use_container_width=True)


def page_country_deep_dive(df: pd.DataFrame, demo_scores: dict):
    st.markdown("## 🔬 Country Deep Dive")

    code = st.selectbox(
        "Select Country",
        options=list(COUNTRIES.keys()),
        format_func=lambda c: f"{COUNTRIES[c]['name']} — {COUNTRIES[c]['plan']}",
    )

    profile = demo_scores.get(code)
    country_info = COUNTRIES[code]
    row = df[df["country_code"] == code].iloc[0] if code in df["country_code"].values else None

    if not profile or row is None:
        st.info("No scored data yet. Run the pipeline first.")
        return

    # Header
    st.markdown(f"<div class='country-header'>{country_info['name']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='plan-subtitle'>📋 {country_info['plan']} &nbsp;|&nbsp; {country_info['plan_period'][0]}–{country_info['plan_period'][1]} &nbsp;|&nbsp; {country_info['region']}</div>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#94a3b8;margin-top:0.75rem'>{profile['plan_summary']}</p>", unsafe_allow_html=True)

    # Score metrics
    col1, col2, col3, col4 = st.columns(4)
    score = row["composite_score"]
    with col1:
        st.markdown(f"""<div class='metric-card'>
            <h3>Composite Score</h3>
            <div class='value' style='color:{score_color(score)}'>{score:.0f}</div>
            <div class='sub'>out of 100</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        on = profile["on_track"]
        at = profile["at_risk"]
        off = profile["off_track"]
        st.markdown(f"""<div class='metric-card'>
            <h3>Target Status</h3>
            <div class='value'><span style='color:#22c55e'>{on}</span> <span style='font-size:0.9rem;color:#475569'>/</span> <span style='color:#f59e0b'>{at}</span> <span style='font-size:0.9rem;color:#475569'>/</span> <span style='color:#ef4444'>{off}</span></div>
            <div class='sub'>On Track / At Risk / Off Track</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        sdg_count = len(profile["sdg_coverage"])
        st.markdown(f"""<div class='metric-card'>
            <h3>SDGs Covered</h3>
            <div class='value'>{sdg_count}<span style='font-size:1rem;color:#64748b'>/17</span></div>
            <div class='sub'>SDG coverage breadth</div>
        </div>""", unsafe_allow_html=True)
    with col4:
        amb = profile.get("overall_ambition_score", 0) * 100
        st.markdown(f"""<div class='metric-card'>
            <h3>Ambition Score</h3>
            <div class='value'>{amb:.0f}<span style='font-size:1rem;color:#64748b'>%</span></div>
            <div class='sub'>Quantified targets, timelines</div>
        </div>""", unsafe_allow_html=True)

    st.divider()

    # Targets table
    st.markdown("#### 📌 Key Policy Targets & Progress")
    targets = profile.get("top_targets", [])
    if targets:
        for t in targets:
            status = t["track_status"]
            pill_class = status.replace("_", "-")
            progress = t.get("progress_ratio") or 0
            bar_width = min(int(progress * 100), 100)
            bar_color = STATUS_COLORS.get(status, "#64748b")

            current = t.get("current_value")
            target_val = t.get("target_value")
            target_yr = t.get("target_year")
            wdi = t.get("wdi_indicator", "")
            wdi_label = WDI_INDICATORS.get(wdi, {}).get("label", wdi) if wdi else "—"

            cv_str = f"{current:.1f}" if current is not None else "N/A"
            tv_str = f"{target_val:.1f}" if target_val is not None else "N/A"

            st.markdown(f"""
            <div style='background:#111827;border:1px solid rgba(255,255,255,0.06);border-radius:10px;padding:1rem 1.25rem;margin-bottom:0.6rem'>
              <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem'>
                <div>
                  <span style='font-weight:600;color:#e2e8f0'>{t['sector']}</span>
                  <span style='color:#64748b;font-size:0.8rem;margin-left:0.75rem'>{wdi_label}</span>
                </div>
                <span class='status-pill {pill_class}'>{t['track_label']}</span>
              </div>
              <div style='color:#94a3b8;font-size:0.85rem;margin-bottom:0.5rem'>{t['description']}</div>
              <div style='display:flex;align-items:center;gap:1rem'>
                <div style='flex:1;background:#1e293b;border-radius:4px;height:6px;overflow:hidden'>
                  <div style='width:{bar_width}%;height:100%;background:{bar_color};border-radius:4px'></div>
                </div>
                <span style='color:#64748b;font-size:0.75rem;white-space:nowrap'>
                  Current: {cv_str} → Target: {tv_str} by {target_yr or "?"}
                </span>
              </div>
            </div>""", unsafe_allow_html=True)

    col_l, col_r = st.columns(2)
    with col_l:
        # Radar: sector coverage
        st.markdown("#### Priority Sectors")
        sectors = profile.get("priority_sectors", [])
        for s in sectors:
            st.markdown(f"<span style='background:#1e293b;color:#63b3ed;padding:3px 12px;border-radius:20px;font-size:0.8rem;margin:2px;display:inline-block'>{s}</span>", unsafe_allow_html=True)

        st.markdown("<br>**Key Themes**", unsafe_allow_html=True)
        for t in profile.get("key_themes", []):
            st.markdown(f"<span style='background:#1a2235;color:#a78bfa;padding:3px 12px;border-radius:20px;font-size:0.8rem;margin:2px;display:inline-block'>{t}</span>", unsafe_allow_html=True)

    with col_r:
        # Progress donut
        st.markdown("#### Progress Breakdown")
        labels = ["On Track", "At Risk", "Off Track", "No Data"]
        values = [profile["on_track"], profile["at_risk"], profile["off_track"], profile.get("no_data", 0)]
        colors = ["#22c55e", "#f59e0b", "#ef4444", "#475569"]
        fig = go.Figure(go.Pie(
            labels=labels, values=values, hole=0.6,
            marker=dict(colors=colors),
            textfont=dict(size=11),
        ))
        fig.add_annotation(text=f"<b>{score:.0f}</b><br><span style='font-size:10px'>Score</span>",
                           x=0.5, y=0.5, showarrow=False, font=dict(size=18, color=TEXT_COLOR))
        fig.update_layout(**PLOTLY_LAYOUT, height=260,
                          showlegend=True,
                          legend=dict(orientation="h", y=-0.05, font=dict(size=10)))
        st.plotly_chart(fig, use_container_width=True)


def page_compare(df: pd.DataFrame, demo_scores: dict):
    st.markdown("## ⚖️ Cross-Country Comparison")

    selected = st.multiselect(
        "Select countries to compare",
        options=list(COUNTRIES.keys()),
        default=["RWA", "GHA", "IND", "KEN", "MYS"],
        format_func=lambda c: COUNTRIES[c]["name"],
    )
    if not selected:
        st.warning("Select at least one country")
        return

    sub = df[df["country_code"].isin(selected)].copy()

    # Spider / radar chart for multi-dimension comparison
    st.markdown("#### Multi-Dimension Radar")
    dims = ["composite_score", "ambition_score", "sdg_coverage_score", "overall_progress"]
    dim_labels = ["Composite Score", "Ambition", "SDG Coverage", "Progress Rate"]

    fig = go.Figure()
    colors_list = ["#63b3ed", "#22c55e", "#f59e0b", "#a78bfa", "#f472b6", "#34d399"]
    for i, code in enumerate(selected):
        row = sub[sub["country_code"] == code]
        if row.empty:
            continue
        row = row.iloc[0]
        vals = [
            row["composite_score"] / 100,
            row["ambition_score"],
            row["sdg_coverage_score"],
            row["overall_progress"] if row["overall_progress"] else 0,
        ]
        fig.add_trace(go.Scatterpolar(
            r=vals + [vals[0]],
            theta=dim_labels + [dim_labels[0]],
            name=COUNTRIES[code]["name"],
            line=dict(color=colors_list[i % len(colors_list)], width=2),
            fill="toself",
            fillcolor=colors_list[i % len(colors_list)].replace("#", "rgba(").replace(")", ",0.07)") if "#" in colors_list[i % len(colors_list)] else colors_list[i % len(colors_list)],
        ))
    fig.update_layout(
        **PLOTLY_LAYOUT, height=420,
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 1], gridcolor=GRID_COLOR, tickfont=dict(size=8)),
            angularaxis=dict(gridcolor=GRID_COLOR),
        ),
        legend=dict(font=dict(size=11)),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Grouped bar: on_track vs off_track
    st.markdown("#### Target Achievement Comparison")
    fig2 = go.Figure()
    country_names = [COUNTRIES[c]["name"] for c in selected if c in sub["country_code"].values]
    for status, color, label in [
        ("on_track",  "#22c55e", "On Track"),
        ("at_risk",   "#f59e0b", "At Risk"),
        ("off_track", "#ef4444", "Off Track"),
    ]:
        sub2 = sub[sub["country_code"].isin(selected)]
        fig2.add_trace(go.Bar(
            name=label,
            x=[COUNTRIES[c]["name"] for c in selected if c in sub2["country_code"].values],
            y=[sub2[sub2["country_code"] == c][status].iloc[0] if c in sub2["country_code"].values else 0 for c in selected if c in sub2["country_code"].values],
            marker_color=color, opacity=0.85,
        ))
    fig2.update_layout(**PLOTLY_LAYOUT, barmode="group", height=340,
        legend=dict(orientation="h", y=-0.2),
        xaxis=dict(gridcolor=GRID_COLOR),
        yaxis=dict(gridcolor=GRID_COLOR),
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Data table
    st.markdown("#### Summary Table")
    display_cols = ["country_name", "plan", "composite_score", "on_track", "at_risk", "off_track", "sdg_count", "region", "income_group"]
    st.dataframe(
        sub[display_cols].rename(columns={
            "country_name": "Country", "plan": "Plan",
            "composite_score": "Score", "on_track": "✅ On Track",
            "at_risk": "⚠️ At Risk", "off_track": "❌ Off Track",
            "sdg_count": "SDGs", "region": "Region", "income_group": "Income Group",
        }).set_index("Country"),
        use_container_width=True,
    )


def page_methodology():
    st.markdown("## 📐 Methodology")
    st.markdown("""
### Pipeline Overview

```
Policy PDFs → Text Extraction → LLM Structured Extraction → WDI Data → Scoring → Dashboard
```

---

### 1. PDF Ingestion (`src/ingest.py`)
Policy plan PDFs are downloaded and processed using **PyMuPDF** (fitz) with pdfplumber as fallback.
Text is chunked into ~3,000 character overlapping windows for LLM consumption.

---

### 2. LLM Extraction (`src/extract.py`)
Each chunk is sent to a **local Ollama model** (Mistral / LLaMA 3.2) with a structured prompt requesting:
- Priority sectors addressed
- Measurable targets with baseline → target value → year
- SDG alignment tags (1–17)
- Ambition signals and timeline milestones
- Closest World Bank WDI indicator code

Results are synthesized across chunks into a unified country policy profile.

---

### 3. World Bank WDI Data (`src/wdi_fetch.py`)
Actual outcome data is fetched via the **wbdata** library for 18 indicators covering:
- Poverty & inequality
- Health outcomes
- Education attainment
- Energy & infrastructure access
- Environmental indicators
- Governance indices

Data spans 2000–2024 with linear trend computation per indicator.

---

### 4. Progress Scoring (`src/score.py`)
For each extracted target:
1. **Project** the WDI indicator value at the target year using linear extrapolation from recent trends
2. **Compute** progress ratio = (actual change) / (required change to hit target)
3. **Assign status**:
   - ✅ **On Track**: ≥75% of required progress achieved
   - ⚠️ **At Risk**: 40–74% of required progress
   - ❌ **Off Track**: <40% of required progress
   - ❓ **No Data**: Missing WDI data or unmapped indicator

**Composite Score** = Progress (60%) + Ambition (25%) + SDG Breadth (15%), scaled 0–100.

---

### Countries & Plans

| Country | Plan | Period |
|---------|------|--------|
| Rwanda | Vision 2050 | 2020–2050 |
| Ghana | Ghana Beyond Aid | 2017–2057 |
| Pakistan | Vision 2025 | 2014–2025 |
| Kenya | Vision 2030 | 2008–2030 |
| Nigeria | Agenda 2050 | 2021–2050 |
| Bangladesh | Perspective Plan 2041 | 2021–2041 |
| India | Vision India@2047 | 2023–2047 |
| Ethiopia | Ethiopia 2030 | 2020–2030 |
| Tanzania | Vision 2050 | 2021–2050 |
| Malaysia | Shared Prosperity Vision 2030 | 2019–2030 |
| Mongolia | Vision 2050 | 2020–2050 |

---
### Limitations
- LLM extraction may miss implicit targets or mis-map WDI indicators
- Linear trend projection assumes continuation of recent trajectory
- Some plans are aspirational with few measurable numeric targets
- WDI data has gaps for some countries/years
""")


# ── Sidebar & routing ──────────────────────────────────────────────────────────

def main():
    with st.sidebar:
        st.markdown("<h2 style='font-family:Syne;font-size:1.3rem;color:#e2e8f0;margin-bottom:0'>Vision 2050</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#64748b;font-size:0.75rem;margin-top:0;margin-bottom:1.5rem'>National Development Plan Analyzer</p>", unsafe_allow_html=True)

        page = st.radio(
            "Navigate",
            ["🌍 Overview", "🔬 Country Deep Dive", "⚖️ Compare", "📐 Methodology"],
            label_visibility="collapsed",
        )
        st.divider()
        st.markdown("<div class='section-label'>Pipeline Status</div>", unsafe_allow_html=True)
        st.info("🔵 Using demo data.\n\nRun `python src/pipeline.py` to analyze real PDFs.", icon="ℹ️")
        st.divider()
        st.markdown("<p style='color:#475569;font-size:0.7rem'>Data: World Bank WDI · LLM: Ollama Mistral · Plans: Gov't PDFs</p>", unsafe_allow_html=True)

    # Load data
    df_real = load_comparison_table()
    df_demo, demo_scores = generate_demo_data()
    df = df_real if not df_real.empty else df_demo

    if page == "🌍 Overview":
        page_overview(df, demo_scores)
    elif page == "🔬 Country Deep Dive":
        page_country_deep_dive(df, demo_scores)
    elif page == "⚖️ Compare":
        page_compare(df, demo_scores)
    elif page == "📐 Methodology":
        page_methodology()


if __name__ == "__main__":
    main()
