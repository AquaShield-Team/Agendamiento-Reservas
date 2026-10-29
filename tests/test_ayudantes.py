# -*- coding: utf-8 -*-
"""Ayudantes puros de cada naviera: lo que se puede verificar sin portal.
Los valores por defecto que son datos de la empresa (contratos, razón social)
se fotografían por hash, para no escribirlos en las pruebas."""
import ast
import datetime
import hashlib
import inspect
import itertools
import json
import re
import types
import unittest
import weakref
from pathlib import Path
from unittest import mock

import cv2
import numpy as np
import openpyxl

import soporte
from test_envio import correr_node


def h(s):
    return hashlib.sha256(str(s).encode("utf-8")).hexdigest()[:16]


def con_opciones(caso, opciones):
    """Mientras dura la prueba, cargar_config devuelve una configuración con estas 'opciones'."""
    original = caso.mod.cargar_config
    caso.mod.cargar_config = lambda: {"opciones": dict(opciones)}
    caso.addCleanup(setattr, caso.mod, "cargar_config", original)


def con_contratos(caso, contratos):
    """Mientras dura la prueba, cargar_config devuelve una configuración con estos contratos por defecto (None: sin
    la llave). Desde el encargo 44 viven en config.json → opciones → contratos_por_defecto."""
    original = caso.mod.cargar_config
    opciones = {} if contratos is None else {"contratos_por_defecto": contratos}
    caso.mod.cargar_config = lambda: {"opciones": opciones}
    caso.addCleanup(setattr, caso.mod, "cargar_config", original)


# Dónde pide cada naviera su contrato por defecto (función, llave): una por cada valor que estaba escrito en el
# programa hasta el encargo 44 (HYUNDAI, en sus dos pasos).
LLAMADAS_CONTRATO = [("_determinar_contrato_one", "one_otros"), ("_determinar_contrato_one", "one_usa"),
                     ("reservar_hyundai", "hyundai"), ("reservar_hyundai", "hyundai"), ("reservar_msc", "msc")]


class TestONE(soporte.CasoAQ):
    def test_contrato_one(self):
        f = self.mod._determinar_contrato_one
        con_contratos(self, {"one_usa": "CT-DEF-USA", "one_otros": "CT-DEF-OTR"})
        self.assertEqual(f({"cotizacion": "CT-X", "destino_final": "LONG BEACH"}, {"contrato_usa": "CT-USA"}), "CT-X")
        self.assertEqual(f({"destino_final": "LONG BEACH"}, {"contrato_usa": "CT-USA", "contrato": "CT-GEN"}), "CT-USA")
        self.assertEqual(f({"destino_final": "LONG BEACH"}, {"contrato": "CT-GEN"}), "CT-GEN")
        self.assertEqual(f({"destino_final": "PUERTO FALSO, USA"}, {}), "CT-DEF-USA")
        self.assertEqual(f({"destino_orig": "CIUDAD GAMMA"}, {"contrato_otros": "CT-OTR"}), "CT-OTR")
        self.assertEqual(f({"destino_orig": "CIUDAD GAMMA"}, {}), "CT-DEF-OTR")
        # Fuera de EE. UU. el 'contrato' general de las credenciales NO se usa: va el de por defecto, que desde el
        # encargo 44 sale de config.json (antes estaba escrito en el programa, y aquí se comparaba por hash).
        self.assertEqual(f({"destino_orig": "CIUDAD GAMMA"}, {"contrato": "CT-GEN"}), "CT-DEF-OTR")


class TestMSC(soporte.CasoAQ):
    def test_desde_msc(self):
        # Hasta 384d3ce (_msc_fecha_futura): hoy + 18 si la fila no traía fecha, o la traía pasada o a 2 días. El portal no
        # lo exige: MSC busca desde hoy, como las demás (CICLO-proxima-salida.md).
        f = self.mod._msc_desde
        hoy = datetime.date.today()
        mas = lambda n: hoy + datetime.timedelta(days=n)
        self.assertEqual(f({"dia_carga": mas(30).isoformat()}), mas(30))
        self.assertEqual(f({"dia_retiro": mas(10).strftime("%d-%m-%Y")}), mas(10))
        self.assertEqual(f({"dia_carga": mas(1).strftime("%d/%m/%Y")}), mas(1))      # a menos de 2 días, también
        for r in ({"dia_carga": "2020-01-01"}, {}, {"dia_carga": "pronto"}):          # pasada, vacía o ilegible: hoy
            with self.subTest(r=r):
                self.assertEqual(f(r), hoy)
        # Un día de carga ilegible cuenta como si la fila no lo trajera: vale el de retiro (CICLO-cola-cuatro-items.md).
        self.assertEqual(f({"dia_carga": "pronto", "dia_retiro": mas(10).strftime("%d-%m-%Y")}), mas(10))

    def test_fecha_etd_msc(self):
        # La ETD como la lee _JS_MSC_NAVES de cada tarjeta («ETD dd MMM aaaa», medida en la corrida del 2026-09-25).
        f = self.mod._msc_fecha_etd
        casos = (("27 SEP 2026", datetime.date(2026, 9, 27)), ("03 Oct 2026", datetime.date(2026, 10, 3)),
                 (" 1 JAN 2027 ", datetime.date(2027, 1, 1)), ("31 FEB 2026", None), ("27 SET 2026", None),
                 ("2026-09-27", None), ("", None), (None, None))
        for texto, esperado in casos:
            with self.subTest(texto=texto):
                self.assertEqual(f(texto), esperado)


class TestFechas(soporte.CasoAQ):
    """Un solo lector de fechas para el día de carga, _fecha_planilla (CICLO-cola-cuatro-items.md): entiende la hora, el
    número de serie de Excel y los textos AAAA-MM-DD y DD-MM-AAAA; cada naviera le da su formato."""
    CASOS = [("2026-10-05", "05 Oct 2026", "05/10/2026"), ("05-10-26", "05 Oct 2026", "05/10/2026"),
             ("5/1/2027", "05 Jan 2027", "05/01/2027"), ("05-10-2026", "05 Oct 2026", "05/10/2026"),
             ("2026/1/5", "05 Jan 2026", "05/01/2026"), ("", "", ""), ("abc", "", ""),
             # Hasta ecbdfaa, CMA no validaba el mes y «2026-13-01» pasaba como «01/13/2026».
             ("2026-13-01", "", ""), ("31-02-2026", "", ""),
             # Con hora: la fecha que da el lector de consola, y las que se escriben a mano.
             ("2026-10-05 00:00:00", "05 Oct 2026", "05/10/2026"), ("2026-10-05T08:30", "05 Oct 2026", "05/10/2026"),
             ("05-10-2026 8:30", "05 Oct 2026", "05/10/2026"), ("5.10.2026", "05 Oct 2026", "05/10/2026"),
             # Como la entrega Excel: el número de serie (con decimales si trae hora), datetime y date.
             ("46300", "05 Oct 2026", "05/10/2026"), (46300.25, "05 Oct 2026", "05/10/2026"),
             (datetime.datetime(2026, 10, 5, 8, 30), "05 Oct 2026", "05/10/2026"),
             (datetime.date(2026, 10, 5), "05 Oct 2026", "05/10/2026")]

    def test_fecha_maersk(self):
        for v, mk, _ in self.CASOS:
            with self.subTest(v=v):
                self.assertEqual(self.mod._mk_fecha_txt(v), mk)

    def test_fecha_cma(self):
        for v, _, cma in self.CASOS:
            with self.subTest(v=v):
                self.assertEqual(self.mod._cma_fecha_txt(v), cma)

    def test_ilegible_solo_si_trae_algo(self):
        f = self.mod._fecha_ilegible
        self.assertEqual([f(v) for v in ("", None, "   ", "2026-10-05", "46300", datetime.date(2026, 10, 5))],
                         [False] * 6)
        self.assertEqual([f(v) for v in ("pronto", "31-02-2026", "2026-13-01", "08:30:00", True)], [True] * 5)

    def corrida(self, nombre):
        vistas = []
        reg = self.mod.Registro(self.sb / nombre / "log.txt", on_log=vistas.append)
        self.addCleanup(reg.cerrar)
        return reg, vistas, self.sb / nombre / "log.txt"

    def test_aviso_de_fecha_ilegible(self):
        reg, vistas, log = self.corrida("fechas_aviso")
        for v in ("", None, "2026-10-05", "46300"):
            self.mod._avisar_dia_carga({"fila": 30, "dia_carga": v}, reg)
        self.assertEqual(vistas, [])                                   # con fecha, o sin nada, no avisa
        self.mod._avisar_dia_carga({"fila": 30, "dia_carga": " por   confirmar "}, reg)
        aviso = ("· ⚠ El día de carga de la fila 30 («por confirmar») no se entiende como fecha: sigo como si la fila no lo "
                 "trajera. Escríbelo como fecha de Excel o como DD-MM-AAAA.")
        for donde in (log.read_text(encoding="utf-8"), "\n".join(vistas)):     # log.txt y pantalla
            self.assertIn(aviso, donde)

    def test_cada_naviera_que_usa_la_fecha_avisa_y_la_lee_con_el_mismo_lector(self):
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}

        def llaman(nombre):
            return sorted({f for f, n in funcs.items() for c in ast.walk(n)
                           if isinstance(c, ast.Call) and getattr(c.func, "id", "") == nombre})
        # ONE se sumó en el encargo 26 (CICLO-cola-siete-items.md): hasta fc7de54 no leía el día de carga.
        self.assertEqual(llaman("_avisar_dia_carga"), ["reservar_cma", "reservar_cosco", "reservar_hyundai",
                                                       "reservar_maersk", "reservar_msc", "reservar_one"])
        # COSCO lo leía por _cosco_fecha_fila hasta 71eff24, y MSC por _msc_fecha_futura hasta 384d3ce; ahora, los dos
        # por _desde (CICLO-proxima-salida.md).
        lectores = ["_cma_fecha_txt", "_desde", "_hmm_fecha", "_mk_fecha_txt"]
        self.assertEqual(llaman("_fecha_planilla"), sorted(lectores + ["_fecha_ilegible"]))
        # Ninguno trae su propio lector: hasta ecbdfaa eran cinco, y ninguno entendía la hora ni el número de serie.
        src = Path(self.mod.__file__).read_text(encoding="utf-8")
        for nombre in lectores:
            texto = ast.get_source_segment(src, funcs[nombre])
            self.assertNotIn("strptime", texto, nombre)
            self.assertNotIn(".match(", texto, nombre)

    def test_maersk_avisa_cuando_no_busca_desde_hoy(self):
        # Decisión de Marcelo (CICLO-cola-siete-items.md): MAERSK busca desde hoy; como sin el portal no se sabe si acepta
        # la fecha de hoy (FRENO), sin día de carga sigue desde mañana y lo avisa. Hasta 50e3f04 no avisaba (desde
        # 16d3583), y antes avisaba «la fila no trae un día de carga que se entienda».
        class Campo:
            def __init__(self, pagina):
                self.pagina = pagina
            first = property(lambda s: s)

            def scroll_into_view_if_needed(self, **k):
                pass

            def click(self, **k):
                if self.pagina.escribir_falla:
                    raise RuntimeError("no acepta escritura")

            def type(self, v, **k):
                self.pagina.hechos.append(("escribe", v))

        class Manana(Campo):
            def click(self, **k):
                self.pagina.hechos.append(("clic", "Select tomorrow"))

        class Pagina(soporte.PaginaFalsa):
            def __init__(self, escribir_falla=False):
                super().__init__()
                self.escribir_falla, self.hechos = escribir_falla, []
                self.keyboard = types.SimpleNamespace(press=lambda k: self.hechos.append(("tecla", k)))

            def get_by_placeholder(self, texto):
                return Campo(self)

            def get_by_text(self, texto, exact=False):
                assert texto == "Select tomorrow"
                return Manana(self)

        manana = ("· ⚠ MAERSK: busco las salidas desde mañana, no desde hoy: todavía no sé si el portal acepta la fecha de "
                  "hoy.")
        casos = (("2026-10-05", False, "05 Oct 2026", [("escribe", "05 Oct 2026"), ("tecla", "Escape")], None),
                 ("", False, "mañana", [("clic", "Select tomorrow")], manana),
                 ("por confirmar", False, "mañana", [("clic", "Select tomorrow")], manana),
                 ("2026-10-05", True, "mañana", [("clic", "Select tomorrow")],
                  "· ⚠ MAERSK: no pude escribir el día de carga (05 Oct 2026), así que busco las salidas desde mañana."))
        for n, (dia, falla, puesta, hechos, aviso) in enumerate(casos):
            with self.subTest(dia=dia, escribir_falla=falla):
                reg, vistas, log = self.corrida(f"fechas_maersk_{n}")
                pagina, det = Pagina(falla), []
                self.assertEqual(self.mod._mk_fecha(pagina, {"dia_carga": dia}, reg, det), puesta)
                self.assertEqual((pagina.hechos, det), (hechos, [f"fecha={puesta}"]))
                for donde in (log.read_text(encoding="utf-8"), "\n".join(vistas)):
                    if aviso:
                        self.assertIn(aviso, donde)
                    else:
                        self.assertNotIn("⚠", donde)


