# ExamenIA

Un **examen de español para inteligencias artificiales que se corrige solo**.

Generas un examen, se lo pasas a cualquier IA (ChatGPT, Claude, Gemini...), pegas sus respuestas y obtienes una nota de 0 a 100 por categorías, con el detalle de cada fallo. Python 3.11 o superior, sin instalar nada.

*English summary: ExamenIA is a zero-dependency Python tool that generates a Spanish-language exam for AI models and grades the answers automatically. Questions are generated from a seed, so answer keys are never distributed. Categories: accent marks, numbers in words, weekdays, verb conjugation, plurals and instruction-following with verifiable rules. It outputs an HTML/Markdown/JSON report and can rank several models side by side.*

## Para qué sirve

Las empresas que entrenan y evalúan IAs necesitan comprobar si una respuesta en español es correcta, y necesitan que esa comprobación sea objetiva. ExamenIA hace justo eso: cada pregunta tiene **una respuesta que se puede verificar con código**, sin opiniones.

## El examen

Son 6 categorías, 5 preguntas cada una por defecto (se puede subir hasta 20):

- **Tildes**: se da una frase sin tildes y la IA debe ponerlas todas.
- **Números en letras**: de 100 a 999 999, con casos como «veintiún mil» o «ciento un mil».
- **Días de la semana**: en qué día cayó una fecha, calculado con el calendario.
- **Conjugación**: formas irregulares en presente, pretérito indefinido y futuro.
- **Plurales**: palabras difíciles como «lápiz», «régimen» o «paraguas».
- **Órdenes con reglas**: instrucciones como «escribe una frase de 7 palabras sin la letra e» o «tres palabras que empiecen por la letra c, separadas por comas». Se comprueban contando letras y palabras.

## Por qué no se puede copiar

Las preguntas salen de un número llamado **semilla**. Con la misma semilla sale siempre el mismo examen, y con otra sale otro distinto. Las soluciones no se guardan en ningún archivo: se vuelven a calcular al corregir. Así se puede crear un examen nuevo cada vez y una IA no puede haberse aprendido las respuestas.

## Uso rápido

```
python -m examenia examen -o examen.md
```

Pega el contenido de `examen.md` en una IA y guarda su respuesta en `respuestas.txt`. Debe tener una línea por pregunta:

```
q01: Los jóvenes de mi pueblo practican varios deportes.
q02: ...
```

Después:

```
python -m examenia corregir respuestas.txt -o informe.html
```

Para comparar varias IAs, pasa varios archivos:

```
python -m examenia corregir chatgpt.txt claude.txt gemini.txt -o informe.html
```

Opciones: `--semilla 7` (otro examen), `--por-categoria 10` (más preguntas). Usa **la misma semilla y el mismo número al crear y al corregir**. El informe puede ser `.html`, `.md` o `.json`.

## Ejemplo incluido

En `examples/` hay un examen, tres archivos de respuestas y el informe que se genera con ellos. Las respuestas de `modelo_a`, `modelo_b` y `modelo_c` están **simuladas a mano** con errores típicos para la demostración. No son de ningún modelo real.

```
python -m examenia corregir examples/respuestas/modelo_a.txt examples/respuestas/modelo_b.txt examples/respuestas/modelo_c.txt -o informe.html
```

## Límites

- Comprueba la **forma** de las respuestas, no si una frase es bonita o tiene sentido. Una frase de 7 palabras sin la letra e cuenta como correcta aunque sea rara.
- Sigue las normas de la RAE y el español de España. Los países de América pueden tener otras formas válidas, que aquí no se aceptan.
- Con 30 preguntas la nota es una orientación. Para comparar modelos de verdad conviene subir `--por-categoria` y probar varias semillas.
- Los datos (frases, plurales, verbos) están escritos a mano: el banco es limitado. Está pensado para ampliarse.

## Estructura

```
examenia/     español (utilidades y datos), preguntas, corrección, informe, cli
tests/        48 pruebas automáticas
examples/     examen, respuestas simuladas e informe
docs/         tutorial paso a paso y explicación del diseño
```

## Tests

```
pip install -r requirements-dev.txt
python -m pytest
```

## Licencia

MIT. Autor: Jaime Sánchez Vicente.
