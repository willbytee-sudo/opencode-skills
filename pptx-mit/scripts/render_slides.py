#!/usr/bin/env python3
"""
Renders a .pptx to one PNG per slide for visual review. Uses LibreOffice (soffice) to convert
to PDF and then PyMuPDF (fitz) to split the PDF into images — so it needs NO Poppler. Own
implementation (MIT).

Usage:
    python -X utf8 render_slides.py presentation.pptx [output_dir] [dpi]

Requires LibreOffice installed (soffice on PATH, or SOFFICE_BIN with the path) and PyMuPDF (✅).
Always run with `-X utf8` on Windows.
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import fitz  # PyMuPDF


def find_soffice() -> str:
    cand = os.environ.get("SOFFICE_BIN") or shutil.which("soffice") or shutil.which("soffice.exe")
    if cand:
        return cand
    for p in (r"C:\Program Files\LibreOffice\program\soffice.exe",
              r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"):
        if Path(p).exists():
            return p
    print("✗ LibreOffice (soffice) not found. Install it and add it to PATH, or set SOFFICE_BIN "
          "to the path of soffice.exe.", file=sys.stderr)
    sys.exit(1)


def render(pptx_path, out_dir, dpi=150):
    soffice = find_soffice()
    src = Path(pptx_path)
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        r = subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", tmp, str(src)],
                           capture_output=True, encoding="utf-8", errors="replace")
        pdf = Path(tmp) / f"{src.stem}.pdf"
        if r.returncode != 0 or not pdf.exists():
            print(f"✗ PDF conversion with LibreOffice failed.\n{r.stdout}\n{r.stderr}", file=sys.stderr)
            sys.exit(1)
        doc = fitz.open(pdf); zoom = dpi / 72.0
        for i, page in enumerate(doc, 1):
            pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
            dest = out / f"slide-{i}.png"; pix.save(dest)
            print(f"Saved {dest} ({pix.width}x{pix.height})")
        print(f"Rendered {doc.page_count} slides into {out}/")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python -X utf8 render_slides.py <presentation.pptx> [output_dir] [dpi]")
        sys.exit(1)
    render(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "render", int(sys.argv[3]) if len(sys.argv) > 3 else 150)
