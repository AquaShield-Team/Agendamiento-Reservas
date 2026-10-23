# -*- coding: utf-8 -*-
"""Después de la guarda del candado: el estado dice lo que el programa vio y cada envío deja
evidencia (CICLO-estado-tras-envio.md).

- EMITIDA solo con la confirmación y un número con la forma medida de la naviera.
- EMITIDA – CONFIRMAR POR CORREO (COSCO, desde el encargo 77, y CMA-CGM, desde el 78): se pulsó, sin errores ni
  fallas, y la pantalla dice que la reserva se envió (FORMA_ENVIADA), con su número; la confirmación llega por correo.
- ENVIADA – REVISAR EN PORTAL: se pulsó (o el clic pudo salir) y no hubo confirmación; desde el encargo 78, también
  con errores de validación y la confirmación o la frase de envío en la pantalla; y desde el 79, COSCO con errores de
  validación y su Submit ya no a la vista (o sin poder leerlo).
- NO ENVIADA: el botón no se pulsó, o el portal marcó errores de validación (con los campos) y, en COSCO, su Submit
  sigue a la vista; desde el encargo 80, a los 20 s del clic, sin que haya aparecido la ventana «Reminder» ni la
  página que dice que la reserva se envió.
- La evidencia: la captura y el HTML de la página y de cada marco, en la carpeta de la corrida.
- El panel lee cada estado con lecturaEstado (JavaScript, se corre en Node).

Páginas falsas y números inventados con la forma medida: ningún portal, captura ni HTML real.
"""
import ast
import itertools
import json
import re
import shutil
import unittest
from pathlib import Path
from unittest import mock

import soporte

P = soporte.PaginaFalsa
N = itertools.count()
CONFIRMA_ONE = "Your booking has been successfully submitted!\nBooking Reference No.\nSCLG23456789\n"
REVISA = "Revisa en el portal si la reserva quedó creada y, si está, anota su número en la planilla."


class Pantalla(P):
    """Página falsa que distingue el JavaScript que se le pide: el HTML completo (evidencia) o el
    texto visible (número). Cuenta las lecturas del texto; no sabe hacer clics ni navegar."""

    def __init__(self, texto="", html="<body>pantalla</body>", frames=None, contenido="<body>de playwright</body>",
                 url="https://portal.invalid/confirmacion"):
        super().__init__(texto, url=url, frames=frames)
        self.html, self.contenido, self.lecturas = html, contenido, 0

    def evaluate(self, js, *a):
        if "getHTML" in js:
            if isinstance(self.html, Exception):
                raise self.html
            return {"html": self.html(self) if callable(self.html) else self.html, "sombras": 0}
        self.lecturas += 1
        return self.texto(js, *a) if callable(self.texto) else self.texto

    def content(self):
        if isinstance(self.contenido, Exception):
            raise self.contenido
        return self.contenido


class ConRegistro(soporte.CasoAQ):
    def corrida(self):
        carpeta = self.sb / f"corrida_{next(N)}"
        return carpeta, self.mod.Registro(carpeta / "log.txt")


