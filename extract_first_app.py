import json

log_path = "/Users/azraozcelik/.gemini/antigravity/brain/4e2f1d56-faf3-48de-ac6c-54f3076d0deb/.system_generated/logs/transcript.jsonl"

with open(log_path, "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        if data.get("type") == "PLANNER_RESPONSE":
            tools = data.get("tool_calls", [])
            for t in tools:
                if t.get("name") == "write_to_file" and "app.py" in t.get("args", {}).get("TargetFile", ""):
                    with open("first_app_code.py", "w") as out:
                        out.write(t["args"]["CodeContent"])
                    print("Found and extracted!")
                    exit(0)
