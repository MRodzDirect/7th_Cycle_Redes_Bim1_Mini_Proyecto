#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificador automatizado de aceptación en Cisco Packet Tracer 9.0.1 para Windows.

Equivalente en Windows de ``tools/pt_accept.py``: lanza ``PacketTracer.exe``
con cada archivo ``.pkt`` o ``.pka``, monitorea las ventanas Win32 del proceso
mediante ``ctypes.windll.user32`` (sin depender de X11/xvfb), detecta diálogos
modales de error o rechazo de archivo y cierra limpiamente la instancia lanzada.
"""

from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
import glob
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any


user32 = ctypes.windll.user32

WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG),
    ]


def buscar_ejecutable_pt(ruta_manual: str | None = None) -> Path:
    """Localiza el binario PacketTracer.exe instalado en Windows."""
    if ruta_manual:
        p = Path(ruta_manual)
        if p.is_file():
            return p
        raise FileNotFoundError(f"No se encontró PacketTracer.exe en: {ruta_manual}")

    patrones = [
        r"C:\Program Files\Cisco Packet Tracer 9.0.1\bin\PacketTracer.exe",
        r"C:\Program Files\Cisco Packet Tracer 9.0\bin\PacketTracer.exe",
        r"C:\Program Files\Cisco Packet Tracer*\bin\PacketTracer.exe",
        r"C:\Program Files (x86)\Cisco Packet Tracer*\bin\PacketTracer.exe",
    ]
    for patron in patrones:
        coincidencias = sorted(glob.glob(patron), reverse=True)
        for c in coincidencias:
            ruta = Path(c)
            if ruta.is_file():
                return ruta

    raise FileNotFoundError(
        "No se encontró PacketTracer.exe en las rutas estándar de Windows."
    )


def _obtener_texto_ventana(hwnd: int) -> str:
    length = user32.GetWindowTextLengthW(hwnd)
    if length <= 0:
        return ""
    buf = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buf, length + 1)
    return buf.value.strip()


def _obtener_clase_ventana(hwnd: int) -> str:
    buf = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, buf, 256)
    return buf.value.strip()


def _obtener_rect_ventana(hwnd: int) -> tuple[int, int, int, int]:
    rect = RECT()
    if user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        return (
            int(rect.left),
            int(rect.top),
            int(rect.right - rect.left),
            int(rect.bottom - rect.top),
        )
    return (0, 0, 0, 0)


def listar_ventanas_visibles(pids_objetivo: set[int] | None = None) -> list[dict[str, Any]]:
    """Enumera todas las ventanas visibles (filtrando opcionalmente por PID)."""
    ventanas: list[dict[str, Any]] = []

    def _callback(hwnd: int, lparam: int) -> bool:
        if not user32.IsWindowVisible(hwnd):
            return True
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pids_objetivo is not None and int(pid.value) not in pids_objetivo:
            return True

        titulo = _obtener_texto_ventana(hwnd)
        clase = _obtener_clase_ventana(hwnd)
        x, y, ancho, alto = _obtener_rect_ventana(hwnd)

        hijos: list[str] = []

        def _child_cb(ch_hwnd: int, _: int) -> bool:
            txt = _obtener_texto_ventana(ch_hwnd)
            if txt:
                hijos.append(txt)
            return True

        user32.EnumChildWindows(hwnd, WNDENUMPROC(_child_cb), 0)

        ventanas.append(
            {
                "hwnd": int(hwnd),
                "pid": int(pid.value),
                "titulo": titulo,
                "clase": clase,
                "ancho": ancho,
                "alto": alto,
                "hijos": hijos,
            }
        )
        return True

    user32.EnumWindows(WNDENUMPROC(_callback), 0)
    return ventanas


def _pids_packet_tracer() -> set[int]:
    """Obtiene los PIDs activos de PacketTracer.exe mediante tasklist."""
    salida = subprocess.run(
        ["tasklist", "/FI", "IMAGENAME eq PacketTracer.exe", "/FO", "CSV", "/NH"],
        capture_output=True,
        text=True,
        check=False,
    ).stdout
    pids: set[int] = set()
    for linea in salida.splitlines():
        partes = [p.strip('"') for p in linea.split('","')]
        if len(partes) >= 2 and partes[0].lower() == "packettracer.exe":
            try:
                pids.append(int(partes[1])) if isinstance(pids, list) else pids.add(int(partes[1]))
            except ValueError:
                pass
    return pids


def probar_archivo_en_pt(
    ruta_pt: Path,
    archivo: Path,
    timeout: float = 35.0,
    espera_estabilidad: float = 4.0,
) -> dict[str, Any]:
    """
    Abre ``archivo`` en PacketTracer.exe y verifica mediante las ventanas Win32
    si el archivo carga limpiamente o si aparece un cuadro de diálogo de error.
    """
    archivo_abs = archivo.resolve()
    nombre_base = archivo_abs.name.lower()
    pids_previos = _pids_packet_tracer()

    inicio = time.monotonic()
    proc = subprocess.Popen(
        [str(ruta_pt), str(archivo_abs)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    momento_carga_detectada: float | None = None
    veredicto = "TIMEOUT"
    detalle = "Tiempo de espera agotado sin respuesta definitiva de la ventana."
    historial_ventanas: list[dict[str, Any]] = []

    try:
        while (time.monotonic() - inicio) < timeout:
            pids_actuales = _pids_packet_tracer() - pids_previos
            pids_actuales.add(proc.pid)
            ventanas = listar_ventanas_visibles(pids_actuales)
            if ventanas:
                historial_ventanas = ventanas

            # Revisar si hay algún diálogo modal pequeño o de error
            for v in ventanas:
                titulo_low = v["titulo"].lower()
                textos_hijos = " ".join(v["hijos"]).lower()

                # Diálogos de error conocidos en inglés o español
                patrones_error = (
                    "incompatible",
                    "unable to open",
                    "no se puede abrir",
                    "corrupted",
                    "corrupto",
                    "invalid",
                    "error",
                    "requires version",
                    "not compatible",
                    "no es compatible",
                )
                if any(p in titulo_low or p in textos_hijos for p in patrones_error):
                    veredicto = "FAIL"
                    detalle = (
                        f"Diálogo de error detectado: titulo={v['titulo']!r}, "
                        f"hijos={v['hijos']!r}, dim={v['ancho']}x{v['alto']}"
                    )
                    return {
                        "archivo": str(archivo),
                        "veredicto": veredicto,
                        "detalle": detalle,
                        "tiempo_s": round(time.monotonic() - inicio, 2),
                        "ventanas": historial_ventanas,
                    }

                # En Qt, un QMessageBox modal sobre la ventana principal suele tener
                # título "Cisco Packet Tracer" o "Packet Tracer" y tamaño reducido (< 650x350)
                if (
                    titulo_low in ("packet tracer", "cisco packet tracer")
                    and 100 < v["ancho"] < 700
                    and 60 < v["alto"] < 380
                    and momento_carga_detectada is not None
                ):
                    veredicto = "FAIL"
                    detalle = (
                        f"QMessageBox modal detectado tras abrir: titulo={v['titulo']!r}, "
                        f"dim={v['ancho']}x{v['alto']}, hijos={v['hijos']!r}"
                    )
                    return {
                        "archivo": str(archivo),
                        "veredicto": veredicto,
                        "detalle": detalle,
                        "tiempo_s": round(time.monotonic() - inicio, 2),
                        "ventanas": historial_ventanas,
                    }

            # Detectar ventana principal con el archivo cargado o ventana de actividad (.pka)
            for v in ventanas:
                titulo_low = v["titulo"].lower()
                es_ventana_documento = (
                    (
                        "cisco packet tracer - " in titulo_low
                        and nombre_base in titulo_low
                    )
                    or ("pt activity" in titulo_low)
                    or (
                        archivo_abs.suffix.lower() == ".pka"
                        and "cisco packet tracer" in titulo_low
                        and v["ancho"] >= 700
                        and len(ventanas) >= 2
                    )
                )
                if es_ventana_documento and momento_carga_detectada is None:
                    momento_carga_detectada = time.monotonic()

            if (
                momento_carga_detectada is not None
                and (time.monotonic() - momento_carga_detectada) >= espera_estabilidad
            ):
                # Verificar en el último instante que no haya ningún popup pequeño
                popups = [
                    v
                    for v in ventanas
                    if 100 < v["ancho"] < 680
                    and 60 < v["alto"] < 360
                    and v["titulo"].lower() in ("packet tracer", "cisco packet tracer", "error", "warning")
                ]
                if popups:
                    veredicto = "FAIL"
                    detalle = f"Popup modal detectado al estabilizar: {popups}"
                else:
                    veredicto = "PASS"
                    titulos = [f"{v['titulo']} ({v['ancho']}x{v['alto']})" for v in ventanas if v["titulo"]]
                    detalle = f"Abierto correctamente en Packet Tracer: {titulos}"
                break

            time.sleep(0.4)
    finally:
        pids_a_cerrar = (_pids_packet_tracer() - pids_previos) | {proc.pid}
        for pid in pids_a_cerrar:
            subprocess.run(
                ["taskkill", "/PID", str(pid), "/T", "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )

    return {
        "archivo": str(archivo),
        "veredicto": veredicto,
        "detalle": detalle,
        "tiempo_s": round(time.monotonic() - inicio, 2),
        "ventanas": historial_ventanas,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verifica apertura real de archivos .pkt y .pka en Cisco Packet Tracer (Windows)."
    )
    parser.add_argument("archivos", nargs="+", help="Rutas de archivos .pkt o .pka a verificar")
    parser.add_argument("--pt-bin", default=None, help="Ruta opcional a PacketTracer.exe")
    parser.add_argument("--timeout", type=float, default=35.0, help="Timeout por archivo en segundos")
    parser.add_argument("--json", action="store_true", help="Imprimir salida en formato JSON")
    args = parser.parse_args(argv)

    ruta_pt = buscar_ejecutable_pt(args.pt_bin)
    resultados = []
    todo_ok = True

    for ruta_str in args.archivos:
        res = probar_archivo_en_pt(ruta_pt, Path(ruta_str), timeout=args.timeout)
        resultados.append(res)
        if res["veredicto"] != "PASS":
            todo_ok = False
        if not args.json:
            print(
                f"[{res['veredicto']}] {res['archivo']} ({res['tiempo_s']}s) -> {res['detalle']}",
                flush=True,
            )

    if args.json:
        print(json.dumps({"pt_bin": str(ruta_pt), "resultados": resultados}, indent=2, ensure_ascii=False))

    return 0 if todo_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
