with open("debug_mcp.txt", "r", encoding="utf-8") as f:
    text = f.read()

for i, line in enumerate(text.split('\\n')):
    print(i, repr(line[:20]))
