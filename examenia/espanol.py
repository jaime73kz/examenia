"""Utilidades de español: tildes, números en letras, días de la semana y bancos de datos."""
import re
import unicodedata

DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
         "noviembre", "diciembre"]


def quitar_tildes(texto: str) -> str:
    """Quita las tildes y diéresis pero conserva la ñ."""
    salida = []
    for car in unicodedata.normalize("NFD", texto):
        if unicodedata.category(car) == "Mn" and car not in "̃":  # ̃ es la tilde de la ñ
            continue
        salida.append(car)
    return unicodedata.normalize("NFC", "".join(salida))


def palabras(texto: str) -> list:
    return re.findall(r"\w+", texto, flags=re.UNICODE)


def normalizar_espacios(texto: str) -> str:
    return re.sub(r"\s+", " ", texto).strip()


_UNIDADES = ["cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez", "once",
             "doce", "trece", "catorce", "quince", "dieciséis", "diecisiete", "dieciocho", "diecinueve", "veinte",
             "veintiuno", "veintidós", "veintitrés", "veinticuatro", "veinticinco", "veintiséis", "veintisiete",
             "veintiocho", "veintinueve"]
_DECENAS = {3: "treinta", 4: "cuarenta", 5: "cincuenta", 6: "sesenta", 7: "setenta", 8: "ochenta", 9: "noventa"}
_CENTENAS = {1: "ciento", 2: "doscientos", 3: "trescientos", 4: "cuatrocientos", 5: "quinientos",
             6: "seiscientos", 7: "setecientos", 8: "ochocientos", 9: "novecientos"}


def _menor_de_mil(n: int, apocopar: bool) -> str:
    if n == 0:
        return ""
    if n == 100:
        return "cien"
    partes = []
    centenas, resto = divmod(n, 100)
    if centenas:
        partes.append(_CENTENAS[centenas])
    if resto:
        if resto < 30:
            palabra = _UNIDADES[resto]
        else:
            decena, unidad = divmod(resto, 10)
            palabra = _DECENAS[decena] + (" y " + _UNIDADES[unidad] if unidad else "")
        partes.append(palabra)
    texto = " ".join(partes)
    if apocopar:  # uno -> un delante de «mil»: veintiún mil, treinta y un mil
        texto = re.sub(r"uno$", "ún" if texto.endswith("veintiuno") else "un", texto)
    return texto


def numero_a_letras(n: int) -> str:
    """Escribe en letras un entero entre 0 y 999 999."""
    if not 0 <= n <= 999_999:
        raise ValueError("solo se admiten números entre 0 y 999999")
    if n == 0:
        return "cero"
    miles, resto = divmod(n, 1000)
    partes = []
    if miles:
        partes.append("mil" if miles == 1 else _menor_de_mil(miles, True) + " mil")
    if resto:
        partes.append(_menor_de_mil(resto, False))
    return " ".join(partes)


def comparar_numero(respuesta: str, esperado: str) -> bool:
    """Compara números en letras sin exigir tildes ni distinguir «veintiún»/«veintiuno» delante de «mil»."""
    def limpio(t):
        t = quitar_tildes(normalizar_espacios(t).lower())
        t = re.sub(r"\bveintiuno mil\b", "veintiun mil", t)
        t = re.sub(r"\buno mil\b", "un mil", t)
        return t
    return limpio(respuesta) == limpio(esperado)


# Frases con las tildes correctas. A la IA se le dan sin ellas.
FRASES_TILDES = [
    "Mañana tendré que ir al médico porque me duele la cabeza.",
    "¿Cuándo llegará el autobús a la estación?",
    "Él dijo que sí, pero tú no estabas allí.",
    "La canción que escuchamos ayer era muy bonita.",
    "Aún no sé qué quiero estudiar en el futuro.",
    "Ese camión lleva más de cien kilos de fruta.",
    "Si quieres té, tendrás que esperar un poco más.",
    "No sé cómo lo hizo, pero lo consiguió en un día.",
    "Está claro que él también vendrá a la reunión.",
    "Qué difícil es encontrar un buen sofá por ese precio.",
    "Mi hermano pequeño juega al fútbol todos los sábados.",
    "El árbol del jardín es más alto que la casa.",
    "Dime dónde vives y te mandaré el paquete.",
    "Todavía no entiendo por qué se marchó tan rápido.",
    "El pájaro cantó desde la ventana de la habitación.",
    "¿Qué hora es? Tengo que coger el tren de las diez.",
    "Los jóvenes de mi pueblo practican varios deportes.",
    "Aquel día llovió tanto que nadie pudo salir.",
    "Necesito papel para escribir una carta a mi tío.",
    "Quizás mañana haga más calor que hoy.",
    "El ratón se escondió debajo del sillón.",
    "Compré azúcar, café y también algo de jamón.",
]