class TestMAERSK(soporte.CasoAQ):
    def test_cliente_maersk(self):
        f = self.mod._mk_cliente
        self.assertEqual(f({"cliente": "CLIENTE FALSO"}, {"cliente": "OTRO"}), "CLIENTE FALSO")
        self.assertEqual(f({}, {"cliente": "OTRO"}), "OTRO")
        self.assertEqual(h(f({}, {})), "21348b96176a17c8")

    def test_fecha_salida_maersk(self):
        # «Departure» de cada salida en «Select sailing», medida en la corrida del 2026-09-25 (CICLO-proxima-salida.md).
        f = self.mod._mk_fecha_salida
        casos = (("27 Sep 2026, 18:00", datetime.date(2026, 9, 27)), ("4 Oct 2026, 06:00", datetime.date(2026, 10, 4)),
                 (" 1 JAN 2027 ", datetime.date(2027, 1, 1)), ("31 Feb 2026, 18:00", None), ("Sep 27 2026", None),
                 ("27 Set 2026, 18:00", None), ("", None), (None, None))
        for texto, esperado in casos:
            with self.subTest(texto=texto):
                self.assertEqual(f(texto), esperado)

    def test_la_forma_de_la_regla_de_origen_y_destino(self):
        # La regla de Marcelo para el origen y el destino de MAERSK (encargo 43): la parte de la sugerencia antes de
        # su primera coma, sin lo que va entre paréntesis (lo de afuera de _mk_partes; hasta el encargo 74, _mk_base),
        # es lo escrito, los dos sin tildes, en mayúsculas y con los espacios de a uno (_mk_plano). Los signos
        # cuentan, y un paréntesis sin cerrar queda.
        casos = (("Puerto Alfa, Pais", "PUERTO ALFA"), ("Puerto Alfa (Norte), Pais", "PUERTO ALFA"),
                 ("(Norte) Puerto Alfa, Pais", "PUERTO ALFA"), ("Puerto Alfa (Norte (Alto)), Pais", "PUERTO ALFA"),
                 ("Puerto  Álfa , País", "PUERTO ALFA"), ("Puerto Alfa", "PUERTO ALFA"),
                 ("Puerto Alfa Norte, Pais", "PUERTO ALFA NORTE"), ("Puerto-Alfa, Pais", "PUERTO-ALFA"),
                 ("Puerto Alfa (Norte, Pais", "PUERTO ALFA (NORTE"), ("Ñandú, Pais", "NANDU"), ("", ""),
                 (None, ""))
        for texto, base in casos:
            with self.subTest(sugerencia=texto):
                self.assertEqual(self.mod._mk_partes(texto)[0], base)
        for texto, plano in (("  puerto   ñandú ", "PUERTO NANDU"), ("PUERTO ALFA (NORTE)", "PUERTO ALFA (NORTE)"),
                             ("PUERTO ALFA, PAIS", "PUERTO ALFA, PAIS"), ("", ""), (None, "")):
            with self.subTest(escrito=texto):
                self.assertEqual(self.mod._mk_plano(texto), plano)

    def test_la_regla_del_parentesis_por_lista(self):
        # Decisión de Marcelo (encargo 75, la opción (a) del 74, CICLO-maersk-parentesis-por-lista.md): con la celda con
        # paréntesis decide la lista entera (_mk_ganadoras), no cada par. Primero, las del mismo paréntesis, lo de
        # adentro en _mk_plano (sin tildes, en mayúsculas y con los espacios de a uno); si no hay ninguna, las que no lo
        # traen, solo si ninguna otra con lo mismo afuera trae otro; si no, ninguna. Con la celda sin paréntesis, todas
        # las que dicen lo mismo afuera (encargo 43). _mk_ciudad elige solo si gana una. Hasta el 75 (_mk_calza, del
        # 74), par por par: con «Alfa (Norte)», «Alfa (Sur)» y «Alfa» ganaba «Alfa», y con «Alfa» y «Alfa (Norte)», las
        # dos. Esta prueba, hasta el 75, test_el_parentesis_cuenta_si_lo_traen_los_dos.
        partes = (("Alfa (Beta), Gama", ("ALFA", ("BETA",))), ("Alfa", ("ALFA", ())),
                  ("Alfa (Norte (Viejo)), Pais", ("ALFA", ("VIEJO", "NORTE"))),
                  ("(Norte) Alfa (Sur), Pais", ("ALFA", ("NORTE", "SUR"))), ("Alfa (Norte", ("ALFA (NORTE", ())),
                  ("Alfa ( región  uno ), Pais", ("ALFA", ("REGION UNO",))), ("", ("", ())), (None, ("", ())))
        for texto, esperado in partes:
            with self.subTest(texto=texto):
                self.assertEqual(self.mod._mk_partes(texto), esperado)
        A, N, S = "Alfa, Pais", "Alfa (Norte), Pais", "Alfa (Sur), Pais"
        listas = (("Alfa (Norte)", [N], [0]),
                  ("Alfa (Nórte)", ["ALFA ( norte ), PAIS"], [0]),            # el mismo, en _mk_plano
                  ("Alfa (Norte)", [S], []),                                 # otro paréntesis (encargo 74)
                  ("Alfa (Norte)", ["Alfa (Norte) (Puerto), Pais"], []),     # todo lo que va entre paréntesis
                  ("Alfa (Norte)", [A], [0]),                                # la que no lo trae, sola (encargo 73)
                  ("Alfa (Norte)", [S, A], []),                              # otra con ese nombre trae otro
                  ("Alfa (Norte)", [A, N], [1]),                             # gana la del mismo
                  ("Alfa (Norte)", [S, A, N], [2]),
                  ("Alfa (Norte)", [A, "Beta (Sur), Pais"], [0]),            # otro nombre con paréntesis no cuenta
                  ("Alfa (Norte)", ["Beta (Norte), Pais"], []),              # el mismo paréntesis, otro nombre
                  ("Alfa (Norte)", ["Beta, Pais"], []),                      # sin paréntesis, otro nombre
                  ("Alfa (Norte)", [A, "Beta, Pais"], [0]),
                  ("Alfa (Norte)", [N, "Alfa (Norte), Otro Pais"], [0, 1]),  # dos del mismo: ganan las dos
                  ("Alfa (Norte)", [A, "Alfa, Otro Pais"], [0, 1]),
                  ("Alfa", [N], [0]),                                        # celda sin paréntesis (encargo 43)
                  ("Alfa", [N, S], [0, 1]),
                  ("Alfa", [A, N], [0, 1]))
        for escrito, lista, ganan in listas:
            with self.subTest(escrito=escrito, lista=lista):
                self.assertEqual(self.mod._mk_ganadoras(lista, self.mod._mk_partes(escrito)), ganan)

    def test_la_regla_por_lista_en_todas_las_listas_chicas(self):
        # Revisión de código del encargo 75: las pruebas por casos dejaron pasar dos huecos seguidos (en el 74, la sin
        # paréntesis que ganaba por descarte; en el 75, la sin paréntesis con otro nombre). Esta recorre todas las
        # listas de 0 a 3 sugerencias de «Alfa», «Beta» y «Alfa Beta», sin paréntesis, con «Norte» y con «Sur»
        # («Alfa Beta», solo sin paréntesis y con «Norte»), contra las celdas «Alfa», «Alfa (Norte)» y «Alfa (Sur)»
        # (1.755 casos), y exige lo que la regla promete (_mk_ganadoras), sin repetir cómo lo calcula: la elegida dice
        # lo mismo afuera que la celda; con la celda con paréntesis, no trae otro, y si no trae ninguno, ninguna otra
        # con ese nombre trae otro; si hay una sola con el mismo paréntesis, gana esa; y con la celda sin paréntesis,
        # se elige si y solo si hay una sola con lo mismo afuera (encargo 43). «Alfa Beta», que empieza como «Alfa»,
        # la sumó la revisión de seguridad del 75: con solo «Alfa» y «Beta», «lo mismo afuera» y «empieza igual» daban
        # lo mismo, y la prueba no veía la diferencia que arregló el encargo 43.
        partes = self.mod._mk_partes
        textos = ("Alfa, Pais", "Alfa (Norte), Pais", "Alfa (Sur), Pais", "Beta, Pais", "Beta (Norte), Pais",
                  "Beta (Sur), Pais", "Alfa Beta, Pais", "Alfa Beta (Norte), Pais")
        casos = elegidas = ninguna = 0
        for celda in ("Alfa", "Alfa (Norte)", "Alfa (Sur)"):
            afuera, parentesis = partes(celda)
            for largo in range(4):
                for lista in itertools.product(textos, repeat=largo):
                    casos += 1
                    ganan = self.mod._mk_ganadoras(list(lista), partes(celda))
                    del_nombre = [partes(t) for t in lista if partes(t)[0] == afuera]
                    mismas = [t for t in lista if partes(t) == (afuera, parentesis)]
                    with self.subTest(celda=celda, lista=lista):
                        if parentesis and len(mismas) == 1:
                            self.assertEqual([lista[i] for i in ganan], mismas)
                        if not parentesis:
                            self.assertEqual(len(ganan) == 1, len(del_nombre) == 1)
                        if len(ganan) != 1:
                            ninguna += 1
                            continue
                        elegidas += 1
                        a, p = partes(lista[ganan[0]])
                        self.assertEqual(a, afuera)
                        if parentesis:
                            self.assertIn(p, ((), parentesis))
                            if not p:
                                self.assertFalse(any(q for _, q in del_nombre))
        # El control: la enumeración no es vacua, y hay de las dos.
        self.assertEqual((casos, elegidas > 100, ninguna > 100), (1755, True, True))


class TestCOSCO(soporte.CasoAQ):
    def test_resumen_cosco(self):
        f = self.mod._cosco_resumen
        self.assertEqual(f({"servicios": ["SVC1", "", "SVC2"], "naves": ["NAVE A"], "etd": "2026-10-01"}),
                         "servicio SVC1 + SVC2 · nave NAVE A · ETD 2026-10-01")
        self.assertEqual(f({"texto": "  uno   dos  "}), "uno dos")
        self.assertEqual(len(f("  a   b " * 30)), 90)
        self.assertEqual(f(None), "")

    def test_normalizar_control(self):
        f = self.mod._norm_ctrl
        self.assertEqual(f("Puerto Montt, Chile"), "PUERTO MONTT CHILE")
        self.assertEqual(f("Añejo-Ñandú (sur)"), "ANEJO NANDU SUR")
        self.assertEqual(f(None), "")

    @staticmethod
    def _puzzle(x_hueco=170, x_pieza=10, y=40, lado=50, ancho=320, alto=160):
        """Fondo con textura y el hueco oscurecido; la pieza en una capa con alfa."""
        rng = np.random.RandomState(7)
        fondo = rng.randint(0, 255, (alto, ancho, 3), dtype=np.uint8)
        pieza = fondo[y:y + lado, x_hueco:x_hueco + lado].copy()
        fondo[y:y + lado, x_hueco:x_hueco + lado] = (fondo[y:y + lado, x_hueco:x_hueco + lado] * 0.5).astype(np.uint8)
        bloque = np.zeros((alto, ancho, 4), dtype=np.uint8)
        bloque[y:y + lado, x_pieza:x_pieza + lado, :3] = pieza
        bloque[y:y + lado, x_pieza:x_pieza + lado, 3] = 255
        return cv2.imencode(".png", fondo)[1].tobytes(), cv2.imencode(".png", bloque)[1].tobytes()

    def test_puzzle_cosco_encuentra_el_hueco(self):
        fondo, bloque = self._puzzle()
        self.assertEqual(tuple(int(v) for v in self.mod._calcular_offset_cosco(fondo, bloque)), (170, 10, 320))
        fondo, bloque = self._puzzle(x_hueco=233, x_pieza=4)
        self.assertEqual(tuple(int(v) for v in self.mod._calcular_offset_cosco(fondo, bloque)), (233, 4, 320))

    def test_puzzle_cosco_sin_pieza(self):
        fondo, _ = self._puzzle()
        vacio = cv2.imencode(".png", np.zeros((160, 320, 4), dtype=np.uint8))[1].tobytes()
        self.assertEqual(tuple(int(v) for v in self.mod._calcular_offset_cosco(fondo, vacio)), (150, 0, 320))

    def test_fecha_de_la_tarjeta_sin_anio(self):
        # La salida y la llegada de la tarjeta de itinerario, medidas en la corrida del 2026-09-25: «Sep27 (Sun)», sin
        # año. Vale el año, cercano a hoy, cuyo día de la semana calce (CICLO-proxima-salida.md).
        f = self.mod._cosco_fecha_tarjeta
        hoy = datetime.date(2026, 9, 25)
        casos = (("Sep27 (Sun)", datetime.date(2026, 9, 27)),
                 (" Nov01 (Sun) ", datetime.date(2026, 11, 1)),
                 ("Jan03 (Sun)", datetime.date(2027, 1, 3)),       # el año siguiente: el único con domingo
                 ("Sep20 (Sun)", datetime.date(2026, 9, 20)),
                 ("sep27 (sun)", datetime.date(2026, 9, 27)),
                 ("Sep27 (Tue)", None),                             # ningún año cercano lo trae en martes
                 ("Feb29 (Sun)", None), ("Sep27", None), ("2026-09-27", None), ("", None), (None, None))
        for texto, esperado in casos:
            with self.subTest(texto=texto):
                self.assertEqual(f(texto, hoy), esperado)

    def test_cada_itinerario_con_su_salida(self):
        filas = [{"i": 0, "salida": "Sep27 (Sun)", "corte": "2026-09-26"}, {"i": 1, "salida": "", "corte": "2026-10-03"},
                 {"i": 2, "salida": "Sep27 (Tue)", "corte": "2026-09-26"}]
        r = self.mod._cosco_con_salida(filas, datetime.date(2026, 9, 25))
        self.assertEqual([x["etd"] for x in r], ["2026-09-27", "", ""])
        self.assertEqual([x["corte"] for x in r], ["2026-09-26", "2026-10-03", "2026-09-26"])
        self.assertEqual([x.get("etd") for x in filas], [None, None, None])      # la lista leída no se toca

    def test_sesion_activa_por_el_nombre_de_config(self):
        # El nombre con que COSCO muestra al operador sale de config.json («nombre_en_pantalla»): hasta 9710ae2 estaba
        # escrito en el código (CICLO-cola-cuatro-items.md). El tablero y el acceso se deciden sin leer la página.
        pagina = "https://portal.test/ebusiness/booking/create"
        casos = [
            ("https://portal.test/ebusiness/dashboard", "", "operador prueba", True),
            ("https://login.test/b2clogin/authorize", "Operador Prueba · Logout", "operador prueba", False),
            (pagina, "Hola, OPERADOR PRUEBA · Logout", " Operador Prueba ", True),
            (pagina, "Hola, Operador Prueba", "operador prueba", False),              # sin logout ni message center
            (pagina, "Hola, Otra Persona · Message Center", "operador prueba", False),
            (pagina, "AquaChile · Logout", "", True),                                 # sin nombre, vale la empresa
            (pagina, "Hola, Operador Prueba · Logout", "", False),                    # sin nombre en config.json
        ]
        lecturas = []
        for url, texto, nombre, esperado in casos:
            def leer(texto=texto):
                lecturas.append(texto)
                return texto
            self.assertIs(self.mod._cosco_sesion_activa(url, leer, nombre), esperado, (url, texto, nombre))
        self.assertEqual(len(lecturas), 5)

    def test_login_cosco_lee_el_nombre_de_config(self):
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        login = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "login_cosco")
        llamadas = [c for c in ast.walk(login)
                    if isinstance(c, ast.Call) and getattr(c.func, "id", "") == "_cosco_sesion_activa"]
        self.assertEqual(len(llamadas), 1)
        self.assertEqual(ast.unparse(llamadas[0].args[2]), "creds.get('nombre_en_pantalla', '')")


