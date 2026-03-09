import json
tickets = [
    "User cannot LOGIN to account",
    "Payment failed for subscription",
    "Login page not loading",
    "User requesting refund",
    "Login error after password reset",
    "Customer login failed during payment",
    "Shipping delay complaint"
]

#keywords = ["login", "refund", "payment"]
user_input = input("Enter keywords separated by commas: ").split(",")
keywords = [k.strip() for k in user_input]
ticket_counts = {}
counter=0

for issue in keywords:
    ticket_counts[issue] = {"count": 0, "tickets": []}  # ✅ new way
# for ticket in tickets:
#     for issue in keywords:
#         if issue.lower() in ticket.lower():
#             ticket_counts[issue] += 1
#             counter+=1
#             break
other_tickets = []

for ticket in tickets:
    matched = False
    for issue in keywords:
        if issue.lower() in ticket.lower():
            ticket_counts[issue]["count"] += 1
            ticket_counts[issue]["tickets"].append(ticket)
            matched = True
            break
    if not matched:
        other_tickets.append(ticket)

ticket_counts["other"] = len(tickets) - counter
print(json.dumps(ticket_counts, indent=4))