class TestResultadoEnvio(ConRegistro):
    def envio(self, pagina, naviera="one", nombre="ONE", pulsado=True, boton="Submit", **kw):
        carpeta, reg = self.corrida()
        try:
            r = self.mod._resultado_envio(pagina, reg, naviera, nombre, "nav_f5_9_confirmado", boton, pulsado, **kw)
        finally:
            reg.cerrar()
        return r, carpeta, (carpeta / "log.txt").read_text(encoding="utf-8")

    def evidencia(self, carpeta):
        return sorted(p.name for p in carpeta.iterdir() if p.name != "log.txt")

    def test_emitida_solo_con_la_forma_medida(self):
        r, carpeta, log = self.envio(Pantalla(CONFIRMA_ONE))
        self.assertEqual(r, ("EMITIDA", "ONE emitida con éxito (Booking: SCLG23456789)"))
        self.assertIn("· 🎉 ONE: Reserva EMITIDA con éxito. Booking: SCLG23456789", log)
        self.assertEqual(self.evidencia(carpeta), ["nav_f5_9_confirmado.html", "nav_f5_9_confirmado.png"])

    def test_pulsado_sin_confirmacion_es_enviada(self):
        pagina = Pantalla("Booking Parties · Review Booking")
        r, carpeta, log = self.envio(pagina)
        detalle = ("ONE: se pulsó «Submit», pero la pantalla no mostró la confirmación con el número de reserva. "
                   + REVISA)
        self.assertEqual(r, ("ENVIADA – REVISAR EN PORTAL", detalle))
        self.assertIn(f"· ⚠ ENVIADA – REVISAR EN PORTAL · {detalle}", log)
        self.assertEqual(pagina.esperas, self.mod.BKG_ESPERA_SEG)          # esperó la confirmación
        self.assertEqual(self.evidencia(carpeta), ["nav_f5_9_confirmado.html", "nav_f5_9_confirmado.png"])

    def test_naviera_sin_forma_nunca_es_emitida(self):
        # CMA y COSCO no tienen forma medida de una confirmación: ni un número con forma de otra naviera las vuelve
        # EMITIDA. Desde el encargo 78, CMA tiene su frase de envío, y sin ella dice que la pantalla no la mostró.
        pagina = Pantalla(CONFIRMA_ONE + "Booking reference: CMAFALSO01")
        r, _, _ = self.envio(pagina, naviera="cma", nombre="CMA", boton="Enviar el booking")
        self.assertEqual(r, ("ENVIADA – REVISAR EN PORTAL",
                             "CMA: se pulsó «Enviar el booking», pero la pantalla no mostró que la reserva se enviara. "
                             + REVISA))
        self.assertEqual(pagina.esperas, self.mod.BKG_ESPERA_SEG)          # esperó la frase, como el número

    def test_no_pulsado_es_no_enviada(self):
        pagina = Pantalla(CONFIRMA_ONE)            # aunque la pantalla mostrara un número, no se lee
        r, carpeta, log = self.envio(pagina, pulsado=False)
        detalle = "ONE: no se pulsó «Submit» porque no estaba en la pantalla. La reserva no se envió."
        self.assertEqual(r, ("NO ENVIADA", detalle))
        self.assertIn(f"· ✗ NO ENVIADA · {detalle}", log)
        self.assertEqual((pagina.lecturas, pagina.esperas), (0, 0))
        self.assertEqual(self.evidencia(carpeta), ["nav_f5_9_confirmado.html", "nav_f5_9_confirmado.png"])

    def test_validacion_es_no_enviada_con_los_campos(self):
        pagina = Pantalla(CONFIRMA_ONE)
        r, _, log = self.envio(pagina, naviera="cosco", nombre="COSCO",
                               campos=["Gross Weight is required", "Temperature is required"])
        detalle = ("COSCO: el portal no aceptó el envío y marcó: «Gross Weight is required»; «Temperature is "
                   "required». La reserva no se envió; corrige esos datos y vuelve a correrla.")
        self.assertEqual(r, ("NO ENVIADA", detalle))
        self.assertIn(f"· ✗ NO ENVIADA · {detalle}", log)
        # Con errores de campo, la pantalla se lee una sola vez, sin esperar: sin la confirmación ni la frase de envío,
        # NO ENVIADA. Hasta el encargo 78 no se leía; con la confirmación a la vista, test_errores_de_campo_con_la_frase.
        pagina = Pantalla("Booking Details")
        r, _, _ = self.envio(pagina, campos=["Gross Weight is required"])
        self.assertEqual((r[0], pagina.lecturas, pagina.esperas), ("NO ENVIADA", 1, 0))
        muchos = [f"Campo {i} is required" for i in range(1, 13)]
        r, _, _ = self.envio(Pantalla(), naviera="cosco", nombre="COSCO", campos=muchos)
        self.assertIn("«Campo 10 is required» y 2 más. La reserva no se envió", r[1])
        self.assertNotIn("Campo 11", r[1])

    def test_error_del_portal_es_enviada(self):
        r, _, _ = self.envio(Pantalla(), naviera="cosco", nombre="COSCO", error_portal="Sistema ocupado")
        self.assertEqual(r, ("ENVIADA – REVISAR EN PORTAL",
                             "COSCO: se pulsó «Submit» y el portal mostró un error: «Sistema ocupado». " + REVISA))
        # Con una naviera medida y un número en pantalla, tampoco se lee: el portal mostró un error.
        pagina = Pantalla(CONFIRMA_ONE)
        r, _, _ = self.envio(pagina, error_portal="Sistema ocupado")
        self.assertEqual((r[0], pagina.lecturas), ("ENVIADA – REVISAR EN PORTAL", 0))

    def test_falla_del_programa_despues_de_pulsar(self):
        r, _, log = self.envio(Pantalla("cargando"), error=RuntimeError("se cerró\n la página"))
        self.assertEqual(r, ("ENVIADA – REVISAR EN PORTAL",
                             "ONE: se pulsó «Submit», pero después el programa falló (RuntimeError: se cerró la "
                             "página). " + REVISA))
        self.assertIn("falla del programa durante el envío: RuntimeError: se cerró la página", log)

    def test_falla_al_pulsar_pudo_salir(self):
        r, _, _ = self.envio(Pantalla("cargando"), pulsado=None, error=TimeoutError("30000 ms"))
        self.assertEqual(r, ("ENVIADA – REVISAR EN PORTAL",
                             "ONE: el programa falló al pulsar «Submit» (TimeoutError: 30000 ms) y el clic pudo "
                             "haber salido. " + REVISA))

    def test_falla_pero_la_confirmacion_esta(self):
        for pulsado in (True, None):
            with self.subTest(pulsado=pulsado):
                r, _, _ = self.envio(Pantalla(CONFIRMA_ONE), pulsado=pulsado, error=RuntimeError("x"))
                self.assertEqual(r, ("EMITIDA", "ONE emitida con éxito (Booking: SCLG23456789)"))

    def test_evidencia_despues_de_leer(self):
        # La evidencia muestra la pantalla sobre la que se decidió: la de después de esperar el número.
        pagina = Pantalla(lambda js, *a: CONFIRMA_ONE if pagina.lecturas >= 4 else "cargando",
                          html=lambda p: f"<p>lecturas={p.lecturas}</p>")
        r, carpeta, _ = self.envio(pagina)
        self.assertEqual(r[0], "EMITIDA")
        self.assertIn("<p>lecturas=4</p>", (carpeta / "nav_f5_9_confirmado.html").read_text(encoding="utf-8"))

    def cosco(self, pagina, **kw):
        return self.envio(pagina, naviera="cosco", nombre="COSCO", **kw)

    def test_cosco_enviada_con_su_frase_es_emitida_por_correo(self):
        # Decisión de Marcelo, encargo 77: COSCO manda el número por correo. Su página tras el envío dice, en el marco
        # del formulario, que la reserva se envió (la forma medida el 22-10): sin errores, EMITIDA – CONFIRMAR POR CORREO,
        # nunca EMITIDA. Hasta ahí, ENVIADA – REVISAR EN PORTAL. Una referencia inventada, con las cifras a la vista.
        pagina = Pantalla("New Booking · Booking Request · Templates",
                          frames=[Marco("nada"), Marco(COSCO_ENVIADA)])
        r, carpeta, log = self.cosco(pagina)
        detalle = ("COSCO: se pulsó «Submit» y la página dijo que la reserva se envió (Booking: CD1234567890). Falta su "
                   "confirmación: revisa que llegue por correo, con ese número.")
        self.assertEqual(r, ("EMITIDA – CONFIRMAR POR CORREO", detalle))
        self.assertEqual(self.mod.EMITIDA_POR_CORREO, "EMITIDA – CONFIRMAR POR CORREO")
        self.assertIn(f"· ✅ EMITIDA – CONFIRMAR POR CORREO · {detalle}", log)
        # El registro del panel la pinta como las emitidas, no como una alerta (clase, en JS_INDEX).
        self.assertEqual(clases(self, [l for l in log.splitlines() if "CONFIRMAR POR CORREO" in l]), [["f-ok", "OK"]])
        self.assertEqual(pagina.esperas, 0)                                 # la frase ya estaba
        self.assertEqual(self.evidencia(carpeta), ["nav_f5_9_confirmado.html", "nav_f5_9_confirmado.png",
                                                   "nav_f5_9_confirmado_marco1.html", "nav_f5_9_confirmado_marco2.html"])
        # La columna del número: la referencia es el número, que COSCO confirma en su correo (decisión de Marcelo,
        # encargo 78). Hasta ahí, decía «confirmar por correo».
        res = {"estado": r[0], "detalle": r[1]}
        self.assertEqual((self.mod._texto_n_reserva(res), self.mod._extraer_bkg_limpio(res)),
                         ("CD1234567890", "CD1234567890"))

    def test_cma_con_booking_enviado_es_emitida_por_correo(self):
        # Decisión de Marcelo, encargo 78: la reserva de CMA-CGM que su página da por enviada y «aún no confirmada»
        # queda EMITIDA – CONFIRMAR POR CORREO, con su número. Las dos señales, como se leyó el 22-10 y en ese orden: el
        # título «Booking enviado» al final de su línea, y después una línea con «Booking» y la referencia sola. Una
        # referencia inventada, a la vista.
        r, _, log = self.envio(Pantalla(CMA_ENVIADA), naviera="cma", nombre="CMA", boton="Enviar el booking")
        detalle = ("CMA: se pulsó «Enviar el booking» y la página dijo que la reserva se envió (Booking: QXZ1234567). "
                   "Falta su confirmación: revisa que llegue por correo, con ese número.")
        self.assertEqual(r, ("EMITIDA – CONFIRMAR POR CORREO", detalle))
        res = {"estado": r[0], "detalle": r[1]}
        self.assertEqual(self.mod._texto_n_reserva(res), "QXZ1234567")
        # Sin una de las dos señales, con la referencia acompañada en su línea, con «Booking enviado» dentro de una
        # frase o con la referencia antes del título, no basta: ENVIADA – REVISAR EN PORTAL (lo último, de la revisión de
        # código del encargo 78).
        otras = {"sin «Booking enviado»": CMA_ENVIADA.replace("Booking enviado", "Booking en proceso"),
                 "la referencia con más texto": CMA_ENVIADA.replace("Booking QXZ1234567\n",
                                                                    "Booking QXZ1234567 Submitted\n"),
                 "otra forma": CMA_ENVIADA.replace("QXZ1234567", "QX1234567"),
                 "sin la línea de la referencia": CMA_ENVIADA.replace("Booking QXZ1234567\n", ""),
                 "«Booking enviado» en una frase": CMA_ENVIADA.replace("Booking enviado\n", "Su Booking enviado ayer\n"),
                 "la referencia antes del título": "Booking QXZ1234567\n" + CMA_ENVIADA.replace("Booking QXZ1234567\n",
                                                                                                 "")}
        for caso, texto in otras.items():
            with self.subTest(caso=caso):
                r, _, _ = self.envio(Pantalla(texto), naviera="cma", nombre="CMA", boton="Enviar el booking")
                self.assertEqual(r[0], "ENVIADA – REVISAR EN PORTAL")

    def test_dos_numeros_distintos_no_deciden(self):
        # Revisión de seguridad del encargo 78: si la pantalla dice que la reserva se envió y muestra más de una
        # referencia distinta con la forma de la naviera, no se sabe cuál es la de esta: ENVIADA – REVISAR EN PORTAL, con
        # todas, y sin número en la columna. Hasta ahí ganaba la primera. Referencias inventadas, a la vista.
        r, _, log = self.envio(Pantalla(CMA_ENVIADA + "Booking ABC0000000\n"), naviera="cma", nombre="CMA",
                               boton="Enviar el booking")
        detalle = ("CMA: se pulsó «Enviar el booking» y la página dijo que la reserva se envió, pero mostró 2 números "
                   "distintos (ABC0000000, QXZ1234567): no se sabe cuál es el de esta reserva. " + REVISA)
        self.assertEqual(r, ("ENVIADA – REVISAR EN PORTAL", detalle))
        self.assertIn(f"· ⚠ ENVIADA – REVISAR EN PORTAL · {detalle}", log)
        self.assertEqual(self.mod._texto_n_reserva({"estado": r[0], "detalle": r[1]}), "")
        casos = {"la otra en un marco": (Pantalla(CMA_ENVIADA, frames=[Marco("Booking ABC0000000")]), "cma", "CMA"),
                 "dos frases de COSCO": (Pantalla(COSCO_ENVIADA + "\nBooking CD0000000000 has been submitted "
                                                  "successfully!"), "cosco", "COSCO")}
        for caso, (pagina, naviera, nombre) in casos.items():
            with self.subTest(caso=caso):
                r, _, _ = self.envio(pagina, naviera=naviera, nombre=nombre)
                self.assertEqual(r[0], "ENVIADA – REVISAR EN PORTAL")
        # La misma referencia dos veces (en la página y en un marco) no es ambigua.
        r, _, _ = self.envio(Pantalla(CMA_ENVIADA, frames=[Marco(CMA_ENVIADA)]), naviera="cma", nombre="CMA")
        self.assertEqual(r[0], "EMITIDA – CONFIRMAR POR CORREO")
        # Con errores de campo, las dos se contradicen con los errores: también ENVIADA – REVISAR EN PORTAL.
        r, _, _ = self.cosco(Pantalla(COSCO_ENVIADA + "\nBooking CD0000000000 has been submitted successfully!"),
                             campos=["Gross Weight is required"])
        self.assertEqual(r[0], "ENVIADA – REVISAR EN PORTAL")
        self.assertIn("(Booking: CD0000000000, CD1234567890)", r[1])

    def test_el_mismo_numero_dos_veces_en_la_corrida(self):
        # Revisión de seguridad del encargo 78: la pantalla de una reserva anterior que sigue a la vista daría su número a
        # la reserva siguiente. Si una referencia ya dio una EMITIDA – CONFIRMAR POR CORREO en esta corrida (el mismo
        # Registro), la segunda vez queda ENVIADA – REVISAR EN PORTAL. Otra referencia, u otra corrida, como siempre.
        carpeta, reg = self.corrida()
        otra = "Booking CD0000000000 has been submitted successfully!"
        try:
            r = [self.mod._resultado_envio(Pantalla(texto), reg, "cosco", "COSCO", f"cosco_f{f}_6_confirmado", "Submit",
                                           True) for f, texto in ((5, COSCO_ENVIADA), (6, COSCO_ENVIADA), (7, otra))]
        finally:
            reg.cerrar()
        self.assertEqual([x[0] for x in r], ["EMITIDA – CONFIRMAR POR CORREO", "ENVIADA – REVISAR EN PORTAL",
                                             "EMITIDA – CONFIRMAR POR CORREO"])
        self.assertEqual(r[1][1], "COSCO: se pulsó «Submit» y la página mostró el mismo número que otra reserva de esta "
                                  "corrida (Booking: CD1234567890, en cosco_f5_6_confirmado): puede ser la pantalla de esa "
                                  "reserva. " + REVISA)
        self.assertIn(f"· ⚠ ENVIADA – REVISAR EN PORTAL · {r[1][1]}", (carpeta / "log.txt").read_text(encoding="utf-8"))
        r, _, _ = self.cosco(Pantalla(COSCO_ENVIADA))
        self.assertEqual(r[0], "EMITIDA – CONFIRMAR POR CORREO")

    def test_errores_de_campo_con_la_frase_son_enviada(self):
        # Decisión de Marcelo, encargo 78: errores de campo y, a la vez, la frase de envío (o el número) en la pantalla
        # se contradicen: ENVIADA – REVISAR EN PORTAL, no NO ENVIADA, que invitaría a repetirla. Una sola lectura, sin
        # espera.
        pagina = Pantalla(COSCO_ENVIADA)
        r, _, log = self.cosco(pagina, campos=["Gross Weight is required"])
        detalle = ("COSCO: se pulsó «Submit»; el portal marcó: «Gross Weight is required», y la página dijo que la "
                   "reserva se envió (Booking: CD1234567890). Las dos señales se contradicen. " + REVISA)
        self.assertEqual(r, ("ENVIADA – REVISAR EN PORTAL", detalle))
        self.assertIn(f"· ⚠ ENVIADA – REVISAR EN PORTAL · {detalle}", log)
        self.assertEqual(pagina.esperas, 0)
        # Sin la frase, como antes: NO ENVIADA, también sin esperarla.
        pagina = Pantalla("Booking Details")
        r, _, _ = self.cosco(pagina, campos=["Gross Weight is required"])
        self.assertEqual((r[0], pagina.esperas), ("NO ENVIADA", 0))
        # Si la página no se deja leer, tampoco se sabe que se envió: NO ENVIADA, como antes.
        class Rompe(Pantalla):
            def evaluate(self, js, *a):
                if "getHTML" in js:
                    return super().evaluate(js, *a)
                raise RuntimeError("marco cerrado")
        r, _, _ = self.cosco(Rompe(COSCO_ENVIADA), campos=["Gross Weight is required"])
        self.assertEqual(r[0], "NO ENVIADA")
        # Y si la lectura misma falla, igual, y log.txt lo dice.
        def falla(*a, **kw):
            raise RuntimeError("se cerró")
        with mock.patch.object(self.mod, "numero_tras_envio", falla):
            r, _, log = self.cosco(Pantalla(COSCO_ENVIADA), campos=["Gross Weight is required"])
        self.assertEqual(r[0], "NO ENVIADA")
        self.assertIn("no pude leer la pantalla para ver si dice que la reserva se envió: RuntimeError: se cerró", log)
        # Una naviera con número y sin frase: el número también contradice los errores.
        r, _, _ = self.envio(Pantalla(CONFIRMA_ONE), campos=["Gross Weight is required"])
        self.assertEqual(r[0], "ENVIADA – REVISAR EN PORTAL")
        # Con el clic a medio dar (el programa falló al pulsar y pudo salir), también se lee (revisión de código).
        r, _, _ = self.cosco(Pantalla(COSCO_ENVIADA), pulsado=None, error=TimeoutError("30000 ms"),
                             campos=["Gross Weight is required"])
        self.assertEqual(r[0], "ENVIADA – REVISAR EN PORTAL")
        # Si no se pulsó, no se lee: NO ENVIADA (no estaba el botón).
        pagina = Pantalla(COSCO_ENVIADA)
        r, _, _ = self.cosco(pagina, pulsado=False, campos=["Gross Weight is required"])
        self.assertEqual((r[0], pagina.lecturas), ("NO ENVIADA", 0))

    def test_errores_de_campo_y_el_submit(self):
        # Decisión de Marcelo, encargo 79: con errores de campo tras el Submit de COSCO, NO ENVIADA solo si el Submit
        # sigue a la vista. Si ya no está, o no se pudo leer, el envío pudo haber entrado: ENVIADA – REVISAR EN PORTAL,
        # con un motivo que lo dice (NO ENVIADA invita a reenviar la fila, y si COSCO aceptó el envío después, la
        # reserva queda duplicada). Los tres casos, por el ayudante y por _resultado_envio, como los encadena
        # reservar_cosco (test_cosco_decide_con_lo_que_vio).
        mod = self.mod
        SUBMIT, REMINDER = mod._JS_COSCO_SUBMIT_PRESENTE, mod._JS_COSCO_HAY_REMINDER

        class Alcance:
            """El marco del formulario o la página: contesta si la ventana «Reminder» está a la vista y, el marco, si el
            Submit sigue a la vista; anota lo que se le pregunta. Cualquier otro JavaScript hace caer la prueba."""
            def __init__(self, submit=None, reminder=False):
                self.submit, self.reminder, self.preguntas = submit, reminder, []

            def evaluate(self, js, *a):
                self.preguntas.append("submit" if js == SUBMIT else "reminder" if js == REMINDER else "otro")
                r = self.submit if js == SUBMIT else self.reminder
                if isinstance(r, Exception):
                    raise r
                return r

        def en_duda(submit, reminder=False):
            marco, pagina = Alcance(submit=submit, reminder=reminder), Alcance()
            carpeta, reg = self.corrida()
            try:
                motivo = mod._cosco_submit_en_duda(marco, pagina, reg)
            finally:
                reg.cerrar()
            return motivo, marco.preguntas + pagina.preguntas, (carpeta / "log.txt").read_text(encoding="utf-8")

        campos = ["Gross Weight is required"]
        revisa = lambda porque: ("COSCO: se pulsó «Submit» y el portal marcó: «Gross Weight is required», pero " + porque
                                 + ": el envío pudo haber entrado. " + REVISA + " Si no está, corrige esos datos y vuelve "
                                 "a correrla.")
        casos = {"a la vista": (True, "NO ENVIADA", "COSCO: el portal no aceptó el envío y marcó: «Gross Weight is "
                                "required». La reserva no se envió; corrige esos datos y vuelve a correrla."),
                 "ya no está": (False, "ENVIADA – REVISAR EN PORTAL", revisa("«Submit» ya no está a la vista")),
                 "la lectura falla": (RuntimeError("marco cerrado"), "ENVIADA – REVISAR EN PORTAL",
                                      revisa("no se pudo leer si «Submit» sigue a la vista"))}
        for caso, (respuesta, estado, detalle) in casos.items():
            with self.subTest(caso=caso):
                motivo, preguntas, log_ayudante = en_duda(respuesta)
                # Primero si la ventana «Reminder» está (el marco y la página), después el Submit (solo el marco).
                self.assertEqual(preguntas, ["reminder", "submit", "reminder"])
                r, _, log = self.cosco(Pantalla("Booking Details"), campos=campos, campos_en_duda=motivo)
                self.assertEqual(r, (estado, detalle))
                self.assertIn(("· ⚠ " if estado != "NO ENVIADA" else "· ✗ ") + f"{estado} · {detalle}", log)
                if isinstance(respuesta, Exception):
                    self.assertIn("no pude leer si el Submit de COSCO sigue a la vista: RuntimeError: marco cerrado",
                                  log_ayudante)
        # Una respuesta que no es True ni False (la lectura no dijo si sigue) tampoco basta para NO ENVIADA, y log.txt
        # dice qué dio (revisión de código del encargo 79).
        for x in (None, "true", 1):
            with self.subTest(respuesta=x):
                motivo, _, log_ayudante = en_duda(x)
                self.assertEqual(motivo, "no se pudo leer si «Submit» sigue a la vista")
                self.assertIn("la lectura del Submit de COSCO no dijo si sigue a la vista: dio un "
                              + type(x).__name__, log_ayudante)
        # Con la ventana «Reminder» a la vista, en el marco o en la página, no se mira el Submit: su propio Submit se
        # leería como el del formulario (revisión de código del encargo 79).
        motivo, preguntas, _ = en_duda(True, reminder=True)
        self.assertEqual((motivo, preguntas), ("la ventana «Reminder» está a la vista", ["reminder"]))
        marco, pagina = Alcance(submit=True), Alcance(reminder=True)
        carpeta, reg = self.corrida()
        try:
            self.assertEqual(mod._cosco_submit_en_duda(marco, pagina, reg), "la ventana «Reminder» está a la vista")
        finally:
            reg.cerrar()
        # Con la frase de envío a la vista, el motivo es la contradicción del encargo 78, que dice más.
        r, _, _ = self.cosco(Pantalla(COSCO_ENVIADA), campos=campos, campos_en_duda="«Submit» ya no está a la vista")
        self.assertEqual(r[0], "ENVIADA – REVISAR EN PORTAL")
        self.assertIn("Las dos señales se contradicen", r[1])
        # FRENA SI del encargo: sin errores de campo, nada cambia (EMITIDA – CONFIRMAR POR CORREO con la frase).
        r, _, _ = self.cosco(Pantalla(COSCO_ENVIADA), campos_en_duda="«Submit» ya no está a la vista")
        self.assertEqual(r[0], "EMITIDA – CONFIRMAR POR CORREO")

    def test_cosco_sin_su_frase_sigue_enviada(self):
        pagina = Pantalla("New Booking · Booking Details · Submit")
        r, _, log = self.cosco(pagina)
        detalle = "COSCO: se pulsó «Submit», pero la pantalla no mostró que la reserva se enviara. " + REVISA
        self.assertEqual(r, ("ENVIADA – REVISAR EN PORTAL", detalle))
        self.assertIn(f"· ⚠ ENVIADA – REVISAR EN PORTAL · {detalle}", log)
        self.assertEqual(pagina.esperas, self.mod.BKG_ESPERA_SEG)          # esperó la frase, como el número

    def test_cosco_con_cualquier_duda_sigue_enviada(self):
        # Ante cualquier duda, ENVIADA – REVISAR EN PORTAL (encargo 77): el clic que pudo no salir, una falla del
        # programa después de pulsar, o un error del portal, aunque la frase esté; y desde el encargo 78, también con
        # errores de validación (test_errores_de_campo_con_la_frase_son_enviada).
        casos = {"falla al pulsar": dict(pulsado=None, error=TimeoutError("30000 ms")),
                 "clic sin respuesta": dict(pulsado=None),
                 "falla después": dict(error=RuntimeError("se cerró")),
                 "error del portal": dict(error_portal="Sistema ocupado")}
        for caso, kw in casos.items():
            with self.subTest(caso=caso):
                r, _, _ = self.cosco(Pantalla(COSCO_ENVIADA), **kw)
                self.assertEqual(r[0], "ENVIADA – REVISAR EN PORTAL")

    def test_cosco_solo_con_la_forma_medida(self):
        # La frase, con la referencia de la forma medida: «Booking», «CD» y 10 cifras, y «has been submitted
        # successfully». Otra forma, o solo una parte, no basta: ENVIADA – REVISAR EN PORTAL.
        otras = ["Booking CD123456789 has been submitted successfully!",       # 9 cifras
                 "Booking CD12345678901 has been submitted successfully!",     # 11 cifras
                 "Booking cd1234567890 has been submitted successfully!",      # la referencia distingue mayúsculas
                 "Booking XD1234567890 has been submitted successfully!",      # otro prefijo
                 "CD1234567890 has been submitted successfully!",              # sin «Booking»
                 "Booking CD1234567890 has been submitted",                    # sin «successfully»
                 "Booking CD1234567890 · Please check booking status",
                 "BookingCD1234567890 has been submitted successfully!",       # «Booking» pegado a la referencia
                 "Booking CD1234567890 has been submitted successfullyX",      # una letra pegada al final
                 # De la revisión de seguridad: otra palabra que termina en «Booking», un salto de línea, y la «ſ»
                 # (s larga), que el plegado de Unicode tomaría por una «s».
                 "Rebooking CD1234567890 has been submitted successfully!",
                 "Pre-Booking CD1234567890 has been submitted successfully!",
                 "Booking\nCD1234567890 has been submitted successfully!",
                 "Booking CD1234567890 has been submitted " + chr(0x17F) + "uccessfully!"]
        for texto in otras:
            with self.subTest(texto=texto):
                r, _, _ = self.cosco(Pantalla(texto))
                self.assertEqual(r[0], "ENVIADA – REVISAR EN PORTAL")
        r, _, _ = self.cosco(Pantalla("booking CD1234567890 HAS BEEN SUBMITTED SUCCESSFULLY!"))   # las palabras, en
        self.assertEqual(r[0], "EMITIDA – CONFIRMAR POR CORREO")                                # cualquier caja

    def test_la_lectura_que_falla_tras_pulsar_es_enviada(self):
        # Con el clic ya dado, una lectura que falla (el navegador que cierra «Detener» en medio de la espera del número
        # o de la frase) es una falla del programa después de pulsar: ENVIADA – REVISAR EN PORTAL. Hasta la revisión de
        # seguridad del encargo 77, la excepción salía del reservador y la fila quedaba DETENIDO o ERROR, con el envío
        # ya hecho (en COSCO, desde que tiene frase, también en esos 15 s).
        class SeCierra(Pantalla):
            def wait_for_timeout(self, ms):
                raise RuntimeError("Target page, context or browser has been closed")
        for naviera, nombre in (("cosco", "COSCO"), ("one", "ONE")):
            with self.subTest(naviera=naviera):
                r, carpeta, log = self.envio(SeCierra("Booking Details"), naviera=naviera, nombre=nombre)
                self.assertEqual(r, ("ENVIADA – REVISAR EN PORTAL",
                                     f"{nombre}: se pulsó «Submit», pero después el programa falló (RuntimeError: "
                                     "Target page, context or browser has been closed). " + REVISA))
                self.assertIn("falla del programa al leer la pantalla después del envío: RuntimeError: Target page", log)
                self.assertEqual(self.evidencia(carpeta), ["nav_f5_9_confirmado.html", "nav_f5_9_confirmado.png"])

    def test_la_frase_de_cosco_no_vale_en_otra_naviera(self):
        for naviera, nombre in (("one", "ONE"), ("maersk", "MAERSK")):
            with self.subTest(naviera=naviera):
                r, _, _ = self.envio(Pantalla(COSCO_ENVIADA), naviera=naviera, nombre=nombre)
                self.assertEqual(r[0], "ENVIADA – REVISAR EN PORTAL")


