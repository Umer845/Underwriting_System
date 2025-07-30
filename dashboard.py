import streamlit as st
import pandas as pd
import plotly.express as px
import psycopg2

def show_dashboard():
    st.set_page_config(layout="wide")
    st.markdown(
        """
        <style>
        body {
            background-color: #f7f7f7;
        }
        .main {
            background-color: #ffffff;
            border-radius: 8px;
            padding: 2rem;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        h1, h2, h3 {
            color: #333333;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("📊 Underwriter Dashboard")
    st.markdown("##### Overview of Vehicle Risk & Premium Data")

    # ---- DB Connection ----
    conn = psycopg2.connect(
        dbname="Underwritter",
        user="postgres",
        password="United2025",
        host="localhost",
        port="5432"
    )

    df = pd.read_sql("SELECT * FROM vehicle_risk", conn)

    if df.empty:
        st.warning("No risk data found yet. Please calculate some risk profiles first.")
    else:
        # ---- Key Metrics ----
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Records", len(df))
        col2.metric("Avg Premium Rate (%)", f"{df['premium_rate'].mean():.2f}")
        col3.metric("Unique Makes", df['make_name'].nunique())

        st.divider()

        # ---- Risk Level Distribution ----
        fig1 = px.histogram(
            df, x="risk_level", color="risk_level",
            title="Risk Level Distribution",
            template="plotly_white"
        )
        fig1.update_layout(
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff",
            bargap=0.3,
            xaxis_title="Risk Level",
            yaxis_title="Count"
        )
        st.plotly_chart(fig1, use_container_width=True)

        # ---- Premium Rate by Make Name ----
        fig2 = px.box(
            df, x="make_name", y="premium_rate", color="risk_level",
            title="Premium Rate by Make Name & Risk Level",
            template="plotly_white"
        )
        fig2.update_layout(
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff",
            xaxis_title="Make Name",
            yaxis_title="Premium Rate (%)",
            boxmode="group"
        )
        st.plotly_chart(fig2, use_container_width=True)

        # ---- Premium Rate by Model Year ----
        fig3 = px.line(
            df.groupby(['model_year'])['premium_rate'].mean().reset_index(),
            x="model_year", y="premium_rate",
            title="Average Premium Rate Over Model Years",
            markers=True,
            template="plotly_white"
        )
        fig3.update_layout(
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff",
            xaxis_title="Model Year",
            yaxis_title="Avg Premium Rate (%)"
        )
        st.plotly_chart(fig3, use_container_width=True)

    conn.close()
