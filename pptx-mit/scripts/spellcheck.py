#!/usr/bin/env python3
"""
Proofreads the text of a .pptx and FLAGS likely mistakes so the model sees them and fixes them
before delivering. Extracts the `<a:t>` runs by reading the ZIP directly (NO python-pptx
needed) and applies light heuristics: encoding artifacts (mojibake), doubled words, and
space-before-punctuation. Then prints the text per slide. Own implementation (MIT). Stdlib only.

Usage:
    python -X utf8 spellcheck.py presentation.pptx

Always run with `-X utf8` on Windows. This is an ASSISTANT, not an infallible checker.
"""
import re
import sys
import zipfile
from xml.etree import ElementTree as ET

A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"

MOJIBAKE = ["Ã", "Â", "Ð", "�", "â€", "Ã©", "Ã±", "Ã¡", "Ã³", "Ãº"]
DOUBLED = re.compile(r"\b(\w+)\s+\1\b", re.IGNORECASE)
SPACE_BEFORE_PUNCT = re.compile(r"\s+[,.;:!?]")


def check(text: str):
    findings = []
    for n, line in enumerate(text.splitlines(), 1):
        for mark in MOJIBAKE:
            if mark in line:
                findings.append((n, f"mojibake '{mark}' (corrupted text): {line.strip()[:80]}"))
                break
        for m in DOUBLED.finditer(line):
            findings.append((n, f"doubled word '{m.group(0)}': {line.strip()[:80]}"))
        if SPACE_BEFORE_PUNCT.search(line):
            findings.append((n, f"space before punctuation: {line.strip()[:80]}"))
    seen, unique = set(), []
    for f in findings:
        if f not in seen:
            seen.add(f); unique.append(f)
    return unique


def extract_text_pptx(path: str) -> str:
    parts = []
    with zipfile.ZipFile(path) as z:
        slides = sorted(
            (n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)),
            key=lambda s: int(re.search(r"slide(\d+)", s).group(1)),
        )
        for i, name in enumerate(slides, 1):
            parts.append(f"## Slide {i}")
            root = ET.fromstring(z.read(name))
            for t in root.iter(f"{{{A_NS}}}t"):
                if t.text and t.text.strip():
                    parts.append(t.text)
            parts.append("")
    return "\n".join(parts)


def main():
    if len(sys.argv) != 2:
        print("usage: python -X utf8 spellcheck.py <presentation.pptx>")
        sys.exit(1)
    text = extract_text_pptx(sys.argv[1])
    findings = check(text)
    print("=" * 70)
    print(f"PROOFREAD — {len(findings)} possible issue(s) flagged")
    print("=" * 70)
    if findings:
        for n, msg in findings:
            print(f"  line {n}: {msg}")
    else:
        print("  (no automatic suspects — still READ the text below)")
    print("\n" + "-" * 70)
    print("TEXT PER SLIDE (read it for mistakes the heuristics can't catch):")
    print("-" * 70)
    print(text)


if __name__ == "__main__":
    main()
