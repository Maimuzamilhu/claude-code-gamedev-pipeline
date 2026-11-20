"""Tiny client for the MCP for Unity HTTP server (no dependencies).

  python unity_bridge.py -c "return Application.unityVersion;"     run inline C#
  python unity_bridge.py snippet.cs                                  run a C# file
  python unity_bridge.py --tool read_console '{"action":"get"}'      call any tool
  python unity_bridge.py --list                                      list tools

Set UNITY_MCP_URL to change the endpoint (default http://127.0.0.1:8080/mcp).
The MCP session id is cached next to this script and refreshed when it goes stale.
"""
import json
import os
import sys
import urllib.error
import urllib.request

URL = os.environ.get("UNITY_MCP_URL", "http://127.0.0.1:8080/mcp")
SID_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".unity_mcp_session")


def _post(payload, sid=None, timeout=600):
    req = urllib.request.Request(URL, data=json.dumps(payload).encode("utf-8"), method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json, text/event-stream")
    if sid:
        req.add_header("Mcp-Session-Id", sid)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        sid = r.headers.get("Mcp-Session-Id") or sid
        body = r.read().decode("utf-8", "replace")
        ctype = r.headers.get("Content-Type", "")
    if "text/event-stream" in ctype:
        msg = None
        for line in body.splitlines():
            if line.startswith("data:"):
                try:
                    obj = json.loads(line[5:].strip())
                except ValueError:
                    continue
                if "result" in obj or "error" in obj:
                    msg = obj
        return sid, msg
    return sid, (json.loads(body) if body.strip() else None)


def _session():
    if os.path.exists(SID_FILE):
        return open(SID_FILE).read().strip()
    sid, _ = _post({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                    "params": {"protocolVersion": "2025-03-26", "capabilities": {},
                               "clientInfo": {"name": "unity-bridge-cli", "version": "1"}}})
    _post({"jsonrpc": "2.0", "method": "notifications/initialized"}, sid)
    with open(SID_FILE, "w") as f:
        f.write(sid or "")
    return sid


def call(method, params):
    payload = {"jsonrpc": "2.0", "id": 2, "method": method, "params": params}
    try:
        return _post(payload, _session())[1]
    except urllib.error.HTTPError as e:
        if e.code in (400, 404) and os.path.exists(SID_FILE):  # stale session: start a new one
            os.remove(SID_FILE)
            return _post(payload, _session())[1]
        raise


def _print(msg):
    if msg is None:
        print("(no response - a long call may still be running in the editor)")
        return 1
    if "error" in msg:
        print("ERROR", json.dumps(msg["error"]))
        return 1
    for c in msg["result"].get("content", []):
        if c.get("type") != "text":
            continue
        try:
            d = json.loads(c["text"])
        except ValueError:
            print(c["text"])
            continue
        if isinstance(d, dict) and "success" in d:
            if d["success"]:
                r = (d.get("data") or {}).get("result")
                print(r if r is not None else d.get("message"))
            else:
                print("FAILED:", d.get("message"), json.dumps(d.get("data"))[:2000])
                return 1
        else:
            print(json.dumps(d, indent=1)[:4000])
    return 0


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    if argv[0] == "--list":
        m = call("tools/list", {})
        print(", ".join(t["name"] for t in m["result"]["tools"]))
        return 0
    if argv[0] == "--tool":
        args = json.loads(argv[2]) if len(argv) > 2 else {}
        return _print(call("tools/call", {"name": argv[1], "arguments": args}))
    code = argv[1] if argv[0] == "-c" else open(argv[0], encoding="utf-8").read()
    return _print(call("tools/call", {"name": "execute_code",
                                      "arguments": {"action": "execute", "code": code}}))


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except urllib.error.URLError as e:
        print("Cannot reach Unity at %s (%s). Is the editor open with the MCP server started?" % (URL, e.reason))
        sys.exit(1)
