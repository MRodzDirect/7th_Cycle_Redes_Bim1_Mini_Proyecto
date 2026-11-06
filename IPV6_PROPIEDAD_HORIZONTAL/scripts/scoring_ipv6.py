#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scoring_ipv6.py -- Generador riguroso del árbol de calificación automática
(`<INITIALSETUP>` y `<COMPARISONS>`) para el laboratorio de Direccionamiento Dinámico
IPv6 en Propiedad Horizontal.

Cumple estrictamente la regla de arquitectura de Packet Tracer 9.0.1:
  "Packet Tracer validates the scoring tree against the network's item model.
   A hand-made minimal node is rejected, while a complete device node cloned
   from a real activity loads fine."

Conserva intactos los árboles `sh["init"]` y `sh["comp"]` de `device_shapes.json`,
renombrando la raíz y los identificadores de dispositivo, y aplicando modificaciones
in-situ (in-place) exclusivamente sobre los nodos existentes para evaluar:
  - Hostname en R1 y SW1
  - Enrutamiento IPv6 unicast en R1
  - Dominio de red en R1
  - Estado de puertos de red
  - VLAN de acceso y modo troncal en puertos del Switch SW1
  - Autoconfiguración y habilitación de IPv6 en PCs (SLAAC / DHCPv6)
  - Habilitación del servicio DNS en SRV-DNS
