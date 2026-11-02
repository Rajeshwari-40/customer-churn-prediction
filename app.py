import os
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Churn Analytics", page_icon="📉", layout="wide")

TEAL, CORAL, NAVY, SLATE = "#14b8a6", "#f43f5e", "#0f172a", "#64748b"
CHURN_COLORS = {"No": TEAL, "Yes": CORAL}

# ---------------- ಸ್ಟೈಲ್ (CSS) ----------------
st.markdown(f"""
<style>
.block-container {{padding-top: 1.5rem; padding-bottom: 2rem;}}
.hero {{
    background: linear-gradient(135deg, {NAVY} 0%, #1e3a5f 60%, #0f766e 100%);
    padding: 28px 34px; border-radius: 18px; color: white; margin-bottom: 22px;
}}
.hero h1 {{margin: 0; font-size: 2.1rem; color: white;}}
.hero p {{margin: 6px 0 0 0; color: #cbd5e1; font-size: 1rem;}}
.kpi {{
    background: white; border-radius: 14px; padding: 18px 20px;
    box-shadow: 0 2px 12px rgba(15, 23, 42, 0.08);
}}
.kpi-label {{color: {SLATE}; font-size: 0.85rem; font-weight: 600;
            text-transform: uppercase; letter-spacing: 0.04em;}}
.kpi-value {{color: {NAVY}; font-size: 2rem; font-weight: 700; line-height: 1.2;}}
.kpi-sub {{color: {SLATE}; font-size: 0.8rem;}}
.insight {{
    background: #f0fdfa; border-left: 5px solid {TEAL}; padding: 14px 18px;
    border-radius: 10px; color: {NAVY}; margin-bottom: 10px;
}}
.stTabs [data-baseweb="tab"] {{font-weight: 600; font-size: 1rem;}}
</style>
""", unsafe_allow_html=True)


def kpi(col, label, value, sub, color):
    col.markdown(
        f"""<div class="kpi" style="border-left: 6px solid {color};">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div></div>""",
        unsafe_allow_html=True,
    )


def style(fig, height=380):
    fig.update_layout(
        template="plotly_white", height=height,
        margin=dict(l=10, r=10, t=50, b=10),
        title_font=dict(size=16, color=NAVY),
        legend=dict(orientation="h", y=1.12, x=0),
    )
    return fig


@st.cache_data
def load():
    return pd.read_csv("telco_scored.csv")


df = load()

# ---------------- ಹೆಡರ್ ----------------
st.markdown("""
<div class="hero">
  <h1>📉 Customer Churn Analytics</h1>
  <p>AI-powered insights to find at-risk customers early and protect revenue.</p>
</div>
""", unsafe_allow_html=True)

# ---------------- ಫಿಲ್ಟರ್‌ಗಳು ----------------
st.sidebar.header("🔎 Filters")
contract = st.sidebar.multiselect("Contract", sorted(df["Contract"].unique()),
                                  default=sorted(df["Contract"].unique()))
payment = st.sidebar.multiselect("Payment Method", sorted(df["PaymentMethod"].unique()),
                                 default=sorted(df["PaymentMethod"].unique()))
internet = st.sidebar.multiselect("Internet Service", sorted(df["InternetService"].unique()),
                                  default=sorted(df["InternetService"].unique()))
threshold = st.sidebar.slider("High-risk threshold", 0.30, 0.95, 0.70, 0.05)

f = df[df["Contract"].isin(contract)
       & df["PaymentMethod"].isin(payment)
       & df["InternetService"].isin(internet)]

if f.empty:
    st.warning("No customers match these filters. Please select at least one option in each filter.")
    st.stop()

high_risk = f[f["ChurnProb"] > threshold]
lost = f.loc[f["ChurnFlag"] == 1, "MonthlyCharges"].sum()
at_risk = high_risk["MonthlyCharges"].sum()

# ---------------- KPI ಕಾರ್ಡ್‌ಗಳು ----------------
c1, c2, c3, c4 = st.columns(4)
kpi(c1, "Total Customers", f"{len(f):,}", "In current selection", "#3b82f6")
kpi(c2, "Churn Rate", f"{f['ChurnFlag'].mean() * 100:.1f}%", "Customers who left", CORAL)
kpi(c3, "Monthly Revenue Lost", f"${lost:,.0f}", "From churned customers", "#f59e0b")
kpi(c4, "High-Risk Customers", f"{len(high_risk):,}", f"${at_risk:,.0f}/month at risk", TEAL)

