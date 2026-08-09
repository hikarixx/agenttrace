import json
from ..storage.local import LocalStorage
def export_openai_dataset(output_file: str):
    storage = LocalStorage()
    runs = storage.list_runs(limit=1000)
    dataset_lines = []
    for run in runs:
        if run.status.value != "completed":
            continue
        try:
            data = storage.export_run(run.id)
            messages = [{"role": "system", "content": "You are a helpful AI assistant executing tasks."}]
            for event in data["events"]:
                meta = event.get("metadata", {})
                if event["type"] == "tool.started":
                    messages.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [{"id": f"call_{event['id'][:8]}", "type": "function", "function": {"name": meta.get("tool_name", ""), "arguments": json.dumps(meta.get("input", {}))}}]
                    })
                elif event["type"] == "tool.completed":
                    messages.append({
                        "role": "tool",
                        "tool_call_id": f"call_{event['parent_id'][:8]}" if event.get("parent_id") else f"call_{event['id'][:8]}",
                        "content": json.dumps(meta.get("output", {}))
                    })
            if len(messages) > 1:
                dataset_lines.append({"messages": messages})
        except Exception:
            continue
    if not dataset_lines:
        print("No valid completed runs found to export.")
        return
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in dataset_lines:
            f.write(json.dumps(line) + "\n")
    print(f"✨ Successfully exported {len(dataset_lines)} conversations to {output_file} in OpenAI JSONL format!")