# app.py
# Streamlit Version 7.0: Color-coded Altair charts + Cannabis preserved
# Run: streamlit run app.py

import os
from datetime import date, timedelta

import altair as alt
import pandas as pd
import streamlit as st


# ----------------------------
# Page config + basic styling
# ----------------------------
st.set_page_config(
    page_title="PPN Research Portal",
    page_icon="📊",
    layout="wide",
)

DARK_CSS = """
<style>
.stApp { background-color: #0e1117; color: #e6e6e6; }
section[data-testid="stSidebar"] { background-color: #111827; }
div[data-testid="stMetric"] {
  background: #111827; border: 1px solid #1f2937; border-radius: 10px; padding: 10px;
}
div[data-testid="stDataFrame"] {
  border: 1px solid #1f2937; border-radius: 10px; overflow: hidden;
}
</style>
"""
st.markdown(DARK_CSS, unsafe_allow_html=True)


# ----------------------------
# Constants
# ----------------------------
CSV_PATH = "seed_data.csv"
LOGO_PATH = "logo.png"

FOCUS_AREAS = ["PTSD", "Addiction", "General Personal Health", "Spirituality"]

# Cannabis is included (filters + Add Record dropdown)
CHEMICALS = ["Psilocybin", "Ketamine", "MDMA", "DMT", "LSD", "Cannabis", "Other"]

INTAKE_FORMS = ["Inhaled", "Eaten", "Drank", "Injected", "Topical", "Other"]
SEX_OPTIONS = ["M", "F", "Non-Binary"]

REQUIRED_COLS = [
    "Practitioner_Name",
    "Client_ID",
    "Treatment_Date",
    "Patient_Age",
    "Patient_Sex",
    "Focus_Area",
    "Chemical_Used",
    "Dosage_Mg",
    "Intake_Form",
    "Protocol_Description",
    "Treatment_Outcome_Rating",
    "Detailed_Results",
    "Next_Steps",
]


# ----------------------------
# Data helpers
# ----------------------------
def make_fallback_dataset() -> pd.DataFrame:
    """Small synthetic dataset so the app still runs if the CSV is missing."""
    today = date.today()
    rows = [
        {
            "Practitioner_Name": "Dr. A. Smith",
            "Client_ID": "P-1024",
            "Treatment_Date": str(today - timedelta(days=30)),
            "Patient_Age": 34,
            "Patient_Sex": "F",
            "Focus_Area": "PTSD",
            "Chemical_Used": "Ketamine",
            "Dosage_Mg": 85,
            "Intake_Form": "Injected",
            "Protocol_Description": "Used a monitored ketamine session with guided imagery and integration.",
            "Treatment_Outcome_Rating": 4,
            "Detailed_Results": "Patient reported fewer intrusive thoughts and improved sleep over the next week.",
            "Next_Steps": "Follow up in 2 weeks.",
        },
        {
            "Practitioner_Name": "Clinician B. Jones",
            "Client_ID": "P-3921",
            "Treatment_Date": str(today - timedelta(days=90)),
            "Patient_Age": 52,
            "Patient_Sex": "M",
            "Focus_Area": "Addiction",
            "Chemical_Used": "Psilocybin",
            "Dosage_Mg": 25,
            "Intake_Form": "Eaten",
            "Protocol_Description": "Used a supervised session with a structured preparation and integration plan.",
            "Treatment_Outcome_Rating": 5,
            "Detailed_Results": "Patient reported lower cravings and stronger commitment to a relapse prevention plan.",
            "Next_Steps": "Integration therapy scheduled.",
        },
        {
            "Practitioner_Name": "Dr. L. Patel",
            "Client_ID": "P-7712",
            "Treatment_Date": str(today - timedelta(days=14)),
            "Patient_Age": 41,
            "Patient_Sex": "Non-Binary",
            "Focus_Area": "General Personal Health",
            "Chemical_Used": "Other",
            "Dosage_Mg": 40,
            "Intake_Form": "Topical",
            "Protocol_Description": "Used a structured session with symptom tracking and follow up coaching.",
            "Treatment_Outcome_Rating": 3,
            "Detailed_Results": "Patient reported some stress reduction but had trouble focusing during the session.",
            "Next_Steps": "Reassess in 3 weeks.",
        },
        {
            "Practitioner_Name": "Clinician D. Allen",
            "Client_ID": "P-6603",
            "Treatment_Date": str(today - timedelta(days=7)),
            "Patient_Age": 29,
            "Patient_Sex": "F",
            "Focus_Area": "Spirituality",
            "Chemical_Used": "DMT",
            "Dosage_Mg": 18,
            "Intake_Form": "Inhaled",
            "Protocol_Description": "Used a brief inhalation session with grounding and a short integration debrief.",
            "Treatment_Outcome_Rating": 2,
            "Detailed_Results": "Patient reported anxiety during the peak and needed extra grounding afterward.",
            "Next_Steps": "Pause and review readiness before next session.",
        },
    ]
    df = pd.DataFrame(rows)
    for col in REQUIRED_COLS:
        if col not in df.columns:
            df[col] = ""
    return df[REQUIRED_COLS].copy()


