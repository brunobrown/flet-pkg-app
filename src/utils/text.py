"""Text processing utilities."""

import re


def clean_readme(text: str) -> str:
    """Clean README for safe Markdown rendering.

    - Converts GitHub admonitions (> [!NOTE]) to bold text
    - Removes badge images and inline images
    - Strips HTML tags (prevents crashes in ft.Markdown)
    - Collapses excessive blank lines
    """
    text = re.sub(r">\s*\[!(NOTE|WARNING|TIP|IMPORTANT|CAUTION)]", "> **\\1:**", text)
    text = re.sub(r"\[!\[[^\]]*\]\([^)]*\)\]\([^)]*\)", "", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
