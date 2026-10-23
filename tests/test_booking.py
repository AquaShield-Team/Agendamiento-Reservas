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
    CONFIRMA_ONE = "Your booking has been successfully submitted!\nBooking Reference No.\nSCLG23456789\n"

    def num(self, pagina, nav="one"):
        return self.mod.numero_tras_envio(pagina, nav)

    def test_forma_medida_de_one(self):
        casos = {self.CONFIRMA_ONE: "SCLG23456789",
                 "Booking Reference No.: SCLG34567890": "SCLG34567890",
                 "booking reference no SCLG45678901": "SCLG45678901",       # la etiqueta, en cualquier caja
                 "Booking Reference No.\nSCLG1000005": "",                  # 7 dígitos
                 "Booking Reference No.\nSCLG100000066": "",                # 9 dígitos
                 "Booking Reference No.\nABCD10000007": "",                 # otro prefijo
                 "Booking Reference No.\nsclg12345678": "",                 # el número distingue mayúsculas
                 "SCLG56789012 · Your booking is confirmed": "",            # sin la etiqueta
                 "Booking Parties · Review Booking · New Booking": ""}
        for texto, esperado in casos.items():
            with self.subTest(texto=texto[:40]):
                self.assertEqual(self.num(P(texto)), esperado)

    def test_forma_medida_de_msc(self):
        casos = {"Your eBooking request has been successfully created and submitted for agency confirmation.\n"
                 "Your eBooking number is :\n\nEBKG67890123\n": "EBKG67890123",
                 "your ebooking number is EBKG78901234": "EBKG78901234",   # la etiqueta, en cualquier caja
                 "Your eBooking number is :\nEBKG2000004": "",              # 7 dígitos
                 "Your eBooking number is :\nEBKG200000055": "",            # 9 dígitos
                 "Your eBooking number is :\nMSCX20000006": "",             # otro prefijo
                 "Your eBooking number is :\nebkg20000007": "",             # el número distingue mayúsculas
                 "Booking reference: EBKG89012345": "",                     # otra etiqueta
                 "Service Contract Number RS00000009 · EBKG90123456": ""}   # sin la etiqueta
        for texto, esperado in casos.items():
            with self.subTest(texto=texto[:40]):
                self.assertEqual(self.num(P(texto), "msc"), esperado)

    def test_forma_medida_de_hyundai(self):
        casos = {"A Tentative Booking has been created.\n- Created tentative booking number: SCLA23456789\n"
                 "The created tentative booking will be reviewed by HMM staff": "SCLA23456789",
                 "created tentative booking number SCLA34567890": "SCLA34567890",   # la etiqueta, en cualquier caja
                 "Created tentative booking number: SCLA1000004": "",               # 7 dígitos
                 "Created tentative booking number: SCLA100000055": "",             # 9 dígitos
                 "Created tentative booking number: SCLG01234567": "",              # otro prefijo
                 "Created tentative booking number: scla10000007": "",              # el número distingue mayúsculas
                 "Booking No: SCLA12345678": "",                                    # otra etiqueta
                 "Service Contract CCL0000000 · SCLA98765432": ""}                  # sin la etiqueta
        for texto, esperado in casos.items():
            with self.subTest(texto=texto[:40]):
                self.assertEqual(self.num(P(texto), "hyundai"), esperado)

    def test_forma_medida_de_maersk(self):
        casos = {"Booking confirmed\nBooking number: 272345678\nThank you, for booking with us": "272345678",
                 "booking number 273456789": "273456789",                  # la etiqueta, en cualquier caja
                 "Booking number: 27000004": "",                           # 8 dígitos
                 "Booking number: 2700000055": "",                         # 10 dígitos
                 "Booking number: SCLA01234567": "",                       # letras
                 "Your booking 274567890 was created": "",                 # otra etiqueta
                 "VESSEL/VOYAGE · 638E · 275678901 · 49 days": ""}         # sin la etiqueta
        for texto, esperado in casos.items():
            with self.subTest(texto=texto[:40]):
                self.assertEqual(self.num(P(texto), "maersk"), esperado)

    def test_lee_los_marcos(self):
        pagina = P("Booking Parties", frames=[Marco("nada"), Marco(self.CONFIRMA_ONE)])
        self.assertEqual(self.num(pagina), "SCLG23456789")

    def test_un_marco_que_falla_no_tapa_a_los_demas(self):
        class Rompe(P):
            def evaluate(self, js, *a):
                raise RuntimeError("marco cerrado")
        self.assertEqual(self.num(Rompe("", frames=[Rompe(""), Marco(self.CONFIRMA_ONE)])), "SCLG23456789")
        self.assertEqual(self.num(Rompe("", frames=[Rompe("")])), "")

    def test_reintenta_hasta_que_aparece(self):
        lecturas = []

        def texto(js, *a):
            lecturas.append(js)
            return self.CONFIRMA_ONE if len(lecturas) >= 4 else "cargando"
        pagina = P(texto)
        self.assertEqual(self.num(pagina), "SCLG23456789")
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

    def test_frase_de_cosco_que_dice_que_se_envio(self):
        # COSCO no muestra una confirmación con número: dice que la reserva se envió, con una referencia (encargo 77; la
        # forma, medida en el marco del formulario el 22-10), que es el número de la reserva (decisión de Marcelo,
        # encargo 78). referencia_tras_envio la lee como el número: la página, sus marcos y sus raíces shadow, con
        # reintentos. Referencias inventadas, con las cifras a la vista.
        ref = lambda pagina, nav="cosco": self.mod.referencia_tras_envio(pagina, nav)
        envio = 'Booking CD1234567890 has been submitted successfully! Please check booking status in the "To do list".'
        self.assertEqual(ref(P("New Booking", frames=[Marco("nada"), Marco(envio)])), "CD1234567890")
        self.assertEqual(ref(P("booking   CD0000000000 \t has been submitted successfully")), "CD0000000000")
        for otra in ("Booking CD123456789 has been submitted successfully", "Booking CD1234567890 was submitted",
                     "Booking Cd1234567890 has been submitted successfully", "New Booking",
                     "booking CD0000000000\nhas been submitted successfully"):    # partida en dos líneas
            with self.subTest(otra=otra):
                self.assertEqual(ref(P(otra)), "")
        # La frase es de COSCO: ONE no la lee, y sin forma no espera; CMA tiene la suya (encargo 78), que no es esta.
        pagina = P(envio)
        self.assertEqual((ref(pagina, "one"), pagina.esperas), ("", 0))
        self.assertEqual(self.mod.referencia_tras_envio(pagina, "cma", espera=0), "")
        # Sin la frase, espera lo mismo que el número.
        pagina = P("New Booking")
        self.assertEqual((ref(pagina), pagina.esperas), ("", self.mod.BKG_ESPERA_SEG))

    def test_frase_de_cma_que_dice_que_se_envio(self):
        # Desde el encargo 78 (decisión de Marcelo), CMA-CGM: su página tras el envío dice «Booking enviado» y trae una
        # línea con «Booking» y la referencia sola, tres letras y 7 cifras, como se leyó el 22-10. Las dos señales y en ese
        # orden: «Booking enviado» al final de su línea (como en la página medida, después de otro «Booking»), y la
        # referencia después; una sola no basta. Se lee como la de COSCO: la página y sus marcos. Referencias inventadas,
        # con las cifras a la vista.
        ref = lambda pagina: self.mod.referencia_tras_envio(pagina, "cma", espera=0)
        envio = ("Booking Booking enviado\nSu reserva aún no está confirmada.\n"
                 "Booking QXZ1234567\nBuque\n")
        self.assertEqual(ref(P("Click & Book", frames=[Marco("nada"), Marco(envio)])), "QXZ1234567")
        self.assertEqual(ref(P("Booking  enviado \nnada\n \tBooking\xa0ABC0000000 \n")), "ABC0000000")
        for caso, otra in {"sin «Booking enviado»": "Su reserva aún no está confirmada.\nBooking QXZ1234567\n",
                           # De la revisión de código del encargo 78: las dos señales, atadas.
                           "la referencia antes del título": "Booking ABC0000000\nBooking enviado\n",
                           "«Booking enviado» en una frase": "Su Booking enviado ayer\nBooking QXZ1234567\n",
                           # De la revisión de seguridad: el título, al principio de su línea.
                           "texto antes del título": "Error: Booking enviado\nBooking QXZ1234567\n",
                           "una letra con tilde pegada": "éBooking enviado\nBooking QXZ1234567\n",
                           "otra palabra antes del título": "Pre Booking enviado\nBooking QXZ1234567\n",
                           "«enviados»": "Booking enviados\nBooking QXZ1234567\n",
                           "«enviado» en otra línea": "Booking\nenviado\nBooking QXZ1234567\n",
                           "«Booking enviado» pegado": "PreBooking enviado\nBooking QXZ1234567\n",
                           "sin la línea de la referencia": "Booking enviado\nSu reserva aún no está confirmada.\n",
                           "la referencia con más texto": "Booking enviado\nBooking QXZ1234567 Submitted\n",
                           "texto antes de «Booking»": "Booking enviado\nTu Booking QXZ1234567\n",
                           "dos letras": "Booking enviado\nBooking QX1234567\n",
                           "8 cifras": "Booking enviado\nBooking QXZ12345678\n",
                           "en minúsculas": "Booking enviado\nBooking qxz1234567\n",
                           "«booking enviado» en minúsculas": "booking enviado\nBooking QXZ1234567\n"}.items():
            with self.subTest(caso=caso):
                self.assertEqual(ref(P(otra)), "")
        # La frase es de CMA: COSCO no la lee.
        self.assertEqual(self.mod.referencia_tras_envio(P(envio), "cosco", espera=0), "")
        # De la revisión de seguridad: con dos referencias distintas en la pantalla (en la página o en un marco), no se
        # sabe cuál es la de esta reserva; la misma dos veces, sí.
        for pagina in (P(envio + "Booking ABC0000000\n"), P(envio, frames=[Marco("Booking ABC0000000")])):
            with self.subTest(pagina=pagina.texto):
                with self.assertRaises(self.mod.ReferenciaAmbigua) as e:
                    ref(pagina)
                self.assertEqual(e.exception.referencias, ["ABC0000000", "QXZ1234567"])
        self.assertEqual(ref(P(envio, frames=[Marco(envio)])), "QXZ1234567")
        # El número de las navieras con forma medida no mira eso: como antes, el primero.
        self.assertEqual(self.num(P(self.CONFIRMA_ONE + "Booking Reference No. SCLG34567890")), "SCLG23456789")