@st.cache_data(show_spinner=False)
def load_data(csv_path: str) -> pd.DataFrame:
    """Load CSV to DataFrame, or use fallback dataset if missing/unreadable."""
    try:
        df = pd.read_csv(csv_path)
    except Exception:
        df = make_fallback_dataset()

    for col in REQUIRED_COLS:
        if col not in df.columns:
            df[col] = ""

    df["Patient_Age"] = pd.to_numeric(df["Patient_Age"], errors="coerce").fillna(0).astype(int)
    df["Dosage_Mg"] = pd.to_numeric(df["Dosage_Mg"], errors="coerce").fillna(0).astype(int)
    df["Treatment_Outcome_Rating"] = pd.to_numeric(
        df["Treatment_Outcome_Rating"], errors="coerce"
    ).fillna(0).astype(int)

    df["Treatment_Date"] = pd.to_datetime(df["Treatment_Date"], errors="coerce")

    for c in ["Practitioner_Name", "Client_ID", "Patient_Sex", "Focus_Area", "Chemical_Used", "Intake_Form"]:
        df[c] = df[c].astype(str).str.strip()

    return df[REQUIRED_COLS].copy()


def clear_data_cache():
    try:
        load_data.clear()
    except Exception:
        try:
            st.cache_data.clear()
        except Exception:
            pass


def append_record_to_csv(csv_path: str, record: dict) -> None:
    """
    Append one row to the CSV using mode='a' so old data is preserved.
    Raises PermissionError if the file is open/locked (common on Windows with Excel).
    """
    abs_path = os.path.abspath(csv_path)
    folder = os.path.dirname(abs_path)
    if folder:
        os.makedirs(folder, exist_ok=True)

    needs_header = (not os.path.exists(abs_path)) or (os.path.getsize(abs_path) == 0)
    row_df = pd.DataFrame([record], columns=REQUIRED_COLS)

    row_df.to_csv(
        abs_path,
        mode="a",
        header=needs_header,
        index=False,
        encoding="utf-8",
        lineterminator="\n",
    )


# ----------------------------
# Search + filter helpers
# ----------------------------
def is_logged_in() -> bool:
    return bool(st.session_state.get("logged_in", False))


def require_login():
    if not is_logged_in():
        st.warning("Please log in first.")
        st.stop()


def search_filter(df: pd.DataFrame, query: str) -> pd.DataFrame:
    """Text search across all columns."""
    q = (query or "").strip()
    if not q:
        return df.copy()

    q_lower = q.lower()
    combined = df.astype(str).apply(lambda row: " | ".join(row.values), axis=1).str.lower()
    return df.loc[combined.str.contains(q_lower, na=False)].copy()


def apply_sidebar_filters(df: pd.DataFrame, focus_list, chemical_list, min_rating: int) -> pd.DataFrame:
    """Apply the sidebar filters."""
    out = df.copy()
    if focus_list is not None:
        out = out[out["Focus_Area"].isin(focus_list)]
    if chemical_list is not None:
        out = out[out["Chemical_Used"].isin(chemical_list)]
    out = out[out["Treatment_Outcome_Rating"] >= int(min_rating)]
    return out.copy()


