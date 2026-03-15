import os
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
category_counts = {
    "login": 0,
    "payment": 0,
    "refund": 0,
    "other": 0
}
tickets = [
    "User cannot login to account",
    "Payment failed during checkout",
    "Customer requesting refund",
    "Login page showing error",
         ]
ticket_report={
    "login": [],
    "payment": [],
    "refund": [],
    "other": []

}
for ticket in tickets:
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

    Ticket: {ticket}
    """
    )

    category=response.output_text.strip()
    if category in category_counts:
        category_counts[category] += 1
    else:
        category_counts["other"] += 1    
    print(f"""{ticket} -> {category}""")
    ticket_report[category].append(ticket)


print("\nSummary")
print("-------")

for category, count in category_counts.items():
    print(f"{category}: {count}")

print("\nDetailed Report")
print("---------------")

# for category, tickets in ticket_report.items():
#     print(f"\n{category.upper()}:")
#     for t in tickets:
#         print(f"- {t}")
print(ticket_report.items())