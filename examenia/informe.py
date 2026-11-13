"""Informes en Markdown, HTML y JSON."""
import html
import json
from pathlib import Path

from .correccion import clasificar
from .preguntas import CATEGORIAS, NOMBRES


def _nivel(nota: float) -> str:
    if nota >= 90:
        return "excelente"
    if nota >= 75:
        return "bueno"
    if nota >= 50:
        return "regular"
    return "flojo"


def a_markdown(resultados: list, semilla: int, por_categoria: int) -> str:
    orden = clasificar(resultados)
    out = [f"# Informe ExamenIA (semilla {semilla}, {por_categoria} preguntas por categoría)", "",
           "## Clasificación", ""]
    for i, r in enumerate(orden, 1):
        out.append(f"{i}. **{r.nombre}**: {r.nota:.0f}/100 ({r.aciertos} de {r.total}), nivel {_nivel(r.nota)}")
    out += ["", "## Nota por categoría", ""]
    for clave, nombre in CATEGORIAS:
        celdas = ", ".join(f"{r.nombre} {r.nota_categoria(clave):.0f}" for r in orden)
        out.append(f"- {nombre}: {celdas}")
    for r in orden:
        out += ["", f"## Fallos de {r.nombre}", ""]
        if not r.fallos:
            out.append("Ninguno.")
        for f in r.fallos:
            out.append(f"- {f.id} ({NOMBRES[f.categoria]}): {f.enunciado}")
            out.append(f"  - respuesta: {f.respuesta or '(vacía)'}")
            if f.explicacion:
                out.append(f"  - {f.explicacion}")
    return "\n".join(out) + "\n"


def a_html(resultados: list, semilla: int, por_categoria: int) -> str:
    e = html.escape
    orden = clasificar(resultados)
    filas = []
    for r in orden:
        barras = "".join(
            f"<div class='cat'><span>{e(nombre)}</span><div class='barra'><i style='width:{r.nota_categoria(c):.0f}%'>"
            f"</i></div><b>{r.nota_categoria(c):.0f}</b></div>" for c, nombre in CATEGORIAS)
        fallos = "".join(
            f"<li><b>{e(f.id)}</b> <small>{e(NOMBRES[f.categoria])}</small><br>{e(f.enunciado)}<br>"
            f"<span class='resp'>Respuesta: {e(f.respuesta or '(vacía)')}</span>"
            + (f"<br><span class='exp'>{e(f.explicacion)}</span>" if f.explicacion else "") + "</li>"
            for f in r.fallos) or "<li>Ninguno.</li>"
        filas.append(
            f"<section><h2>{e(r.nombre)} <span class='nota {_nivel(r.nota)}'>{r.nota:.0f}/100</span></h2>"
            f"<p>{r.aciertos} aciertos de {r.total}. Nivel {_nivel(r.nota)}.</p>{barras}"
            f"<details><summary>Ver fallos ({len(r.fallos)})</summary><ul>{fallos}</ul></details></section>")
    return (
        "<!doctype html><html lang='es'><head><meta charset='utf-8'><title>Informe ExamenIA</title>"
        "<style>body{font-family:system-ui,sans-serif;max-width:820px;margin:2rem auto;padding:0 1rem;color:#1f2933}"
        "section{border:1px solid #d8dee4;border-radius:10px;padding:1rem 1.2rem;margin:1rem 0}"
        ".cat{display:grid;grid-template-columns:190px 1fr 40px;gap:.6rem;align-items:center;margin:.3rem 0}"
        ".barra{background:#e8ecf0;border-radius:6px;height:12px}.barra i{display:block;height:12px;border-radius:6px;"
        "background:#2f6fed}.nota{font-size:.9rem;padding:.15rem .6rem;border-radius:999px;color:#fff}"
        ".excelente{background:#1a7f37}.bueno{background:#2f6fed}.regular{background:#b7791f}.flojo{background:#c0392b}"
        "li{margin:.6rem 0}.resp{color:#555}.exp{color:#a33}small{color:#777}</style></head><body>"
        f"<h1>Informe ExamenIA</h1><p>Semilla {semilla}, {por_categoria} preguntas por categoría.</p>"
        + "".join(filas) + "</body></html>")


def a_dict(resultados: list, semilla: int, por_categoria: int) -> dict:
    return {"semilla": semilla, "por_categoria": por_categoria, "modelos": [
        {"nombre": r.nombre, "nota": round(r.nota, 1), "aciertos": r.aciertos, "total": r.total,
         "categorias": {c: {"aciertos": a, "total": t} for c, (a, t) in r.por_categoria.items()},
         "fallos": [vars(f) for f in r.fallos]} for r in clasificar(resultados)]}


def escribir(resultados: list, semilla: int, por_categoria: int, ruta) -> Path:
    ruta = Path(ruta)
    ext = ruta.suffix.lower()
    if ext == ".json":
        contenido = json.dumps(a_dict(resultados, semilla, por_categoria), ensure_ascii=False, indent=2)
    elif ext == ".md":
        contenido = a_markdown(resultados, semilla, por_categoria)
    elif ext in (".html", ".htm"):
        contenido = a_html(resultados, semilla, por_categoria)
    else:
        raise ValueError("el informe debe acabar en .html, .md o .json")
    ruta.write_text(contenido, encoding="utf-8")
    return ruta
