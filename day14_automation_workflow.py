import json
import os
from openai import OpenAI
from datetime import datetime

client = OpenAI()

def load_tickets():
    with open("tickets.json", "r") as file:
        return json.load(file)

def build_open_queue_counts(results):
    open_queue_counts = {
        "high": 0,
        "medium": 0
    }

    for ticket in results:
        priority = ticket["priority"]

        if priority in open_queue_counts:
            open_queue_counts[priority] += 1

    return open_queue_counts

def load_existing_results():
    results = []
    processed_ids = set()

    if os.path.exists("classified_tickets_day7.json"):
        try:
            with open("classified_tickets_day7.json", "r") as file:
                existing_results = json.load(file)
        except json.JSONDecodeError:
            existing_results = []

        for ticket in existing_results:
            processed_ids.add(ticket["id"])

        results = existing_results

    return results, processed_ids

def classify_ticket(ticket_text):
    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=f"""
Classify this support ticket.

Ticket:
{ticket_text}

Return ONLY valid JSON in this format:
{{"category": "login", "priority": "high", "confidence": 0.92}}

Rules:
- category must be one of: login, payment, refund, other
- priority must be one of: high, medium, low
- confidence must be a number between 0 and 1
"""
        )
        result = response.output_text.strip()

    except Exception as e:
        print(f"API error for ticket: {ticket_text}")
        print(e)
        return "other", "low", 0

    try:
        data = json.loads(result)

        category = data["category"].strip().lower()
        priority = data["priority"].strip().lower()
        confidence = float(data["confidence"])

        valid_categories = {"login", "payment", "refund", "other"}
        valid_priorities = {"high", "medium", "low"}

        if category not in valid_categories:
            category = "other"

        if priority not in valid_priorities:
            priority = "low"

        if confidence < 0 or confidence > 1:
            confidence = 0

        return category, priority, confidence

    except (json.JSONDecodeError, KeyError, ValueError, TypeError):
        print(f"Invalid AI output for ticket: {ticket_text}")
        print(result)
        return "other", "low", 0

def build_new_category_counts():
    return {
        "login": 0,
        "payment": 0,
        "refund": 0,
        "other": 0
    }

def build_new_priority_counts():
    return {
        "high": 0,
        "medium": 0,
        "low": 0
    }

def build_total_category_counts(results):
    total_category_counts = {
        "login": 0,
        "payment": 0,
        "refund": 0,
        "other": 0
    }

    for ticket in results:
        category = ticket["category"]

        if category in total_category_counts:
            total_category_counts[category] += 1
        else:
            total_category_counts["other"] += 1

    return total_category_counts

def build_total_priority_counts(results):
    total_priority_counts = {
        "high": 0,
        "medium": 0,
        "low": 0
    }

    for ticket in results:
        priority = ticket["priority"]

        if priority in total_priority_counts:
            total_priority_counts[priority] += 1

    return total_priority_counts

def build_total_status_counts(results):
    status_counts = {
        "open": 0,
        "needs_review": 0
    }

    for ticket in results:
        #Reads if status exists in the tickets else adds a default open to them
        status = ticket.get("status", "open")  
        if status in status_counts:
            status_counts[status] += 1

    return status_counts

def build_aging_summary(results):
    aging_counts = {
        "fresh": 0,
        "old": 0
    }

    now = datetime.now()

    for ticket in results:
        #using .get here since not all tickets have this field. Using this allows us to 
        #run the code on the returned "none" value and skip iterations allowing code to 
        #run without key error. 
        created_at = ticket.get("created_at")

        if not created_at:
            continue

        created_time = datetime.fromisoformat(created_at)
        age_hours = (now - created_time).total_seconds() / 3600

        if age_hours >= 24:
            aging_counts["old"] += 1
        else:
            aging_counts["fresh"] += 1

    return aging_counts

def build_sorted_results(results):
    priority_order = {
        "high": 1,
        "medium": 2,
        "low": 3
    }

    return sorted(
        results,
        key=lambda ticket: priority_order[ticket["priority"]]
    )

def get_sla_hours(priority):
    sla_map = {
        "high": 4,
        "medium": 24,
        "low": 72
    }

    return sla_map.get(priority, 72)

def build_sla_breach_summary(results):

    sla_breach_counts = {
        "high": 0,
        "medium": 0,
        "low": 0
    }

    for ticket in results:

        priority = ticket["priority"]
        sla_breached = ticket.get("sla_breached", False)

        if sla_breached and priority in sla_breach_counts:
            sla_breach_counts[priority] += 1

    return sla_breach_counts

def build_escalation_queue(results):

    escalation_queue = []

    for ticket in results:

        priority = ticket["priority"]
        sla_breached = ticket.get("sla_breached", False)
    
        if sla_breached and priority in ["high", "medium"]:

            escalation_queue.append(ticket)

    return escalation_queue    

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

