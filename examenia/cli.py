"""Interfaz de línea de comandos."""
import argparse
import sys
from pathlib import Path

from . import __version__
from .correccion import clasificar, corregir, leer_respuestas, leer_texto
from .informe import escribir
from .preguntas import crear_examen, examen_a_markdown


def cmd_examen(args) -> int:
    preguntas = crear_examen(args.semilla, args.por_categoria)
    Path(args.output).write_text(examen_a_markdown(preguntas, args.semilla, args.por_categoria), encoding="utf-8")
    print(f"Examen de {len(preguntas)} preguntas guardado en {args.output}")
    print("Pégaselo a una IA y guarda su respuesta en un archivo .txt")
    return 0


def cmd_corregir(args) -> int:
    preguntas = crear_examen(args.semilla, args.por_categoria)
    resultados = []
    for archivo in args.respuestas:
        ruta = Path(archivo)
        if not ruta.is_file():
            raise ValueError(f"no existe el archivo de respuestas: {archivo}")
        respuestas = leer_respuestas(leer_texto(ruta))
        if not respuestas:
            raise ValueError(f"no he encontrado respuestas en {archivo} (formato esperado: q01: respuesta)")
        resultados.append(corregir(preguntas, respuestas, ruta.stem))
    print(f"Corregidos {len(resultados)} modelos, {len(preguntas)} preguntas cada uno:")
    for r in clasificar(resultados):
        print(f"  {r.nombre:<20} {r.nota:5.1f}/100  ({r.aciertos}/{r.total})")
    ruta = escribir(resultados, args.semilla, args.por_categoria, args.output)
    print(f"\nInforme guardado en {ruta}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="examenia", description="Examen de español para IAs que se corrige solo.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("examen", help="crea el examen para pegárselo a una IA")
    p.add_argument("--semilla", type=int, default=1, help="número que decide las preguntas (por defecto 1)")
    p.add_argument("--por-categoria", type=int, default=5, help="preguntas por categoría, de 1 a 20 (por defecto 5)")
    p.add_argument("-o", "--output", default="examen.md")
    p.set_defaults(func=cmd_examen)
    p = sub.add_parser("corregir", help="corrige uno o varios archivos de respuestas")
    p.add_argument("respuestas", nargs="+", help="archivos .txt o .json con las respuestas de cada IA")
    p.add_argument("--semilla", type=int, default=1, help="debe ser la misma que al crear el examen")
    p.add_argument("--por-categoria", type=int, default=5, help="debe ser el mismo que al crear el examen")
    p.add_argument("-o", "--output", default="informe.html", help="informe (.html, .md o .json)")
    p.set_defaults(func=cmd_corregir)
    return parser


def main(argv=None) -> int:
    for flujo in (sys.stdout, sys.stderr):  # la consola de Windows no siempre admite todos los caracteres
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(errors="replace")
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (ValueError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
