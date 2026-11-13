# Tutorial: usar ExamenIA paso a paso (Windows)

## 1. Lo que necesitas

Python 3.11 o superior. Para comprobarlo, abre el símbolo del sistema y escribe `python --version`.

## 2. Descargar el proyecto

1. Entra en https://github.com/jaime73kz/examenia.
2. Pulsa el botón verde **Code** y luego **Download ZIP**.
3. Haz clic derecho en el zip y elige **Extraer todo**.

## 3. Abrir la terminal en la carpeta correcta

1. Abre la carpeta `examenia` extraída. Debes ver `README.md` y una carpeta `examenia`.
2. Haz clic en la barra de direcciones del Explorador, borra lo que hay, escribe `cmd` y pulsa Enter.
3. Se abre una ventana negra: la terminal, ya dentro de la carpeta.

## 4. Ver el ejemplo

```
python -m examenia corregir examples/respuestas/modelo_a.txt examples/respuestas/modelo_b.txt examples/respuestas/modelo_c.txt -o informe.html
```

Abre `informe.html` con doble clic. Verás una tarjeta por modelo con su nota, barras por categoría y la lista de fallos.

## 5. Examinar una IA de verdad

1. Crea el examen:
   ```
   python -m examenia examen -o examen.md
   ```
2. Abre `examen.md` con el Bloc de notas, selecciona todo (Ctrl+A), copia (Ctrl+C) y pégalo en la IA que quieras probar.
3. La IA responde con líneas como `q01: respuesta`. Copia su respuesta completa.
4. Abre el Bloc de notas, pega y guarda el archivo como `chatgpt.txt` en la misma carpeta. En **Tipo** elige "Todos los archivos" para que no añada `.txt` doble.
5. Corrígelo:
   ```
   python -m examenia corregir chatgpt.txt -o informe.html
   ```
6. Repite con otras IAs y guarda cada respuesta en su archivo. Para compararlas:
   ```
   python -m examenia corregir chatgpt.txt claude.txt gemini.txt -o informe.html
   ```

## 6. Un examen distinto

Cambia la semilla y el tamaño. Hay que usar **los mismos valores al crear y al corregir**:

```
python -m examenia examen --semilla 7 --por-categoria 10 -o examen.md
python -m examenia corregir chatgpt.txt --semilla 7 --por-categoria 10 -o informe.html
```

## 7. Cómo leer el informe

- **Nota**: aciertos entre total, de 0 a 100. Más de 90 es excelente, de 75 a 89 bueno, de 50 a 74 regular, menos de 50 flojo.
- **Barras**: la nota de cada categoría. Muestran en qué es buena o mala cada IA.
- **Ver fallos**: cada pregunta fallada con lo que respondió la IA y lo que se esperaba, o la regla que incumplió.

## 8. Problemas frecuentes

- **`python` no se reconoce**: instala Python desde python.org y marca "Add Python to PATH".
- **`no existe el archivo de respuestas`**: el archivo no está en la carpeta donde abriste la terminal, o se llama `respuestas.txt.txt`. Revisa el nombre.
- **`no he encontrado respuestas`**: el archivo no tiene líneas como `q01: respuesta`. Pídele a la IA que respete el formato.
- **Sale muy mala nota por una línea movida**: comprueba que la IA no ha cambiado los números de pregunta.