COSCO_ENVIADA = ('Booking CD1234567890 has been submitted successfully! Please check booking status in the "To do list".\n'
                 "Copy to Create New")
# Lo que muestra la página de CMA-CGM tras «Enviar el booking», como lo leyó el JavaScript del programa el 22-10, con
# las palabras del portal y una referencia inventada (tres letras y 7 cifras seguidas).
CMA_ENVIADA = ("Booking enviado\n"
               "Su reserva aún no está confirmada. Le avisaremos una vez que la hayamos confirmado.\n"
               "Booking QXZ1234567\n"
               "Buque\nRef. de viaje\n")


class Marco(Pantalla):
    """Un marco de la página: se guarda igual que la página."""


class TestEvidencia(ConRegistro):
    def guardar(self, pagina):
        carpeta, reg = self.corrida()
        try:
            self.mod._guardar_evidencia(pagina, reg, "cosco_f5_6_confirmado")
        finally:
            reg.cerrar()
        return carpeta, (carpeta / "log.txt").read_text(encoding="utf-8")

    def leer(self, carpeta, nombre):
        return (carpeta / nombre).read_text(encoding="utf-8")

    def test_captura_y_html_de_la_pagina_y_los_marcos(self):
        pagina = Pantalla(html="<body>principal</body>",
                          frames=[Marco(html="<body>uno</body>", url="https://portal.invalid/m1"),
                                  Marco(html="<body>dos</body>", url="https://portal.invalid/m2")])
        carpeta, log = self.guardar(pagina)
        self.assertEqual(sorted(p.name for p in carpeta.iterdir()),
                         ["cosco_f5_6_confirmado.html", "cosco_f5_6_confirmado.png", "cosco_f5_6_confirmado_marco1.html",
                          "cosco_f5_6_confirmado_marco2.html", "log.txt"])
        self.assertEqual(self.leer(carpeta, "cosco_f5_6_confirmado.html"),
                         "<!-- página · https://portal.invalid/confirmacion -->\n<body>principal</body>")
        self.assertEqual(self.leer(carpeta, "cosco_f5_6_confirmado_marco2.html"),
                         "<!-- marco 2 · https://portal.invalid/m2 -->\n<body>dos</body>")
        self.assertEqual(pagina.capturas, [("cosco_f5_6_confirmado.png", False)])   # la ventana, no la página entera
        self.assertIn("evidencia del envío: cosco_f5_6_confirmado.png y 3 de 3 HTML (la página y 2 marco(s); "
                      "0 sin raíces shadow)", log)

    def test_sin_javascript_usa_el_html_de_playwright(self):
        carpeta, log = self.guardar(Pantalla(frames=[Marco(html=RuntimeError("marco sin permiso"))]))
        self.assertEqual(self.leer(carpeta, "cosco_f5_6_confirmado_marco1.html"),
                         "<!-- marco 1 · https://portal.invalid/confirmacion -->\n<body>de playwright</body>")
        self.assertIn("2 de 2 HTML (la página y 1 marco(s); 1 sin raíces shadow)", log)

    def test_un_html_que_falla_se_avisa_y_no_tapa_a_los_demas(self):
        roto = Marco(html=RuntimeError("marco cerrado"), contenido=RuntimeError("marco cerrado"))
        carpeta, log = self.guardar(Pantalla(frames=[roto, Marco(html="<body>dos</body>")]))
        self.assertIn("· ⚠ No pude guardar el HTML del marco 1 tras el envío: RuntimeError: marco cerrado", log)
        self.assertFalse((carpeta / "cosco_f5_6_confirmado_marco1.html").exists())
        self.assertIn("<body>dos</body>", self.leer(carpeta, "cosco_f5_6_confirmado_marco2.html"))
        self.assertIn("2 de 3 HTML", log)

    def test_no_repite_el_marco_principal(self):
        # En Playwright, page.frames empieza con el marco principal, que es la misma página.
        pagina = Pantalla(html="<body>principal</body>", frames=[Marco(html="<body>principal</body>"),
                                                                 Marco(html="<body>hijo</body>")])
        pagina.main_frame = pagina.frames[0]
        carpeta, log = self.guardar(pagina)
        self.assertIn("<body>hijo</body>", self.leer(carpeta, "cosco_f5_6_confirmado_marco1.html"))
        self.assertFalse((carpeta / "cosco_f5_6_confirmado_marco2.html").exists())
        self.assertIn("2 de 2 HTML (la página y 1 marco(s)", log)

    def test_el_javascript_trae_las_raices_shadow(self):
        # El JavaScript no corre offline: se fija su forma. Solo lee (ni clics ni navegación).
        js = self.mod._JS_HTML_COMPLETO
        self.assertIn("if (e.shadowRoot) { raices.push(e.shadowRoot); visitar(e.shadowRoot); }", js)
        self.assertIn("html.getHTML({shadowRoots: raices})", js)
        for accion in ("click(", "location", "submit(", "dispatchEvent"):
            self.assertNotIn(accion, js)


class Boton:
    def __init__(self, hay, visible):
        self.hay, self.visible, self.clics = hay, visible, 0

    def count(self):
        return self.hay

    def is_visible(self):
        return self.visible

    def click(self):
        self.clics += 1


class Alcance:
    def __init__(self, boton, js_pulsa=False):
        self.boton, self.js_pulsa, self.selectores, self.js = boton, js_pulsa, [], []

    def locator(self, selector):
        self.selectores.append(selector)
        return type("Loc", (), {"first": self.boton})()

    def evaluate(self, js, *a):
        self.js.append((js,) + a)
        return self.js_pulsa


class TestPulsarBoton(soporte.CasoAQ):
    def test_pulsa_el_boton_visible(self):
        a = Alcance(Boton(1, True), js_pulsa=True)
        self.assertIs(self.mod._pulsar_boton(a, "button:has-text('Submit')", "JS", "^submit$"), True)
        self.assertEqual((a.boton.clics, a.selectores, a.js), (1, ["button:has-text('Submit')"], []))

    def test_sin_boton_visible_usa_el_javascript(self):
        for hay, visible in ((0, False), (1, False)):
            for pulsa in (True, False):
                with self.subTest(hay=hay, pulsa=pulsa):
                    a = Alcance(Boton(hay, visible), js_pulsa=pulsa)
                    self.assertIs(self.mod._pulsar_boton(a, "sel", "JS", "^submit$"), pulsa)
                    self.assertEqual((a.boton.clics, a.js), (0, [("JS", "^submit$")]))
        a = Alcance(Boton(0, False), js_pulsa=1)
        self.assertIs(self.mod._pulsar_boton(a, "sel", "JS"), True)
        self.assertEqual(a.js, [("JS",)])

    def test_sin_boton_ni_javascript_no_pulsa(self):
        a = Alcance(Boton(1, False), js_pulsa=True)
        self.assertIs(self.mod._pulsar_boton(a, "sel"), False)
        self.assertEqual((a.boton.clics, a.js), (0, []))


def tras_la_guarda(mod, nombre, tree=None):
    """Sentencias que corren después de la guarda del candado en el reservador 'nombre': la rama
    else de la guarda o, si no tiene, lo que la sigue en su bloque."""
    tree = tree or ast.parse(Path(mod.__file__).read_text(encoding="utf-8"))
    f = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == nombre)
    for padre in ast.walk(f):
        for campo in ("body", "orelse"):
            cuerpo = getattr(padre, campo, None)
            for i, s in enumerate(cuerpo if isinstance(cuerpo, list) else []):
                if isinstance(s, ast.If) and ast.unparse(s.test) == "not es_modo_emision()":
                    return s.orelse or cuerpo[i + 1:]
    raise AssertionError(f"{nombre}: no encontré la guarda del candado")


def normal(fuente):
    return ast.unparse(ast.parse(fuente))


def despues_de_la_guarda(mod, nombre):
    """Lo que corre el reservador 'nombre' después de la guarda del candado (tras_la_guarda), compilado aparte como una
    función de page, frame, reg y f, con las variables del programa: el código real, sin copiarlo (en el censo, el
    mutado). Así una prueba lo corre de punta a punta, del clic al estado, sobre un portal falso (encargo 80)."""
    tree = ast.parse(Path(mod.__file__).read_text(encoding="utf-8"))
    funcion = ast.parse("def despues(page, frame, reg, f):\n    pass").body[0]
    funcion.body = tras_la_guarda(mod, nombre, tree)
    modulo = ast.fix_missing_locations(ast.Module(body=[funcion], type_ignores=[]))
    espacio = dict(vars(mod))
    exec(compile(modulo, mod.__file__, "exec"), espacio)
    return espacio["despues"]


