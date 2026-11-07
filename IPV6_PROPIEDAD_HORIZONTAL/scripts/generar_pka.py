#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_pka.py -- Orquestador principal de 12 pasos para generar automáticamente los
archivos `.pkt` y `.pka` del proyecto "Implementación de Direccionamiento Dinámico
en una Red IPv6 (Propiedad Horizontal)".

Uso desde Windows PowerShell o Ubuntu WSL:
    python IPV6_PROPIEDAD_HORIZONTAL/scripts/generar_pka.py --spec IPV6_PROPIEDAD_HORIZONTAL/escenario.json
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
from pathlib import Path
from typing import Any

import compat_windows
import activity
from generar_topologia import construir_topologia_pkt
from preparar_spec import RUTA_ESCENARIO_DEFAULT, preparar_especificacion
from scoring_ipv6 import generar_scoring_ipv6
from validar_ipv6 import auditar_red_diagnostico_hito10, auditar_red_resuelta_ipv6
from validar_pka import validar_archivo_pka, validar_archivo_pkt

RUTA_SKELETON = compat_windows.RUTA_REPO_TOOLS / "activity_skeleton.xml"


def _ensamblar_archivo_pka(
    ruta_salida: Path,
    xml_inicial: str,
    xml_respuesta: str,
    init_scoring_xml: str,
    comp_scoring_xml: str,
    paginas_html: list[str],
    metadata: dict[str, Any],
) -> None:
    """Construye y guarda un archivo `.pka` completo a partir de `activity_skeleton.xml`."""
    act = activity.Activity(str(RUTA_SKELETON))
    act.set_instructions(list(paginas_html), enable_tab=True, layout=0, title=metadata["titulo"])
    act.set_password(metadata.get("password_actividad", "IPV6_MAESTRO_2026"))
    act.set_permissions(
        locked=False,
        noguest=False,
        component_list="Ip, Switching, Routing, Physical, Other",
        locking_enabled=False,
    )
    act.set_feedback(
        incomplete=metadata.get("feedback_incompleto", "Sigue avanzando con los hitos."),
        complete=metadata.get("feedback_completo", "¡Laboratorio completado al 100%!"),
    )
    # Limpiar atributos de temporizador heredados de activity_skeleton.xml
    # para evitar valores negativos (COUNTDOWNLEFT=-1175269632) y tiempo previo (ELAPSED=22369)
    act._set_attr("ACTIVITY", "COUNTDOWNLEFT", "0")
    act._set_attr("ACTIVITY", "COUNTDOWNMS", "0")
    act._set_attr("ACTIVITY", "COUNTDOWN_EXPIRED", "0")
    act._set_attr("ACTIVITY", "ELAPSED", "0")
    act._set_attr("ACTIVITY", "FORWARD_ANS_SIM_MS", "0")
    act._set_attr("ACTIVITY", "ENABLED", "no")
    act._set_attr("ACTIVITY", "TIMERTYPE", "0")

    act.set_scoring_xml(init_scoring_xml, comp_scoring_xml)
    act.set_networks(initial_xml=xml_inicial, answer_xml=xml_respuesta)
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    act.save(str(ruta_salida))