class TestProximaSalida(soporte.CasoAQ):
    """La regla de la próxima salida, decidida por Marcelo (CICLO-proxima-salida.md): la fuente única de las navieras
    que eligen entre varias salidas de la nave de la fila."""
    HOY = datetime.date(2026, 9, 25)

    def d(self, n):
        return self.HOY + datetime.timedelta(days=n)

    def test_la_proxima_desde_la_fecha(self):
        f = self.mod._proxima_salida
        casos = (([], (None, "ninguna")),
                 ([(None, "a")], ("a", "")),                               # una sola sin fecha: nada con qué comparar
                 ([(self.d(4), "a")], ("a", "")),
                 ([(self.d(-1), "a")], (None, "ninguna")),                 # ya salió
                 ([(self.d(9), "a"), (self.d(2), "b")], ("b", "")),        # la próxima, no la primera de la lista
                 ([(self.d(-3), "a"), (self.d(5), "b")], ("b", "")),       # las que ya salieron no cuentan
                 ([(self.d(0), "a"), (self.d(5), "b")], ("a", "")),        # hoy cuenta
                 ([(self.d(2), "a"), (self.d(2), "b"), (self.d(9), "c")], (None, "empate")),
                 ([(self.d(-2), "a"), (self.d(-2), "b"), (self.d(9), "c")], ("c", "")),
                 ([(self.d(2), "a"), (None, "b")], (None, "sin-fecha")))
        for salidas, esperado in casos:
            with self.subTest(salidas=salidas):
                self.assertEqual(f(salidas, self.HOY), esperado)

    def test_desde_hoy_o_el_dia_de_carga_posterior(self):
        hoy = datetime.date.today()
        mas = lambda n: hoy + datetime.timedelta(days=n)
        f = self.mod._desde
        self.assertEqual((f({}), f(None)), (hoy, hoy))
        self.assertEqual(f({"dia_carga": mas(10).isoformat()}), mas(10))
        self.assertEqual(f({"dia_carga": mas(10).strftime("%d-%m-%Y")}), mas(10))
        self.assertEqual(f({"dia_carga": "2020-01-01"}), hoy)             # pasado: desde hoy
        self.assertEqual(f({"dia_carga": "por confirmar"}), hoy)          # ilegible: desde hoy

    def test_el_motivo_en_palabras(self):
        f = self.mod._por_que_sin_salida
        self.assertEqual(f("empate", [(self.d(2), "a"), (self.d(2), "b"), (self.d(9), "c")], self.HOY),
                         "2 de las 3 opciones salen el 27-09-2026, la próxima salida desde el 25-09-2026")
        self.assertEqual(f("sin-fecha", [(self.d(2), "a"), (None, "b"), (None, "c")], self.HOY),
                         "no pude leer la fecha de salida de 2 de las 3 opciones")
        self.assertEqual(f("ninguna", [(self.d(-2), "a"), (self.d(-9), "b")], self.HOY),
                         "las 2 opciones salen antes del 25-09-2026")
        self.assertEqual(f("ninguna", [(self.d(-2), "a")], self.HOY), "la única opción sale antes del 25-09-2026")
        self.assertEqual(f("ninguna", [], self.HOY), "no hay opciones")
        # La fila trae un viaje que ninguna salida de la nave trae (MAERSK y COSCO, CICLO-cierre-de-frenos.md): da lo mismo
        # cuándo salen.
        self.assertEqual(f("sin-viaje", [(self.d(2), "a"), (None, "b"), (self.d(-9), "c")], self.HOY),
                         "ninguna de las 3 opciones de la nave trae el viaje de la fila")
        self.assertEqual(f("sin-viaje", [(self.d(2), "a")], self.HOY), "la única opción de la nave no trae el viaje de la fila")
        self.assertEqual(f("sin-viaje", [(self.d(2), "a"), (self.d(2), "b")], self.HOY, lambda o: None),
                         "ninguna de las 2 opciones de la nave trae el viaje de la fila")
        # La salida pedida está, pero el portal ya no deja reservarla (MAERSK, CICLO-ampliar-la-busqueda.md).
        self.assertEqual(f("no-reservable", [(self.d(2), "a")], self.HOY), "la salida pedida ya no se puede reservar")
        self.assertEqual(f("no-reservable", [(self.d(2), "a"), (self.d(9), "b")], self.HOY, lambda o: None),
                         "la salida pedida ya no se puede reservar")

    def test_hasta_donde_busque(self):
        # Hasta qué fecha buscó la naviera que no encontró la nave: la última salida que mostró el portal, y por qué dejó
        # de ampliar (decisión de Marcelo, CICLO-ampliar-la-busqueda.md).
        f = self.mod._hasta_donde_busque
        self.assertEqual(f([self.d(2), None, self.d(30), self.d(9)], "el portal no deja ampliar más la búsqueda"),
                         "busqué hasta el 25-10-2026, la última salida que mostró el portal, y el portal no deja "
                         "ampliar más la búsqueda")
        for fechas in ([], [None]):
            with self.subTest(fechas=fechas):
                self.assertEqual(f(fechas, "X"), "el portal no mostró ninguna salida con fecha, y X")
        self.assertEqual(self.mod.NO_AMPLIA_MAS, "el portal no deja ampliar más la búsqueda")

    # --- El desempate por el menor tiempo de tránsito (decisión de Marcelo, CICLO-cola-tres-items.md) ---
    DIAS = staticmethod(lambda n, h=0: datetime.timedelta(days=n, hours=h))

    def test_desempate_por_el_menor_tiempo_de_transito(self):
        # Entre las del mismo día, la de menor tiempo de tránsito; si alguna no lo trae legible o el menor se repite,
        # ninguna. Los transbordos no cuentan. Hasta 2825153, todo empate quedaba NO ENVIADA.
        f = self.mod._proxima_salida
        tt = {"a": self.DIAS(40), "b": self.DIAS(38), "c": self.DIAS(10), "d": self.DIAS(38), "e": None,
              "f": self.DIAS(44, 6), "g": self.DIAS(44), "z": self.DIAS(0), "n": self.DIAS(-1)}.get
        casos = (([(self.d(2), "a"), (self.d(2), "b"), (self.d(9), "c")], ("b", "")),     # «c» tarda menos, pero sale después
                 ([(self.d(2), "a"), (self.d(2), "b"), (self.d(2), "d")], (None, "empate")),    # el menor se repite
                 ([(self.d(2), "a"), (self.d(2), "e")], (None, "empate")),                 # una sin tránsito legible
                 ([(self.d(2), "f"), (self.d(2), "g")], ("g", "")),                        # las horas cuentan
                 ([(self.d(2), "e"), (self.d(5), "a")], ("e", "")),                        # sola ese día, aunque no lo traiga
                 ([(self.d(2), "a"), (self.d(2), "z")], (None, "empate")),                 # un tránsito de cero no sirve
                 ([(self.d(2), "a"), (self.d(2), "n")], (None, "empate")),                 # ni uno negativo
                 ([(self.d(2), "a"), (None, "b")], (None, "sin-fecha")))
        for salidas, esperado in casos:
            with self.subTest(salidas=salidas):
                self.assertEqual(f(salidas, self.HOY, tt), esperado)
        # Sin tránsito, como hasta ahora: el empate queda empate.
        self.assertEqual(f([(self.d(2), "a"), (self.d(2), "b")], self.HOY), (None, "empate"))

    def test_el_motivo_con_el_tiempo_de_transito(self):
        f = self.mod._por_que_sin_salida
        tt = {"a": self.DIAS(40), "b": self.DIAS(40), "c": self.DIAS(10), "e": None, "f": self.DIAS(44, 6),
              "g": self.DIAS(44, 6), "z": self.DIAS(0)}.get
        base = "2 de las 3 opciones salen el 27-09-2026, la próxima salida desde el 25-09-2026"
        self.assertEqual(f("empate", [(self.d(2), "a"), (self.d(2), "b"), (self.d(9), "c")], self.HOY, tt),
                         base + ", y 2 de ellas tienen el menor tiempo de tránsito, 40 días")
        self.assertEqual(f("empate", [(self.d(2), "a"), (self.d(2), "e"), (self.d(9), "c")], self.HOY, tt),
                         base + ", y no pude leer el tiempo de tránsito de 1 de ellas")
        self.assertEqual(f("empate", [(self.d(2), "f"), (self.d(2), "g"), (self.d(9), "c")], self.HOY, tt),
                         base + ", y 2 de ellas tienen el menor tiempo de tránsito, 44 días y 6 horas")
        self.assertEqual(self.mod._texto_transito(self.DIAS(1, 1)), "1 día y 1 hora")
        # Una salida que ya pasó no cuenta en el día del empate, aunque tarde menos.
        self.assertEqual(f("empate", [(self.d(-1), "c"), (self.d(2), "a"), (self.d(2), "b")], self.HOY, tt),
                         "2 de las 3 opciones salen el 27-09-2026, la próxima salida desde el 25-09-2026, y 2 de ellas tienen "
                         "el menor tiempo de tránsito, 40 días")
        # Un tránsito de cero no se puede usar: cuenta como no leído.
        self.assertEqual(f("empate", [(self.d(2), "a"), (self.d(2), "z")], self.HOY, tt),
                         "2 de las 2 opciones salen el 27-09-2026, la próxima salida desde el 25-09-2026, y no pude leer el "
                         "tiempo de tránsito de 1 de ellas")
        # Sin tránsito, o con otro motivo, el texto de siempre.
        self.assertEqual(f("empate", [(self.d(2), "a"), (self.d(2), "b"), (self.d(9), "c")], self.HOY), base)
        self.assertEqual(f("sin-fecha", [(self.d(2), "a"), (None, "b")], self.HOY, tt),
                         "no pude leer la fecha de salida de 1 de las 2 opciones")


    def test_anota_el_desempate(self):
        # Cuando el tránsito desempató, el log dice cuántas salían ese día y con qué tiempos (CICLO-cola-tres-items.md).
        vistas = []
        reg = types.SimpleNamespace(info=vistas.append)
        tt = {"a": self.DIAS(48), "b": self.DIAS(40), "c": self.DIAS(10), "d": self.DIAS(44, 6), "e": None}.get
        f = self.mod._anotar_desempate
        f(reg, [(self.d(2), "a"), (self.d(2), "b"), (self.d(2), "d"), (self.d(9), "c")], self.HOY, tt)
        self.assertEqual(vistas, ["3 salidas de la nave salen el 27-09-2026: elijo la de menor tiempo de tránsito, 40 días "
                                  "(las otras: 44 días y 6 horas, 48 días)"])
        # Sola ese día, sin tránsito legible, o sin salidas: nada que anotar.
        for salidas in ([(self.d(2), "a"), (self.d(9), "b")], [(self.d(2), "a"), (self.d(2), "e")], [], [(None, "a")],
                        [(self.d(-3), "a"), (self.d(-3), "b")]):
            with self.subTest(salidas=salidas):
                vistas.clear()
                f(reg, salidas, self.HOY, tt)
                self.assertEqual(vistas, [])

    def test_cada_naviera_anota_el_desempate(self):
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        llamadas = sorted((n.name, ast.unparse(c)) for n in tree.body if isinstance(n, ast.FunctionDef)
                          for c in ast.walk(n) if isinstance(c, ast.Call) and getattr(c.func, "id", "") == "_anotar_desempate")
        self.assertEqual(llamadas, [
            ("_hmm_elegir_nave", "_anotar_desempate(reg, _hmm_salidas(disponibles), desde, _hmm_transito)"),
            ("_mk_elegir_nave", "_anotar_desempate(reg, _mk_salidas(cand), desde, _mk_transito)"),
            ("reservar_cosco", "_anotar_desempate(reg, _cosco_salidas(cand), _desde(reserva), _cosco_transito)"),
            ("reservar_msc", "_anotar_desempate(reg, _msc_salidas(exacta), desde, _msc_transito)"),
            ("reservar_one", "_anotar_desempate(reg, _one_salidas(tarjetas), desde, _one_transito)")])


class Marco:
    def __init__(self, url="", titulo="", texto=""):
        self.url, self._t, self._x = url, titulo, texto

    def locator(self, sel):
        return soporte.RaizFalsa(self)          # el programa lee el marco con plazo (encargo 55)

    def title(self):
        return self._t

    def evaluate(self, js, *a):
        return self._x


class TestNaveCompleta(soporte.CasoAQ):
    """Una tarjeta calza con la nave solo si trae todas sus palabras (decisión de Marcelo, CICLO-cola-tres-items.md), cada
    una como palabra entera (CICLO-cola-seis-items.md)."""
    # (texto de la tarjeta, palabras de la fila, calza): los casos de la regla, para Python y para su JavaScript.
    CASOS = (("MSC NAVE UNO 001E", ["MSC", "NAVE", "UNO"], True),
             ("msc nave uno", ["MSC", "NAVE", "UNO"], True),          # sin distinguir mayúsculas
             ("MSC NAVE DOS 001E", ["MSC", "NAVE", "UNO"], False),    # le falta una
             ("NAVE UNO 001E", ["MSC", "NAVE", "UNO"], False),        # sin el prefijo tampoco
             # Cada palabra, entera: sin una letra o un número pegado antes ni después. Hasta f68ce6c bastaba que fuera
             # parte del texto, y calzaban estos cuatro y los dos marcados más abajo.
             ("SAVANNAH", ["ANNA"], False),
             ("SAVANNA", ["ANNA"], False),                           # pegada antes
             ("ANNAH", ["ANNA"], False),                             # pegada después
             ("MSC NAVE UNO FA001E", ["MSC", "NAVE", "UNO", "FA001"], False),
             ("SAVANNAH ANNA 001E", ["ANNA"], True),                 # la segunda vez sí va entera
             ("MSC ANNA/001E", ["ANNA", "001E"], True),              # un signo separa palabras
             ("NAVE (001E)", ["NAVE", "001E"], True),
             ("NAVE1 UNO", ["NAVE"], False),                         # un número pegado también (calzaba)
             ("EL ÑANDÚ 1", ["ÑANDÚ"], True),
             ("ÑANDÚ", ["ANDÚ"], False),                              # la Ñ y las tildes son letras (calzaba)
             ("MSC NAVE UNO", [], False),                             # sin palabras, ninguna
             ("", ["NAVE"], False))

    def test_trae_la_nave(self):
        f = self.mod._trae_la_nave
        for texto, palabras, calza in self.CASOS + ((None, ["NAVE"], False),):
            with self.subTest(texto=texto, palabras=palabras):
                self.assertIs(f(texto, palabras), calza)

    def test_la_misma_regla_en_javascript(self):
        # _JS_TRAE_LA_NAVE, que ONE, HYUNDAI, MAERSK y CMA llevan al principio de su JavaScript, da lo mismo que
        # _trae_la_nave en cada caso; y _palabraEn, con la que MAERSK exige el orden, lo mismo que _palabra_en.
        desde = (("NAVE UNO NAVE", "NAVE", 1, 9), ("SAVANNAH ANNA", "ANNA", 0, 9), ("ANNA", "ANNA", 1, -1),
                 ("XNAVE", "NAVE", 0, -1), ("A ", "", 0, -1))        # una palabra vacía no está en ninguna parte
        guion = ("const [trae, en] = (() => {" + self.mod._JS_TRAE_LA_NAVE + "return [_traeLaNave, _palabraEn]; })();\n"
                 "console.log(JSON.stringify([" + json.dumps([[t, p] for t, p, _ in self.CASOS]) + ".map(([t, p]) => trae(t, p)), "
                 + json.dumps([[t, p, d] for t, p, d, _ in desde]) + ".map(([t, p, d]) => en(t, p, d))]));\n")
        calces, posiciones = correr_node(self, guion)
        self.assertEqual(calces, [c for _, _, c in self.CASOS])
        self.assertEqual(posiciones, [x for _, _, _, x in desde])
        self.assertEqual([self.mod._palabra_en(t, p, d) for t, p, d, _ in desde], posiciones)
        # Las letras de la regla son las mismas con que _fila_sin_nave separa las palabras.
        clase = re.search(r"\[(0-9A-Z[^\]]*)\]", inspect.getsource(self.mod._fila_sin_nave)).group(1)
        letras = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ" + clase.replace("0-9A-Z", "")
        self.assertEqual(sorted(self.mod._LETRAS_DE_NAVE), sorted(letras))

    def test_las_navieras_de_javascript_con_el_ayudante(self):
        # ONE, HYUNDAI, MAERSK y CMA llevan _JS_TRAE_LA_NAVE al principio de su función, armado con la constante (no una
        # copia), y calzan con él; MSC y COSCO, con _trae_la_nave (la prueba siguiente). Hasta f68ce6c cada JavaScript
        # comparaba con su propio «includes» o «indexOf», como parte del texto (CICLO-cola-seis-items.md).
        arbol = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        armado = {t.id: n.value for n in arbol.body if isinstance(n, ast.Assign) for t in n.targets
                  if isinstance(t, ast.Name)}
        for nombre, calces in (("_JS_ONE_TARJETAS_NAVE", ["_traeLaNave(suNave, palabras)"]),
                               ("_JS_HMM_INDICE_NAVE", ["_traeLaNave(v, T)"]),
                               ("_JS_HMM_TARJETAS", ["_traeLaNave(primera, T)"]),
                               ("_JS_MK_SALIDAS", ["_palabraEn(t, x, pos)"]),
                               # Desde el encargo 67, CMA, con la nave del primer tramo (primerTramo).
                               ("_JS_CMA_RUTAS", ["_traeLaNave(vessel.toUpperCase(), toks)"])):
            with self.subTest(js=nombre):
                js = getattr(self.mod, nombre)
                self.assertTrue(js.split("=>", 1)[1].lstrip().startswith("{" + self.mod._JS_TRAE_LA_NAVE))
                self.assertIn("_JS_TRAE_LA_NAVE", [x.id for x in ast.walk(armado[nombre]) if isinstance(x, ast.Name)])
                self.assertEqual([c for c in calces if js.count(c) == 1], calces)

    def test_msc_y_cosco_calzan_con_el_ayudante(self):
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}

        def asignas(nombre, variable):
            return [ast.unparse(n) for n in ast.walk(funcs[nombre]) if isinstance(n, ast.Assign)
                    and ast.unparse(n.targets[0]) == variable]
        # Hasta 9051f43, con all(...) directo: una fila sin palabras de nave calzaba con todas las tarjetas, y en COSCO
        # también por el viaje solo.
        # Desde el encargo 66, de esas, las que traen el viaje de la fila (_msc_es_la_pedida, test_clics.TestMsc).
        self.assertEqual(asignas("reservar_msc", "exacta"),
                         ["exacta = [n for n in naves if n.get('sel') and _trae_la_nave(_norm(n.get('nave')), toks)]",
                          "exacta = [n for n in exacta if _msc_es_la_pedida(n, toks, viaje)]"])
        self.assertEqual(asignas("reservar_cosco", "cand"), ["cand = _cosco_calzan(filas, toks_nave, toks_todos)"])
        # El aviso de «ese barco con otro viaje», con la misma regla que el calce: sus dos primeras palabras, cada una
        # entera, en cualquier lugar del campo. Hasta f68ce6c tenían que ir juntas y en ese orden, como parte del texto:
        # «MSC NAVE» no avisaba con «NAVE MSC 001E», y avisaba con «MSC NAVES 001E» (CICLO-cola-seis-items.md).
        self.assertEqual(asignas("reservar_msc", "parecidas"),
                         ["parecidas = [n['nave'] for n in naves if _trae_la_nave(_norm(n.get('nave')), toks[:2])]"])

    def test_cosco_calza_en_una_de_sus_naves(self):
        # Cada itinerario con sus naves de «Vessel / Voyage», como las lee _JS_COSCO_LISTA_NAVES: la nave y su viaje en un
        # solo texto, y dos cuando hay transbordo.
        a = {"i": 0, "naves": ["CSCL ALFA 001E", "COSCO SHIPPING BETA 002W"]}
        b = {"i": 1, "naves": ["COSCO SHIPPING GAMA 003E"]}
        c = {"i": 2, "naves": ["CSCL BETA 001E", "COSCO SHIPPING DELTA 004W"]}     # las palabras, repartidas en dos
        d = {"i": 3, "naves": ["COSCO SHIPPING BETA 009W"]}
        e = {"i": 4, "texto": "COSCO SHIPPING BETA 002W"}                           # sin naves leídas
        f = lambda nave, viaje: self.mod._cosco_calzan([a, b, c, d, e], nave, nave + viaje)
        nave = ["COSCO", "SHIPPING", "BETA"]
        self.assertEqual([x["i"] for x in f(nave, ["002W"])], [0])                  # la nave con su viaje
        self.assertEqual([x["i"] for x in f(nave, ["999W"])], [0, 3])               # otro viaje: la nave sola
        self.assertEqual([x["i"] for x in f(nave, [])], [0, 3])
        # Hasta 9051f43, con el texto de toda la fila, la 2 también calzaba («CSCL BETA» y «COSCO SHIPPING DELTA»); y sin
        # palabras de nave calzaban todas, o las del viaje solo.
        self.assertEqual(f([], ["002W"]), [])
        self.assertEqual(f([], []), [])
        # El viaje también va entero, porque pasa por el mismo ayudante: «002» no es el viaje «002W», y queda la nave con
        # cualquier viaje. Hasta f68ce6c, [0] (CICLO-cola-seis-items.md).
        self.assertEqual([x["i"] for x in f(nave, ["002"])], [0, 3])


