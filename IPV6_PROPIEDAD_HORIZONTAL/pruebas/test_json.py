#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_json.py -- Pruebas unitarias de validación del archivo declarativo `escenario.json`,
subredes IPv6, VLANs, dispositivos, enlaces y archivos de instrucciones HTML.
"""

from __future__ import annotations

import ipaddress
import json
import sys
import unittest
from pathlib import Path

RUTA_PRUEBAS = Path(__file__).resolve().parent
RUTA_MODULO = RUTA_PRUEBAS.parent
sys.path.insert(0, str(RUTA_MODULO / "scripts"))

from preparar_spec import RUTA_ESCENARIO_DEFAULT, preparar_especificacion, validar_escenario


class PruebasEspecificacionJSON(unittest.TestCase):
    """Suite de pruebas sobre la especificación declarativa `escenario.json`."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = preparar_especificacion(RUTA_ESCENARIO_DEFAULT)

    def test_01_validacion_sin_errores(self) -> None:
        """Verifica que `validar_escenario` devuelva cero errores."""
        errores = validar_escenario(self.spec, RUTA_MODULO)
        self.assertEqual(errores, [])

    def test_02_cinco_departamentos_y_metodos_ipv6(self) -> None:
        """Verifica los 5 departamentos, sus VLANs (10..50) y métodos SLAAC/Stateless/Stateful."""
        deptos = self.spec["departamentos"]
        self.assertEqual(len(deptos), 5)
        esperado = {
            1: (10, "2001:DB8:ACAD:10::/64", "SLAAC", False, False),
            2: (20, "2001:DB8:ACAD:20::/64", "DHCPv6 Stateless", False, True),
            3: (30, "2001:DB8:ACAD:30::/64", "DHCPv6 Stateful", True, False),
            4: (40, "2001:DB8:ACAD:40::/64", "DHCPv6 Stateless", False, True),
            5: (50, "2001:DB8:ACAD:50::/64", "SLAAC", False, False),
        }
        for d in deptos:
            num = d["numero"]
            vlan, prefijo, metodo, m_flag, o_flag = esperado[num]
            self.assertEqual(d["vlan_id"], vlan)
            self.assertEqual(d["prefijo"], prefijo)
            self.assertEqual(d["metodo"], metodo)
            self.assertEqual(d["ra_managed_flag"], m_flag)
            self.assertEqual(d["ra_other_flag"], o_flag)
            red = ipaddress.IPv6Network(d["prefijo"], strict=True)
            self.assertEqual(red.prefixlen, 64)

    def test_03_catorce_dispositivos_y_trece_enlaces(self) -> None:
        """Verifica el inventario exacto de 14 dispositivos y 13 enlaces."""
        self.assertEqual(len(self.spec["devices"]), 14)
        self.assertEqual(len(self.spec["links"]), 13)

    def test_04_diez_hitos_html_cargados(self) -> None:
        """Verifica que las 10 páginas HTML de hitos existan y tengan contenido válido."""
        self.assertEqual(len(self.spec["instructions"]), 10)
        for idx, html in enumerate(self.spec["instructions"], start=1):
            self.assertIn("<html", html.lower())
            self.assertIn(f"Hito {idx}", html)


if __name__ == "__main__":
    unittest.main(verbosity=2)
