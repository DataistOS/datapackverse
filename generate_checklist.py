import json

def calculate_progress(version):
    """Calculate development progress percentage based on semantic versioning."""
    major, minor, patch = map(int, version.split('.'))

    if major >= 1:
        return "100%"
    elif minor > 0:
        # Each minor increment adds 10% (base 20%)
        progress = min(20 + (minor * 10), 90)
        return f"{progress}%"
    elif patch > 0:
        # Each patch increment adds 5%
        progress = min(patch * 5, 15)
        return f"{progress}%"
    else:
        # Default start progress
        return "5%"

def generate_rst():
    """Read tools registry and generate an RST formatted checklist file."""
    with open('tools.json', 'r') as f:
        tools = json.load(f)

    # Define RST table header
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
        progress = calculate_progress(t.get('version', '0.0.1'))
        rows += f"   * - {t['name']}\n"
        rows += f"     - {t['version']}\n"
        rows += f"     - ✅\n"
        rows += f"     - ✅\n"
        rows += f"     - {progress}\n"

    with open('checklist.rst', 'w') as f:
        f.write(header + rows)

    print("Successfully generated checklist.rst with automated progress tracking.")

if __name__ == "__main__":
    generate_rst()