class TestViajeDeLaFila(soporte.CasoAQ):
    """El viaje de la fila, con la regla de palabra entera de MAERSK y COSCO (_trae_el_viaje), la que desde el encargo 66
    usan también ONE, MSC, HYUNDAI y CMA-CGM para elegir su salida (decisión de Marcelo, CICLO-viaje-y-origen.md)."""
    # (lo que la salida muestra de su nave, el viaje de la fila, lo trae). Viajes inventados.
    CASOS = (("ONE NAVE UNO ZZ101E", "ZZ101E", True),
             ("ONE NAVE UNO ZZ101E", "zz101e", True),                 # sin distinguir mayúsculas
             ("one nave uno zz101e", "ZZ101E", True),
             ("ONE NAVE UNO 1ZZ101E", "ZZ101E", False),               # parte de otra palabra: con algo antes
             ("ONE NAVE UNO ZZ101EA", "ZZ101E", False),               # o después
             ("ONE NAVE UNO ZZ101E", "ZZ101", False),
             ("HMM NAVE (0101W)", "0101W", True),                     # entre paréntesis, como en el «1st Vessel»
             ("MSC NAVE ZZ101A", "ZZ101A", True),
             ("Buque principal NAVE Ref. de viaje 0ZZ1ZZ1ZZ", "0ZZ1ZZ1ZZ", True),
             ("ONE NAVE UNO ZZ101E", "ZZ 101E", False),               # cada palabra, entera: «ZZ» no está sola
             ("ONE NAVE UNO ZZ 101E", "ZZ 101E", True),
             ("ONE NAVE UNO ZZ101E", "ZZ101E ZZ102E", False),         # todas sus palabras
             ("ONE NAVE UNO ZZ101E", "", True),                       # la fila sin viaje: no hay viaje que comparar
             ("ONE NAVE UNO ZZ101E", None, True),
             ("ONE NAVE UNO ZZ101E", "   ", True),
             ("", "ZZ101E", False),
             (None, "ZZ101E", False))

    def test_trae_el_viaje(self):
        for texto, viaje, trae in self.CASOS:
            with self.subTest(texto=texto, viaje=viaje):
                self.assertIs(self.mod._trae_el_viaje(texto, viaje), trae)

    def test_las_palabras_del_viaje(self):
        # Como toma COSCO las del viaje: en mayúsculas, separadas por cualquier espacio en blanco y sin las de una letra,
        # como un «/» o un «-» suelto (revisión del encargo 67: hasta ahí las dejaba, y «ZZ101E / ZZ102E» pedía también
        # un «/» como palabra, que ninguna salida trae).
        f = self.mod._palabras_del_viaje
        self.assertEqual([f("zz101e"), f(" ZZ 101E "), f("ZZ\t101E"), f(""), f(None), f("  "), f(101)],
                         [["ZZ101E"], ["ZZ", "101E"], ["ZZ", "101E"], [], [], [], ["101"]])
        self.assertEqual([f("ZZ101E / ZZ102E"), f("ZZ101E -"), f("A"), f("- ZZ101E")],
                         [["ZZ101E", "ZZ102E"], ["ZZ101E"], [], ["ZZ101E"]])
        self.assertIs(self.mod._trae_el_viaje("ONE NAVE UNO ZZ101E", "ZZ101E -"), True)
        self.assertIs(self.mod._trae_el_viaje("ONE NAVE UNO ZZ101E", "ZZ101E / ZZ102E"), False)

    def test_la_misma_regla_en_javascript(self):
        # ONE, HYUNDAI y CMA-CGM la comparan en su JavaScript con _traeLaNave y las palabras que les pasa el programa
        # (_palabras_del_viaje): da lo mismo que _trae_el_viaje. La fila sin viaje no compara: su lista va vacía, y cada
        # JavaScript lo mira aparte (test_clics).
        f = self.mod._palabras_del_viaje
        casos = [(t, f(v)) for t, v, _ in self.CASOS if f(v)]
        guion = ("const trae = (() => {" + self.mod._JS_TRAE_LA_NAVE + "return _traeLaNave; })();\n"
                 "console.log(JSON.stringify(" + json.dumps(casos) + ".map(([t, v]) => trae(t, v))));\n")
        self.assertEqual(correr_node(self, guion), [self.mod._trae_el_viaje(t, " ".join(v)) for t, v in casos])


class PaginaQueNoSeToca:
    """Una página que falla con cualquier uso: el reservador no puede abrir el portal."""

    def __getattr__(self, nombre):
        raise AssertionError(f"el reservador tocó la página: {nombre}")


class TestFilaSinNave(soporte.CasoAQ):
    """Una fila que no pide una nave (vacía, con un comodín o con solo el prefijo de la naviera) queda NO ENVIADA sin abrir
    el portal (decisiones de Marcelo, CICLO-solo-la-nave-pedida.md y CICLO-cola-seis-items.md)."""
    MOTIVO = "la fila no trae una nave para reservar"

    def test_fila_sin_nave(self):
        f = self.mod._fila_sin_nave
        # Los comodines de CMA iban en la celda entera, y los de HYUNDAI eran palabras que su búsqueda quitaba, igual que
        # las de una letra; ahora son una sola lista. Las palabras se separan por cualquier signo, y las de una letra no
        # cuentan: ninguna naviera las busca.
        sin = ("", None, "   ", "-", "--", "—", "AUTO", "auto", "Cualquiera", "LIBRE", "N/A", "n/a", "NINGUNA", "NONE",
               "PRIMERA DISPONIBLE", "primera  disponible", "AUTO / LIBRE", "NAVE POR COMPLETAR", "(completar)",
               "AUTO.", "(AUTO)", "¿CUALQUIERA?", "PRIMERA-DISPONIBLE", "auto/libre", "PRIMERA/DISPONIBLE", "AUTO X",
               "X", "V.")
        # Solo el prefijo de la naviera, solo o con comodines, tampoco pide una nave (CICLO-cola-seis-items.md). Hasta
        # f68ce6c, «MSC» pedía una: cada naviera la buscaba como parte del campo de la nave de sus tarjetas, y calzaba con
        # toda nave que la trajera.
        prefijos = ("MSC", "msc", "HMM", "CMA CGM", "CMA-CGM", "ONE", "COSCO", "MV", "HYUNDAI", "Maersk", "(MSC)",
                    "HMM PRIMERA", "MSC / AUTO")
        # CSCL y COSCO SHIPPING también (CICLO-inicio-de-todas.md); COSCO SHIPPING como sus dos palabras, igual que CMA CGM,
        # así que SHIPPING sola, o antes de COSCO, tampoco pide una nave. Hasta c4df3ab, todas estas pedían una.
        prefijos += ("CSCL", "cscl", "COSCO SHIPPING", "Cosco Shipping", "COSCO-SHIPPING", "COSCO SHIPPING / AUTO",
                     "CSCL COSCO SHIPPING", "(COSCO SHIPPING)", "SHIPPING", "SHIPPING COSCO", "COSCO AUTO SHIPPING")
        # Una fila que dice MANUAL tampoco pide una nave: la hace el operador (CICLO-cola-seis-items.md). Hasta f68ce6c,
        # «MANUAL» pedía una: el panel la dejaba sin marcar, pero si se corría, cada naviera buscaba «MANUAL» en sus
        # tarjetas.
        manuales = ("MANUAL", "manual", "Reserva manual", "NAVE UNO MANUAL")
        # Con una palabra que no es comodín ni prefijo, la fila pide esa nave, y cada naviera la busca con todas sus
        # palabras, el prefijo incluido.
        con = ("NAVE PRUEBA UNO", "HMM NAVE", "AUTO NAVE", "NAVE LIBRE", "NA", "VOY", "NW2", "Ñandú",
               "MSC NAVE", "MSCA", "ONE NAVE UNO", "MANUEL")
        # Con una nave, CSCL y COSCO SHIPPING son parte de ella; pegadas a otra letra, no son el prefijo.
        con += ("CSCL NAVE", "COSCO SHIPPING NAVE", "NAVE COSCO SHIPPING", "COSCO NAVE SHIPPING", "COSCOSHIPPING", "CSCLA",
                "SHIPPINGS")
        # MANUAL como parte de otra palabra no es MANUAL: la celda pide esa nave (hasta c4df3ab, era MANUAL).
        con += ("MANUALMENTE", "NAVE SEMIMANUAL")
        for nave in sin + prefijos + manuales:
            with self.subTest(nave=nave):
                self.assertIs(f(nave), True)
        for nave in con:
            with self.subTest(nave=nave):
                self.assertIs(f(nave), False)
        self.assertEqual(self.mod.NAVES_COMODIN,
                         ("AUTO", "CUALQUIERA", "LIBRE", "NINGUNA", "NONE", "PRIMERA", "DISPONIBLE"))
        self.assertEqual(self.mod.NAVES_PREFIJO, ("MSC", "CMA", "CGM", "HMM", "ONE", "COSCO", "MV", "HYUNDAI", "MAERSK",
                                                  "CSCL", "SHIPPING"))
        self.assertEqual(self.mod.FILA_SIN_NAVE, self.MOTIVO)

    def corrida(self, nombre):
        vistas = []
        reg = self.mod.Registro(self.sb / nombre / "log.txt", on_log=vistas.append)
        self.addCleanup(reg.cerrar)
        return reg, vistas, self.sb / nombre / "log.txt"

    def test_fila_manual(self):
        # La regla con que el panel la deja sin marcar, que hasta f68ce6c vivía en su JavaScript: dice MANUAL como
        # palabra entera, sin distinguir mayúsculas (CICLO-cola-seis-items.md y CICLO-inicio-de-todas.md). Hasta c4df3ab
        # bastaba que fuera parte del texto: «MANUALMENTE» era MANUAL.
        f = self.mod._fila_manual
        for nave, manual in (("MANUAL", True), ("manual", True), ("Reserva manual", True), ("MANUALMENTE", False),
                             ("NAVE UNO MANUAL", True), ("NAVE UNO", False), ("MANUEL", False), ("", False),
                             (None, False), ("(MANUAL)", True), ("NAVE-MANUAL", True), ("MANUAL.", True),
                             ("SEMIMANUAL", False), ("MANUAL2", False), ("MANUALÑ", False), ("MANUALÁ", False),
                             ("MANUALÉ", False), ("ÍMANUAL", False), ("MANUALÓ", False), ("ÚMANUAL", False),
                             ("MANUALÜ", False), ("NAVE_MANUAL", True), ("SEMIMANUAL MANUAL", True)):
            with self.subTest(nave=nave):
                self.assertIs(f(nave), manual)
        self.assertEqual(self.mod.FILA_MANUAL, "la fila está marcada para hacerse a mano")

    def test_ningun_reservador_abre_el_portal_con_manual(self):
        # Una fila MANUAL que se corre igual queda NO ENVIADA con su propio motivo, sin tocar la página, en las seis
        # navieras (CICLO-cola-seis-items.md). Hasta f68ce6c entraba al portal y buscaba «MANUAL» como nave.
        motivo = "la fila está marcada para hacerse a mano"
        linea = (f"· ✗ fila 9: NO ENVIADA · {motivo}. No entro al portal por ella: hazla a mano en el portal, o escribe "
                 "en la celda solo la nave, sin MANUAL, si quieres que la arme yo.")
        for clave, reservar in sorted(self.mod.RESERVADORES.items()):
            for k, nave in enumerate(("MANUAL", "Nave uno manual")):
                with self.subTest(naviera=clave, nave=nave):
                    reg, vistas, log = self.corrida(f"manual_{clave}_{k}")
                    reserva = {"fila": 9, "nave": nave, "pol": "PUERTO ALFA", "destino_orig": "PUERTO BETA",
                               "destino_final": "CIUDAD GAMMA", "viaje": "", "dia_carga": ""}
                    self.assertEqual(reservar(PaginaQueNoSeToca(), reserva, {}, reg), ("NO ENVIADA", motivo))
                    for donde in (log.read_text(encoding="utf-8"), "\n".join(vistas)):     # log.txt y pantalla
                        self.assertIn(linea, donde)
                        self.assertNotIn(self.MOTIVO, donde)

    def test_ningun_reservador_abre_el_portal_sin_nave(self):
        # Hasta a198645, ONE y COSCO devolvían OMITIDO solo con la celda vacía, y HYUNDAI también con «completar»; con un
        # comodín, las seis entraban al portal, y hasta f68ce6c también con solo el prefijo de la naviera («HMM»). Los
        # orquestadores ya la apartan antes de abrir el navegador (test_web, test_consola).
        self.assertEqual(sorted(self.mod.RESERVADORES), ["cma", "cosco", "hyundai", "maersk", "msc", "one"])
        linea = (f"· ✗ fila 9: NO ENVIADA · {self.MOTIVO}. No entro al portal por ella: escribe la nave en la planilla "
                 "y vuelve a armar la reserva.")
        for clave, reservar in sorted(self.mod.RESERVADORES.items()):
            for k, nave in enumerate(("", "AUTO", "NAVE POR COMPLETAR", "HMM")):
                with self.subTest(naviera=clave, nave=nave):
                    reg, vistas, log = self.corrida(f"sin_nave_{clave}_{k}")
                    reserva = {"fila": 9, "nave": nave, "pol": "PUERTO ALFA", "destino_orig": "PUERTO BETA",
                               "destino_final": "CIUDAD GAMMA", "viaje": "", "dia_carga": ""}
                    self.assertEqual(reservar(PaginaQueNoSeToca(), reserva, {}, reg), ("NO ENVIADA", self.MOTIVO))
                    for donde in (log.read_text(encoding="utf-8"), "\n".join(vistas)):     # log.txt y pantalla
                        self.assertIn(linea, donde)

    def test_con_nave_pasa_igual(self):
        # Con nave, el decorador llama al reservador tal cual: la fila, las credenciales, el registro y on_pausa, con su
        # nombre y su documentación.
        def bien(page, reserva, creds, reg, on_pausa=None):
            """doc de prueba"""
            return ("OK-EJEMPLO", f"fila {reserva['fila']} {creds} {on_pausa}")
        envuelto = self.mod._con_la_nave_de_la_fila(bien)
        reg, vistas, _ = self.corrida("con_nave")
        self.assertEqual(envuelto(PaginaQueNoSeToca(), {"fila": 5, "nave": "NAVE PRUEBA UNO"}, "cred", reg, on_pausa="p"),
                         ("OK-EJEMPLO", "fila 5 cred p"))
        self.assertEqual((envuelto.__name__, envuelto.__doc__, vistas), ("bien", "doc de prueba", []))

    def test_una_sola_regla(self):
        # La regla es una sola: CMA decide con ella, y ningún reservador ni JavaScript tiene la suya. Hasta a198645, CMA
        # tenía su tupla de comodines y HYUNDAI quitaba de la nave AUTO, PRIMERA, DISPONIBLE y CUALQUIERA en su
        # JavaScript; ONE y COSCO devolvían OMITIDO con la celda vacía, y HYUNDAI también con «completar». «completar»
        # queda también en el lector del panel web, que no se toca: convierte esa celda en vacía.
        src = Path(self.mod.__file__).read_text(encoding="utf-8")
        tree = ast.parse(src)
        funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
        asigna = [ast.unparse(n) for n in ast.walk(funcs["_cma_seleccionar_itinerario"]) if isinstance(n, ast.Assign)
                  and ast.unparse(n.targets[0]) == "nave_especificada"]
        self.assertEqual(asigna, ["nave_especificada = not _fila_sin_nave(nave_pedida)"])
        con = lambda pred: sorted(nombre for nombre, f in funcs.items() for n in ast.walk(f)
                                  if isinstance(n, ast.Constant) and isinstance(n.value, str) and pred(n.value))
        self.assertEqual(con(lambda v: v.lower() == "completar"), ["_fila_sin_nave", "leer_filas"])
        self.assertEqual(con(lambda v: v == "OMITIDO"), [])
        # Ninguna función trae los comodines como texto, y ningún JavaScript trae entre comillas un comodín ni un prefijo
        # de naviera (casi todos los prefijos sí están como texto en otras funciones: son los nombres de las navieras).
        self.assertEqual(con(lambda v: v in self.mod.NAVES_COMODIN), [])
        js = [n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str) and "=>" in n.value]
        # MANUAL tiene una sola regla, _fila_manual: hasta f68ce6c el panel tenía la suya en su JavaScript.
        self.assertEqual(con(lambda v: v == "MANUAL"), ["_fila_manual"])
        self.assertEqual([w for w in self.mod.NAVES_COMODIN + self.mod.NAVES_PREFIJO + ("MANUAL",) for x in js
                          if f"'{w}'" in x or f'"{w}"' in x], [])



