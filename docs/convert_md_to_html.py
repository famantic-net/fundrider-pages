#!/usr/bin/env python3
"""
convert_md_to_html.py

A simple command-line utility to convert a Markdown file to a styled HTML document.
"""

import argparse
import sys

# Requires the 'markdown' package: install with `pip install markdown`
import markdown

# Updated HTML template with more inline CSS
TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
    body {{
      font-family: 'Inter', Arial, sans-serif; /* Modern font */
      font-size: 11pt;
      line-height: 1.6; /* Improved line spacing */
      margin: 0; /* Remove default margin */
      padding: 0; /* Remove default padding */
      background-color: #f4f4f9; /* Light gray background */
      color: #333; /* Darker text for better contrast */
      display: flex;
      flex-direction: column;
      align-items: center;
    }}
    .container {{
      background-color: #ffffff; /* White content background */
      margin: 2rem;
      padding: 1.5rem 2.5rem; /* More padding inside the content area */
      max-width: 800px;
      width: calc(100% - 4rem); /* Responsive width with padding */
      box-shadow: 0 4px 12px rgba(0,0,0,0.08); /* Subtle shadow for depth */
      border-radius: 8px; /* Rounded corners for the container */
    }}
    h1, h2, h3, h4, h5, h6 {{
      margin-top: 1.8rem;
      margin-bottom: 0.8rem;
      font-weight: 600; /* Bolder headings */
      color: #2c3e50; /* Dark blue-gray for headings */
    }}
    h1 {{
      font-size: 2.2em;
      border-bottom: 2px solid #e0e0e0; /* Lighter border */
      padding-bottom: 0.4rem;
    }}
    h2 {{
      font-size: 1.8em;
      border-bottom: 1px solid #eee;
      padding-bottom: 0.3rem;
    }}
    h3 {{
      font-size: 1.5em;
    }}
    p {{
      margin-bottom: 1rem;
    }}
    a {{
      color: #3498db; /* Clearer link color */
      text-decoration: none; /* No underline by default */
    }}
    a:hover {{
      text-decoration: underline; /* Underline on hover */
      color: #2980b9;
    }}
    ul, ol {{
      margin-left: 1.5rem;
      padding-left: 0.5rem; /* Adjusted padding */
    }}
    li {{
      margin-bottom: 0.5rem; /* Increased spacing between list items */
    }}
    code {{
      background-color: #ecf0f1; /* Light background for inline code */
      padding: 0.2em 0.4em;
      margin: 0 0.1em;
      font-size: 0.85em;
      border-radius: 3px;
      font-family: 'Courier New', Courier, monospace;
    }}
    pre {{
      background-color: #2c3e50; /* Dark background for code blocks */
      color: #f8f8f2; /* Light text for code blocks */
      padding: 1rem;
      border-radius: 5px;
      overflow-x: auto; /* Allow horizontal scrolling for long lines */
      font-size: 0.9em;
      line-height: 1.45;
    }}
    pre code {{
      background-color: transparent; /* Code inside pre should not have its own background */
      padding: 0;
      margin: 0;
      font-size: inherit; /* Inherit font size from pre */
      color: inherit; /* Inherit color */
    }}
    blockquote {{
      border-left: 4px solid #3498db; /* Blue left border for blockquotes */
      margin-left: 0;
      padding-left: 1rem;
      color: #555;
      font-style: italic;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 1rem;
      margin-bottom: 1rem;
      box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }}
    th, td {{
      border: 1px solid #ddd;
      padding: 0.75rem;
      text-align: left;
    }}
    th {{
      background-color: #f9f9f9; /* Light background for table headers */
      font-weight: 600;
    }}
    img {{
      max-width: 100%;
      height: auto;
      border-radius: 4px; /* Rounded corners for images */
      margin-top: 0.5rem;
      margin-bottom: 0.5rem;
    }}
    hr {{
        border: none;
        border-top: 1px solid #e0e0e0;
        margin: 2rem 0;
    }}
  </style>
</head>
<body>
  <div class="container">
{body}
  </div>
</body>
</html>
"""

def convert(markdown_text: str) -> str:
    """
    Convert Markdown text to HTML using the TEMPLATE.
    The HTML <title> is fixed to "Fundrider Daily Charts Info".
    The 'extra' extension enables features like tables, fenced code blocks, etc.
    The 'toc' extension can generate a table of contents (though not used in template by default).
    """
    # Using 'extra' for features like tables, fenced code, footnotes.
    # Using 'sane_lists' for more predictable list parsing.
    # Using 'codehilite' for syntax highlighting if Pygments is installed.
    #   Install with: pip install Pygments
    #   If Pygments is not installed, code blocks will still be formatted by 'pre' style.
    html_body = markdown.markdown(
        markdown_text,
        extensions=['extra', 'sane_lists', 'codehilite', 'toc']
    )

    # Set the title to the desired fixed value.
    # The logic for extracting title from H1 has been removed.
    title = "Fundrider Daily Charts Info"

    return TEMPLATE.format(title=title, body=html_body)

def main():
    parser = argparse.ArgumentParser(
        description="Convert a Markdown file to a styled HTML document."
    )
    parser.add_argument(
        "input",
        nargs="?",
        type=argparse.FileType('r', encoding='utf-8'), # Specify UTF-8 encoding
        default=sys.stdin,
        help="Input Markdown file (default: stdin)"
    )
    parser.add_argument(
        "-o", "--output",
        type=argparse.FileType('w', encoding='utf-8'), # Specify UTF-8 encoding
        default=sys.stdout,
        help="Output HTML file (default: stdout)"
    )
    args = parser.parse_args()

    try:
        md_text = args.input.read()
        html_output = convert(md_text)
        args.output.write(html_output)
    except Exception as e:
        sys.stderr.write(f"Error during conversion: {e}\n")
        sys.exit(1)
    finally:
        # Ensure files are closed if they are not stdin/stdout
        if args.input is not sys.stdin:
            args.input.close()
        if args.output is not sys.stdout:
            args.output.close()

if __name__ == "__main__":
    main()
