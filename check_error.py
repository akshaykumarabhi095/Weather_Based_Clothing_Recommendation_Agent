import requests

# This is the key from your screenshot
API_KEY = "AIzaSyCOIUuyORBe9iCGEZTpf2WZNEnFqF_ZCYc"

print(f"Testing Key: {API_KEY[:10]}...")

# 1. Ask Google: "Why are you rejecting me?"
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
response = requests.get(url, verify=False)

print(f"\nStatus Code: {response.status_code}")
print("👇 HERE IS THE REAL ERROR MESSAGE 👇")
print(response.text)
print("👆 ------------------------------ 👆")