def format_for_display(df: pd.DataFrame) -> pd.DataFrame:
    """Keep all columns, format date for readability."""
    out = df.copy()
    if pd.api.types.is_datetime64_any_dtype(out["Treatment_Date"]):
        out["Treatment_Date"] = out["Treatment_Date"].dt.strftime("%Y-%m-%d")
    return out


def safe_str(value) -> str:
    if value is None:
        return ""
    s = str(value)
    return "" if s.lower() == "nan" else s


def pick_best_row_for_client(df_filtered: pd.DataFrame, client_id: str) -> pd.Series:
    """If Client_ID appears multiple times, show the most recent one."""
    subset = df_filtered[df_filtered["Client_ID"].astype(str) == str(client_id)].copy()
    if subset.empty:
        return pd.Series(dtype="object")

    if pd.api.types.is_datetime64_any_dtype(subset["Treatment_Date"]):
        subset = subset.sort_values("Treatment_Date", ascending=False, na_position="last")

    return subset.iloc[0]


def df_to_csv_bytes(df_in: pd.DataFrame) -> bytes:
    """Convert a DataFrame to CSV bytes for download."""
    df_out = df_in.copy()
    if "Treatment_Date" in df_out.columns and pd.api.types.is_datetime64_any_dtype(df_out["Treatment_Date"]):
        df_out["Treatment_Date"] = df_out["Treatment_Date"].dt.strftime("%Y-%m-%d")
    return df_out.to_csv(index=False).encode("utf-8")


# ----------------------------
# Altair theme (dark-friendly) + chart builders
# ----------------------------
def enable_altair_dark_theme():
    theme_name = "ppn_dark_theme_v7"
    if st.session_state.get("alt_theme_enabled", False):
        try:
            alt.themes.enable(theme_name)
        except Exception:
            pass
        return

    theme_config = {
        "config": {
            "background": "transparent",
            "title": {"color": "#e6e6e6", "fontSize": 14},
            "axis": {
                "labelColor": "#e6e6e6",
                "titleColor": "#e6e6e6",
                "gridColor": "#1f2937",
                "domainColor": "#1f2937",
                "tickColor": "#1f2937",
            },
            "legend": {"labelColor": "#e6e6e6", "titleColor": "#e6e6e6"},
            "view": {"stroke": "#1f2937"},
        }
    }

    try:
        alt.themes.register(theme_name, lambda: theme_config)
    except Exception:
        pass

    try:
        alt.themes.enable(theme_name)
    except Exception:
        pass

    st.session_state["alt_theme_enabled"] = True


def build_avg_outcome_by_chemical_chart(df_in: pd.DataFrame) -> alt.Chart:
    tmp = (
        df_in.groupby("Chemical_Used", dropna=False)["Treatment_Outcome_Rating"]
        .mean()
        .reset_index()
    )
    tmp["Chemical_Used"] = tmp["Chemical_Used"].astype(str)
    tmp["Treatment_Outcome_Rating"] = tmp["Treatment_Outcome_Rating"].astype(float)

    chart = (
        alt.Chart(tmp, title="Avg Outcome by Chemical")
        .mark_bar()
        .encode(
            y=alt.Y("Chemical_Used:N", sort="-x", title=None),
            x=alt.X("Treatment_Outcome_Rating:Q", title="Average Outcome Rating"),
            color=alt.Color(
                "Chemical_Used:N",
                title="Chemical",
                scale=alt.Scale(scheme="tableau20"),
            ),
            tooltip=[
                alt.Tooltip("Chemical_Used:N", title="Chemical"),
                alt.Tooltip("Treatment_Outcome_Rating:Q", title="Avg Outcome", format=".2f"),
            ],
        )
        .properties(height=300)
    )
    return chart


