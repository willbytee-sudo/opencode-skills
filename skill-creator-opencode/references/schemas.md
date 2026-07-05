# Esquemas JSON (skill-creator-opencode)

Estructuras JSON para las evals y el registro de resultados. En opencode el flujo de
prueba es **manual / con subagentes** (no hay harness automático de benchmark; ver
SKILL.md → "Probar e iterar en opencode"), así que estos esquemas son ligeros y sirven
para organizar tus casos de prueba y su evaluación a mano.

---

## evals/evals.json

Define los casos de prueba de una skill. Va en `evals/evals.json` dentro de la carpeta
de la skill (esta carpeta NO se distribuye; `package_skill.py` la excluye).

```json
{
  "skill_name": "nombre-de-la-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "El prompt tal como lo escribiría un usuario real",
      "expected_output": "Descripción en lenguaje natural del resultado esperado",
      "files": ["evals/files/muestra1.pdf"],
      "expectations": [
        "La salida incluye X",
        "La skill usó el script Y",
        "El .docx conserva los acentos (á, é, ñ)"
      ]
    }
  ]
}
```

**Campos:**
- `skill_name`: coincide con el `name` del frontmatter.
- `evals[].id`: entero único.
- `evals[].prompt`: la tarea a ejecutar (concreta, con detalle realista).
- `evals[].expected_output`: descripción legible del éxito.
- `evals[].files`: (opcional) archivos de entrada, rutas relativas a la raíz de la skill.
- `evals[].expectations`: afirmaciones verificables (para chequear a mano o con un script).

---

## grading.json (resultado de evaluar un caso)

Al evaluar la salida de un caso contra sus `expectations`, guarda el resultado. Usa
EXACTAMENTE los campos `text`, `passed`, `evidence`:

```json
{
  "eval_id": 1,
  "expectations": [
    { "text": "La salida incluye X", "passed": true,  "evidence": "aparece en la línea 12 de salida.md" },
    { "text": "Conserva los acentos", "passed": false, "evidence": "'función' salió como 'funciAn'" }
  ]
}
```
Para lo que se pueda verificar por programa, escribe y corre un script (más rápido y
reproducible) en vez de revisarlo a ojo.

---

## Estructura del workspace (pruebas manuales)

Guarda los resultados en `<nombre-skill>-workspace/`, hermana de la carpeta de la skill,
organizada por iteración:

```
mi-skill-workspace/
├── iteration-1/
│   ├── eval-1-nombre-descriptivo/
│   │   ├── with_skill/outputs/     # salida usando la skill
│   │   ├── without_skill/outputs/  # baseline sin la skill (opcional)
│   │   └── grading.json
│   └── eval-2-.../
└── iteration-2/
```

No crees todo por adelantado: arma cada carpeta a medida que avanzas.

---

## Optimización de la description (evals de disparo)

Si vas a afinar la `description` para que la skill se dispare mejor, arma 20 consultas
mezcladas (deben disparar / no deben disparar):

```json
[
  { "query": "el prompt del usuario, concreto y con detalle", "should_trigger": true },
  { "query": "un near-miss que comparte palabras pero necesita otra cosa", "should_trigger": false }
]
```
Las mejores consultas negativas son los *near-miss* (comparten palabras clave pero
requieren otra herramienta). Evita negativos obvios: no prueban nada.