class TestFilaSinRuta(soporte.CasoAQ):
    """Una fila con nave que no trae su puerto de carga o su destino queda NO ENVIADA sin abrir el portal, como la fila
    sin nave (decisión de Marcelo, encargo 42, CICLO-maersk-y-fila-sin-ruta.md). Hasta ahí, con el texto vacío, los
    ayudantes de origen y de destino de las seis navieras calzaban con cualquier sugerencia a la vista."""
    PUERTO = "a la fila le falta el puerto de carga"
    DESTINO = "a la fila le falta el destino"

    def corrida(self, nombre):
        vistas = []
        reg = self.mod.Registro(self.sb / nombre / "log.txt", on_log=vistas.append)
        self.addCleanup(reg.cerrar)
        return reg, vistas, self.sb / nombre / "log.txt"

    @staticmethod
    def fila(pol="PUERTO ALFA", orig="PUERTO BETA", final="CIUDAD GAMMA", nave="NAVE PRUEBA UNO"):
        return {"fila": 9, "nave": nave, "pol": pol, "destino_orig": orig, "destino_final": final, "viaje": "",
                "dia_carga": ""}

    def test_falta_en_la_fila(self):
        # Las navieras buscan con la parte antes de la primera coma: sin una palabra ahí (_ciudad_de) no hay puerto ni
        # destino, y el puerto de carga se mide sin «CHILE» ni «CL» en ninguna posición (_puerto_de_carga; revisiones
        # del encargo 42: con «X CHILE», la palabra era el país, y COSCO buscaba «X»; después pasaban «CHILE X» y «№»,
        # que al normalizarse da «NO»; «CL», decisión de Marcelo, encargo 43). El destino es el final o, si viene
        # vacío, el original (leer_filas ya lo llena así, y leer_reservas también): con «-» en el final, las navieras
        # buscarían «-».
        f = lambda **k: self.mod._falta_en_la_fila(self.fila(**k))       # noqa: E731
        for pol in ("", None, "   ", ", CHILE", " , CHILE", ",", "-", "X", "?", "X, CHILE", "CHILE", "Chile",
                    " chile , CHILE", "Chile (Chile)", "X CHILE", "1 CHILE", "S/N CHILE", "X - CHILE", "x (Chile)",
                    "CHILE X", "Chile - X", "X CHILE Y", "CHILE S/N", "CHILE 1", "№", "CL", "cl", " CL , CHILE",
                    "CL CHILE", "CHILE CL", "Chile (CL)", "X CL", "CL X", "CL-CHILE"):
            with self.subTest(pol=pol):
                self.assertEqual(f(pol=pol), self.PUERTO)
        for orig, final in (("", ""), (None, None), (", PAIS", ""), ("", " , PAIS"), ("PUERTO BETA", ","),
                            ("PUERTO BETA", "-"), ("X", ""), ("", "?, PAIS")):
            with self.subTest(orig=orig, final=final):
                self.assertEqual(f(orig=orig, final=final), self.DESTINO)
        for k in ({}, {"orig": ""}, {"final": ""}, {"final": None}, {"pol": "PUERTO ALFA, CHILE"},
                  {"final": "CIUDAD GAMMA, PAIS"}, {"pol": "PUERTO CHILE ALFA"}, {"pol": "Puerto Ñu (Chile)"},
                  {"pol": "Chile (Puerto Alfa)"}, {"pol": "PUERTO CL"}, {"pol": "CLARO"}, {"pol": "PUERTO ALFA, CL"}):
            with self.subTest(**k):
                self.assertEqual(f(**k), "")
        self.assertEqual(f(pol="", orig="", final=""), self.PUERTO)      # sin los dos, el puerto primero
        self.assertEqual(self.mod._falta_en_la_fila(None), self.PUERTO)
        self.assertEqual((self.mod.FILA_SIN_PUERTO, self.mod.FILA_SIN_DESTINO), (self.PUERTO, self.DESTINO))

    def test_ciudad_de(self):
        # Lo que cada naviera escribe de la celda: la parte antes de la primera coma, sin los espacios de los extremos,
        # si trae dos letras o números seguidos, de cualquier alfabeto; si no, nada: «-», «?» o «X» calzarían con
        # cualquier sugerencia que los trajera (revisión de código del encargo 42).
        for celda, texto in (("  PUERTO ALFA , PAIS", "PUERTO ALFA"), ("PUERTO ALFA", "PUERTO ALFA"),
                             ("ÑÚ, PAIS", "ÑÚ"), ("A1", "A1"), ("10", "10"), ("-", ""), ("?", ""), ("X", ""),
                             ("X, PAIS", ""), ("X-Y Z", ""), ("__", ""), (", PAIS", ""), ("   ", ""), ("", ""),
                             (None, "")):
            with self.subTest(celda=celda):
                self.assertEqual(self.mod._ciudad_de(celda), texto)

    def linea(self, falta, que):
        return (f"· ✗ fila 9: NO ENVIADA · {falta}. No entro al portal por ella: escribe {que} en la planilla y vuelve "
                "a armar la reserva.")

    def test_ningun_reservador_abre_el_portal_sin_ruta(self):
        # Los orquestadores ya la apartan antes de abrir el navegador (test_web, test_consola); el decorador cuida
        # cualquier otro camino, sin tocar la página.
        casos = ((dict(pol=""), self.PUERTO, "el puerto de carga"),
                 (dict(pol=", CHILE"), self.PUERTO, "el puerto de carga"),
                 (dict(orig="", final=""), self.DESTINO, "el destino"))
        for clave, reservar in sorted(self.mod.RESERVADORES.items()):
            for k, (cambio, falta, que) in enumerate(casos):
                with self.subTest(naviera=clave, cambio=cambio):
                    reg, vistas, log = self.corrida(f"sin_ruta_{clave}_{k}")
                    self.assertEqual(reservar(PaginaQueNoSeToca(), self.fila(**cambio), {}, reg), ("NO ENVIADA", falta))
                    for donde in (log.read_text(encoding="utf-8"), "\n".join(vistas)):     # log.txt y pantalla
                        self.assertIn(self.linea(falta, que), donde)

    def test_sin_nave_dice_sin_nave(self):
        # Sin nave y sin la ruta, el motivo es el de la nave: su decorador va por fuera.
        for clave, reservar in sorted(self.mod.RESERVADORES.items()):
            with self.subTest(naviera=clave):
                reg, vistas, _ = self.corrida(f"sin_nave_ni_ruta_{clave}")
                fila = self.fila(pol="", orig="", final="", nave="AUTO")
                self.assertEqual(reservar(PaginaQueNoSeToca(), fila, {}, reg), ("NO ENVIADA", TestFilaSinNave.MOTIVO))
                self.assertNotIn(self.PUERTO, "\n".join(vistas))

    def test_con_la_ruta_pasa_igual(self):
        # Con la ruta, el decorador llama al reservador tal cual: la fila, las credenciales, el registro y on_pausa,
        # con su nombre y su documentación.
        def bien(page, reserva, creds, reg, on_pausa=None):
            """doc de prueba"""
            return ("OK-EJEMPLO", f"fila {reserva['fila']} {creds} {on_pausa}")
        envuelto = self.mod._con_la_ruta_de_la_fila(bien)
        reg, vistas, _ = self.corrida("con_ruta")
        self.assertEqual(envuelto(PaginaQueNoSeToca(), self.fila(), "cred", reg, on_pausa="p"),
                         ("OK-EJEMPLO", "fila 9 cred p"))
        self.assertEqual((envuelto.__name__, envuelto.__doc__, vistas), ("bien", "doc de prueba", []))


class TestOtroContenedorMaersk(soporte.CasoAQ):
    """Una fila de MAERSK que pide otro contenedor que el de las filas, «40 HC REEFER», queda NO ENVIADA sin abrir el
    portal (decisión de Marcelo, encargo 63, CICLO-maersk-otro-contenedor-y-reefer.md): MAERSK elige siempre «40 Reefer
    High» y, en los ajustes reefer, «Standard (40´)». Hasta ahí, con otro contenedor escribía otra palabra clave en la
    lista de tipos, y si el texto no traía «REEF», «RF» o «RH», se saltaba los ajustes reefer."""
    SOLO = "y en MAERSK el programa reserva solo «40 HC REEFER»"

    def corrida(self, nombre):
        vistas = []
        reg = self.mod.Registro(self.sb / nombre / "log.txt", on_log=vistas.append)
        self.addCleanup(reg.cerrar)
        return reg, vistas, self.sb / nombre / "log.txt"

    @staticmethod
    def fila(contenedor="40 HC REEFER", **cambios):
        return dict(TestFilaSinRuta.fila(**cambios), contenedor=contenedor)

    def test_otro_contenedor(self):
        # Sin distinguir mayúsculas y con los espacios de a uno. Cualquier otro texto es otro contenedor, también uno
        # que lo trae dentro; y una celda vacía no dice cuál (la consola, con la columna y la celda vacía).
        f = lambda c, nav="maersk": self.mod._otro_contenedor(nav, self.fila(c))       # noqa: E731
        self.assertEqual(self.mod.CONTENEDOR_DE_LAS_FILAS, "40 HC REEFER")
        for c in ("40 HC REEFER", "40 hc reefer", "  40  HC\tREEFER ", "40 Hc Reefer"):
            with self.subTest(contenedor=c):
                self.assertEqual(f(c), "")
        for c, dice in (("20 DRY", "20 DRY"), ("40 DRY", "40 DRY"), ("40HC REEFER", "40HC REEFER"),
                        ("40 HC REEFER SOC", "40 HC REEFER SOC"), ("45 HC REEFER", "45 HC REEFER"),
                        ("40 REEFER", "40 REEFER"), ("  20   dry ", "20 dry"), ("X" * 50, "X" * 40),
                        ("20 DRY" + chr(0), "20 DRY?"), ("20" + chr(27) + "DRY" + chr(127), "20?DRY?"),
                        # Uno invisible, que antes el motivo no mostraba: decía que la fila pedía «40 HC REEFER».
                        ("40 HC REEFER" + chr(0x200B), "40 HC REEFER?"), (chr(0xFEFF) + "20 DRY", "?20 DRY")):
            with self.subTest(contenedor=c):
                self.assertEqual(f(c), f"la fila pide el contenedor «{dice}», {self.SOLO}")
                # La planilla descargada lo puede escribir: openpyxl no escribe un carácter de control (revisión de
                # seguridad del encargo 65; hasta ahí, la fila quedaba sin su resultado).
                openpyxl.Workbook().active.cell(1, 1).value = f(c)
        for c in ("", None, "   "):
            with self.subTest(contenedor=c):
                self.assertEqual(f(c), f"la fila no dice qué contenedor pide, {self.SOLO}")
        self.assertEqual(self.mod._otro_contenedor("maersk", None), f"la fila no dice qué contenedor pide, {self.SOLO}")
        # Las otras navieras no miran el contenedor.
        for nav in ("one", "msc", "cma", "cosco", "hyundai"):
            with self.subTest(naviera=nav):
                self.assertEqual((f("20 DRY", nav), f("", nav)), ("", ""))

    def linea(self, motivo):
        return (f"· ✗ fila 9: NO ENVIADA · {motivo}. No entro al portal por ella: resérvala a mano en el portal, o "
                "corrige el contenedor en la planilla si la fila pide «40 HC REEFER».")

    def test_maersk_no_abre_el_portal_con_otro_contenedor(self):
        # Los orquestadores ya la apartan antes de abrir el navegador (test_web, test_consola); el decorador cuida
        # cualquier otro camino, sin tocar la página.
        casos = (("20 DRY", f"la fila pide el contenedor «20 DRY», {self.SOLO}"),
                 ("", f"la fila no dice qué contenedor pide, {self.SOLO}"))
        for k, (c, motivo) in enumerate(casos):
            with self.subTest(contenedor=c):
                reg, vistas, log = self.corrida(f"otro_contenedor_{k}")
                self.assertEqual(self.mod.RESERVADORES["maersk"](PaginaQueNoSeToca(), self.fila(c), {}, reg),
                                 ("NO ENVIADA", motivo))
                for donde in (log.read_text(encoding="utf-8"), "\n".join(vistas)):     # log.txt y pantalla
                    self.assertIn(self.linea(motivo), donde)

    def test_sin_nave_o_sin_ruta_dicen_eso(self):
        # Sin nave o sin la ruta, y con otro contenedor, el motivo es el de la nave o el de la ruta: su decorador va por
        # dentro de los dos.
        casos = ((dict(nave="AUTO"), TestFilaSinNave.MOTIVO), (dict(pol=""), TestFilaSinRuta.PUERTO))
        for k, (cambio, motivo) in enumerate(casos):
            with self.subTest(cambio=cambio):
                reg, vistas, _ = self.corrida(f"otro_contenedor_sin_{k}")
                fila = self.fila("20 DRY", **cambio)
                self.assertEqual(self.mod.RESERVADORES["maersk"](PaginaQueNoSeToca(), fila, {}, reg),
                                 ("NO ENVIADA", motivo))
                self.assertNotIn("20 DRY", "\n".join(vistas))

    def test_con_el_contenedor_pasa_igual(self):
        # Con el contenedor de las filas, el decorador llama al reservador tal cual: la fila, las credenciales, el
        # registro y on_pausa, con su nombre y su documentación.
        def bien(page, reserva, creds, reg, on_pausa=None):
            """doc de prueba"""
            return ("OK-EJEMPLO", f"fila {reserva['fila']} {creds} {on_pausa}")
        envuelto = self.mod._mk_con_el_contenedor_de_la_fila(bien)
        reg, vistas, _ = self.corrida("con_el_contenedor")
        self.assertEqual(envuelto(PaginaQueNoSeToca(), self.fila(" 40 hc reefer"), "cred", reg, on_pausa="p"),
                         ("OK-EJEMPLO", "fila 9 cred p"))
        self.assertEqual((envuelto.__name__, envuelto.__doc__, vistas), ("bien", "doc de prueba", []))


