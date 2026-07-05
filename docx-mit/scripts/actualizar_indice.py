#!/usr/bin/env python3
"""
Rellena (actualiza) el índice/TOC y todos los campos de un .docx para que quede armado sin
pulsar F9 en Word. Usa Word por COM (Windows) o LibreOffice; si no hay ninguno, marca el
documento para que Word actualice los campos al ABRIR (updateFields=true). Implementación
propia (MIT). Solo stdlib.

Uso:
    python -X utf8 actualizar_indice.py documento.docx [salida.docx]

Si no das salida, actualiza el mismo archivo. **Cierra el .docx en Word antes de correrlo**
(no puede estar abierto). Trabaja sobre archivos en una carpeta normal (Documents, etc.):
Word bloquea con "Vista Protegida" los archivos abiertos por automatización desde %TEMP%.
Correr SIEMPRE con `-X utf8` en Windows.
"""
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


# ---------- Word (COM vía PowerShell) — Windows ----------
def word_disponible() -> bool:
    if os.name != "nt":
        return False
    ps = "try { $w=New-Object -ComObject Word.Application; $w.Quit(); 'OK' } catch { 'NO' }"
    r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
                       capture_output=True, encoding="utf-8", errors="replace")
    return "OK" in (r.stdout or "")


def con_word(inp: str, out: str) -> tuple[bool, str]:
    ip = str(Path(inp).resolve())
    op = str(Path(out).resolve())
    ps = f"""
$ErrorActionPreference='Stop'
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
try {{
  $d = $w.Documents.Open('{ip}', $false, $false)
  [void]$d.Fields.Update()
  foreach ($toc in $d.TablesOfContents) {{ [void]$toc.Update() }}
  $d.SaveAs([ref]'{op}', [ref]16)
  $d.Close($false)
}} finally {{ $w.Quit() }}
'HECHO'
"""
    r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
                       capture_output=True, encoding="utf-8", errors="replace")
    return ("HECHO" in (r.stdout or "")), (r.stderr or r.stdout or "")


# ---------- LibreOffice (macro) — multiplataforma ----------
MACRO = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE script:module PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "module.dtd">
<script:module xmlns:script="http://openoffice.org/2000/script" script:name="Indices" script:language="StarBasic">
Sub ActualizarIndices
  oDoc = ThisComponent
  oIdx = oDoc.getDocumentIndexes()
  For i = 0 To oIdx.Count - 1
    oIdx.getByIndex(i).update()
  Next i
  oDoc.getTextFields().refresh()
  oDoc.store()
  oDoc.close(True)
End Sub
</script:module>"""


def buscar_soffice():
    c = os.environ.get("SOFFICE_BIN") or shutil.which("soffice") or shutil.which("soffice.exe")
    if c:
        return c
    for p in (r"C:\Program Files\LibreOffice\program\soffice.exe",
              r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"):
        if Path(p).exists():
            return p
    return None


def con_libreoffice(soffice: str, inp: str, out: str) -> tuple[bool, str]:
    if Path(out).resolve() != Path(inp).resolve():
        shutil.copyfile(inp, out)
    appdata = os.environ.get("APPDATA", str(Path.home() / ".config"))
    carpeta = Path(appdata) / "LibreOffice" / "4" / "user" / "basic" / "Standard"
    if not carpeta.exists():
        try:
            subprocess.run([soffice, "--headless", "--terminate_after_init"], capture_output=True, timeout=30)
        except Exception:  # noqa: BLE001
            pass
        carpeta.mkdir(parents=True, exist_ok=True)
    (carpeta / "Indices.xba").write_text(MACRO, encoding="utf-8")
    cmd = [soffice, "--headless", "--norestore",
           "vnd.sun.star.script:Standard.Indices.ActualizarIndices?language=Basic&location=application",
           str(Path(out).resolve())]
    try:
        r = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace", timeout=60)
    except subprocess.TimeoutExpired:
        return False, "LibreOffice excedió el timeout"
    return r.returncode == 0, (r.stderr or "")


# ---------- Fallback: marcar updateFields=true ----------
def marcar_updatefields(inp: str, out: str) -> None:
    W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    zin = zipfile.ZipFile(inp)
    nombres = zin.namelist()
    if "word/settings.xml" in nombres:
        s = zin.read("word/settings.xml").decode("utf-8")
        if "w:updateFields" not in s:
            s = s.replace("<w:settings ", "<w:settings ", 1)  # no-op para mantener prefijos
            ins = '<w:updateFields w:val="true"/>'
            # insertar justo después de la etiqueta de apertura <w:settings ...>
            i = s.find(">", s.find("<w:settings")) + 1
            s = s[:i] + ins + s[i:]
    else:
        s = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
             f'<w:settings xmlns:w="{W}"><w:updateFields w:val="true"/></w:settings>')
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
        escrito = False
        for item in zin.infolist():
            if item.filename == "word/settings.xml":
                zout.writestr(item, s); escrito = True
            else:
                zout.writestr(item, zin.read(item.filename))
        if not escrito:
            zout.writestr("word/settings.xml", s)
            # nota: para un settings.xml nuevo habría que declararlo en Content_Types/rels;
            # por eso el fallback ideal es que el .docx ya traiga settings.xml (lo normal).
    zin.close()


def main():
    if len(sys.argv) not in (2, 3):
        print("uso: python -X utf8 actualizar_indice.py <documento.docx> [salida.docx]")
        sys.exit(1)
    inp = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) == 3 else inp
    if out == inp:
        # trabajar sobre un temporal y luego reemplazar, por seguridad
        tmp = str(Path(inp).with_suffix(".tmp.docx"))
    else:
        tmp = out

    if word_disponible():
        ok, msg = con_word(inp, tmp)
        motor = "Word"
    else:
        soffice = buscar_soffice()
        if soffice:
            ok, msg = con_libreoffice(soffice, inp, tmp)
            motor = "LibreOffice"
        else:
            marcar_updatefields(inp, tmp if tmp != inp else out)
            print("⚠ No hay Word ni LibreOffice. Se marcó el documento para que Word actualice "
                  "el índice AL ABRIR (updateFields=true). Ábrelo en Word una vez para que se rellene.")
            if out == inp and Path(tmp).exists():
                os.replace(tmp, inp)
            sys.exit(0)

    if not ok:
        print(f"✗ Falló la actualización con {motor}:\n{msg}", file=sys.stderr)
        sys.exit(1)
    if out == inp:
        os.replace(tmp, inp)
    print(f"✓ Índice y campos actualizados con {motor} -> {out}")


if __name__ == "__main__":
    main()
