#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_scoring.py -- Pruebas automatizadas sobre los archivos de actividad `.pka`
(`Grupo_IPV6_Estudiante.pka`, `Grupo_IPV6_Maestro.pka`, `Grupo_IPV6_Diagnostico_Hito10.pka`)
y sus árboles de evaluación `<INITIALSETUP>` y `<COMPARISONS>`.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

RUTA_PRUEBAS = Path(__file__).resolve().parent
RUTA_MODULO = RUTA_PRUEBAS.parent
sys.path.insert(0, str(RUTA_MODULO / "scripts"))

from validar_pka import validar_archivo_pka


class PruebasScoringPKA(unittest.TestCase):
    """Suite de validación de los archivos `.pka` y del sistema de calificación automática."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.dir_salida = RUTA_MODULO / "salida"

    def test_01_pka_estudiante_valido(self) -> None:
        """Verifica Grupo_IPV6_Estudiante.pka (3 redes, 10 páginas, 89 puntos de evaluación)."""
        res = validar_archivo_pka(self.dir_salida / "Grupo_IPV6_Estudiante.pka")
        self.assertTrue(res["valido"], f"Errores: {res.get('errores')}")
        self.assertEqual(res["redes_embebidas"], 3)
        self.assertEqual(res["paginas_instrucciones"], 10)
        self.assertEqual(res["puntos_evaluacion"], 89)
        self.assertTrue(res["password_configurada"])

    def test_02_pka_maestro_valido(self) -> None:
        """Verifica Grupo_IPV6_Maestro.pka (3 redes resueltas, 10 páginas, 89 puntos)."""
        res = validar_archivo_pka(self.dir_salida / "Grupo_IPV6_Maestro.pka")
        self.assertTrue(res["valido"], f"Errores: {res.get('errores')}")
        self.assertEqual(res["redes_embebidas"], 3)
        self.assertEqual(res["paginas_instrucciones"], 10)
        self.assertEqual(res["puntos_evaluacion"], 89)

    def test_03_pka_diagnostico_hito10_valido(self) -> None:
        """Verifica Grupo_IPV6_Diagnostico_Hito10.pka (Troubleshooting Hito 10)."""
        res = validar_archivo_pka(self.dir_salida / "Grupo_IPV6_Diagnostico_Hito10.pka")
        self.assertTrue(res["valido"], f"Errores: {res.get('errores')}")
        self.assertEqual(res["redes_embebidas"], 3)
        self.assertEqual(res["paginas_instrucciones"], 10)
        self.assertEqual(res["puntos_evaluacion"], 89)


if __name__ == "__main__":
    unittest.main(verbosity=2)
