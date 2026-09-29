"""Health & Welfare Carrier Benchmark — internal administrator tool.

Compares the four Toyota-group health & welfare plans' carrier lineups,
broker compensation, and insured-line cost proxy from DOL Form 5500
Schedule A filings (plan year 2024). Internal use only — not affiliated
with any carrier.
"""

import pandas as pd
import altair as alt
import streamlit as st

DATA_PATH = "data/hw_schedule_a_2024.csv"

BAR_COLOR = "#0e544c"
FEE_COLOR = "#7fb5a3"
GRAY = "#6b6259"
BAR_SIZE = 40

COMPANIES = {
    "woven": {
        "label": "Woven by Toyota, U.S.",
        "abbr": "Woven",
        "plan": "Health and Welfare Benefit Plan (501)",
        "participants": "529 / 511",
        "funding": "Mixed — insurance + general assets (partly self-insured)",
    },
    "tri": {
        "label": "Toyota Research Institute",
        "abbr": "TRI",
        "plan": "Health and Welfare Plan (501)",
        "participants": "261 / 282",
        "funding": "Fully insured",
    },
    "tcna": {
        "label": "Toyota Connected North America",
        "abbr": "TCNA",
        "plan": "Health and Welfare Plan (501)",
        "participants": "243 / 247",
        "funding": "Mixed — insurance + general assets (partly self-insured)",
    },
    "tmna": {
        "label": "Toyota Motor North America",
        "abbr": "TMNA",
        "plan": "Health and Welfare Benefit Plan (503)",
        "participants": "43,006 / 44,701",
        "funding": "Mixed — insurance + general assets (partly self-insured)",
    },
}

CARRIER_NAMES = {
    "CALIFORNIA PHYSICIANS SERVICE": "Blue Shield of California",
    "KAISER FOUNDATION HEALTH PLAN, INC.": "Kaiser Permanente",
    "KAISER FOUNDATION HEALTH PLAN INC": "Kaiser Permanente",
    "KAISER FOUNDATION HEALTH PLAN OF THE NORTHWEST": "Kaiser Permanente NW",
    "METROPOLITAN LIFE INSURANCE COMPANY": "MetLife",
    "METROPOLITAN GENERAL INSURANCE COMPANY": "MetLife",
    "METLIFE LEGAL PLANS": "MetLife Legal Plans",
    "VISION SERVICE PLAN": "VSP",
    "NATIONAL UNION FIRE INSURANCE COMPANY OF PITTSBURGH, PA": "AIG (National Union Fire)",
    "FOUR EVER LIFE INSURANCE COMPANY": "Four Ever Life",
    "FOUR EVER LIFE INS CO.": "Four Ever Life",
    "HAWAII MEDICAL SERVICE ASSOCIATION": "HMSA",
    "MODERN HEALTH": "Modern Health",
    "UNUM LIFE INSURANCE COMPANY OF AMERICA": "Unum",
    "UNUM INSURANCE COMPANY": "Unum",
    "DELTA DENTAL OF CALIFORNIA": "Delta Dental",
    "ACE AMERICAN INSURANCE COMPANY": "Chubb (ACE American)",
    "PRE-PAID LEGAL SERVICES, INC DBA LEGALSHIELD": "LegalShield",
    "UNITEDHEALTHCARE INSURANCE COMPANY": "UnitedHealthcare",
    "HEALTH ADVOCATE SOLUTIONS, INC.": "Health Advocate",
    "DEARBORN LIFE INSURANCE COMPANY": "Dearborn",
    "BLUECROSS BLUESHIELD OF TEXAS": "BCBS of Texas",
    "SECURIAN LIFE INSURANCE COMPANY": "Securian",
    "THE PRUDENTIAL INSURANCE COMPANY OF AMERICA": "Prudential",
    "ARAG SERVICES, LLC": "ARAG",
    "AMERICAN HERITAGE LIFE INSURANCE COMPANY": "American Heritage (Allstate)",
    "LINCOLN NATIONAL LIFE INSURANCE COMPANY": "Lincoln Financial",
    "EMPATHIA, INC.": "Empathia",
}