# (singular, plural)
PLURALES = [
    ("lápiz", "lápices"), ("canción", "canciones"), ("joven", "jóvenes"), ("examen", "exámenes"),
    ("país", "países"), ("razón", "razones"), ("luz", "luces"), ("pez", "peces"), ("régimen", "regímenes"),
    ("carácter", "caracteres"), ("análisis", "análisis"), ("crisis", "crisis"), ("autobús", "autobuses"),
    ("árbol", "árboles"), ("ley", "leyes"), ("rey", "reyes"), ("menú", "menús"), ("paraguas", "paraguas"),
    ("reloj", "relojes"), ("virus", "virus"), ("mes", "meses"), ("lunes", "lunes"), ("actriz", "actrices"),
    ("vez", "veces"),
]

VERBOS = ["ser", "ir", "tener", "hacer", "poder", "decir", "venir", "saber", "poner", "querer", "dar", "ver"]
PERSONAS = ["yo", "tú", "él", "nosotros", "ellos"]
TIEMPOS = ["presente", "pretérito indefinido", "futuro simple"]

_PRESENTE = {
    "ser": "soy eres es somos son", "ir": "voy vas va vamos van",
    "tener": "tengo tienes tiene tenemos tienen", "hacer": "hago haces hace hacemos hacen",
    "poder": "puedo puedes puede podemos pueden", "decir": "digo dices dice decimos dicen",
    "venir": "vengo vienes viene venimos vienen", "saber": "sé sabes sabe sabemos saben",
    "poner": "pongo pones pone ponemos ponen", "querer": "quiero quieres quiere queremos quieren",
    "dar": "doy das da damos dan", "ver": "veo ves ve vemos ven",
}
_INDEFINIDO = {
    "ser": "fui fuiste fue fuimos fueron", "ir": "fui fuiste fue fuimos fueron",
    "tener": "tuve tuviste tuvo tuvimos tuvieron", "hacer": "hice hiciste hizo hicimos hicieron",
    "poder": "pude pudiste pudo pudimos pudieron", "decir": "dije dijiste dijo dijimos dijeron",
    "venir": "vine viniste vino vinimos vinieron", "saber": "supe supiste supo supimos supieron",
    "poner": "puse pusiste puso pusimos pusieron", "querer": "quise quisiste quiso quisimos quisieron",
    "dar": "di diste dio dimos dieron", "ver": "vi viste vio vimos vieron",
}
_RAIZ_FUTURO = {"ser": "ser", "ir": "ir", "tener": "tendr", "hacer": "har", "poder": "podr", "decir": "dir",
                "venir": "vendr", "saber": "sabr", "poner": "pondr", "querer": "querr", "dar": "dar", "ver": "ver"}
_TERMINACION_FUTURO = ["é", "ás", "á", "emos", "án"]


def conjugar(verbo: str, persona: str, tiempo: str) -> str:
    i = PERSONAS.index(persona)
    if tiempo == "presente":
        return _PRESENTE[verbo].split()[i]
    if tiempo == "pretérito indefinido":
        return _INDEFINIDO[verbo].split()[i]
    if tiempo == "futuro simple":
        return _RAIZ_FUTURO[verbo] + _TERMINACION_FUTURO[i]
    raise ValueError(tiempo)


PALABRAS_INICIO_FIN = [("Ayer", "casa"), ("Siempre", "tarde"), ("Nunca", "mañana"), ("Hoy", "música"),
                       ("Quizás", "amigos"), ("Entonces", "playa"), ("Luego", "tiempo"), ("Después", "verano")]
PALABRAS_REPETIR = ["sol", "casa", "libro", "agua", "tiempo", "amigo", "camino", "noche"]
LETRAS_LISTA = list("bcdfglmprst")
LETRAS_PROHIBIDAS = list("eaos")

EJEMPLOS_INICIO_FIN = {
    "Ayer": "Ayer por la tarde volví a casa", "Siempre": "Siempre llegamos un poco tarde",
    "Nunca": "Nunca lo dejes para mañana", "Hoy": "Hoy escucho mucha buena música",
    "Quizás": "Quizás vengan mis mejores amigos", "Entonces": "Entonces nos fuimos a la playa",
    "Luego": "Luego hablamos con más tiempo", "Después": "Después llegó por fin el verano",
}
EJEMPLOS_LISTA = {
    "b": "banco, barco, bota", "c": "casa, coche, cielo", "d": "dedo, dado, dulce", "f": "flor, fuego, foca",
    "g": "gato, goma, gorra", "l": "luna, libro, lago", "m": "mesa, mano, mar", "p": "pan, perro, playa",
    "r": "rana, rosa, río", "s": "sol, silla, sopa", "t": "tren, taza, tarde",
}