def summarize_actions(action_queue):
    action_summary = {}

    for ticket in action_queue:
        action = ticket.get("action")

        if action not in action_summary:
            action_summary[action] = 0

        action_summary[action] += 1

    return action_summary

def filter_tickets(results, priority=None, 
                breached=None, category=None,
                status=None, keyword=None,
                sort_by=None, action=None
                ):
    filtered = []

    for ticket in results:
        if priority is not None and ticket["priority"] != priority:
            continue

        if breached is not None and ticket.get("sla_breached", False) != breached:
            continue

        if category is not None and ticket["category"] != category:
            continue

        if status is not None and ticket.get("status") != status:
            continue
        
        if keyword is not None and keyword.lower() not in ticket["text"].lower():
            continue

        if action is not None and action.lower() not in ticket.get("action") != action:
            continue

        filtered.append(ticket)

    if sort_by == "priority":
            priority_order = {"high": 1, "medium": 2, "low": 3}
            filtered = sorted(filtered, key=lambda x: priority_order.get(x["priority"], 4))

    elif sort_by == "sla":
            filtered = sorted(filtered, key=lambda x: x.get("sla_hours") or 999)

    elif sort_by == "created":
            filtered = sorted(filtered, key=lambda x: x.get("created_at") or "")

    return filtered

def run_query(
        title, results, priority=None,
        breached=None, category=None,
        status=None, keyword=None, sort_by=None, 
        action=None):

    filtered = filter_tickets(
        results,
        priority=priority,
        breached=breached,
        category=category,
        status=status,
        keyword=keyword, 
        sort_by=sort_by, 
        action= action
        
    )

    print_tickets(title, filtered)

def print_summary(title, counts):
    print(f"\n{title}")
    print("-" * len(title))

    for label, count in counts.items():
        print(f"{label.capitalize():<7} : {count}")

def print_triage_queue(sorted_results):
    print("\nTriage Queue")
    print("------------")

    for ticket in sorted_results:
        if ticket["priority"] != "low":
            print(
                f'ID: {ticket["id"]:3} | '
                f'Priority: {ticket["priority"].capitalize():<3} | '
                f'Category: {ticket["category"].capitalize():<7} | '
                f'Text: {ticket["text"]} | ' 
                f'SLA: {ticket.get("sla_hours", "N/A")} | '
                f'Breached: {ticket.get("sla_breached", False)} | '
            )

def print_processing_summary(processed_count, skipped_count):
    print("\nProcessing Summary")
    print("------------------")
    print("New tickets processed:", processed_count)
    print("Tickets skipped:", skipped_count)

def run_daily_workflow(results):
    action_queue = build_action_queue(results)
    action_summary = summarize_actions(action_queue)

    print_summary("Action Summary", action_summary)

    run_query("Escalate Now", action_queue, action="escalate_now")
    run_query("Needs Review", action_queue, action="review_now")
    run_query("Follow Up Soon", action_queue, action="follow_up_soon")
    run_query("Monitor Closely", action_queue, action="monitor_closely")

# def print_review_queue(review_queue):
#     print("\nReview Queue")
#     print("------------")

#     for ticket in review_queue:
#         print(
#             f'ID: {ticket["id"]} | '
#             f'Status: {ticket["status"]:<12} | '
#             f'Priority: {ticket["priority"]:<12} | '
#             f'Category: {ticket["category"]:<12} | '
#             f'Confidence: {ticket["confidence"]:.2f} | '
#             f'Text: {ticket["text"]:<12} | '
#             f'SLA Hours: {ticket["sla_hours"]:<3} | '
#             f'SLA Breached: {ticket["sla_breached"]} | '
#             )

def print_tickets(title, results):
    print(f"\n{title}")
    print("-" * len(title))

    if not results:
        print("No tickets found.")
        return

    for ticket in results:
        # Safe extraction
        ticket_id = ticket.get("id", "N/A")
        priority = ticket.get("priority", "N/A").capitalize()
        category = ticket.get("category", "N/A").capitalize()
        status = ticket.get("status", "N/A")
        text = ticket.get("text", "")

        # SLA formatting fix
        sla_hours = ticket.get("sla_hours")
        sla_display = f"{sla_hours}h" if sla_hours is not None else "N/A"

        breached = ticket.get("sla_breached", False)

        print(
            f'ID: {ticket_id:<4} | '
            f'Priority: {priority:<7} | '
            f'Category: {category:<10} | '
            f'Status: {status:<12} | '
            f'SLA: {sla_display:<5} | '
            f'Breached: {str(breached):<5} | '
            f'Text: {text}'
        )