def build_treatments_by_focus_area_chart(df_in: pd.DataFrame) -> alt.Chart:
    tmp = (
        df_in["Focus_Area"]
        .astype(str)
        .value_counts()
        .reset_index()
    )
    tmp.columns = ["Focus_Area", "Total_Treatments"]
    tmp["Focus_Area"] = tmp["Focus_Area"].astype(str)
    tmp["Total_Treatments"] = tmp["Total_Treatments"].astype(int)

    chart = (
        alt.Chart(tmp, title="Treatments by Focus Area")
        .mark_bar()
        .encode(
            y=alt.Y("Focus_Area:N", sort="-x", title=None),
            x=alt.X("Total_Treatments:Q", title="Total Treatments"),
            color=alt.Color(
                "Focus_Area:N",
                title="Focus Area",
                scale=alt.Scale(scheme="set2"),
            ),
            tooltip=[
                alt.Tooltip("Focus_Area:N", title="Focus Area"),
                alt.Tooltip("Total_Treatments:Q", title="Treatments"),
            ],
        )
        .properties(height=300)
    )
    return chart


# ----------------------------
# Branding header
# ----------------------------
st.title("Psychedelic Practitioners Network")
st.subheader("Clinical Wisdom Trust & Research Database")
st.caption("Prototype tool for clinicians to search, compare, and record treatment notes. Uses synthetic data only.")


# ----------------------------
# Sidebar: Logo + Navigation + Filters
# ----------------------------
with st.sidebar:
    st.image(LOGO_PATH, use_container_width=True)

    st.header("Navigation")
    page = st.radio(
        "Go to",
        ["Login", "Search Database", "Add New Record"],
        index=0,
        label_visibility="collapsed",
    )

    st.divider()

    if is_logged_in():
        st.success("Logged in")
        if st.button("Log out"):
            st.session_state["logged_in"] = False
            st.rerun()
    else:
        st.info("Not logged in")

    focus_selected = None
    chemical_selected = None
    min_success_rating = 1

    if page == "Search Database":
        st.divider()
        st.subheader("Filter by Category")

        focus_selected = st.multiselect(
            "Focus Area",
            options=FOCUS_AREAS,
            default=FOCUS_AREAS,
            help="Pick one or more focus areas. Leave all selected to show everything.",
            key="filter_focus",
        )

        chemical_selected = st.multiselect(
            "Chemical",
            options=CHEMICALS,
            default=CHEMICALS,
            help="Pick one or more chemicals. Leave all selected to show everything.",
            key="filter_chemical",
        )

        min_success_rating = st.slider(
            "Minimum Rating",
            min_value=1,
            max_value=5,
            value=1,
            help="If you set this to 4, you will only see records rated 4 or 5.",
            key="filter_min_rating",
        )


# ----------------------------
# Load data
# ----------------------------
df = load_data(CSV_PATH)

if not os.path.exists(CSV_PATH):
    st.warning(
        "I could not find 'seed_data.csv' in this folder. The app is using a small built-in sample dataset. "
        "If you add a record, the app will create 'seed_data.csv' and save it."
    )


# ----------------------------
# Page 1: Login
# ----------------------------
if page == "Login":
    st.subheader("Login")

    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Username", value="", help="Prototype login only.")
        password = st.text_input("Password", value="", type="password", help="Prototype login only.")
        submitted = st.form_submit_button("Log in")

    if submitted:
        if username == "admin" and password == "password":
            st.session_state["logged_in"] = True
            st.success("Login successful. You can now use the database.")
        else:
            st.session_state["logged_in"] = False
            st.error("Login failed. Please check your username and password.")

    st.divider()
    st.write("Tip: For this prototype, use Username = admin and Password = password.")


