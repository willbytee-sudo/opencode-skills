#!/usr/bin/env python3
"""
Extracts the text of a .pptx, one `## Slide N` section per slide, by reading the ZIP directly
(the `<a:t>` runs). NO python-pptx needed. Replaces the sandbox-only `extract-text` binary.
Own implementation (MIT). Stdlib only.

Usage:
    python -X utf8 extract_text.py presentation.pptx

Always run with `-X utf8` on Windows.
"""
import re
import sys
import zipfile
from xml.etree import ElementTree as ET

A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"


def main():
    if len(sys.argv) != 2:
        print("usage: python -X utf8 extract_text.py <presentation.pptx>")
        sys.exit(1)

    with zipfile.ZipFile(sys.argv[1]) as z:
        slides = sorted(
            (n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)),
            key=lambda s: int(re.search(r"slide(\d+)", s).group(1)),
        )
        for i, name in enumerate(slides, 1):
            print(f"## Slide {i}")
            root = ET.fromstring(z.read(name))
            for t in root.iter(f"{{{A_NS}}}t"):
                if t.text and t.text.strip():
                    print(t.text)
            print()


if __name__ == "__main__":
    main()