st.write("")

# ---------------- ಟ್ಯಾಬ್‌ಗಳು ----------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Overview", "🔍 Churn Drivers", "🚨 High-Risk Customers", "🧠 Model Insights"])


def rate_by(col):
    return f.groupby(col)["ChurnFlag"].mean().mul(100).reset_index(name="Churn %")

with tab1:
    a, b = st.columns([1, 1.4])
    with a:
        fig = px.pie(f, names="Churn", hole=0.6, color="Churn",
                     color_discrete_map=CHURN_COLORS, title="Customers: Stayed vs Churned")
        fig.update_traces(textinfo="percent", textfont_size=16)
        fig.update_layout(legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center"))
        st.plotly_chart(style(fig), use_container_width=True)
    with b:
        fig = px.bar(rate_by("Contract"), x="Contract", y="Churn %", text_auto=".1f",
                     color_discrete_sequence=[CORAL], title="Churn Rate by Contract (%)")
        st.plotly_chart(style(fig), use_container_width=True)

    top = rate_by("Contract").sort_values("Churn %", ascending=False).iloc[0]
    st.markdown(
        f"""<div class="insight">💡 <b>Insight:</b> <b>{top['Contract']}</b> customers churn the most
        ({top['Churn %']:.1f}%). Offering discounts for longer contracts can reduce churn.</div>""",
        unsafe_allow_html=True)

with tab2:
    a, b = st.columns(2)
    with a:
        order = ["0-12", "13-24", "25-48", "49-72"]
        fig = px.bar(rate_by("TenureGroup"), x="TenureGroup", y="Churn %", text_auto=".1f",
                     category_orders={"TenureGroup": order},
                     color_discrete_sequence=[CORAL], title="Churn Rate by Tenure (months)")
        st.plotly_chart(style(fig), use_container_width=True)
    with b:
        fig = px.box(f, x="Churn", y="MonthlyCharges", color="Churn",
                     color_discrete_map=CHURN_COLORS, title="Monthly Charges vs Churn")
        st.plotly_chart(style(fig), use_container_width=True)

    a, b = st.columns(2)
    with a:
        fig = px.bar(rate_by("PaymentMethod"), x="Churn %", y="PaymentMethod", orientation="h",
                     text_auto=".1f", color_discrete_sequence=["#6366f1"],
                     title="Churn Rate by Payment Method (%)")
        st.plotly_chart(style(fig), use_container_width=True)
    with b:
        fig = px.bar(rate_by("InternetService"), x="InternetService", y="Churn %",
                     text_auto=".1f", color_discrete_sequence=["#f59e0b"],
                     title="Churn Rate by Internet Service (%)")
        st.plotly_chart(style(fig), use_container_width=True)

with tab3:
    st.markdown(
        f"""<div class="insight">🎯 <b>{len(high_risk):,}</b> customers have churn probability above
        <b>{threshold:.0%}</b>. Contact them first with retention offers.</div>""",
        unsafe_allow_html=True)
    risk = (high_risk.sort_values("ChurnProb", ascending=False)
            [["customerID", "Contract", "tenure", "MonthlyCharges", "ChurnProb"]])
    st.dataframe(
        risk.head(100), use_container_width=True, hide_index=True,
        column_config={
            "ChurnProb": st.column_config.ProgressColumn(
                "Churn Risk", min_value=0.0, max_value=1.0, format="%.2f"),
            "MonthlyCharges": st.column_config.NumberColumn("Monthly ($)", format="$%.2f"),
            "tenure": "Tenure (months)",
        })
    st.download_button("⬇️ Download high-risk list (CSV)",
                       risk.to_csv(index=False), "high_risk_customers.csv", "text/csv")

with tab4:
    st.markdown("""<div class="insight">🧠 <b>Model:</b> XGBoost classifier, explained with SHAP.
    Features at the top influence churn the most.</div>""", unsafe_allow_html=True)
    a, b = st.columns(2)
    if os.path.exists("shap_summary.png"):
        a.image("shap_summary.png", caption="SHAP feature importance")
    if os.path.exists("eda.png"):
        b.image("eda.png", caption="Exploratory data analysis")

st.caption("Built with Python, XGBoost, SHAP, Plotly and Streamlit • Dataset: Telco Customer Churn (Kaggle)")
