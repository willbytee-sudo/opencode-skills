---
name: skill-creator-opencode
description: >-
  Úsala para crear skills nuevas, y para modificar, mejorar o validar skills existentes
  de opencode. Dispara cuando el usuario quiere crear una skill desde cero, convertir un
  flujo de trabajo en skill ("haz una skill de esto"), editar u optimizar una skill,
  validar su formato, empaquetarla para distribuir, o afinar su description para que se
  dispare mejor. Pensada para opencode en Windows y en español.
metadata:
  origen: obra derivada de la skill "skill-creator" de Anthropic (Apache-2.0), adaptada a opencode/Windows y traducida al español. Ver NOTICE.
  entorno: opencode en Windows — Python 3.13 (stdlib; sin PyYAML)
  licencia: Apache-2.0 (ver LICENSE y NOTICE)
  regla_critica: correr TODOS los scripts con "python -X utf8"; instalar skills en ~/.config/opencode/skills/
---

# Creador de skills para opencode

Skill para crear skills nuevas e ir mejorándolas de forma iterativa. A grandes rasgos:

- Decide qué debe hacer la skill y, a grandes rasgos, cómo.
- Escribe un borrador del SKILL.md.
- Prueba la skill con 2-3 prompts realistas.
- Evalúa los resultados con el usuario (cualitativa y, si aplica, cuantitativamente).
- Reescribe la skill según el feedback. Repite hasta quedar satisfechos.
- Valida, empaqueta e instala.

Tu trabajo es detectar en qué punto está el usuario y ayudarlo a avanzar. Sé flexible:
si dicen "no quiero correr mil evals, solo improvisemos", hazlo así.

## Cómo opencode ejecuta esta skill (adaptaciones clave — LEER PRIMERO)

1. **`SKILL_DIR` con ruta absoluta.** opencode corre desde el directorio del proyecto,
   no desde el de la skill. Fija la variable a donde la tengas instalada:
   ```bash
   # Instalada en opencode (Windows):
   SKILL_DIR="$HOME/.config/opencode/skills/skill-creator-opencode"
   # (ajústala si trabajas desde el repo)
   ```
2. **REGLA UTF-8:** corre Python con `python -X utf8` SIEMPRE.
3. **Sin PyYAML:** los scripts parsean el frontmatter con un parser propio (utils.py), así
   que no necesitan dependencias externas.
