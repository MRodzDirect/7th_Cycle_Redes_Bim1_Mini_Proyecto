# Proyecto: Generador Automático `.pka` / `.pkt` — Direccionamiento Dinámico IPv6 en Propiedad Horizontal

Este repositorio contiene la implementación integral del proyecto especificado en [`README-PLAN.md`](file:///c:/Users/MRodz/Documents/U/7th_Cycle/Networking_and_Distributed_Systems/Week%205/Proyecto/README-PLAN.md) y [`PLANIFICACION.md`](file:///c:/Users/MRodz/Documents/U/7th_Cycle/Networking_and_Distributed_Systems/Week%205/Proyecto/PLANIFICACION.md).

Toda la implementación del proyecto reside en [`IPV6_PROPIEDAD_HORIZONTAL/`](file:///c:/Users/MRodz/Documents/U/7th_Cycle/Networking_and_Distributed_Systems/Week%205/Proyecto/IPV6_PROPIEDAD_HORIZONTAL/README.md), apoyándose en el repositorio base [`GENERADOR/packet-tracer-pkt-format/`](file:///c:/Users/MRodz/Documents/U/7th_Cycle/Networking_and_Distributed_Systems/Week%205/Proyecto/GENERADOR/packet-tracer-pkt-format/README.md) sin modificar ninguno de sus archivos originales.

## Resumen de Artefactos Generados

- **Topologías `.pkt` listas para Packet Tracer 8.2+:**
  - [`IPV6_PROPIEDAD_HORIZONTAL/salida/topologia_inicial.pkt`](file:///c:/Users/MRodz/Documents/U/7th_Cycle/Networking_and_Distributed_Systems/Week%205/Proyecto/IPV6_PROPIEDAD_HORIZONTAL/salida/topologia_inicial.pkt): Topología física completa (14 dispositivos, 13 enlaces) sin configuración lógica IPv6.
  - [`IPV6_PROPIEDAD_HORIZONTAL/salida/topologia_resuelta.pkt`](file:///c:/Users/MRodz/Documents/U/7th_Cycle/Networking_and_Distributed_Systems/Week%205/Proyecto/IPV6_PROPIEDAD_HORIZONTAL/salida/topologia_resuelta.pkt): Topología 100% resuelta (Golden Master) con SLAAC, DHCPv6 Stateless, DHCPv6 Stateful, VLANs 10–50 y 9 registros DNS `AAAA`.
  - [`IPV6_PROPIEDAD_HORIZONTAL/salida/topologia_diagnostico_hito10.pkt`](file:///c:/Users/MRodz/Documents/U/7th_Cycle/Networking_and_Distributed_Systems/Week%205/Proyecto/IPV6_PROPIEDAD_HORIZONTAL/salida/topologia_diagnostico_hito10.pkt): Topología con las 3 fallas deliberadas del Hito 10 inyectadas para práctica de *troubleshooting*.
- **Actividades Interactivas `.pka` (Activity Wizard con 194 puntos de evaluación y 10 Hitos HTML):**
  - [`IPV6_PROPIEDAD_HORIZONTAL/salida/Grupo_IPV6_Estudiante.pka`](file:///c:/Users/MRodz/Documents/U/7th_Cycle/Networking_and_Distributed_Systems/Week%205/Proyecto/IPV6_PROPIEDAD_HORIZONTAL/salida/Grupo_IPV6_Estudiante.pka): Actividad principal para estudiantes (inicia en 0/194 puntos).
  - [`IPV6_PROPIEDAD_HORIZONTAL/salida/Grupo_IPV6_Maestro.pka`](file:///c:/Users/MRodz/Documents/U/7th_Cycle/Networking_and_Distributed_Systems/Week%205/Proyecto/IPV6_PROPIEDAD_HORIZONTAL/salida/Grupo_IPV6_Maestro.pka): Actividad pre-resuelta para validación docente (inicia en 194/194 puntos — 100%).
  - [`IPV6_PROPIEDAD_HORIZONTAL/salida/Grupo_IPV6_Diagnostico_Hito10.pka`](file:///c:/Users/MRodz/Documents/U/7th_Cycle/Networking_and_Distributed_Systems/Week%205/Proyecto/IPV6_PROPIEDAD_HORIZONTAL/salida/Grupo_IPV6_Diagnostico_Hito10.pka): Actividad de diagnóstico del Hito 10.
- **Documentación Detallada:**
  - Consulte [`IPV6_PROPIEDAD_HORIZONTAL/README.md`](file:///c:/Users/MRodz/Documents/U/7th_Cycle/Networking_and_Distributed_Systems/Week%205/Proyecto/IPV6_PROPIEDAD_HORIZONTAL/README.md) para el informe técnico completo, tablas de direccionamiento, arquitectura de scripts y guía de ejecución en **Windows PowerShell** y **Ubuntu WSL**.
