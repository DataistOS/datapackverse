import json
import urllib.request
import urllib.error

def calculate_progress(version):
    clean_version = version.split('-')[0]
    try:
        major, minor, patch = map(int, clean_version.split('.'))
    except (ValueError, IndexError):
        return "5%"

    if major >= 1:
        return "100%"
    elif minor > 0:
        progress = min(20 + (minor * 10), 90)
        return f"{progress}%"
    elif patch > 0:
        progress = min(patch * 5, 15)
        return f"{progress}%"
    else:
        return "5%"

def get_remote_version(tool_name):
    url = f"https://raw.githubusercontent.com/DataistOS/{tool_name}/heuristic/VERSION"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            content = response.read().decode('utf-8').strip()
            if 'echo "' in content:
                return content.split('"')[1]
            return content
    except Exception:
        return None

def update_and_generate():
    json_path = 'tools.json'

    with open(json_path, 'r', encoding='utf-8') as f:
        tools = json.load(f)

    for t in tools:
        print(f"Checking version for {t['name']}...")
        remote_version = get_remote_version(t['name'])
        if remote_version:
            t['version'] = remote_version

    with open(json_path, 'w', encoding='utf-8') as f:
        f.write("[\n")
        for i, tool in enumerate(tools):
            line = json.dumps(tool, ensure_ascii=False)
            if i < len(tools) - 1:
                f.write(f" {line},\n")
            else:
                f.write(f" {line}\n")
        f.write("]")
    print("tools.json updated successfully.")

    header = """Tool Status Checklist
=====================

.. list-table:: Current status of Dataist ecosystem tools
   :widths: 30 30 40
   :header-rows: 1

   * - Tool Name
     - Version
     - Progress
"""

    rows = ""
    total_score = 0
    for t in tools:
        progress_str = calculate_progress(t['version'])
        total_score += int(progress_str.replace('%', ''))
        rows += f"   * - {t['name']}\n"
        rows += f"     - {t['version']}\n"
        rows += f"     - {progress_str}\n"

    avg_progress = total_score / len(tools)

    footer = f"""
.. admonition:: Dataist Distribution Health
   
   Overall Ecosystem Progress: **{avg_progress:.1f}%**
"""

    with open('checklist.rst', 'w', encoding='utf-8') as f:
        f.write(header + rows + footer)

    print(f"checklist.rst generated successfully. Ecosystem Health: {avg_progress:.1f}%")

if __name__ == "__main__":
    update_and_generate()