# ----------------------------
# Page 2: Search Database (color-coded charts)
# ----------------------------
elif page == "Search Database":
    require_login()
    st.subheader("Search Database")

    st.write("Type a word like PTSD, Ketamine, MDMA, Cannabis, a client ID, or a practitioner name.")
    query = st.text_input(
        "Search",
        value="",
        placeholder="Example: PTSD, Cannabis, P-1024, Dr. Smith",
        help="This searches across all fields in the results.",
        key="main_search",
    )

    filtered_df = search_filter(df, query)
    filtered_df = apply_sidebar_filters(filtered_df, focus_selected, chemical_selected, min_success_rating)

    total_found = int(len(filtered_df))
    avg_rating = float(filtered_df["Treatment_Outcome_Rating"].mean()) if total_found > 0 else 0.0

    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        st.metric("Total records found", f"{total_found}")
    with c2:
        st.metric("Average success rating", f"{avg_rating:.2f}" if total_found > 0 else "0.00")
    with c3:
        st.caption("Results reflect your text search and your sidebar filters.")

    st.divider()

    if total_found == 0:
        st.warning("No records found matching your criteria.")
        st.stop()

    enable_altair_dark_theme()

    st.subheader("Analytics")
    left, right = st.columns(2)

    with left:
        st.altair_chart(
            build_avg_outcome_by_chemical_chart(filtered_df),
            use_container_width=True,
        )
    with right:
        st.altair_chart(
            build_treatments_by_focus_area_chart(filtered_df),
            use_container_width=True,
        )

    st.download_button(
        label="📥 Download Search Results as CSV",
        data=df_to_csv_bytes(filtered_df),
        file_name="ppn_search_results.csv",
        mime="text/csv",
        help="Downloads the exact results you are currently seeing (after search and filters).",
    )

    st.divider()

    st.subheader("Results Table")
    st.dataframe(
        format_for_display(filtered_df),
        use_container_width=True,
        hide_index=True,
    )

    st.divider()
    st.subheader("Patient Drill-Down")
    st.write("Select a Client ID to view full details.")

    client_ids = sorted(filtered_df["Client_ID"].astype(str).dropna().unique().tolist())
    select_options = ["Select a Client ID to view full details."] + client_ids

    chosen = st.selectbox(
        "Client ID",
        options=select_options,
        index=0,
        label_visibility="collapsed",
        help="This list is based on your current search results.",
        key="drilldown_client",
    )

    if chosen != select_options[0]:
        row = pick_best_row_for_client(filtered_df, chosen)

        header_cols = st.columns(4)
        header_cols[0].metric("Client ID", safe_str(row.get("Client_ID")))
        header_cols[1].metric("Age", safe_str(row.get("Patient_Age")))
        header_cols[2].metric("Sex", safe_str(row.get("Patient_Sex")))
        header_cols[3].metric("Focus Area", safe_str(row.get("Focus_Area")))

        protocol_cols = st.columns(5)
        protocol_cols[0].metric("Chemical", safe_str(row.get("Chemical_Used")))
        protocol_cols[1].metric("Dosage (mg)", safe_str(row.get("Dosage_Mg")))
        protocol_cols[2].metric("Intake Form", safe_str(row.get("Intake_Form")))
        protocol_cols[3].metric("Outcome Rating", safe_str(row.get("Treatment_Outcome_Rating")))

        tdate = row.get("Treatment_Date")
        if pd.notna(tdate) and hasattr(tdate, "strftime"):
            tdate_str = tdate.strftime("%Y-%m-%d")
        else:
            tdate_str = safe_str(tdate)
        protocol_cols[4].metric("Treatment Date", tdate_str)

        st.divider()
        st.markdown("#### Protocol Description")
        st.write(safe_str(row.get("Protocol_Description")))

        st.markdown("#### Clinical Notes")
        st.markdown("**Detailed Results**")
        st.write(safe_str(row.get("Detailed_Results")))

        st.markdown("**Next Steps**")
        st.write(safe_str(row.get("Next_Steps")))


