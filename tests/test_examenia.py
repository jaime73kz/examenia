import datetime
import json

import pytest

from examenia import espanol as es
from examenia.cli import main
from examenia.correccion import clasificar, corregir, leer_respuestas
from examenia.informe import a_dict, a_html, a_markdown, escribir
from examenia.preguntas import CATEGORIAS, crear_examen, examen_a_markdown


# ---------------------------------------------------------------- utilidades de español

@pytest.mark.parametrize("n,texto", [
    (0, "cero"), (15, "quince"), (21, "veintiuno"), (31, "treinta y uno"), (100, "cien"), (101, "ciento uno"),
    (1000, "mil"), (2021, "dos mil veintiuno"), (21000, "veintiún mil"), (31000, "treinta y un mil"),
    (101000, "ciento un mil"), (21345, "veintiún mil trescientos cuarenta y cinco"),
    (999999, "novecientos noventa y nueve mil novecientos noventa y nueve"), (16000, "dieciséis mil"),
])
def test_numero_a_letras(n, texto):
    assert es.numero_a_letras(n) == texto


def test_numero_fuera_de_rango():
    with pytest.raises(ValueError):
        es.numero_a_letras(1_000_000)


def test_comparar_numero_tolerante():
    assert es.comparar_numero("Veintiuno mil trescientos", "veintiún mil trescientos")
    assert es.comparar_numero("dieciseis mil", "dieciséis mil")
    assert not es.comparar_numero("dieciséis mil uno", "dieciséis mil")


def test_quitar_tildes_conserva_la_enye():
    assert es.quitar_tildes("Mañana él también") == "Mañana el tambien"


def test_todas_las_frases_pierden_tildes_y_son_estables():
    for frase in es.FRASES_TILDES:
        sin = es.quitar_tildes(frase)
        assert sin != frase and es.quitar_tildes(sin) == sin


def test_conjugaciones_completas():
    for v in es.VERBOS:
        for t in es.TIEMPOS:
            for p in es.PERSONAS:
                assert es.conjugar(v, p, t)
    assert es.conjugar("hacer", "él", "pretérito indefinido") == "hizo"
    assert es.conjugar("tener", "nosotros", "futuro simple") == "tendremos"
    assert es.conjugar("ir", "yo", "pretérito indefinido") == es.conjugar("ser", "yo", "pretérito indefinido")


def test_dias_de_la_semana_conocidos():
    assert es.DIAS[datetime.date(2000, 1, 1).weekday()] == "sábado"
    assert es.DIAS[datetime.date(2020, 12, 25).weekday()] == "viernes"


# ---------------------------------------------------------------- examen

def test_examen_determinista_y_distinto_por_semilla():
    a = [p.enunciado for p in crear_examen(7, 5)]
    assert a == [p.enunciado for p in crear_examen(7, 5)]
    assert a != [p.enunciado for p in crear_examen(8, 5)]


def test_ids_y_numero_de_preguntas():
    examen = crear_examen(1, 4)
    assert len(examen) == 4 * len(CATEGORIAS)
    assert [p.id for p in examen] == [f"q{i:02d}" for i in range(1, len(examen) + 1)]


def test_limites_de_preguntas():
    with pytest.raises(ValueError):
        crear_examen(1, 0)
    with pytest.raises(ValueError):
        crear_examen(1, 21)


def test_no_se_repiten_enunciados_con_semillas_variadas():
    for semilla in range(1, 15):
        enunciados = [p.enunciado for p in crear_examen(semilla, 8) if p.categoria in ("tildes", "plurales", "conjugacion")]
        assert len(enunciados) == len(set(enunciados))


def test_el_examen_no_contiene_las_soluciones():
    texto = examen_a_markdown(crear_examen(1, 5), 1, 5)
    for p in crear_examen(1, 5):
        if p.categoria in ("tildes", "numeros"):
            assert p.esperado not in texto


# ---------------------------------------------------------------- corrección

