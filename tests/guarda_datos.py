# -*- coding: utf-8 -*-
"""La guarda de datos reales: lo que entra al repo, que es PÚBLICO, no trae razones sociales ni datos con la forma de
un dato real (encargo 72, CICLO-guarda-de-datos.md).

Por qué: la auditoría del 2026-10-16 encontró dos razones sociales en una prueba (tests/test_clics.py), publicadas
desde el 01-10, y nada las vigilaba. La sonda de secretos (tests/sonda_secretos.py) busca solo lo que config.json sabe:
las credenciales, el nombre del operador y los datos de la cuenta.

QUÉ BUSCA, en el texto y en el nombre de cada archivo. Nunca imprime un valor: dice el tipo, el archivo y la línea, y de
una razón social, su forma jurídica.
- razón social: un nombre seguido de una forma jurídica (SpA, Ltda., Inc., LLC, S.A. y otras) o precedido de una de
  las que van delante (como las rusas). Es la guarda 9 de Carga NEPPEX (tools/armar-pages.mjs en 0b47898), portada a
  Python: las mismas formas, los mismos separadores y el mismo nombre, de 1 a 6 palabras, la primera con mayúscula.
- RUT con su dígito verificador bien calculado (módulo 11), con guion.
- correo.
- contenedor con su dígito de control bien calculado (ISO 6346).
- teléfono chileno, móvil o fijo.
- número de reserva con la forma con que el programa lo lee: SCLG, EBKG o SCLA y 8 cifras (FORMA_BOOKING de
  AQUASHIELD.py), 9 cifras que empiezan con 27 o con 28 (MAERSK: los «28» desde la emisión del 22-10, encargo 77), o 9
  cifras detrás de su etiqueta («Booking number», o «Booking:», como escribe el programa una EMITIDA); y, con la forma de
  su página tras el envío del 22-10 (encargo 77), los de CMA-CGM, tres letras y 7 cifras, y los de COSCO, dos letras
  («CD» en la muestra) y 10 cifras, con las letras en cualquier caja y un espacio o un guion antes de las cifras. Las
  formas con letras se ven también detrás del escape de un literal («\\n», «\\t»).
- BL de naviera: un prefijo de naviera (SCAC) y de 6 a 12 letras o cifras, con 6 cifras seguidas.
- pedido de AquaChile: 40 y 6 cifras.
- dirección IPv4 pública.
- nombre y apellido: un nombre de pila de la lista de la auditoría del 2026-10-16 y una palabra con mayúscula.

LO QUE PASA, declarado, y cada cosa con su contador al lado del resultado:
- PERMITIDOS, por VALOR EXACTO, comparado sin caja, tildes ni puntuación: la propia empresa como el programa la escribe
  en los formularios (se publica a propósito: decisión de Marcelo del 01-10, encargo 44), y el nombre y el correo
  noreply del dueño (decisión de Marcelo, encargo 44). Por valor exacto y no por «termina en», como en NEPPEX: un nombre
  ajeno escrito delante del propio, separado solo por espacios, frena, y también el propio en una frase que empieza con
  mayúscula; se reescribe el texto, y la lista no crece por eso. La suite fija la lista. Del nombre, la regla mira el
  nombre de pila y la palabra que sigue: pasa si ahí empieza uno de los permitidos, entero.
- La propia empresa entre comillas, «», paréntesis o detrás de un signo (`COSCO_SHIPPER = "AQUACHILE S.A."`): se aparta
  antes de buscar, porque en el código va pegada a un identificador. NEPPEX no lo necesitaba: mira una página.
- Un número inventado: el que tiene las cifras que cambian todas iguales, o seguidas de a una, subiendo o bajando
  (12345678, 98765432, 11111111; de uno de MAERSK, las 7 que siguen al 27 o al 28; de uno de CMA-CGM, las 7 que siguen a
  las letras; de uno de COSCO, las 10 que siguen a las letras). Un número inventado con otra forma frena, y
  se reescribe con una de esas.
- Un correo de un dominio reservado para ejemplos (RFC 2606 y RFC 6761: example.com, .net y .org, y los que terminan en
  .example, .test, .invalid o .localhost), y el usuario y la clave de una dirección («https://usuario:clave@…»): esos
  los mira la sonda de secretos.
- Una IP privada, local o reservada para documentación (las que no son globales para `ipaddress`).
- Por propiedad, como en NEPPEX: la tipografía PT Sans, Serif o Mono, si la palabra que sigue no empieza con mayúscula
  (NEPPEX miraba las cinco que siguen; acá un comentario sigue en la línea de abajo, y la frase de abajo empieza con
  mayúscula), y un nombre de una sola letra (una plantilla). Y dos propias de este repo: letras sueltas, todas de una
  sola letra, como el logo del panel Tkinter, «A Q U A S H I E L D»; y una lista de formas separadas por comas o barras,
  donde cada palabra del «nombre» es otra forma.
- Las formas que busca la razón social, en este mismo archivo, entre sus dos marcas: escritas, son su propio hallazgo.
  Solo ahí, y solo para la razón social: el resto del archivo se revisa entero.
- Lo que va en base64 (las tipografías incrustadas en AQUASHIELD.py, una tira de 200 caracteres o más) y los hashes (16
  caracteres hexadecimales o más, con una letra): se apartan antes de buscar. Un hash de git da un número con forma de
  pedido de vez en cuando (NEPPEX lo midió), y el base64 forma palabras al azar.

Antes de buscar, el texto pasa a su forma NFC (en NEPPEX, la expresión admite las marcas combinantes, una clase que el
`re` de Python no tiene): así un nombre escrito con sus tildes aparte se ve igual. Y un archivo que no es UTF-8 se lee
como Windows-1252.

LO QUE NO VE (LÍMITES), como en NEPPEX y por lo que midieron las revisiones del encargo 72:
- un nombre de cliente sin forma jurídica (lo ve solo quien lo lee), y uno que empieza con minúscula, o con la forma de
  dos letras en minúscula;
- el nombre y la forma en campos separados (un JSON), o unidos por un punto o un guion a otra palabra en minúscula;
- una forma que no está en las listas;
- una nave, un viaje, un contrato o una dirección postal; un número de reserva de CMA-CGM o de COSCO con otra forma que
  la medida el 22-10 (una muestra de cada una), aunque se ve en minúscula y con un espacio o un guion; uno de MAERSK
  que no empieza con 27 ni con 28 y va sin su etiqueta; un número partido por un carácter invisible (se cambia por un
  espacio) o escrito con cifras de ancho completo; un teléfono de 9 cifras pegadas; una IPv6;
- un nombre y apellido en mayúsculas, o con el apellido primero;
- un dato pegado a otra palabra o a una tira de 200 caracteres o más, partido en dos líneas, o armado en el código
  (`"40" + str(…)`);
- un archivo en UTF-16 sin BOM.
Una versión de cuatro partes, de una a tres cifras cada una, se lee como una IP: si es pública, frena, y se reescribe.
Y tres letras y 7 cifras, o dos letras y 10 cifras, pegadas o con un espacio o un guion (un monto con el código de su
moneda, por ejemplo), se leen como un número de CMA-CGM o de COSCO: frena, y se reescribe con las cifras a la vista o
con sus puntos de miles (revisiones del encargo 77).

DÓNDE CORRE:
- En la suite (tests/test_guarda_datos.py), sobre lo que git versionaría: lo seguido y lo nuevo que .gitignore no
  excluye, tal como está en el árbol de trabajo; lo que el índice guarda distinto del árbol; y el nombre de cada
  archivo. Nunca lee lo que .gitignore excluye: ahí viven config.json, logs/ y las planillas.
- En el hook pre-commit (.githooks/pre-commit): `python tests/guarda_datos.py --pre-commit` lee SOLO el índice que git
  le pasa al hook (GIT_INDEX_FILE), que es lo que se va a commitear, después de sus controles.
- A mano: `python tests/guarda_datos.py`, lo mismo que la suite, con lo no commiteado.

Antes de mirar, el instrumento se prueba (control positivo): el detector, sobre una muestra de cada tipo; la lectura,
sobre un repo inventado con un caso de cada forma de entrar; y la lectura del índice, sobre uno donde el índice, el
árbol y un índice aparte dicen cosas distintas. Si no ve sus casos conocidos, aborta en vez de informar un cero.
Los valores de los controles son inventados, y van armados por partes: escritos enteros, esta guarda los encontraría en
este archivo.
"""
import bisect
import codecs
import collections
import contextlib
import dataclasses
import ipaddress
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import unicodedata
import uuid

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PROPIO = "tests/guarda_datos.py"
# Las pruebas lo cambian por el Popen de verdad: el arnés (tests/soporte.py) pone una trampa en subprocess.Popen.
POPEN = subprocess.Popen
PLAZO_GIT = 120   # segundos para cada llamada a git