BENEFIT_NAMES = {
    "HEALTH/DRUG/PPO": "Medical (PPO)",
    "HEALTH/DRUG/HMO": "Medical (HMO)",
    "HEALTH": "Medical",
    "HEALTH/DENTAL/VISION/DRUG": "Medical / Dental / Vision",
    "HEALTH/DENTAL/VISION/LIFE_INSUR/DRUG/PPO/OTHER (ACCIDENTAL DEATH AND DISMEMBERMENT)":
        "Medical / Dental / Vision / Life",
    "DENTAL": "Dental",
    "VISION": "Vision",
    "LIFE_INSUR": "Life insurance",
    "LIFE_INSUR/TEMP_DISAB/LONG_TERM_DISAB/OTHER (ACCIDENTAL DEATH AND DISMEMBERMENT, EMPLOYEE ASSISTANCE PROGRAM)":
        "Life / Disability / EAP",
    "VISION/LIFE_INSUR/TEMP_DISAB/LONG_TERM_DISAB/OTHER (ACCIDENTAL DEATH AND DISMEMBERMENT, ACCIDENT, CRITICAL ILLNESS)":
        "Life / Disability / Vision",
    "LONG_TERM_DISAB": "Long-term disability",
    "OTHER (LEGAL)": "Legal",
    "OTHER (EMPLOYEE ASSISTANCE PROGRAM)": "EAP",
    "OTHER (BUSINESS TRAVEL ACCIDENT)": "Business travel accident",
    "OTHER (AD&D)": "AD&D",
    "OTHER (HOSPITAL EE PAID)": "Hospital indemnity (employee-paid)",
    "OTHER (GROUP ACCIDENT)": "Group accident",
    "OTHER (ATTAINED AGE CRITICAL ILLNESS)": "Critical illness",
}

CAVEATS = """**Data & caveats**
- Source: DOL Form 5500 Schedule A filings, plan year 2024 (calendar year; filings received in 2025/2026).
- Schedule A reports **insurance contracts only**. Self-insured portions (TMNA and TCNA core medical) leave no Schedule A trace and are invisible here.
- Earned-premium, claims-paid, and retention fields are **blank in the source filings**. "Charges paid" is the amount paid to the carrier and is used here as a cost proxy for insured lines — it is not a filed premium and does not split employer vs employee share.
- Per-covered-life figures = charges paid ÷ persons covered at year-end. Covered lives typically include dependents; figures reflect each plan's enrolled mix and design, not a normalized benchmark rate.
- Broker compensation shows **amounts only** — the dataset carries no broker names.
- Form 5500 does **not** disclose: deductibles, out-of-pocket max, coinsurance, employee premium share, employer HSA contributions, provider networks, or plan design quality.
"""


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df["carrier"] = df["insurer_name"].map(
        lambda n: CARRIER_NAMES.get(n, n.title()))
    df["coverage"] = df["benefit_type"].map(
        lambda b: BENEFIT_NAMES.get(b, b.replace("_", " ").title()))
    df["company_label"] = df["company"].map(lambda c: COMPANIES[c]["label"])
    df["abbr"] = df["company"].map(lambda c: COMPANIES[c]["abbr"])
    return df


def money(x):
    if pd.isna(x):
        return "—"
    return f"${x:,.0f}"


def caveats():
    with st.expander("Data & caveats"):
        st.markdown(CAVEATS)


st.set_page_config(page_title="H&W Carrier Benchmark", layout="wide")
st.title("Health & Welfare Carrier Benchmark")
st.caption("Internal administrator tool · DOL Form 5500 Schedule A, plan year 2024")

df = load_data()

tab_lineup, tab_broker, tab_cost = st.tabs(
    ["Carrier lineup", "Broker compensation", "Cost proxy"])

# ------------------------------------------------------------ Carrier lineup
with tab_lineup:
    st.subheader("Carrier lineup")
    choice = st.selectbox(
        "Company",
        options=list(COMPANIES.keys()),
        format_func=lambda c: COMPANIES[c]["label"],
    )
    meta = COMPANIES[choice]
    c1, c2, c3 = st.columns(3)
    c1.metric("Plan", meta["plan"])
    c2.metric("Participants (BOY / active)", meta["participants"])
    c3.metric("Funding arrangement", meta["funding"])

    sub = df[df["company"] == choice].copy().sort_values("charges_paid", ascending=False)
    if choice == "tcna":
        st.info("No medical carrier rows for this plan — core medical is self-insured "
                "and leaves no Schedule A trace.")
    if choice == "tmna":
        st.info("Only ~1,260 Kaiser HMO lives appear here for 44,701 active participants — "
                "core medical is self-insured and leaves no Schedule A trace.")

    tbl = pd.DataFrame(
        {
            "Carrier": sub["carrier"],
            "Coverage": sub["coverage"],
            "Covered lives": sub["persons_covered"].map(lambda x: f"{int(x):,}"),
            "Charges paid": sub["charges_paid"].map(money),
            "Commissions": sub["commissions_paid"].map(money),
            "Fees": sub["fees_paid"].map(money),
        }
    )
    st.dataframe(tbl, use_container_width=True, hide_index=True)
    st.caption("Charges paid = amount paid to the carrier in 2024 (filed fact). "
               "Commissions/fees = broker compensation reported on Schedule A.")
    caveats()