def ejecutar_pipeline_completo(
    ruta_spec: Path = RUTA_ESCENARIO_DEFAULT,
    directorio_salida: Path | None = None,
) -> dict[str, Any]:
    """Ejecuta el flujo de trabajo de 12 pasos para generar y validar todos los artefactos."""
    if directorio_salida is None:
        directorio_salida = ruta_spec.resolve().parent / "salida"
    directorio_salida.mkdir(parents=True, exist_ok=True)

    lineas_log: list[str] = []

    def registrar(paso: int, mensaje: str) -> None:
        marca = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        linea = f"[{marca}] [Paso {paso:02d}/12] {mensaje}"
        print(linea)
        lineas_log.append(linea)

    # Paso 1: Leer y validar escenario.json + configuraciones + instrucciones HTML
    registrar(1, f"Cargando y validando especificación desde {ruta_spec.name} (Backend: {compat_windows.BACKEND_ACTIVO})")
    spec = preparar_especificacion(ruta_spec)

    # Paso 2: Verificar plantillas de dispositivos y coordenadas
    registrar(2, f"Verificados {len(spec['devices'])} dispositivos, {len(spec['links'])} enlaces y {len(spec['departamentos'])} departamentos IPv6")

    # Paso 3: Construir red inicial del estudiante (topologia_inicial.pkt)
    ruta_pkt_inicial = directorio_salida / "topologia_inicial.pkt"
    registrar(3, f"Construyendo red inicial del estudiante -> {ruta_pkt_inicial.name}")
    xml_inicial = construir_topologia_pkt(spec, ruta_pkt_inicial, modo="inicial")

    # Paso 4: Construir red de respuesta / solución completa (topologia_resuelta.pkt)
    ruta_pkt_resuelta = directorio_salida / "topologia_resuelta.pkt"
    registrar(4, f"Construyendo red de respuesta (Answer Network) -> {ruta_pkt_resuelta.name}")
    xml_resuelta = construir_topologia_pkt(spec, ruta_pkt_resuelta, modo="resuelta")

    # Paso 5: Construir red de diagnóstico con 3 fallos para el Hito 10
    ruta_pkt_diag = directorio_salida / "topologia_diagnostico_hito10.pkt"
    registrar(5, f"Construyendo red de diagnóstico Hito 10 (3 fallos inyectados) -> {ruta_pkt_diag.name}")
    xml_diagnostico = construir_topologia_pkt(spec, ruta_pkt_diag, modo="diagnostico")

    # Paso 6: Generar árbol de calificación automática (INITIALSETUP / COMPARISONS)
    registrar(6, "Generando árboles de evaluación <INITIALSETUP> y <COMPARISONS> desde device_shapes.json")
    init_sc, comp_sc, resumen_scoring = generar_scoring_ipv6(spec)
    registrar(
        6,
        f"Árbol de scoring compilado: {resumen_scoring['dispositivos_evaluados']} dispositivos evaluados, "
        f"{resumen_scoring['total_puntos_evaluacion']} puntos totales",
    )

    # Paso 7: Ensamblar Grupo_IPV6_Estudiante.pka (Inicial = sin configurar, Respuesta = resuelta)
    ruta_pka_estudiante = directorio_salida / "Grupo_IPV6_Estudiante.pka"
    registrar(7, f"Ensamblando actividad principal del estudiante -> {ruta_pka_estudiante.name}")
    _ensamblar_archivo_pka(
        ruta_pka_estudiante,
        xml_inicial=xml_inicial,
        xml_respuesta=xml_resuelta,
        init_scoring_xml=init_sc,
        comp_scoring_xml=comp_sc,
        paginas_html=spec["instructions"],
        metadata=spec["metadata"],
    )

    # Paso 8: Ensamblar Grupo_IPV6_Maestro.pka (Inicial = resuelta, Respuesta = resuelta -> 100% inmediato)
    ruta_pka_maestro = directorio_salida / "Grupo_IPV6_Maestro.pka"
    registrar(8, f"Ensamblando actividad resuelta del docente (100% Check Results) -> {ruta_pka_maestro.name}")
    _ensamblar_archivo_pka(
        ruta_pka_maestro,
        xml_inicial=xml_resuelta,
        xml_respuesta=xml_resuelta,
        init_scoring_xml=init_sc,
        comp_scoring_xml=comp_sc,
        paginas_html=spec["instructions"],
        metadata=spec["metadata"],
    )

    # Paso 9: Ensamblar Grupo_IPV6_Diagnostico_Hito10.pka (Inicial = con 3 fallos, Respuesta = resuelta)
    ruta_pka_diag = directorio_salida / "Grupo_IPV6_Diagnostico_Hito10.pka"
    registrar(9, f"Ensamblando actividad de diagnóstico Hito 10 -> {ruta_pka_diag.name}")
    _ensamblar_archivo_pka(
        ruta_pka_diag,
        xml_inicial=xml_diagnostico,
        xml_respuesta=xml_resuelta,
        init_scoring_xml=init_sc,
        comp_scoring_xml=comp_sc,
        paginas_html=spec["instructions"],
        metadata=spec["metadata"],
    )

    # Paso 10: Validar estructuralmente todos los contenedores .pkt y .pka
    registrar(10, "Ejecutando validación criptográfica EAX y estructural de archivos .pkt y .pka")
    validaciones_pkt = {
        ruta.name: validar_archivo_pkt(ruta)
        for ruta in (ruta_pkt_inicial, ruta_pkt_resuelta, ruta_pkt_diag)
    }
    validaciones_pka = {
        ruta.name: validar_archivo_pka(ruta)
        for ruta in (ruta_pka_estudiante, ruta_pka_maestro, ruta_pka_diag)
    }

    # Paso 11: Auditar configuración IPv6 (SLAAC, Stateless, Stateful, VLANs, DNS AAAA y fallos Hito 10)
    registrar(11, "Ejecutando auditoría técnica de protocolos IPv6, DHCPv6, RA, VLANs y DNS AAAA")
    auditoria_ipv6 = auditar_red_resuelta_ipv6(ruta_pkt_resuelta)
    auditoria_hito10 = auditar_red_diagnostico_hito10(ruta_pkt_diag)

    todos_validos = (
        all(v["valido"] for v in validaciones_pkt.values())
        and all(v["valido"] for v in validaciones_pka.values())
        and auditoria_ipv6["valido"]
        and auditoria_hito10["valido"]
    )

    # Paso 12: Emitir informe_generacion.json y log_generacion.txt
    informe = {
        "proyecto": spec["metadata"]["titulo"],
        "fecha_generacion": datetime.datetime.now().isoformat(),
        "backend_criptografico": compat_windows.BACKEND_ACTIVO,
        "plataforma_ejecucion": sys.platform,
        "python_version": sys.version.split()[0],
        "estado_global": "EXITOSO" if todos_validos else "CON_ERRORES",
        "resumen_topologia": {
            "total_dispositivos": len(spec["devices"]),
            "total_enlaces": len(spec["links"]),
            "total_departamentos": len(spec["departamentos"]),
            "total_hitos_html": len(spec["instructions"]),
        },
        "resumen_scoring": resumen_scoring,
        "validaciones_pkt": validaciones_pkt,
        "validaciones_pka": validaciones_pka,
        "auditoria_ipv6_resuelta": auditoria_ipv6,
        "auditoria_diagnostico_hito10": auditoria_hito10,
    }

    ruta_informe = directorio_salida / "informe_generacion.json"
    ruta_log = directorio_salida / "log_generacion.txt"
    registrar(12, f"Guardando {ruta_informe.name} y {ruta_log.name} (Estado global: {informe['estado_global']})")

    ruta_informe.write_text(
        json.dumps(informe, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    ruta_log.write_text("\n".join(lineas_log) + "\n", encoding="utf-8")

    if not todos_validos:
        raise RuntimeError(
            f"La generación terminó con errores de validación. Revise {ruta_informe}"
        )

    return informe


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generador automático de laboratorios IPv6 (.pkt / .pka) para Propiedad Horizontal"
    )
    parser.add_argument(
        "--spec",
        default=str(RUTA_ESCENARIO_DEFAULT),
        help="Ruta al archivo JSON de especificación (por defecto: escenario.json)",
    )
    parser.add_argument(
        "--out-dir",
        default=None,
        help="Directorio de salida para los archivos .pkt y .pka (por defecto: salida/)",
    )
    args = parser.parse_args()

    ruta_spec = Path(args.spec).resolve()
    dir_out = Path(args.out_dir).resolve() if args.out_dir else None
    ejecutar_pipeline_completo(ruta_spec, dir_out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