# --- LAS EXCEPCIONES, por valor exacto --------------------------------------------------------------------------------
PERMITIDOS = (
    ("razón social", "AQUACHILE S.A.",
     "la propia empresa, como el programa la escribe en los formularios de COSCO y MAERSK: se publica a propósito "
     "(decisión de Marcelo del 01-10, encargo 44)"),
    ("nombre y apellido", "Marcelo Ramirez",
     "el dueño, autor y committer de cada commit (decisión de Marcelo, encargo 44)"),
    ("nombre y apellido", "Marcelo Andrés Ramírez Sánchez",
     "el dueño, completo, en el pie del panel (decisión de Marcelo, encargo 44)"),
    ("correo", "269565694+1992MARS@users.noreply.github.com",
     "el correo noreply del dueño en GitHub, autor y committer de cada commit: público a propósito (encargo 44)"),
)


def clave(s):
    """Sin caja, sin tildes y sin puntuación: «AquaChile S.A.» y «AQUACHILE S. A.» quedan iguales."""
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if not unicodedata.combining(c)).upper()
    return " ".join(re.sub(r"[\W_]+", " ", s).split())


def permitido(tipo, texto, desde=None):
    """¿Es `texto` un valor permitido de `tipo`? Con `desde`: ¿empieza ahí, en `texto`, uno permitido, entero, y no
    sigue una letra o una cifra pegada? Un correo se compara tal cual, sin caja: sin su puntuación sería otro correo."""
    for t, valor, _ in PERMITIDOS:
        if t != tipo:
            continue
        if tipo == "correo":
            if texto.lower() == valor.lower():
                return True
            continue
        trozo = texto if desde is None else texto[desde:desde + len(valor)]
        pegado = desde is not None and texto[desde + len(valor):desde + len(valor) + 1].isalnum()
        if clave(trozo) == clave(valor) and not pegado:
            return True
    return False


MARCA_DESDE = "# --- las formas que busca la razón social: desde acá ---"
MARCA_HASTA = "# --- las formas que busca la razón social: hasta acá ---"
# --- las formas que busca la razón social: desde acá ---
# La guarda 9 de Carga NEPPEX (tools/armar-pages.mjs @ 0b47898), portada a Python. Python no trae \p{Lu}: la clase se
# arma con las mayúsculas de los alfabetos latino, griego y cirílico.
MAYUS = "[" + "".join(re.escape(chr(c)) for c in range(0x41, 0x530) if chr(c).isupper()) + "]"


def _libre(palabra):
    return "".join(f"[{c.upper()}{c.lower()}]" if c.isalpha() else c for c in palabra)


def _abreviatura(letras):
    return "(?:" + r"\.?\s?".join(letras) + "|" + _libre(letras) + r")\.?"


def _dos_letras(par):
    return par[0] + r"(?:\s{0,2}[.\-]\s{0,2}|\s{1,2})?" + par[1] + r"\.?"


# Las formas, en tres clases, porque la caja es lo que separa una forma de un texto cualquiera: las de tres letras o
# más, en cualquier caja; las de dos, solo en mayúsculas (en minúsculas pegaban en el código minificado); y las de
# varias palabras, escritas aparte.
TRES_O_MAS = ("SAIC", "OJSC", "PJSC", "SARL", "EIRL", "LTDA", "CORP", "GMBH", "SAC", "SAS", "SPA", "SRL", "LDA", "LTD",
              "LLC", "LLP", "PLC", "INC", "ASA", "OYJ", "APS", "KFT", "ZRT", "JSC", "TOV")
DOS = ("SA", "SL", "AG", "AS", "AB", "BV", "NV", "KG", "KK", "OY")
PALABRAS = ("Incorporated", "Corporation", "Limitada", "Limited", "Eireli")
OTRAS = (r"[Ss]ociedad\s+[Aa]n[óoÓO]nima", r"SOCIEDAD\s+AN[ÓO]NIMA", r"[Ss]ociedad\s+(?:por\s+[Aa]cciones|[Ll]imitada)",
         r"[Ss]\.?\s?de\s+[Rr]\.?\s?[Ll]\.?(?:\s+de\s+[Cc]\.?\s?[Vv]\.?)?", r"[Ss]dn\.?\s*[Bb]hd\.?",
         r"[Ss]p\.?\s?z\s?o\.\s?o\.?", r"[Dd]\.\s?o\.\s?o\.?", r"[Ss]\.\s?r\.\s?o\.?", r"S\.\s?p\.\s?A\.?",
         r"S\.\s?r\.\s?l\.?", r"A/S", r"S/A", r"Co\.", r"[Cc][IiÍí][Aa]\.?", r"Lt[ée]e", "Oy")
FORMAS = "|".join(OTRAS + tuple(_libre(p) for p in PALABRAS) + tuple(_abreviatura(t) for t in TRES_O_MAS)
                  + tuple(_dos_letras(d) for d in DOS))
FORMAS_DELANTE = ("OOO", "ООО", "ZAO", "ЗАО", "OAO", "ОАО", "PAO", "ПАО", "UAB", "SIA", "PT", "LLC", "JSC", "OJSC",
                  "PJSC", "ТОО", "ТОВ")
# El nombre: de 1 a 6 palabras, la primera con mayúscula (o cifras y una letra, «3M»), cada una con tope de largo (sin
# él, un bloque largo de mayúsculas costaba minutos: lo midió NEPPEX).
RESTO = r"[\w&'’]{0,59}\.?"
NOMBRE = "(?:" + MAYUS + r"|\d{1,6}[^\W\d_])" + RESTO + r"(?:\s{1,8}[^\W_]" + RESTO + "){0,5}"
RAZON_DETRAS = re.compile("(" + NOMBRE + r")(?:\s{0,8}[,/\-]\s{0,8}|\s{1,8})(" + FORMAS + r")(?![^\W_])")
RAZON_DELANTE = re.compile(r"(?<![^\W_])(" + "|".join(FORMAS_DELANTE) + r")\s{1,8}(" + NOMBRE + ")")
FORMA_SOLA = re.compile("(?:" + FORMAS + "|" + "|".join(FORMAS_DELANTE) + ")")
# Lo que separa palabras sin ser un espacio pasa a uno, como en NEPPEX: un escape, una entidad de HTML, un %HH, una
# etiqueta, la unión de dos cadenas, y las comillas, paréntesis y signos. No cambia los saltos de línea: la línea que se
# informa es la del archivo.
SEPARADORES = (
    (re.compile(r"\\u[0-9A-Fa-f]{4}|\\x[0-9A-Fa-f]{2}|\\[A-Za-z][*+?]?"), " "),
    (re.compile(r"\\(?=[.\-/])"), ""),
    (re.compile(r"&(?:#\d+|#x[0-9A-Fa-f]+|[A-Za-z][A-Za-z0-9]{1,30});?"), " "),
    (re.compile(r"%[0-9A-Fa-f]{2}"), " "),
    (re.compile(r"</?[A-Za-z][\w:-]*([^<>]{0,300})>"), r" \1 "),
    (re.compile(r"([\"'`])[ \t]*\+[ \t]*\1"), " "),
    (re.compile(r"[\"«»“”„()\[\]{}*_|;:=`]"), " "),
)
FAMILIA_PT = re.compile(r"^(?:SANS|SERIF|MONO)$")
# Un ejemplo escrito de cada una de OTRAS, en su orden, para la prueba de cada forma (test_guarda_datos): escritos fuera
# de estas marcas, serían su propio hallazgo.
EJEMPLOS_DE_OTRAS = ("Sociedad Anónima", "SOCIEDAD ANÓNIMA", "Sociedad por Acciones", "S. de R.L. de C.V.", "Sdn Bhd",
                     "Sp. z o.o.", "d.o.o.", "s.r.o.", "S.p.A.", "S.r.l.", "A/S", "S/A", "Co.", "Cía.", "Ltée", "Oy")