# ------------------------------------------------------- Broker compensation
with tab_broker:
    st.subheader("Broker compensation by company (2024)")
    agg = (df.groupby("company")[["commissions_paid", "fees_paid"]]
             .sum().reset_index())
    agg["abbr"] = agg["company"].map(lambda c: COMPANIES[c]["abbr"])
    agg["total"] = agg["commissions_paid"] + agg["fees_paid"]
    order = agg.sort_values("total", ascending=False)["abbr"].tolist()

    long = pd.melt(agg, id_vars=["abbr", "total"],
                   value_vars=["commissions_paid", "fees_paid"],
                   var_name="Type", value_name="Amount")
    long["Type"] = long["Type"].map({"commissions_paid": "Commissions",
                                     "fees_paid": "Fees"})
    stacked = (
        alt.Chart(long)
        .mark_bar(size=BAR_SIZE)
        .encode(
            x=alt.X("abbr:N", sort=order, title=None),
            y=alt.Y("Amount:Q", title="USD"),
            color=alt.Color("Type:N",
                            scale=alt.Scale(domain=["Commissions", "Fees"],
                                            range=[BAR_COLOR, FEE_COLOR]),
                            legend=alt.Legend(title=None)),
            tooltip=[alt.Tooltip("abbr:N", title="Company"),
                     alt.Tooltip("Type:N"),
                     alt.Tooltip("Amount:Q", format="$,.0f")],
        )
    )
    totals = (
        alt.Chart(agg)
        .mark_text(dy=-8, color="#2b2620", fontWeight=600, fontSize=12)
        .encode(
            x=alt.X("abbr:N", sort=order, title=None),
            y=alt.Y("total:Q"),
            text=alt.Text("total:Q", format="$,.0f"),
        )
    )
    st.altair_chart((stacked + totals).properties(height=320), use_container_width=True)
    st.caption("Broker names are not disclosed in the dataset — amounts only.")

    st.subheader("Broker compensation by carrier")
    detail = df.copy()
    detail["Total comp"] = detail["commissions_paid"] + detail["fees_paid"]
    detail = detail[detail["Total comp"] > 0].sort_values("Total comp", ascending=False)
    tbl2 = pd.DataFrame(
        {
            "Company": detail["abbr"],
            "Carrier": detail["carrier"],
            "Coverage": detail["coverage"],
            "Commissions": detail["commissions_paid"].map(money),
            "Fees": detail["fees_paid"].map(money),
            "Total": detail["Total comp"].map(money),
        }
    )
    st.dataframe(tbl2, use_container_width=True, hide_index=True)
    caveats()

# ---------------------------------------------------------------- Cost proxy
with tab_cost:
    st.subheader("Insured medical cost proxy (2024)")
    st.caption("Charges paid per covered life — usable as a premium proxy for insured "
               "medical lines only. Self-insured medical is invisible on Schedule A.")
    med = df[df["benefit_type"].str.contains("HEALTH") & (df["persons_covered"] > 0)].copy()
    med["per_life"] = med["charges_paid"] / med["persons_covered"]
    med["bar_label"] = med["abbr"] + " · " + med["carrier"] + " · " + \
        med["persons_covered"].map(lambda x: f"{int(x):,} lives")
    med = med.sort_values("per_life", ascending=False)

    bars = (
        alt.Chart(med)
        .mark_bar(color=BAR_COLOR, size=BAR_SIZE)
        .encode(
            x=alt.X("bar_label:N", sort=None, title=None,
                    axis=alt.Axis(labelAngle=-25)),
            y=alt.Y("per_life:Q", title="Charges paid per covered life (USD)"),
            tooltip=[alt.Tooltip("abbr:N", title="Company"),
                     alt.Tooltip("carrier:N", title="Carrier"),
                     alt.Tooltip("coverage:N", title="Coverage"),
                     alt.Tooltip("persons_covered:Q", title="Covered lives", format=",.0f"),
                     alt.Tooltip("charges_paid:Q", title="Charges paid", format="$,.0f"),
                     alt.Tooltip("per_life:Q", title="Per covered life", format="$,.0f")],
        )
    )
    labels = (
        alt.Chart(med)
        .mark_text(dy=-8, color="#2b2620", fontWeight=600, fontSize=12)
        .encode(
            x=alt.X("bar_label:N", sort=None),
            y=alt.Y("per_life:Q"),
            text=alt.Text("per_life:Q", format="$,.0f"),
        )
    )
    st.altair_chart((bars + labels).properties(height=340), use_container_width=True)

    tbl3 = pd.DataFrame(
        {
            "Company": med["abbr"],
            "Carrier": med["carrier"],
            "Coverage": med["coverage"],
            "Covered lives": med["persons_covered"].map(lambda x: f"{int(x):,}"),
            "Charges paid": med["charges_paid"].map(money),
            "$ per covered life": med["per_life"].map(money),
        }
    )
    st.dataframe(tbl3, use_container_width=True, hide_index=True)
    caveats()
