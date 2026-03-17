import httpx
import json

def test():
    url = "https://yoktezmcp.fastmcp.app/mcp/"
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    resp = httpx.post(url, json=payload, headers=headers)
    
    for line in resp.text.split('\n'):
        if line.startswith('data: '):
            data = json.loads(line[6:])
            tools = data.get("result", {}).get("tools", [])
            for t in tools:
                if t.get('name') == 'search_yok_tez_detailed':
                    with open('schema_raw.txt', 'w', encoding='utf-8') as f:
                        f.write(json.dumps(t.get('inputSchema'), indent=2))

test()
