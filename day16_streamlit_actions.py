import streamlit as st
import json
import pandas as pd
import json
import os
from openai import OpenAI

client = OpenAI()

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

        ticket["action"] = action
        action_queue.append(ticket)

    return action_queue

def generate_ai_response(ticket_text):
    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=f"""
You are a customer support agent.

Write a clear, professional, and helpful email-style response to this support ticket.

Ticket:
{ticket_text}

Keep the response concise and practical.
Do not invent refunds, credits, or actions unless mentioned in the ticket.
"""
        )
        return response.output_text.strip()

    except Exception as e:
        return f"Error generating response: {e}"

def highlight_sla(row):
    if row["sla_breached"] is True:
        return ["background-color: #ff4d4d"] * len(row)
    return [""] * len(row)

st.set_page_config(page_title="Ticket Dashboard", layout="wide")

st.title("AI Support Ticket Dashboard")

with open("classified_tickets.json", "r") as file:
    results = json.load(file)

action_queue = build_action_queue(results)
df = pd.DataFrame(action_queue)

st.sidebar.header("Filters")

priority_filter = st.sidebar.selectbox("Priority", ["all", "high", "medium", "low"])
status_filter = st.sidebar.selectbox("Status", ["all", "open", "closed", "needs_review"])
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

if filtered_df.empty:
    st.warning("No tickets match the current filters.")
    st.stop()

st.subheader("Filtered Tickets")

styled_df = filtered_df.style.apply(highlight_sla, axis=1)

st.dataframe(styled_df)

st.subheader("Ticket Detail View")

ticket_ids = filtered_df["id"].tolist()
selected_id = st.selectbox("Select Ticket ID", ticket_ids)

selected_ticket = filtered_df[filtered_df["id"] == selected_id].iloc[0]

st.write(selected_ticket)

if st.button("Generate AI Response"):
    ai_response = generate_ai_response(selected_ticket["text"])
    st.subheader("AI Draft Response")
    st.write(ai_response)
 