# --- las formas que busca la razón social: hasta acá ---

# --- los datos con forma de dato real ---------------------------------------------------------------------------------
RUT = re.compile(r"(?<![\d.])(\d{1,2})\.?(\d{3})\.?(\d{3})-([\dkK])(?!\w)")
CORREO = re.compile(r"(?<![\w.+%-])([\w.+-]{1,64})@((?:[\w-]{1,63}\.){1,6}[A-Za-z]{2,24})(?![\w-])")
DOMINIOS_RESERVADOS = re.compile(r"(?:^|\.)(?:example\.(?:com|net|org)|[\w-]+\.(?:example|test|invalid|localhost))$|"
                                 r"^(?:example|test|invalid|localhost)$", re.I)
CONTENEDOR = re.compile(r"(?<![A-Za-z0-9])([A-Z]{4})\s?(\d{6})\s?(\d)(?![A-Za-z0-9])")
TELEFONO = re.compile(r"(?<!\d)\+?56[ .-]?\(?(?:9|2|[3-7]\d)\)?[ .-]?\d{3,4}[ .-]?\d{4}(?!\d)"
                      r"|(?<!\d)(?<!\d[.,])\(?0?(?:9|2|[3-7]\d)\)?[ .-]\d{4}[ .-]\d{4}(?!\d)(?![.,]\d)")
# Delante de un número de reserva, ni una letra ni una cifra pegada, salvo la letra de un escape escrito en un literal
# («\n», «\r», «\t», «\f»): en una prueba, el texto de una página va en un literal, y con «\nCD…» la «n» lo tapaba
# (revisión de seguridad del encargo 77).
_ANTES = r"(?:(?<![A-Za-z0-9])|(?<=\\[nrtf]))"
RESERVA = re.compile(_ANTES + r"(?:SCLG|EBKG|SCLA)\s?(\d{8})(?!\d)")
# MAERSK: 9 cifras que empiezan con 27 o, desde la emisión del 22-10, con 28 (encargo 77).
RESERVA_MAERSK = re.compile(r"(?<!\d)2[78](\d{7})(?!\d)")
# CMA-CGM y COSCO, con la forma de su página tras el envío del 22-10 (encargo 77; una muestra de cada una): CMA, tres
# letras y 7 cifras («Booking AAA9999999», en la tarjeta «Booking enviado»); COSCO, «CD» y 10 cifras («Booking
# CD9999999999 has been submitted successfully!»). Con una sola muestra, la forma se toma más ancha, como la de SCLG:
# las letras en cualquier caja, COSCO con dos letras cualesquiera, y un espacio o un guion antes de las cifras
# (revisión de seguridad del encargo 77). En lo versionado no agrega ningún hallazgo.
RESERVA_CMA = re.compile(_ANTES + r"[A-Za-z]{3}[ -]?(\d{7})(?![A-Za-z0-9])")
RESERVA_COSCO = re.compile(_ANTES + r"[A-Za-z]{2}[ -]?(\d{10})(?![A-Za-z0-9])")
# Los espacios, con tope: con `\s*:?\s*`, una tira larga de espacios detrás de la etiqueta retrocedía sin fin (64.000,
# 46 s; lo midió la revisión de seguridad del encargo 72). «Booking:» también es una etiqueta: así escribe el programa
# el número de una EMITIDA («(Booking: …)», _resultado_envio), y un número de MAERSK con otro prefijo pasaba
# (revisión de seguridad del encargo 77).
RESERVA_CON_ETIQUETA = re.compile(r"(?i:booking(?:\s{1,20}(?:number|no\.?|n[°º])(?:\s{0,20}:)?|\s{0,3}:))"
                                  r"\s{0,20}(\d{9})(?!\d)")
BL = re.compile(r"(?<![A-Za-z0-9])(?:MAEU|MEDU|MSCU|HLCU|CMDU|ONEY|COSU|EGLV|EVRG|YMLU|ZIMU|HDMU|SUDU|OOLU|APLU|WHLC|"
                r"PCIU|SMLM|HAMU)([A-Z0-9]{6,12})(?![A-Za-z0-9])")
PEDIDO = re.compile(r"(?<!\d)40(\d{6})(?!\d)")
IPV4 = re.compile(r"(?<![\d.])(\d{1,3}(?:\.\d{1,3}){3})(?!\d|\.\d)")
PERSONA = re.compile(r"\b(?:Juan|José|Jose|Luis|Carlos|Jorge|Pedro|Diego|Francisco|Pablo|Andrés|Andres|Felipe|Cristián|"
                     r"Cristian|Sergio|Patricio|Claudio|Gonzalo|Matías|Matias|Sebastián|Sebastian|Ricardo|"
                     r"Alejandro|Mauricio|Marcelo|Daniel|Javier|Ignacio|Tomás|Tomas|Nicolás|Nicolas|Héctor|Hector|"
                     r"Raúl|Raul|Víctor|Victor|Manuel|Fernando|María|Maria|Ana|Carolina|Camila|Francisca|Valentina|"
                     r"Daniela|Paula|Constanza|Catalina|Javiera|Fernanda|Claudia|Patricia|Andrea|Macarena|Paola|"
                     r"Gabriela|Lorena|Verónica|Veronica|Carmen|Rosa|Isabel|Sofía|Sofia|John|Michael|David|Robert|"
                     r"James|Mary|Jennifer|Linda|Kenji|Takashi|Hiroshi)\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]{2,}\b")
BASE64 = re.compile(r"[A-Za-z0-9+/]{200,}={0,2}")
# Los caracteres invisibles (los de ancho cero, las marcas de dirección, el guion suave y el BOM) pasan a un espacio,
# del mismo largo: escondían un dato dentro de una palabra («S·.A.» con uno de ancho cero entre medio).
INVISIBLES = {c: " " for c in (0x00AD, 0x200B, 0x200C, 0x200D, 0x200E, 0x200F, 0x2060, 0xFEFF)}
# Lo que separa un correo de lo que va antes en el mismo «token»: para saber si es el usuario de una dirección.
CORTES = " \t\n\"'<>()[],;"
HASH = re.compile(r"(?<![0-9A-Za-z])[0-9A-Fa-f]{16,}(?![0-9A-Za-z])")
LETRA_HEX = re.compile(r"[A-Fa-f]")
BOMS = ((codecs.BOM_UTF32_LE, "utf-32"), (codecs.BOM_UTF32_BE, "utf-32"),   # antes que UTF-16: su BOM empieza igual
        (codecs.BOM_UTF16_LE, "utf-16"), (codecs.BOM_UTF16_BE, "utf-16"), (codecs.BOM_UTF8, "utf-8-sig"))

# Una entrada del índice cuyo objeto este programa no puede leer: el hook la frena, porque lo que no se lee no se da
# por limpio.
SIN_OBJETO = "objeto que git no tiene"


