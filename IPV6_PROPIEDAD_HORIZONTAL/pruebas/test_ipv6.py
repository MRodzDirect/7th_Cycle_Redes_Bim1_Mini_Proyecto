#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_ipv6.py -- Pruebas unitarias de auditoría de protocolos IPv6 (SLAAC, DHCPv6
Stateless, DHCPv6 Stateful, subinterfaces 802.1Q, VLANs, DNS AAAA y fallos Hito 10).
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

RUTA_PRUEBAS = Path(__file__).resolve().parent
RUTA_MODULO = RUTA_PRUEBAS.parent
sys.path.insert(0, str(RUTA_MODULO / "scripts"))

from validar_ipv6 import auditar_red_diagnostico_hito10, auditar_red_resuelta_ipv6


class PruebasConfiguracionIPv6(unittest.TestCase):
    """Suite de pruebas sobre la configuración IPv6 en la red resuelta y de diagnóstico."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.dir_salida = RUTA_MODULO / "salida"

    def test_01_auditoria_ipv6_red_resuelta(self) -> None:
        """Verifica SLAAC, DHCPv6 Stateless (O=1), DHCPv6 Stateful (M=1), VLANs y DNS AAAA."""
        rep = auditar_red_resuelta_ipv6(self.dir_salida / "topologia_resuelta.pkt")
        self.assertTrue(rep["valido"], f"Errores IPv6: {rep.get('errores')}")
        verif = rep["verificaciones"]
        self.assertTrue(verif["r1_ipv6_unicast_routing"])
        for vlan in (10, 20, 30, 40, 50):
            self.assertTrue(verif[f"r1_subif_vlan_{vlan}"])
        self.assertTrue(verif["r1_pool_stateful_prefix"])
        self.assertTrue(verif["sw1_trunk_gi0_1"])
        self.assertTrue(verif["srv_dns_habilitado"])
        self.assertTrue(verif["srv_dns_base_datos_limpia"])

    def test_02_auditoria_tres_fallos_hito10(self) -> None:
        """Verifica que la red de diagnóstico del Hito 10 contenga los 3 fallos previstos."""
        rep = auditar_red_diagnostico_hito10(
            self.dir_salida / "topologia_diagnostico_hito10.pkt"
        )
        self.assertTrue(rep["valido"], f"Fallo en diagnóstico Hito 10: {rep}")
        self.assertTrue(rep["fallo_1_vlan40_omitida_en_troncal"])
        self.assertTrue(rep["fallo_2_flag_o_omitido_en_gi0_0_20"])
        self.assertTrue(rep["fallo_3_dhcp_server_omitido_en_gi0_0_30"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
