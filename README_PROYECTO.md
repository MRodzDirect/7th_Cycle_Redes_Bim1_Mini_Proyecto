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

## Estructura Aplicada del Proyecto

```shell
root
|   PLANIFICACION.md
|   README-PLAN.md
|   README_PROYECTO.md
|   sources.md
|
|
+---GENERADOR
|   |   Generador Overview.md
|   |
|   \---packet-tracer-pkt-format
|       |   .gitignore
|       |   BUILDER_PORT.md
|       |   CHANGELOG.md
|       |   FORMAT.md
|       |   LICENSE
|       |   mkdocs.yml
|       |   pt9.py
|       |   pyproject.toml
|       |   README.md
|       |   README.zh-CN.md
|       |   SKILL.md
|       |
|       +---.github
|       |   \---workflows
|       |           ci.yml
|       |           docs.yml
|       |
|       +---build
|       |       ios_attestation.json
|       |
|       +---corpus
|       |   |   CORPUS_INDEX.tsv
|       |   |   fetch_corpus.py
|       |   |   INTERNET_SOURCES.md
|       |   |   README.md
|       |   |   SOURCES.tsv
|       |   |
|       |   \---samples
|       |           sample_activity.pka
|       |           sample_lab.pkt
|       |
|       +---demo
|       |       build_demo.py
|       |
|       +---docs
|       |       ACTIVITY.md
|       |       ANALYSIS_PLAN.md
|       |       CAPABILITIES.md
|       |       CONFIGURATION.md
|       |       CORPUS_REPORT.md
|       |       CORPUS_VERIFICATION.md
|       |       decrypt-pkt-to-xml.md
|       |       ENTERPRISE_PROBLEMS.md
|       |       ENTERPRISE_PROBLEMS_YAMLT.md
|       |       FORMAT_SPECIFICATION.md
|       |       generate-lab-from-python.md
|       |       index.md
|       |       LARGE_TOPOLOGY_TEST.md
|       |       LAYOUT_INVESTIGATION.md
|       |       LEGACY_FORMAT.md
|       |       open-pkt-without-packet-tracer.md
|       |       PACKET_TRACER_VALIDATION.md
|       |       PKA_GENERATION.md
|       |       POWER_INVESTIGATION.md
|       |       SCENE_GRAPH.md
|       |       schema_catalogue.json
|       |       SCHEMA_REFERENCE.md
|       |
|       +---generators
|       |   +---jasdf_aewc
|       |   |   |   build_jasdf_aewc.py
|       |   |   |   jasdf_kit.py
|       |   |   |   pool_renames.json
|       |   |   |   README.md
|       |   |   |   run_all.sh
|       |   |   |   validate.py
|       |   |   |
|       |   |   +---build
|       |   |   |       final_sha256.txt
|       |   |   |       final_sha256_smoke.txt
|       |   |   |       final_sha256_standard.txt
|       |   |   |       port_model.json
|       |   |   |       report_enterprise.json
|       |   |   |       report_smoke.json
|       |   |   |       report_standard.json
|       |   |   |
|       |   |   +---docs
|       |   |   |       ADDRESS_PLAN.csv
|       |   |   |       ADDRESS_PLAN_smoke.csv
|       |   |   |       ADDRESS_PLAN_standard.csv
|       |   |   |       DESIGN.md
|       |   |   |       EVIDENCE.md
|       |   |   |       INVENTORY_enterprise.csv
|       |   |   |       INVENTORY_smoke.csv
|       |   |   |       INVENTORY_standard.csv
|       |   |   |       SERVICES.md
|       |   |   |       SERVICES_smoke.md
|       |   |   |       SERVICES_standard.md
|       |   |   |       SUBNETS.csv
|       |   |   |       SUBNETS_smoke.csv
|       |   |   |       SUBNETS_standard.csv
|       |   |   |       VALIDATION.md
|       |   |   |       VLANS.csv
|       |   |   |       VLANS_smoke.csv
|       |   |   |       VLANS_standard.csv
|       |   |   |
|       |   |   \---tools
|       |   |           build_port_model.py
|       |   |           draw_topology.py
|       |   |           export_plan.py
|       |   |           mine3.py
|       |   |           mine_corpus.py
|       |   |           serial_probe.py
|       |   |           stp_probe.py
|       |   |
|       |   \---jasdf_layout
|       |           layout.patch
|       |           README.md
|       |
|       +---hooks
|       |       rewrite_repo_links.py
|       |
|       +---native
|       |   \---pkt_core_native
|       |       |   Cargo.lock
|       |       |   Cargo.toml
|       |       |   Makefile
|       |       |   pyproject.toml
|       |       |   README.md
|       |       |
|       |       \---src
|       |               cast256.rs
|       |               cast_tables.rs
|       |               lib.rs
|       |               serpent.rs
|       |               twofish.rs
|       |
|       +---overrides
|       |       main.html
|       |
|       +---src
|       |   \---pkt_core
|       |       |   audit.py
|       |       |   diff.py
|       |       |   errors.py
|       |       |   export.py
|       |       |   py.typed
|       |       |   resources.py
|       |       |   __init__.py
|       |       |
|       |       +---builder
|       |       |   |   lab.py
|       |       |   |   __init__.py
|       |       |   |
|       |       |   \---__pycache__
|       |       |           lab.cpython-314.pyc
|       |       |           __init__.cpython-314.pyc
|       |       |
|       |       +---cli
|       |       |       main.py
|       |       |       __init__.py
|       |       |
|       |       +---codec
|       |       |   |   container.py
|       |       |   |   qcompress.py
|       |       |   |   __init__.py
|       |       |   |
|       |       |   \---__pycache__
|       |       |           container.cpython-314.pyc
|       |       |           qcompress.cpython-314.pyc
|       |       |           __init__.cpython-314.pyc
|       |       |
|       |       +---crypto
|       |       |   |   ciphers.py
|       |       |   |   ciphers_pure.py
|       |       |   |   keys.py
|       |       |   |   primitives.py
|       |       |   |   stream.py
|       |       |   |   __init__.py
|       |       |   |
|       |       |   \---__pycache__
|       |       |           ciphers.cpython-314.pyc
|       |       |           ciphers_pure.cpython-314.pyc
|       |       |           keys.cpython-314.pyc
|       |       |           primitives.cpython-314.pyc
|       |       |           stream.cpython-314.pyc
|       |       |           __init__.cpython-314.pyc
|       |       |
|       |       +---data
|       |       |       device_templates.json
|       |       |       network_seed.xml
|       |       |       __init__.py
|       |       |
|       |       +---models
|       |       |       base.py
|       |       |       lab.py
|       |       |       network.py
|       |       |       schema.py
|       |       |       services.py
|       |       |       __init__.py
|       |       |
|       |       +---xml
|       |       |   |   nodes.py
|       |       |   |   writer.py
|       |       |   |   __init__.py
|       |       |   |
|       |       |   \---__pycache__
|       |       |           nodes.cpython-314.pyc
|       |       |           writer.cpython-314.pyc
|       |       |           __init__.cpython-314.pyc
|       |       |
|       |       \---__pycache__
|       |               errors.cpython-314.pyc
|       |               resources.cpython-314.pyc
|       |               __init__.cpython-314.pyc
|       |
|       +---tests
|       |   |   test_audit.py
|       |   |   test_ciphers.py
|       |   |   test_cli.py
|       |   |   test_corpus_acceptance.py
|       |   |   test_coverage_gaps.py
|       |   |   test_export_diff.py
|       |   |   test_framing_and_keys.py
|       |   |   test_fuzz.py
|       |   |   test_install_module.py
|       |   |   test_ios_audit.py
|       |   |   test_lab_api.py
|       |   |   test_layout.py
|       |   |   test_legacy.py
|       |   |   test_models.py
|       |   |   test_power.py
|       |   |   test_pt9.py
|       |   |   test_reproducible_build.py
|       |   |   test_resources.py
|       |   |   test_rust_backend.py
|       |   |   test_stream.py
|       |   |   test_xml_lossless.py
|       |   |
|       |   \---fixtures
|       |       |   README.md
|       |       |
|       |       \---unpacked
|       |           +---activity
|       |           |       sample_activity.container.json
|       |           |       sample_activity.xml
|       |           |       topology.dot
|       |           |       topology.json
|       |           |
|       |           \---lab
|       |               |   sample_lab.container.json
|       |               |   sample_lab.xml
|       |               |   topology.dot
|       |               |   topology.json
|       |               |
|       |               \---configs
|       |                       R1.cfg
|       |                       R2.cfg
|       |                       SW1.cfg
|       |
|       +---tools
|       |   |   activity.py
|       |   |   activity_skeleton.xml
|       |   |   audit_ios_commands.py
|       |   |   audit_links.py
|       |   |   bench_crypto_backends.py
|       |   |   build_configured_lab.py
|       |   |   build_large_topology.py
|       |   |   build_wired_lab.py
|       |   |   check_layout.py
|       |   |   check_readability.py
|       |   |   device_shapes.json
|       |   |   device_templates.json
|       |   |   finalise_lab.py
|       |   |   gen_cast_tables.py
|       |   |   harvest_library.py
|       |   |   harvest_merge.py
|       |   |   lab_api.py
|       |   |   legacy_probe.py
|       |   |   make_scored_lab.py
|       |   |   network_seed.xml
|       |   |   phase1_inventory.py
|       |   |   pt_accept.py
|       |   |   pt_runtime_verify.py
|       |   |   repack_layout.py
|       |   |   schema_catalogue.py
|       |   |   scoring.py
|       |   |   verify_in_packet_tracer.sh
|       |   |
|       |   \---__pycache__
|       |           activity.cpython-314.pyc
|       |           lab_api.cpython-314.pyc
|       |           scoring.cpython-314.pyc
|       |
|       +---typings
|       |       pkt_core_native.pyi
|       |
|       \---__pycache__
|               pt9.cpython-314.pyc
|
\---IPV6_PROPIEDAD_HORIZONTAL
    |   escenario.json
    |   README.md
    |   requirements.txt
    |
    +---configuraciones
    |       dhcpv6_stateful.txt
    |       dhcpv6_stateless.txt
    |       router_ipv6.txt
    |       servidor_dns.txt
    |       switch_vlan.txt
    |
    +---instrucciones
    |       hito_01.html
    |       hito_02.html
    |       hito_03.html
    |       hito_04.html
    |       hito_05.html
    |       hito_06.html
    |       hito_07.html
    |       hito_08.html
    |       hito_09.html
    |       hito_10.html
    |
    +---plantillas
    |       pc_clean_donor.xml
    |       r1_clean_donor.xml
    |       referencia_ipv6_nodos.json
    |       srv_clean_donor.xml
    |       sw1_clean_donor.xml
    |
    +---pruebas
    |   |   test_ipv6.py
    |   |   test_json.py
    |   |   test_scoring.py
    |   |   test_topologia.py
    |   |
    |   +---evidencias
    |   |       auditoria_comandos_ios.json
    |   |       auditoria_comandos_ios.md
    |   |       reporte_pruebas_automatizadas.txt
    |   |
    |   \---__pycache__
    |           test_ipv6.cpython-314.pyc
    |           test_json.cpython-314.pyc
    |           test_scoring.cpython-314.pyc
    |           test_topologia.cpython-314.pyc
    |
    +---salida
    |       Grupo_IPV6_Diagnostico_Hito10.pka
    |       Grupo_IPV6_Estudiante.pka
    |       Grupo_IPV6_Maestro.pka
    |       informe_generacion.json
    |       log_generacion.txt
    |       topologia_diagnostico_hito10.pkt
    |       topologia_inicial.pkt
    |       topologia_resuelta.pkt
    |
    \---scripts
        |   compat_windows.py
        |   generar_pka.py
        |   generar_topologia.py
        |   preparar_spec.py
        |   scoring_ipv6.py
        |   validar_ipv6.py
        |   validar_pka.py
        |   verificar_pt_windows.py
        |
        \---__pycache__
                compat_windows.cpython-314.pyc
                generar_pka.cpython-314.pyc
                generar_topologia.cpython-314.pyc
                preparar_spec.cpython-314.pyc
                scoring_ipv6.cpython-314.pyc
                validar_ipv6.cpython-314.pyc
                validar_pka.cpython-314.pyc
                verificar_pt_windows.cpython-314.pyc

```