def _lista(fabrica):
    # sin repr: los nombres de archivo podrían traer un dato, y unittest muestra variables
    return dataclasses.field(default_factory=fabrica, repr=False)


@dataclasses.dataclass
class Cuenta:
    hallazgos: list = _lista(list)                        # (tipo, archivo, línea, detalle): nunca el valor
    permitidos: collections.Counter = _lista(collections.Counter)   # tipo -> cuántos
    saltos: collections.Counter = _lista(collections.Counter)       # motivo -> cuántos: lo que pasa, declarado
    archivos: int = 0
    del_indice: int = 0
    descartados: list = _lista(list)                      # (archivo, motivo): binarios, ilegibles, fuera del repo
    ausentes: list = _lista(list)                         # seguidos por git y borrados del árbol de trabajo


def evidente(cifras):
    """Un número inventado a la vista: todas sus cifras iguales, o seguidas de a una, subiendo o bajando."""
    if len(set(cifras)) <= 1:
        return True
    pasos = {(int(b) - int(a)) % 10 for a, b in zip(cifras, cifras[1:])}
    return pasos in ({1}, {9})


def dv_rut(cuerpo):
    s, m = 0, 2
    for d in reversed(cuerpo):
        s += int(d) * m
        m = 2 if m == 7 else m + 1
    r = 11 - s % 11
    return "0" if r == 11 else "K" if r == 10 else str(r)


def contenedor_valido(c):
    """El dígito de control de ISO 6346: las letras valen de 10 a 38, sin los múltiplos de 11."""
    valores, n = {}, 10
    for letra in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        if n % 11 == 0:
            n += 1
        valores[letra] = n
        n += 1
    s = sum((valores[ch] if ch.isalpha() else int(ch)) * 2 ** i for i, ch in enumerate(c[:10]))
    return (s % 11) % 10 == int(c[10])


def _blanco(m):
    """Lo que se aparta queda en espacios, del mismo largo y con sus saltos de línea: las líneas no se mueven."""
    return re.sub(r"[^\n]", " ", m.group(0))


def _apartar_permitidos(t, cuenta):
    """La propia empresa delimitada por un signo (comillas, «», paréntesis, un igual) se aparta antes de buscar."""
    for tipo, valor, _ in PERMITIDOS:
        if tipo != "razón social":
            continue
        rx = re.compile(r"(?<![\w\s.&'’-])" + re.escape(valor) + r"(?!\w)", re.I)
        t, n = rx.subn(_blanco, t)
        if n:
            cuenta.permitidos[tipo] += n
    return t


def _sin_las_formas_propias(t, archivo, cuenta):
    """En este mismo archivo, lo que va entre sus dos marcas queda fuera de la razón social (solo de ella)."""
    if archivo != PROPIO:
        return t
    lineas = t.split("\n")
    desde = [i for i, linea in enumerate(lineas) if linea.strip() == MARCA_DESDE]
    hasta = [i for i, linea in enumerate(lineas) if linea.strip() == MARCA_HASTA]
    if len(desde) != 1 or len(hasta) != 1 or desde[0] > hasta[0]:
        return t                                   # sin sus marcas, se revisa entero: falla cerrada
    cuenta.saltos["las formas, en el archivo de la guarda"] += 1
    return "\n".join(" " * len(linea) if desde[0] <= i <= hasta[0] else linea for i, linea in enumerate(lineas))


def _preparar(t):
    for rx, por in SEPARADORES:
        t = rx.sub(por, t)
    return t


class _Lineas:
    """La línea (1..n) de una posición de un texto. Los saltos de línea se cuentan una vez, con el primer hallazgo:
    contar desde el principio en cada uno hacía la revisión cuadrática (60.000 hallazgos en 1,4 MB, 46 s; lo midió la
    revisión de seguridad del encargo 72)."""

    def __init__(self, t):
        self.t, self.saltos = t, None

    def __call__(self, i):
        if self.saltos is None:
            self.saltos = [m.start() for m in re.finditer("\n", self.t)]
        return bisect.bisect_left(self.saltos, i) + 1


def _razones(t, archivo, cuenta):
    p = _preparar(t)
    linea = _Lineas(p)

    def una(m, nombre, forma, delante):
        palabras = nombre.split()
        if delante and forma == "PT" and FAMILIA_PT.match(clave(palabras[0])) and not (
                len(palabras) > 1 and palabras[1][:1].isupper()):
            cuenta.saltos["tipografía PT"] += 1
        elif len(nombre) == 1 and nombre.isalpha():
            cuenta.saltos["plantilla de una letra"] += 1
        elif all(len(w) == 1 for w in clave(m.group(0)).split()) and re.match(r"\s[^\W\d_](?![^\W_])", p[m.end():]):
            # Una palabra escrita con sus letras separadas, que sigue después de la «forma»: el logo del panel. Unas
            # iniciales que terminan en la forma («J&J», o tres iniciales y la forma) sí cuentan.
            cuenta.saltos["letras sueltas"] += 1
        elif not delante and re.search(r"[,/]", p[m.end(1):m.start(2)]) and all(
                FORMA_SOLA.fullmatch(w) for w in palabras):
            cuenta.saltos["lista de formas jurídicas"] += 1
        elif permitido("razón social", m.group(0)):
            cuenta.permitidos["razón social"] += 1
        else:
            cuenta.hallazgos.append(("razón social", archivo, linea(m.start()), " ".join(forma.split())))
    for m in RAZON_DETRAS.finditer(p):
        una(m, m.group(1), m.group(2), False)
    for m in RAZON_DELANTE.finditer(p):
        una(m, m.group(2), m.group(1), True)


def _datos(t, archivo, cuenta):
    linea = _Lineas(t)

    def hallazgo(tipo, m):
        cuenta.hallazgos.append((tipo, archivo, linea(m.start()), ""))

    def numero(tipo, m, cifras):
        if evidente(cifras):
            cuenta.saltos["número inventado a la vista"] += 1
        else:
            hallazgo(tipo, m)

    for m in RUT.finditer(t):
        cuerpo = "".join(m.groups()[:3]).lstrip("0")
        if cuerpo and dv_rut(cuerpo) == m.group(4).upper():
            numero("RUT", m, cuerpo)
    for m in CORREO.finditer(t):
        # El usuario y la clave de una dirección («https://usuario:clave@…»), solo si lo que va antes, en el mismo
        # token, trae «://». Hasta la revisión de seguridad del encargo 72 bastaba un «:» delante, y un correo escrito
        # como «contacto:alguien@…» pasaba.
        inicio = max(t.rfind(c, 0, m.start()) for c in CORTES) + 1
        if "://" in t[inicio:m.start()]:
            cuenta.saltos["usuario y clave de una dirección"] += 1
        elif DOMINIOS_RESERVADOS.search(m.group(2)):
            cuenta.saltos["correo de un dominio reservado"] += 1
        elif permitido("correo", m.group(0)):
            cuenta.permitidos["correo"] += 1
        else:
            hallazgo("correo", m)
    for m in CONTENEDOR.finditer(t):
        c = "".join(m.groups())
        if contenedor_valido(c):
            numero("contenedor", m, c[4:10])
    for m in TELEFONO.finditer(t):
        numero("teléfono", m, re.sub(r"\D", "", m.group(0))[-8:])
    for m in RESERVA.finditer(t):
        numero("número de reserva", m, m.group(1))
    for m in RESERVA_MAERSK.finditer(t):
        numero("número de reserva", m, m.group(1))
    for m in RESERVA_CON_ETIQUETA.finditer(t):
        if not RESERVA_MAERSK.fullmatch(m.group(1)):    # los de MAERSK ya los vio RESERVA_MAERSK
            numero("número de reserva", m, m.group(1))
    for m in RESERVA_CMA.finditer(t):
        numero("número de reserva", m, m.group(1))
    for m in RESERVA_COSCO.finditer(t):
        numero("número de reserva", m, m.group(1))
    for m in BL.finditer(t):
        if re.search(r"\d{6}", m.group(1)):
            numero("BL", m, re.sub(r"\D", "", m.group(1)))
    for m in PEDIDO.finditer(t):
        numero("pedido", m, m.group(1))
    for m in IPV4.finditer(t):
        try:
            ip = ipaddress.IPv4Address(m.group(1))
        except ValueError:
            continue                            # una versión, como la de Chrome: no es una IP
        if ip.is_global:
            hallazgo("IP pública", m)
        else:
            cuenta.saltos["IP privada, local o de documentación"] += 1
    for m in PERSONA.finditer(t):
        if permitido("nombre y apellido", t, m.start()):
            cuenta.permitidos["nombre y apellido"] += 1
        else:
            hallazgo("nombre y apellido", m)


