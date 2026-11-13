"""Lectura de respuestas y corrección."""
import re
from collections import OrderedDict
from dataclasses import dataclass, field

from .preguntas import CATEGORIAS, NOMBRES

_LINEA = re.compile(r"^[\s>*`_-]*(q\d+)[\s*`_]*[:.)\-][\s*`_]*(.*?)[\s*`_]*$", re.IGNORECASE)


def _id_normal(identificador: str) -> str:
    """q1, Q01 y q001 son la misma pregunta: q01."""
    return f"q{int(identificador.strip().lower().lstrip('q')):02d}"


def leer_respuestas(texto: str) -> dict:
    """Acepta líneas `q01: respuesta` (también con markdown) o un JSON {"q01": "respuesta"}."""
    texto = texto.strip()
    if texto.startswith("{"):
        import json
        datos = json.loads(texto)
        return {_id_normal(str(k)): str(v) for k, v in datos.items()}
    respuestas = {}
    for linea in texto.splitlines():
        if linea.strip().startswith("#"):
            continue
        m = _LINEA.match(linea)
        if m:
            valor = m.group(2).strip()
            if len(valor) >= 2 and valor[0] in "«\"'“" and valor[-1] in "»\"'”":
                valor = valor[1:-1].strip()
            respuestas[_id_normal(m.group(1))] = valor
    return respuestas


def leer_texto(ruta) -> str:
    """Lee un archivo de texto de Windows: UTF-8 (con o sin BOM) o, si no lo es, ANSI (cp1252)."""
    datos = open(ruta, "rb").read()
    try:
        return datos.decode("utf-8-sig")
    except UnicodeDecodeError:
        return datos.decode("cp1252", errors="replace")


@dataclass
class Fallo:
    id: str
    categoria: str
    enunciado: str
    respuesta: str
    explicacion: str


@dataclass
class Resultado:
    nombre: str
    por_categoria: dict = field(default_factory=OrderedDict)    # clave -> [aciertos, total]
    fallos: list = field(default_factory=list)
    sin_responder: int = 0

    @property
    def aciertos(self):
        return sum(a for a, _ in self.por_categoria.values())

    @property
    def total(self):
        return sum(t for _, t in self.por_categoria.values())

    @property
    def nota(self):
        """Nota de 0 a 100."""
        return 100.0 * self.aciertos / self.total if self.total else 0.0

    def nota_categoria(self, clave):
        a, t = self.por_categoria[clave]
        return 100.0 * a / t if t else 0.0


def corregir(preguntas: list, respuestas: dict, nombre: str = "modelo") -> Resultado:
    res = Resultado(nombre)
    for clave, _ in CATEGORIAS:
        res.por_categoria[clave] = [0, 0]
    for p in preguntas:
        res.por_categoria[p.categoria][1] += 1
        respuesta = respuestas.get(p.id)
        if respuesta is None or not respuesta.strip():
            res.sin_responder += 1
            res.fallos.append(Fallo(p.id, p.categoria, p.enunciado, "", "sin respuesta; " + f"esperado: {p.esperado}"
                                    if p.categoria not in ("reglas",) else "sin respuesta"))
            continue
        acierto, explicacion = p.comprobar(respuesta)
        if acierto:
            res.por_categoria[p.categoria][0] += 1
        else:
            res.fallos.append(Fallo(p.id, p.categoria, p.enunciado, respuesta, explicacion))
    return res


def clasificar(resultados: list) -> list:
    return sorted(resultados, key=lambda r: (-r.nota, r.nombre))


__all__ = ["leer_texto", "leer_respuestas", "corregir", "clasificar", "Resultado", "Fallo", "NOMBRES"]
