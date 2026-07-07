#!/usr/bin/env python3
"""
Converts each page of a .pdf to PNG with PyMuPDF (fitz) — no Poppler needed. Own
implementation (MIT).

Usage:
    python -X utf8 pdf_to_images.py input.pdf output_dir/ [dpi]

Always run with `-X utf8` on Windows.
"""
import os
import sys

import fitz  # PyMuPDF


def convert(pdf_path, out_dir, dpi=200):
    os.makedirs(out_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    zoom = dpi / 72.0
    for i, page in enumerate(doc, 1):
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
        dest = os.path.join(out_dir, f"page_{i}.png")
        pix.save(dest)
        print(f"Saved {dest} ({pix.width}x{pix.height})")
    print(f"Converted {doc.page_count} pages")


if __name__ == "__main__":
    if len(sys.argv) not in (3, 4):
        print("usage: python -X utf8 pdf_to_images.py <input.pdf> <output_dir> [dpi]")
        sys.exit(1)
    dpi = int(sys.argv[3]) if len(sys.argv) == 4 else 200
    convert(sys.argv[1], sys.argv[2], dpi)
