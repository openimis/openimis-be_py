import requests
import json

# Test GraphQL query directly to backend
url = "http://127.0.0.1:8000/api/graphql"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer YOUR_JWT_TOKEN_HERE"  # Replace with real token
}

query = '''
query {
  opensearchDashboard(name_Iexact: "Individual") {
    edges {
      node {
        id
        name
        url
        synchDisabled
      }
    }
  }
}
'''

payload = {
    "query": query
}

try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print("Response:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")