#!/usr/bin/env python3
"""
Revisa la ortografía del texto de un .pptx y SEÑALA posibles faltas para que el modelo las
vea y las corrija antes de entregar. Extrae los `<a:t>` leyendo el ZIP directamente (NO
necesita python-pptx) y aplica heurísticas para el español: mojibake, tildes perdidas,
terminaciones -ción/-sión/-tión sin tilde y palabras que sin tilde no existen. Luego imprime
el texto por diapositiva. Implementación propia (MIT). Solo stdlib.

Uso:
    python -X utf8 revisar_ortografia.py presentacion.pptx

Correr SIEMPRE con `-X utf8` en Windows. Es un ASISTENTE, no un corrector infalible.
"""
import re
import sys
import zipfile
from xml.etree import ElementTree as ET

A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"

SIEMPRE_TILDE = {
    "tambien": "también", "asi": "así", "aqui": "aquí", "alli": "allí", "aca": "acá",
    "alla": "allá", "segun": "según", "despues": "después", "ademas": "además",
    "quizas": "quizás", "atras": "atrás", "detras": "detrás", "jamas": "jamás",
    "numero": "número", "numeros": "números", "codigo": "código", "pagina": "página",
    "paginas": "páginas", "linea": "línea", "lineas": "líneas", "titulo": "título",
    "parrafo": "párrafo", "capitulo": "capítulo", "indice": "índice", "metodo": "método",
    "analisis": "análisis", "sintesis": "síntesis", "rapido": "rápido", "practico": "práctico",
    "basico": "básico", "publico": "público", "politica": "política", "economia": "economía",
    "energia": "energía", "categoria": "categoría", "dia": "día", "dias": "días",
    "ultimo": "último", "proximo": "próximo", "minimo": "mínimo", "maximo": "máximo",
    "facil": "fácil", "dificil": "difícil", "util": "útil", "debil": "débil",
    "arbol": "árbol", "azucar": "azúcar", "telefono": "teléfono", "sabado": "sábado",
    "miercoles": "miércoles", "album": "álbum",
}
MOJIBAKE = ["Ã", "Â", "Ð", "�", "â€", "Ã³", "Ã±", "Ã©", "Ã¡", "Ãº", "Ã­"]
VOCAL_MOJI = re.compile(r"[a-záéíóúñ][AEIOU][a-záéíóúñ]")
SUFIJO_ION = re.compile(r"\b[a-zñ]*[bcdfghjklmnpqrstvwxyz]ion\b", re.IGNORECASE)
TOKEN = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+")


def revisar(texto: str):
    hallazgos = []
    for n, linea in enumerate(texto.splitlines(), 1):
        low = linea.lower()
        for marca in MOJIBAKE:
            if marca in linea:
                hallazgos.append((n, f"mojibake '{marca}' (texto corrupto): {linea.strip()[:80]}"))
                break
        for m in VOCAL_MOJI.finditer(linea):
            hallazgos.append((n, f"posible tilde perdida cerca de '{m.group(0)}': {linea.strip()[:80]}"))
        for w in TOKEN.findall(low):
            if w in SIEMPRE_TILDE:
                hallazgos.append((n, f"'{w}' -> '{SIEMPRE_TILDE[w]}'"))
        for m in SUFIJO_ION.finditer(low):
            w = m.group(0)
            hallazgos.append((n, f"'{w}' -> '{w[:-3]}ión' (¿falta tilde?)"))
    vistos, unicos = set(), []
    for h in hallazgos:
        if h not in vistos:
            vistos.add(h); unicos.append(h)
    return unicos


def extraer_texto_pptx(path: str) -> str:
    partes = []
    with zipfile.ZipFile(path) as z:
        slides = sorted(
            (n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)),
            key=lambda s: int(re.search(r"slide(\d+)", s).group(1)),
        )
        for i, name in enumerate(slides, 1):
            partes.append(f"## Slide {i}")
            root = ET.fromstring(z.read(name))
            for t in root.iter(f"{{{A_NS}}}t"):
                if t.text and t.text.strip():
                    partes.append(t.text)
            partes.append("")
    return "\n".join(partes)


def main():
    if len(sys.argv) != 2:
        print("uso: python -X utf8 revisar_ortografia.py <presentacion.pptx>")
        sys.exit(1)
    texto = extraer_texto_pptx(sys.argv[1])
    hallazgos = revisar(texto)
    print("=" * 70)
    print(f"REVISIÓN ORTOGRÁFICA — {len(hallazgos)} posible(s) falta(s) señaladas")
    print("=" * 70)
    if hallazgos:
        for n, msg in hallazgos:
            print(f"  línea {n}: {msg}")
    else:
        print("  (sin sospechosos automáticos — igual REVISA el texto de abajo)")
    print("\n" + "-" * 70)
    print("TEXTO POR DIAPOSITIVA (léelo buscando faltas que la heurística no detecta):")
    print("-" * 70)
    print(texto)


if __name__ == "__main__":
    main()
