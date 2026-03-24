# ai-transition
Documenting my structured transition from Customer Support to AI Engineer — Python, APIs, SQL, and AI projects.
# AI Ticket Analyzer Dashboard

## Problem
Support teams handle hundreds of tickets daily, many of which follow repetitive patterns such as login issues, payment failures, and refund requests.
Most teams:
- Manually triage tickets
- Miss SLA deadlines
- Lack visibility into ticket categories and trends
- Respond inconsistently to customers

This leads to slower resolution times and poor customer experience.

## Solution
This project is an AI-powered ticket analysis dashboard that:

- Classifies tickets into categories (login, payment, refund, other)
- Assigns priority levels automatically
- Tracks SLA breaches in real-time
- Provides filtered views for operational decision-making
- Generates AI-powered draft responses for support agents

The system helps support teams move from reactive handling to structured, data-driven workflows.

## Key Features
- AI-based ticket classification (OpenAI API)
- Priority-based triage system
- SLA breach detection
- Action queue for escalation
- Interactive Streamlit dashboard
- Ticket filtering (category, priority, SLA status)
- AI-generated response drafts (with regenerate option)

## Architecture
tickets.json → Python processing script → classification + SLA logic → Streamlit dashboard

Components:
- Python (data processing + AI integration)
- OpenAI API (classification + response generation)
- Pandas (data handling)
- Streamlit (UI layer)

## Business Impact
- Reduces manual ticket triage effort
- Improves SLA adherence
- Speeds up response time
- Enables consistent communication with customers
- Provides visibility into support operations

## How to Run

1. Clone the repository
2. Install dependencies:
   pip install streamlit pandas openai

3. Set your OpenAI API key:
   export OPENAI_API_KEY="your_key_here"

4. Run the dashboard:
   streamlit run day18_streamlit_enhancements.py

## Demo Note

This project is designed as a functional prototype to demonstrate how AI can be integrated into customer support workflows.