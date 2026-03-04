tickets = [
    "User cannot login to account",
    "Payment failed for subscription",
    "Login page not loading",
    "User requesting refund",
    "Login error after password reset"
]
keywords = ["login", "refund", "payment"]

def count_total_tickets(ticket_list):
    return len(ticket_list)

def count_keyword_tickets(ticket_list, keyword):
    count = 0
    for ticket in ticket_list:
        if keyword.lower() in ticket.lower():
            count += 1
    return count

# def summary_function(ticket_list):
#     print("Ticket Summary",)  
#     total=count_total_tickets(tickets)
#     login_count=count_keyword_tickets(tickets,"login")
#     refund_tickets=count_keyword_tickets(tickets,"refund")
#     print("Total Ticket:",total)
#     print("Login Ticket:", login_count)
#     print("Refund Tickets:",refund_tickets)

def summary_function(ticket_list, disposition):

    print("----- Ticket Summary -----")
    total = count_total_tickets(ticket_list)
    print("Total tickets:", total)
    for issue in disposition:
            count = count_keyword_tickets(ticket_list, issue)
            print(issue.capitalize(), "tickets:", count)


    

if __name__ == "__main__":
    summary_function(tickets, keywords)