class TestCMA(soporte.CasoAQ):
    def detecta(self, frames=(), iframe=False, titulo="", texto=""):
        pagina = soporte.PaginaFalsa(texto=lambda js, *a: iframe if "querySelector('iframe" in js else texto,
                                     titulo=titulo, frames=list(frames))
        return self.mod._cma_es_robotcheck(pagina)

    def test_robotcheck_cma(self):
        self.assertTrue(self.detecta(frames=[Marco(url="https://geo.captcha-delivery.com/x")]))
        self.assertTrue(self.detecta(frames=[Marco(titulo="Access blocked")]))
        self.assertTrue(self.detecta(frames=[Marco(texto="Please prove you are not a robot")]))
        self.assertTrue(self.detecta(iframe=True))
        self.assertTrue(self.detecta(titulo="Verificación de seguridad"))
        self.assertTrue(self.detecta(texto="Desliza la flecha hacia la derecha"))
        self.assertFalse(self.detecta(frames=[Marco(url="https://www.ejemplo.invalid/")], titulo="Inicio", texto="Bienvenido"))

    def test_robotcheck_cma_pagina_que_falla(self):
        class Rompe(soporte.PaginaFalsa):
            @property
            def frames(self):
                raise RuntimeError("pagina cerrada")

            @frames.setter
            def frames(self, v):
                pass
        self.assertFalse(self.mod._cma_es_robotcheck(Rompe()))


class TestReefer(soporte.CasoAQ):
    def test_temperatura_reefer(self):
        f = self.mod._temp_reserva
        self.assertEqual(f({"temp": "-18"}), "-18")
        for r in ({}, None, {"temp": "  "}):
            with self.subTest(r=r):
                self.assertEqual(f(r), "-20")
        self.assertEqual((self.mod.TEMP_REEFER, self.mod.PESO_REEFER), ("-20", "22500"))

    # Desde el ítem 8 (CICLO-cola-nueve-items.md) el peso y la temperatura viven en config.json → opciones.
    AVISO_PESO = ("⚠ config.json no trae «peso_reefer_kg» en «opciones»: uso el valor de siempre, 22500. Si quieres "
                  "otro, escríbelo ahí como número.")

    def con_config(self, opciones):
        """Mientras dura la prueba, cargar_config devuelve una configuración con estas 'opciones'."""
        original = self.mod.cargar_config
        self.mod.cargar_config = lambda: {"opciones": dict(opciones)}
        self.addCleanup(setattr, self.mod, "cargar_config", original)

    def test_peso_y_temperatura_salen_de_config(self):
        self.con_config({"peso_reefer_kg": 24000, "temperatura_reefer_c": -18})
        self.assertEqual((self.mod._peso_reefer(), self.mod._temp_reserva({}), self.mod._temp_reserva({"temp": "-15"})),
                         ("24000", "-18", "-15"))

    def test_numeros_de_config(self):
        casos = ((22500, "22500"), (-20, "-20"), (22500.0, "22500"), (-20.5, "-20.5"), ("22500", "22500"),
                 (" -20 ", "-20"), ("-20,5", "-20.5"), (True, None), (False, None), (None, None), ("", None),
                 ("fría", None), ([22500], None), (float("nan"), None), (float("inf"), None))
        for valor, esperado in casos:
            with self.subTest(valor=valor):
                self.assertEqual(self.mod._numero_config(valor), esperado)

    def test_si_falta_o_no_es_numero_usa_el_de_siempre_y_avisa_una_vez(self):
        self.con_config({"temperatura_reefer_c": "fría"})
        vistas = []
        reg = self.mod.Registro(self.sb / "corrida_reefer" / "log.txt", on_log=vistas.append)
        self.addCleanup(reg.cerrar)
        for _ in range(2):
            self.assertEqual((self.mod._peso_reefer(), self.mod._temp_reserva({})), ("22500", "-20"))
        temperatura = ("⚠ En config.json, «temperatura_reefer_c» vale \"fría\" y no es un número: uso el valor de "
                       "siempre, -20. Si quieres otro, escríbelo ahí como número.")
        for donde in ((self.sb / "corrida_reefer" / "log.txt").read_text(encoding="utf-8"), "\n".join(vistas)):
            self.assertEqual((donde.count(self.AVISO_PESO), donde.count(temperatura)), (1, 1))

    def test_sin_corrida_avisa_una_vez_por_la_consola_y_el_panel(self):
        self.con_config({})
        panel = []
        for nombre, valor in (("_wlog", panel.append), ("_REGISTROS_ABIERTOS", weakref.WeakSet())):
            self.addCleanup(setattr, self.mod, nombre, getattr(self.mod, nombre))
            setattr(self.mod, nombre, valor)
        self.mod._AVISOS_SIN_CORRIDA.clear()
        self.addCleanup(self.mod._AVISOS_SIN_CORRIDA.clear)
        for _ in range(2):
            self.assertEqual(self.mod._peso_reefer(), "22500")
        self.assertEqual(panel, [self.AVISO_PESO])

    def test_una_sola_fuente(self):
        # El peso y la temperatura de siempre se nombran solo en sus constantes y en sus lectores de config.json.
        # Hasta 9e5285c, ONE y MSC tenían «22500» escrito aparte, y MSC un «-20» de respaldo.
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        usos = sorted(getattr(nodo, "name", type(nodo).__name__) for nodo in tree.body for n in ast.walk(nodo)
                      if isinstance(n, ast.Name) and n.id in ("PESO_REEFER", "TEMP_REEFER")
                      or isinstance(n, ast.Constant) and n.value in ("22500", "-20"))
        self.assertEqual(usos, ["Assign"] * 4 + ["_peso_reefer", "_temperatura_reefer"])

    def test_la_plantilla_trae_las_llaves(self):
        opciones = json.loads((soporte.FUENTES / "config.example.json").read_text(encoding="utf-8"))["opciones"]
        self.assertEqual((opciones.get("peso_reefer_kg"), opciones.get("temperatura_reefer_c")), (22500, -20))


class TestContratosPorDefecto(soporte.CasoAQ):
    """Desde el encargo 44, los contratos que van cuando ni la fila ni las credenciales traen uno viven en
    config.json → opciones → contratos_por_defecto: estaban escritos en el programa, y salieron para publicar el repo
    (CICLO-publicar-el-repo.md)."""

    def test_salen_de_config(self):
        con_contratos(self, {"one_usa": " CT-DEF-USA ", "one_otros": "CT-DEF-OTR", "msc": "CT-DEF-MSC",
                             "hyundai": "CT-DEF-HMM"})
        self.assertEqual([self.mod._contrato_por_defecto(k) for k in ("one_usa", "one_otros", "msc", "hyundai")],
                         ["CT-DEF-USA", "CT-DEF-OTR", "CT-DEF-MSC", "CT-DEF-HMM"])

    def test_sin_la_llave_o_sin_texto_queda_vacio_y_avisa_una_vez(self):
        vistas = []
        reg = self.mod.Registro(self.sb / "corrida_contratos" / "log.txt", on_log=vistas.append)
        self.addCleanup(reg.cerrar)
        casos = ((None, "msc"), ({"hyundai": 123}, "hyundai"), ({"one_usa": ""}, "one_usa"))
        for contratos, clave in casos:
            with self.subTest(clave=clave):
                con_contratos(self, contratos)
                for _ in range(2):
                    self.assertEqual(self.mod._contrato_por_defecto(clave), "")
        fin = ": sigo sin contrato por defecto. Si quieres uno, escríbelo ahí."
        sin_llave = "⚠ config.json no trae «msc» en «opciones → contratos_por_defecto»" + fin
        sin_texto = "⚠ En config.json, «contratos_por_defecto → hyundai» no es un texto" + fin
        for donde in ((self.sb / "corrida_contratos" / "log.txt").read_text(encoding="utf-8"), "\n".join(vistas)):
            # El vacío es una decisión del operador: no se avisa.
            self.assertEqual((donde.count(sin_llave), donde.count(sin_texto), donde.count("one_usa")), (1, 1, 0))

    def test_el_programa_ya_no_los_trae(self):
        # Cada naviera pide el suyo a _contrato_por_defecto, y en las líneas que hablan de contratos no queda un
        # código (letras mayúsculas y cifras juntas, 6 o más). Hasta el encargo 44, cuatro estaban escritos ahí.
        fuente = Path(self.mod.__file__).read_text(encoding="utf-8")
        tree = ast.parse(fuente)
        llamadas = sorted((nodo.name, n.args[0].value) for nodo in tree.body if isinstance(nodo, ast.FunctionDef)
                          for n in ast.walk(nodo) if isinstance(n, ast.Call)
                          and getattr(n.func, "id", "") == "_contrato_por_defecto"
                          and n.args and isinstance(n.args[0], ast.Constant))
        self.assertEqual(llamadas, LLAMADAS_CONTRATO)
        codigo = re.compile(r"\b(?=[A-Z0-9-]*\d)(?=[A-Z0-9-]*[A-Z])[A-Z0-9][A-Z0-9-]{5,}\b")
        con_codigo = [i for i, linea in enumerate(fuente.splitlines(), start=1)
                      if re.search(r"contrat|contract|shipper|cliente|cuenta", linea, re.I) and codigo.search(linea)]
        self.assertEqual(con_codigo, [])
        # El código de Shipper de HYUNDAI (4 letras y 4 cifras) tampoco: sale de config.json desde la revisión del
        # encargo 44, con su lector, en reservar_hyundai.
        self.assertEqual(re.findall(r"\b[A-Z]{4}\d{4}\b", fuente), [])
        lectores = [nodo.name for nodo in tree.body if isinstance(nodo, ast.FunctionDef) for n in ast.walk(nodo)
                    if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "_codigo_shipper_hyundai"]
        self.assertEqual(lectores, ["reservar_hyundai"])

    def test_hyundai_sin_contrato_no_elige_a_ciegas(self):
        # reservar_hyundai nunca elige un contrato sin mirar antes que no esté vacío (en un equipo sin los contratos en
        # config.json, lo estaría). En el paso 2 no elige nada: desde el encargo 91 lo elige _hmm_contrato_paso2, dentro
        # de «if ctto», y ya no _hmm_select_por_texto, que con un texto vacío tomaba la primera opción. En Booking
        # Details corta (revisión de código del encargo 44: hasta ahí, sin contrato iba a la primera opción real de la
        # lista). Con contrato, desde el encargo 89 lo elige _hmm_elegir_contrato, después del corte
        # (TestContratoDeHyundai).
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        f = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "reservar_hyundai")

        def con_ctto(nodo):
            return [n for n in ast.walk(nodo) if isinstance(n, ast.Call)
                    and ((getattr(n.func, "id", "") == "_hmm_select_por_texto" and len(n.args) > 2
                          and "ctto" in ast.unparse(n.args[2]))
                         or (getattr(n.func, "id", "") == "_hmm_contrato_paso2"
                             and [getattr(a, "id", "") for a in n.args[:2]] == ["page", "ctto"]))]

        guardadas = {id(c) for n in ast.walk(f) if isinstance(n, ast.If) and getattr(n.test, "id", "") == "ctto"
                     for parte in n.body for c in con_ctto(parte)}
        self.assertEqual([getattr(c.func, "id", "") for c in con_ctto(f)], ["_hmm_contrato_paso2"])
        cortes = [n.lineno for n in ast.walk(f) if isinstance(n, ast.If) and isinstance(n.test, ast.UnaryOp)
                  and isinstance(n.test.op, ast.Not) and getattr(n.test.operand, "id", "") == "ctto"
                  and any(isinstance(m, ast.Raise)
                          and getattr(getattr(m.exc, "func", None), "id", "") == "ObjetivoNoEncontrado"
                          for m in n.body)]
        sin_guarda = [c.lineno for c in con_ctto(f) if id(c) not in guardadas]
        elegir = [n.lineno for n in ast.walk(f) if isinstance(n, ast.Call)
                  and getattr(n.func, "id", "") == "_hmm_elegir_contrato"
                  and [getattr(a, "id", "") for a in n.args[:2]] == ["page", "ctto"]]
        self.assertEqual((len(con_ctto(f)), len(guardadas), len(cortes), len(sin_guarda), len(elegir)),
                         (1, 1, 1, 0, 1))
        self.assertLess(cortes[0], elegir[0])

    def test_la_plantilla_trae_las_llaves_vacias(self):
        opciones = json.loads((soporte.FUENTES / "config.example.json").read_text(encoding="utf-8"))["opciones"]
        self.assertEqual(opciones.get("contratos_por_defecto"),
                         {"one_usa": "", "one_otros": "", "msc": "", "hyundai": ""})
        self.assertEqual(opciones.get("codigo_shipper_hyundai"), "")

    def test_el_codigo_shipper_de_hyundai_sale_de_config(self):
        con_opciones(self, {"codigo_shipper_hyundai": " SHIP0001 "})
        self.assertEqual(self.mod._codigo_shipper_hyundai(), "SHIP0001")

    def test_sin_el_codigo_shipper_queda_vacio_y_avisa_una_vez(self):
        vistas = []
        reg = self.mod.Registro(self.sb / "corrida_shipper" / "log.txt", on_log=vistas.append)
        self.addCleanup(reg.cerrar)
        for opciones in ({}, {"codigo_shipper_hyundai": 7}):
            with self.subTest(opciones=opciones):
                con_opciones(self, opciones)
                for _ in range(2):
                    self.assertEqual(self.mod._codigo_shipper_hyundai(), "")
        aviso = ("⚠ config.json no trae «codigo_shipper_hyundai» en «opciones»: busco el Shipper de HYUNDAI solo "
                 "por el nombre de la empresa.")
        for donde in ((self.sb / "corrida_shipper" / "log.txt").read_text(encoding="utf-8"), "\n".join(vistas)):
            # Una vez por corrida: el segundo caso (no es un texto) ya no avisa, porque comparte la llave del aviso.
            self.assertEqual((donde.count(aviso), donde.count("codigo_shipper_hyundai")), (1, 1))


