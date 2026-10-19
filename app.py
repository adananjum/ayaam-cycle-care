import streamlit as st
from datetime import date, timedelta, datetime
from statistics import mean, stdev

# ---------------- PAGE SETUP ----------------
st.set_page_config(
    page_title="AYAAM | Cycle Care",
    page_icon="🌸",
    layout="wide"
)



# ---------------- DESIGN ----------------
st.markdown("""
<style>

/* Main page */
.stApp {
    background-color: #FFFDFD;
    color: #382D32;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #FFF1F4 !important;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
    color: #54283B !important;
}

/* Sidebar headings */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #873F59 !important;
}

/* Main headings */
h1, h2, h3 {
    color: #873F59 !important;
}

/* Normal text */
.stApp p,
.stApp label {
    color: #382D32;
}

/* FIX: Metric cards on the Home page */
[data-testid="stMetric"] {
    background-color: #FCE4EC !important;
    padding: 20px !important;
    border-radius: 16px !important;
    border: 1px solid #F3C4D3 !important;
    box-shadow: 0 3px 10px rgba(135, 63, 89, 0.08);
}

/* Card labels: Designed for, Core focus, Built around */
[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] p,
[data-testid="stMetricLabel"] label {
    color: #873F59 !important;
    font-size: 15px !important;
    font-weight: 600 !important;
}

/* Card values: You, Cycle care, Privacy */
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] div {
    color: #54283B !important;
    font-size: 28px !important;
    font-weight: 700 !important;
}

/* Buttons */
.stButton > button {
    background-color: #B85C78 !important;
    color: #FFFFFF !important;
    border-radius: 10px;
    border: none;
    padding: 0.55rem 1rem;
}

/* Button hover */
.stButton > button:hover {
    background-color: #923F5D !important;
    color: #FFFFFF !important;
}

/* Input fields */
.stTextInput input,
.stTextArea textarea {
    background-color: #FFFFFF !important;
    color: #382D32 !important;
    border: 1px solid #E8B8C8 !important;
}

/* Dropdowns and select controls */
.stSelectbox div[data-baseweb="select"] {
    background-color: #FFFFFF;
}

/* Info messages */
[data-testid="stAlert"] {
    border-radius: 12px;
}

/* Consistent rounded cards and containers */
div[data-testid="stExpander"] {
    border-radius: 12px;
    border-color: #F3C4D3;
}

</style>
""", unsafe_allow_html=True)


# ---------------- CYCLE LOGIC ----------------
def cycle_lengths(start_dates):
    dates = sorted(start_dates)
    return [
        (dates[i + 1] - dates[i]).days
        for i in range(len(dates) - 1)
    ]


def predict_next_period(start_dates, typical_cycle=28):
    dates = sorted(set(start_dates))

    if not dates:
        return None

    lengths = cycle_lengths(dates)

    # Reject impossible or suspicious cycle intervals
    if any(length < 10 or length > 90 for length in lengths):
        return {"error": "Please check your dates. One or more cycle intervals look unusual."}

    # Use the user's history when there is enough information
    if len(lengths) >= 2:
        recent = lengths[-6:]
        average = mean(recent)
        variation = stdev(recent) if len(recent) >= 2 else 3
        based_on = "Your recorded cycle history"
    else:
        average = typical_cycle
        variation = 3
        based_on = "Your selected typical cycle length"

    predicted = dates[-1] + timedelta(days=round(average))
    margin = max(2, round(variation))

    return {
        "predicted_start": predicted,
        "earliest": predicted - timedelta(days=margin),
        "latest": predicted + timedelta(days=margin),
        "avg_cycle_length": round(average, 1),
        "variation_days": round(variation, 1),
        "is_irregular": variation > 4,
        "based_on": based_on,
    }


def estimate_ovulation(predicted_start):
    ovulation = predicted_start - timedelta(days=14)
    return {
        "ovulation": ovulation,
        "fertile_start": ovulation - timedelta(days=5),
        "fertile_end": ovulation + timedelta(days=1),
    }