class TestReservadores(soporte.CasoAQ):
    """Después de la guarda, cada reservador pulsa el MISMO botón de antes (sin clics nuevos),
    guarda el error si algo falla y decide con _resultado_envio. El flujo en el portal no corre
    offline: se fija su forma. Lo de antes de la guarda lo vigila test_candado."""
    PROHIBIDOS = ("extraer_numero_booking", "_emitida(", "'EMITIDA'", "Consultar portal", "en proceso", "Ver captura",
                  "Pendiente", "reg.captura(")

    def envio(self, nombre, pulsar, resultado):
        post = tras_la_guarda(self.mod, nombre)
        fuente = "\n".join(ast.unparse(s) for s in post)
        self.assertIn("pulsado, error = (None, None)", fuente)
        intentos = [s for s in post if isinstance(s, ast.Try)]
        self.assertEqual(len(intentos), 1, f"{nombre}: se esperaba un solo try después de la guarda")
        asignaciones = [ast.unparse(n) for n in ast.walk(intentos[0]) if isinstance(n, ast.Assign)]
        self.assertIn(normal(f"pulsado = {pulsar}"), asignaciones)
        self.assertEqual([(ast.unparse(h.type), h.name, [ast.unparse(b) for b in h.body]) for h in intentos[0].handlers],
                         [("Exception", "e", ["error = e"])])
        self.assertEqual(ast.unparse(post[-1]), normal(f"return {resultado}"))
        for prohibido in self.PROHIBIDOS:
            self.assertNotIn(prohibido, fuente)
        return post

    def test_one_decide_con_lo_que_vio(self):
        self.envio("reservar_one",
                   """_pulsar_boton(page, "button:has-text('Submit'), button:has-text('Enviar'), button[type='submit']",
                                    _JS_CLICK_BTN, "^(submit|enviar|submit booking)$")""",
                   """_resultado_envio(page, reg, "one", "ONE", f"one_f{f}_11_confirmado", "Submit", pulsado, error)""")

    def test_msc_decide_con_lo_que_vio(self):
        self.envio("reservar_msc",
                   """_pulsar_boton(page, "button:has-text('Submit'), button[type='submit']", _JS_CLICK_BTN, "^(submit|enviar)$")""",
                   """_resultado_envio(page, reg, "msc", "MSC", f"msc_f{f}_6_confirmado", "Submit", pulsado, error)""")

    def test_hyundai_decide_con_lo_que_vio(self):
        post = self.envio("reservar_hyundai",
                          """_pulsar_boton(page, "button:has-text('Create NOW'), .btn:has-text('Create NOW')")""",
                          """_resultado_envio(page, reg, "hyundai", "HYUNDAI", f"hmm_f{f}_6_confirmado", "Create NOW",
                                              pulsado, error)""")
        # La ventana de confirmación de HMM se acepta igual que antes y solo si se pulsó «Create NOW».
        modal = "#confirmBtn, button:has-text('Confirm'), button:has-text('Yes'), button:has-text('Aceptar')"
        si_pulso = [n for s in post for n in ast.walk(s) if isinstance(n, ast.If) and ast.unparse(n.test) == "pulsado"]
        self.assertEqual(len(si_pulso), 1)
        self.assertIn(modal, ast.unparse(si_pulso[0]))
        self.assertEqual(sum(ast.unparse(s).count(modal) for s in post), 1)

    def test_maersk_decide_con_lo_que_vio(self):
        self.envio("reservar_maersk",
                   """_pulsar_boton(page, "button:has-text('Submit booking'), button:has-text('Book now')")""",
                   """_resultado_envio(page, reg, "maersk", "MAERSK", f"mk_f{f}_7_confirmado", "Submit booking",
                                       pulsado, error)""")

    def test_cma_decide_con_lo_que_vio(self):
        self.envio("reservar_cma",
                   """_pulsar_boton(page, "button:has-text('Enviar el booking'), button:has-text('Send booking'), "
                                          "button:has-text('Submit booking')", plazo_ms=CMA_PLAZO_MS)""",
                   """_resultado_envio(page, reg, "cma", "CMA", f"cma_f{f}_6_confirmado", "Enviar el booking", pulsado,
                                       error, plazo_ms=CMA_PLAZO_MS)""")
        self.assertNotIn("cma", self.mod.FORMA_BOOKING)       # sin forma medida: nunca EMITIDA

    def test_cosco_decide_con_lo_que_vio(self):
        post = self.envio("reservar_cosco",
                          """_pulsar_boton(frame, "button:has-text('Submit'), .btn:has-text('Submit')", _JS_COSCO_SUBMIT)""",
                          """_resultado_envio(page, reg, "cosco", "COSCO", f"cosco_f{f}_6_confirmado", "Submit", pulsado,
                                              error, campos=campos, error_portal=error_portal, campos_en_duda=en_duda)""")
        condicionales = [ast.unparse(n) for s in post for n in ast.walk(s) if isinstance(n, ast.If)]
        # Solo espera el resultado si pulsó; con la ventana Reminder ya vista, los errores de campo
        # no bastan para NO ENVIADA: van como error del portal (ENVIADA – REVISAR EN PORTAL).
        self.assertIn(normal("if pulsado:\n    campos, error_portal, vio_reminder = "
                             "_cosco_esperar_resultado(page, frame, reg)"), condicionales)
        self.assertIn(normal("if campos and vio_reminder:\n"
                             "    error_portal = '; '.join(campos + ([error_portal] if error_portal else []))\n"
                             "    campos = []"), condicionales)
        # Desde el encargo 79, con errores de campo mira si el Submit sigue a la vista, y solo entonces (el camino sin
        # errores de campo no lo mira).
        self.assertEqual(ast.unparse(post[-2]), "en_duda = _cosco_submit_en_duda(frame, page, reg) if campos else ''")
        self.assertNotIn("cosco", self.mod.FORMA_BOOKING)     # sin forma medida: nunca EMITIDA a secas (desde el
                                                              # encargo 77, EMITIDA – CONFIRMAR POR CORREO, con su frase)

    def test_la_evidencia_y_el_estado_solo_despues_de_la_guarda(self):
        # FRENA del encargo: guardar la evidencia no puede cambiar el flujo antes de la guarda.
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        despues = {nombre: {id(n) for s in tras_la_guarda(self.mod, nombre, tree) for n in ast.walk(s)}
                   for nombre in ("reservar_one", "reservar_msc", "reservar_cma", "reservar_cosco",
                                  "reservar_hyundai", "reservar_maersk")}
        llamadas = {}
        for f in (n for n in tree.body if isinstance(n, ast.FunctionDef)):
            for n in ast.walk(f):
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in (
                        "_resultado_envio", "_guardar_evidencia", "_cosco_esperar_resultado", "_pulsar_boton"):
                    tras = f.name in despues and id(n) in despues[f.name]
                    llamadas.setdefault(n.func.id, []).append((f.name, tras))
        seis = sorted((n, True) for n in despues)
        self.assertEqual(sorted(llamadas["_resultado_envio"]), seis)
        self.assertEqual(sorted(llamadas["_pulsar_boton"]), seis)
        self.assertEqual(llamadas["_guardar_evidencia"], [("_resultado_envio", False)])
        self.assertEqual(llamadas["_cosco_esperar_resultado"], [("reservar_cosco", True)])


def correr_node(caso, guion):
    """Corre 'guion' en Node (fuera del navegador) y devuelve lo que imprimió, leído como JSON."""
    node = shutil.which("node")
    caso.assertTrue(node, "esta prueba corre JavaScript en Node y Node no está instalado")
    ruta = caso.sb / f"guion_{next(N)}.js"
    ruta.write_text(guion, encoding="utf-8")
    rc, out, err = soporte.hijo([node, str(ruta)], cwd=caso.sb)
    caso.assertEqual(rc, 0, err[-600:])
    return json.loads(out)


def clases(caso, lineas):
    """Cómo pinta el registro del panel cada línea (clase, en JS_INDEX), corrida en Node."""
    m = re.search(r"^function clase\(l\) \{\n.*?\n\}\n", caso.mod.JS_INDEX, re.S | re.M)
    caso.assertIsNotNone(m, "no encontré clase en JS_INDEX")
    return correr_node(caso, m.group(0) + f"console.log(JSON.stringify({json.dumps(lineas)}.map(clase)));\n")


class Nada:
    """Localizador de Playwright que no encuentra nada."""
    first = property(lambda self: self)
    last = property(lambda self: self)

    def count(self):
        return 0

    def is_visible(self):
        return False

    def all(self):
        return []


class AlcanceCOSCO:
    """El formulario (marco) o la página de COSCO después de Submit: cada JavaScript de la espera
    recibe la respuesta de su tipo, que reconoce por un pedazo de su texto (TIPOS); uno desconocido queda anotado y la
    prueba cae. Cuenta las esperas, con cada una adelanta el reloj de la prueba (estado["reloj"]; encargo 80), y anota
    cada localizador. Desde el encargo 78 no hay un tipo para pulsar el Submit de
    la ventana «Reminder»: un JavaScript que pulse es desconocido, salvo que traiga uno de esos pedazos (uno que trajera
    «submit below document» contaría como la pregunta por la ventana, y la prueba caería por las esperas; revisión de
    código del encargo 78)."""
    TIPOS = (("submit below document", "reminder"), ("[class*=boat]", "carga"),
             ("el-form-item__error", "errores"), ("(?:Request", "numero"), ("submitted successfully", "exito"),
             ("return !!b;", "submit_presente"), ("c.innerText || c.textContent", "texto"))

    def __init__(self, estado, **resp):
        self.estado, self.resp, self.esperas = estado, resp, 0

    def evaluate(self, js, *a):
        if len(self.estado["vistos"]) > 5000:
            raise Colgada("la espera no termina")
        tipo = next((t for clave, t in self.TIPOS if clave in js), "desconocido")
        self.estado["vistos"].append(tipo)
        r = self.resp.get(tipo)
        return r(self.estado) if callable(r) else r

    def locator(self, selector):
        self.estado["localizadores"].append(selector)
        return Nada()

    def wait_for_timeout(self, ms):
        self.esperas += 1
        self.estado["reloj"] += ms / 1000


class Reloj:
    """El time del programa, detenido: avanza solo con las esperas de la página falsa ('ahora', en s), como en
    test_datadome. La espera de COSCO cuenta su tope con errores de campo con time.monotonic (encargo 80), y el Registro
    usa time.time."""

    def __init__(self, ahora):
        self.ahora = ahora

    def monotonic(self):
        return self.ahora()

    def time(self):
        return 1000.0 + self.ahora()


class Colgada(BaseException):
    """Una espera que no termina, en una página falsa con el reloj detenido: deriva de BaseException para que ningún
    `except Exception` del programa se la trague y la prueba caiga en vez de quedar colgada."""


class TestCosco(soporte.CasoAQ):
    """Lo nuevo de COSCO tras Submit: el JavaScript que dice si pulsó, el que separa los errores de
    validación del aviso del portal, y la espera, que devuelve lo que vio sin decidir el estado."""
    CAMPOS = "'.el-form-item__error'"
    AVISOS = "'.el-message--error, .el-alert--error, .el-notification--error'"

    def test_js_submit_dice_si_pulso(self):
        guion = ("const el = (t) => ({textContent: t, clics: 0, click() { this.clics++; }});\n"
                 "const correr = (els) => { global.document = {querySelectorAll: () => els};\n"
                 "  const f = " + self.mod._JS_COSCO_SUBMIT + ";\n  return [f(), els.map(e => e.clics)]; };\n"
                 "console.log(JSON.stringify([correr([el('Save'), el(' Submit '), el('Submit booking')]), "
                 "correr([el('Save')])]));\n")
        self.assertEqual(correr_node(self, guion), [[True, [0, 1, 0]], [False, [0]]])

    def test_js_submit_presente_solo_el_submit_a_la_vista(self):
        # Desde el encargo 79 decide NO ENVIADA o ENVIADA – REVISAR EN PORTAL con errores de campo
        # (_cosco_submit_en_duda): «Submit» entero, sin distinguir mayúsculas ni los espacios de los lados, y a la vista
        # (offsetParent); oculto, otro texto o nada, false (revisión de código del encargo 79).
        guion = ("const el = (t, v) => ({textContent: t, offsetParent: v ? {} : null});\n"
                 "const correr = (els) => { global.document = {querySelectorAll: () => els};\n"
                 "  const f = " + self.mod._JS_COSCO_SUBMIT_PRESENTE + ";\n  return f(); };\n"
                 "console.log(JSON.stringify([correr([el('Save', true), el('Submit', true)]), "
                 "correr([el(' submit ', true)]), correr([el('Submit', false)]), "
                 "correr([el('Submit booking', true)]), correr([])]));\n")
        self.assertEqual(correr_node(self, guion), [True, True, False, False, False])

    def test_js_errores_separa_campos_y_aviso(self):
        guion = ("const el = (t, v) => ({textContent: t, offsetParent: v ? {} : null});\n"
                 "const correr = (tabla) => { global.document = {querySelectorAll: (s) => tabla[s] || []};\n"
                 "  const f = " + self.mod._JS_COSCO_ERRORES + ";\n  return f(); };\n"
                 "console.log(JSON.stringify([\n"
                 "  correr({[" + self.CAMPOS + "]: [el('Gross Weight is required', true), "
                 "el('  Gross\\n  Weight is required ', true), el('Temperature is required', true), "
                 "el('Oculto is required', false), el('', true)],\n"
                 "          [" + self.AVISOS + "]: [el('Allocation needs further confirmation', true), "
                 "el('Sistema ocupado', true)]}),\n"
                 "  correr({})]));\n")
        self.assertEqual(correr_node(self, guion), [
            {"campos": ["Gross Weight is required", "Temperature is required"], "portal": "Sistema ocupado"},
            {"campos": [], "portal": ""}])

    def test_errores_de_los_dos_alcances(self):
        class A:
            def __init__(self, r):
                self.r = r

            def evaluate(self, js):
                if isinstance(self.r, Exception):
                    raise self.r
                return self.r
        marco = A({"campos": ["Gross Weight is required"], "portal": ""})
        pagina = A({"campos": ["Gross Weight is required", "Shipper is required"], "portal": "Sistema ocupado"})
        juntos = (["Gross Weight is required", "Shipper is required"], "Sistema ocupado")
        self.assertEqual(self.mod._cosco_errores(marco, pagina), juntos)
        self.assertEqual(self.mod._cosco_errores(A(RuntimeError("marco cerrado")), pagina), juntos)
        self.assertEqual(self.mod._cosco_errores(None, A({})), ([], ""))

    def esperar(self, **resp):
        # El reloj del programa avanza solo con las esperas de la página (estado["reloj"], en s desde el clic).
        estado = {"vistos": [], "localizadores": [], "reloj": 0.0}
        marco, pagina = AlcanceCOSCO(estado, **resp), AlcanceCOSCO(estado)
        carpeta = self.sb / f"cosco_{next(N)}"
        with mock.patch.object(self.mod, "time", Reloj(lambda: estado["reloj"])):
            reg = self.mod.Registro(carpeta / "log.txt")
            try:
                r = self.mod._cosco_esperar_resultado(pagina, marco, reg)
            finally:
                reg.cerrar()
        self.assertNotIn("desconocido", estado["vistos"], "la espera corrió un JavaScript que la prueba no conoce")
        self.assertEqual(estado["localizadores"], [], "la espera buscó algo que pulsar")
        return r, pagina.esperas, estado, (carpeta / "log.txt").read_text(encoding="utf-8")

    def test_errores_de_validacion_esperan_hasta_el_tope(self):
        # Decisión de Marcelo, encargo 80: con errores de campo, antes de darlos por un rechazo la espera sigue mirando
        # hasta 20 s desde el clic si aparece la ventana «Reminder» o la página que dice que la reserva se envió. Sin
        # ninguna, vuelve con los errores a los 20 s justos del reloj: 2 vueltas hasta los errores, a los 3 s, y 12 más
        # (11 de 1,5 s y la última de 0,5). La etiqueta «Booking confirmation sent to» del formulario da _JS_COSCO_EXITO
        # (medido): no cuenta como la página de envío. Hasta el encargo 79 volvía a los 3 s, con la primera lectura.
        r, esperas, estado, log = self.esperar(errores={"campos": ["Gross Weight is required"], "portal": ""},
                                               submit_presente=True, exito=True)
        self.assertEqual((r, esperas, estado["reloj"]), ((["Gross Weight is required"], "", False), 14, 20.0))
        self.assertEqual(estado["vistos"].count("exito"), 0)
        self.assertEqual(log.count("COSCO marcó errores de campo a los 3 s de esperar el resultado. Antes de darlos por "
                                   "un rechazo, espero hasta los 20 s desde el Submit, sin pulsar nada, por si aparece "
                                   "la ventana 'Reminder' o la página que dice que la reserva se envió."), 1)
        self.assertEqual(log.count("A los 20 s del Submit no apareció la ventana 'Reminder' ni la página que dice que "
                                   "la reserva se envió."), 1)

    def test_espera_corta_con_aviso_del_portal(self):
        r, esperas, _, _ = self.esperar(errores={"campos": [], "portal": "Sistema ocupado"}, submit_presente=True)
        self.assertEqual((r, esperas), (([], "Sistema ocupado", False), 2))

    def test_reminder_no_se_pulsa(self):
        # Decisión de Marcelo, encargo 78: del Submit de la ventana «Reminder» no se pulsa nada; solo se espera. Como el
        # 22-10: la ventana aparece, sigue cinco vueltas, se cierra sola y después llega la señal de envío. Sin un solo
        # clic: sin ningún JavaScript que la espera no conozca (uno que pulsara sería desconocido) y sin buscar nada con
        # un localizador (esperar lo exige).
        r, esperas, _, log = self.esperar(reminder=lambda e: e["vistos"].count("reminder") <= 5, exito=True)
        self.assertEqual((r, esperas), (([], "", True), 7))
        # Un paso normal, no un error (encargo 77): log.txt dice cuándo aparece y cuándo deja de verse, contados desde
        # que empieza a esperar (6 vueltas de 1,5 s).
        self.assertEqual(log.count("Ventana 'Reminder' a la vista a los 2 s de esperar el resultado: es un paso normal de "
                                   "COSCO, que recuerda enviar los documentos antes de su plazo. No pulso nada y sigo "
                                   "esperando."), 1)
        self.assertEqual(log.count("La ventana 'Reminder' dejó de verse a los 9 s de esperar el resultado."), 1)
        # El registro del panel no pinta ninguna de sus líneas como una alerta (clase, en JS_INDEX).
        lineas = [l for l in log.splitlines() if "Reminder" in l]
        self.assertEqual(len(lineas), 3)                  # la espera, la ventana a la vista y el cierre
        self.assertNotIn(["f-alerta", "REVISAR"], clases(self, lineas))

    def test_reminder_que_vuelve_dice_una_vez_que_se_cerro(self):
        # La ventana aparece, se va, vuelve y se va: cada aviso, una sola vez.
        vueltas = iter([True, False, True])
        r, _, _, log = self.esperar(reminder=lambda e: next(vueltas, False),
                                    exito=lambda e: e["vistos"].count("reminder") >= 6, submit_presente=True)
        self.assertEqual(r, ([], "", True))
        self.assertEqual([log.count("a la vista a los"), log.count("La ventana 'Reminder' dejó de verse")], [1, 1])

    def test_al_agotarse_con_la_carga_lee_los_errores(self):
        # Como con la ventana, con la máscara de carga hasta el final los errores no se leen en ninguna vuelta: también
        # se leen al cumplirse el plazo (revisión de código del encargo 77), y van como aviso del portal, sin la ventana
        # también: al plazo no se sabe si COSCO creó la reserva (revisión de seguridad).
        r, esperas, _, _ = self.esperar(carga=True, errores={"campos": ["Gross Weight is required"], "portal": "Ocupado"})
        self.assertEqual((r, esperas), (([], "Gross Weight is required; Ocupado", False), 120))

    def test_reminder_tardio_tampoco_se_pulsa(self):
        # La ventana aparece en la sexta vuelta y no se cierra: solo se espera hasta el plazo, sin un clic.
        r, esperas, _, log = self.esperar(reminder=lambda e: e["vistos"].count("reminder") > 10, submit_presente=True)
        self.assertEqual((r, esperas), (([], "", True), 120))
        self.assertEqual(log.count("No pulso nada y sigo esperando."), 1)
        self.assertIn("Se cumplió el plazo de 180 s sin confirmación de COSCO.", log)

    def test_espera_se_agota(self):
        # Sin nada en pantalla y con el Submit todavía visible: vueltas de 2 × 1,5 s hasta el plazo de 180 s.
        r, esperas, _, log = self.esperar(submit_presente=True)
        self.assertEqual((r, esperas), (([], "", False), 120))
        self.assertIn("Se cumplió el plazo de 180 s sin confirmación de COSCO.", log)

    def test_al_agotarse_lee_los_errores(self):
        # Con la ventana abierta hasta el final, los errores no se leen en ninguna vuelta: al cumplirse el plazo se
        # leen una vez, para que el estado no decida sin ellos (encargo 77), y van como aviso del portal: ENVIADA –
        # REVISAR EN PORTAL, nunca NO ENVIADA. Hasta ahí, volvía sin leerlos.
        r, esperas, _, _ = self.esperar(reminder=True, errores={"campos": ["Gross Weight is required"], "portal": ""})
        self.assertEqual((r, esperas), (([], "Gross Weight is required", True), 120))