def revisar_texto(texto, archivo, cuenta):
    """Busca en `texto` y anota en `cuenta`. Es lo único que mira el contenido: la suite y el hook pasan por acá."""
    t = unicodedata.normalize("NFC", texto).translate(INVISIBLES)
    t, n = BASE64.subn(_blanco, t)
    if n:
        cuenta.saltos["tira en base64"] += n

    def hash_(m):
        if LETRA_HEX.search(m.group(0)):
            cuenta.saltos["hash"] += 1
            return _blanco(m)
        return m.group(0)
    t = HASH.sub(hash_, t)
    t = _apartar_permitidos(t, cuenta)
    _razones(_sin_las_formas_propias(t, archivo, cuenta), archivo, cuenta)
    _datos(t, archivo, cuenta)


def _leer(datos, archivo, cuenta, nombre=None):
    """Los bytes de un archivo: texto (UTF-8, o Windows-1252 si no es UTF-8, o UTF-16 o UTF-32 con BOM) o, si trae NUL,
    binario, que se lee por las letras que trae sueltas y frena el commit. `nombre` es como se informa (la ruta, o la
    ruta y «(índice)»)."""
    nombre = nombre or archivo
    if b"\0" not in datos:
        try:
            texto = datos.decode("utf-8")
        except UnicodeDecodeError:
            # Leído como UTF-8 con reemplazos, una «ñ» de Windows-1252 partía la palabra, y la razón social no se veía
            # (lo midió la revisión de seguridad del encargo 72).
            texto = datos.decode("cp1252", "replace")
            cuenta.saltos["leído como Windows-1252"] += 1
    else:
        texto = None
        for bom, codificacion in BOMS:
            if datos.startswith(bom):
                try:
                    texto = datos.decode(codificacion)
                except UnicodeDecodeError:
                    pass
                break
        if texto is None:
            cuenta.descartados.append((nombre, "binario"))
            texto = datos.replace(b"\0", b"").decode("utf-8", "replace")
    antes = len(cuenta.hallazgos)
    revisar_texto(texto, archivo, cuenta)
    if nombre != archivo:                       # el hallazgo dice de dónde salió: del índice, no del árbol
        cuenta.hallazgos[antes:] = [(t, nombre, n, d) for t, _, n, d in cuenta.hallazgos[antes:]]


def _matar_arbol(p):
    """Al vencer el plazo, git y todo lo que lanzó. Desde PowerShell o cmd, `git` es un lanzador que corre el git real
    como hijo, y Popen.kill() mata solo al lanzador; y un hijo de git con las tuberías abiertas dejaba esperando a
    communicate() sin plazo (300 s con un plazo de 4: lo midió la revisión de seguridad del encargo 72). Por eso, el
    taskkill de System32 con su árbol, y la última lectura también con plazo (ya no espera a un hijo que quedó vivo)."""
    if os.name == "nt":
        taskkill = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32", "taskkill.exe")
        try:
            POPEN([taskkill, "/T", "/F", "/PID", str(p.pid)], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                  stderr=subprocess.DEVNULL).wait(timeout=30)
        except (OSError, subprocess.TimeoutExpired):
            pass                                   # queda el kill de abajo
    p.kill()
    try:
        p.communicate(timeout=10)
    except subprocess.TimeoutExpired:
        pass                                       # el error que sigue lo dice; no se espera más


# --- lo que versiona git ----------------------------------------------------------------------------------------------
def _git(raiz, *argumentos, entrada=None, indice=None):
    # Sin las GIT_* heredadas: con un GIT_DIR (un hook de git lo pone), git leería ese repo y no el de `raiz`. El índice
    # se pasa a propósito cuando hace falta: es el que git le da al hook pre-commit.
    entorno = {k: v for k, v in os.environ.items() if not k.upper().startswith("GIT_")}
    if indice is not None:
        entorno["GIT_INDEX_FILE"] = str(indice)
    p = POPEN(["git", "-C", str(raiz), *argumentos],
              stdin=subprocess.PIPE if entrada is not None else subprocess.DEVNULL,
              stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=entorno)
    try:
        salida, error = p.communicate(entrada, timeout=PLAZO_GIT)
    except subprocess.TimeoutExpired:
        _matar_arbol(p)
        raise RuntimeError(f"git {argumentos[0]}: no terminó en {PLAZO_GIT} s")
    if p.returncode:
        raise RuntimeError(f"git {argumentos[0]}: {error.decode('utf-8', 'replace').strip()}")
    return salida


def _lote(raiz, objetos, indice=None):
    """El contenido de cada objeto (`:ruta` del índice, o un sha), en una sola llamada; None si git no lo tiene."""
    if not objetos:
        return []
    salida = _git(raiz, "cat-file", "--batch", entrada=b"".join(o.encode("utf-8") + b"\n" for o in objetos),
                  indice=indice)
    contenidos, i = [], 0
    for _ in objetos:
        fin = salida.index(b"\n", i)
        cabecera, i = salida[i:fin].split(), fin + 1
        if cabecera[-1] == b"missing":
            contenidos.append(None)
            continue
        tamano = int(cabecera[2])
        contenidos.append(salida[i:i + tamano])
        i += tamano + 1
    return contenidos


def versionables(raiz):
    """Lo que git versionaría: lo seguido y lo nuevo que .gitignore no excluye. `raiz` tiene que ser la raíz de un repo:
    una carpeta sin .git propio, dentro de otro repo, leería las reglas y los archivos de ese otro."""
    tope = _git(raiz, "rev-parse", "--show-toplevel").decode("utf-8").strip()
    if pathlib.Path(tope).resolve() != pathlib.Path(raiz).resolve():
        raise RuntimeError(f"{raiz} no es la raíz de un repo de git")
    salida = _git(raiz, "ls-files", "-z", "--cached", "--others", "--exclude-standard")
    return sorted({r.decode("utf-8") for r in salida.split(b"\0") if r})


def _del_indice(raiz):
    """{ruta: contenido} de lo que el índice guarda distinto del árbol de trabajo (cambiado o borrado sin agregar)."""
    rutas = sorted({r.decode("utf-8") for r in _git(raiz, "diff", "--name-only", "-z").split(b"\0") if r})
    return dict(zip(rutas, _lote(raiz, [":" + r for r in rutas])))


