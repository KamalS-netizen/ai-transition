import requests
url="https://jsonplaceholder.typicode.com/todos"
response = requests.get(url)
print(response)
data=response.json()
print(type(data))
#print(data)
#print("Title:", data["title"])
#print("Completed:", data["completed"])
print(data[0])
count=0
i=1

for item in data[:10]:
    status = "Completed" if item["completed"] else "Incomplete"

    print(i, item["title"])
    print("Status:", status)
    print()

    i += 1

print("Total incomplete tasks:", count)