class AlcancePortal(P):
    """La página de COSCO o el marco de su formulario: responde con lo que muestra su PortalCOSCO en ese instante, y le
    pasa sus esperas y sus localizadores."""

    def __init__(self, portal, en_el_marco, frames=None):
        super().__init__(url="https://elines.invalid/bkg2" if en_el_marco else "https://elines.invalid/", frames=frames)
        self.portal, self.en_el_marco = portal, en_el_marco

    def evaluate(self, js, *a):
        return self.portal.responder(js, self.en_el_marco)

    def locator(self, sel):
        self.portal.localizadores.append(sel)
        return Nada()

    def wait_for_timeout(self, ms):
        self.portal.esperar(ms)


class PortalCOSCO:
    """COSCO después de su guarda, en el tiempo: la página y el marco de su formulario (AlcancePortal), con un reloj en
    milisegundos que avanza solo con sus esperas. Lo que muestran sale de los segundos desde el clic del Submit, en
    tramos [desde, hasta): los errores de campo y la máscara de carga (en el marco), la ventana «Reminder» (en la página
    o, con 'reminder_en_el_marco', en el marco), la página que dice que la reserva se envió (la frase de COSCO, en el
    marco, desde 'envio') y el Submit del formulario (en el marco, hasta 'submit_hasta'). El marco da siempre _JS_COSCO_EXITO: la etiqueta «Booking
    confirmation sent to» de su formulario (medido en la guarda del 22-10; encargo 80). Anota cada JavaScript que no
    conoce y cada localizador, y corta con Colgada si la espera no termina."""
    SIEMPRE = (0, 10 ** 6)

    def __init__(self, mod, errores=SIEMPRE, carga=(0, 0), reminder=(0, 0), envio=None, submit_hasta=10 ** 6,
                 reminder_en_el_marco=False):
        self.mod, self.errores, self.carga, self.reminder = mod, errores, carga, reminder
        self.envio, self.submit_hasta, self.reminder_en_el_marco = envio, submit_hasta, reminder_en_el_marco
        self.ms, self.clic, self.esperas = 0, None, 0
        self.desconocidos, self.localizadores = [], []
        self.marco = AlcancePortal(self, True)
        self.pagina = AlcancePortal(self, False, frames=[self.marco])

    def ahora(self):
        return self.ms / 1000

    def seg(self):
        """Segundos desde el clic del Submit; None antes."""
        return None if self.clic is None else (self.ms - self.clic) / 1000

    def ve(self, desde, hasta):
        return self.clic is not None and desde * 1000 <= self.ms - self.clic < hasta * 1000

    def esperar(self, ms):
        self.esperas += 1
        if self.esperas > 400:
            raise Colgada("la espera no termina")
        self.ms += ms

    def responder(self, js, en_el_marco):
        m = self.mod
        if "getHTML" in js:
            return {"html": "<p>marco</p>" if en_el_marco else "<p>página</p>", "sombras": 0}
        if js.startswith("window.scrollTo"):
            return None
        if js == m._JS_COSCO_SUBMIT and en_el_marco and self.clic is None:
            self.clic = self.ms
            return True
        enviada = self.envio is not None and self.ve(self.envio, 10 ** 6)
        respuestas = {
            m._JS_COSCO_HAY_REMINDER: en_el_marco == self.reminder_en_el_marco and self.ve(*self.reminder),
            m._JS_COSCO_EN_CARGA: en_el_marco and self.ve(*self.carga),
            m._JS_COSCO_ERRORES: {"campos": ["Gross Weight is required"] if en_el_marco and self.ve(*self.errores)
                                  else [], "portal": ""},
            m._JS_COSCO_NUMERO: "",
            m._JS_COSCO_EXITO: en_el_marco,
            m._JS_COSCO_SUBMIT_PRESENTE: en_el_marco and self.ve(0, self.submit_hasta),
            m._JS_TEXTO_VISIBLE: (COSCO_ENVIADA if enviada else "Booking Details\nBooking confirmation sent to")
                                 if en_el_marco else "",
        }
        if js in respuestas:
            return respuestas[js]
        self.desconocidos.append(js[:60])
        return None


class TestCoscoTrasLosErrores(ConRegistro):
    """Decisión de Marcelo, encargo 80 (CICLO-cosco-espera-tras-errores.md): con errores de campo tras el Submit de COSCO,
    antes de dar NO ENVIADA la espera sigue mirando hasta 20 s desde el clic si aparece la ventana «Reminder» o la página
    que dice que la reserva se envió, y con cualquiera de las dos sigue su camino enseguida, sin esperar el resto. NO
    ENVIADA solo si a los 20 s el Submit sigue a la vista y no apareció ninguna. Corre de punta a punta el código real de
    reservar_cosco después de su guarda (despues_de_la_guarda), del clic al estado, sobre un portal falso en el tiempo."""
    SUBMIT = "button:has-text('Submit'), .btn:has-text('Submit')"
    RECHAZO = ("COSCO: el portal no aceptó el envío y marcó: «Gross Weight is required». La reserva no se envió; "
               "corrige esos datos y vuelve a correrla.")
    TRAMO = "COSCO marcó errores de campo a los 3 s de esperar el resultado. Antes de darlos por un rechazo"
    TOPE = "A los 20 s del Submit no apareció la ventana 'Reminder' ni la página que dice que la reserva se envió."

    def correr(self, **escena):
        portal = PortalCOSCO(self.mod, **escena)
        with mock.patch.object(self.mod, "time", Reloj(portal.ahora)):
            carpeta, reg = self.corrida()
            try:
                r = despues_de_la_guarda(self.mod, "reservar_cosco")(portal.pagina, portal.marco, reg, 8)
            finally:
                reg.cerrar()
        self.assertEqual(portal.desconocidos, [], "corrió un JavaScript que la prueba no conoce")
        self.assertEqual(portal.localizadores, [self.SUBMIT], "buscó algo que pulsar además del Submit")
        return r, portal.seg(), (carpeta / "log.txt").read_text(encoding="utf-8")

    def test_rechazo_que_dura_los_20_s(self):
        # Errores de campo desde el principio, el Submit a la vista y ni la ventana ni la página de envío: NO ENVIADA, a
        # los 20 s del clic justos. Hasta el encargo 79, a los 3 s. La etiqueta del formulario que da _JS_COSCO_EXITO no
        # corta el tramo.
        r, seg, log = self.correr()
        self.assertEqual((r, seg), (("NO ENVIADA", self.RECHAZO), 20.0))
        self.assertEqual([log.count(self.TRAMO), log.count(self.TOPE)], [1, 1])
        # Con errores que llegan después del tope (la máscara de carga hasta los 21 s), no espera más: NO ENVIADA con la
        # primera lectura, como hasta el encargo 79. El tope cuenta desde el clic, no desde los errores.
        r, seg, log = self.correr(carga=(0, 21))
        self.assertEqual((r, seg), (("NO ENVIADA", self.RECHAZO), 22.5))
        self.assertNotIn("Antes de darlos por un rechazo", log)
        # Con el Submit ya no a la vista a los 20 s, el envío pudo haber entrado: ENVIADA – REVISAR EN PORTAL (encargo
        # 79).
        r, seg, _ = self.correr(submit_hasta=10)
        self.assertEqual((r[0], seg), ("ENVIADA – REVISAR EN PORTAL", 20.0))
        self.assertIn("pero «Submit» ya no está a la vista: el envío pudo haber entrado", r[1])

    def test_reminder_que_llega_dentro_del_tramo(self):
        # La ventana a la vista de los 9 a los 12 s: el tramo la ve a los 9 s y sigue su camino enseguida. Mientras siga
        # a la vista solo se espera, y los errores vistos antes van como aviso del portal (encargo 77): ENVIADA –
        # REVISAR EN PORTAL a los 13,5 s, sin esperar el resto del tramo.
        linea = ("Ventana 'Reminder' a la vista a los 9 s de esperar el resultado, con campos marcados antes: es un paso "
                 "normal de COSCO, que sale después del envío. No pulso nada y sigo esperando.")
        for en_el_marco in (False, True):         # la ventana, en la página o en el marco del formulario
            with self.subTest(en_el_marco=en_el_marco):
                r, seg, log = self.correr(reminder=(9, 12), reminder_en_el_marco=en_el_marco)
                self.assertEqual((r, seg), (("ENVIADA – REVISAR EN PORTAL", "COSCO: se pulsó «Submit» y el portal "
                                             "mostró un error: «Gross Weight is required». " + REVISA), 13.5))
                self.assertEqual(log.count(linea), 1)
                self.assertEqual(log.count("La ventana 'Reminder' dejó de verse a los 12 s de esperar el resultado."), 1)
                self.assertNotIn(self.TOPE, log)
        # Un paso normal: el registro del panel no la pinta como una alerta (clase, en JS_INDEX; revisión de código).
        self.assertEqual(clases(self, [linea]), [["f-info", ""]])
        # Una ventana que se ve en una sola vuelta del tramo también cuenta: la espera la recuerda, y nunca da NO
        # ENVIADA después.
        r, seg, _ = self.correr(reminder=(7.5, 8))
        self.assertEqual((r[0], seg), ("ENVIADA – REVISAR EN PORTAL", 10.5))

    def test_pagina_de_envio_dentro_del_tramo(self):
        # La página que dice que la reserva se envió desde los 10 s, cuando los errores y el Submit ya no se ven: el tramo
        # la ve a los 10,5 s y sigue su camino enseguida: EMITIDA – CONFIRMAR POR CORREO, con su número.
        r, seg, log = self.correr(errores=(0, 10), envio=10, submit_hasta=10)
        self.assertEqual((r[0], seg), ("EMITIDA – CONFIRMAR POR CORREO", 10.5))
        self.assertIn("(Booking: CD1234567890)", r[1])
        self.assertEqual(log.count("La página dijo que la reserva se envió a los 10 s de esperar el resultado, después "
                                   "de los errores de campo."), 1)
        self.assertNotIn(self.TOPE, log)
        # Con los errores todavía a la vista, las dos señales se contradicen (encargo 78): ENVIADA – REVISAR EN PORTAL.
        r, seg, _ = self.correr(envio=10)
        self.assertEqual((r[0], seg), ("ENVIADA – REVISAR EN PORTAL", 10.5))
        self.assertIn("Las dos señales se contradicen", r[1])

    def test_sin_errores_de_campo_no_hay_tramo(self):
        # FRENA SI del encargo: sin errores de campo, la espera no mira nada nuevo ni espera más. La etiqueta del
        # formulario la corta a los 3 s, como antes, y la frase la lee _resultado_envio, cada segundo hasta 15 s:
        # EMITIDA – CONFIRMAR POR CORREO a los 10 s.
        r, seg, log = self.correr(errores=(0, 0), envio=10, submit_hasta=10)
        self.assertEqual((r[0], seg), ("EMITIDA – CONFIRMAR POR CORREO", 10.0))
        self.assertNotIn("Antes de darlos por un rechazo", log)

    def test_pagina_de_envio_es_la_frase(self):
        # La página de envío es la frase de FORMA_ENVIADA, con la que decide el estado, en una sola lectura: no la
        # etiqueta «Booking confirmation sent to» del formulario, que da _JS_COSCO_EXITO también antes del clic (medido).
        # Con dos referencias distintas, también lo es; si la lectura falla, no.
        mod = self.mod
        pagina = Pantalla("Booking Details\nBooking confirmation sent to")
        self.assertFalse(mod._cosco_pagina_de_envio(pagina))
        self.assertEqual((pagina.lecturas, pagina.esperas), (1, 0))
        self.assertTrue(mod._cosco_pagina_de_envio(Pantalla(COSCO_ENVIADA)))
        dos = COSCO_ENVIADA + "\nBooking CD0000000000 has been submitted successfully"
        self.assertTrue(mod._cosco_pagina_de_envio(Pantalla(dos)))

        class Cerrada(Pantalla):
            """Una página que ya no deja leer sus marcos: la lectura falla con un error que no es de la frase."""
            @property
            def frames(self):
                raise RuntimeError("la página se cerró")

            @frames.setter
            def frames(self, valor):
                pass
        self.assertFalse(mod._cosco_pagina_de_envio(Cerrada("")))