def respuestas_perfectas(examen):
    return {p.id: p.ejemplo for p in examen}


@pytest.mark.parametrize("semilla", [1, 2, 3, 42])
def test_respuestas_perfectas_sacan_100(semilla):
    examen = crear_examen(semilla, 6)
    r = corregir(examen, respuestas_perfectas(examen))
    assert r.nota == 100 and not r.fallos


def test_sin_respuestas_saca_0():
    examen = crear_examen(1, 5)
    r = corregir(examen, {})
    assert r.nota == 0 and r.sin_responder == len(examen)


def test_respuestas_mal_dan_fallos_con_explicacion():
    examen = crear_examen(1, 5)
    r = corregir(examen, {p.id: "xyz" for p in examen})
    assert r.nota == 0 and len(r.fallos) == len(examen)
    assert all(f.explicacion for f in r.fallos)


def test_tildes_es_estricto():
    examen = [p for p in crear_examen(1, 5) if p.categoria == "tildes"]
    p = examen[0]
    assert p.comprobar(p.esperado)[0]
    assert not p.comprobar(es.quitar_tildes(p.esperado))[0]
    assert p.comprobar("  " + p.esperado.replace(" ", "  ") + " ")[0]


def test_dia_de_la_semana_tolera_tilde_y_mayusculas():
    p = [q for q in crear_examen(1, 5) if q.categoria == "fechas"][0]
    assert p.comprobar(p.esperado.upper() + ".")[0]
    assert p.comprobar(es.quitar_tildes(p.esperado))[0]
    assert not p.comprobar("lunes" if p.esperado != "lunes" else "martes")[0]


def reglas(semilla=1, n=6):
    return [p for p in crear_examen(semilla, n) if p.categoria == "reglas"]


def test_reglas_aceptan_su_ejemplo_y_rechazan_texto_vacio_de_sentido():
    for p in reglas():
        assert p.comprobar(p.ejemplo)[0], p.enunciado
        assert not p.comprobar("Hola")[0], p.enunciado


def test_regla_sin_letra_detecta_la_letra_aunque_lleve_tilde():
    for s in range(1, 40):
        for p in reglas(s, 6):
            if "no contenga la letra «e»" in p.enunciado:
                assert not p.comprobar("Él lee mucho todos los días")[0]
                return
    pytest.fail("no se generó ninguna regla sin la letra e")


def test_regla_de_tres_palabras_con_letra():
    for s in range(1, 40):
        for p in reglas(s, 6):
            if p.enunciado.startswith("Escribe exactamente tres"):
                letra = p.enunciado.split("«")[1][0]
                assert p.comprobar(f"{letra}a, {letra}e, {letra}o")[0]
                assert not p.comprobar(f"{letra}a, {letra}a, {letra}o")[0]
                assert not p.comprobar(f"{letra}a, {letra}e")[0]
                assert not p.comprobar(f"{letra}a {letra}e {letra}o")[0]
                return


def test_regla_de_repetir_cuenta_palabras_exactas():
    for s in range(1, 40):
        for p in reglas(s, 6):
            if "exactamente dos veces" in p.enunciado:
                palabra = p.enunciado.split("«")[1].split("»")[0]
                assert p.comprobar(f"hoy vi {palabra} y luego {palabra} otra vez")[0]
                assert not p.comprobar(f"hoy vi {palabra} y luego otra vez algo")[0]
                assert not p.comprobar(f"{palabra} {palabra} {palabra} otra vez hoy")[0]
                return


# ---------------------------------------------------------------- lectura de respuestas

def test_leer_respuestas_formatos():
    texto = "# comentario\nq01: Hola mundo\n**q02:** «adiós»\n- q03. \"tres\"\n`q04`: cuatro\nbasura\nq05 -  cinco  \n"
    assert leer_respuestas(texto) == {"q01": "Hola mundo", "q02": "adiós", "q03": "tres", "q04": "cuatro", "q05": "cinco"}