"""

from __future__ import annotations

import copy
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import compat_windows
import scoring

RUTA_SHAPES = compat_windows.RUTA_REPO_TOOLS / "device_shapes.json"


def _renombrar_arbol_dispositivo(el: ET.Element, nuevo_nombre: str) -> None:
    """Reemplaza el nombre de dispositivo donante en la raíz del nodo."""
    nombre_anterior = el.findtext("NAME") or ""
    for e in el.iter("NAME"):
        if e.text == nombre_anterior:
            e.text = nuevo_nombre
    for e in el.iter("ID"):
        if e.text == nombre_anterior:
            e.text = nuevo_nombre


def _buscar_nodo_por_camino(raiz: ET.Element, camino_ids_o_nombres: list[str]) -> ET.Element | None:
    """Navega una ruta jerárquica buscando por ID o NAME en cada nivel."""
    actual: ET.Element | None = raiz
    for paso in camino_ids_o_nombres:
        if actual is None:
            return None
        encontrado = None
        for hijo in actual.findall("NODE"):
            id_txt = (hijo.findtext("ID") or "").strip()
            nm_txt = (hijo.findtext("NAME") or "").strip()
            if id_txt == paso or nm_txt == paso:
                encontrado = hijo
                break
        actual = encontrado
    return actual


def _configurar_nodo_in_place(
    nodo: ET.Element,
    *,
    valor: str | None = None,
    check_type: str = "1",
    puntos: str = "1",
    componente: str | None = None,
) -> bool:
    """Actualiza atributos in-situ en un elemento `<NODE>` existente."""
    el_name = nodo.find("NAME")
    if el_name is None:
        return False

    if valor is not None:
        el_name.set("nodeValue", str(valor))
    el_name.set("checkType", str(check_type))

    el_pts = nodo.find("POINTS")
    if el_pts is None:
        el_pts = ET.SubElement(nodo, "POINTS")
    el_pts.text = str(puntos)

    if componente:
        el_comp = nodo.find("COMPONENTS")
        if el_comp is None:
            el_comp = ET.SubElement(nodo, "COMPONENTS")
        el_comp.text = componente

    return True


def generar_scoring_ipv6(
    spec: dict[str, Any], shapes: dict[str, Any] | None = None
) -> tuple[str, str, dict[str, Any]]:
    """Construye `(initialsetup_xml, comparisons_xml, resumen_scoring)` asegurando que
    cada nodo de dispositivo en `<INITIALSETUP>` y `<COMPARISONS>` sea un clon 100% completo
    e intacto del modelo original en `device_shapes.json`.
    """
    if shapes is None:
        shapes = scoring.load_shapes(str(RUTA_SHAPES))

    departamentos = spec["departamentos"]
    init_nodes: list[str] = []
    comp_nodes: list[str] = []
    resumen_por_dispositivo: dict[str, dict[str, Any]] = {}
    modelos_omitidos: list[str] = []

    for disp in spec["devices"]:
        nombre = disp["name"]
        modelo = disp["model"]
        if modelo not in shapes["models"]:
            modelos_omitidos.append(modelo)
            continue

        sh_model = shapes["models"][modelo]
        comp_el = ET.fromstring(sh_model["comp"])
        init_el = ET.fromstring(sh_model["init"]) if sh_model.get("init") else None

        _renombrar_arbol_dispositivo(comp_el, nombre)
        if init_el is not None:
            _renombrar_arbol_dispositivo(init_el, nombre)

        items_evaluados = 0
        total_puntos_disp = 0

        def calificar_en_ambos(camino: list[str], val: str, pts: str = "1", comp: str = "Other"):
            nonlocal items_evaluados, total_puntos_disp
            n_comp = _buscar_nodo_por_camino(comp_el, camino)
            if n_comp is not None:
                _configurar_nodo_in_place(n_comp, valor=val, check_type="1", puntos=pts, componente=comp)
                items_evaluados += 1
                total_puntos_disp += int(pts)
            if init_el is not None:
                n_init = _buscar_nodo_por_camino(init_el, camino)
                if n_init is not None:
                    _configurar_nodo_in_place(n_init, valor=val, check_type="1", puntos=pts, componente=comp)

        if modelo == "2911":
            # 1. Host Name de R1
            calificar_en_ambos(["Host Name"], nombre, pts="2", comp="Other")

            # 2. IPv6 Unicast Routing en COMP
            n_unicast = _buscar_nodo_por_camino(comp_el, ["Routesv6", "Ipv6 Unicast Routing"])
            if n_unicast is not None:
                _configurar_nodo_in_place(n_unicast, valor="1", check_type="1", puntos="4", componente="Routing")
                items_evaluados += 1
                total_puntos_disp += 4

            # 3. Dominio en DNS
            calificar_en_ambos(["DNS", "IP Domain Name"], spec["metadata"]["dominio"], pts="2", comp="Other")

            # 4. Puertos físicos arriba y con IPv6 Enable
            for puerto in ("GigabitEthernet0/0", "GigabitEthernet0/1", "GigabitEthernet0/2"):
                calificar_en_ambos(["Ports", puerto, "Power"], "1", pts="1", comp="Physical")
                calificar_en_ambos(["Ports", puerto, "Port Up"], "1", pts="1", comp="Physical")
                calificar_en_ambos(["Ports", puerto, "IPv6 Enable"], "1", pts="2", comp="Ip")

        elif modelo == "2960-24TT":
            # 1. Host Name de SW1
            calificar_en_ambos(["Host Name"], nombre, pts="2", comp="Other")

            # 2. Enlace troncal hacia R1 (Gi0/1)
            calificar_en_ambos(["Ports", "GigabitEthernet0/1", "Power"], "1", pts="1", comp="Physical")
            calificar_en_ambos(["Ports", "GigabitEthernet0/1", "Port Up"], "1", pts="1", comp="Physical")
            calificar_en_ambos(["Ports", "GigabitEthernet0/1", "Dynamic Mode"], "1", pts="3", comp="Switching")

            # 3. Puertos de acceso de los 5 departamentos (Fa0/1..Fa0/5)
            for depto in departamentos:
                vlan_id = str(depto["vlan_id"])
                p_sw = depto.get("sw_port_pc") or depto.get("switch_port", "FastEthernet0/1")
                calificar_en_ambos(["Ports", p_sw, "Power"], "1", pts="1", comp="Physical")
                calificar_en_ambos(["Ports", p_sw, "Port Up"], "1", pts="1", comp="Physical")
                calificar_en_ambos(["Ports", p_sw, "Access VLAN"], vlan_id, pts="3", comp="Switching")

        elif modelo == "PC-PT":
            # Puertos físicos e IPv6 Enable / Auto Config
            calificar_en_ambos(["Ports", "FastEthernet0", "Power"], "1", pts="1", comp="Physical")
            calificar_en_ambos(["Ports", "FastEthernet0", "Port Up"], "1", pts="1", comp="Physical")
            calificar_en_ambos(["Ports", "FastEthernet0", "IPv6 Enable"], "1", pts="2", comp="Ip")
            calificar_en_ambos(["Ports", "FastEthernet0", "Auto Config"], "1", pts="3", comp="Ip")

        elif modelo == "Server-PT":
            # Servidor DNS
            calificar_en_ambos(["Ports", "FastEthernet0", "Power"], "1", pts="1", comp="Physical")
            calificar_en_ambos(["Ports", "FastEthernet0", "Port Up"], "1", pts="1", comp="Physical")
            calificar_en_ambos(["Ports", "FastEthernet0", "IPv6 Enable"], "1", pts="2", comp="Ip")
            calificar_en_ambos(["DNS", "DNS Enable"], "1", pts="4", comp="Ip")

        resumen_por_dispositivo[nombre] = {
            "modelo": modelo,
            "items_evaluados": items_evaluados,
            "total_puntos": total_puntos_disp,
        }

        if init_el is not None:
            init_nodes.append(ET.tostring(init_el, encoding="unicode"))
        comp_nodes.append(ET.tostring(comp_el, encoding="unicode"))

    apertura_red = (
        '<NODE><NAME checkType="0" eclass="8" headNode="true" '
        'incorrectFeedback="" nodeValue="" obfuscateName="false" overrideDBGrading="false" '
        'variableEnabled="false" variableName="">Network</NAME><ID>Network</ID>'
        "<COMPONENTS></COMPONENTS><POINTS></POINTS>"
    )
    cierre_red = "</NODE>"

    initialsetup_xml = (
        f"<INITIALSETUP>{apertura_red}{''.join(init_nodes)}{cierre_red}"
        "<LOAD_INIT_TREE>true</LOAD_INIT_TREE></INITIALSETUP>"
    )
    comparisons_xml = (
        f"<COMPARISONS>{apertura_red}{''.join(shapes.get('scaffold', []))}"
        f"{''.join(comp_nodes)}{cierre_red}</COMPARISONS>"
    )

    total_puntos_global = sum(d["total_puntos"] for d in resumen_por_dispositivo.values())
    resumen_global = {
        "dispositivos_evaluados": len(resumen_por_dispositivo),
        "modelos_sin_shape_solo_topologia": sorted(set(modelos_omitidos)),
        "total_puntos_evaluacion": total_puntos_global,
        "componentes_activos": "Ip, Switching, Routing, Physical, Other",
        "detalle_dispositivos": resumen_por_dispositivo,
    }

    return initialsetup_xml, comparisons_xml, resumen_global


if __name__ == "__main__":
    from preparar_spec import RUTA_ESCENARIO_DEFAULT, preparar_especificacion

    spec_data = preparar_especificacion(RUTA_ESCENARIO_DEFAULT)
    init_str, comp_str, resumen = generar_scoring_ipv6(spec_data)
    print(
        f"[OK] Scoring IPv6 generado: {resumen['dispositivos_evaluados']} dispositivos evaluados, "
        f"{resumen['total_puntos_evaluacion']} puntos totales."
    )
    for k, v in resumen["detalle_dispositivos"].items():
        print(f"  - {k} ({v['modelo']}): {v['total_puntos']} pts ({v['items_evaluados']} items)")
