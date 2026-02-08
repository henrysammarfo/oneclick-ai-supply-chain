"""Streamlit dashboard for OneClick AI Supply Chain."""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="OneClick AI - Supply Chain", layout="wide", page_icon="🔗")

st.markdown("""
<style>
    .stApp { background-color: #0a0a1a; }
    .metric-card { background: rgba(0,212,255,0.1); border: 1px solid #00d4ff; border-radius: 10px; padding: 15px; }
    h1, h2, h3 { color: #00d4ff !important; }
</style>
""", unsafe_allow_html=True)

st.title("OneClick AI - Supply Chain Agent Network")
st.markdown("*Decentralized AI agents sourcing any product globally*")

with st.sidebar:
    st.header("Configuration")
    scenario = st.selectbox("Scenario", ["Ferrari F8 Tributo", "60ft Luxury Yacht", "200-Room Hotel", "Custom"])
    product = st.text_input("Product", scenario) if scenario == "Custom" else scenario
    st.divider()
    use_real = st.checkbox("Use Real APIs", value=True)
    rounds = st.slider("Negotiation Rounds", 1, 5, 3)
    max_sup = st.slider("Max Suppliers", 5, 25, 15)
    run = st.button("Start Sourcing", type="primary", use_container_width=True)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Components", "0")
c2.metric("Suppliers", "0")
c3.metric("Total Cost", "$0")
c4.metric("Delivery", "0 days")

st.divider()
tab1, tab2, tab3, tab4 = st.tabs(["Supply Graph", "Agent Activity", "Components", "Analytics"])

with tab1:
    fig = go.Figure()
    fig.update_layout(template="plotly_dark", paper_bgcolor="#0a0a1a", plot_bgcolor="#0a0a1a", height=500, title="Supply Chain Network")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Agent Message Feed")
    st.info("Messages appear here during sourcing")

with tab3:
    st.dataframe(pd.DataFrame(columns=["Component", "Category", "Supplier", "Cost", "Delivery"]), use_container_width=True)

with tab4:
    st.info("Analytics charts generated after sourcing")

if run:
    with st.spinner("Agents working..."):
        st.success(f"Sourcing initiated for: {product}")
        st.info("Run `python run_demo.py` for the full pipeline")
