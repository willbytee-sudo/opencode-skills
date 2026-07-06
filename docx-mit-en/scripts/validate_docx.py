#!/usr/bin/env python3
"""
Practical validation of a .docx: checks the ZIP is intact, the XML parts are well-formed,
the required parts exist, and python-docx can open it. Own implementation (MIT). Stdlib +
lxml + python-docx only.

Usage:
    python -X utf8 validate_docx.py document.docx

Always run with `-X utf8` on Windows.
"""
import sys
import zipfile

from lxml import etree

REQUIRED = ("[Content_Types].xml", "word/document.xml")


def main():
    if len(sys.argv) != 2:
        print("usage: python -X utf8 validate_docx.py <document.docx>")
        sys.exit(1)

    path = sys.argv[1]
    errors = []

    try:
        z = zipfile.ZipFile(path)
    except (zipfile.BadZipFile, FileNotFoundError) as e:
        print(f"✗ Not a valid .docx/ZIP: {e}")
        sys.exit(2)

    if z.testzip():
        errors.append("corrupt ZIP")

    names = set(z.namelist())
    for req in REQUIRED:
        if req not in names:
            errors.append(f"missing required part: {req}")

    for name in z.namelist():
        if name.endswith((".xml", ".rels")):
            try:
                etree.fromstring(z.read(name))
            except etree.XMLSyntaxError as e:
                errors.append(f"malformed XML in {name}: {e}")

    paragraphs = None
    try:
        from docx import Document
        paragraphs = len(Document(path).paragraphs)
    except Exception as e:  # noqa: BLE001
        errors.append(f"python-docx could not open it: {e}")

    if errors:
        print("✗ VALIDATION FAILED:")
        for e in errors:
            print("  -", e)
        sys.exit(1)

    print(f"✓ VALIDATION OK — ZIP intact, XML well-formed, required parts present, "
          f"python-docx opens it ({paragraphs} paragraphs)")


if __name__ == "__main__":
    main()
