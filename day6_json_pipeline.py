import json
import os
from openai import OpenAI

client = OpenAI()

# Load incoming tickets
with open("tickets.json", "r") as file:
    tickets = json.load(file)

results = []

new_category_counts = {
    "login": 0,
    "payment": 0,
    "refund": 0,
    "other": 0
}
Total_category_count ={
    "login": 0,
    "payment": 0,
    "refund": 0,
    "other": 0
}

processed_ids = set()
processed_count = 0
skipped_count = 0

# Load already processed tickets if the file exists
if os.path.exists("classified_tickets.json"):
    try:
        with open("classified_tickets.json", "r") as file:
            existing_results = json.load(file)
    except json.JSONDecodeError:
        existing_results = []

    for ticket in existing_results:
        processed_ids.add(ticket["id"])

    results = existing_results

# Process tickets
for ticket in tickets:
    ticket_id = ticket["id"]
    ticket_text = ticket["text"]

#Skipping Processed Tickets
    if ticket_id in processed_ids:
        print(f"Skipping ticket {ticket_id} (already classified)")
        skipped_count += 1
        continue

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=f"""
Classify the support ticket into ONE category only.

Categories:
login
payment
refund
other

Return ONLY the category word.

Ticket: {ticket_text}
"""
    )

    category = response.output_text.strip()

    print(f""":
            Ticket :{ticket_id }
            Category:  {category}
            Text:  {ticket_text}
            """)

    results.append({
        "id": ticket_id,
        "text": ticket_text,
        "category": category
    })
    processed_count += 1

    if category in new_category_counts:
        category_counts[category] += 1
    else:
        new_category_counts["other"] += 1

# Save results
with open("classified_tickets.json", "w") as file:
    json.dump(results, file, indent=4)

print("\nCategory Summary")
print("----------------")

for category, count in new_category_counts.items():
    print(f"{category:<7} : {count}")

print("\nTotal Tickets So Far")
print("--------------------")

for category, count in Total_category_count.items():
    print(f"{category:<7} : {count}")

print("\nProcessing Summary")
print("------------------")
print("New tickets processed:", processed_count)
print("Tickets skipped:", skipped_count)