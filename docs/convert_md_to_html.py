#!/usr/bin/env python3
"""
convert_md_to_html.py

A simple command-line utility to convert a Markdown file to a styled HTML document.
"""

import argparse
import sys

# Requires the 'markdown' package: install with `pip install markdown`
import markdown

# Basic HTML template with inline CSS
TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <style>
    body {{ font-family: Arial, sans-serif; font-size: 11pt; line-height: 1.4; margin: 2rem; max-width: 800px; }}
    h1 {{ border-bottom: 2px solid #333; padding-bottom: 0.3rem; margin-top: 2rem; }}
    ul, ol {{ margin-left: 1.5rem; }}
    li {{ margin-bottom: 0.3rem; margin-top: 0.2rem; }}
  </style>
</head>
<body>
{body}
</body>
</html>
"""

def convert(markdown_text: str) -> str:
    """
    Convert Markdown text to HTML using the TEMPLATE.
    The HTML <title> is taken from the first H1 in the Markdown.
    """
    html_body = markdown.markdown(markdown_text, extensions=['extra'])
    # Extract first H1 as title if present
    title = "Document"
    for line in markdown_text.splitlines():
        if line.startswith('# '):
            title = line.lstrip('# ').strip()
            break
    return TEMPLATE.format(title=title, body=html_body)

def main():
    parser = argparse.ArgumentParser(
        description="Convert a Markdown file to a styled HTML document."
    )
    parser.add_argument(
        "input",
        nargs="?",
        type=argparse.FileType('r'),
        default=sys.stdin,
        help="Input Markdown file (default: stdin)"
    )
    parser.add_argument(
        "-o", "--output",
        type=argparse.FileType('w'),
        default=sys.stdout,
        help="Output HTML file (default: stdout)"
    )
    args = parser.parse_args()

    md_text = args.input.read()
    html_output = convert(md_text)
    args.output.write(html_output)

if __name__ == "__main__":
    main()
