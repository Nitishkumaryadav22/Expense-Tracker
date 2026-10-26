import streamlit as st
import json
import os
from datetime import date

# -----------------------------
# Expense Tracker (Core Python)
# -----------------------------
FILE_NAME = "expenses.json"

st.set_page_config(page_title="Expense Tracker", page_icon="💸", layout="wide")


def load_expenses():
    """Load expenses from the JSON file."""
    if not os.path.exists(FILE_NAME):
        return []

    try:
        with open(FILE_NAME, "r", encoding="utf-8") as file:
            data = json.load(file)
            if isinstance(data, list):
                return data
            return []
    except (json.JSONDecodeError, OSError):
        return []


def save_expenses(expenses):
    """Save expenses to the JSON file."""
    with open(FILE_NAME, "w", encoding="utf-8") as file:
        json.dump(expenses, file, indent=4)


def calculate_total(expenses):
    """Calculate total spending."""
    total = 0
    for expense in expenses:
        total += expense["amount"]
    return total


def format_rupees(amount):
    return f"₹{amount:,.2f}"


# Keep the latest data in Streamlit session state.
if "expenses" not in st.session_state:
    st.session_state.expenses = load_expenses()

st.title("💸 Personal Expense Tracker")
st.caption("Track your daily spending with Python and Streamlit.")

expenses = st.session_state.expenses

# Summary section
total_spent = calculate_total(expenses)
expense_count = len(expenses)

col1, col2 = st.columns(2)
col1.metric("Total Spending", format_rupees(total_spent))
col2.metric("Number of Expenses", expense_count)

st.divider()

# Add an expense
st.subheader("➕ Add a New Expense")

with st.form("add_expense_form", clear_on_submit=True):
    col1, col2 = st.columns(2)

    with col1:
        expense_title = st.text_input(
            "Expense description",
            placeholder="e.g. Lunch, bus fare, groceries"
        )
        amount = st.number_input(
            "Amount (₹)",
            min_value=0.0,
            value=0.0,
            step=10.0,
            format="%.2f"
        )

    with col2:
        category = st.selectbox(
            "Category",
            [
                "Food",
                "Transport",
                "Education",
                "Shopping",
                "Bills",
                "Health",
                "Entertainment",
                "Other"
            ]
        )
        expense_date = st.date_input("Expense date", value=date.today())

    submitted = st.form_submit_button("Add Expense", use_container_width=True)

    if submitted:
        if not expense_title.strip():
            st.error("Please enter an expense description.")
        elif amount <= 0:
            st.error("Amount must be greater than ₹0.")
        else:
            new_expense = {
                "id": max([item.get("id", 0) for item in expenses], default=0) + 1,
                "title": expense_title.strip(),
                "amount": round(amount, 2),
                "category": category,
                "date": expense_date.isoformat()
            }
            expenses.append(new_expense)
            save_expenses(expenses)
            st.session_state.expenses = expenses
            st.success("Expense added successfully!")
            st.rerun()

st.divider()

# View and filter expenses
st.subheader("📋 Your Expenses")

if not expenses:
    st.info("No expenses recorded yet. Add your first expense above.")
else:
    available_categories = ["All"] + sorted(
        {expense["category"] for expense in expenses}
    )
    selected_category = st.selectbox(
        "Filter by category",
        available_categories
    )

    filtered_expenses = []
    for expense in expenses:
        if selected_category == "All" or expense["category"] == selected_category:
            filtered_expenses.append(expense)

    st.write(f"Showing **{len(filtered_expenses)}** expense(s).")

    # Show newest expenses first
    for expense in sorted(
        filtered_expenses,
        key=lambda item: (item.get("date", ""), item.get("id", 0)),
        reverse=True
    ):
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 2, 1])

            with col1:
                st.markdown(f"**{expense['title']}**")
                st.caption(f"{expense['date']} • {expense['category']}")

            with col2:
                st.markdown(f"### {format_rupees(expense['amount'])}")

            with col3:
                if st.button("🗑️ Delete", key=f"delete_{expense['id']}"):
                    st.session_state.expenses = [
                        item for item in st.session_state.expenses
                        if item.get("id") != expense["id"]
                    ]
                    save_expenses(st.session_state.expenses)
                    st.rerun()

    st.divider()

    # Category-wise summary using only core Python
    st.subheader("📊 Category-wise Spending")

    category_totals = {}
    for expense in expenses:
        expense_category = expense["category"]
        if expense_category not in category_totals:
            category_totals[expense_category] = 0
        category_totals[expense_category] += expense["amount"]

    for expense_category, category_total in sorted(
        category_totals.items(),
        key=lambda item: item[1],
        reverse=True
    ):
        st.write(f"**{expense_category}** — {format_rupees(category_total)}")
        st.progress(min(category_total / total_spent, 1.0) if total_spent else 0.0)

    # Download a backup of the expense records
    json_data = json.dumps(expenses, indent=4)
    st.download_button(
        label="⬇️ Download expenses as JSON",
        data=json_data,
        file_name="expenses_backup.json",
        mime="application/json",
        use_container_width=True
    )

st.caption("Your records are stored locally in expenses.json beside this Python file.")