class TestNumeroLimpio(soporte.CasoAQ):
    """Los patrones se prueban con estado EMITIDA: desde f03bb75 solo una EMITIDA tiene número, y desde el encargo 78
    también una EMITIDA – CONFIRMAR POR CORREO, solo con el de su «(Booking: …)» (test_envio)."""

    def limpio(self, r):
        return self.mod._extraer_bkg_limpio(r)

    def emitida(self, **r):
        return self.limpio({"estado": "EMITIDA", **r})

    def test_campo_booking_manda(self):
        self.assertEqual(self.emitida(booking="ABC123456", detalle="SCLG87654321"), "ABC123456")
        self.assertEqual(self.emitida(booking="en proceso", detalle="ok SCLG87654321 ok"), "SCLG87654321")

    def test_patrones_por_naviera(self):
        self.assertEqual(self.emitida(detalle="HYUNDAI SCLA76543210"), "SCLA76543210")
        self.assertEqual(self.emitida(detalle="MAERSK Bkg: 276789012"), "276789012")
        self.assertEqual(self.emitida(detalle="MAERSK 272345678 listo"), "272345678")   # solo «27…»
        # Desde el 22-10 MAERSK da números que empiezan con 28 (encargo 77): suelto no lo ve la regla de los «27…», y
        # como lo escribe _resultado_envio, «(Booking: …)», lo toma la regla de la etiqueta.
        self.assertEqual(self.emitida(detalle="MAERSK 282345678 listo"), "")
        self.assertEqual(self.emitida(detalle="MAERSK emitida con éxito (Booking: 282345678)"), "282345678")
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
