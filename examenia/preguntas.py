"""Generación de las preguntas. Todo sale de una semilla: el mismo examen se puede regenerar y corregir sin
repartir nunca las soluciones."""
import datetime
import random
from dataclasses import dataclass
from typing import Callable

from . import espanol as es

CATEGORIAS = [
    ("tildes", "Tildes"),
    ("numeros", "Números en letras"),
    ("fechas", "Días de la semana"),
    ("conjugacion", "Conjugación"),
    ("plurales", "Plurales"),
    ("reglas", "Órdenes con reglas"),
]
NOMBRES = dict(CATEGORIAS)
MAX_POR_CATEGORIA = 20


@dataclass
class Pregunta:
    id: str
    categoria: str
    enunciado: str
    esperado: str                              # lo que se muestra en el informe como respuesta correcta
    comprobar: Callable[[str], tuple]          # respuesta -> (acierto, explicación)
    ejemplo: str = ""                          # una respuesta válida (para pruebas y ejemplos)


def _igual(respuesta: str, esperado: str, tolerante: bool = False) -> tuple:
    a, b = es.normalizar_espacios(respuesta), es.normalizar_espacios(esperado)
    if tolerante:
        a, b = es.quitar_tildes(a.lower()), es.quitar_tildes(b.lower())
    return (a == b, "" if a == b else f"esperado: {esperado}")


# ---------------------------------------------------------------- generadores deterministas por categoría

def _tildes(rng, n):
    frases = rng.sample(es.FRASES_TILDES, n)
    for frase in frases:
        sin = es.quitar_tildes(frase)
        yield (f"Reescribe la frase poniendo todas las tildes que faltan, sin cambiar nada más: «{sin}»",
               frase, lambda r, f=frase: _igual(r, f), frase)


def _numeros(rng, n):
    rangos = [(100, 999), (1000, 9999), (10000, 99999), (100000, 999999)]
    for i in range(n):
        bajo, alto = rangos[i % len(rangos)]
        numero = rng.randint(bajo, alto)
        letras = es.numero_a_letras(numero)
        formato = f"{numero:,}".replace(",", ".")
        yield (f"Escribe en letras el número {formato} (el punto separa los miles).", letras,
               lambda r, e=letras: (es.comparar_numero(r, e), "" if es.comparar_numero(r, e) else f"esperado: {e}"),
               letras)


def _fechas(rng, n):
    vistas = set()
    while len(vistas) < n:
        fecha = datetime.date(rng.randint(1950, 2026), rng.randint(1, 12), rng.randint(1, 28))
        if fecha in vistas:
            continue
        vistas.add(fecha)
        dia = es.DIAS[fecha.weekday()]
        texto = f"{fecha.day} de {es.MESES[fecha.month - 1]} de {fecha.year}"
        yield (f"El {texto}, ¿qué día de la semana era? Responde solo con el nombre del día.", dia,
               lambda r, d=dia: (es.quitar_tildes(es.normalizar_espacios(r).lower().strip(".")) == es.quitar_tildes(d),
                                 "" if es.quitar_tildes(es.normalizar_espacios(r).lower().strip(".")) == es.quitar_tildes(d)
                                 else f"esperado: {d}"), dia)


def _conjugacion(rng, n):
    combos = [(v, p, t) for v in es.VERBOS for p in es.PERSONAS for t in es.TIEMPOS]
    for verbo, persona, tiempo in rng.sample(combos, n):
        forma = es.conjugar(verbo, persona, tiempo)
        yield (f"Conjuga el verbo «{verbo}» en {tiempo}, persona «{persona}». Responde solo con la forma verbal.",
               forma, lambda r, f=forma: _igual(r.strip(".").lower(), f), forma)


def _plurales(rng, n):
    for singular, plural in rng.sample(es.PLURALES, n):
        yield (f"Escribe el plural de «{singular}». Responde solo con la palabra.", plural,
               lambda r, p=plural: _igual(r.strip(".").lower(), p), plural)


def _primera_y_ultima(texto):
    pal = es.palabras(texto)
    return (pal[0].casefold(), pal[-1].casefold()) if pal else ("", "")


def _regla_n_palabras(rng):
    n = rng.randint(4, 9)

    def comprobar(r):
        c = len(es.palabras(r))
        return (c == n, "" if c == n else f"tiene {c} palabras y se pedían {n}")
    return (f"Escribe una frase con exactamente {n} palabras.", f"una frase de {n} palabras", comprobar,
            " ".join("Mi hermano pequeño toca la guitarra todas las tardes".split()[:n]))


def _regla_sin_letra(rng):
    letra = rng.choice(es.LETRAS_PROHIBIDAS)

    def comprobar(r):
        if len(es.palabras(r)) < 5:
            return (False, "tiene menos de 5 palabras")
        if letra in es.quitar_tildes(r.lower()):
            return (False, f"contiene la letra «{letra}»")
        return (True, "")
    ejemplo = {"e": "Hoy mi tío compró un libro azul", "a": "El perro come queso con miel", "o": "Mi gata sale a la calle",
               "s": "El gato duerme en la cama grande"}[letra]
    return (f"Escribe una frase de al menos 5 palabras que no contenga la letra «{letra}» (ni mayúscula ni minúscula).",
            f"una frase de 5 palabras o más sin la letra «{letra}»", comprobar, ejemplo)


