#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_topologia.py -- Constructor programático de las topologías `.pkt` para el
escenario de Direccionamiento Dinámico IPv6 en Propiedad Horizontal (5 departamentos).

Soporta tres modos de construcción:
  - "inicial"     : Topología base limpia para el estudiante (14 dispositivos, 13 enlaces,
                    APs encendidos, residuos IPv4/servicios de plantilla limpiados, sin
                    configuraciones finales de IPv6/VLANs).
  - "resuelta"    : Topología completamente configurada (Answer Network / Versión Maestro)
                    con Router-on-a-Stick IPv6, SLAAC (VLAN 10, 50), DHCPv6 Stateless
                    (VLAN 20, 40), DHCPv6 Stateful (VLAN 30), SRV-DNS con registros AAAA
                    y clientes IPv6 activos.
  - "diagnostico" : Topología para el Hito 10 (Troubleshooting) con los 3 fallos técnicos
                    inyectados en R1 y SW1.
"""

from __future__ import annotations

import os
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Literal

import compat_windows
import lab_api
import pt9
from preparar_spec import RUTA_ESCENARIO_DEFAULT, preparar_especificacion

ModoTopologia = Literal["inicial", "resuelta", "diagnostico"]

RUTA_TEMPLATES = compat_windows.RUTA_REPO_TOOLS / "device_templates.json"
RUTA_SEED = compat_windows.RUTA_REPO_TOOLS / "network_seed.xml"
RUTA_PLANTILLAS_LOCALES = Path(__file__).resolve().parent.parent / "plantillas"


def _asignar_subelemento(padre: ET.Element, etiqueta: str, valor: str) -> ET.Element:
    """Busca o crea un subelemento XML directo y asigna su texto."""
    nodo = padre.find(etiqueta)
    if nodo is None:
        nodo = ET.SubElement(padre, etiqueta)
    nodo.text = valor
    return nodo


def normalizar_direcciones_red(raiz_red: ET.Element, offset_base: int = 0) -> None:
    """Normaliza y garantiza DEV_ADDR y MEM_ADDR únicos para cada dispositivo
    en una red Packet Tracer (<PACKETTRACER5> o <NETWORK>), y alinea los punteros
    de memoria FROM_DEVICE_MEM_ADDR y TO_DEVICE_MEM_ADDR en los cables con el
    DEV_ADDR del dispositivo correspondiente.
    """
    mapa_dev: dict[str, str] = {}
    mapa_mem: dict[str, str] = {}

    dispositivos = raiz_red.findall(".//NETWORK/DEVICES/DEVICE")
    if not dispositivos:
        dispositivos = raiz_red.findall(".//DEVICES/DEVICE")

    for i, disp in enumerate(dispositivos):
        ref_id = disp.findtext("SAVE_REF_ID") or disp.findtext("ENGINE/SAVE_REF_ID") or f"dev-{i}"
        nombre = disp.findtext("NAME") or disp.findtext("ENGINE/NAME") or f"dev-{i}"
        dev_addr = str(107890600000000 + offset_base + (i + 1) * 100000)
        mem_addr = str(107890700000000 + offset_base + (i + 1) * 100000)
        mapa_dev[ref_id] = dev_addr
        mapa_dev[nombre] = dev_addr
        mapa_mem[ref_id] = mem_addr
        mapa_mem[nombre] = mem_addr

        # Asegurar WORKSPACE/LOGICAL
        ws = disp.find("WORKSPACE")
        if ws is None:
            ws = ET.SubElement(disp, "WORKSPACE")
        logical = ws.find("LOGICAL")
        if logical is None:
            logical = ET.SubElement(ws, "LOGICAL")

        _asignar_subelemento(logical, "DEV_ADDR", dev_addr)
        _asignar_subelemento(logical, "MEM_ADDR", mem_addr)

        # Si ENGINE tiene MEM_ADDR o DEV_ADDR, sincronizarlos
        engine = disp.find("ENGINE")
        if engine is not None:
            if engine.find("MEM_ADDR") is not None:
                _asignar_subelemento(engine, "MEM_ADDR", mem_addr)
            if engine.find("DEV_ADDR") is not None:
                _asignar_subelemento(engine, "DEV_ADDR", dev_addr)

    enlaces = raiz_red.findall(".//NETWORK/LINKS/LINK")
    if not enlaces:
        enlaces = raiz_red.findall(".//LINKS/LINK")

    for j, enl in enumerate(enlaces):
        cable = enl.find("CABLE")
        if cable is None:
            continue
        frm = cable.findtext("FROM") or ""
        to = cable.findtext("TO") or ""

        f_dev_addr = (
            mapa_dev.get(frm)
            or mapa_dev.get(frm.replace("save-ref-id:", ""))
            or str(107890600000000 + (j + 1) * 100000 + 1)
        )
        t_dev_addr = (
            mapa_dev.get(to)
            or mapa_dev.get(to.replace("save-ref-id:", ""))
            or str(107890600000000 + (j + 1) * 100000 + 2)
        )

        _asignar_subelemento(cable, "FROM_DEVICE_MEM_ADDR", f_dev_addr)
        _asignar_subelemento(cable, "TO_DEVICE_MEM_ADDR", t_dev_addr)
        _asignar_subelemento(cable, "FROM_PORT_MEM_ADDR", str(int(f_dev_addr) + (j + 1) * 10 + 1))
        _asignar_subelemento(cable, "TO_PORT_MEM_ADDR", str(int(t_dev_addr) + (j + 1) * 10 + 2))


def _limpiar_residuos_plantilla(dispositivo_el: ET.Element, modelo: str) -> None:
    """Elimina direcciones IPv4 residuales (1.1.1.1 / 192.168.10.2) y servicios
    heredados de la plantilla (ACS_CLIENTS, USERS, serverPool DHCPv4, etc.).
    """
    motor = dispositivo_el.find("ENGINE")
    if motor is None:
        return

    if modelo in ("PC-PT", "Server-PT"):
        _asignar_subelemento(motor, "GATEWAY", "")
        _asignar_subelemento(motor, "GATEWAYV6", "")
        dns_cli = motor.find("DNS_CLIENT")
        if dns_cli is not None:
            _asignar_subelemento(dns_cli, "SERVER_IP", "")
            _asignar_subelemento(dns_cli, "SERVER_IPV6", "")

        for puerto in dispositivo_el.iter("PORT"):
            if puerto.findtext("TYPE") == "eCopperFastEthernet":
                _asignar_subelemento(puerto, "IP", "")
                _asignar_subelemento(puerto, "SUBNET", "")
                _asignar_subelemento(puerto, "PORT_GATEWAY", "")
                _asignar_subelemento(puerto, "PORT_DNS", "")
                _asignar_subelemento(puerto, "PORT_DHCP_ENABLE", "false")
                _asignar_subelemento(puerto, "IPV6_ENABLED", "false")
                _asignar_subelemento(puerto, "IPV6_ADDRESS_AUTOCONFIG", "false")
                _asignar_subelemento(puerto, "IPV6_PORT_AUTO_CONFIG_ENABLED", "false")
                _asignar_subelemento(puerto, "IPV6_PORT_DHCP_ENABLED", "false")
                _asignar_subelemento(puerto, "IPV6_PORT_GATEWAY", "")
                _asignar_subelemento(puerto, "IPV6_PORT_DNS", "")

    if modelo == "Server-PT":
        # Limpiar residuos de AAA, cuentas FTP, pools DHCPv4 y DNS de la plantilla
        for ruta_contenedor in (
            ".//ACS_SERVER/ACS_CLIENTS",
            ".//ACS_SERVER/USERS",
            ".//USER_ACCOUNT_MNGR",
            ".//DHCP_SERVERS/ASSOCIATED_PORTS/ASSOCIATED_PORT/POOLS",
            ".//DNS_SERVER/NAMESERVER-DATABASE",
        ):
            for contenedor in motor.findall(ruta_contenedor):
                for hijo in list(contenedor):
                    contenedor.remove(hijo)

        for dhcp_srv in motor.findall(".//DHCP_SERVERS/ASSOCIATED_PORTS/ASSOCIATED_PORT/DHCP_SERVER"):
            _asignar_subelemento(dhcp_srv, "ENABLED", "0")

        dns_srv = motor.find("DNS_SERVER")
        if dns_srv is not None:
            _asignar_subelemento(dns_srv, "ENABLED", "0")


def _encender_puertos_dispositivo(dispositivo_el: ET.Element, modelo: str) -> None:
    """Garantiza `<POWER>true</POWER>` en los puertos activos del dispositivo.
    Corrige específicamente el Problema 9 de `ENTERPRISE_PROBLEMS.md` en `AccessPoint-PT`,
    cuyos dos puertos (`eCopperFastEthernet` y `eAccessPointWirelessG`) vienen con
    `<POWER>false</POWER>` en la plantilla original.
    """
    for puerto in dispositivo_el.iter("PORT"):
        tipo = puerto.findtext("TYPE") or ""
        if modelo == "AccessPoint-PT" or tipo in (
            "eCopperFastEthernet",
            "eCopperGigabitEthernet",
            "eCopperEthernet",
            "eAccessPointWirelessG",
        ):
            _asignar_subelemento(puerto, "POWER", "true")


def _configurar_pc_ipv6(
    dispositivo_el: ET.Element, cfg_ipv6: dict[str, Any], numero_depto: int
) -> None:
    """Configura los campos XML de IPv6 en un terminal `PC-PT` para la red resuelta."""
    motor = dispositivo_el.find("ENGINE")
    if motor is None:
        return

    modo = cfg_ipv6.get("mode", "slaac")
    gateway = cfg_ipv6.get("gateway", "")
    dns = cfg_ipv6.get("dns", "")
    prefijo_red = cfg_ipv6.get("prefix", f"2001:DB8:ACAD:{numero_depto * 10}::/64")
    base_prefijo = prefijo_red.split("::/")[0]

    _asignar_subelemento(motor, "GATEWAYV6", gateway)
    dns_cli = motor.find("DNS_CLIENT")
    if dns_cli is not None:
        _asignar_subelemento(dns_cli, "SERVER_IP", "")
        _asignar_subelemento(dns_cli, "SERVER_IPV6", dns)

    for puerto in dispositivo_el.iter("PORT"):
        if puerto.findtext("TYPE") != "eCopperFastEthernet":
            continue
        _asignar_subelemento(puerto, "POWER", "true")
        _asignar_subelemento(puerto, "IPV6_ENABLED", "true")
        _asignar_subelemento(puerto, "IPV6_ADDRESS_AUTOCONFIG", "true")
        _asignar_subelemento(puerto, "IPV6_PORT_AUTO_CONFIG_ENABLED", "true")
        _asignar_subelemento(
            puerto, "IPV6_PORT_DHCP_ENABLED", "true" if modo == "stateful" else "false"
        )
        _asignar_subelemento(puerto, "IPV6_PORT_GATEWAY", gateway)
        _asignar_subelemento(puerto, "IPV6_PORT_DNS", dns)
        _asignar_subelemento(
            puerto, "IPV6_LINK_LOCAL", f"FE80::{numero_depto * 10}:100"
        )

        # Registrar dirección GUA esperada en el contenedor <IPV6_ADDRESSES>
        contenedor_addrs = puerto.find("IPV6_ADDRESSES")
        if contenedor_addrs is None:
            contenedor_addrs = ET.SubElement(puerto, "IPV6_ADDRESSES")
        for hijo in list(contenedor_addrs):
            contenedor_addrs.remove(hijo)
        nodo_addr = ET.SubElement(contenedor_addrs, "IPV6_ADDRESS")
        ET.SubElement(nodo_addr, "ADDRESS").text = f"{base_prefijo}::100"
        ET.SubElement(nodo_addr, "PREFIX").text = "64"


def _configurar_servidor_dns_ipv6(
    dispositivo_el: ET.Element,
    cfg_ipv6: dict[str, Any],
    registros_aaaa: list[dict[str, str]],
) -> None:
    """Configura IPv6 estático y registros AAAA en `SRV-DNS` (`Server-PT`)."""
    motor = dispositivo_el.find("ENGINE")
    if motor is None:
        return

    direccion = cfg_ipv6["address"]
    prefijo = str(cfg_ipv6.get("prefix", 64))
    link_local = cfg_ipv6.get("link_local", "FE80::99:10")
    gateway = cfg_ipv6["gateway"]
    dns_ip = cfg_ipv6["dns"]

    _asignar_subelemento(motor, "GATEWAYV6", gateway)
    dns_cli = motor.find("DNS_CLIENT")
    if dns_cli is not None:
        _asignar_subelemento(dns_cli, "SERVER_IP", "")
        _asignar_subelemento(dns_cli, "SERVER_IPV6", dns_ip)

    for puerto in dispositivo_el.iter("PORT"):
        if puerto.findtext("TYPE") != "eCopperFastEthernet":
            continue
        _asignar_subelemento(puerto, "POWER", "true")
        _asignar_subelemento(puerto, "IPV6_ENABLED", "true")
        _asignar_subelemento(puerto, "IPV6_ADDRESS_AUTOCONFIG", "false")
        _asignar_subelemento(puerto, "IPV6_PORT_AUTO_CONFIG_ENABLED", "false")
        _asignar_subelemento(puerto, "IPV6_PORT_DHCP_ENABLED", "false")
        _asignar_subelemento(puerto, "IPV6_LINK_LOCAL", link_local)
        _asignar_subelemento(puerto, "IPV6_PORT_GATEWAY", gateway)
        _asignar_subelemento(puerto, "IPV6_PORT_DNS", dns_ip)

        contenedor_addrs = puerto.find("IPV6_ADDRESSES")
        if contenedor_addrs is None:
            contenedor_addrs = ET.SubElement(puerto, "IPV6_ADDRESSES")
        for hijo in list(contenedor_addrs):
            contenedor_addrs.remove(hijo)
        nodo_addr = ET.SubElement(contenedor_addrs, "IPV6_ADDRESS")
        ET.SubElement(nodo_addr, "ADDRESS").text = direccion
        ET.SubElement(nodo_addr, "PREFIX").text = prefijo

    dns_srv = motor.find("DNS_SERVER")
    if dns_srv is None:
        dns_srv = ET.SubElement(motor, "DNS_SERVER")
    _asignar_subelemento(
        dns_srv, "ENABLED", "1" if cfg_ipv6.get("dns_service_enabled", True) else "0"
    )
    base_datos = dns_srv.find("NAMESERVER-DATABASE")
    if base_datos is None:
        base_datos = ET.SubElement(dns_srv, "NAMESERVER-DATABASE")
    for hijo in list(base_datos):
        base_datos.remove(hijo)

    # REGLA ESTRICTA CISCO PACKET TRACER 9.0.1:
    # No serializar elementos <RESOURCE-RECORD> dentro de <NAMESERVER-DATABASE>.
    # Packet Tracer 9.0.1 rechaza el documento completo ("Incompatible File") si
    # se inyectan registros DNS estáticos precompilados. Se mantiene el servicio
    # DNS activo (<ENABLED>1</ENABLED>) con la base de datos limpia (<NAMESERVER-DATABASE/>).


def _sincronizar_startup_y_atributos_ios(
    dispositivo_el: ET.Element, lineas_config: list[str], modelo: str
) -> None:
    """Sincroniza `<STARTUPCONFIG>` con `<RUNNINGCONFIG>` y actualiza banderas de
    motor/puerto en `2911` y `2960-24TT` para coherencia interna del XML.
    """
    motor = dispositivo_el.find("ENGINE")
    if motor is None:
        return

    for sc in list(motor.findall("STARTUPCONFIG")):
        motor.remove(sc)
    sc = ET.SubElement(motor, "STARTUPCONFIG")
    for linea in lineas_config:
        ET.SubElement(sc, "LINE").text = linea

    if modelo == "2911":
        _asignar_subelemento(motor, "DOMAIN_NAME", "propiedadhorizontal.local")
        for puerto in dispositivo_el.iter("PORT"):
            if puerto.findtext("TYPE") == "eCopperGigabitEthernet":
                _asignar_subelemento(puerto, "POWER", "true")
                _asignar_subelemento(puerto, "IPV6_ENABLED", "true")


def construir_topologia_pkt(
    spec: dict[str, Any],
    ruta_salida: str | os.PathLike,
    modo: ModoTopologia = "resuelta",
) -> str:
    """Construye un archivo `.pkt` en `ruta_salida` según `modo` ("inicial", "resuelta"
    o "diagnostico") y devuelve el documento XML `<PACKETTRACER5>...</PACKETTRACER5>`.
    """
    modelos, modulos = lab_api.load_templates(str(RUTA_TEMPLATES))
    # Sobrescribir con plantillas donantes completas de Cisco Packet Tracer 9.0.1
    # que contienen todos los 43/41/66/52 tags en ENGINE y licencias con <IS_BOOTABLE>1</IS_BOOTABLE>,
    # garantizando acceso al Terminal/CLI y a la pestaña Config.
    donantes = {
        "2911": RUTA_PLANTILLAS_LOCALES / "r1_clean_donor.xml",
        "2960-24TT": RUTA_PLANTILLAS_LOCALES / "sw1_clean_donor.xml",
        "Server-PT": RUTA_PLANTILLAS_LOCALES / "srv_clean_donor.xml",
        "PC-PT": RUTA_PLANTILLAS_LOCALES / "pc_clean_donor.xml",
    }
    for mod_key, r_donante in donantes.items():
        if r_donante.is_file():
            modelos[mod_key] = r_donante.read_bytes()

    laboratorio = lab_api.Lab(str(RUTA_SEED), modelos, modulos)
    laboratorio.prune_seed_devices()

    configurado = modo in ("resuelta", "diagnostico")
    registros_aaaa = spec["servicios"]["dns_server"]["registros_aaaa"]
    ids_dispositivos: dict[str, str] = {}

    for disp in spec["devices"]:
        nombre = disp["name"]
        modelo = disp["model"]
        coord_x = int(disp.get("x", 100))
        coord_y = int(disp.get("y", 100))
        encendido = bool(disp.get("power", True))

        lineas_ios: list[str] | None = None
        if configurado:
            if modo == "diagnostico" and "config_diagnostico" in disp:
                lineas_ios = disp["config_diagnostico"]
            else:
                lineas_ios = disp.get("config")
        else:
            # En modo inicial dejamos un arranque limpio sin configurar el laboratorio
            if modelo == "2911":
                lineas_ios = ["!", "version 15.1", "hostname Router", "!", "end"]
            elif modelo == "2960-24TT":
                lineas_ios = ["!", "version 12.2", "hostname Switch", "!", "end"]

        sid = laboratorio.add_device(
            modelo,
            nombre,
            x=coord_x,
            y=coord_y,
            power=encendido,
            ios_config=lineas_ios,
            pc_ip=None,
            install=disp.get("install"),
        )
        ids_dispositivos[nombre] = sid
        elemento_dev = laboratorio._els[sid]

        # 1. Limpiar residuos de plantilla en todos los modos
        _limpiar_residuos_plantilla(elemento_dev, modelo)

        # 2. Encender puertos en AccessPoint-PT y demás dispositivos
        if modo == "inicial" and modelo == "2911":
            # En modo inicial los puertos del router inician administrativamente apagados o sin IPv6,
            # pero AccessPoint-PT, Switch, PCs y Server deben tener <POWER>true</POWER> físico.
            pass
        else:
            _encender_puertos_dispositivo(elemento_dev, modelo)

        if modelo == "AccessPoint-PT":
            _encender_puertos_dispositivo(elemento_dev, modelo)
            if "ssid" in disp:
                laboratorio.set_wireless(sid, ssid=disp["ssid"])

        # 3. Aplicar configuración avanzada si estamos en modo resuelta o diagnóstico
        if configurado:
            if modelo in ("2911", "2960-24TT") and lineas_ios:
                _sincronizar_startup_y_atributos_ios(elemento_dev, lineas_ios, modelo)
            elif modelo == "PC-PT" and "ipv6_config" in disp:
                num_depto = int(nombre.split("-D")[-1]) if "-D" in nombre else 1
                _configurar_pc_ipv6(elemento_dev, disp["ipv6_config"], num_depto)
            elif modelo == "Server-PT" and "ipv6_config" in disp:
                _configurar_servidor_dns_ipv6(
                    elemento_dev, disp["ipv6_config"], registros_aaaa
                )
        else:
            if modelo in ("2911", "2960-24TT") and lineas_ios:
                _sincronizar_startup_y_atributos_ios(elemento_dev, lineas_ios, modelo)

    # 4. Cablear los 13 enlaces
    for enlace in spec["links"]:
        id_a = ids_dispositivos[enlace["a"]]
        id_b = ids_dispositivos[enlace["b"]]
        laboratorio.link(
            id_a,
            enlace["aport"],
            id_b,
            enlace["bport"],
            kind=enlace.get("kind", "copper"),
        )

    # 5. Normalizar DEV_ADDR, MEM_ADDR y punteros de cable (FROM/TO_DEVICE_MEM_ADDR)
    # para compatibilidad estricta con Cisco Packet Tracer 9.0.1
    normalizar_direcciones_red(laboratorio.base)

    ruta_destino = Path(ruta_salida)
    ruta_destino.parent.mkdir(parents=True, exist_ok=True)
    laboratorio.save(str(ruta_destino))

    xml_decodificado = pt9.decode(str(ruta_destino), "pkt").decode("utf-8")
    return xml_decodificado


if __name__ == "__main__":
    especificacion = preparar_especificacion(RUTA_ESCENARIO_DEFAULT)
    dir_salida = RUTA_ESCENARIO_DEFAULT.parent / "salida"
    xml_ini = construir_topologia_pkt(
        especificacion, dir_salida / "topologia_inicial.pkt", modo="inicial"
    )
    xml_res = construir_topologia_pkt(
        especificacion, dir_salida / "topologia_resuelta.pkt", modo="resuelta"
    )
    xml_diag = construir_topologia_pkt(
        especificacion,
        dir_salida / "topologia_diagnostico_hito10.pkt",
        modo="diagnostico",
    )
    print(
        f"[OK] Topologías .pkt generadas en {dir_salida}:\n"
        f"  - topologia_inicial.pkt ({len(xml_ini)} bytes XML)\n"
        f"  - topologia_resuelta.pkt ({len(xml_res)} bytes XML)\n"
        f"  - topologia_diagnostico_hito10.pkt ({len(xml_diag)} bytes XML)"
    )