# ---------------- SESSION DATA ----------------
if "symptom_logs" not in st.session_state:
    st.session_state.symptom_logs = []

if "prediction" not in st.session_state:
    st.session_state.prediction = None

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("# 🌸 AYAAM")
st.sidebar.caption("Private, intelligent cycle care")
page = st.sidebar.radio(
    "Navigate",
    ["Home", "Cycle Tracker", "Daily Journal", "Ramadan Planner", "About AYAAM"]
)

st.sidebar.divider()
st.sidebar.caption("Prototype demo • Use fictional data during presentations")

# ---------------- HOME ----------------
if page == "Home":
    st.title("Your wellbeing, understood.")
    st.write(
        "A calmer, more personal way to understand your cycle, "
        "notice patterns and prepare for the days ahead."
    )

    st.info(
        "Welcome to AYAAM. Start by entering period dates in Cycle Tracker "
        "to see an example prediction."
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Designed for", "You")
    col2.metric("Core focus", "Cycle care")
    col3.metric("Built around", "Privacy")

    st.subheader("Your cycle-care space")
    a, b = st.columns(2)

    with a:
        st.markdown("### 🌷 Understand")
        st.write("Explore cycle estimates and learn from recorded dates.")

        st.markdown("### 📝 Reflect")
        st.write("Record symptoms, mood, energy and sleep.")

    with b:
        st.markdown("### 🔒 Protect")
        st.write("Privacy is a core design goal for AYAAM.")

        st.markdown("### 🌙 Belong")
        st.write("Explore optional planning tools shaped around local needs.")

    st.caption(
        "Cycle estimates are not medical diagnoses or reliable contraception. "
        "This demonstration is not a validated medical product."
    )

# ---------------- CYCLE TRACKER ----------------
elif page == "Cycle Tracker":
    st.title("🌸 Cycle Tracker")
    st.write("Enter previous period start dates, from oldest to newest.")

    st.caption(
        "Demo example dates are provided below. Replace them with fictional "
        "or test dates to explore the prototype."
    )

    today = date.today()
    defaults = [
        today - timedelta(days=85),
        today - timedelta(days=57),
        today - timedelta(days=29),
    ]

    date_text = st.text_input(
        "Period start dates (YYYY-MM-DD, separated by commas)",
        value=", ".join(d.isoformat() for d in defaults)
    )

    typical_cycle = st.selectbox(
        "Typical cycle length, if you have limited history",
        [21, 24, 26, 28, 30, 32, 35]
    )

    if st.button("Calculate my estimate"):
        try:
            entered_dates = [
                datetime.strptime(x.strip(), "%Y-%m-%d").date()
                for x in date_text.split(",")
                if x.strip()
            ]

            if any(d > today for d in entered_dates):
                st.error("Please don't enter future period start dates.")
            elif len(set(entered_dates)) != len(entered_dates):
                st.error("There are duplicate dates. Please check your entries.")
            elif len(entered_dates) < 1:
                st.error("Please enter at least one period start date.")
            else:
                st.session_state.prediction = predict_next_period(
                    entered_dates, typical_cycle
                )

        except ValueError:
            st.error("Use YYYY-MM-DD format, for example 2026-08-15.")

    result = st.session_state.prediction

    if result:
        if "error" in result:
            st.error(result["error"])
        else:
            st.divider()
            st.subheader("Your estimated cycle overview")

            c1, c2, c3 = st.columns(3)
            c1.metric("Estimated next period", result["predicted_start"].strftime("%d %b %Y"))
            c2.metric("Average cycle length", f"{result['avg_cycle_length']} days")
            c3.metric(
                "Estimated date range",
                f"{result['earliest'].strftime('%d %b')} – {result['latest'].strftime('%d %b')}"
            )

            ov = estimate_ovulation(result["predicted_start"])

            st.markdown("### Estimated cycle milestones")
            st.write(f"🌷 Possible period window: {result['earliest']} to {result['latest']}")
            st.write(f"🌼 Estimated ovulation: {ov['ovulation']}")
            st.write(f"💗 Estimated fertile window: {ov['fertile_start']} to {ov['fertile_end']}")

            st.caption(f"Estimate based on: {result['based_on']}.")

            if result["is_irregular"]:
                st.warning(
                    "Your recorded cycle lengths vary. These estimates may be less reliable."
                )

            st.info(
                "Ovulation timing can vary substantially. These dates are rough estimates "
                "and should not be used to prevent pregnancy or diagnose a condition."
            )

# ---------------- DAILY JOURNAL ----------------
elif page == "Daily Journal":
    st.title("📝 Daily Journal")
    st.write("A gentle space to record how you're feeling today.")

    log_date = st.date_input("Date", value=date.today())

    symptoms = st.multiselect(
        "Physical symptoms",
        ["Cramps", "Bloating", "Headache", "Fatigue", "Skin changes", "Tender breasts"]
    )

    mood = st.selectbox(
        "Mood",
        ["Choose mood", "Calm", "Happy", "Anxious", "Irritable", "Low", "Tearful"]
    )

    energy = st.select_slider(
        "Energy level",
        options=["Very low", "Low", "Moderate", "High", "Very high"],
        value="Moderate"
    )

    sleep = st.select_slider(
        "Sleep quality",
        options=["Poor", "Fair", "Good", "Very good"],
        value="Good"
    )

    notes = st.text_area("Optional notes")

    if st.button("Save journal entry"):
        st.session_state.symptom_logs.append({
            "date": str(log_date),
            "symptoms": symptoms,
            "mood": mood,
            "energy": energy,
            "sleep": sleep,
            "notes": notes
        })
        st.success("Your entry has been added to this demo session.")

    st.divider()
    st.subheader("Recent entries")

    if st.session_state.symptom_logs:
        for entry in reversed(st.session_state.symptom_logs):
            with st.expander(f"Journal entry — {entry['date']}"):
                st.write("Symptoms:", ", ".join(entry["symptoms"]) or "None selected")
                st.write("Mood:", entry["mood"])
                st.write("Energy:", entry["energy"])
                st.write("Sleep:", entry["sleep"])
                if entry["notes"]:
                    st.write("Notes:", entry["notes"])
    else:
        st.caption("Your journal entries will appear here during this session.")

    st.caption("Demo entries are held in session memory, not securely stored.")

# ---------------- RAMADAN PLANNER ----------------
elif page == "Ramadan Planner":
    st.title("🌙 Ramadan Planner")
    st.write(
        "An example of AYAAM's optional faith-aware planning tools. "
        "This screen demonstrates the concept; it does not automatically "
        "determine religious obligations."
    )

    st.markdown("### Personal planning")
    missed = st.number_input(
        "Missed fasts you want to plan for",
        min_value=0,
        max_value=365,
        value=0,
        step=1
    )

    completed = st.number_input(
        "Fasts already completed",
        min_value=0,
        max_value=365,
        value=0,
        step=1
    )

    remaining = max(0, missed - completed)

    st.metric("Remaining in your plan", remaining)

    st.write(
        "You can use this space to organise personal reminders and plan "
        "ahead. For religious rulings, consult a trusted qualified scholar."
    )

# ---------------- ABOUT ----------------
elif page == "About AYAAM":
    st.title("About AYAAM")
    st.subheader("Private, intelligent cycle care")
    st.write(
        "AYAAM is a women’s health app concept designed to help women "
        "understand cycle patterns in a way that is private, accessible "
        "and relevant to their lives."
    )

    st.markdown("### Our three pillars")
    st.markdown("""
    - **Understand:** cycle estimates and daily symptom records.
    - **Protect:** privacy-first design as a product goal.
    - **Belong:** local languages and optional cultural planning.
    """)

    st.markdown("### Future vision")
    st.write(
        "Future development may include multilingual health education, "
        "stronger privacy controls, expanded life-stage modes and "
        "a private AI assistant."
    )

    st.warning(
        "This is an early demonstration, not a production-ready medical app. "
        "Authentication, encryption, durable storage and AI features have "
        "not been implemented in this prototype."
    )

st.divider()
st.caption("AYAAM • Early prototype for concept demonstration")
