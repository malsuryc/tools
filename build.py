import os
import re
import json

# Configuration
INDEX_FILE = "index.html"
MARKER_START = "// <!-- AUTO-GENERATED:START -->"
MARKER_END = "// <!-- AUTO-GENERATED:END -->"


def extract_metadata(file_path):
    """Extracts tool metadata from an HTML file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Helper to extract meta content by name (for tool:*)
    def get_tool_meta(name):
        match = re.search(
            r'<meta\s+name=["\']tool:'
            + re.escape(name)
            + r'["\']\s+content=["\'](.*?)["\']',
            content,
        )
        return match.group(1) if match else None

    # Helper to extract meta content by property (for og:*)
    def get_og_meta(prop):
        match = re.search(
            r'<meta\s+property=["\']'
            + re.escape(prop)
            + r'["\']\s+content=["\'](.*?)["\']',
            content,
        )
        return match.group(1) if match else None

    title = get_og_meta("og:title")
    if not title:
        return None  # Not a tool file

    desc = get_og_meta("og:description") or ""
    tags_str = get_tool_meta("tags") or ""
    tags = [t.strip() for t in tags_str.split(",")] if tags_str else []
    is_new = get_tool_meta("is_new") == "true"

    return {
        "id": os.path.splitext(os.path.basename(file_path))[0],
        "title": title,
        "desc": desc,
        "path": f"./{os.path.basename(file_path)}",
        "tags": tags,
        "isNew": is_new,
    }


def main():
    tools = []

    # Scan directory
    for filename in os.listdir("."):
        if filename.endswith(".html") and filename != INDEX_FILE:
            print(f"Processing {filename}...")
            tool_data = extract_metadata(filename)
            if tool_data:
                tools.append(tool_data)
                print(f"  Found tool: {tool_data['title']}")
            else:
                print("  Skipping (no tool metadata found)")

    # Sort tools (optional, e.g., by title or newness)
    tools.sort(key=lambda x: x["title"])

    # Generate JS code
    tools_json = json.dumps(tools, indent=4)
    new_content_block = (
        f"{MARKER_START}\n        const tools = {tools_json};\n        {MARKER_END}"
    )

    # Update index.html
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        index_content = f.read()

    # Regex to replace the block
    pattern = re.compile(
        re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END), re.DOTALL
    )

    if not pattern.search(index_content):
        print(f"Error: Markers not found in {INDEX_FILE}")
        return

    updated_content = pattern.sub(new_content_block, index_content)

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(updated_content)

    print(f"Successfully updated {INDEX_FILE} with {len(tools)} tools.")


if __name__ == "__main__":
    main()
