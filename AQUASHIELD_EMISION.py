"""
AQUASHIELD - Modo Emisión Real de Reservas
AquaChile - Plataforma AQUASHIELD

Este módulo inicializa AQUASHIELD con la variable de entorno
AQUASHIELD_EMITIR=1 activada, permitiendo la emisión y confirmación
definitiva de reservas en los portales navieros (ONE, MSC, CMA-CGM,
COSCO, HYUNDAI y MAERSK).
"""
import os
import sys

# Forzar el modo de emisión real antes de cargar AQUASHIELD
os.environ["AQUASHIELD_EMITIR"] = "1"

import AQUASHIELD

if __name__ == "__main__":
    AQUASHIELD.main()