def escanear(raiz, fuentes=None):
    """Lo que git versionaría en `raiz`. Con `fuentes` (la copia de las fuentes del censo, soporte.FUENTES), cada
    archivo que la copia trae se lee de ahí: el censo deja en ella su archivo mutado."""
    cuenta = Cuenta()
    adentro = pathlib.Path(raiz).resolve()
    for rel in versionables(raiz):
        revisar_texto(rel, rel + " (nombre)", cuenta)   # el nombre también entra al repo
        copia = pathlib.Path(fuentes) / rel if fuentes is not None else None
        ruta = copia if copia is not None and copia.is_file() else pathlib.Path(raiz) / rel
        try:
            if ruta.is_symlink():
                datos = os.readlink(ruta).encode("utf-8")   # lo que git guarda de un enlace; nunca se sigue
            elif ruta == pathlib.Path(raiz) / rel and not ruta.resolve().is_relative_to(adentro):
                cuenta.descartados.append((rel, "fuera del repo"))   # una carpeta del camino lleva afuera
                continue
            elif ruta.is_file():
                datos = ruta.read_bytes()
            elif not ruta.exists():
                cuenta.ausentes.append(rel)
                continue
            else:
                cuenta.descartados.append((rel, "no es un archivo"))
                continue
        except OSError as e:
            cuenta.descartados.append((rel, f"no se abre ({type(e).__name__})"))
            continue
        cuenta.archivos += 1
        _leer(datos, rel, cuenta)
    for rel, datos in _del_indice(raiz).items():
        nombre = f"{rel} (índice)"
        if datos is None:
            cuenta.descartados.append((nombre, "sin versión en el índice"))
            continue
        cuenta.del_indice += 1
        _leer(datos, rel, cuenta, nombre)
    return cuenta


def escanear_indice(raiz, indice):
    """Lo que lleva el índice `indice`, que es lo que se va a commitear: cada entrada, por su nombre y por el objeto que
    guarda. No lee el árbol de trabajo ni lo nuevo sin agregar, que no entra en el commit."""
    cuenta = Cuenta()
    objetos = {}
    for e in _git(raiz, "ls-files", "-s", "-z", indice=indice).split(b"\0"):
        if not e:
            continue
        meta, ruta = e.split(b"\t", 1)
        modo, objeto, etapa = meta.split()
        rel = ruta.decode("utf-8")
        revisar_texto(rel, rel + " (nombre)", cuenta)
        if etapa != b"0":
            cuenta.descartados.append((rel, "conflicto sin resolver"))
        elif modo == b"160000":
            cuenta.descartados.append((rel, "submódulo"))
        else:
            objetos[rel] = objeto.decode("ascii")
    for (rel, objeto), datos in zip(objetos.items(), _lote(raiz, list(objetos.values()), indice=indice)):
        if datos is None:
            cuenta.descartados.append((rel, SIN_OBJETO))
            continue
        cuenta.archivos += 1
        _leer(datos, rel, cuenta)
    return cuenta


def por_tipo(cuenta):
    """{tipo: cuántos} de los hallazgos."""
    return dict(collections.Counter(h[0] for h in cuenta.hallazgos))


def mostrar(nombre):
    """Un nombre de archivo para mostrar, sin el dato que pueda traer. Si la guarda ve un dato en la ruta, queda su
    carpeta y «‹un nombre con un dato›» (o, si el dato está en la carpeta, «‹una ruta con un dato›»); si no, la ruta,
    sin sus tiras de 5 cifras o más. Lo de «(nombre)» y «(índice)» se conserva. Hasta la revisión de seguridad del
    encargo 72, un nombre con una razón social o un correo salía entero en el informe, en el hook y en la suite."""
    m = re.fullmatch(r"(.*?)((?: \((?:nombre|índice)\))*)", nombre, re.S)
    ruta, sufijo = m.group(1), m.group(2)

    def con_dato(texto):
        c = Cuenta()
        revisar_texto(texto, "nombre", c)
        return bool(c.hallazgos)
    if con_dato(ruta):
        carpeta = ruta.rsplit("/", 1)[0] if "/" in ruta else ""
        ruta = "‹una ruta con un dato›" if carpeta and con_dato(carpeta) else \
            (carpeta + "/" if carpeta else "") + "‹un nombre con un dato›"
    return re.sub(r"\d{5,}", "<cifras>", ruta) + sufijo


def informe(hallazgos, tope=30):
    """Tipo, archivo y línea de cada hallazgo, y la forma de una razón social: nunca el valor."""
    lineas = [f"{mostrar(a)}:{n} {t}" + (f" ({d})" if d else "")
              for t, a, n, d in sorted(hallazgos, key=lambda h: h[1:3])]
    return "; ".join(lineas[:tope]) + (f"; y {len(lineas) - tope} más" if len(lineas) > tope else "")


# --- los controles ----------------------------------------------------------------------------------------------------
def muestras():
    """Un ejemplo inventado de cada tipo, armado por partes: (texto, lo que tiene que dar)."""
    sa, ltda = "S" + chr(46) + "A" + chr(46), "Lt" + "da."
    cuerpo = "76" + "543" + "218"
    rut = f"{cuerpo[:2]}.{cuerpo[2:5]}.{cuerpo[5:]}-{dv_rut(cuerpo)}"
    propia = PERMITIDOS[0][1]
    return [
        ("Pesquera Inventada " + sa, "razón social"),
        ("PESQUERA INVENTADA " + chr(83) + "PA", "razón social"),
        ("Pesquera Inventada " + ltda, "razón social"),
        (chr(79) * 3 + " «Pesquera Inventada»", "razón social"),
        ("Pesquera del sur <b>" + sa + "</b>", "razón social"),
        ("Cliente Inventado " + propia, "razón social"),            # un nombre ajeno delante del propio: frena
        ("Copyright " + propia, "razón social"),
        (chr(80) + "T Sans Inventada Foods", "razón social"),
        (chr(83) + "AS " + chr(65) + "B", "razón social"),           # un nombre que es una forma, sin coma: cuenta
        ("font-family: 'PT Sans', sans-serif; /* PT Sans trae dos pesos */", "tipografía PT"),
        ("X " + sa, "plantilla de una letra"),
        ('text="A Q U A S H I E L D"', "letras sueltas"),
        ("A B C " + sa, "razón social"),                          # unas iniciales que terminan en la forma: cuentan
        ("Pesquera Inventada" + chr(0x200B) + sa, "razón social"),  # un invisible entre el nombre y la forma
        ("formas (" + "SpA, Ltda., Inc." + ")", "lista de formas jurídicas"),
        ('NOMBRE = "' + propia + '"', "permitido"),
        ("su cliente " + propia + " va en el formulario", "permitido"),
        ("return a.s+n.v", "nada"),
        ("rut " + rut, "RUT"),
        ("alguien" + "@" + "dominio-real.cl", "correo"),
        ("contacto:" + "alguien" + "@" + "dominio-real.cl", "correo"),     # «:» delante, sin «://»: es un correo
        (PERMITIDOS[3][1].replace("+", "."), "correo"),                   # el del dueño, con otra puntuación
        ("alguien" + "@" + "dominio.example.com", "correo de un dominio reservado"),
        ("https://" + "usuario:clave" + "@portal.cl/x", "usuario y clave de una dirección"),
        (PERMITIDOS[3][1], "permitido"),
        ("CSQU" + "305438" + "3", "contenedor"),                   # el ejemplo de la norma ISO 6346
        ("+56 9 " + "8765" + " 4312", "teléfono"),
        ("(2) " + "2654" + " 3210", "teléfono"),
        ("(02) " + "2654" + " 3210", "teléfono"),
        ("SCLG" + "2794" + "6031", "número de reserva"),
        ("bkg " + "27" + "3958164", "número de reserva"),
        ("Booking number: " + "6213" + "48957", "número de reserva"),
        ("EBKG" + "1234" + "5678", "número inventado a la vista"),
        ("EBKG" + "7777" + "7777", "número inventado a la vista"),
        ("bkg " + "27" + "7654321", "número inventado a la vista"),
        # Encargo 77: MAERSK con 28 (con su etiqueta, una sola vez), CMA-CGM y COSCO.
        ("bkg " + "28" + "3958164", "número de reserva"),
        ("Booking number: " + "28" + "3958164", "número de reserva"),
        ("bkg " + "28" + "1234567", "número inventado a la vista"),
        ("Booking " + "QXZ" + "3958164", "número de reserva"),
        ("Booking " + "QXZ" + "1234567", "número inventado a la vista"),
        ("Booking " + "CD" + "3958164027", "número de reserva"),
        ("Booking " + "CD" + "1234567890", "número inventado a la vista"),
        # Sus bordes (revisiones del encargo 77): una cifra o una letra de más, pegada, ya no es la forma medida.
        ("Booking " + "QXZ" + "3958164" + "7", "nada"),                # 8 cifras
        ("Booking " + "QXZ" + "3958164" + "K", "nada"),                # una letra pegada después
        ("Booking " + "1" + "QXZ" + "3958164", "nada"),                # una cifra pegada antes
        ("Booking " + "CD" + "3958164027" + "5", "nada"),              # 11 cifras
        ("Booking " + "X" + "CD" + "3958164027", "nada"),              # una letra pegada antes
        # Y su forma ancha: otras dos letras, en minúscula, con un espacio o un guion antes de las cifras.
        ("Booking " + "XD" + "3958164027", "número de reserva"),
        ("booking " + "qxz" + "3958164", "número de reserva"),
        ("Booking " + "QXZ-" + "3958164", "número de reserva"),
        ("Booking " + "CD " + "3958164027", "número de reserva"),
        # Detrás del escape de un literal («\n» escrito, con su barra), en las tres formas con letras.
        ("Booking enviado" + "\\n" + "QXZ" + "3958164", "número de reserva"),
        ("x" + "\\t" + "CD" + "3958164027", "número de reserva"),
        ("x" + "\\n" + "SCLG" + "2794" + "6031", "número de reserva"),
        # «Booking:» es una etiqueta: así escribe el programa el número de una EMITIDA, también con otro prefijo.
        ("MAERSK emitida con éxito (Booking: " + "29" + "3958164" + ")", "número de reserva"),
        ("MAERSK emitida con éxito (Booking: " + "123456789" + ")", "número inventado a la vista"),
        ("MAEU" + "246810" + "357", "BL"),
        ("pedido " + "40" + "871236", "pedido"),
        ("desde " + "200." + "45.17.9", "IP pública"),
        ("desde " + "192.0." + "2.17", "IP privada, local o de documentación"),
        ("Chrome " + "145.0." + "7632.6", "nada"),
        ("desde " + "300.1." + "2.3", "nada"),                     # parece una IP, pero 300 no es un octeto
        ("Juan" + " Inventado", "nombre y apellido"),
        ("Marcelo" + " Inventado", "nombre y apellido"),           # el nombre de pila del dueño, con otro apellido
        (PERMITIDOS[1][1] + " <correo>", "permitido"),
        (PERMITIDOS[1][1] + "zz", "nombre y apellido"),           # el del dueño, con otra palabra pegada
        ("© " + PERMITIDOS[2][1], "permitido"),
        ("commit " + "9f3a" + "c0e4d1b2a3f4e5d6", "hash"),
        ("x = '" + "QUJD" * 60 + "'", "tira en base64"),
    ]