4. **Dónde viven las skills en opencode:** una carpeta por skill en
   `~/.config/opencode/skills/<nombre>/` (en Windows: `C:\Users\<usuario>\.config\opencode\skills\<nombre>\`).
   Instalar = copiar/descomprimir la carpeta ahí y **reiniciar opencode**.

## Comunicarte con el usuario

Puede usar esta skill gente con muy distinto nivel técnico. Ajusta el lenguaje según las
señales: "evaluación"/"benchmark" son aceptables; para "JSON" o "aserción" conviene ver
que el usuario los maneja antes de usarlos sin explicar. Si dudas, define el término en
media línea.

---

## Crear una skill

### 1. Captura la intención
Entiende qué quiere el usuario. Si la conversación ya trae el flujo a capturar ("convierte
esto en una skill"), extrae primero de ahí: herramientas usadas, secuencia de pasos,
correcciones del usuario, formatos de entrada/salida. Confirma antes de seguir. Pregunta:
1. ¿Qué debe habilitar esta skill?
2. ¿Cuándo debe dispararse? (frases/contextos del usuario)
3. ¿Cuál es el formato de salida esperado?
4. ¿Conviene armar casos de prueba? Las skills con salida objetivamente verificable
   (transformar archivos, extraer datos, generar código, pasos fijos) se benefician; las
   subjetivas (estilo de escritura, arte) muchas veces no. Sugiere el default y decide con el usuario.

### 2. Entrevista e investiga
Pregunta proactivamente por casos borde, formatos, archivos de ejemplo, criterios de éxito
y dependencias. Revisa si hay MCPs útiles para investigar. Llega con contexto para no
cargarle el trabajo al usuario.

### 3. Escribe el SKILL.md
Rellena:
- **name**: identificador en kebab-case (minúsculas, dígitos, guiones; máx. 64).
- **description**: cuándo dispararse Y qué hace. Es el mecanismo principal de disparo:
  incluye qué hace **y** contextos concretos de cuándo usarla (todo el "cuándo" va aquí,
  no en el cuerpo). Claude tiende a **sub-disparar** las skills, así que hazla un poco
  "insistente". En vez de "Cómo construir un dashboard", escribe "…Úsala siempre que el
  usuario mencione dashboards, visualización de datos o mostrar cualquier tipo de dato,
  aunque no diga explícitamente 'dashboard'." (Sin `<` ni `>`; máx. 1024 caracteres.)
- **compatibility** (opcional): herramientas/dependencias requeridas.
- **metadata** (opcional): entorno, licencia, notas.
- el resto de la skill :)

### Guía para escribir skills

#### Anatomía
```
nombre-skill/
├── SKILL.md (obligatorio)
│   ├── frontmatter YAML (name, description obligatorios)
│   └── instrucciones en Markdown
└── recursos (opcional)
    ├── scripts/    - código ejecutable para tareas deterministas/repetitivas
    ├── references/ - documentos que se cargan al contexto cuando hacen falta
    └── assets/     - archivos usados en la salida (plantillas, íconos, fuentes)
```

#### Divulgación progresiva (progressive disclosure)
Tres niveles de carga:
1. **Metadata** (name + description) — siempre en contexto (~100 palabras).
2. **Cuerpo del SKILL.md** — en contexto cuando la skill se dispara (< 500 líneas ideal).
3. **Recursos** — según se necesiten (ilimitado; los scripts se ejecutan sin cargarse al contexto).

Claves: mantén SKILL.md bajo 500 líneas; si te acercas, agrega una capa de jerarquía con
punteros claros a qué leer después. Referencia los archivos desde SKILL.md diciendo cuándo
leerlos. Para referencias grandes (>300 líneas), incluye una tabla de contenido. Cuando una
skill cubre varios dominios, organiza por variante en `references/` (Claude lee solo el relevante).

#### Principio de no-sorpresa
Las skills no deben contener malware ni código de explotación, y su contenido no debe
sorprender respecto a lo que describen. No crees skills engañosas ni para acceso no
autorizado o exfiltración. (Un "roleplay como X" sí está bien.)

#### Patrones de escritura
Prefiere el **imperativo**. Explica el **porqué** de lo que pides; los LLMs de hoy son
inteligentes y con buen contexto van más allá de instrucciones rígidas. Si te ves escribiendo
SIEMPRE/NUNCA en mayúsculas o estructuras muy rígidas, es señal de alerta: replantea y explica
el motivo. Empieza por un borrador y luego míralo con ojos frescos y mejóralo.

Formato de salida:
```markdown
## Estructura del informe
Usa SIEMPRE esta plantilla exacta:
# [Título]
## Resumen ejecutivo
## Hallazgos clave
## Recomendaciones
```
Ejemplos:
```markdown
## Formato de mensaje de commit
**Ejemplo 1:**
Entrada: Agregué autenticación con tokens JWT
Salida: feat(auth): implementar autenticación basada en JWT
```

### 4. Casos de prueba
Tras el borrador, propón 2-3 prompts realistas (lo que un usuario diría de verdad) y
muéstraselos al usuario: "Aquí tienes unos casos de prueba, ¿te parecen bien o agregamos
más?". Guárdalos en `evals/evals.json` (ver [references/schemas.md](references/schemas.md)).
Aún no escribas aserciones; solo los prompts.

---

## Probar e iterar en opencode

> **Nota de adaptación:** el skill-creator original de Claude Code trae un harness
> automático de benchmark (`run_eval.py`, `run_loop.py`, `aggregate_benchmark.py`,
> `generate_report.py`, visor HTML de evals y subagentes graders) que depende del CLI
> `claude -p` y del modelo de subagentes de Claude Code. **Ese harness NO se portó** a
> opencode (usaría `opencode run` y otra orquestación). En su lugar, el flujo en opencode
> es **manual / con subagentes**, que es suficiente para iterar bien.

Flujo recomendado:

1. **Corre cada caso de prueba.** Si tu opencode tiene subagentes, lanza uno por caso que
   lea el `SKILL.md` y ejecute el prompt; guarda las salidas en
   `<skill>-workspace/iteration-N/eval-<id>/with_skill/outputs/`. Si no, ejecútalos tú,
   uno por uno, leyendo el SKILL.md y siguiéndolo. (Opcional: un baseline **sin** la skill
   para comparar.)
2. **Redacta aserciones** verificables por cada caso (ver el campo `expectations` en
   [references/schemas.md](references/schemas.md)) y explícaselas al usuario. Para lo que se
   pueda chequear por programa, escribe un pequeño script en vez de revisarlo a ojo.
3. **Muéstrale las salidas al usuario** para que las evalúe (abre los archivos, enséñale el
   texto/render). Pídele feedback concreto por caso: "¿Cómo se ve? ¿Algo que cambiarías?".
4. **Registra el resultado** en `grading.json` por caso (campos `text`/`passed`/`evidence`).

### Cómo pensar las mejoras
- **Generaliza desde el feedback.** Iteras sobre pocos ejemplos porque es rápido, pero la
  skill debe servir para millones de prompts distintos. Evita parches sobreajustados y MUSTs
  opresivos; si un problema es terco, prueba otra metáfora o patrón de trabajo.
- **Mantén el prompt liviano.** Quita lo que no aporta. Lee las transcripciones (no solo las
  salidas): si la skill hace perder tiempo al modelo, recorta esa parte y observa.
- **Explica el porqué.** Aunque el feedback sea terso, entiende qué necesita el usuario y
  transmítelo como razonamiento, no como reglas rígidas.
- **Detecta trabajo repetido entre casos.** Si en los 3 casos el modelo escribió un
  `crear_docx.py` o un `build_chart.py` parecido, es señal fuerte de que la skill debería
  **traer ese script** en `scripts/`. Escríbelo una vez y que la skill lo use.

### El bucle
Aplica mejoras → vuelve a correr los casos en `iteration-<N+1>/` → muestra al usuario →
lee el feedback → mejora otra vez. Sigue hasta que el usuario esté contento, el feedback
quede vacío, o no avances de forma significativa.

---

## Optimización de la description

La `description` del frontmatter decide si la skill se dispara. Tras crear/mejorar la skill,
ofrece afinarla. En opencode, sin el harness automático (`run_loop.py`), hazlo manual:

1. **Genera ~20 consultas de disparo** (8-10 que deben disparar, 8-10 que no), realistas y
   con detalle (rutas, nombres de columnas, contexto del usuario). Las mejores negativas son
   *near-miss*. Ver el esquema en [references/schemas.md](references/schemas.md). Revísalas con el usuario.
2. **Evalúa la description actual** contra esas consultas (razona/prueba cada una: ¿la
   description actual la haría disparar correctamente?). Anota fallos.
3. **Propón una description mejor** que arregle los fallos sin sobre-disparar, y compárala
   contra las mismas consultas. Muéstrale al usuario el antes/después.

Cómo funciona el disparo: las skills aparecen con name + description; Claude decide
consultarlas según la description, y **solo** para tareas que no resuelve trivialmente. Por
eso las consultas de prueba deben ser sustanciales (multi-paso), no "lee este PDF".

---

## Validar, empaquetar e instalar (scripts, correr con `-X utf8`)

```bash
SKILL_DIR="$HOME/.config/opencode/skills/skill-creator-opencode"

# Andamiar una skill nueva (crea SKILL.md de plantilla + subcarpetas)
python -X utf8 "$SKILL_DIR/scripts/init_skill.py" mi-skill ./skills

# Validar el formato (frontmatter, kebab-case, longitudes)
python -X utf8 "$SKILL_DIR/scripts/quick_validate.py" ./skills/mi-skill

# Empaquetar a .zip distribuible (valida primero)
python -X utf8 "$SKILL_DIR/scripts/package_skill.py" ./skills/mi-skill ./dist
```

**Instalar en opencode:** descomprime el `.zip` (o copia la carpeta) dentro de
`~/.config/opencode/skills/` y **reinicia opencode**. Estructura final:
`~/.config/opencode/skills/mi-skill/SKILL.md`.

| Script | Para qué |
|--------|----------|
| `init_skill.py` | andamia una skill nueva (SKILL.md de plantilla + carpetas) |
| `quick_validate.py` | valida SKILL.md/frontmatter (sin PyYAML) |
| `package_skill.py` | valida y empaqueta la carpeta en un `.zip` |
| `utils.py` | parser de frontmatter compartido |

## Actualizar una skill existente
- **Conserva el nombre original** (carpeta y campo `name`). Ej.: si es `research-helper`,
  no lo renombres a `research-helper-v2`.
- Si la ruta instalada es de solo lectura, copia a una ubicación editable, edita ahí y
  empaqueta desde la copia.

## Referencias
- [references/schemas.md](references/schemas.md) — esquemas JSON de `evals.json`, `grading.json`
  y la estructura del workspace de pruebas.

> **Licencia: Apache-2.0 (ver `LICENSE` y `NOTICE`).** Esta skill es una **obra
> derivada** de la skill `skill-creator` de **Anthropic, PBC** (Apache-2.0,
> https://github.com/anthropics/skills), traducida al español y adaptada al entorno
> opencode/Windows. Los scripts se reescribieron para no depender de PyYAML y se
> reemplazó el harness automático de evals por un flujo manual. No afiliada a Anthropic.