class PaginaContrato:
    """La lista «Contract No» del paso 3 de HYUNDAI (#selContractNo). Cada opción es un texto (su valor es su código,
    el texto antes de « - », como en el HTML del paso 3 que guardaron las corridas del colega) o un par (texto, valor).
    Cada lectura de sus opciones (el JavaScript de _hmm_pares, con el selector de argumento) da la siguiente de
    'lecturas' (la última se repite), en pares; el JavaScript de _hmm_select_por_texto elige como el del programa (la
    primera opción que trae todos los textos, en mayúsculas) y da su valor; select_option deja elegida la primera con
    ese valor, como el navegador, o falla si 'acepta' es False; y la lectura de la opción elegida da su texto, o
    'queda' si se le pasa (la lista quedó con otra), o falla si 'se_lee' es False. Anota cada lectura, cada elección y
    cada comprobación, y cada espera aparte; un JavaScript que no conoce lo anota en 'inesperado' y devuelve None,
    porque el programa se tragaría una excepción en su try (la prueba exige esa lista vacía)."""

    def __init__(self, lecturas, acepta=True, queda=None, se_lee=True):
        self.lecturas = [[self.opcion(o) for o in lista] for lista in lecturas]
        self.acepta, self.queda, self.se_lee = acepta, queda, se_lee
        self.actual, self.elegida, self.hechos, self.esperas, self.inesperado = [], None, [], [], []

    @staticmethod
    def opcion(o):
        """Una opción como (texto, valor, etiqueta): el valor, si no viene, es su código; la etiqueta, si no viene, su
        texto con los espacios de a uno, como el `label` de una opción sin ese atributo."""
        o = o if isinstance(o, tuple) else (o, o.split(" - ")[0])
        return o if len(o) == 3 else (o[0], o[1], " ".join(o[0].split()))

    def wait_for_timeout(self, ms):
        self.esperas.append(ms)

    def evaluate(self, js, arg=None):
        if arg is None and "#selContractNo" in js and "selectedIndex" in js:
            self.hechos.append(("comprueba",))
            if not self.se_lee:
                raise RuntimeError("la página no contestó" + chr(10) + "LINEA FALSA")
            return self.queda if self.queda is not None else self.elegida
        if arg == "#selContractNo" and "s.options" in js:
            if self.lecturas:
                self.actual = self.lecturas.pop(0)
            self.hechos.append(("lee", len(self.actual)))
            return [list(o) for o in self.actual]
        if isinstance(arg, dict) and arg.get("sel") == "#selContractNo":
            toks = arg["toks"]
            o = next((v for t, v, _ in self.actual if all(x in t.upper() for x in toks)), None)
            return o if o is not None else ""
        self.inesperado.append(js[:60])
        return None

    def select_option(self, sel, value=None, timeout=None):
        self.hechos.append(("elige", sel, value))
        if not self.acepta:
            raise RuntimeError("el portal no la aceptó")
        self.elegida = next((t for t, v, e in self.actual if value in (v, e)), None)


class PaginaPaso2:
    """La lista de contrato del paso 2 de HYUNDAI (HMM_LISTA_PASO2): su lectura (el JavaScript de _hmm_pares, con ese
    selector) da 'opciones', pares (texto, valor), o falla si 'lee' no es True (con 'lee' como mensaje);
    select_option la elige, o falla si 'acepta' es False. Anota cada lectura y cada elección; un JavaScript que no
    conoce lo anota en 'inesperado' (la prueba exige esa lista vacía)."""

    def __init__(self, sel, opciones, lee=True, acepta=True):
        self.sel, self.opciones, self.lee, self.acepta = sel, opciones, lee, acepta
        self.hechos, self.inesperado = [], []

    def evaluate(self, js, arg=None):
        if arg == self.sel and "s.options" in js:
            self.hechos.append(("lee",))
            if self.lee is not True:
                raise RuntimeError(self.lee or "la página no contestó")
            return [list(PaginaContrato.opcion(o)) for o in self.opciones]
        self.inesperado.append(js[:60])
        return None

    def select_option(self, sel, value=None, timeout=None):
        self.hechos.append(("elige", sel, value))
        if not self.acepta:
            raise RuntimeError("el portal no la aceptó")


class TestContratoDeHyundai(soporte.CasoAQ):
    """«Contract No» del paso 3 de HYUNDAI (decisión de Marcelo, encargo 89, CICLO-hyundai-contrato-por-posicion.md):
    con un contrato configurado, solo la única opción cuyo código (el texto antes de « - ») o, desde el encargo 90,
    cuyo texto completo es el contrato entero, y después se lee la lista para ver que quedó esa; si no está, si dos
    calzan (comparten el código), si la lista no muestra ninguno
    o si queda otra, NO ENVIADA sin elegir otra cosa, con el contrato que buscó, saneado, y, si se corrige escribiéndolo,
    dónde (panel → Credenciales → HYUNDAI → columna Contrato). Hasta ahí elegía la primera opción real, por su posición,
    y bastaba que el texto de la opción contuviera el contrato."""
    LISTA = ["Select", "OTRO-UNO - (GA)", "CT-PRUEBA-HMM - (GA)", "Dummy", "Direct Input"]
    DONDE = "panel → Credenciales → HYUNDAI → columna Contrato"
    FIN = ", así que no pulsé nada. La reserva no se envió; revisa ese paso en el portal."
    NO_ESTA = ("Contract No de HYUNDAI: no encontré el contrato «{}» entre los {} que ofrece el portal (se compara "
               "entero con el código de cada opción, su texto antes de « - », o con su texto completo; se corrige en "
               "el panel → Credenciales → HYUNDAI → columna Contrato)")

    def correr(self, pagina, nombre, ctto="CT-PRUEBA-HMM"):
        """Corre _hmm_elegir_contrato dentro de un reservador decorado como reservar_hyundai (_sin_clic_a_ciegas), con
        la evidencia del corte reemplazada. Devuelve (resultado, log.txt), y exige que la página no viera nada
        inesperado."""
        log = self.sb / nombre / "log.txt"
        reg = self.mod.Registro(log)
        self.addCleanup(reg.cerrar)

        @self.mod._sin_clic_a_ciegas("hmm")
        def reservar(page, reserva, creds, reg, on_pausa=None):
            self.mod._hmm_elegir_contrato(page, ctto, reg)
            return ("SIGUE", "")
        with mock.patch.object(self.mod, "_evidencia_antes_de_la_guarda", lambda *a, **k: None):
            r = reservar(pagina, {"fila": 9}, {}, reg)
        self.assertEqual(pagina.inesperado, [])
        return r, log.read_text(encoding="utf-8")

    def test_elige_la_unica_que_trae_el_contrato(self):
        # Aunque haya otra opción real antes, y aunque la del contrato llegue después: lee hasta que llegue (antes se
        # quedaba con la primera lectura que traía una real). El contrato, sin distinguir mayúsculas ni los espacios de
        # sus extremos, como antes, y la opción también en minúsculas. Después lee qué opción quedó elegida.
        minusculas = ["Select", "otro-uno - (ga)", "ct-prueba-hmm - (ga)"]
        for k, (ctto, lista, valor) in enumerate((("CT-PRUEBA-HMM", self.LISTA, "CT-PRUEBA-HMM"),
                                                  (" ct-prueba-hmm ", self.LISTA, "CT-PRUEBA-HMM"),
                                                  ("CT-PRUEBA-HMM", minusculas, "ct-prueba-hmm"))):
            with self.subTest(ctto=ctto, lista=lista):
                p = PaginaContrato([["Select"], ["Select", "OTRO-UNO - (GA)"], lista])
                r, log = self.correr(p, f"contrato_elige_{k}", ctto)
                self.assertEqual(r, ("SIGUE", ""))
                self.assertEqual([h for h in p.hechos if h[0] != "lee"],
                                 [("elige", "#selContractNo", valor), ("comprueba",)])
                self.assertEqual([h for h in p.hechos if h[0] == "lee"], [("lee", 1), ("lee", 2), ("lee", len(lista))])
                self.assertIn(f"Contract No: '{valor}'", log)
                self.assertIn("Contract No: la lista quedó con la opción del contrato", log)

    def test_el_contrato_se_compara_entero(self):
        # La decisión (a): el contrato entero contra el código de la opción (o, desde el encargo 90, contra su texto
        # completo), nunca «el texto lo contiene». Un contrato escrito a medias no calza con el que lo contiene (antes
        # lo elegía), tampoco un pedazo o un alargue del texto completo; y con el entero, entre una opción que lo
        # contiene y la suya, elige la suya (antes: «lo traen 2», NO ENVIADA).
        for k, (ctto, lista) in enumerate((("CT-PRUEBA", self.LISTA),
                                           ("CT-1", ["Select", "CT-12 - (GA)"]),
                                           ("PRUEBA-HMM", self.LISTA),
                                           ("CT-PRUEBA-HMM - (G", self.LISTA),
                                           ("CT-PRUEBA-HMM - (GA) X", self.LISTA),
                                           ("PRUEBA-HMM - (GA)", self.LISTA))):
            with self.subTest(ctto=ctto):
                p = PaginaContrato([lista])
                r, _ = self.correr(p, f"contrato_a_medias_{k}", ctto)
                reales = len([o for o in lista if o.lower() not in ("select", "dummy", "direct input")])
                self.assertEqual(r, ("NO ENVIADA", self.NO_ESTA.format(ctto, reales) + self.FIN))
                self.assertNotIn("elige", [h[0] for h in p.hechos])
        p = PaginaContrato([["Select", "CT-PRUEBA-HMM-2 - (GA)", "CT-PRUEBA-HMM - (GA)"]])
        r, _ = self.correr(p, "contrato_entero")
        self.assertEqual(r, ("SIGUE", ""))
        self.assertEqual([h for h in p.hechos if h[0] != "lee"],
                         [("elige", "#selContractNo", "CT-PRUEBA-HMM"), ("comprueba",)])

    def test_acepta_el_texto_completo_de_la_opcion(self):
        # Decisión de Marcelo, encargo 90: el contrato copiado de la lista tal cual, con el texto completo de su opción,
        # la elige, como su código; sin distinguir mayúsculas ni los espacios de los extremos, en el contrato y en la
        # opción. Con el 89 quedaba NO ENVIADA.
        minusculas = ["Select", "otro-uno - (ga)", "ct-prueba-hmm - (ga)"]
        for k, (ctto, lista, valor) in enumerate((("CT-PRUEBA-HMM - (GA)", self.LISTA, "CT-PRUEBA-HMM"),
                                                  (" ct-prueba-hmm - (ga) ", self.LISTA, "CT-PRUEBA-HMM"),
                                                  ("CT-PRUEBA-HMM - (GA)", minusculas, "ct-prueba-hmm"))):
            with self.subTest(ctto=ctto, lista=lista):
                p = PaginaContrato([lista])
                r, log = self.correr(p, f"contrato_texto_{k}", ctto)
                self.assertEqual(r, ("SIGUE", ""))
                self.assertEqual([h for h in p.hechos if h[0] != "lee"],
                                 [("elige", "#selContractNo", valor), ("comprueba",)])
                self.assertIn("Contract No: la lista quedó con la opción del contrato", log)
        self.assertEqual(self.mod._hmm_contratos_que_calzan(self.LISTA, "ct-prueba-hmm - (ga)"),
                         ["CT-PRUEBA-HMM - (GA)"])
        self.assertEqual(self.mod._hmm_contratos_que_calzan(["  CT-PRUEBA-HMM - (GA) "], "CT-PRUEBA-HMM - (GA)"),
                         ["  CT-PRUEBA-HMM - (GA) "])

    def test_si_no_esta_no_envia_y_no_elige_por_posicion(self):
        # Con la primera opción real a la vista y sin la del contrato: lee las 15 veces, cada 0,4 s, y corta sin elegir
        # nada. Hasta el encargo 89 elegía esa primera, por su posición.
        p = PaginaContrato([["Select", "OTRO-UNO - (GA)", "OTRO-DOS - (GA)", "Dummy", "Direct Input"]])
        r, log = self.correr(p, "contrato_no_esta")
        self.assertEqual(r, ("NO ENVIADA", self.NO_ESTA.format("CT-PRUEBA-HMM", 2) + self.FIN))
        self.assertEqual(p.hechos, [("lee", 5)] * self.mod.HMM_LECTURAS_CONTRATO)
        self.assertEqual(p.esperas, [400] * self.mod.HMM_LECTURAS_CONTRATO)
        self.assertIn("Contract No opciones: Select | OTRO-UNO - (GA) | OTRO-DOS - (GA) | Dummy | Direct Input", log)
        self.assertEqual(self.mod.HMM_LECTURAS_CONTRATO, 15)

    def test_si_la_lista_no_trae_contratos_no_culpa_al_configurado(self):
        # Si el portal no mostró ningún contrato (la lista vacía, o solo «Select», «Dummy» y «Direct Input»), el
        # motivo lo dice, sin mandar a corregir el contrato, que puede estar bien (revisión de código del encargo 89).
        for k, lista in enumerate(([], ["Select"], ["Select", "Dummy", "Direct Input"])):
            with self.subTest(lista=lista):
                p = PaginaContrato([lista])
                r, _ = self.correr(p, f"contrato_sin_lista_{k}")
                self.assertEqual(r, ("NO ENVIADA", "Contract No de HYUNDAI: no encontré ningún contrato en la lista "
                                                   "del portal (no mostró ninguno en 6 s; el configurado es "
                                                   "«CT-PRUEBA-HMM»)" + self.FIN))
                self.assertNotIn("elige", [h[0] for h in p.hechos])

    def test_las_opciones_que_no_son_un_contrato_no_cuentan(self):
        # «Select», «Dummy» y «Direct Input» no son un contrato (HMM_NO_SON_CONTRATO, las de antes): un contrato
        # configurado que es el código de una de ellas no elige nada. Un contrato de solo espacios tampoco calza: sin
        # eso, calzaría con una opción de solo espacios (revisión de código).
        for k, ctto in enumerate(("Direct Input", "DUMMY", "   ")):
            with self.subTest(ctto=ctto):
                p = PaginaContrato([["Select", "CT-PRUEBA-HMM - (GA)", "Dummy", "Direct Input"]])
                r, _ = self.correr(p, f"contrato_no_es_{k}", ctto)
                self.assertEqual(r[0], "NO ENVIADA")
                self.assertNotIn("elige", [h[0] for h in p.hechos])
        self.assertEqual(self.mod._hmm_contratos_que_calzan(["   ", "CT-PRUEBA-HMM - (GA)"], "  "), [])

    def test_si_dos_tienen_el_mismo_codigo_no_elige_la_primera(self):
        # Dos opciones con el mismo código: con el contrato escrito como el código, calzan las dos, y NO ENVIADA; el
        # motivo no manda a corregirlo, y el decorador dice que se revise el paso en el portal.
        p = PaginaContrato([["Select", "CT-PRUEBA-HMM - (GA)", "CT-PRUEBA-HMM - (FMC)"]])
        r, _ = self.correr(p, "contrato_dos")
        self.assertEqual(r, ("NO ENVIADA", "Contract No de HYUNDAI: no encontré una sola opción con el contrato "
                                           "«CT-PRUEBA-HMM»: el portal ofrece 2 con ese mismo código" + self.FIN))
        self.assertNotIn("elige", [h[0] for h in p.hechos])
        # Escrito con el texto completo de una de ellas (encargo 90), la regla la separa, pero si las dos tienen el
        # mismo valor (el código, como en el HTML del paso 3), al elegir no se distinguen: NO ENVIADA, sin elegir nada,
        # se haya escrito el texto de la primera o el de la segunda (decisión de Marcelo, encargo 91). Hasta ahí, con
        # el de la primera la reserva seguía, y con el de la segunda la frenaba la comprobación.
        dos = ["Select", "CT-PRUEBA-HMM - (FMC)", "CT-PRUEBA-HMM - (GA)"]
        for k, ctto in enumerate(("CT-PRUEBA-HMM - (FMC)", "CT-PRUEBA-HMM - (GA)")):
            with self.subTest(ctto=ctto):
                p = PaginaContrato([dos])
                r, _ = self.correr(p, f"contrato_dos_texto_{k}", ctto)
                self.assertEqual(r, ("NO ENVIADA", "Contract No de HYUNDAI: no encontré una sola opción con el "
                                                   f"contrato «{ctto}»: el portal da el mismo valor a 2 opciones, y al "
                                                   "elegir no se distinguen" + self.FIN))
                self.assertNotIn("elige", [h[0] for h in p.hechos])
        # Lo mismo si el valor lo comparte una opción que no es un contrato («Select», por ejemplo).
        p = PaginaContrato([[("Select", "CT-PRUEBA-HMM"), "CT-PRUEBA-HMM - (GA)"]])
        r, _ = self.correr(p, "contrato_valor_de_select")
        self.assertEqual(r, ("NO ENVIADA", "Contract No de HYUNDAI: no encontré una sola opción con el contrato "
                                           "«CT-PRUEBA-HMM»: el portal da el mismo valor a 2 opciones, y al elegir no "
                                           "se distinguen" + self.FIN))
        # Y si otra opción tiene ese valor como etiqueta (su texto): `select_option(value=…)` de Playwright para Python
        # elige por el valor o por la etiqueta (revisión de código del encargo 91).
        p = PaginaContrato([[("Select", ""), ("CT-1", "ZZ"), ("CT-1 - (GA)", "CT-1")]])
        r, _ = self.correr(p, "contrato_valor_como_etiqueta", "CT-1 - (GA)")
        self.assertEqual(r, ("NO ENVIADA", "Contract No de HYUNDAI: no encontré una sola opción con el contrato "
                                           "«CT-1 - (GA)»: el portal da el mismo valor a 2 opciones, y al elegir no se "
                                           "distinguen" + self.FIN))
        self.assertNotIn("elige", [h[0] for h in p.hechos])
        # Con el mismo código y valores distintos, el texto completo elige la suya; el código solo, sigue sin poder.
        distintos = [("Select", ""), ("CT-PRUEBA-HMM - (FMC)", "CT-FMC"), ("CT-PRUEBA-HMM - (GA)", "CT-GA")]
        p = PaginaContrato([distintos])
        self.assertEqual(self.correr(p, "contrato_valores_distintos", "CT-PRUEBA-HMM - (GA)")[0], ("SIGUE", ""))
        self.assertEqual([h for h in p.hechos if h[0] != "lee"], [("elige", "#selContractNo", "CT-GA"), ("comprueba",)])
        p = PaginaContrato([distintos])
        self.assertEqual(self.correr(p, "contrato_valores_distintos_codigo")[0][0], "NO ENVIADA")

    def test_si_la_lista_no_acepta_la_eleccion_corta(self):
        p = PaginaContrato([self.LISTA], acepta=False)
        r, _ = self.correr(p, "contrato_no_acepta")
        self.assertEqual(r, ("NO ENVIADA", "Contract No de HYUNDAI: no encontré cómo dejar elegido el contrato "
                                           "«CT-PRUEBA-HMM»: la lista no lo aceptó o ya no lo trae" + self.FIN))
        self.assertEqual([h for h in p.hechos if h[0] == "elige"], [("elige", "#selContractNo", "CT-PRUEBA-HMM")])

    def test_si_la_lista_queda_con_otra_opcion_corta(self):
        # Después de elegir, lee qué opción quedó elegida (revisión de seguridad del encargo 89): si es otra, o si no se
        # puede leer, NO ENVIADA, y log.txt dice cuál quedó. El tercer caso no fuerza la lectura: una opción de otro
        # contrato cuyo texto contiene entero el de la del contrato, y va antes, es la que elige _hmm_select_por_texto
        # (la primera que lo contiene), y la comprobación la ve (segunda revisión de código del encargo 89).
        antes = ["Select", "XCT-PRUEBA-HMM - (GA)", "CT-PRUEBA-HMM - (GA)"]
        for k, (pagina, como, valor, quedo) in enumerate((
                (PaginaContrato([self.LISTA], queda="OTRO-UNO - (GA)"), "quedó otra opción", "CT-PRUEBA-HMM",
                 "OTRO-UNO - (GA)"),
                (PaginaContrato([self.LISTA], se_lee=False), "no pude leer qué opción quedó", "CT-PRUEBA-HMM", None),
                (PaginaContrato([antes]), "quedó otra opción", "XCT-PRUEBA-HMM", "XCT-PRUEBA-HMM - (GA)"))):
            with self.subTest(como=como, valor=valor):
                r, log = self.correr(pagina, f"contrato_queda_{k}")
                self.assertEqual(r, ("NO ENVIADA", "Contract No de HYUNDAI: no encontré el contrato «CT-PRUEBA-HMM» "
                                                   f"elegido en la lista: después de elegirlo, {como}" + self.FIN))
                self.assertEqual([h for h in pagina.hechos if h[0] != "lee"],
                                 [("elige", "#selContractNo", valor), ("comprueba",)])
                if quedo:
                    self.assertIn(f"Contract No: la lista quedó con «{quedo}»", log)
                else:
                    self.assertNotIn("la lista quedó con «", log)
                    # El error va saneado: un salto de línea no parte la línea (encargo 91).
                    self.assertIn("Contract No: err al leer la opción elegida (la página no contestó LINEA FALSA)", log)

    def test_js_lee_la_lista_y_la_opcion_elegida(self):
        # Los dos JavaScript que leen «Contract No», corridos en Node sobre una lista falsa (segunda revisión de código
        # del encargo 89: la página falsa de arriba los reconoce por su texto y no los corre). De cada opción, su texto
        # sin los espacios de sus extremos y, desde el encargo 91, su valor, de la lista del selector que recibe; de la
        # elegida, su texto (no su valor); sin la lista, [] y null.
        guion = ("const lee = " + self.mod._JS_HMM_CONTRATOS + ";\nconst elegida = " + self.mod._JS_HMM_CONTRATO_ELEGIDO
                 + ";\nconst P2 = " + json.dumps(self.mod.HMM_LISTA_PASO2) + r""";
const op = (t, v, l) => ({textContent: t, value: v, label: l});
const s = (i) => ({options: [op('Select', '', 'Select'), op('\n   CT-PRUEBA-HMM - (GA)\n', 'CT-PRUEBA-HMM', 'L-UNO'),
                             op('OTRO-UNO - (GA)', 'OTRO-UNO', 'L-DOS')], selectedIndex: i});
const paso2 = {options: [op('PASO-DOS - (GA)', 'PASO-DOS', 'L-TRES')], selectedIndex: 0};
const r = [];
for (const sel of [s(1), s(2), s(0), s(-1), null]) {
  global.document = {querySelector: (q) => (q === '#selContractNo' ? sel : (q === P2 ? paso2 : null))};
  r.push([lee('#selContractNo'), elegida(), lee(P2)]);
}
console.log(JSON.stringify(r));
""")
        lista = [["Select", "", "Select"], ["CT-PRUEBA-HMM - (GA)", "CT-PRUEBA-HMM", "L-UNO"],
                 ["OTRO-UNO - (GA)", "OTRO-UNO", "L-DOS"]]
        p2 = [["PASO-DOS - (GA)", "PASO-DOS", "L-TRES"]]
        self.assertEqual(correr_node(self, guion), [[lista, "CT-PRUEBA-HMM - (GA)", p2], [lista, "OTRO-UNO - (GA)", p2],
                                                    [lista, "Select", p2], [lista, None, p2], [[], None, p2]])

    def test_el_motivo_muestra_el_contrato_saneado(self):
        # El motivo va a la planilla, y openpyxl no escribe un carácter de control: el contrato va como lo muestra
        # _hmm_contrato_a_la_vista, con los espacios de a uno, hasta 40 caracteres y cada carácter de control o de
        # formato como «?» (revisión de seguridad del encargo 89).
        ctto = "CT" + chr(0) + "PRUEBA" + chr(0x202E) + " x" * 30
        visto = "CT?PRUEBA?" + " x" * 15
        self.assertEqual(self.mod._hmm_contrato_a_la_vista(ctto), visto)
        p = PaginaContrato([self.LISTA])
        r, _ = self.correr(p, "contrato_saneado", ctto)
        self.assertEqual(r, ("NO ENVIADA", self.NO_ESTA.format(visto, 2) + self.FIN))
        # La línea «Contract No opciones» de log.txt va saneada igual: el texto de las opciones viene del portal
        # (encargo 91; revisión de seguridad del encargo 89). Hasta ahí, una opción con un salto de línea partía la
        # línea.
        rara = "OTRO" + chr(0) + "UNO" + chr(10) + "- (GA)"
        p = PaginaContrato([["Select", rara, "CT-PRUEBA-HMM - (GA)"]])
        r, log = self.correr(p, "contrato_opciones_saneadas")
        self.assertEqual(r, ("SIGUE", ""))
        self.assertIn("Contract No opciones: Select | OTRO?UNO - (GA) | CT-PRUEBA-HMM - (GA)", log)
        self.assertNotIn(chr(0), log)

    def test_los_motivos_dicen_donde_se_escribe(self):
        # Los siete cortes de «Contract No de HYUNDAI» del programa: sin contrato (en reservar_hyundai) y los seis de
        # _hmm_elegir_contrato (desde el encargo 91, también el del valor compartido). Ninguno nombra config.json; los
        # dos que se corrigen escribiendo el contrato dicen dónde; y ninguno muestra el contrato sin sanear (ctto). Sin
        # contrato: «no encontré un contrato (se escribe en el panel → Credenciales → HYUNDAI → columna Contrato)». Y
        # reservar_hyundai le quita los espacios al de las credenciales, en el paso 2 y en el 3, como ONE, MSC y
        # CMA-CGM.
        self.assertEqual(self.mod.HMM_DONDE_VA_EL_CONTRATO, self.DONDE)
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        cortes = [(f.name, n.exc.args[1]) for f in tree.body if isinstance(f, ast.FunctionDef) for n in ast.walk(f)
                  if isinstance(n, ast.Raise) and isinstance(n.exc, ast.Call)
                  and getattr(n.exc.func, "id", "") == "ObjetivoNoEncontrado" and n.exc.args
                  and getattr(n.exc.args[0], "value", "") == "Contract No de HYUNDAI"]
        self.assertEqual(sorted(nombre for nombre, _ in cortes), ["_hmm_elegir_contrato"] * 6 + ["reservar_hyundai"])
        textos = [ast.unparse(b) for _, b in cortes]
        self.assertEqual([t for t in textos if "config.json" in t], [])
        self.assertEqual(sum("HMM_DONDE_VA_EL_CONTRATO" in t for t in textos), 2)
        self.assertEqual([t for t in textos if "ctto" in t], [])
        sin = next(b for nombre, b in cortes if nombre == "reservar_hyundai")
        self.assertEqual(eval(compile(ast.Expression(sin), "motivo", "eval"), vars(self.mod)),
                         f"un contrato (se escribe en el {self.DONDE})")
        f = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "reservar_hyundai")
        ctto = [ast.unparse(n.value) for n in ast.walk(f) if isinstance(n, ast.Assign)
                and ast.unparse(n.targets[0]) == "ctto"]
        self.assertEqual(ctto, ["str(creds.get('contrato') or '').strip() or _contrato_por_defecto('hyundai')"] * 2)


