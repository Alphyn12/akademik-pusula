import asyncio
import json

async def dump_mcp_tools():
    proc = await asyncio.create_subprocess_exec(
        "npx.cmd", "-y", "@saidsurucu/yoktez-mcp",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    init_msg = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1.0.0"}
        }
    }
    
    proc.stdin.write((json.dumps(init_msg) + "\n").encode())
    await proc.stdin.drain()
    
    # Read until initialize response
    while True:
        line = await proc.stdout.readline()
        if not line:
            print("Process closed unexpectedly")
            break
        try:
            resp = json.loads(line.decode().strip())
            if resp.get("id") == 1:
                break
        except json.JSONDecodeError:
            pass
            
    notif_msg = {
        "jsonrpc": "2.0",
        "method": "notifications/initialized",
        "params": {}
    }
    proc.stdin.write((json.dumps(notif_msg) + "\n").encode())
    await proc.stdin.drain()
    
    tools_msg = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    proc.stdin.write((json.dumps(tools_msg) + "\n").encode())
    await proc.stdin.drain()
    
    while True:
        line = await proc.stdout.readline()
        if not line:
            break
        try:
            resp = json.loads(line.decode().strip())
            if resp.get("id") == 2:
                print("TOOLS RESPONSE:", json.dumps(resp, indent=2))
                break
        except json.JSONDecodeError:
            pass
            
    proc.terminate()

asyncio.run(dump_mcp_tools())
