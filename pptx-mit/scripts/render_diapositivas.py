#!/usr/bin/env python3
"""
Renderiza un .pptx a un PNG por diapositiva para revisión visual. Usa LibreOffice (soffice)
para convertir a PDF y luego PyMuPDF (fitz) para partir el PDF en imágenes — así NO necesita
Poppler. Implementación propia (MIT).

Uso:
    python -X utf8 render_diapositivas.py presentacion.pptx [carpeta_salida] [dpi]

Requiere LibreOffice instalado (soffice en el PATH, o SOFFICE_BIN con la ruta) y PyMuPDF (✅).
Correr SIEMPRE con `-X utf8` en Windows.
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
    for p in [r"C:\Program Files\LibreOffice\program\soffice.exe",
              r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"]:
        if Path(p).exists():
            return p
    print("✗ No se encontró LibreOffice (soffice). Instálalo y agrégalo al PATH, o exporta "
          "SOFFICE_BIN con la ruta a soffice.exe.", file=sys.stderr)
    sys.exit(1)


def render(pptx_path, out_dir, dpi=150):
    soffice = find_soffice()
    src = Path(pptx_path)
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        r = subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", tmp, str(src)],
                           capture_output=True, text=True)
        pdf = Path(tmp) / f"{src.stem}.pdf"
        if r.returncode != 0 or not pdf.exists():
            print(f"✗ Falló la conversión a PDF con LibreOffice.\n{r.stdout}\n{r.stderr}", file=sys.stderr)
            sys.exit(1)
        doc = fitz.open(pdf); zoom = dpi / 72.0
        for i, page in enumerate(doc, 1):
            pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
            dest = out / f"slide-{i}.png"; pix.save(dest)
            print(f"Guardada {dest} ({pix.width}x{pix.height})")
        print(f"Renderizadas {doc.page_count} diapositivas en {out}/")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("uso: python -X utf8 render_diapositivas.py <presentacion.pptx> [carpeta_salida] [dpi]")
        sys.exit(1)
    render(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "render", int(sys.argv[3]) if len(sys.argv) > 3 else 150)
