import json
tickets = [
    "User cannot login to account",
    "Payment failed for subscription",
    "Login page not loading",
    "User requesting refund",
    "Login error after password reset",
    "Customer login failed during payment",
    "Shipping delay complaint"
]

#keywords = ["login", "refund", "payment"]
user_input = input("Enter keywords separated by commas: ")
keywords = user_input.split(",")
ticket_counts = {}
counter=0

for issue in keywords:
    ticket_counts[issue] = 0


for ticket in tickets:
    for issue in keywords:
        if issue.lower() in ticket.lower():
            ticket_counts[issue] += 1
            counter+=1
            break

ticket_counts["other"] = len(tickets) - counter
print(json.dumps(ticket_counts, indent=4))