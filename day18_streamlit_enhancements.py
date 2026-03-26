import streamlit as st
import json
import pandas as pd
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

        new_ticket = {
        "id": ticket.get("id"),
        "text": ticket.get("text"),
        "category": ticket.get("category"),
        "priority": ticket.get("priority"),
        "confidence": ticket.get("confidence"),
        "status": ticket.get("status"),
        "sla_breached": ticket.get("sla_breached"),
        "action": action
        }

        action_queue.append(new_ticket)

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
        return response.output_text.strip() or None

    except Exception as e:
        return f"Error generating response: {e}"

def highlight_sla(row):
    if row["sla_breached"] is True:
        return ["background-color: #ff4d4d"] * len(row)
    return [""] * len(row)

#Main Header 
st.set_page_config(page_title="Ticket Dashboard", layout="wide")
#Page title 
st.title("AI Support Ticket Dashboard")
#Store previous results
try:
     with open("classified_tickets.json", "r") as file:
         results = json.load(file)
         
except FileNotFoundError:
    st.error("classified_tickets.json file not found.")
    st.stop()
except json.JSONDecodeError:
    st.error("Error decoding JSON. File may be corrupted.")
    st.stop()
except Exception as e:
    st.error(f"Unexpected error: {e}")
    st.stop()

action_queue = build_action_queue(results)
#Store all data
df = pd.DataFrame(action_queue)

#Create Categories
total_tickets = len(df)
open_tickets = len(df[df["status"] == "open"])
needs_review_tickets = len(df[df["status"] == "needs_review"])
sla_breached_tickets = len(df[df["sla_breached"] == True])

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Tickets", total_tickets)
col2.metric("Open", open_tickets)
col3.metric("Needs Review", needs_review_tickets)
col4.metric("SLA Breached", sla_breached_tickets)

st.subheader("Action Summary")
action_summary = df["action"].value_counts().reset_index()
action_summary.columns = ["action", "count"]
action_summary.index = action_summary.index + 1
st.dataframe(action_summary, use_container_width=True)


st.subheader("Category Summary")
category_summary = df["category"].value_counts().reset_index()
category_summary.columns = ["category", "count"]
category_summary.index = category_summary.index + 1
st.dataframe(category_summary, use_container_width=True)


#SideBar Filters creation
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

#Create Filtered Table
st.subheader("Filtered Tickets")

#Highlight Breached SLAs
styled_df = filtered_df.style.apply(highlight_sla, axis=1)

st.dataframe(styled_df)


if "ai_responses" not in st.session_state:
    st.session_state.ai_responses = {}

#Individual Ticket details
st.subheader("Ticket Detail View")

ticket_ids = filtered_df["id"].tolist()
selected_id = st.selectbox("Select Ticket ID", ticket_ids)

selected_ticket = filtered_df[filtered_df["id"] == selected_id].iloc[0]
ticket_id= selected_ticket["id"]

st.write(selected_ticket)

existing_response= st.session_state.ai_responses.get(ticket_id)

if existing_response is None:
    if st.button("Generate AI Response", key=f"generate_{ticket_id}"):
        response = generate_ai_response(selected_ticket["text"])
        if response:
            st.session_state.ai_responses[ticket_id] = response
        else:
            st.warning("Failed to generate response. Try again.")
        
        st.rerun()
    
if existing_response is not None:
    st.subheader("AI Draft Response")
    st.write(f"**Ticket ID:** {ticket_id}")
    st.write(existing_response)

    if st.button("Regenerate Response", key=f"regen_{ticket_id}"):
        response = generate_ai_response(selected_ticket["text"])
        if response:
            st.session_state.ai_responses[ticket_id] = response
        else:
            st.warning("Regeneration failed. Try again.")
        st.rerun()