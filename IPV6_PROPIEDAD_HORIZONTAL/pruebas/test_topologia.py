#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_topologia.py -- Pruebas automatizadas sobre las topologías `.pkt` generadas
(`topologia_inicial.pkt`, `topologia_resuelta.pkt` y `topologia_diagnostico_hito10.pkt`).
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

RUTA_PRUEBAS = Path(__file__).resolve().parent
RUTA_MODULO = RUTA_PRUEBAS.parent
sys.path.insert(0, str(RUTA_MODULO / "scripts"))

from validar_pka import validar_archivo_pkt


class PruebasTopologiaPKT(unittest.TestCase):
    """Suite de validación estructural y física de las topologías `.pkt`."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.dir_salida = RUTA_MODULO / "salida"

    def test_01_topologia_inicial_valida(self) -> None:
        """Verifica contenedor EAX, 14 dispositivos, 13 enlaces y limpieza en topologia_inicial.pkt."""
        res = validar_archivo_pkt(self.dir_salida / "topologia_inicial.pkt")
        self.assertTrue(res["valido"], f"Errores: {res.get('errores')}")
        self.assertEqual(res["dispositivos"], 14)
        self.assertEqual(res["enlaces"], 13)

    def test_02_topologia_resuelta_valida(self) -> None:
        """Verifica contenedor EAX, 14 dispositivos, 13 enlaces y limpieza en topologia_resuelta.pkt."""
        res = validar_archivo_pkt(self.dir_salida / "topologia_resuelta.pkt")
        self.assertTrue(res["valido"], f"Errores: {res.get('errores')}")
        self.assertEqual(res["dispositivos"], 14)
        self.assertEqual(res["enlaces"], 13)

    def test_03_topologia_diagnostico_hito10_valida(self) -> None:
        """Verifica contenedor EAX, 14 dispositivos y 13 enlaces en topologia_diagnostico_hito10.pkt."""
        res = validar_archivo_pkt(self.dir_salida / "topologia_diagnostico_hito10.pkt")
        self.assertTrue(res["valido"], f"Errores: {res.get('errores')}")
        self.assertEqual(res["dispositivos"], 14)
        self.assertEqual(res["enlaces"], 13)


if __name__ == "__main__":
    unittest.main(verbosity=2)
