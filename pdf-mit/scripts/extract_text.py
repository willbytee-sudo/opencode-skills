#!/usr/bin/env python3
"""
Extracts the text of a .pdf with pdfplumber (keeps layout better than pypdf). Replaces the
sandbox-only `extract-text` binary. Own implementation (MIT).

Usage:
    python -X utf8 extract_text.py document.pdf [--tables]

With `--tables` it also tries to extract tables. Always run with `-X utf8` on Windows.
"""
import sys

import pdfplumber


def main():
    args = sys.argv[1:]
    tables = "--tables" in args
    args = [a for a in args if a != "--tables"]
    if len(args) != 1:
        print("usage: python -X utf8 extract_text.py <document.pdf> [--tables]")
        sys.exit(1)

    with pdfplumber.open(args[0]) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            print(f"## Page {i}")
            print(page.extract_text() or "")
            if tables:
                for j, table in enumerate(page.extract_tables(), 1):
                    print(f"\n[Table {j} on page {i}]")
                    for row in table:
                        print("\t".join("" if c is None else c for c in row))
            print()


if __name__ == "__main__":
    main()
