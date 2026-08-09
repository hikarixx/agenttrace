from ..storage.local import LocalStorage
def generate_pytest_file(run_id: str, output_file: str):
    storage = LocalStorage()
    try:
        data = storage.export_run(run_id)
    except Exception as e:
        print(f"Error loading run {run_id}: {e}")
        return
    run = data["run"]
    events = data["events"]
    test_code = f'"""\nAuto-generated pytest file from AgentTrace Run {run_id}\nTask: {run["task"]}\n"""\n\n'
    test_code += "import pytest\nfrom unittest.mock import patch, MagicMock\n\n"
    tools_used = []
    for evt in events:
        if evt["type"] == "tool.started":
            tools_used.append(evt)
    if not tools_used:
        print("No tools found in this run to generate tests for.")
        return
    test_code += "def test_agent_tools_execution():\n"
    for i, tool in enumerate(tools_used):
        meta = tool.get("metadata", {})
        tool_name = meta.get("tool_name", "unknown")
        input_args = meta.get("input", {})
        test_code += f"    # Test case for {tool_name}\n"
        test_code += f"    with patch('{tool_name}') as mock_{i}:\n"
        output_data = {}
        for completed_evt in events:
            if completed_evt["type"] == "tool.completed" and (completed_evt["id"] == tool["id"] or completed_evt.get("parent_id") == tool["id"]):
                output_data = completed_evt.get("metadata", {}).get("output", {})
                break
        test_code += f"        mock_{i}.return_value = {output_data}\n"
        test_code += f"        result = mock_{i}(**{input_args})\n"
        test_code += f"        assert result == {output_data}\n\n"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(test_code)
    print(f"🧪 Auto-generated pytest suite saved to {output_file}!")