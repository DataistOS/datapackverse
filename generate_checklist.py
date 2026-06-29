import json
import urllib.request
import urllib.error

def calculate_progress(version):
    """Calculate progress percentage based on semantic versioning (handles suffixes)."""
    # Remove any suffix like -alpha or -beta to handle semantic strings
    clean_version = version.split('-')[0]
    try:
        major, minor, patch = map(int, clean_version.split('.'))
    except (ValueError, IndexError):
        return "5%"

    if major >= 1:
        return "100%"
    elif minor > 0:
        # Progress increases by 10% for each minor version
        progress = min(20 + (minor * 10), 90)
        return f"{progress}%"
    elif patch > 0:
        # Progress increases by 5% for each patch version
        progress = min(patch * 5, 15)
        return f"{progress}%"
    else:
        return "5%"

def get_remote_version(tool_name):
    """Fetch version from GitHub raw file."""
    url = f"https://raw.githubusercontent.com/DataistOS/{tool_name}/heuristic/VERSION"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return response.read().decode('utf-8').strip()
    except Exception:
        return None

def update_and_generate():
    """Sync tool versions from GitHub and generate output documents with compact formatting."""
    json_path = 'tools.json'

    # Read existing tools data
    with open(json_path, 'r', encoding='utf-8') as f:
        tools = json.load(f)

    # 1. Update version field from GitHub
    for t in tools:
        print(f"Checking version for {t['name']}...")
        remote_version = get_remote_version(t['name'])
        if remote_version:
            t['version'] = remote_version

    # 2. Save updated tools.json in compact format (one object per line)
    with open(json_path, 'w', encoding='utf-8') as f:
        f.write("[\n")
        for i, tool in enumerate(tools):
            line = json.dumps(tool, ensure_ascii=False)
            if i < len(tools) - 1:
                f.write(f" {line},\n")
            else:
                f.write(f" {line}\n")
        f.write("]")
    print("tools.json updated successfully in compact format.")

    # 3. Generate RST formatted checklist based on updated data
    header = """Tool Status Checklist
=====================

.. list-table:: Current status of Dataist ecosystem tools
   :widths: 20 15 15 15 20
   :header-rows: 1

   * - Tool Name
     - Version
     - GitHub Repo
     - Logo Status
     - Progress
"""

    rows = ""
    for t in tools:
        progress = calculate_progress(t['version'])
        rows += f"   * - {t['name']}\n"
        rows += f"     - {t['version']}\n"
        rows += f"     - ✅\n"
        rows += f"     - ✅\n"
        rows += f"     - {progress}\n"

    with open('checklist.rst', 'w', encoding='utf-8') as f:
        f.write(header + rows)

    print("checklist.rst generated successfully.")

if __name__ == "__main__":
    update_and_generate()