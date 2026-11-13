# Cómo está hecho ExamenIA

Este documento explica el diseño para poder contarlo en una entrevista en un par de minutos.

## La idea en una frase

Un examen en español para IAs donde **cada respuesta se puede comprobar con código**, sin que nadie tenga que opinar.

## El problema que resuelve

Evaluar a una IA a mano es lento y subjetivo. Evaluarla con un examen fijo tiene otro problema: si las preguntas están en internet, la IA puede haberlas visto al entrenarse. ExamenIA resuelve las dos cosas: la corrección es automática y las preguntas se generan nuevas.

## Cómo funciona

1. **Semilla.** Un número decide qué preguntas salen. Python crea un generador de números aleatorios con esa semilla, así que el mismo número da siempre las mismas preguntas.
2. **Generación.** Cada categoría tiene su generador. Algunas eligen de un banco escrito a mano, como las frases y los plurales. Otras calculan, como los números en letras o el día de la semana de una fecha.
3. **Examen.** Se escribe un archivo con las preguntas y las instrucciones para la IA. No contiene soluciones.
4. **Respuestas.** La IA contesta con líneas `q01: respuesta`. El lector acepta también formato markdown, comillas y mayúsculas.
5. **Corrección.** Al corregir se vuelve a generar el mismo examen con la misma semilla. Cada pregunta trae su propia función que decide si la respuesta es correcta. No hay un archivo de soluciones que se pueda filtrar.
6. **Informe.** Se calcula la nota total y por categoría y se escribe un informe HTML, Markdown o JSON. Con varios archivos de respuestas se obtiene una clasificación.

## Decisiones

**Una función de comprobación por pregunta.** Tildes, plurales y conjugaciones se comparan con la respuesta exacta. Las órdenes con reglas se comprueban con código: contar palabras, buscar una letra, comprobar cómo empieza y termina una frase. Esto permite aceptar muchas respuestas distintas siempre que cumplan la regla.

**Distinto nivel de exigencia según la pregunta.** En las tildes hay que acertar todas, porque es justo lo que se mide. En los números en letras no se exigen tildes ni se distingue «veintiún» de «veintiuno» delante de «mil», porque se mide si el número está bien escrito, no la ortografía. Cada categoría mide una sola cosa.

**Números en letras con una función propia.** Es la parte más delicada: «veintiún mil», «ciento un mil», «cien mil» y «dieciséis» tienen reglas especiales. Tiene pruebas para los casos límite.

**Conjugaciones por regla y por tabla.** Las formas irregulares del presente y del indefinido se guardan en una tabla. El futuro se construye con la raíz irregular más las terminaciones, que son iguales para todos los verbos.

**Sin dependencias.** Todo usa la biblioteca estándar de Python, así que funciona con solo tener Python.

## Pruebas

Hay 48 tests. Comprueban los números en letras, que todas las frases pierden las tildes, que el examen es el mismo con la misma semilla y distinto con otra, que unas respuestas perfectas sacan 100 en 60 semillas distintas, que cada regla acepta lo correcto y rechaza lo incorrecto, que el lector de respuestas entiende varios formatos y que el informe escapa el HTML.

## Limitaciones honestas

- Mide la forma de la respuesta, no su calidad ni su sentido.
- Sigue las normas del español de España.
- El banco de frases, plurales y verbos es pequeño y está escrito a mano.
- Con 30 preguntas la nota es orientativa.

## Ideas para ampliar

- Más categorías: sinónimos, signos de puntuación, concordancia, uso de «haber» y «a ver».
- Variantes de español de América.
- Llamar directamente a la API de cada IA para no tener que copiar y pegar.
- Medir con modelos reales y publicar los resultados.