def _regla_mayusculas(rng):
    n = rng.randint(3, 8)

    def comprobar(r):
        if len(es.palabras(r)) != n:
            return (False, f"debe tener {n} palabras")
        if r != r.upper():
            return (False, "no está toda en mayúsculas")
        return (True, "")
    return (f"Escribe en MAYÚSCULAS una frase de exactamente {n} palabras.", f"{n} palabras en mayúsculas", comprobar,
            " ".join("MI HERMANO PEQUEÑO TOCA LA GUITARRA TODAS LAS TARDES".split()[:n]))


def _regla_inicio_fin(rng):
    inicio, fin = rng.choice(es.PALABRAS_INICIO_FIN)

    def comprobar(r):
        pal = es.palabras(r)
        if len(pal) < 5:
            return (False, "tiene menos de 5 palabras")
        primera, ultima = _primera_y_ultima(r)
        if primera != inicio.casefold():
            return (False, f"no empieza por «{inicio}»")
        if ultima != fin.casefold():
            return (False, f"no termina con «{fin}»")
        return (True, "")
    return (f"Escribe una frase de al menos 5 palabras que empiece por la palabra «{inicio}» y termine con la "
            f"palabra «{fin}».", f"empieza por «{inicio}» y termina con «{fin}»", comprobar,
            es.EJEMPLOS_INICIO_FIN[inicio])


def _regla_lista_letra(rng):
    letra = rng.choice(es.LETRAS_LISTA)

    def comprobar(r):
        elementos = [e.strip() for e in r.split(",")]
        if len(elementos) != 3 or any(not e for e in elementos):
            return (False, "debe haber exactamente tres elementos separados por comas")
        if any(len(es.palabras(e)) != 1 for e in elementos):
            return (False, "cada elemento debe ser una sola palabra")
        if len({e.casefold() for e in elementos}) != 3:
            return (False, "las palabras deben ser distintas")
        if any(es.quitar_tildes(e.casefold())[0] != letra for e in elementos):
            return (False, f"todas deben empezar por «{letra}»")
        return (True, "")
    return (f"Escribe exactamente tres palabras distintas que empiecen por la letra «{letra}», separadas por "
            f"comas y sin nada más.", f"tres palabras distintas con «{letra}», separadas por comas", comprobar,
            es.EJEMPLOS_LISTA[letra])


def _regla_repetir(rng):
    palabra = rng.choice(es.PALABRAS_REPETIR)

    def comprobar(r):
        pal = [p.casefold() for p in es.palabras(r)]
        veces = pal.count(palabra)
        if len(pal) < 5:
            return (False, "tiene menos de 5 palabras")
        return (veces == 2, "" if veces == 2 else f"«{palabra}» aparece {veces} veces y se pedían 2")
    return (f"Escribe una frase de al menos 5 palabras que contenga la palabra «{palabra}» exactamente dos veces.",
            f"contiene «{palabra}» dos veces", comprobar,
            f"Dijo «{palabra}» y repitió «{palabra}» sin parar")


REGLAS = [_regla_n_palabras, _regla_sin_letra, _regla_mayusculas, _regla_inicio_fin, _regla_lista_letra,
          _regla_repetir]


def _reglas(rng, n):
    orden = REGLAS[:]
    rng.shuffle(orden)
    for i in range(n):
        yield orden[i % len(orden)](rng)


GENERADORES = {"tildes": _tildes, "numeros": _numeros, "fechas": _fechas, "conjugacion": _conjugacion,
               "plurales": _plurales, "reglas": _reglas}
LIMITES = {"tildes": len(es.FRASES_TILDES), "plurales": len(es.PLURALES)}


def crear_examen(semilla: int = 1, por_categoria: int = 5) -> list:
    """Devuelve la lista de preguntas. La misma semilla da siempre el mismo examen."""
    if not 1 <= por_categoria <= MAX_POR_CATEGORIA:
        raise ValueError(f"por_categoria debe estar entre 1 y {MAX_POR_CATEGORIA}")
    for clave, tope in LIMITES.items():
        if por_categoria > tope:
            raise ValueError(f"la categoría «{NOMBRES[clave]}» solo tiene {tope} preguntas distintas")
    preguntas = []
    for clave, _ in CATEGORIAS:
        rng = random.Random(f"{semilla}:{clave}")
        for enunciado, esperado, comprobar, ejemplo in GENERADORES[clave](rng, por_categoria):
            preguntas.append(Pregunta(f"q{len(preguntas) + 1:02d}", clave, enunciado, esperado, comprobar, ejemplo))
    return preguntas


INSTRUCCIONES = (
    "Eres un estudiante que hace un examen de español. Responde a todas las preguntas.\n"
    "Formato obligatorio: una línea por pregunta, con el número y dos puntos, por ejemplo `q01: respuesta`.\n"
    "No añadas explicaciones, comentarios ni comillas. Escribe solo la respuesta pedida."
)


def examen_a_markdown(preguntas: list, semilla: int, por_categoria: int) -> str:
    lineas = [f"# ExamenIA (semilla {semilla}, {por_categoria} preguntas por categoría)", "", INSTRUCCIONES, ""]
    actual = None
    for p in preguntas:
        if p.categoria != actual:
            actual = p.categoria
            lineas += ["", f"## {NOMBRES[actual]}", ""]
        lineas.append(f"{p.id}. {p.enunciado}")
    return "\n".join(lineas) + "\n"