class TestLecturaDelPanel(soporte.CasoAQ):
    """El panel pinta cada fila según lecturaEstado. Se corre en Node, fuera del navegador."""

    def lecturas(self, estados):
        m = re.search(r"^function lecturaEstado\(est\) \{\n.*?\n\}\n", self.mod.JS_INDEX, re.S | re.M)
        self.assertIsNotNone(m, "no encontré lecturaEstado en JS_INDEX")
        guion = m.group(0) + f"console.log(JSON.stringify({json.dumps(estados)}.map(lecturaEstado)));\n"
        return dict(zip(estados, correr_node(self, guion)))

    def test_marca_por_defecto_tambien_las_filas_sin_nave(self):
        # Una fila sin nave va marcada, como las demás: queda NO ENVIADA con el motivo sin entrar al portal, y así llega a
        # log.txt y a la planilla. Solo las MANUAL quedan sin marcar. Hasta a198645, la fila con la nave vacía quedaba sin
        # marcar, con el aviso «esas se omiten», y no llegaba a la planilla (CICLO-solo-la-nave-pedida.md). Cuál es MANUAL
        # lo dice el programa (f.manual, de /api/filas): hasta f68ce6c el panel lo decidía por su cuenta con el texto de
        # la nave, y la última, sin f.manual, quedaba sin marcar (CICLO-cola-seis-items.md).
        js = self.mod.JS_INDEX
        m = re.search(r"^function marcadaPorDefecto\(f\) \{\n.*?\n\}\n", js, re.S | re.M)
        self.assertIsNotNone(m, "no encontré marcadaPorDefecto en JS_INDEX")
        filas = [{"nave": ""}, {"nave": "AUTO", "sin_nave": True}, {"nave": "NAVE UNO"},
                 {"nave": "reserva manual", "manual": True}, {}, {"nave": "MANUAL"}]
        guion = m.group(0) + f"console.log(JSON.stringify({json.dumps(filas)}.map(marcadaPorDefecto)));\n"
        self.assertEqual(correr_node(self, guion), [True, True, True, False, True, True])
        # La tabla y «Todas» marcan con ella, y la etiqueta y el aviso usan la regla del programa (f.sin_nave).
        for trozo in ('const chk = marcadaPorDefecto(f) ? "checked" : "";',
                      "c.checked = marcadaPorDefecto(FILAS[i]);",
                      "${f.sin_nave ? \"<span class='sin-nave'>sin nave</span> \" + esc(f.nave) : esc(f.nave)}",
                      "const sin = FILAS.filter(f => f.sin_nave).length;",
                      '" reserva(s) no traen una nave para reservar: quedan NO ENVIADA, sin entrar al portal. "'):
            with self.subTest(trozo=trozo):
                self.assertEqual(js.count(trozo), 1)
        self.assertNotIn("esas se omiten", js)

    def test_marca_y_cuenta_aparte_las_filas_sin_ruta(self):
        # La fila con nave y sin puerto de carga o sin destino se ve marcada antes de correr, en la celda que le falta,
        # y se cuenta aparte, como la fila sin nave (decisión de Marcelo, encargo 43, CICLO-maersk-elige-exacto.md; las
        # marcas, de /api/filas: test_web). Va marcada para correr, como las demás: queda NO ENVIADA con su motivo, sin
        # entrar al portal. Hasta ahí, el panel no la distinguía.
        js = self.mod.JS_INDEX
        m = re.search(r"^function marcadaPorDefecto\(f\) \{\n.*?\n\}\n", js, re.S | re.M)
        filas = [{"nave": "NAVE UNO", "sin_puerto": True}, {"nave": "NAVE UNO", "sin_destino": True}]
        guion = m.group(0) + f"console.log(JSON.stringify({json.dumps(filas)}.map(marcadaPorDefecto)));\n"
        self.assertEqual(correr_node(self, guion), [True, True])
        for trozo in ("${f.sin_puerto ? \"<span class='sin-ruta'>sin puerto de carga</span> \" + esc(f.pol) : "
                      "esc(f.pol)}",
                      "${f.sin_destino ? \"<span class='sin-ruta'>sin destino</span> \" + esc(f.destino_final)\n"
                      "                          : esc(f.destino_final)}",
                      "const sinRuta = FILAS.filter(f => f.sin_puerto || f.sin_destino).length;",
                      '" reserva(s) con nave no traen su puerto de carga o su destino: quedan NO ENVIADA, "'):
            with self.subTest(trozo=trozo):
                self.assertEqual(js.count(trozo), 1)
        self.assertIn(".sin-nave, .sin-ruta, .otro-contenedor { color: var(--text-muted); font-style: italic; }",
                      self.mod.CSS_INDEX)

    def test_marca_y_cuenta_aparte_las_filas_con_otro_contenedor(self):
        # La fila de MAERSK que pide otro contenedor se ve marcada antes de correr, junto a «Reserva N» (la tabla no
        # muestra el contenedor), con el que pide, y se cuenta aparte, como la sin ruta (decisión de Marcelo, encargo
        # 64, CICLO-maersk-contenedor-consola-y-panel.md; la marca, de /api/filas: test_web). Va marcada para correr,
        # como las demás: queda NO ENVIADA con su motivo, sin entrar al portal. Hasta ahí, el panel no la distinguía.
        js, m = self.mod.JS_INDEX, self.mod
        marcada = re.search(r"^function marcadaPorDefecto\(f\) \{\n.*?\n\}\n", js, re.S | re.M).group(0)
        esc = re.search(r"^function esc\(s\) \{\n.*?\n\}\n", js, re.S | re.M).group(0)
        marca = ("${\n        f.otro_contenedor ? \" <span class='otro-contenedor'>otro contenedor: \"\n"
                 "                            + esc(f.contenedor_a_la_vista) + \"</span>\"\n"
                 "                          : \"\"}</td>")
        aviso = (f'" reserva(s) de MAERSK piden otro contenedor que «{m.CONTENEDOR_DE_LAS_FILAS}»: quedan NO '
                 'ENVIADA, " +\n                     "sin entrar al portal. Resérvalas a mano en el portal, o '
                 'corrige el contenedor en la planilla.",')
        for trozo in (marca, "const otroCont = FILAS.filter(f => f.otro_contenedor).length;", aviso,
                      'Reserva ${i + 1}' + marca):
            with self.subTest(trozo=trozo[:40]):
                self.assertEqual(js.count(trozo), 1)
        # La página pinta el contenedor que muestra el motivo, el que trae /api/filas (contenedor_a_la_vista, desde
        # el encargo 65), no la celda: recortado y sin caracteres invisibles (revisiones del encargo 65).
        filas = [{"nave": "NAVE UNO", "otro_contenedor": True, "contenedor": "20 DRY",
                  "contenedor_a_la_vista": "20 DRY"},
                 {"nave": "NAVE UNO", "otro_contenedor": True, "contenedor": "<b>40' HC</b>",
                  "contenedor_a_la_vista": "<b>40' HC</b>"},
                 {"nave": "NAVE UNO", "otro_contenedor": False, "contenedor": "40 HC REEFER",
                  "contenedor_a_la_vista": ""},
                 {"nave": "NAVE UNO", "otro_contenedor": True, "contenedor": "X" * 50,
                  "contenedor_a_la_vista": "X" * 40}]
        guion = (marcada + esc + f"const filas = {json.dumps(filas)};\n"
                 + "console.log(JSON.stringify([filas.map(marcadaPorDefecto), filas.map(f => `Reserva 1"
                 + marca[:-len("</td>")] + "`)]));\n")
        self.assertEqual(correr_node(self, guion),
                         [[True, True, True, True],
                          ["Reserva 1 <span class='otro-contenedor'>otro contenedor: 20 DRY</span>",
                           "Reserva 1 <span class='otro-contenedor'>otro contenedor: &lt;b&gt;40' HC&lt;/b&gt;</span>",
                           "Reserva 1",
                           f"Reserva 1 <span class='otro-contenedor'>otro contenedor: {'X' * 40}</span>"]])
        self.assertIn(".sin-nave, .sin-ruta, .otro-contenedor { color: var(--text-muted); font-style: italic; }",
                      m.CSS_INDEX)

    def test_lectura_de_cada_estado(self):
        # «OK-EJEMPLO» es «lista»: no se emitió. Hasta el encargo 34 era «emitida» (CICLO-one-y-maersk-eligen-la-nave.md).
        esperado = {"EN CURSO": "curso", "EMITIDA": "emitida", "OK-EJEMPLO": "lista", "DETENIDO": "detenido",
                    "NO ENVIADA": "no-enviada", "ENVIADA – REVISAR EN PORTAL": "revisar-portal",
                    "REVISAR": "revisar", "ERROR": "revisar", "SIN-CUPO": "sin-cupo", "": "otro",
                    "OTRO ESTADO": "otro", "EMITIDA – CONFIRMAR POR CORREO": "emitida-correo"}
        self.assertEqual(self.lecturas(list(esperado)), esperado)

    def test_emitida_por_correo_se_pinta_como_emitida(self):
        # COSCO, desde el encargo 77, y CMA-CGM, desde el 78: el panel la lee por el mismo texto del programa
        # (EMITIDA_POR_CORREO, que el JavaScript repite), la cuenta como emitida, y su columna dice lo de la planilla
        # (n_reserva): desde el encargo 78, el número de su «(Booking: …)», con la insignia de un número; sin él,
        # «confirmar por correo». El mismo estado que log.txt y que la planilla (test_planilla).
        js = self.mod.JS_INDEX
        self.assertEqual(js.count(f'if (est === "{self.mod.EMITIDA_POR_CORREO}") return "emitida-correo";'), 1)
        m = re.search(r'\} else if \(lectura === "emitida-correo"\) \{\n(.*?)\n        \} else if', js, re.S)
        self.assertIsNotNone(m, "el panel no tiene rama para emitida-correo")
        for trozo in ('chip(f, "ok", "emitida – confirmar por correo");', "totalEmitidas++;",
                      'tr.classList.add("fila-emitida");',
                      'tdBkg.innerHTML = bkg ? `<span class="badge-bkg">${esc(nres)}</span>`\n',
                      ': `<span class="badge-bkg-vacio" style="color:var(--text-secondary)">${esc(nres)}</span>`;'):
            with self.subTest(trozo=trozo):
                self.assertIn(trozo, m.group(1))
        t, limpio = self.mod._texto_n_reserva, self.mod._extraer_bkg_limpio
        self.assertEqual(self.mod.CONFIRMAR_POR_CORREO, "confirmar por correo")
        correo = "EMITIDA – CONFIRMAR POR CORREO"
        casos = [({"estado": correo}, ""),
                 # El detalle del encargo 77, sin su «(Booking: …)»: la referencia no se toma de otra forma del texto.
                 ({"estado": correo, "booking": "BKGFALSO12",
                   "detalle": "Booking CD1234567890 has been submitted successfully"}, ""),
                 ({"estado": correo, "detalle": "COSCO: … se envió (Booking: CD1234567890). COSCO la confirma"},
                  "CD1234567890"),
                 ({"estado": correo, "detalle": "CMA: … se envió (Booking: QXZ1234567). CMA la confirma"}, "QXZ1234567"),
                 # Solo con su estado: otra con el mismo detalle no tiene número.
                 ({"estado": "ENVIADA – REVISAR EN PORTAL", "detalle": "… (Booking: CD1234567890). …"}, "")]
        for r, numero in casos:
            with self.subTest(r=r):
                self.assertEqual((limpio(r), t(r)), (numero, numero or ("confirmar por correo" if r["estado"] == correo
                                                                        else "")))

    def test_cada_lectura_nueva_pinta_su_fila(self):
        js = self.mod.JS_INDEX
        self.assertIn("const lectura = lecturaEstado(est);", js)
        # SIN-CUPO, desde el encargo 40: hasta ahí quedaba en «procesando…» (CICLO-maersk-busqueda-vacia.md).
        for lectura, texto in (("no-enviada", "no enviada"), ("revisar-portal", "revisar en portal"),
                               ("sin-cupo", "sin cupo")):
            with self.subTest(lectura=lectura):
                m = re.search(r'\} else if \(lectura === "%s"\) \{\n(.*?)\n        \} else if' % lectura, js, re.S)
                self.assertIsNotNone(m, f"el panel no tiene rama para {lectura}")
                bloque = m.group(1)
                self.assertIn(f'chip(f, "rev", "{texto}");', bloque)
                self.assertIn('if (tr) tr.classList.remove("fila-activa", "fila-emitida");', bloque)   # deja «en curso»
                self.assertIn(f'color:var(--danger)">{texto}</span>', bloque)                         # y «procesando…»

    def test_lista_para_emitir_no_es_emitida(self):
        # Con el candado cerrado, la OK-EJEMPLO no se emitió: su columna dice lo que dice la planilla (n_reserva, de
        # _texto_n_reserva), nunca «Confirmada», y la píldora y el estado final la cuentan aparte de las emitidas. Hasta el
        # encargo 34, «✓ Confirmada» y «N de M emitidas» (CICLO-one-y-maersk-eligen-la-nave.md).
        js = self.mod.JS_INDEX
        codigo = "\n".join(l for l in js.splitlines() if not l.strip().startswith("//"))    # el comentario lo nombra
        self.assertNotIn("Confirmada", codigo)
        m = re.search(r'\} else if \(lectura === "emitida" \|\| lectura === "lista"\) \{\n(.*?)\n        \} else if', js, re.S)
        self.assertIsNotNone(m, "el panel no pinta juntas la emitida y la lista")
        for trozo in ('chip(f, "ok", lista ? "ok (previa)" : "emitida");', "if (lista) totalListas++; else totalEmitidas++;",
                      '${esc(nres || "—")}</span>'):
            with self.subTest(trozo=trozo):
                self.assertIn(trozo, m.group(1))
        self.assertEqual(js.count('const nres = (typeof r === "object" && r) ? (r.n_reserva || "") : "";'), 1)
        for trozo in ("const cuenta = cuentaCorrida(totalEmitidas, totalListas, selCount);",
                      "estado(`Terminó: ${cuentaCorrida(totalEmitidas, totalListas, selCount)}`);"):
            with self.subTest(trozo=trozo):
                self.assertEqual(js.count(trozo), 1)
        f = re.search(r"^function cuentaCorrida\(emitidas, listas, total\) \{\n.*?\n\}\n", js, re.S | re.M)
        self.assertIsNotNone(f, "no encontré cuentaCorrida en JS_INDEX")
        casos = [[0, 3, 5], [2, 0, 5], [0, 0, 5], [1, 2, 5]]
        guion = f.group(0) + f"console.log(JSON.stringify({json.dumps(casos)}.map(c => cuentaCorrida(...c))));\n"
        self.assertEqual(correr_node(self, guion), ["3 de 5 listas para emitir", "2 de 5 emitidas", "0 de 5 emitidas",
                                                    "1 de 5 emitidas · 2 de 5 listas para emitir"])
        # El texto de la columna, de una sola fuente, el mismo de la planilla.
        t = self.mod._texto_n_reserva
        self.assertEqual([t({"estado": "EMITIDA", "detalle": "MSC emitida con éxito (Booking: EBKG65432109)"}),
                          t({"estado": "EMITIDA", "booking": "BKGFALSO12"}), t({"estado": "OK-EJEMPLO"}),
                          t({"estado": "EMITIDA"}), t({"estado": "NO ENVIADA"}), t({"estado": "OK-EJEMPLO", "booking": "X9"}),
                          t(None)],
                         ["EBKG65432109", "BKGFALSO12", "lista para emitir", "", "", "lista para emitir", ""])

    def aviso_de_modo(self, pagina, panel):
        """El aviso de la página que no arma las reservas: 'pagina', el modo que muestra (o None si no lo pudo leer);
        'panel', el que dijo el panel (o None si no dijo uno). Con los nombres de NOMBRE_DEL_MODO, los del programa."""
        n = self.mod.NOMBRE_DEL_MODO
        muestra = f"muestra el modo {n[pagina]}" if isinstance(pagina, bool) else "no muestra el modo del panel"
        esta = f"está en modo {n[panel]}" if isinstance(panel, bool) else "no dijo en qué modo está"
        return (f"No armé las reservas: esta página {muestra}, y el panel {esta}. Recarga la página (F5) para ver el "
                f"modo del panel, y vuelve a armarlas.")

    def test_el_panel_vuelve_a_leer_su_modo_antes_de_armar(self):
        # Decisión de Marcelo, encargo 52 (CICLO-puerto-libre-y-modo-al-armar.md): la página pinta su aviso de modo al
        # cargar (MODO_PAGINA); antes de armar, vuelve a leer el modo del panel (/api/config), y si no es el que
        # muestra, no corre y avisa que hay que recargarla. Tampoco corre si el panel no dice un modo (no contesta, o no
        # dice true ni false) o si la página no pudo leer el suyo. Se corre en Node, con api, feed y estado falsos.
        js = self.mod.JS_INDEX
        f = re.search(r"^async function mismoModo\(\) \{\n.*?\n\}\n", js, re.S | re.M)
        a = re.search(r"^function avisoDeModo\(pagina, panel\) \{\n.*?\n\}\n", js, re.S | re.M)
        self.assertIsNotNone(f, "no encontré mismoModo en JS_INDEX")
        self.assertIsNotNone(a, "no encontré avisoDeModo en JS_INDEX")
        # El aviso va a la vista, no solo al registro plegado (avisoFijo, encargo 61), y si el panel contestó con un
        # error (su configuración no se lee: «error500»), dice también su motivo. Sin respuesta («error»), no.
        g = re.search(r"^function avisoFijo\(texto, cls, etiqueta\) \{\n.*?\n\}\n", js, re.S | re.M)
        self.assertIsNotNone(g, "no encontré avisoFijo en JS_INDEX")
        casos = [[False, False], [True, True], [False, True], [True, False], [False, "error"], [None, False],
                 [None, "error"], [False, "false"], [True, None], [None, "error500"]]
        guion = ("let MODO_PAGINA = null, RESPUESTA = null, AVISOS = [], ESTADOS = [], RUTAS = [], NOTAS = [];\n"
                 "async function api(ruta) {\n"
                 "  RUTAS.push(ruta);\n"
                 "  if (RESPUESTA === 'error') throw new Error('sin respuesta');\n"
                 "  if (RESPUESTA === 'error500') {\n"
                 "    const e = new Error('config.json roto'); e.status = 500; throw e;\n"
                 "  }\n"
                 "  return { modo_emision: RESPUESTA };\n"
                 "}\n"
                 "function feed(t, c, e) { AVISOS.push([t, c, e]); }\n"
                 "function notaVisible(t) { NOTAS.push(t); }\n"
                 "function estado(t) { ESTADOS.push(t); }\n"
                 + f.group(0) + a.group(0) + g.group(0) +
                 "(async () => {\n"
                 "  const salida = [];\n"
                 f"  for (const [pagina, panel] of {json.dumps(casos)}) {{\n"
                 "    MODO_PAGINA = pagina; RESPUESTA = panel; AVISOS = []; ESTADOS = []; RUTAS = []; NOTAS = [];\n"
                 "    salida.push([await mismoModo(), AVISOS, ESTADOS, RUTAS, NOTAS]);\n"
                 "  }\n"
                 "  console.log(JSON.stringify(salida));\n"
                 "})();\n")
        esperado = []
        for pagina, panel in casos:
            dijo = panel if isinstance(panel, bool) else None
            if isinstance(pagina, bool) and pagina is dijo:
                esperado.append([True, [], [], ["/api/config"], []])
            else:
                aviso = self.aviso_de_modo(pagina, dijo)
                if panel == "error500":
                    aviso += " El panel no pudo leer su configuración: config.json roto"
                esperado.append([False, [[aviso, "f-alerta", "REVISAR"]], ["Recarga la página antes de armar"],
                                 ["/api/config"], [aviso]])
        self.assertEqual(correr_node(self, guion), esperado)

    def test_armar_pregunta_el_modo_y_lo_manda(self):
        # El botón de armar pregunta el modo (mismoModo) antes de tocar la pantalla o el panel, y manda a /api/correr el
        # modo que muestra la página, que el panel vuelve a comparar con el suyo (test_web). MODO_PAGINA es el modo con
        # que la página pintó su aviso al cargar, y el aviso se pinta con él (encargo 52).
        js = self.mod.JS_INDEX
        for trozo in ("let MODO_PAGINA = null;", "MODO_PAGINA = Boolean(d.modo_emision);", "if (MODO_PAGINA) {",
                      "if (!(await mismoModo())) return;"):
            with self.subTest(trozo=trozo):
                self.assertEqual(js.count(trozo), 1)
        self.assertEqual(js.count("d.modo_emision"), 1)
        m = re.search(r'^\$\("#wg-armar"\)\.onclick = async \(\) => \{\n(.*?)\n\};\n', js, re.S | re.M)
        self.assertIsNotNone(m, "no encontré el botón de armar")
        boton = m.group(1)
        pregunta = boton.find("if (!(await mismoModo())) return;")
        self.assertGreater(pregunta, -1)
        for despues in ('$("#log").innerHTML = ""; CURSOR = 0;', 'chip(f, "curso", "en curso");',
                        'await api("/api/correr"'):
            with self.subTest(despues=despues):
                self.assertGreater(boton.find(despues), pregunta)
        self.assertIn('body: JSON.stringify({ hoja: HOJA_ACT, usuario: $("#usuario").value, filas, '
                      'modo: MODO_PAGINA })', boton)


