#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
preparar_spec.py -- Carga, valida y compila la especificación completa del escenario
IPv6 en Propiedad Horizontal (`escenario.json`), integrando archivos de configuración
CLI (`configuraciones/*.txt`) y las 10 páginas HTML de hitos (`instrucciones/*.html`).
"""

from __future__ import annotations

import ipaddress
import json
from pathlib import Path
from typing import Any

import compat_windows  # noqa: F401


RUTA_BASE = Path(__file__).resolve().parent.parent
RUTA_ESCENARIO_DEFAULT = RUTA_BASE / "escenario.json"
RUTA_PORT_MODEL = (
    compat_windows.RUTA_REPO / "generators" / "jasdf_aewc" / "build" / "port_model.json"
)


def cargar_lineas_ios(ruta_archivo: Path) -> list[str]:
    """Lee un archivo de configuración IOS y devuelve sus líneas limpias."""
    if not ruta_archivo.exists():
        raise FileNotFoundError(f"No existe el archivo de configuración: {ruta_archivo}")
    texto = ruta_archivo.read_text(encoding="utf-8")
    lineas: list[str] = []
    for linea in texto.splitlines():
        if linea.strip().startswith("! ===") or linea.strip().startswith("! ---"):
            continue
        lineas.append(linea.rstrip("\r\n"))
    return lineas


def construir_config_con_fallos_hito10(
    lineas_r1: list[str], lineas_sw1: list[str]
) -> tuple[list[str], list[str]]:
    """Genera las configuraciones de R1 y SW1 con los 3 fallos inyectados para el Hito 10:
    1. En SW1 Gi0/1: omitir la VLAN 40 de `switchport trunk allowed vlan` (10,20,30,50).
    2. En R1 Gi0/0.20: omitir `ipv6 nd other-config-flag`.
    3. En R1 Gi0/0.30: omitir `ipv6 dhcp server DEPT3_STATEFUL`.
    """
    r1_fallo: list[str] = []
    contexto_actual = ""
    for linea in lineas_r1:
        limpia = linea.strip()
        if limpia.startswith("interface "):
            contexto_actual = limpia
        elif limpia == "!":
            contexto_actual = ""

        if (
            contexto_actual == "interface GigabitEthernet0/0.20"
            and limpia == "ipv6 nd other-config-flag"
        ):
            continue
        if (
            contexto_actual == "interface GigabitEthernet0/0.30"
            and limpia == "ipv6 dhcp server DEPT3_STATEFUL"
        ):
            continue
        r1_fallo.append(linea)

    sw1_fallo: list[str] = []
    for linea in lineas_sw1:
        if "switchport trunk allowed vlan 10,20,30,40,50" in linea:
            sw1_fallo.append(" switchport trunk allowed vlan 10,20,30,50")
        else:
            sw1_fallo.append(linea)

    return r1_fallo, sw1_fallo


def validar_escenario(spec: dict[str, Any], ruta_base: Path = RUTA_BASE) -> list[str]:
    """Valida la integridad técnica del diccionario `escenario.json`.
    Devuelve una lista de errores (vacía si todo es válido).
    """
    errores: list[str] = []

    for seccion in ("metadata", "departamentos", "servicios", "devices", "links", "instrucciones_archivos"):
        if seccion not in spec:
            errores.append(f"Falta la sección obligatoria '{seccion}' en escenario.json")

    if errores:
        return errores

    # 1. Validar los 5 departamentos
    departamentos = spec["departamentos"]
    if len(departamentos) != 5:
        errores.append(f"Se esperaban exactamente 5 departamentos, se encontraron {len(departamentos)}")

    vlans_vistas: set[int] = set()
    prefijos_vistos: set[str] = set()
    metodos_esperados = {
        1: ("SLAAC", False, False, 10),
        2: ("DHCPv6 Stateless", False, True, 20),
        3: ("DHCPv6 Stateful", True, False, 30),
        4: ("DHCPv6 Stateless", False, True, 40),
        5: ("SLAAC", False, False, 50),
    }

    for depto in departamentos:
        num = depto.get("numero")
        vlan = depto.get("vlan_id")
        prefijo = depto.get("prefijo")
        gw_cidr = depto.get("gateway_cidr")
        metodo = depto.get("metodo")
        flag_m = depto.get("ra_managed_flag")
        flag_o = depto.get("ra_other_flag")

        if vlan in vlans_vistas:
            errores.append(f"VLAN duplicada: {vlan}")
        vlans_vistas.add(vlan)

        if prefijo in prefijos_vistos:
            errores.append(f"Prefijo IPv6 duplicado: {prefijo}")
        prefijos_vistos.add(prefijo)

        try:
            red = ipaddress.IPv6Network(prefijo, strict=True)
            if red.prefixlen != 64:
                errores.append(f"El prefijo {prefijo} del Depto {num} no es /64")
            interfaz_gw = ipaddress.IPv6Interface(gw_cidr)
            if interfaz_gw.ip not in red:
                errores.append(f"El gateway {gw_cidr} no pertenece a la subred {prefijo}")
        except Exception as exc:
            errores.append(f"Error de formato IPv6 en Depto {num}: {exc}")

        if num in metodos_esperados:
            exp_metodo, exp_m, exp_o, exp_vlan = metodos_esperados[num]
            if metodo != exp_metodo:
                errores.append(f"Depto {num}: método esperado '{exp_metodo}', actual '{metodo}'")
            if flag_m != exp_m or flag_o != exp_o:
                errores.append(f"Depto {num}: flags RA M/O incorrectos ({flag_m}, {flag_o})")
            if vlan != exp_vlan:
                errores.append(f"Depto {num}: VLAN esperada {exp_vlan}, actual {vlan}")

    # 2. Validar dispositivos (14 dispositivos)
    dispositivos = spec["devices"]
    nombres_disp: dict[str, dict[str, Any]] = {}
    modelos_permitidos = {"2911", "2960-24TT", "AccessPoint-PT", "PC-PT", "Server-PT", "Cloud-PT"}
    for disp in dispositivos:
        nombre = disp.get("name")
        modelo = disp.get("model")
        if not nombre or not modelo:
            errores.append(f"Dispositivo sin nombre o modelo: {disp}")
            continue
        if nombre in nombres_disp:
            errores.append(f"Nombre de dispositivo duplicado: {nombre}")
        if modelo not in modelos_permitidos:
            errores.append(f"Modelo no permitido o desconocido en {nombre}: {modelo}")
        nombres_disp[nombre] = disp

        if "config_file" in disp:
            ruta_cfg = ruta_base / disp["config_file"]
            if not ruta_cfg.exists():
                errores.append(f"Archivo de configuración no encontrado para {nombre}: {ruta_cfg}")

    for requerido in (
        "R1", "SW1", "SRV-DNS", "Cloud-PT",
        "AP-D1", "AP-D2", "AP-D3", "AP-D4", "AP-D5",
        "PC-D1", "PC-D2", "PC-D3", "PC-D4", "PC-D5",
    ):
        if requerido not in nombres_disp:
            errores.append(f"Falta el dispositivo obligatorio '{requerido}'")

    # 3. Validar enlaces (13 enlaces)
    enlaces = spec["links"]
    puertos_usados: set[tuple[str, str]] = set()
    for idx, enlace in enumerate(enlaces):
        origen = enlace.get("a")
        puerto_a = enlace.get("aport")
        destino = enlace.get("b")
        puerto_b = enlace.get("bport")
        if origen not in nombres_disp:
            errores.append(f"Enlace #{idx}: dispositivo origen '{origen}' inexistente")
        if destino not in nombres_disp:
            errores.append(f"Enlace #{idx}: dispositivo destino '{destino}' inexistente")
        if (origen, puerto_a) in puertos_usados:
            errores.append(f"Puerto duplicado en enlaces: {origen} {puerto_a}")
        if (destino, puerto_b) in puertos_usados:
            errores.append(f"Puerto duplicado en enlaces: {destino} {puerto_b}")
        puertos_usados.add((origen, puerto_a))
        puertos_usados.add((destino, puerto_b))

    # 4. Validar existencia de los 10 archivos HTML de instrucciones
    instrucciones = spec["instrucciones_archivos"]
    if len(instrucciones) != 10:
        errores.append(f"Se esperaban 10 archivos de hitos HTML, hay {len(instrucciones)}")
    for rel_html in instrucciones:
        ruta_html = ruta_base / rel_html
        if not ruta_html.exists():
            errores.append(f"No existe el archivo de instrucción HTML: {ruta_html}")

    return errores


def preparar_especificacion(ruta_escenario: Path = RUTA_ESCENARIO_DEFAULT) -> dict[str, Any]:
    """Carga `escenario.json`, valida todas sus reglas y adjunta en memoria:
    - `config_lines` en R1 y SW1
    - `config_lines_diagnostico` en R1 y SW1 (para el Hito 10)
    - `instructions_html` con el listado de las 10 páginas HTML de hitos.
    """
    ruta_base = ruta_escenario.resolve().parent
    spec = json.loads(ruta_escenario.read_text(encoding="utf-8"))
    errores = validar_escenario(spec, ruta_base)
    if errores:
        detalle = "\n  - ".join(errores)
        raise ValueError(f"Errores de validación en {ruta_escenario}:\n  - {detalle}")

    lineas_r1 = cargar_lineas_ios(ruta_base / "configuraciones" / "router_ipv6.txt")
    lineas_sw1 = cargar_lineas_ios(ruta_base / "configuraciones" / "switch_vlan.txt")
    r1_diag, sw1_diag = construir_config_con_fallos_hito10(lineas_r1, lineas_sw1)

    for disp in spec["devices"]:
        if disp["name"] == "R1":
            disp["config"] = lineas_r1
            disp["config_diagnostico"] = r1_diag
        elif disp["name"] == "SW1":
            disp["config"] = lineas_sw1
            disp["config_diagnostico"] = sw1_diag

    paginas_html: list[str] = []
    for rel_html in spec["instrucciones_archivos"]:
        ruta_html = ruta_base / rel_html
        paginas_html.append(ruta_html.read_text(encoding="utf-8"))
    spec["instructions"] = paginas_html

    return spec


if __name__ == "__main__":
    datos = preparar_especificacion()
    print(
        f"[OK] Especificación validada: {len(datos['devices'])} dispositivos, "
        f"{len(datos['links'])} enlaces, {len(datos['instructions'])} hitos HTML."
    )
