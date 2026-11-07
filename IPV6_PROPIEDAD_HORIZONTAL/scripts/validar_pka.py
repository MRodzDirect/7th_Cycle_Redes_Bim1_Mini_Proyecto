#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validar_pka.py -- Validador estructural, criptográfico y de contenedor para archivos
`.pkt` y `.pka` generados para Packet Tracer 9.0.1.

Verifica:
  1. Desencriptación EAX (Twofish-128) con verificación estricta de etiqueta MAC de 16 bytes.
  2. Desofuscación de capas A y B y descompresión Qt `qCompress` (cabecera big-endian + zlib).
  3. Bien-formado XML (`xml.etree.ElementTree.fromstring`).
  4. Para `.pkt`: etiqueta raíz `<PACKETTRACER5>`, 14 dispositivos, 13 enlaces, puertos válidos
     según `port_model.json`, encendido de puertos en `AccessPoint-PT` y ausencia de IPs
     residuales de plantilla (`1.1.1.1` / `192.168.10.2`).
  5. Para `.pka`: etiqueta raíz `<PACKETTRACER5_ACTIVITY>`, exactamente 3 redes `<PACKETTRACER5>`
     embebidas (`[0]` actual, `[1]` inicial, `[2]` respuesta), árboles `<INITIALSETUP>` y
     `<COMPARISONS>` válidos, 10 páginas HTML `<PAGE>` en `<INSTRUCTIONS>` y contraseña de
     Activity Wizard (`ACTIVITY/@PASS`).