class TestContratoPaso2DeHyundai(soporte.CasoAQ):
    """La lista de contrato del paso 2 de HYUNDAI (decisión de Marcelo, encargo 91,
    CICLO-hyundai-valor-compartido-y-paso2.md): _hmm_contrato_paso2 elige solo la opción cuyo código o texto completo
    es el contrato, como el paso 3, y cuyo valor no comparte otra, por su valor; si no, no elige nada y no corta: queda
    el del portal. Hasta ahí elegía con _hmm_select_por_texto la primera que contenía el contrato. Medido antes del
    cambio: en el HTML de las 17 corridas, la lista no traía ninguna opción."""
    OPCIONES = [("Select", ""), ("OTRO-UNO - (GA)", "OTRO-UNO"), ("CT-PRUEBA-HMM - (GA)", "CT-PRUEBA-HMM")]

    def paso2(self, pagina, nombre, ctto="CT-PRUEBA-HMM"):
        """Corre _hmm_contrato_paso2; devuelve (lo que devolvió, log.txt) y exige que la página no viera nada inesperado
        y que no saliera ninguna excepción."""
        log = self.sb / nombre / "log.txt"
        reg = self.mod.Registro(log)
        self.addCleanup(reg.cerrar)
        r = self.mod._hmm_contrato_paso2(pagina, ctto, reg)
        self.assertEqual(pagina.inesperado, [])
        return r, log.read_text(encoding="utf-8")

    def test_elige_solo_la_que_calza_exacto_por_su_valor(self):
        sel = self.mod.HMM_LISTA_PASO2
        self.assertEqual(sel, "select[id*='contract' i], select[name*='contract' i]")
        for k, ctto in enumerate(("CT-PRUEBA-HMM", " ct-prueba-hmm - (ga) ")):
            with self.subTest(ctto=ctto):
                p = PaginaPaso2(sel, self.OPCIONES)
                r, log = self.paso2(p, f"paso2_elige_{k}", ctto)
                self.assertIs(r, True)
                self.assertEqual(p.hechos, [("lee",), ("elige", sel, "CT-PRUEBA-HMM")])
                self.assertIn("Contract No (Paso 2): 'CT-PRUEBA-HMM'", log)

    def test_sin_una_que_calce_exacto_no_elige(self):
        # La lista vacía (lo medido), un contrato a medias (con «contiene», lo elegía), dos con el mismo código, o
        # una cuyo valor comparte otra: no elige nada, queda el del portal, y log.txt lo dice.
        sel = self.mod.HMM_LISTA_PASO2
        for k, (opciones, ctto, dice) in enumerate((
                ([], "CT-PRUEBA-HMM", "sin opción que calce exacto con el contrato (calzan 0 de 0)"),
                (self.OPCIONES, "CT-PRUEBA", "sin opción que calce exacto con el contrato (calzan 0 de 3)"),
                ([("CT-PRUEBA-HMM - (GA)", "A"), ("CT-PRUEBA-HMM - (FMC)", "B")], "CT-PRUEBA-HMM",
                 "sin opción que calce exacto con el contrato (calzan 2 de 2)"),
                ([("CT-PRUEBA-HMM - (FMC)", "CT-PRUEBA-HMM"), ("CT-PRUEBA-HMM - (GA)", "CT-PRUEBA-HMM")],
                 "CT-PRUEBA-HMM - (FMC)", "sin opción que se distinga (el mismo valor en 2 opciones)"),
                ([("Select", ""), ("CT-1", "ZZ"), ("CT-1 - (GA)", "CT-1")], "CT-1 - (GA)",
                 "sin opción que se distinga (el mismo valor en 2 opciones)"))):
            with self.subTest(k=k):
                p = PaginaPaso2(sel, opciones)
                r, log = self.paso2(p, f"paso2_no_elige_{k}", ctto)
                self.assertIs(r, False)
                self.assertEqual(p.hechos, [("lee",)])
                self.assertIn(f"Contract No (Paso 2): {dice}; queda el del portal", log)

    def test_si_falla_no_corta(self):
        # Si la lectura o la elección fallan, no elige y sigue: el paso 2 nunca corta (el contrato de la reserva lo
        # elige y lo comprueba el paso 3). El error va a log.txt saneado: un salto de línea no parte la línea.
        sel = self.mod.HMM_LISTA_PASO2
        p = PaginaPaso2(sel, self.OPCIONES, lee="no contestó" + chr(10) + "LINEA FALSA")
        r, log = self.paso2(p, "paso2_no_lee")
        self.assertIs(r, False)
        self.assertIn("Contract No (Paso 2): err lectura (no contestó LINEA FALSA); queda el del portal", log)
        p = PaginaPaso2(sel, self.OPCIONES, acepta=False)
        r, log = self.paso2(p, "paso2_no_acepta")
        self.assertIs(r, False)
        self.assertEqual(p.hechos, [("lee",), ("elige", sel, "CT-PRUEBA-HMM")])
        self.assertIn("Contract No (Paso 2): err select (el portal no la aceptó); queda el del portal", log)

    def test_lo_del_portal_va_saneado(self):
        sel = self.mod.HMM_LISTA_PASO2
        valor = "CT" + chr(0) + "1"
        p = PaginaPaso2(sel, [("Select", ""), ("CT" + chr(0) + "1 - (GA)", valor)])
        r, log = self.paso2(p, "paso2_saneado", "CT" + chr(0) + "1")
        self.assertIs(r, True)
        self.assertEqual(p.hechos, [("lee",), ("elige", sel, valor)])
        self.assertIn("Contract No (Paso 2): 'CT?1'", log)
        self.assertNotIn(chr(0), log)


class TestPlantilla(soporte.CasoAQ):
    def test_la_plantilla_no_trae_nombres(self):
        # Marcadores neutros en vez de personas: hasta 9710ae2, el primer operador llevaba un nombre
        # (CICLO-cola-cuatro-items.md). El nombre en pantalla de COSCO va vacío, como el usuario y la clave.
        plantilla = json.loads((soporte.FUENTES / "config.example.json").read_text(encoding="utf-8"))
        self.assertEqual(list(plantilla["usuarios"]), ["usuario1", "usuario2"])
        self.assertEqual([d["cosco"].get("nombre_en_pantalla") for d in plantilla["usuarios"].values()], ["", ""])


if __name__ == "__main__":
    unittest.main()