def como_sale(cuenta):
    if cuenta.hallazgos:
        return cuenta.hallazgos[0][0] if len(cuenta.hallazgos) == 1 else "varios"
    if cuenta.saltos:
        return next(iter(cuenta.saltos)) if len(cuenta.saltos) == 1 else "varios"
    return "permitido" if cuenta.permitidos else "nada"


def control_detector():
    """Control positivo del detector: cada muestra tiene que dar exactamente lo suyo. Devuelve las que no."""
    rotas = []
    for texto, esperado in muestras():
        c = Cuenta()
        revisar_texto(texto, "muestra", c)
        if como_sale(c) != esperado:
            rotas.append(f"«{esperado}» salió «{como_sale(c)}»")
    return rotas


def _union(destino, enlace):
    """Una unión de Windows (en otro sistema, un enlace a la carpeta): crearla no pide permisos de administrador."""
    try:
        import _winapi
    except ImportError:
        os.symlink(destino, enlace, target_is_directory=True)
    else:
        _winapi.CreateJunction(str(destino), str(enlace))


@contextlib.contextmanager
def _git_ajeno(tmp):
    """Como corre git desde un hook: con GIT_DIR y GIT_INDEX_FILE puestos, que apuntan a otro lado."""
    nombres = ("GIT_DIR", "GIT_INDEX_FILE")
    antes = {k: os.environ.get(k) for k in nombres}
    os.environ.update({k: str(pathlib.Path(tmp) / "no-es-un-repo") for k in nombres})
    try:
        yield
    finally:
        for k, v in antes.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def _repo_inventado(tmp, prefijo):
    raiz = pathlib.Path(tmp) / (prefijo + uuid.uuid4().hex[:8])
    raiz.mkdir(parents=True)
    _git(raiz, "-c", "init.defaultBranch=main", "init", "-q")
    return raiz


def _dato():
    """Una razón social inventada, armada por partes."""
    return ("Pesquera Inventada " + "S" + chr(46) + "A" + chr(46)).encode("utf-8")


def control(tmp):
    """Control positivo de la lectura: un repo inventado con un caso de cada forma de entrar. Si no da exactamente lo
    esperado, no audita (RuntimeError)."""
    raiz = _repo_inventado(tmp, "guarda_")
    d = _dato()
    numero = "SCLG" + "2794" + "6031"
    archivos = {
        "texto.md": b"Lo pidio " + d + b" ayer.",
        "numero.txt": b"reserva " + numero.encode(),
        "limpio.md": b"Nada que ver aqui.",
        "utf16.txt": codecs.BOM_UTF16_LE + ("dato " + d.decode()).encode("utf-16-le"),
        "latin.txt": ("Lo pidió Pesquera Ñandú " + "S" + chr(46) + "A" + chr(46)).encode("cp1252"),
        "fuente.bin": b"\0\1" + d,
        "nombre " + numero + ".md": b"",
        "indice.md": d,
        "borrado.md": d,
        "sub/vacio.txt": b"",
        "union/f.txt": b"",
        ".gitignore": b"ignorado.md\n",
    }
    for nombre, datos in archivos.items():
        (raiz / nombre).parent.mkdir(parents=True, exist_ok=True)
        (raiz / nombre).write_bytes(datos)
    _git(raiz, "add", "-f", "--", *archivos)    # -f: aunque un .gitignore global de quien corre la suite los excluya
    afuera = raiz.parent / (raiz.name + "_afuera")
    afuera.mkdir()
    (afuera / "f.txt").write_bytes(d)
    (raiz / "union" / "f.txt").unlink()
    (raiz / "union").rmdir()
    _union(afuera, raiz / "union")                # la carpeta seguida pasa a llevar afuera: no se lee
    (raiz / "indice.md").write_bytes(b"limpio")   # agregado con el dato y limpiado después, sin volver a agregar
    (raiz / "borrado.md").unlink()                # borrado sin agregar: el índice lo conserva
    (raiz / "nuevo.md").write_bytes(d)            # sin agregar: git lo versionaría igual
    (raiz / "ignorado.md").write_bytes(d)         # .gitignore lo excluye: no se lee
    with _git_ajeno(tmp):
        c = escanear(raiz)
    try:
        versionables(raiz / "sub")   # una carpeta dentro de un repo no es la raíz de un repo
    except RuntimeError:
        pass
    else:
        raise RuntimeError("control positivo: el instrumento lee una carpeta que no es la raíz de un repo")
    obtenido = {
        "hallazgos": sorted((mostrar(a), t) for t, a, _, _ in c.hallazgos),
        "descartados": sorted(n for n, _ in c.descartados),
        "ausentes": c.ausentes,
    }
    esperado = {
        "hallazgos": sorted([("texto.md", "razón social"), ("numero.txt", "número de reserva"),
                             ("utf16.txt", "razón social"), ("latin.txt", "razón social"),
                             ("fuente.bin", "razón social"),
                             (mostrar("nombre " + numero + ".md (nombre)"), "número de reserva"),
                             ("indice.md (índice)", "razón social"), ("borrado.md (índice)", "razón social"),
                             ("nuevo.md", "razón social")]),
        "descartados": ["fuente.bin", "union/f.txt"],
        "ausentes": ["borrado.md"],
    }
    if obtenido != esperado:
        raise RuntimeError("control positivo: el instrumento no ve sus casos conocidos y no audita. Se esperaba "
                           f"{esperado} y salió {obtenido}")
    return f"repo inventado: {len(archivos) + 2} archivos"


