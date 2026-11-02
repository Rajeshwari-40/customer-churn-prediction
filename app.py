import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Churn Dashboard", layout="wide")
st.title("📉 Customer Churn Analytics Dashboard")

df = pd.read_csv("telco_scored.csv")

# ---------- ಫಿಲ್ಟರ್‌ಗಳು ----------
st.sidebar.header("Filters")
contract = st.sidebar.multiselect("Contract", df["Contract"].unique(),
                                  default=list(df["Contract"].unique()))
payment = st.sidebar.multiselect("Payment Method", df["PaymentMethod"].unique(),
                                 default=list(df["PaymentMethod"].unique()))
internet = st.sidebar.multiselect("Internet Service", df["InternetService"].unique(),
                                  default=list(df["InternetService"].unique()))
threshold = st.sidebar.slider("High-risk threshold", 0.3, 0.95, 0.7)

f = df[df["Contract"].isin(contract)
       & df["PaymentMethod"].isin(payment)
       & df["InternetService"].isin(internet)]

# ---------- KPI ಕಾರ್ಡ್‌ಗಳು ----------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Customers", f"{len(f):,}")
c2.metric("Churn Rate", f"{f['ChurnFlag'].mean() * 100:.1f}%")
c3.metric("Monthly Revenue Lost",
          f"${f.loc[f['ChurnFlag'] == 1, 'MonthlyCharges'].sum():,.0f}")
c4.metric("High-Risk Customers", int((f["ChurnProb"] > threshold).sum()))

# ---------- ಚಾರ್ಟ್‌ಗಳು ----------
left, right = st.columns(2)

with left:
    fig1 = px.histogram(f, x="Contract", color="Churn", barmode="group",
                        title="Churn by Contract")
    st.plotly_chart(fig1, use_container_width=True)

with right:
    fig2 = px.histogram(f, x="tenure", color="Churn", nbins=30,
                        title="Churn by Tenure (months)")
    st.plotly_chart(fig2, use_container_width=True)

left2, right2 = st.columns(2)

with left2:
    fig3 = px.box(f, x="Churn", y="MonthlyCharges", title="Monthly Charges vs Churn")
    st.plotly_chart(fig3, use_container_width=True)

with right2:
    fig4 = px.histogram(f, x="PaymentMethod", color="Churn", barmode="group",
                        title="Churn by Payment Method")
    st.plotly_chart(fig4, use_container_width=True)

# ---------- ಹೆಚ್ಚು ರಿಸ್ಕ್ ಗ್ರಾಹಕರು ----------
st.subheader("🚨 High-Risk Customers (to contact first)")
risk = (f[f["ChurnProb"] > threshold]
        .sort_values("ChurnProb", ascending=False)
        [["customerID", "Contract", "tenure", "MonthlyCharges", "ChurnProb"]]
        .head(50))
st.dataframe(risk, use_container_width=True)