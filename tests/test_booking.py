# -*- coding: utf-8 -*-
"""Número de booking: numero_tras_envio (la forma medida de cada naviera en la página de
confirmación) y _extraer_bkg_limpio (lo que el panel muestra y escribe). Textos inventados con
la forma de cada naviera. Fotografía, rarezas incluidas:
- _extraer_bkg_limpio devuelve «Templates» como número (la palabra no está en su lista negra).
  Desde f03bb75 solo lo hace con una EMITIDA, y COSCO nunca llega a EMITIDA sin forma medida.
(Hasta 42247d4 existía extraer_numero_booking, el lector viejo de CMA, COSCO y los patrones
genéricos. Ningún reservador lo usaba y se borró con sus pruebas: CICLO-cola-nueve-items.md.)
"""
import unittest

import soporte

P = soporte.PaginaFalsa


class Marco(P):
    """Un marco de la página: se lee igual que la página."""


class TestNumeroTrasEnvio(soporte.CasoAQ):
    """numero_tras_envio: la forma medida en las capturas, leída en la página, sus
    marcos y sus raíces shadow, con reintentos. Números inventados con la forma medida."""
    CONFIRMA_ONE = "Your booking has been successfully submitted!\nBooking Reference No.\nSCLG10000002\n"

    def num(self, pagina, nav="one"):
        return self.mod.numero_tras_envio(pagina, nav)

    def test_forma_medida_de_one(self):
        casos = {self.CONFIRMA_ONE: "SCLG10000002",
                 "Booking Reference No.: SCLG10000003": "SCLG10000003",
                 "booking reference no SCLG10000004": "SCLG10000004",       # la etiqueta, en cualquier caja
                 "Booking Reference No.\nSCLG1000005": "",                  # 7 dígitos
                 "Booking Reference No.\nSCLG100000066": "",                # 9 dígitos
                 "Booking Reference No.\nABCD10000007": "",                 # otro prefijo
                 "Booking Reference No.\nsclg10000008": "",                 # el número distingue mayúsculas
                 "SCLG10000009 · Your booking is confirmed": "",            # sin la etiqueta
                 "Booking Parties · Review Booking · New Booking": ""}
        for texto, esperado in casos.items():
            with self.subTest(texto=texto[:40]):
                self.assertEqual(self.num(P(texto)), esperado)

    def test_forma_medida_de_msc(self):
        casos = {"Your eBooking request has been successfully created and submitted for agency confirmation.\n"
                 "Your eBooking number is :\n\nEBKG20000002\n": "EBKG20000002",
                 "your ebooking number is EBKG20000003": "EBKG20000003",   # la etiqueta, en cualquier caja
                 "Your eBooking number is :\nEBKG2000004": "",              # 7 dígitos
                 "Your eBooking number is :\nEBKG200000055": "",            # 9 dígitos
                 "Your eBooking number is :\nMSCX20000006": "",             # otro prefijo
                 "Your eBooking number is :\nebkg20000007": "",             # el número distingue mayúsculas
                 "Booking reference: EBKG20000008": "",                     # otra etiqueta
                 "Service Contract Number RS00000009 · EBKG20000010": ""}   # sin la etiqueta
        for texto, esperado in casos.items():
            with self.subTest(texto=texto[:40]):
                self.assertEqual(self.num(P(texto), "msc"), esperado)

    def test_forma_medida_de_hyundai(self):
        casos = {"A Tentative Booking has been created.\n- Created tentative booking number: SCLA10000002\n"
                 "The created tentative booking will be reviewed by HMM staff": "SCLA10000002",
                 "created tentative booking number SCLA10000003": "SCLA10000003",   # la etiqueta, en cualquier caja
                 "Created tentative booking number: SCLA1000004": "",               # 7 dígitos
                 "Created tentative booking number: SCLA100000055": "",             # 9 dígitos
                 "Created tentative booking number: SCLG10000006": "",              # otro prefijo
                 "Created tentative booking number: scla10000007": "",              # el número distingue mayúsculas
                 "Booking No: SCLA10000008": "",                                    # otra etiqueta
                 "Service Contract CCL0000009 · SCLA10000010": ""}                  # sin la etiqueta
        for texto, esperado in casos.items():
            with self.subTest(texto=texto[:40]):
                self.assertEqual(self.num(P(texto), "hyundai"), esperado)

    def test_forma_medida_de_maersk(self):
        casos = {"Booking confirmed\nBooking number: 270000002\nThank you, for booking with us": "270000002",
                 "booking number 270000003": "270000003",                  # la etiqueta, en cualquier caja
                 "Booking number: 27000004": "",                           # 8 dígitos
                 "Booking number: 2700000055": "",                         # 10 dígitos
                 "Booking number: SCLA10000006": "",                       # letras
                 "Your booking 270000007 was created": "",                 # otra etiqueta
                 "VESSEL/VOYAGE · 638E · 270000008 · 49 days": ""}         # sin la etiqueta
        for texto, esperado in casos.items():
            with self.subTest(texto=texto[:40]):
                self.assertEqual(self.num(P(texto), "maersk"), esperado)

    def test_lee_los_marcos(self):
        pagina = P("Booking Parties", frames=[Marco("nada"), Marco(self.CONFIRMA_ONE)])
        self.assertEqual(self.num(pagina), "SCLG10000002")

    def test_un_marco_que_falla_no_tapa_a_los_demas(self):
        class Rompe(P):
            def evaluate(self, js, *a):
                raise RuntimeError("marco cerrado")
        self.assertEqual(self.num(Rompe("", frames=[Rompe(""), Marco(self.CONFIRMA_ONE)])), "SCLG10000002")
        self.assertEqual(self.num(Rompe("", frames=[Rompe("")])), "")

    def test_reintenta_hasta_que_aparece(self):
        lecturas = []

        def texto(js, *a):
            lecturas.append(js)
            return self.CONFIRMA_ONE if len(lecturas) >= 4 else "cargando"
        pagina = P(texto)
        self.assertEqual(self.num(pagina), "SCLG10000002")
        self.assertEqual((len(lecturas), pagina.esperas), (4, 3))
        # Lee también las raíces shadow. El JavaScript no corre offline: se fija su forma.
        self.assertIn("if (e.shadowRoot) {", lecturas[0])
        self.assertIn("visitar(e.shadowRoot);", lecturas[0])

    def test_sin_numero_espera_lo_justo(self):
        pagina = P("Booking Parties")
        self.assertEqual(self.num(pagina), "")
        self.assertEqual(pagina.esperas, self.mod.BKG_ESPERA_SEG)
        self.assertEqual(self.mod.BKG_ESPERA_SEG, 15)

    def test_naviera_sin_forma_medida_no_lee(self):
        pagina = P(self.CONFIRMA_ONE)
        self.assertEqual((self.num(pagina, "cma"), self.num(pagina, "cosco"), pagina.esperas), ("", "", 0))


