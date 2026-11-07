#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validar_ipv6.py -- Auditor técnico de direccionamiento dinámico IPv6 (SLAAC, DHCPv6
Stateless, DHCPv6 Stateful, subinterfaces 802.1Q, VLANs y DNS AAAA) sobre las
topologías generadas.
"""

from __future__ import annotations

import os
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import compat_windows
import pt9


def auditar_red_resuelta_ipv6(ruta_pkt: str | os.PathLike) -> dict[str, Any]:
    """Audita la configuración IPv6 completa de `topologia_resuelta.pkt`."""
    ruta = Path(ruta_pkt)
    xml_texto = pt9.decode(str(ruta), "pkt", verify_tag=True).decode("utf-8")
    raiz = ET.fromstring(xml_texto)

    errores: list[str] = []
    verificaciones: dict[str, bool] = {}

    dispositivos = {
        (d.findtext("ENGINE/NAME") or ""): d
        for d in raiz.findall(".//NETWORK/DEVICES/DEVICE")
    }

    # 1. Auditar Router R1
    r1 = dispositivos.get("R1")
    if r1 is None:
        errores.append("No se encontró el router R1")
    else:
        lineas_r1 = [
            (l.text or "") for l in r1.findall(".//ENGINE/RUNNINGCONFIG/LINE")
        ]
        texto_r1 = "\n".join(lineas_r1)

        verificaciones["r1_ipv6_unicast_routing"] = "ipv6 unicast-routing" in texto_r1
        if not verificaciones["r1_ipv6_unicast_routing"]:
            errores.append("R1 no tiene habilitado 'ipv6 unicast-routing'")

        # Verificar las 5 subinterfaces .10 a .50
        for vlan, metodo, flag_esperado, pool_esperado in (
            (10, "SLAAC", None, None),
            (20, "DHCPv6 Stateless", "ipv6 nd other-config-flag", "DEPT2_STATELESS"),
            (30, "DHCPv6 Stateful", "ipv6 nd managed-config-flag", "DEPT3_STATEFUL"),
            (40, "DHCPv6 Stateless", "ipv6 nd other-config-flag", "DEPT4_STATELESS"),
            (50, "SLAAC", None, None),
        ):
            subif = f"interface GigabitEthernet0/0.{vlan}"
            encap = f"encapsulation dot1Q {vlan}"
            addr = f"ipv6 address 2001:DB8:ACAD:{vlan}::1/64"
            ok_subif = (subif in texto_r1) and (encap in texto_r1) and (addr in texto_r1)
            verificaciones[f"r1_subif_vlan_{vlan}"] = ok_subif
            if not ok_subif:
                errores.append(f"R1: configuración incompleta en {subif}")

            if flag_esperado and flag_esperado not in texto_r1:
                errores.append(f"R1: falta '{flag_esperado}' para VLAN {vlan} ({metodo})")
            if pool_esperado:
                if f"ipv6 dhcp pool {pool_esperado}" not in texto_r1:
                    errores.append(f"R1: falta definición del pool '{pool_esperado}'")
                if f"ipv6 dhcp server {pool_esperado}" not in texto_r1:
                    errores.append(f"R1: falta asociación 'ipv6 dhcp server {pool_esperado}'")

        verificaciones["r1_pool_stateful_prefix"] = (
            "address prefix 2001:DB8:ACAD:30::/64" in texto_r1
        )
        if not verificaciones["r1_pool_stateful_prefix"]:
            errores.append("R1: el pool DEPT3_STATEFUL no contiene 'address prefix 2001:DB8:ACAD:30::/64'")

    # 2. Auditar Switch SW1
    sw1 = dispositivos.get("SW1")
    if sw1 is None:
        errores.append("No se encontró el switch SW1")
    else:
        lineas_sw1 = [
            (l.text or "") for l in sw1.findall(".//ENGINE/RUNNINGCONFIG/LINE")
        ]
        texto_sw1 = "\n".join(lineas_sw1)
        for vlan in (10, 20, 30, 40, 50):
            if f"vlan {vlan}" not in texto_sw1:
                errores.append(f"SW1: falta declaración de 'vlan {vlan}'")
            if f"switchport access vlan {vlan}" not in texto_sw1:
                errores.append(f"SW1: ningún puerto asignado a 'switchport access vlan {vlan}'")
        verificaciones["sw1_trunk_gi0_1"] = (
            "interface GigabitEthernet0/1" in texto_sw1
            and "switchport mode trunk" in texto_sw1
            and "switchport trunk allowed vlan 10,20,30,40,50" in texto_sw1
        )
        if not verificaciones["sw1_trunk_gi0_1"]:
            errores.append("SW1: configuración troncal 802.1Q en Gi0/1 incompleta")

    # 3. Auditar los 5 PCs (PC-D1 a PC-D5)
    for num, modo_esperado in (
        (1, "slaac"),
        (2, "stateless"),
        (3, "stateful"),
        (4, "stateless"),
        (5, "slaac"),
    ):
        nom_pc = f"PC-D{num}"
        pc = dispositivos.get(nom_pc)
        if pc is None:
            errores.append(f"No se encontró el terminal {nom_pc}")
            continue
        puerto = pc.find(".//PORT")
        if puerto is None:
            errores.append(f"{nom_pc} no tiene elemento <PORT>")
            continue
        v6_en = (puerto.findtext("IPV6_ENABLED") or "").lower() == "true"
        v6_auto = (puerto.findtext("IPV6_ADDRESS_AUTOCONFIG") or "").lower() == "true"
        v6_dhcp = (puerto.findtext("IPV6_PORT_DHCP_ENABLED") or "").lower() == "true"
        verificaciones[f"{nom_pc}_ipv6_activo"] = v6_en and v6_auto
        if not (v6_en and v6_auto):
            errores.append(f"{nom_pc}: IPV6_ENABLED o IPV6_ADDRESS_AUTOCONFIG no están en true")
        if modo_esperado == "stateful" and not v6_dhcp:
            errores.append(f"{nom_pc} (Stateful): IPV6_PORT_DHCP_ENABLED debería ser true")
        if modo_esperado in ("slaac", "stateless") and v6_dhcp:
            errores.append(f"{nom_pc} ({modo_esperado}): IPV6_PORT_DHCP_ENABLED debería ser false")

    # 4. Auditar Servidor DNS (SRV-DNS)
    srv = dispositivos.get("SRV-DNS")
    if srv is None:
        errores.append("No se encontró el servidor SRV-DNS")
    else:
        dns_en = srv.findtext(".//ENGINE/DNS_SERVER/ENABLED") == "1"
        rrs = srv.findall(".//ENGINE/DNS_SERVER/NAMESERVER-DATABASE/RESOURCE-RECORD")
        verificaciones["srv_dns_habilitado"] = dns_en
        verificaciones["srv_dns_base_datos_limpia"] = len(rrs) == 0
        if not dns_en:
            errores.append("SRV-DNS no tiene el servicio DNS habilitado (<ENABLED>1</ENABLED>)")
        if len(rrs) > 0:
            errores.append(
                f"SRV-DNS contiene {len(rrs)} registros RESOURCE-RECORD precompilados; "
                "Packet Tracer 9.0.1 requiere NAMESERVER-DATABASE vacía para evitar rechazo de archivo."
            )

    return {
        "archivo": str(ruta),
        "valido": len(errores) == 0,
        "verificaciones": verificaciones,
        "errores": errores,
    }


def auditar_red_diagnostico_hito10(ruta_pkt: str | os.PathLike) -> dict[str, Any]:
    """Verifica que `topologia_diagnostico_hito10.pkt` contenga exactamente los 3
    fallos pedagógicos diseñados para el Hito 10 (Troubleshooting).
    """
    ruta = Path(ruta_pkt)
    xml_texto = pt9.decode(str(ruta), "pkt", verify_tag=True).decode("utf-8")
    raiz = ET.fromstring(xml_texto)

    dispositivos = {
        (d.findtext("ENGINE/NAME") or ""): d
        for d in raiz.findall(".//NETWORK/DEVICES/DEVICE")
    }
    r1 = dispositivos["R1"]
    sw1 = dispositivos["SW1"]

    texto_r1 = "\n".join((l.text or "") for l in r1.findall(".//ENGINE/RUNNINGCONFIG/LINE"))
    texto_sw1 = "\n".join((l.text or "") for l in sw1.findall(".//ENGINE/RUNNINGCONFIG/LINE"))

    fallo_1_presente = "switchport trunk allowed vlan 10,20,30,50" in texto_sw1
    fallo_2_presente = texto_r1.count("ipv6 nd other-config-flag") == 1
    fallo_3_presente = "ipv6 dhcp server DEPT3_STATEFUL" not in texto_r1

    return {
        "archivo": str(ruta),
        "valido": fallo_1_presente and fallo_2_presente and fallo_3_presente,
        "fallo_1_vlan40_omitida_en_troncal": fallo_1_presente,
        "fallo_2_flag_o_omitido_en_gi0_0_20": fallo_2_presente,
        "fallo_3_dhcp_server_omitido_en_gi0_0_30": fallo_3_presente,
    }


if __name__ == "__main__":
    dir_salida = Path(__file__).resolve().parent.parent / "salida"
    rep_res = auditar_red_resuelta_ipv6(dir_salida / "topologia_resuelta.pkt")
    print(f"[IPV6 RESUELTA] valido={rep_res['valido']} | errores={len(rep_res['errores'])}")
    rep_diag = auditar_red_diagnostico_hito10(
        dir_salida / "topologia_diagnostico_hito10.pkt"
    )
    print(f"[IPV6 DIAGNOSTICO HITO 10] valido={rep_diag['valido']} | {rep_diag}")