tickets = load_tickets()
results, processed_ids = load_existing_results()

category_counts = build_new_category_counts()
priority_counts = build_new_priority_counts()

processed_count = 0
skipped_count = 0
review_count = 0
review_queue = []

for ticket in tickets:
    ticket_id = ticket["id"]
    ticket_text = ticket["text"]

    if ticket_id in processed_ids:
        print(f"Skipping ticket {ticket_id} (already classified)")
        skipped_count += 1
        continue

    category, priority, confidence = classify_ticket(ticket_text)

    created_at = ticket.get("created_at", datetime.now().isoformat())    
    sla_hours = get_sla_hours(priority)
    created_time = datetime.fromisoformat(created_at)
    age_hours = (datetime.now() - created_time).total_seconds() / 3600
    sla_breached = age_hours > sla_hours

    if confidence < 0.60:
        review_count += 1
        status="needs_review"
        review_queue.append({
            "id": ticket_id,
            "text": ticket_text,
            "category": category,
            "priority": priority,
            "confidence": confidence,
            "status": status,
            "created_at": created_at,
            "sla_hours": sla_hours,
            "sla_breached": sla_breached
    })
    else:
        status = "open"
    
    print(f"{ticket_id}: {ticket_text} -> {category}, {priority}, Confidence: {confidence}")

    results.append({
        "id": ticket_id,
        "text": ticket_text,
        "category": category,
        "priority": priority,
        "confidence": confidence,
        "status": status,
        "created_at": created_at,
        "sla_hours": sla_hours,
        "sla_breached": sla_breached
    })

    processed_count += 1

    if category in category_counts:
        category_counts[category] += 1
    else:
        category_counts["other"] += 1

    if priority in priority_counts:
        priority_counts[priority] += 1
    
review_queue_counts = {
    "Needs review": review_count
    }

with open("classified_tickets_day7.json", "w") as file:
    json.dump(results, file, indent=4)

total_category_counts = build_total_category_counts(results)
total_priority_counts = build_total_priority_counts(results)
sorted_results = build_sorted_results(results)
open_queue_counts = build_open_queue_counts(results)
total_status_counts = build_total_status_counts(results)
aging_counts = build_aging_summary(results)
sla_breach_counts = build_sla_breach_summary(results)
escalation_queue = build_escalation_queue(results)
needs_review_tickets = filter_tickets(results, status="needs_review")

action_queue = build_action_queue(results)
action_summary = summarize_actions(action_queue)
#high_breached_tickets = filter_tickets(results, priority="high", breached=True)
# medium_breached_tickets = filter_tickets(results, priority="medium", breached=True)
# login_tickets = filter_tickets(results, category="login")
# high_login_breach=filter_tickets(results, priority="high", breached=True, category="login")
#print_escalation_queue("High Breached Tickets ", high_breached_tickets)
#print_escalation_queue("Medium Breached Tickets ", medium_breached_tickets)
#print_escalation_queue("Login Tickets ", login_tickets)
#print_escalation_queue("High Login Breach Tickets ", high_login_breach)
print_summary("New Category Summary", category_counts)
print_summary("New Priority Summary", priority_counts)
print_summary("Total Category Summary", total_category_counts)
print_summary("Total Priority Summary", total_priority_counts)
print_summary("Open Queue Summary", open_queue_counts)
print_summary("Review Queue Summary", review_queue_counts)
print_summary("Status Summary", total_status_counts)
print_summary("Age Summary", aging_counts)
print_summary("SLA Breach Summary", sla_breach_counts)
print_summary("Action Summary ", action_summary)
print_triage_queue(sorted_results)
print_tickets("Tickets to review from this Run", review_queue)
print_tickets("Escalation Queue", escalation_queue)
print_tickets("Review Queue", needs_review_tickets)
print_processing_summary(processed_count, skipped_count)
run_query("High Breached Tickets", results, priority="high", breached=True)
run_query("Login Tickets", results, category="login")
run_query("All Review Tickets", results, status="needs_review")
run_query("Open High Tickets", results, priority="high", status="open")
run_query("High Breached Login Tickets",results,priority="high",breached=True,category="login")
run_query("Open Login Tickets",results,category="login",status="open")
run_query("Login Keyword Search", results, keyword="login")
run_query("Refund Keyword Search", results, keyword="refund")
run_query("Needs Review Random Search", results, status="needs_review", keyword="random")
run_query(
    "Sorted High Breached",
    results,
    priority="high",
    breached=True,
    sort_by="sla"
)

run_query(
    "Login Tickets Sorted by Priority",
    results,
    category="login",
    sort_by="priority"
)
##Hashing out since we now do the same for all actions in one reporting function
# run_query("To be followed Up later", action_queue, action="follow_up_soon")
run_daily_workflow(results)