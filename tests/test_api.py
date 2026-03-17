import requests
import urllib.parse
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

query = "SAE 8620 steel heat treatment"
start_year = 2015
end_year = 2026

print("--- CROSSREF TEST ---")
try:
    # Use query.bibliographic instead of just query, add mailto to polite pool
    # Remove select to see if that caused 400
    url = f"https://api.crossref.org/works?query.bibliographic={urllib.parse.quote(query)}&filter=from-pub-date:{start_year},until-pub-date:{end_year}&rows=3"
    headers = {'User-Agent': 'AkademikPusula/1.0 (mailto:test@example.com)'}
    response = requests.get(url, headers=headers, timeout=10)
    print("Status:", response.status_code)
    if response.status_code == 200:
        data = response.json()
        items = data.get('message', {}).get('items', [])
        for item in items:
            print("-", item.get('title', ['No Title'])[0])
    else:
        print("Error content:", response.text[:200])
except Exception as e:
    print("Crossref Error:", e)

print("\n--- ARXIV TEST ---")
try:
    # Use quotes for exact phrase or use ti/abs instead of all
    # search_query=all:"SAE 8620 steel heat treatment"
    exact_query = f'"{query}"'
    url = f"http://export.arxiv.org/api/query?search_query=all:{urllib.parse.quote(exact_query)}&start=0&max_results=3"
    response = requests.get(url, timeout=10)
    print("Status:", response.status_code)
    soup = BeautifulSoup(response.text, 'xml')
    entries = soup.find_all('entry')
    if not entries:
        print("No entries found with exact query. Trying without quotes but ti: (title)")
        url2 = f"http://export.arxiv.org/api/query?search_query=ti:{urllib.parse.quote(query)}&start=0&max_results=3"
        response2 = requests.get(url2, timeout=10)
        soup2 = BeautifulSoup(response2.text, 'xml')
        entries = soup2.find_all('entry')
        
    for entry in entries:
        title = entry.title.text.strip().replace('\n', ' ')
        print("-", title)
except Exception as e:
    print("arXiv Error:", e)
