"""
This script synchronizes the version information of Dataist ecosystem tools by
fetching the latest versions from remote GitHub repositories. It updates the
local 'tools.json' file and generates a 'checklist.rst' document, providing an
overview of the ecosystem's health, progress, and category-based performance.
"""

import json
import urllib.request
import urllib.error
from collections import defaultdict
import sys

# Constants for console styling
GREEN = "\033[92m"
BLUE = "\033[94m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_progress(iteration, total, tool_name):
    """Displays a dynamic progress bar in the terminal."""
    length = 20
    filled = int(length * iteration // total)
    bar = '█' * filled + '-' * (length - filled)
    sys.stdout.write(f'\r{BLUE}Syncing:{RESET} |{bar}| {iteration}/{total} | {tool_name:<25}')
    sys.stdout.flush()
    if iteration == total:
        sys.stdout.write('\n')

def calculate_progress(version):
    """Calculates development progress percentage based on semantic versioning."""
    clean_version = version.split('-')[0]
    try:
        major, minor, patch = map(int, clean_version.split('.'))
    except (ValueError, IndexError):
        return "5%"

    if major >= 1: return "100%"
    if minor > 0: return f"{min(20 + (minor * 10), 90)}%"
    if patch > 0: return f"{min(patch * 5, 15)}%"
    return "5%"

def get_remote_version(tool_name):
    """Fetches the latest version from the remote heuristic/VERSION file."""
    url = f"https://raw.githubusercontent.com/DataistOS/{tool_name}/heuristic/VERSION"
    try:
        with urllib.request.urlopen(url, timeout=3) as response:
            content = response.read().decode('utf-8').strip()
            return content.split('"')[1] if 'echo "' in content else content
    except (urllib.error.URLError, Exception):
        return None

def update_and_generate():
    """Orchestrates version synchronization and report generation."""
    json_path = 'tools.json'
    with open(json_path, 'r', encoding='utf-8') as f:
        tools = json.load(f)

    category_stats = defaultdict(list)
    missing_versions = []
    total_score = 0

    print(f"{BOLD}{BLUE}🚀 Starting Dataist Ecosystem Sync...{RESET}")

    for i, tool in enumerate(tools, start=1):
        print_progress(i, len(tools), tool['name'])
        remote_version = get_remote_version(tool['name'])

        if remote_version:
            tool['version'] = remote_version
        else:
            missing_versions.append(tool['name'])

        score = int(calculate_progress(tool['version']).strip('%'))
        total_score += score
        category_stats[tool['category']].append(score)

    # Save updated JSON: Write each tool item on a new line for cleaner version control
    with open(json_path, 'w', encoding='utf-8') as f:
        f.write("[\n")
        for i, tool in enumerate(tools):
            # Serialize each dictionary to a single-line JSON string
            line = json.dumps(tool, ensure_ascii=False)
            # Append comma if not the last item, then add a newline
            f.write(f" {line}{',' if i < len(tools) - 1 else ''}\n")
        f.write("]")

    # Generate RST Content
    rows = []
    for i, t in enumerate(tools, start=1):
        rows.append(f"   * - {i}\n     - `{t['name']} <https://github.com/DataistOS/{t['name']}>`_\n"
                    f"     - {t['version']}\n     - {calculate_progress(t['version'])}")

    header = ("Tool Status Checklist\n=====================\n\n"
              ".. list-table:: Current status of Dataist ecosystem tools\n"
              "   :widths: 5 25 30 40\n   :header-rows: 1\n\n"
              "   * - #\n     - Tool Name\n     - Version\n     - Progress\n")

    cat_breakdown = "\n".join([f"- **{c}**: {sum(s)/len(s):.1f}%" for c, s in category_stats.items()])
    footer = (f"\n.. admonition:: Dataist Distribution Health\n\n"
              f"   Overall Ecosystem Progress: **{total_score/len(tools):.1f}%**\n\n"
              f"Category Breakdown\n------------------\n\n{cat_breakdown}")

    with open('checklist.rst', 'w', encoding='utf-8') as f:
        f.write(header + "\n".join(rows) + footer)

    print(f"{GREEN}✅ Sync Complete! Ecosystem Health: {total_score/len(tools):.1f}%{RESET}")

    if missing_versions:
        print(f"\n{BOLD}{RED}⚠️  Warning: {len(missing_versions)} repositories lack a VERSION file:{RESET}")
        for tool in missing_versions:
            print(f" - {tool}")

if __name__ == "__main__":
    update_and_generate()