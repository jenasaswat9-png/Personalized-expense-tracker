# frontend/add_update_ui.py
import streamlit as st
from datetime import date
from utils import fetch_expenses_from_backend, push_expenses_to_backend

def render_add_update():
    st.subheader("Add / Update expenses for a date")
    col1, col2 = st.columns([1, 2])
    with col1:
        expense_date = st.date_input("Select date", value=date.today())
        if st.button("Load"):
            rows = fetch_expenses_from_backend(expense_date)
            st.session_state["loaded"] = rows
    with col2:
        st.info("Enter one or more expense items and press Save")

    # dynamic form entries
    if "items" not in st.session_state:
        st.session_state['items'] = [{"amount": 0.0, "category": "", "notes": ""}]

    def add_row():
        st.session_state['items'].append({"amount": 0.0, "category": "", "notes": ""})

    for i, item in enumerate(st.session_state['items']):
        with st.expander(f"Item {i+1}", expanded=True):
            item["amount"] = st.number_input(f"Amount {i}", value=float(item.get("amount", 0.0)))
            item["category"] = st.text_input(f"Category {i}", value=item.get("category", ""))
            item["notes"] = st.text_input(f"Notes {i}", value=item.get("notes", ""))
            if st.button(f"Remove {i}"):
                st.session_state.items.pop(i)
                st.experimental_rerun()

    st.button("Add item", on_click=add_row)

    if st.button("Save to server"):
        rows = st.session_state.items
        push_expenses_to_backend(expense_date.isoformat(), rows)
        st.success("Saved successfully")
        st.session_state.items = [{"amount": 0.0, "category": "", "notes": ""}]