# ----------------------------
# Page 3: Add New Record (Cannabis preserved)
# ----------------------------
elif page == "Add New Record":
    require_login()
    st.subheader("Add New Record")
    st.write("This form permanently appends a new row into seed_data.csv on your computer.")

    with st.expander("Add New Record", expanded=True):
        with st.form("add_record_form"):
            top1, top2, top3 = st.columns(3)
            with top1:
                practitioner = st.text_input(
                    "Practitioner Name",
                    placeholder="Example: Dr. A. Smith",
                    help="Use a consistent naming style so searches work well.",
                )
            with top2:
                client_id = st.text_input(
                    "Client ID",
                    placeholder="Example: P-1234",
                    help="Use an anonymous code. Do not use real names.",
                )
            with top3:
                treatment_date = st.date_input(
                    "Treatment Date",
                    value=date.today(),
                    help="When the treatment session took place.",
                )

            st.divider()

            r1c1, r1c2 = st.columns(2)
            with r1c1:
                age = st.number_input(
                    "Patient Age",
                    min_value=21,
                    max_value=75,
                    value=35,
                    step=1,
                    help="Whole number only.",
                )
            with r1c2:
                sex = st.selectbox(
                    "Sex",
                    SEX_OPTIONS,
                    help="Choose the option that best matches the record.",
                )

            r2c1, r2c2 = st.columns(2)
            with r2c1:
                focus_area = st.selectbox(
                    "Focus Area",
                    FOCUS_AREAS,
                    help="Used for filtering and analytics charts.",
                )
            with r2c2:
                chemical = st.selectbox(
                    "Chemical Used",
                    CHEMICALS,
                    help="Used for filtering and analytics charts.",
                )

            r3c1, r3c2 = st.columns(2)
            with r3c1:
                dosage = st.number_input(
                    "Dosage (mg)",
                    min_value=0,
                    max_value=2000,
                    value=25,
                    step=1,
                    help="Whole number only. Use 0 if unknown.",
                )
            with r3c2:
                intake_form = st.selectbox(
                    "Intake Form",
                    INTAKE_FORMS,
                    help="How the chemical was taken.",
                )

            st.divider()

            protocol = st.text_area(
                "Protocol Description",
                placeholder="Example: Preparation, session structure, monitoring, and integration approach.",
                height=90,
                help="Short description of the method used.",
            )
            detailed = st.text_area(
                "Detailed Results",
                placeholder="Example: Key clinical observations, patient-reported outcomes, adverse events.",
                height=140,
                help="Write full notes here so they read well in the drill-down view.",
            )
            next_steps = st.text_input(
                "Next Steps",
                placeholder="Example: Follow up in 2 weeks, integration therapy scheduled.",
                help="Short plan for follow-up and integration.",
            )
            outcome = st.slider(
                "Treatment Outcome Rating (1 to 5)",
                min_value=1,
                max_value=5,
                value=4,
                help="1 = No effect, 5 = Highly successful.",
            )

            submitted = st.form_submit_button("Submit")

        if submitted:
            if not practitioner.strip():
                st.error("Please fill in Practitioner Name.")
                st.stop()
            if not client_id.strip():
                st.error("Please fill in Client ID.")
                st.stop()

            record = {
                "Practitioner_Name": practitioner.strip(),
                "Client_ID": client_id.strip(),
                "Treatment_Date": str(treatment_date),
                "Patient_Age": int(age),
                "Patient_Sex": sex,
                "Focus_Area": focus_area,
                "Chemical_Used": chemical,
                "Dosage_Mg": int(dosage),
                "Intake_Form": intake_form,
                "Protocol_Description": (protocol or "").strip(),
                "Treatment_Outcome_Rating": int(outcome),
                "Detailed_Results": (detailed or "").strip(),
                "Next_Steps": (next_steps or "").strip(),
            }

            try:
                append_record_to_csv(CSV_PATH, record)
                clear_data_cache()
                st.success("✅ Record successfully added to the PPN Database!")
                st.caption(f"Saved to: {os.path.abspath(CSV_PATH)}")

                st.dataframe(
                    pd.DataFrame([record], columns=REQUIRED_COLS),
                    use_container_width=True,
                    hide_index=True,
                )
                st.rerun()

            except PermissionError:
                st.error("I could not save because the file looks busy or open.")
                st.write("If seed_data.csv is open in another program (like Excel), close it and try again.")
                st.caption(f"File path: {os.path.abspath(CSV_PATH)}")

            except OSError as e:
                st.error("I could not save the record due to a file problem.")
                st.write("Please make sure you can write to this folder, then try again.")
                st.caption(f"Details: {e}")

            except Exception as e:
                st.error("I could not save the record due to an unexpected error.")
                st.caption(f"Details: {e}")