class TestNumeroLimpio(soporte.CasoAQ):
    """Los patrones se prueban con estado EMITIDA: desde f03bb75 solo una EMITIDA tiene número."""

    def limpio(self, r):
        return self.mod._extraer_bkg_limpio(r)

    def emitida(self, **r):
        return self.limpio({"estado": "EMITIDA", **r})

    def test_campo_booking_manda(self):
        self.assertEqual(self.emitida(booking="ABC123456", detalle="SCLG00000001"), "ABC123456")
        self.assertEqual(self.emitida(booking="en proceso", detalle="ok SCLG00000001 ok"), "SCLG00000001")

    def test_patrones_por_naviera(self):
        self.assertEqual(self.emitida(detalle="HYUNDAI SCLA00000002"), "SCLA00000002")
        self.assertEqual(self.emitida(detalle="MAERSK Bkg: 270000001"), "270000001")
        self.assertEqual(self.emitida(detalle="MAERSK 270000002 listo"), "270000002")   # solo «27…»
        self.assertEqual(self.emitida(detalle="x EBKG0000003 y"), "EBKG0000003")
        self.assertEqual(self.emitida(detalle="Reference No: REFFALSO55"), "REFFALSO55")

    def test_sin_numero(self):
        self.assertEqual(self.emitida(detalle="CMA emitida; Bkg: Ver captura"), "")
        self.assertEqual(self.emitida(detalle="COSCO emitida con éxito (Booking: en proceso)"), "")
        self.assertEqual(self.limpio({}), "")
        self.assertEqual(self.limpio(None), "")

    def test_templates_pasa_como_numero(self):
        self.assertEqual(self.emitida(detalle="COSCO emitida con éxito (Booking: Templates)"), "Templates")

    def test_solo_una_emitida_tiene_numero(self):
        # Hasta f03bb75 el número se tomaba del detalle de cualquier estado, y un error del portal
        # que citara un código lo llevaba en verde a «N° de reserva emitida».
        r = {"booking": "ABC123456", "detalle": "el portal mostró un error: «Booking: COSFALSO9876 ya existe»"}
        for estado in ("ENVIADA – REVISAR EN PORTAL", "NO ENVIADA", "OK-EJEMPLO", "REVISAR", "ERROR", "EN CURSO", ""):
            with self.subTest(estado=estado):
                self.assertEqual(self.limpio({"estado": estado, **r}), "")
        self.assertEqual(self.limpio({"estado": "EMITIDA", "detalle": r["detalle"]}), "COSFALSO9876")


class TestLectorViejo(soporte.CasoAQ):
    def test_ya_no_existe(self):
        # Ningún reservador usaba extraer_numero_booking: se borró con sus pruebas (CICLO-cola-nueve-items.md).
        self.assertFalse(hasattr(self.mod, "extraer_numero_booking"))


if __name__ == "__main__":
    unittest.main()
