import json
import os
from openai import OpenAI

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
Classify the support ticket using both category and priority.

Category options:
login
payment
refund
other

Priority rules:
high = user is blocked, issue is urgent, or impact is severe
medium = important issue but not fully blocking
low = minor issue, typo, general question, or low urgency

Return ONLY valid JSON in this format:

{{"category": "login", "priority": "high"}}

Ticket: {ticket_text}
"""
        )

        result = response.output_text.strip()

    except Exception as e:
        print(f"API call failed for ticket: {ticket_text}")
        print("Error:", e)
        return "other", "low"

    try:
        data = json.loads(result)
        category = data["category"].strip().lower()
        priority = data["priority"].strip().lower()

        valid_categories = {"login", "payment", "refund", "other"}
        valid_priorities = {"high", "medium", "low"}

        if category not in valid_categories:
            category = "other"

        if priority not in valid_priorities:
            priority = "low"

    except (json.JSONDecodeError, KeyError):
        print(f"AI returned unexpected JSON format for ticket: {result}")
        category = "other"
        priority = "low"

    return category, priority


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


def print_summary(title, counts):
    print(f"\n{title}")
    print("-" * len(title))

    for label, count in counts.items():
        print(f"{label:<7} : {count}")


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


def print_triage_queue(sorted_results):
    print("\nTriage Queue")
    print("------------")

    for ticket in sorted_results:
        if ticket["priority"] != "low":
            print(
                f'ID: {ticket["id"]} | '
                f'Priority: {ticket["priority"]:<6} | '
                f'Category: {ticket["category"]:<7} | '
                f'Text: {ticket["text"]}'
            )


def print_processing_summary(processed_count, skipped_count):
    print("\nProcessing Summary")
    print("------------------")
    print("New tickets processed:", processed_count)
    print("Tickets skipped:", skipped_count)


tickets = load_tickets()
results, processed_ids = load_existing_results()

category_counts = build_new_category_counts()
priority_counts = build_new_priority_counts()

processed_count = 0
skipped_count = 0

for ticket in tickets:
    ticket_id = ticket["id"]
    ticket_text = ticket["text"]

    if ticket_id in processed_ids:
        print(f"Skipping ticket {ticket_id} (already classified)")
        skipped_count += 1
        continue

    category, priority = classify_ticket(ticket_text)

    print(f"{ticket_id}: {ticket_text} -> {category}, {priority}")

    results.append({
        "id": ticket_id,
        "text": ticket_text,
        "category": category,
        "priority": priority
    })

    processed_count += 1

    if category in category_counts:
        category_counts[category] += 1
    else:
        category_counts["other"] += 1

    if priority in priority_counts:
        priority_counts[priority] += 1

with open("classified_tickets_day7.json", "w") as file:
    json.dump(results, file, indent=4)

total_category_counts = build_total_category_counts(results)
total_priority_counts = build_total_priority_counts(results)
sorted_results = build_sorted_results(results)
open_queue_counts = build_open_queue_counts(results)

print_summary("New Category Summary", category_counts)
print_summary("New Priority Summary", priority_counts)
print_summary("Total Category Summary", total_category_counts)
print_summary("Total Priority Summary", total_priority_counts)
print_summary("Open Queue Summary", open_queue_counts)
print_triage_queue(sorted_results)
print_processing_summary(processed_count, skipped_count)