def test_leer_respuestas_json():
    assert leer_respuestas('{"q01": "a", "Q02": "b"}') == {"q01": "a", "q02": "b"}


# ---------------------------------------------------------------- informes y CLI

@pytest.fixture
def resultados():
    examen = crear_examen(1, 5)
    buenas = respuestas_perfectas(examen)
    malas = dict(buenas)
    malas["q01"] = "<script>alert(1)</script>"
    malas["q06"] = "mil"
    return [corregir(examen, buenas, "bueno"), corregir(examen, malas, "malo<b>")]


def test_clasificacion_y_notas(resultados):
    orden = clasificar(resultados)
    assert [r.nombre for r in orden][0] == "bueno" and orden[0].nota == 100 and orden[1].nota < 100


def test_informes(resultados, tmp_path):
    assert "Clasificación" in a_markdown(resultados, 1, 5)
    datos = a_dict(resultados, 1, 5)
    assert datos["modelos"][0]["nombre"] == "bueno"
    json.dumps(datos)
    for nombre in ("i.html", "i.md", "i.json"):
        assert escribir(resultados, 1, 5, tmp_path / nombre).exists()
    with pytest.raises(ValueError):
        escribir(resultados, 1, 5, tmp_path / "i.pdf")


def test_html_escapa(resultados):
    texto = a_html(resultados, 1, 5)
    assert "<script>alert(1)</script>" not in texto and "&lt;script&gt;" in texto and "malo&lt;b&gt;" in texto


def test_cli_de_principio_a_fin(tmp_path, capsys):
    examen_md = tmp_path / "examen.md"
    assert main(["examen", "-o", str(examen_md)]) == 0
    assert "q30." in examen_md.read_text(encoding="utf-8")
    examen = crear_examen(1, 5)
    resp = tmp_path / "ia.txt"
    resp.write_text("\n".join(f"{p.id}: {p.ejemplo}" for p in examen), encoding="utf-8")
    assert main(["corregir", str(resp), "-o", str(tmp_path / "informe.html")]) == 0
    assert "100.0/100" in capsys.readouterr().out
    assert (tmp_path / "informe.html").exists()


def test_cli_errores(tmp_path, capsys):
    assert main(["corregir", str(tmp_path / "no_existe.txt")]) == 2
    vacio = tmp_path / "v.txt"
    vacio.write_text("nada util", encoding="utf-8")
    assert main(["corregir", str(vacio)]) == 2
    assert main(["examen", "--por-categoria", "99"]) == 2
    assert "Error" in capsys.readouterr().err


def test_respuestas_perfectas_en_muchas_semillas():
    for semilla in range(1, 61):
        examen = crear_examen(semilla, 12)
        assert corregir(examen, respuestas_perfectas(examen)).nota == 100, semilla


def test_lectura_de_archivos_de_windows(tmp_path):
    from examenia.correccion import leer_texto
    texto = "q01: Los jóvenes de mi pueblo\nq02: canción\n"
    for nombre, codificacion in (("a.txt", "utf-8"), ("b.txt", "utf-8-sig"), ("c.txt", "cp1252")):
        ruta = tmp_path / nombre
        ruta.write_bytes(texto.encode(codificacion))
        assert leer_respuestas(leer_texto(ruta)) == {"q01": "Los jóvenes de mi pueblo", "q02": "canción"}, nombre


def test_ids_de_respuesta_se_normalizan():
    assert leer_respuestas("q1: uno\nQ02) dos\n q3 - tres\nq010: diez") == {
        "q01": "uno", "q02": "dos", "q03": "tres", "q10": "diez"}
    assert leer_respuestas('{"q1": "a"}') == {"q01": "a"}


def test_el_numero_aclara_que_el_punto_separa_miles():
    p = [q for q in crear_examen(1, 5) if q.categoria == "numeros"][0]
    assert "el punto separa los miles" in p.enunciado
