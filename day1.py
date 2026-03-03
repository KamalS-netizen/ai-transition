tickets=["login issue", "payment failed", "account locked", "login Issue"]
total=len(tickets)
Login=0
for ticket in tickets:
    if "login" in ticket.lower():
        Login = Login + 1
print(total)
print(Login)

print("----- Summary -----")
print("Total tickets:", total)
print("Login related tickets:", Login)