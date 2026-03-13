# frontend/analytics_ui.py
import streamlit as st
from datetime import date, timedelta
import matplotlib.pyplot as plt
from utils import get_analytics_from_backend
import pandas as pd

def render_analytics():
    st.subheader("Analytics")
    today = date.today()
    default_start = today - timedelta(days=30)
    start_date = st.date_input("Start date", default_start)
    end_date = st.date_input("End date", today)

    if st.button("Compute"):
        data = get_analytics_from_backend(start_date, end_date)

        if not data:
            st.info("No data for selected period")
            return

        df = pd.DataFrame([
            {"category": k, "total": v["total"], "percentage": v["percentage"]}
            for k, v in data.items()
        ])

        st.subheader("Expense Summary")

        # KPI CARDS
        total_spending = df["total"].sum()
        top_category = df.sort_values("total", ascending=False).iloc[0]["category"]
        num_categories = len(df)

        col1, col2, col3 = st.columns(3)

        col1.metric(
            label="Total Spending",
            value=f"${total_spending:.2f}"
        )

        col2.metric(
            label="Top Category",
            value=top_category
        )

        col3.metric(
            label="Categories",
            value=num_categories
        )

        st.divider()

        # DATA TABLE
        st.subheader("Category Breakdown")
        st.dataframe(df)

        # BAR CHART
        st.subheader("Category Spending")
        st.bar_chart(df.set_index("category")["total"])

        # PIE CHART
        st.subheader("Spending Distribution")

        fig, ax = plt.subplots()
        ax.pie(
            df["total"],
            labels=df["category"],
            autopct="%1.1f%%",
            startangle=90
        )
        ax.axis("equal")

        st.pyplot(fig)