"""

from __future__ import annotations

import json
import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import compat_windows
import pt9

RE_REDES_PKT = re.compile(r"<PACKETTRACER5>.*?</PACKETTRACER5>", re.S)
RUTA_PORT_MODEL = (
    compat_windows.RUTA_REPO / "generators" / "jasdf_aewc" / "build" / "port_model.json"
)


def validar_archivo_pkt(ruta_pkt: str | os.PathLike) -> dict[str, Any]:
    """Decodifica y audita estructuralmente un archivo `.pkt`."""
    ruta = Path(ruta_pkt)
    errores: list[str] = []
    advertencias: list[str] = []

    if not ruta.exists():
        return {"archivo": str(ruta), "valido": False, "errores": ["El archivo no existe"]}

    tamano_bytes = ruta.stat().st_size
    try:
        xml_bytes = pt9.decode(str(ruta), "pkt", verify_tag=True)
        xml_texto = xml_bytes.decode("utf-8")
    except Exception as exc:
        return {
            "archivo": str(ruta),
            "valido": False,
            "errores": [f"Fallo de desencriptación/contenedor PT9: {exc}"],
        }

    try:
        raiz = ET.fromstring(xml_texto)
    except Exception as exc:
        return {
            "archivo": str(ruta),
            "valido": False,
            "errores": [f"XML mal formado: {exc}"],
        }

    if raiz.tag != "PACKETTRACER5":
        errores.append(f"Etiqueta raíz inesperada: {raiz.tag} (se esperaba PACKETTRACER5)")

    dispositivos = raiz.findall(".//NETWORK/DEVICES/DEVICE")
    enlaces = raiz.findall(".//NETWORK/LINKS/LINK")

    if len(dispositivos) != 14:
        errores.append(f"Cantidad de dispositivos incorrecta: {len(dispositivos)} (esperados: 14)")
    if len(enlaces) != 13:
        errores.append(f"Cantidad de enlaces incorrecta: {len(enlaces)} (esperados: 13)")

    # Mapa de SAVE_REF_ID -> (nombre, modelo)
    mapa_ref: dict[str, tuple[str, str]] = {}
    mapa_dev_addr: dict[str, str] = {}
    lista_dev_addrs: list[tuple[str, str]] = []
    lista_mem_addrs: list[tuple[str, str]] = []

    for disp in dispositivos:
        motor = disp.find("ENGINE")
        if motor is None:
            errores.append("Dispositivo sin nodo <ENGINE>")
            continue
        nombre = motor.findtext("NAME") or ""
        tipo_el = motor.find("TYPE")
        modelo = tipo_el.get("model", "") if tipo_el is not None else ""
        ref_id = motor.findtext("SAVE_REF_ID") or ""
        mapa_ref[ref_id] = (nombre, modelo)

        # Auditoría de DEV_ADDR y MEM_ADDR en WORKSPACE/LOGICAL
        dev_addr = disp.findtext("WORKSPACE/LOGICAL/DEV_ADDR") or ""
        mem_addr = disp.findtext("WORKSPACE/LOGICAL/MEM_ADDR") or ""
        if not dev_addr:
            errores.append(f"El dispositivo {nombre} no tiene <WORKSPACE><LOGICAL><DEV_ADDR>")
        else:
            mapa_dev_addr[ref_id] = dev_addr
            mapa_dev_addr[nombre] = dev_addr
            lista_dev_addrs.append((nombre, dev_addr))

        if not mem_addr:
            errores.append(f"El dispositivo {nombre} no tiene <WORKSPACE><LOGICAL><MEM_ADDR>")
        else:
            lista_mem_addrs.append((nombre, mem_addr))

        if (motor.findtext("POWER") or "").lower() != "true":
            errores.append(f"El dispositivo {nombre} ({modelo}) tiene <ENGINE><POWER> apagado")

        # Verificar que AccessPoint-PT tenga todos los puertos encendidos
        if modelo == "AccessPoint-PT":
            for p in disp.iter("PORT"):
                if (p.findtext("POWER") or "").lower() != "true":
                    errores.append(
                        f"El Access Point {nombre} tiene un puerto con <POWER>false</POWER>"
                    )

        # Verificar ausencia de IPs IPv4 residuales de plantilla (1.1.1.1 / 192.168.10.2)
        if modelo in ("PC-PT", "Server-PT"):
            for p in disp.iter("PORT"):
                ip_v4 = (p.findtext("IP") or "").strip()
                if ip_v4 in ("1.1.1.1", "192.168.10.2"):
                    errores.append(
                        f"Residuo IPv4 de plantilla detectado en {nombre}: <IP>{ip_v4}</IP>"
                    )

    # Validar unicidad de DEV_ADDR
    vistos_dev: dict[str, list[str]] = {}
    for nom, da in lista_dev_addrs:
        vistos_dev.setdefault(da, []).append(nom)
    for da, noms in vistos_dev.items():
        if len(noms) > 1:
            errores.append(f"DEV_ADDR duplicado '{da}' compartido por dispositivos {noms}")

    # Validar unicidad de MEM_ADDR
    vistos_mem: dict[str, list[str]] = {}
    for nom, ma in lista_mem_addrs:
        vistos_mem.setdefault(ma, []).append(nom)
    for ma, noms in vistos_mem.items():
        if len(noms) > 1:
            errores.append(f"MEM_ADDR duplicado '{ma}' compartido por dispositivos {noms}")

    # Validar puertos de enlaces contra port_model.json y consistencia de punteros de memoria
    port_model = {}
    if RUTA_PORT_MODEL.exists():
        port_model = json.loads(RUTA_PORT_MODEL.read_text(encoding="utf-8"))

    for idx, enl in enumerate(enlaces):
        cable = enl.find("CABLE")
        if cable is None:
            errores.append(f"Enlace #{idx} sin elemento <CABLE>")
            continue
        from_id = cable.findtext("FROM") or ""
        to_id = cable.findtext("TO") or ""
        puertos = [p.text or "" for p in cable.findall("PORT")]
        if from_id not in mapa_ref:
            errores.append(f"Enlace #{idx}: FROM '{from_id}' no corresponde a ningún dispositivo")
        if to_id not in mapa_ref:
            errores.append(f"Enlace #{idx}: TO '{to_id}' no corresponde a ningún dispositivo")
        if len(puertos) != 2:
            errores.append(f"Enlace #{idx}: cantidad de etiquetas <PORT> distinta de 2")
        elif port_model and from_id in mapa_ref and to_id in mapa_ref:
            nom_a, mod_a = mapa_ref[from_id]
            nom_b, mod_b = mapa_ref[to_id]
            # Cloud-PT admite Ethernet6 (slot 6 PT-CLOUD-NM-1CE) además de Port 0/Ethernet1
            puertos_validos_a = set(port_model.get(mod_a, {}).keys()) | {"Ethernet6"}
            puertos_validos_b = set(port_model.get(mod_b, {}).keys()) | {"Ethernet6"}
            if puertos[0] not in puertos_validos_a:
                errores.append(f"Puerto inválido en {nom_a} ({mod_a}): {puertos[0]}")
            if puertos[1] not in puertos_validos_b:
                errores.append(f"Puerto inválido en {nom_b} ({mod_b}): {puertos[1]}")

        # Validar alineación de FROM_DEVICE_MEM_ADDR y TO_DEVICE_MEM_ADDR con el DEV_ADDR correspondiente
        f_d_mem = cable.findtext("FROM_DEVICE_MEM_ADDR") or ""
        t_d_mem = cable.findtext("TO_DEVICE_MEM_ADDR") or ""
        esperado_from = mapa_dev_addr.get(from_id)
        esperado_to = mapa_dev_addr.get(to_id)
        if esperado_from and f_d_mem != esperado_from:
            errores.append(
                f"Enlace #{idx} ({from_id} -> {to_id}): FROM_DEVICE_MEM_ADDR '{f_d_mem}' "
                f"no coincide con DEV_ADDR '{esperado_from}' del dispositivo de origen"
            )
        if esperado_to and t_d_mem != esperado_to:
            errores.append(
                f"Enlace #{idx} ({from_id} -> {to_id}): TO_DEVICE_MEM_ADDR '{t_d_mem}' "
                f"no coincide con DEV_ADDR '{esperado_to}' del dispositivo de destino"
            )

    return {
        "archivo": str(ruta),
        "formato": "pkt",
        "tamano_bytes": tamano_bytes,
        "xml_bytes": len(xml_bytes),
        "dispositivos": len(dispositivos),
        "enlaces": len(enlaces),
        "valido": len(errores) == 0,
        "errores": errores,
        "advertencias": advertencias,
    }


def validar_archivo_pka(ruta_pka: str | os.PathLike) -> dict[str, Any]:
    """Decodifica y audita estructuralmente un archivo de actividad `.pka`."""
    ruta = Path(ruta_pka)
    errores: list[str] = []
    advertencias: list[str] = []

    if not ruta.exists():
        return {"archivo": str(ruta), "valido": False, "errores": ["El archivo no existe"]}

    tamano_bytes = ruta.stat().st_size
    try:
        xml_bytes = pt9.decode(str(ruta), "pkt", verify_tag=True)
        xml_texto = xml_bytes.decode("utf-8")
    except Exception as exc:
        return {
            "archivo": str(ruta),
            "valido": False,
            "errores": [f"Fallo de desencriptación/contenedor PT9: {exc}"],
        }

    try:
        raiz = ET.fromstring(xml_texto)
    except Exception as exc:
        return {
            "archivo": str(ruta),
            "valido": False,
            "errores": [f"XML de actividad mal formado: {exc}"],
        }

    if raiz.tag != "PACKETTRACER5_ACTIVITY":
        errores.append(
            f"Etiqueta raíz inesperada: {raiz.tag} (se esperaba PACKETTRACER5_ACTIVITY)"
        )

    bloques_pkt = RE_REDES_PKT.findall(xml_texto)
    if len(bloques_pkt) != 3:
        errores.append(
            f"El archivo .pka debe embeber exactamente 3 redes <PACKETTRACER5>, tiene {len(bloques_pkt)}"
        )

    # Verificar que los bloques [0] (working) y [1] (initial) coincidan
    if len(bloques_pkt) == 3 and bloques_pkt[0] != bloques_pkt[1]:
        advertencias.append("Los bloques de red [0] (actual) y [1] (inicial) no son idénticos")

    # Verificar INITIALSETUP y COMPARISONS
    nodo_init = raiz.find("INITIALSETUP")
    nodo_comp = raiz.find("COMPARISONS")
    nodos_init_count = 0
    nodos_comp_count = 0
    puntos_init = 0

    if nodo_init is None:
        errores.append("Falta la sección <INITIALSETUP>")
    else:
        nodos_init_count = len(list(nodo_init.iter("NODE")))
        if nodo_init.findtext("LOAD_INIT_TREE") != "true":
            errores.append("<INITIALSETUP> debe contener <LOAD_INIT_TREE>true</LOAD_INIT_TREE>")
        for node in nodo_init.iter("NODE"):
            name_el = node.find("NAME")
            ct = name_el.get("checkType", "0") if name_el is not None else "0"
            pt = node.find("POINTS")
            if ct != "0" and pt is not None and (pt.text or "").strip().isdigit():
                puntos_init += int((pt.text or "0").strip())
        if puntos_init <= 0:
            errores.append("El árbol <INITIALSETUP> no tiene puntos de evaluación activos")

    if nodo_comp is None:
        errores.append("Falta la sección <COMPARISONS>")
    else:
        nodos_comp_count = len(list(nodo_comp.iter("NODE")))
        if nodos_comp_count < nodos_init_count:
            errores.append(
                f"<COMPARISONS> ({nodos_comp_count}) tiene menos nodos que <INITIALSETUP> ({nodos_init_count})"
            )

    # Verificar instrucciones (10 páginas HTML)
    paginas = raiz.findall(".//ACTIVITY/INSTRUCTIONS/PAGE")
    if len(paginas) != 10:
        errores.append(
            f"Se esperaban 10 páginas <PAGE> en <INSTRUCTIONS>, se encontraron {len(paginas)}"
        )

    nodo_act = raiz.find("ACTIVITY")
    password_act = nodo_act.get("PASS", "") if nodo_act is not None else ""
    if not password_act:
        advertencias.append("El atributo ACTIVITY/@PASS está vacío")

    # Validar atributos de temporizador en <ACTIVITY>
    if nodo_act is not None:
        cd_left = nodo_act.get("COUNTDOWNLEFT", "0")
        try:
            if int(cd_left) < 0:
                errores.append(
                    f"Atributo de temporizador inválido en <ACTIVITY>: COUNTDOWNLEFT='{cd_left}' (no debe ser negativo)"
                )
        except ValueError:
            errores.append(f"Atributo COUNTDOWNLEFT no numérico: '{cd_left}'")

        cd_ms = nodo_act.get("COUNTDOWNMS", "0")
        try:
            if int(cd_ms) < 0:
                errores.append(f"Atributo COUNTDOWNMS no debe ser negativo: '{cd_ms}'")
        except ValueError:
            errores.append(f"Atributo COUNTDOWNMS no numérico: '{cd_ms}'")

        elapsed = nodo_act.get("ELAPSED", "0")
        try:
            if int(elapsed) < 0:
                errores.append(f"Atributo ELAPSED no debe ser negativo: '{elapsed}'")
        except ValueError:
            errores.append(f"Atributo ELAPSED no numérico: '{elapsed}'")

    # Validar que cada una de las 3 redes embebidas tenga DEV_ADDR únicos y punteros alineados
    for idx_red, b_xml in enumerate(bloques_pkt):
        try:
            net_root = ET.fromstring(b_xml)
        except Exception as exc_b:
            errores.append(f"Red embebida #{idx_red} XML corrupto: {exc_b}")
            continue

        devs_net = net_root.findall(".//NETWORK/DEVICES/DEVICE")
        mapa_dev_net: dict[str, str] = {}
        vistos_dev_net: dict[str, list[str]] = {}

        for d in devs_net:
            ref = d.findtext("SAVE_REF_ID") or d.findtext("ENGINE/SAVE_REF_ID") or ""
            nom = d.findtext("NAME") or d.findtext("ENGINE/NAME") or ""
            da = d.findtext("WORKSPACE/LOGICAL/DEV_ADDR") or ""
            if not da:
                errores.append(f"Red embebida #{idx_red}: Dispositivo {nom} sin DEV_ADDR")
            else:
                mapa_dev_net[ref] = da
                mapa_dev_net[nom] = da
                vistos_dev_net.setdefault(da, []).append(nom)

        for da, noms in vistos_dev_net.items():
            if len(noms) > 1:
                errores.append(
                    f"Red embebida #{idx_red}: DEV_ADDR duplicado '{da}' en dispositivos {noms}"
                )

        for j_enl, enl in enumerate(net_root.findall(".//NETWORK/LINKS/LINK")):
            cab = enl.find("CABLE")
            if cab is None:
                continue
            frm = cab.findtext("FROM") or ""
            to = cab.findtext("TO") or ""
            f_mem = cab.findtext("FROM_DEVICE_MEM_ADDR") or ""
            t_mem = cab.findtext("TO_DEVICE_MEM_ADDR") or ""
            esp_f = mapa_dev_net.get(frm)
            esp_t = mapa_dev_net.get(to)
            if esp_f and f_mem != esp_f:
                errores.append(
                    f"Red embebida #{idx_red}, Enlace #{j_enl} ({frm} -> {to}): "
                    f"FROM_DEVICE_MEM_ADDR '{f_mem}' != DEV_ADDR '{esp_f}'"
                )
            if esp_t and t_mem != esp_t:
                errores.append(
                    f"Red embebida #{idx_red}, Enlace #{j_enl} ({frm} -> {to}): "
                    f"TO_DEVICE_MEM_ADDR '{t_mem}' != DEV_ADDR '{esp_t}'"
                )

    comp_list = raiz.findtext("COMPONENT_LIST") or ""
    for cat_req in ("Ip", "Switching", "Routing", "Physical", "Other"):
        if cat_req not in comp_list:
            errores.append(f"Categoría '{cat_req}' ausente en <COMPONENT_LIST> ({comp_list})")

    return {
        "archivo": str(ruta),
        "formato": "pka",
        "tamano_bytes": tamano_bytes,
        "xml_bytes": len(xml_bytes),
        "redes_embebidas": len(bloques_pkt),
        "paginas_instrucciones": len(paginas),
        "nodos_initialsetup": nodos_init_count,
        "nodos_comparisons": nodos_comp_count,
        "puntos_evaluacion": puntos_init,
        "password_configurada": bool(password_act),
        "component_list": comp_list,
        "valido": len(errores) == 0,
        "errores": errores,
        "advertencias": advertencias,
    }


if __name__ == "__main__":
    dir_salida = Path(__file__).resolve().parent.parent / "salida"
    for nombre_pkt in (
        "topologia_inicial.pkt",
        "topologia_resuelta.pkt",
        "topologia_diagnostico_hito10.pkt",
    ):
        ruta_f = dir_salida / nombre_pkt
        if ruta_f.exists():
            res = validar_archivo_pkt(ruta_f)
            print(f"[PKT] {nombre_pkt}: valido={res['valido']} ({res.get('tamano_bytes')} bytes)")
    for nombre_pka in (
        "Grupo_IPV6_Estudiante.pka",
        "Grupo_IPV6_Maestro.pka",
        "Grupo_IPV6_Diagnostico_Hito10.pka",
    ):
        ruta_f = dir_salida / nombre_pka
        if ruta_f.exists():
            res = validar_archivo_pka(ruta_f)
            print(
                f"[PKA] {nombre_pka}: valido={res['valido']} "
                f"({res.get('puntos_evaluacion')} pts, {res.get('paginas_instrucciones')} páginas)"
            )
