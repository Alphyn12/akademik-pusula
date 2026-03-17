import httpx
import json
import logging

def test():
    url = "https://yoktezmcp.fastmcp.app/mcp/"
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "search_yok_tez_detailed",
            "arguments": {
                "author_name": "SUSANTEZ",
                "results_per_page": 20
            }
        }
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    resp = httpx.post(url, json=payload, headers=headers)
    with open("debug_mcp.txt", "w", encoding="utf-8") as f:
        f.write(resp.text)
    print("Response saved to debug_mcp.txt")

test()
