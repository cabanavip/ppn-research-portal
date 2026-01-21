import streamlit as st
import pandas as pd
import altair as alt
import random
import os
from datetime import date

# -----------------------------------------------------------------------------
# 1. APP CONFIGURATION & STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="PPN Research Portal",
    page_icon="🧠",
    layout="wide"
)

# CSS: Google Fonts (Remote) + Stitch Design
st.markdown("""
<style>
    /* 1. Import Inter Font from Google */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap');

    /* 2. FORCE FONT GLOBALLY */
    html, body, [class*="css"], [class*="st-"], button, input, textarea {
        font-family: 'Inter', sans-serif !important;
    }

    /* 3. Global Typography Size */
    html, body {
        font-size: 18px !important;
        color: #f3f4f6;
        background-color: #0e1117;
    }
    
    /* Global Background */
    .stApp { background-color: #0e1117; }
    
    /* Headers Scaling */
    h1 { font-size: 3rem !important; font-weight: 800; color: #f9fafb !important; letter-spacing: -0.02em; }
    h2 { font-size: 2.2rem !important; font-weight: 700; color: #f9fafb !important; letter-spacing: -0.01em; }
    h3 { font-size: 1.75rem !important; font-weight: 600; color: #f9fafb !important; }
    
    /* SIDEBAR STYLING */
    section[data-testid="stSidebar"] { 
        background-color: #111827; 
        border-right: 1px solid #1f2937;
    }
    
    /* SIDEBAR BUTTONS */
    div[data-testid="stSidebar"] .stButton button {
        width: 100%;
        text-align: left;
        background-color: transparent;
        border: 1px solid transparent;
        color: #9ca3af;
        margin-bottom: 6px;
        padding: 12px 16px;
        border-radius: 8px;
        transition: all 0.2s ease-in-out;
        font-weight: 500;
        font-size: 16px !important;
        font-family: 'Inter', sans-serif !important;
    }
    div[data-testid="stSidebar"] .stButton button:hover {
        background-color: #1f2937;
        border-color: #374151;
        color: #60a5fa;
        transform: translateX(4px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    div[data-testid="stSidebar"] .stButton button:focus {
        background-color: #1f2937;
        color: #60a5fa;
        border-color: #60a5fa;
    }

    /* CARDS & CONTAINERS */
    .stitch-card {
        background-color: #1f2937;
        padding: 28px;
        border-radius: 12px;
        border: 1px solid #374151;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 24px;
    }
    
    /* PRICING CARDS */
    .pricing-card {
        background-color: #1f2937;
        padding: 40px;
        border-radius: 16px;
        border: 1px solid #374151;
        text-align: center;
        height: 100%;
        transition: transform 0.2s;
    }
    .pricing-card:hover {
        transform: translateY(-5px);
        border-color: #60a5fa;
    }
    .price-tag {
        font-size: 2.5rem;
        font-weight: 800;
        color: #f3f4f6;
        margin: 20px 0;
        font-family: 'Inter', sans-serif !important;
    }
    .feature-list {
        text-align: left;
        margin: 30px 0;
        line-height: 2;
        color: #9ca3af;
        font-size: 16px;
    }
    
    /* Mission Hero */
    .mission-hero {
        font-size: 1.8rem;
        line-height: 1.5;
        font-style: italic;
        text-align: center;
        color: #e5e7eb;
        padding: 60px 40px;
        margin: 40px 0;
        border-left: 6px solid #f59e0b;
        background: linear-gradient(90deg, #1f2937 0%, #111827 100%);
        border-radius: 8px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        font-family: 'Inter', sans-serif !important;
    }

    /* Medical Card */
    .med-card {
        background-color: #1f2937;
        padding: 24px;
        border-radius: 12px;
        border-left: 5px solid #3b82f6;
        border-top: 1px solid #374151;
        border-right: 1px solid #374151;
        border-bottom: 1px solid #374151;
        margin-top: 15px;
    }

    /* Hide Default Nav */
    [data-testid="stSidebarNav"] {display: none;}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. SESSION STATE
# -----------------------------------------------------------------------------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'page' not in st.session_state:
    st.session_state.page = 'Dashboard'
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
if 'data_scope' not in st.session_state:
    st.session_state.data_scope = "Global Network"

# -----------------------------------------------------------------------------
# 3. DATA & CONSTANTS
# -----------------------------------------------------------------------------
CSV_PATH = "seed_data.csv"
REQUIRED_COLS = [
    "Practitioner_Name", "Client_ID", "Treatment_Date", "Patient_Age", "Patient_Sex",
    "Focus_Area", "Chemical_Used", "Dosage_Mg", "Intake_Form", "Protocol_Description",
    "Treatment_Outcome_Rating", "Detailed_Results", "Next_Steps"
]
FOCUS_AREAS = ["PTSD", "Addiction", "General Personal Health", "Spirituality"]
CHEMICALS = ["Psilocybin", "Ketamine", "MDMA", "DMT", "LSD", "Cannabis", "Other"]
INTAKE_FORMS = ["Inhaled", "Eaten", "Drank", "Injected", "Topical", "Other"]
SEX_OPTIONS = ["M", "F", "Non-Binary"]

def get_practitioner_details(name):
    random.seed(name)
    locs = ["Portland, OR", "Denver, CO", "Oakland, CA", "Ann Arbor, MI", "Austin, TX"]
    specs = ["Integration Specialist", "Somatic Therapy", "Trauma Informed Care"]
    return {
        "Name": name,
        "Location": random.choice(locs),
        "Specialty": random.choice(specs),
        "Email": f"dr.{name.split()[-1].lower()}@ppn.network"
    }

# -----------------------------------------------------------------------------
# 4. DATA LOGIC
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_data():
    try:
        df = pd.read_csv(CSV_PATH)
        for c in REQUIRED_COLS:
            if c not in df.columns: df[c] = ""
        df["Treatment_Outcome_Rating"] = pd.to_numeric(df["Treatment_Outcome_Rating"], errors='coerce').fillna(0)
        return df
    except:
        return pd.DataFrame(columns=REQUIRED_COLS)

def append_record_to_csv(record):
    df = pd.DataFrame([record])
    hdr = not os.path.exists(CSV_PATH)
    try:
        df.to_csv(CSV_PATH, mode='a', header=hdr, index=False)
        load_data.clear()
        return True
    except Exception as e:
        st.error(f"Save Error: {e}")
        return False

def parse_smart_query(query, dataframe):
    if not query: return dataframe
    q_str = query.lower().strip()
    mask = (
        dataframe['Chemical_Used'].str.lower().str.contains(q_str, na=False) |
        dataframe['Focus_Area'].str.lower().str.contains(q_str, na=False) |
        dataframe['Practitioner_Name'].str.lower().str.contains(q_str, na=False) |
        dataframe['Client_ID'].str.lower().str.contains(q_str, na=False)
    )
    return dataframe[mask]

df = load_data()

# -----------------------------------------------------------------------------
# 5. SIDEBAR LOGIC
# -----------------------------------------------------------------------------
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.markdown("## PPN")

    # --- STATE A: LOGGED OUT ---
    if not st.session_state.logged_in:
        st.markdown("### Practitioner Login")
        with st.form("sidebar_login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            btn = st.form_submit_button("Secure Login", type="primary", use_container_width=True)
            
            if btn:
                if u == "admin" and p == "password":
                    st.session_state.logged_in = True
                    st.session_state.page = 'Dashboard'
                    st.rerun()
                else:
                    st.error("Invalid Credentials")

    # --- STATE B: LOGGED IN ---
    else:
        def nav_to(page):
            st.session_state.page = page
            st.rerun()

        st.caption("MENU")
        if st.button("📊  Dashboard"): nav_to('Dashboard')
        if st.button("➕  Add New Record"): nav_to('Add Record')
        if st.button("💎  Membership"): nav_to('Membership')
        
        st.markdown("---")
        if st.button("Log Out"):
            st.session_state.logged_in = False
            st.rerun()


# -----------------------------------------------------------------------------
# 6. MAIN CONTENT AREA LOGIC
# -----------------------------------------------------------------------------

# --- VIEW A: LOGGED OUT (Landing Page) ---
if not st.session_state.logged_in:
    
    # Hero: Mission Statement
    st.markdown("""
    <div class="mission-hero">
    "We are a community of nootropic practitioners devoted to improving the quality of each human life. 
    We share a philosophy of optimizing what nature provides in a safe and life changing way. 
    We openly share our professional expertise, practical experience, and protocols with each other. 
    We are stronger together."
    </div>
    """, unsafe_allow_html=True)
    
    # Testimonials
    t1, t2, t3 = st.columns(3)
    with t1:
        st.markdown('<div class="stitch-card"><h4>Dr. Sarah Jenkins</h4><p style="color:#9ca3af; font-style:italic">"The PPN database has completely transformed how I track patient outcomes. The peer data is invaluable."</p></div>', unsafe_allow_html=True)
    with t2:
        st.markdown('<div class="stitch-card"><h4>Marcus Thorne, PhD</h4><p style="color:#9ca3af; font-style:italic">"Finally, a secure place to share protocols without stigma. The community aspect is a game changer."</p></div>', unsafe_allow_html=True)
    with t3:
        st.markdown('<div class="stitch-card"><h4>Dr. Elena Rodriguez</h4><p style="color:#9ca3af; font-style:italic">"I use the trend analysis daily to benchmark patient outcomes against the network average."</p></div>', unsafe_allow_html=True)


# --- VIEW B: LOGGED IN (App Features) ---
else:
    
    # PAGE: DASHBOARD (Default)
    if st.session_state.page == 'Dashboard':
        st.title("Clinical Research Dashboard")
        
        # 1. SCOPE TOGGLE
        scope = st.radio("Data Scope", ["Global Network", "My Practice (Dr. A. Smith)"], horizontal=True)
        st.markdown("---")

        # 2. FILTER DATA
        active_df = df.copy()
        if "My Practice" in scope:
            active_df = active_df[active_df['Practitioner_Name'] == "Dr. A. Smith"]
            if active_df.empty:
                st.warning("You have not contributed any records yet. Switch to Global Network to see peer data.")

        # 3. SEARCH BAR
        c_search, c_act = st.columns([4, 1])
        with c_search:
            q = st.text_input("Search", placeholder="Search practitioners, chemicals, conditions...", value=st.session_state.search_query, label_visibility="collapsed")
        with c_act:
            if st.button("Run Query", type="primary", use_container_width=True):
                st.session_state.search_query = q
                st.rerun()

        # REMOVED: Advanced Search Placeholder as requested

        filtered_df = parse_smart_query(st.session_state.search_query, active_df)

        # 4. ANALYTICS
        st.markdown("<br>", unsafe_allow_html=True)
        if not filtered_df.empty:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Efficacy Trend**")
                bar = alt.Chart(filtered_df).mark_bar().encode(
                    x=alt.X('Chemical_Used', title=None),
                    y=alt.Y('mean(Treatment_Outcome_Rating)', title='Avg Rating'),
                    color=alt.Color('Chemical_Used', scale=alt.Scale(scheme='viridis'), legend=None),
                    tooltip=['Chemical_Used', 'mean(Treatment_Outcome_Rating)']
                ).properties(height=250, background='transparent')
                st.altair_chart(bar, use_container_width=True)
            with c2:
                st.markdown("**Demographics**")
                donut = alt.Chart(filtered_df).mark_arc(innerRadius=60).encode(
                    theta='count()',
                    color=alt.Color('Focus_Area', scale=alt.Scale(scheme='viridis'), legend=None),
                    tooltip=['Focus_Area', 'count()']
                ).properties(height=250, background='transparent')
                st.altair_chart(donut, use_container_width=True)

        # 5. DATA TABLES
        st.markdown("### Patient Records")
        st.dataframe(filtered_df[['Client_ID', 'Patient_Age', 'Chemical_Used', 'Dosage_Mg', 'Treatment_Outcome_Rating', 'Protocol_Description']], use_container_width=True, hide_index=True)

        # Drill Down
        st.markdown("### Patient Medical Card")
        ids = filtered_df['Client_ID'].unique()
        sel_id = st.selectbox("Select Client ID", ["Select..."] + list(ids))
        if sel_id != "Select...":
            rec = filtered_df[filtered_df['Client_ID'] == sel_id].iloc[0]
            st.markdown(f"""
            <div class="med-card">
                <h3>📁 Client: {rec['Client_ID']}</h3>
                <p><strong>Practitioner:</strong> {rec['Practitioner_Name']} | <strong>Date:</strong> {rec['Treatment_Date']}</p>
                <hr style="border-color:#374151">
                <p><strong>Protocol:</strong><br>{rec['Protocol_Description']}</p>
                <p style="color:#4ade80"><strong>Results:</strong><br>{rec['Detailed_Results']}</p>
                <p><strong>Next Steps:</strong> {rec['Next_Steps']}</p>
            </div>
            """, unsafe_allow_html=True)

    # PAGE: ADD RECORD
    elif st.session_state.page == 'Add Record':
        st.title("Add Clinical Record")
        with st.form("add_rec"):
            c1, c2 = st.columns(2)
            practitioner = c1.text_input("Practitioner Name", value="Dr. A. Smith")
            client_id = c2.text_input("Client ID (Anonymized)")
            
            c3, c4 = st.columns(2)
            age = c3.number_input("Age", 18, 100, 30)
            sex = c4.selectbox("Sex", SEX_OPTIONS)
            
            c5, c6 = st.columns(2)
            focus = c5.selectbox("Focus Area", FOCUS_AREAS)
            chem = c6.selectbox("Chemical", CHEMICALS)
            
            c7, c8 = st.columns(2)
            dose = c7.number_input("Dosage (mg)", 0, 5000, 0)
            intake = c8.selectbox("Intake", INTAKE_FORMS)
            
            prot = st.text_area("Protocol")
            res = st.text_area("Results")
            nxt = st.text_input("Next Steps")
            out = st.slider("Outcome (1-5)", 1, 5, 3)
            
            if st.form_submit_button("Save Record", type="primary"):
                rec = {
                    "Practitioner_Name": practitioner, "Client_ID": client_id, "Treatment_Date": str(date.today()),
                    "Patient_Age": age, "Patient_Sex": sex, "Focus_Area": focus, "Chemical_Used": chem,
                    "Dosage_Mg": dose, "Intake_Form": intake, "Protocol_Description": prot,
                    "Treatment_Outcome_Rating": out, "Detailed_Results": res, "Next_Steps": nxt
                }
                if append_record_to_csv(rec):
                    st.success("Saved!")

    # PAGE: MEMBERSHIP
    elif st.session_state.page == 'Membership':
        st.title("Upgrade your Practice")
        st.markdown("Unlock the full potential of the PPN Network with our premium tiers.")
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="pricing-card">
                <h2 style="color:#60a5fa !important">The Guild</h2>
                <p>Practitioner Tier</p>
                <div class="price-tag">$49<span style="font-size:1rem; color:#9ca3af">/mo</span></div>
                <div class="feature-list">
                    ✅ Access to Global Analytics<br>
                    ✅ Benchmark your Protocols<br>
                    ✅ Peer Network Directory<br>
                    ✅ Unlimited Searches
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.button("Subscribe (Individual)", use_container_width=True, type="primary")
            
        with col2:
            st.markdown("""
            <div class="pricing-card" style="border-color:#f59e0b">
                <h2 style="color:#f59e0b !important">Clinic OS</h2>
                <p>Enterprise Tier</p>
                <div class="price-tag">$499<span style="font-size:1rem; color:#9ca3af">/mo</span></div>
                <div class="feature-list">
                    ✅ Multi-provider Dashboard<br>
                    ✅ Export Raw Data (CSV/API)<br>
                    ✅ White-label Patient Portal<br>
                    ✅ Dedicated Success Manager
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.button("Contact Sales", use_container_width=True)