def control_indice(tmp):
    """Control positivo de la lectura del índice, la del hook: el índice, el árbol de trabajo y un índice aparte (como
    el de `git commit -a`) dicen cosas distintas, y tiene que leer SOLO el índice que se le da."""
    raiz = _repo_inventado(tmp, "indice_")
    d = _dato()
    agregar = {"agregado.md": d, "limpio.md": b"limpio"}
    for nombre, datos in agregar.items():
        (raiz / nombre).write_bytes(datos)
    _git(raiz, "add", "-f", "--", *agregar)
    (raiz / "agregado.md").write_bytes(b"limpio")   # el índice conserva el dato
    (raiz / "limpio.md").write_bytes(d)             # el árbol lo trae, el índice no
    (raiz / "suelto.md").write_bytes(d)             # sin agregar: no entra en el commit
    indice = raiz / ".git" / "index"
    aparte = raiz / ".git" / "index-aparte"
    aparte.write_bytes(indice.read_bytes())
    (raiz / "solo-aparte.md").write_bytes(d)
    _git(raiz, "add", "-f", "--", "solo-aparte.md", indice=aparte)
    # Y una entrada cuyo objeto no existe (git la acepta en el índice): tiene que quedar como ilegible, no como limpia.
    _git(raiz, "update-index", "--add", "--cacheinfo", "100644," + "1234567890abcdef" * 2 + "12345678,roto.md",
         indice=aparte)
    with _git_ajeno(tmp):
        vistas = {"normal": escanear_indice(raiz, indice), "aparte": escanear_indice(raiz, aparte)}
    obtenido = {k: (sorted(a for _, a, _, _ in c.hallazgos), list(c.descartados)) for k, c in vistas.items()}
    esperado = {"normal": (["agregado.md"], []),
                "aparte": (["agregado.md", "solo-aparte.md"], [("roto.md", SIN_OBJETO)])}
    if obtenido != esperado:
        raise RuntimeError("control positivo del índice: no lee lo que se va a commitear y no audita. Se esperaba "
                           f"{esperado} y salió {obtenido}")
    if not veredicto(vistas["normal"])[0] or not veredicto(Cuenta(descartados=[("roto.md", SIN_OBJETO)]))[0] \
            or not veredicto(Cuenta(descartados=[("planilla.xlsx", "binario")]))[0] or veredicto(Cuenta())[0]:
        raise RuntimeError("control positivo del índice: el veredicto del hook no frena lo que tiene que frenar")
    return "índice: el propio, uno aparte y el veredicto"


def veredicto(cuenta):
    """(frena, motivo) del hook: frena un hallazgo, una entrada que no pudo leer y un binario. Un binario (una planilla
    comprimida, un PDF, una imagen) puede traer un dato que la guarda no lee: no entra al repo público. Hasta la
    revisión de seguridad del encargo 72, solo se contaba."""
    if cuenta.hallazgos:
        return True, ("Lo que vas a commitear trae datos con forma de dato real, y el repo es público. Tipo, archivo y "
                      "línea, nunca el valor: " + informe(cuenta.hallazgos)
                      + ". Reescríbelos con un valor inventado a la vista (tests/guarda_datos.py dice cuáles pasan)")
    ilegibles = [n for n, m in cuenta.descartados if m == SIN_OBJETO]
    if ilegibles:
        return True, (f"No pude leer {len(ilegibles)} entrada(s) de lo que vas a commitear "
                      f"({', '.join(mostrar(n) for n in ilegibles)}), y lo que no se lee no se da por limpio")
    binarios = [n for n, m in cuenta.descartados if m == "binario"]
    if binarios:
        return True, (f"Lo que vas a commitear trae {len(binarios)} archivo(s) binario(s) "
                      f"({', '.join(mostrar(n) for n in binarios)}): la guarda no los puede leer, y el repo es público")
    return False, ""


def resumen(cuenta):
    saltos = ", ".join(f"{m} {n}" for m, n in sorted(cuenta.saltos.items()) if n) or "ninguno"
    permitidos = ", ".join(f"{t} {n}" for t, n in sorted(cuenta.permitidos.items()) if n) or "ninguno"
    return (f"{cuenta.archivos} archivos ({cuenta.del_indice} versiones del índice distintas del árbol) · hallazgos "
            f"{len(cuenta.hallazgos)} · permitidos por valor exacto: {permitidos} · pasan, declarados: {saltos} · "
            f"descartados {len(cuenta.descartados)} · ausentes del árbol {len(cuenta.ausentes)}")


def pre_commit():
    """El hook pre-commit: la guarda sobre el índice que git le pasa (GIT_INDEX_FILE), con los controles antes.
    Devuelve el código de salida del hook: 1 frena el commit."""
    if not sys.stderr.isatty():
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    rotas = control_detector()
    if rotas:
        print(f"pre-commit: FRENADO. El detector está roto ({'; '.join(rotas)}): no puedo revisar este commit.",
              file=sys.stderr)
        return 1
    raiz = pathlib.Path(_git(pathlib.Path.cwd(), "rev-parse", "--show-toplevel").decode("utf-8").strip())
    # GIT_INDEX_FILE es relativo a donde git corre el hook (la raíz del árbol). Un índice que no existe se leería como
    # uno vacío, y daría un verde con cero archivos: frena.
    puesto = os.environ.get("GIT_INDEX_FILE")
    indice = (pathlib.Path.cwd() / puesto) if puesto else \
        raiz / _git(raiz, "rev-parse", "--git-path", "index").decode("utf-8").strip()
    if not indice.is_file():
        print(f"pre-commit: FRENADO. No encuentro el índice que se va a commitear ({indice}): no puedo revisar este "
              "commit. Si sabes lo que haces: git commit --no-verify", file=sys.stderr)
        return 1
    with tempfile.TemporaryDirectory(prefix="guarda-pre-commit-", ignore_cleanup_errors=True) as tmp:
        vistos = [control(tmp), control_indice(tmp)]
    c = escanear_indice(raiz, indice)
    print(f"pre-commit: guarda de datos reales, controles en verde (detector: {len(muestras())} muestras · "
          f"{' · '.join(vistos)}). Lo que se va a commitear: {resumen(c)}", file=sys.stderr)
    frena, motivo = veredicto(c)
    if not frena:
        return 0
    print(f"pre-commit: FRENADO. {motivo}. Si sabes lo que haces: git commit --no-verify", file=sys.stderr)
    return 1


def a_mano():
    """`python tests/guarda_datos.py`: lo que git versionaría hoy en este repo, con lo no commiteado."""
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    rotas = control_detector()
    if rotas:
        print(f"ABORTA: el detector está roto ({'; '.join(rotas)})")
        return 2
    with tempfile.TemporaryDirectory(prefix="guarda-", ignore_cleanup_errors=True) as tmp:
        vistos = [control(tmp), control_indice(tmp)]
    c = escanear(RAIZ)
    print(f"controles en verde (detector: {len(muestras())} muestras · {' · '.join(vistos)})")
    print(f"lo que git versionaría: {resumen(c)}")
    if c.hallazgos:
        print("hallazgos (tipo, archivo y línea, nunca el valor): " + informe(c.hallazgos, tope=200))
    return 1 if c.hallazgos else 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--pre-commit"]:
        sys.exit(pre_commit())
    if sys.argv[1:]:
        sys.exit("uso: python tests/guarda_datos.py [--pre-commit]")
    sys.exit(a_mano())
