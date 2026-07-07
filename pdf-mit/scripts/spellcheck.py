#!/usr/bin/env python3
"""
Proofreads the text of a .pdf and FLAGS likely mistakes so the model sees them and fixes them
before delivering. Extracts the text with pdfplumber and applies light heuristics: encoding
artifacts (mojibake), doubled words, and space-before-punctuation. Then prints the full text
for a visual proofread. Own implementation (MIT).

Usage:
    python -X utf8 spellcheck.py document.pdf

Always run with `-X utf8` on Windows. This is an ASSISTANT, not an infallible checker.
"""
import re
import sys

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


def extract_text_pdf(path: str) -> str:
    import pdfplumber
    parts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            parts.append(page.extract_text() or "")
    return "\n".join(parts)


def main():
    if len(sys.argv) != 2:
        print("usage: python -X utf8 spellcheck.py <document.pdf>")
        sys.exit(1)
    text = extract_text_pdf(sys.argv[1])
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
    print("FULL TEXT (read it for mistakes the heuristics can't catch):")
    print("-" * 70)
    print(text)


if __name__ == "__main__":
    main()
