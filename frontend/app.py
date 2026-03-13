import streamlit as st
from add_update_ui import render_add_update
from analytics_ui import render_analytics

st.set_page_config(page_title="Expense Tracker", page_icon="💸", layout="wide")

# ---- ADD THIS SECTION ----
st.markdown(
"""
<style>
.big-title {
font-size:42px;
font-weight:700;
color:#4CAF50;
}
</style>
""",
unsafe_allow_html=True
)

st.markdown(
'<p class="big-title">💸 Expense Analytics Platform</p>',
unsafe_allow_html=True
)
# --------------------------

def main():
    st.sidebar.title("Expense Manager")
    page = st.sidebar.radio("Go to", ["Add / Update", "Analytics", "Import CSV", "About"])

    st.header("Personalized Expense Tracker")
    if page == "Add / Update":
        render_add_update()
    elif page == "Analytics":
        render_analytics()
    elif page == "Import CSV":
        st.info("Upload a CSV with columns: expense_date,amount,category,notes")
        uploaded = st.file_uploader("CSV file", type=["csv"])
        if uploaded:
            import pandas as pd
            df = pd.read_csv(uploaded, parse_dates=["expense_date"])
            st.write("Preview", df.head())
            if st.button("Upload to server"):
                # Call backend API to upload by date groups
                grouped = df.groupby(df['expense_date'].dt.date)
                for d, group in grouped:
                    rows = group.to_dict(orient="records")
                    # call backend (simple helper)
                    from frontend.utils import push_expenses_to_backend
                    push_expenses_to_backend(d.isoformat(), rows)
                st.success("Uploaded")
    else:
        st.markdown("""
        **About this app**  
        The **Personalized Expense Tracker** is a full-stack data application designed to help users record, manage, and analyze their daily expenses.

        This project demonstrates how a modern data-driven application can be built using a **Streamlit frontend** and a **FastAPI backend**, enabling efficient data processing, analytics generation, and an interactive user interface.

        Users can add and update expenses, upload historical records, and analyze spending patterns across categories and time periods. The application processes this data to generate meaningful insights such as category-wise spending distribution and overall expenditure trends.

        Beyond basic expense tracking, the project highlights practical software engineering practices including modular project structure, API-based communication between services, database interaction, and clean UI design. It serves as a portfolio-ready example of building an end-to-end analytics application using Python.
        """)

if __name__ == "__main__":
    main()