import json
import re

with open("mcp_debug_final.log", "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()
    
# Find the JSON part
match = re.search(r'RAW RESP TEXT: event: message\n*data: (\{.*\})', text)
if match:
    json_str = match.group(1)
    data = json.loads(json_str)
    print("KEYS IN DATA:", data.keys())
    if "result" in data:
        print("KEYS IN RESULT:", data["result"].keys())
        if "content" in data["result"]:
            content = data["result"]["content"]
            print("CONTENT TYPE:", type(content))
            if isinstance(content, list):
                print("CONTENT LEN:", len(content))
        else:
            print("NO content IN result!")
else:
    print("NO JSON FOUND IN RAW RESP TEXT")
    # Let's see if there's any JSON
    for line in text.split('\\n'):
        if 'data: {' in line:
            print(line[:100])