# Un DOM falso para correr en Node lo que la página hace con sus elementos: cada selector da siempre el mismo elemento.
DOM_FALSO = """
class El {
  constructor() { this.textContent = ""; this._html = ""; this.hidden = false; this.options = []; this.value = "";
                  this.abierto = 0; }
  set innerHTML(v) { this._html = v; if (v === "") this.options = []; }
  get innerHTML() { return this._html; }
  appendChild(o) { this.options.push(o); }
  addEventListener() {}
  showModal() { this.abierto++; }
}
const EL = {};
const $ = s => (EL[s] = EL[s] || new El());
let MARCADAS = [];
const document = { createElement: () => ({}), querySelectorAll: () => MARCADAS };
let FEED = [], ESTADOS = [], RUTAS = [], RESPUESTAS = {};
function feed(t, c, e) { FEED.push([t, c, e]); }
function estado(t) { ESTADOS.push(t); }
function pintarWidgets() {}
async function api(ruta) {
  RUTAS.push(ruta);
  const r = RESPUESTAS[ruta.split("?")[0]];
  if (r instanceof Error) throw r;
  return r;
}
function fallo(texto, status) { const e = new Error(texto); e.status = status; return e; }
const aviso = () => [$("#aviso-panel").textContent, $("#aviso-panel").hidden];
"""


