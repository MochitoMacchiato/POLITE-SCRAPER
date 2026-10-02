import requests

r = requests.get("https://books.toscrape.com/robots.txt", timeout=5)
print(r.status_code, r.text)