import requests
import json

def test_elsevier():
    query = "machine learning"
    api_key = "2069e35f952b0b258790b9a23409618b"
    
    url = f"https://api.elsevier.com/content/search/sciencedirect?query={query}&count=5"
    print("Testing Elsevier API:", url)
    headers = {
        "Accept": "application/json",
        "X-ELS-APIKey": api_key
    }
    res = requests.get(url, headers=headers)
    print("Status code:", res.status_code)
    if res.status_code == 200:
        data = res.json()
        print(json.dumps(data, indent=2)[:500])
    else:
        print(res.text)
test_elsevier()