class TestLoQueFaltaALaVista(soporte.CasoAQ):
    """Lo que falta para empezar, o por qué un botón no hizo nada, se ve en el panel (decisión de Marcelo, encargo 61,
    CICLO-clon-nuevo-y-config.md): en el aviso bajo la nota del modo, que siempre se ve. Medido en un clon nuevo: sin
    config.json, la página decía por qué solo en el registro plegado (y antes de cargar una planilla ni lo mostraba), y
    Credenciales, Operador, «Solo iniciar sesión» y «Armar» no hacían nada a la vista. Se corre en Node, con un DOM
    falso."""

    def trozo(self, patron):
        m = re.search(patron, self.mod.JS_INDEX, re.S | re.M)
        self.assertIsNotNone(m, f"no encontré {patron[:40]} en JS_INDEX")
        return m.group(0)

    def funciones(self):
        return (self.trozo(r"^function esc\(s\) \{\n.*?\n\}\n")
                + self.trozo(r"^function notaVisible\(texto\) \{\n.*?\n\}\n")
                + self.trozo(r"^function avisoFijo\(texto, cls, etiqueta\) \{\n.*?\n\}\n")
                + self.trozo(r"^const SIN_OPERADOR = .*?;\n"))

    def test_el_aviso_se_ve_y_va_al_registro(self):
        guion = (DOM_FALSO + self.funciones() +
                 "const salida = [aviso()];\n"
                 "avisoFijo('falta algo'); salida.push(aviso());\n"
                 "avisoFijo('marca una', 'f-info', 'AVISO'); salida.push(aviso());\n"
                 "notaVisible(''); salida.push(aviso());\n"
                 "console.log(JSON.stringify([salida, FEED]));\n")
        self.assertEqual(correr_node(self, guion),
                         [[["", False], ["⚠ falta algo", False], ["⚠ marca una", False], ["", True]],
                          [["falta algo", "f-alerta", "REVISAR"], ["marca una", "f-info", "AVISO"]]])
        self.assertEqual(self.mod.HTML_INDEX.count('<p class="rs-aviso" id="aviso-panel" role="alert" hidden></p>'), 1)
        self.assertEqual(self.mod.CSS_INDEX.count(".rs-aviso {"), 1)

    def test_al_cargar_dice_lo_que_falta(self):
        arranque = self.trozo(r"^// ---------- arranque ----------\n\(async \(\) => \{\n.*?\n\}\)\(\);\n")
        arranque = "const arranque = " + arranque.split("\n", 1)[1][:-len("();\n")] + ";\n"
        casos = [{"error": "config.json roto"},
                 {"aviso": "lo creé", "usuarios": ["usuario1"]},
                 {"aviso": "", "usuarios": []},
                 {"aviso": "", "usuarios": ["usuario1"]}]
        guion = (DOM_FALSO + self.funciones() + "let MODO_PAGINA = null, CURSOR = 0, CORRIENDO = false;\n" + arranque +
                 "(async () => {\n"
                 "  const salida = [];\n"
                 f"  for (const c of {json.dumps(casos)}) {{\n"
                 "    for (const k in EL) delete EL[k];\n"
                 "    FEED = []; ESTADOS = [];\n"
                 "    RESPUESTAS['/api/config'] = c.error ? fallo(c.error, 500) :\n"
                 "      { version: 'v', modo_emision: false, aviso: c.aviso, usuarios: c.usuarios, navieras: [] };\n"
                 "    await arranque();\n"
                 "    salida.push([aviso(), $('#nota-modo').innerHTML, $('#navs').innerHTML, [...FEED], [...ESTADOS],\n"
                 "                 $('#usuario').options.length]);\n"
                 "  }\n"
                 "  // «Entrar a los portales», con la página cargada: sin naviera marcada, y con el login que falla.\n"
                 "  await $('#entrar').onclick({ stopPropagation() {} });\n"
                 "  const sinMarcar = aviso();\n"
                 "  MARCADAS = [{ checked: true, dataset: { nav: 'one' } }];\n"
                 "  RESPUESTAS['/api/login'] = fallo('Usuario x no está', 500);\n"
                 "  await $('#entrar').onclick({ stopPropagation() {} });\n"
                 "  salida.push([sinMarcar, aviso()]);\n"
                 "  console.log(JSON.stringify(salida));\n"
                 "})();\n")
        r = correr_node(self, guion)
        texto = "No pude leer la configuración: config.json roto"
        sin_operador = ("Todavía no hay ningún operador en config.json: créalo en Credenciales (la llave, arriba a la "
                        "derecha), con «+ Nuevo operador».")
        self.assertEqual(r[0], [["⚠ " + texto, False], "<b>Modo sin leer:</b> el panel no pudo leer su configuración, "
                                "y no arma reservas hasta que la lea.", f'<p class="nota">{texto}</p>',
                                [[texto, "f-alerta", "REVISAR"]], ["No pude leer la configuración"], 0])
        self.assertEqual([x[0] for x in r[1:4]], [["⚠ lo creé", False], ["⚠ " + sin_operador, False], ["", True]])
        self.assertEqual([x[1].startswith("<b>🛡️ Modo Seguro Activo:</b>") for x in r[1:4]], [True] * 3)
        self.assertEqual([x[3] for x in r[1:4]], [[], [], []])           # lo que dijo el panel ya está en su registro
        self.assertEqual(r[4], [["⚠ Marca al menos una naviera", False],
                                ["⚠ No pude entrar: Usuario x no está", False]])

    def test_credenciales_sin_leer_abren_el_cuadro_con_el_motivo(self):
        abrir = self.trozo(r"^async function abrirCred\(usuario, yaAbierto\) \{\n.*?\n\}\n")
        guion = (DOM_FALSO + self.funciones() + "let CRED = null; const dlg = $('#dlg-cred');\n" + abrir +
                 "(async () => {\n"
                 "  $('#cred-op').appendChild({}); $('#cred-filas').innerHTML = '<tr>vieja</tr>';\n"
                 "  RESPUESTAS['/api/credenciales'] = fallo('config.json roto', 500);\n"
                 "  await abrirCred('usuario1');\n"
                 "  const roto = [dlg.abierto, $('#cred-estado').textContent, $('#cred-op').options.length,\n"
                 "                $('#cred-filas').innerHTML, aviso(), [...FEED], CRED];\n"
                 "  await abrirCred('usuario1', true);\n"
                 "  roto.push(dlg.abierto);\n"
                 "  RESPUESTAS['/api/credenciales'] = { operadores: [], navieras: [] };\n"
                 "  await abrirCred('');\n"
                 "  const vacio = [dlg.abierto, $('#cred-estado').textContent, aviso()];\n"
                 "  RESPUESTAS['/api/credenciales'] = { operadores: ['usuario1'], navieras: [] };\n"
                 "  await abrirCred('usuario1');\n"
                 "  console.log(JSON.stringify([roto, vacio, [dlg.abierto, $('#cred-estado').textContent]]));\n"
                 "})();\n")
        texto = "No pude leer las credenciales: config.json roto"
        sin_operador = ("Todavía no hay ningún operador en config.json: créalo en Credenciales (la llave, arriba a la "
                        "derecha), con «+ Nuevo operador».")
        self.assertEqual(correr_node(self, guion),
                         [[1, texto, 0, "", ["⚠ " + texto, False], [[texto, "f-alerta", "REVISAR"]], None, 1],
                          [2, sin_operador, ["", True]], [3, ""]])

    def test_armar_y_entrar_avisan_a_la_vista(self):
        js = self.mod.JS_INDEX
        for trozo in ('avisoFijo("No pude arrancar: " + e.message);', 'avisoFijo("No pude entrar: " + e.message);',
                      'if (!navs.length) { avisoFijo("Marca al menos una naviera", "f-info", "AVISO"); return; }'):
            with self.subTest(trozo=trozo):
                self.assertEqual(js.count(trozo), 1)
        for viejo in ('feed("No pude arrancar', 'feed("No pude entrar', 'feed("Marca al menos',
                      'feed("No pude leer las credenciales'):
            with self.subTest(viejo=viejo):
                self.assertNotIn(viejo, js)
        # Armar limpia el aviso antes de preguntar el modo, como cada botón al empezar.
        m = re.search(r'^\$\("#wg-armar"\)\.onclick = async \(\) => \{\n(.*?)\n\};\n', js, re.S | re.M)
        boton = m.group(1)
        self.assertLess(boton.index('notaVisible("");'), boton.index("if (!(await mismoModo())) return;"))
        self.assertIn('if (!r.ok) { const e = new Error(await r.text()); e.status = r.status; throw e; }', js)


class TestMarcaDeLaSesion(soporte.CasoAQ):
    """La página manda la marca de la sesión del panel en cada pedido, y la renueva una vez si el panel se reinició
    (decisión de Marcelo, encargo 66, CICLO-viaje-y-origen.md). Se corre en Node, fuera del navegador."""

    def trozo(self, patron):
        m = re.search(patron, self.mod.JS_INDEX, re.S | re.M)
        self.assertIsNotNone(m, patron)
        return m.group(0)

    def funciones(self, *nombres):
        return "".join(self.trozo(rf"^(?:async )?function {n}\(.*?\) \{{\n.*?\n\}}\n") for n in nombres)

    def test_cada_pedido_con_la_marca_y_una_renovacion(self):
        guion = (r"""global.document = {querySelector: (s) => s === 'meta[name="aquashield-sesion"]'
  ? {getAttribute: (a) => (a === 'content' ? 'marca-vieja' : null)} : null};
""" + self.trozo(r"^const RX_SESION = .*?;\n") + "let SESION = sesionDeLaPagina();\n"
                  + self.funciones("sesionDeLaPagina", "conSesion", "renovarSesion", "pedir", "api") + r"""
const pedidos = [];
let panel = 'marca-nueva', pagina = 'marca-nueva', paginaFalla = false;
global.fetch = async (ruta, opts) => {
  const h = (opts && opts.headers) || {};
  pedidos.push([ruta, h['X-AquaShield-Sesion'] || null, h['Content-Type'] || null]);
  if (ruta === '/') {
    if (paginaFalla) throw new Error('sin red');
    return {ok: true, status: 200, text: async () => (pagina === null ? '<html></html>'
      : '<head><meta name="aquashield-sesion" content="' + pagina + '"></head>')};
  }
  const ok = h['X-AquaShield-Sesion'] === panel;
  return {ok, status: ok ? 200 : 403, text: async () => (ok ? '' : 'no viene de su página'), json: async () => ({ruta})};
};
const r = [];
const probar = async (ruta, opts) => {
  pedidos.length = 0;
  try { r.push([await api(ruta, opts), pedidos.slice(), SESION]); }
  catch (e) { r.push([e.status, e.message, pedidos.slice(), SESION]); }
};
(async () => {
  await probar('/api/estado');
  await probar('/api/correr', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: '{}'});
  panel = 'otra'; pagina = 'otra-mas';
  await probar('/api/config');
  await probar('/api/config');
  pagina = null; await probar('/api/config');
  paginaFalla = true; await probar('/api/config');
  console.log(JSON.stringify(r));
})();
""")
        no = "no viene de su página"
        pide = lambda marca: [["/api/config", marca, None], ["/", None, None]]
        self.assertEqual(correr_node(self, guion), [
            # La marca de la página, vieja: el panel contesta 403, la página lee la nueva de «/» y repite una vez.
            [{"ruta": "/api/estado"}, [["/api/estado", "marca-vieja", None], ["/", None, None],
                                       ["/api/estado", "marca-nueva", None]], "marca-nueva"],
            # Con las cabeceras que ya traía el pedido.
            [{"ruta": "/api/correr"}, [["/api/correr", "marca-nueva", "application/json"]], "marca-nueva"],
            # Repite una sola vez: si tampoco la acepta, el error.
            [403, no, pide("marca-nueva") + [["/api/config", "otra-mas", None]], "otra-mas"],
            # Sin una marca nueva en la página (la misma, ninguna, o la página no contesta), no repite.
            [403, no, pide("otra-mas"), "otra-mas"], [403, no, pide("otra-mas"), "otra-mas"],
            [403, no, pide("otra-mas"), "otra-mas"]])

    def test_dos_pedidos_a_la_vez_con_la_marca_vieja(self):
        # Dos pedidos salen a la vez con la marca de antes de que el panel se reiniciara: los dos reciben el 403, y los
        # dos repiten con la nueva (revisión del encargo 67). Hasta ahí el segundo veía la marca nueva, que ya había
        # leído el primero, como «la misma», no repetía, y su 403 llegaba al operador.
        guion = (r"""global.document = {querySelector: (s) => s === 'meta[name="aquashield-sesion"]'
  ? {getAttribute: (a) => (a === 'content' ? 'marca-vieja' : null)} : null};
""" + self.trozo(r"^const RX_SESION = .*?;\n") + "let SESION = sesionDeLaPagina();\n"
                  + self.funciones("sesionDeLaPagina", "conSesion", "renovarSesion", "pedir", "api") + r"""
const paginas = [];
global.fetch = async (ruta, opts) => {
  await new Promise(r => setImmediate(r));
  const h = (opts && opts.headers) || {};
  if (ruta === '/') {
    paginas.push(ruta);
    await new Promise(r => setImmediate(r));
    return {ok: true, status: 200, text: async () => '<meta name="aquashield-sesion" content="marca-nueva">'};
  }
  const ok = h['X-AquaShield-Sesion'] === 'marca-nueva';
  return {ok, status: ok ? 200 : 403, text: async () => (ok ? '' : 'no viene de su página'), json: async () => ({ruta})};
};
(async () => {
  const r = await Promise.all(['/api/estado', '/api/config', '/api/filas'].map(ruta =>
    api(ruta).catch(e => [e.status, e.message])));
  console.log(JSON.stringify([r, SESION, paginas.length]));
})();
""")
        # Cada uno lee la página una vez, y repite una vez.
        self.assertEqual(correr_node(self, guion), [[{"ruta": "/api/estado"}, {"ruta": "/api/config"},
                                                    {"ruta": "/api/filas"}], "marca-nueva", 3])

    def test_el_nombre_de_la_descarga(self):
        # El nombre, entero, de filename* si lo trae; si no, o si no se puede leer, de filename (revisión del encargo 67;
        # el panel manda los dos, _disposicion). La cabecera, la que arma el programa.
        d = self.mod._disposicion("Reservas – octubre 🐟 - resultados 14-10_0935.xlsx")
        guion = self.funciones("nombreDeDescarga") + "console.log(JSON.stringify([" + ", ".join(
            "nombreDeDescarga(" + json.dumps(c) + ")" for c in (
                d, 'attachment; filename="Plan.xlsx"', "attachment; filename=\"Plan.xlsx\"; filename*=UTF-8''%E2%80",
                "attachment; filename*=utf-8''Plan%20B.xlsx", None, "")) + "]));\n"
        self.assertEqual(correr_node(self, guion), ["Reservas – octubre 🐟 - resultados 14-10_0935.xlsx", "Plan.xlsx",
                                                    "Plan.xlsx", "Plan B.xlsx", "planilla - resultados.xlsx",
                                                    "planilla - resultados.xlsx"])

    def test_la_descarga_con_la_marca(self):
        # La planilla con los resultados llega por pedir, con la marca, y se guarda con el nombre que da el panel; un
        # error del panel queda a la vista. Hasta el encargo 66 era una navegación a /api/descargar, sin la marca.
        guion = (self.funciones("nombreDeDescarga") + r"""
const boton = {}; const $ = (s) => (s === '#wg-descargar' ? boton : null);
function apagado() { return false; }
const notas = [], llamadas = [], creados = [], tiempos = [];
function notaVisible(t) { notas.push(t); }
let respuesta;
async function pedir(ruta) { llamadas.push(ruta); if (respuesta instanceof Error) throw respuesta; return respuesta; }
global.document = {createElement: (tag) => { const a = {tag, clics: 0, quitado: false, click() { this.clics++; },
                                                         remove() { this.quitado = true; }}; creados.push(a); return a; },
                   body: {appendChild: () => {}}};
URL.createObjectURL = (b) => 'blob:' + b; URL.revokeObjectURL = () => {};
globalThis.setTimeout = (f, ms) => { tiempos.push(ms); };
""" + self.trozo(r'^\$\("#wg-descargar"\)\.onclick = async \(\) => \{\n.*?\n\};\n') + r"""
const r = [];
(async () => {
  respuesta = {ok: true, headers: {get: (h) => (h === 'Content-Disposition'
    ? 'attachment; filename="Prueba - resultados 14-10_0935.xlsx"' : null)}, blob: async () => 'PLANILLA'};
  await boton.onclick();
  r.push([llamadas.slice(), notas.slice(), creados.map(a => [a.tag, a.href, a.download, a.clics, a.quitado]),
          tiempos.slice()]);
  respuesta = {ok: false, text: async () => 'No hay planilla cargada.'}; notas.length = 0; creados.length = 0;
  await boton.onclick();
  r.push([notas.slice(), creados.length]);
  respuesta = new Error('sin red'); notas.length = 0;
  await boton.onclick();
  r.push([notas.slice(), creados.length, nombreDeDescarga(null), nombreDeDescarga('attachment')]);
  console.log(JSON.stringify(r));
})();
""")
        self.assertEqual(correr_node(self, guion), [
            [["/api/descargar"], [""], [["a", "blob:PLANILLA", "Prueba - resultados 14-10_0935.xlsx", 1, True]], [60000]],
            [["", "No hay planilla cargada."], 0],
            [["", "No pude descargar la planilla: sin red"], 0, "planilla - resultados.xlsx",
             "planilla - resultados.xlsx"]])
        self.assertNotIn('window.location = "/api/descargar"', self.mod.JS_INDEX)


if __name__ == "__main__":
    unittest.main()
