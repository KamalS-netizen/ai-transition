import streamlit as st
import json
import pandas as pd

def build_action_queue(results):
    action_queue = []

    for ticket in results:
        priority = ticket.get("priority")
        status = ticket.get("status")
        sla_breached = ticket.get("sla_breached", False)

        if status == "closed":
            action = "no_action"
        elif sla_breached and priority in ["high", "medium"]:
            action = "escalate_now"
        elif status == "needs_review":
            action = "review_now"
        elif status == "open" and priority == "high":
            action = "follow_up_soon"
        elif status == "open" and priority == "medium":
            action = "monitor_closely"
        else:
            action = "monitor"

        action_queue.append({
            "id": ticket.get("id"),
            "text": ticket.get("text"),
            "category": ticket.get("category"),
            "priority": priority,
            "status": status,
            "sla_breached": sla_breached,
            "created_at": ticket.get("created_at"),
            "action": action
        })

    return action_queue

st.set_page_config(page_title="Ticket Dashboard", layout="wide")

st.title("AI Support Ticket Dashboard")
st.write("Day 15 - Streamlit version of the ticket system")

with open("classified_tickets.json", "r") as file:
    results = json.load(file)

action_queue = build_action_queue(results)
df = pd.DataFrame(action_queue)

if "action" not in df.columns:
    df["action"] = "no_action"
else:
    df["action"] = df["action"].fillna("no_action")

st.sidebar.header("Filters")

priority_filter = st.sidebar.selectbox(
    "Priority",
    ["all", "high", "medium", "low"]
)

status_filter = st.sidebar.selectbox(
    "Status",
    ["all", "open", "closed", "needs_review"]
)

action_filter = st.sidebar.selectbox(
    "Action",
    ["all", "escalate_now", "review_now", "follow_up_soon", "monitor_closely", "monitor", "no_action"]
)

filtered_df = df.copy()

if priority_filter != "all":
    filtered_df = filtered_df[filtered_df["priority"] == priority_filter]

if status_filter != "all":
    filtered_df = filtered_df[filtered_df["status"] == status_filter]

if action_filter != "all":
    filtered_df = filtered_df[filtered_df["action"] == action_filter]

st.subheader("Summary")

total_tickets = len(filtered_df)
open_tickets = len(filtered_df[filtered_df["status"] == "open"])
review_tickets = len(filtered_df[filtered_df["status"] == "needs_review"])
breached_tickets = len(filtered_df[filtered_df["sla_breached"] == True])

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Tickets", total_tickets)
col2.metric("Open", open_tickets)
col3.metric("Needs Review", review_tickets)
col4.metric("SLA Breached", breached_tickets)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Action Summary")
    action_summary = filtered_df["action"].value_counts()
    st.dataframe(action_summary, use_container_width=True)

with col2:
    st.subheader("Category Summary")
    category_summary = filtered_df["category"].value_counts()
    st.dataframe(category_summary, use_container_width=True)

st.subheader("Filtered Tickets")
st.dataframe(filtered_df, use_container_width=True)

st.subheader("Ticket Detail View")

ticket_ids = filtered_df["id"].tolist()
selected_id = st.selectbox("Select Ticket ID", ticket_ids)

selected_ticket = filtered_df[filtered_df["id"] == selected_id].iloc[0]

st.write(f"**ID:** {selected_ticket['id']}")
st.write(f"**Category:** {selected_ticket['category']}")
st.write(f"**Priority:** {selected_ticket['priority']}")
st.write(f"**Status:** {selected_ticket['status']}")
st.write(f"**Action:** {selected_ticket['action']}")
st.write(f"**SLA Breached:** {selected_ticket['sla_breached']}")
st.write(f"**Created At:** {selected_ticket['created_at']}")
st.write("**Text:**")
st.write(selected_ticket["text"])