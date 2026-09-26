def generate_markdown_comment(
    target_function,
    blast_radius,
    dependency_tree,
    test_commands
):
    comment = ""

    comment += "## 💥 Blast Radius Report\n\n"

    comment += "<details>\n"
    comment += "<summary>🔍 Modified Function</summary>\n\n"
    comment += f"**{target_function}** was modified in this PR.\n\n"
    comment += "</details>\n\n"

    comment += "---\n\n"

    comment += "<details>\n"
    comment += "<summary>⚠️ Impact Level</summary>\n\n"
    comment += "[🔴](https://discord.com/assets/75d49373b7b7ee6f.svg) High\n\n"
    comment += "[🟠](https://discord.com/assets/aa280fe3f1679fdf.svg) Medium\n\n"
    comment += "[🟢](https://discord.com/assets/2d6d478121939bde.svg) Low\n\n"
    comment += "</details>\n\n"

    comment += "---\n\n"

    comment += "<details>\n"
    comment += "<summary>🌳 Dependency Tree</summary>\n\n"
    comment += "```text\n"
    comment += dependency_tree
    comment += "\n```\n\n"
    comment += "</details>\n\n"

    comment += "---\n\n"

    comment += "<details>\n"
    comment += "<summary>🧪 Watsonx Recommended Tests</summary>\n\n"

    for command in test_commands:
        comment += f"- `{command}`\n"

    comment += "\n</details>\n\n"

    comment += "---\n\n"
    comment += "*Generated automatically by Blast Radius.*\n"

    return comment