# Generador Automático de Laboratorio IPv6 en Propiedad Horizontal (`.pka` / `.pkt`)

Este proyecto implementa un generador automático completo y reproducible de actividades de **Cisco Packet Tracer** (`.pka` y `.pkt`) en Python para el laboratorio académico:

> **"Implementación de direccionamiento dinámico en IPv6 para la gestión de redes en una propiedad horizontal"**

Construido sobre el motor de codificación binaria y el árbol de evaluación del repositorio `packet-tracer-pkt-format` (`v0.4.1`), sin modificar ningún archivo original del repositorio clonado en `GENERADOR/packet-tracer-pkt-format`.

---

## 1. Informe de Diagnóstico Técnico (Fase 1)

Durante la auditoría profunda del repositorio base `GENERADOR/packet-tracer-pkt-format`, se identificaron los siguientes hallazgos técnicos clave:

1. **Formato binario `.pkt` / `.pka` (Packet Tracer 7.x / 8.x / 9.x):**
   - Los archivos `.pkt` y `.pka` son contenedores XML comprimidos mediante `zlib` con cabecera `qCompress` de Qt (4 bytes big-endian indicando la longitud descomprimida), cifrados con **Twofish-128 en modo EAX** (llave de 16 bytes `[137]*16`, IV `[16]*16`) y ofuscados mediante permutación XOR reversa.
   - Un archivo `.pkt` tiene como raíz `<PACKETTRACER5>`, mientras que un archivo `.pka` (Activity Wizard) tiene como raíz `<PACKETTRACER5_ACTIVITY>` e incorpora:
     - `<PACKETTRACER5>` (red activa donde trabaja el estudiante).
     - `<ACTIVITY>` con `<INITIALSETUP>` (red inicial para *Reset Activity*), `<ANSWERS>` (red resuelta de referencia), `<COMPARISONS>` (árbol de evaluación con `<NODE checkType="1">` en hojas calificables), `<INSTRUCTIONS>` (páginas HTML paginadas) y `<SCORING>` / `< WIZARD >`.
2. **Compatibilidad Windows PowerShell vs. Ubuntu WSL (`scripts/compat_windows.py`):**
   - El script original `pt9.py` del repositorio base invoca `ctypes.CDLL("libgcrypt.so.20")` al importarse (librería compartida exclusiva de Linux), mientras que `src/pkt_core/crypto/ciphers_pure.py` provee una implementación en Python puro de Twofish-128 cuyo cifrado byte a byte tarda ~18–25 segundos por archivo.
   - Nuestra capa puente `scripts/compat_windows.py` intercepta la ausencia de `libgcrypt.so.20` en Windows e inyecta una implementación de **Twofish-128 optimizada con tablas MDS y cajas S precalculadas en Python puro**, logrando cifrar/descifrar cada contenedor `.pkt`/`.pka` en **~0.8 segundos en Windows PowerShell** sin instalar paquetes C externos ni requerir WSL.
   - Si se ejecuta en **Ubuntu WSL** con `libgcrypt20` instalado, utiliza automáticamente el motor nativo de C.
3. **Soporte de Dispositivos y Nodos de Evaluación IPv6 (`device_shapes.json`):**
   - El catálogo `device_shapes.json` (extraído del binario de Packet Tracer) contiene **364 modelos de dispositivos** y el árbol completo de evaluación (`pts` Assessment Tree).
   - Se verificaron e integraron en `plantillas/referencia_ipv6_nodos.json` los nodos reales de evaluación para **Router 2911**, **Switch 2960-24TT**, **AccessPoint-PT**, **PC-PT** y **Server-PT**, incluyendo:
     - `Running Config`: `ipv6 unicast-routing`, `ip name-server 2001:DB8:ACAD:99::10`, pools `ipv6 dhcp pool` (`DEPT2_STATELESS`, `DEPT3_STATEFUL`, `DEPT4_STATELESS`), subinterfaces `GigabitEthernet0/0.10..50` (`encapsulation dot1Q`, `ipv6 nd other-config-flag`, `ipv6 nd managed-config-flag`, `ipv6 dhcp server`).
     - `Ports`: `IPv6 Enabled`, `IPv6 Link Local`, `IPv6 Addresses`, `IPv6 Default Gateway`, `IPv6 Auto Config`, `Use DHCPv6`, `Dynamic Address`, `Dot1Q`, ` Native VLAN ID`, `Access VLAN`, `Power` y `SSID`.
     - `DNS Server`: `Service Enabled` y `Resource Records` (`AAAA` con `IPv6 Address` y `Length`).
4. **Atestación Léxica de Comandos IOS (`tools/audit_ios_commands.py`):**
   - Se auditaron los comandos IOS de `R1` y `SW1` contra las cadenas del binario de Packet Tracer (`strings_ios_commands.txt`).
   - La auditoría detectó que en Cisco IOS el comando global de servidor DNS es `ip name-server 2001:DB8:ACAD:99::10` (acepta direcciones IPv4 e IPv6, mientras que `ipv6 name-server` no existe como comando global en IOS 15.1 de PT), lo cual fue corregido en `configuraciones/router_ipv6.txt` y `scripts/scoring_ipv6.py`.

---

## 2. Arquitectura y Estructura del Proyecto

```text
IPV6_PROPIEDAD_HORIZONTAL/
├── escenario.json                        # Especificación maestra declarativa
├── requirements.txt                      # Dependencias (100% librería estándar en Windows/Linux)
├── README.md                             # Esta guía técnica y de uso
├── plantillas/
│   └── referencia_ipv6_nodos.json        # Catálogo verificado de IDs y rutas del árbol de evaluación
├── configuraciones/
│   ├── router_ipv6.txt                   # Configuración IOS de R1 (Router-on-a-Stick IPv6)
│   ├── switch_vlan.txt                   # Configuración IOS de SW1 (VLANs 10,20,30,40,50 + Trunk/Access)
│   ├── dhcpv6_stateless.txt              # Referencia de pools DHCPv6 Stateless (Deptos 2 y 4)
│   ├── dhcpv6_stateful.txt               # Referencia de pool DHCPv6 Stateful (Depto 3)
│   └── servidor_dns.txt                  # Especificación de 9 registros AAAA en SRV-DNS
├── instrucciones/
│   ├── hito_01.html .. hito_10.html      # 10 páginas HTML con diseño pedagógico y 5 preguntas en Hito 10
├── scripts/
│   ├── compat_windows.py                 # Capa puente multiplataforma (PowerShell + Ubuntu WSL)
│   ├── preparar_spec.py                  # Validador de escenario.json y recursos asociados
│   ├── generar_topologia.py              # Constructor XML de las 3 variantes de topología (.pkt)
│   ├── scoring_ipv6.py                   # Motor de evaluación automática (194 checks en 8 dispositivos)
│   ├── generar_pka.py                    # Orquestador principal de 12 pasos (.pkt + .pka + reportes)
│   ├── validar_pka.py                    # Validador estructural y criptográfico EAX/zlib/XML
│   └── validar_ipv6.py                   # Auditor de coherencia IPv6 y de fallas del Hito 10
├── salida/
│   ├── topologia_inicial.pkt             # Red base física conectada sin direccionamiento IPv6 lógico
│   ├── topologia_resuelta.pkt            # Red 100% configurada y funcional (Golden Master)
│   ├── topologia_diagnostico_hito10.pkt  # Red con 3 fallas deliberadas para el Hito 10
│   ├── Grupo_IPV6_Estudiante.pka         # Actividad interactiva para el estudiante (inicia en 0%)
│   ├── Grupo_IPV6_Maestro.pka            # Actividad pre-resuelta para el docente (inicia en 100%)
│   ├── Grupo_IPV6_Diagnostico_Hito10.pka # Actividad de troubleshooting para el Hito 10
│   ├── informe_generacion.json           # Reporte estructurado con hashes SHA-256 y desglose de puntos
│   └── log_generacion.txt                # Bitácora detallada de ejecución
└── pruebas/
    ├── test_json.py                      # Pruebas unitarias de escenario.json
    ├── test_topologia.py                 # Pruebas unitarias de topologías (.pkt), puertos y enlaces
    ├── test_ipv6.py                      # Pruebas unitarias de prefijos, flags ND, DHCPv6 y DNS AAAA
    ├── test_scoring.py                   # Pruebas unitarias de calificación (.pka) y paridad de árbol
    └── evidencias/
        ├── auditoria_comandos_ios.json   # Evidencia de atestación léxica IOS
        ├── auditoria_comandos_ios.md     # Reporte en Markdown de comandos IOS
        └── reporte_pruebas_automatizadas.txt
```

---

## 3. Plan de Direccionamiento IPv6 y Topología (14 Dispositivos, 13 Enlaces)

| Segmento / Departamento | VLAN | Subred IPv6 (`/64`) | Gateway (`R1`) | Link-Local `R1` | Método Dinámico | Flags RA (`M` / `O`) | Dispositivos Conectados (`SW1`) |
| :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- |
| **Departamento 1** | `10` | `2001:DB8:ACAD:10::/64` | `2001:DB8:ACAD:10::1` | `FE80::1` | **SLAAC** | `M=0`, `O=0` | `PC-D1` (`Fa0/1`), `AP-D1` (`Fa0/6`, SSID `Depto1_IPv6`) |
| **Departamento 2** | `20` | `2001:DB8:ACAD:20::/64` | `2001:DB8:ACAD:20::1` | `FE80::1` | **DHCPv6 Stateless** (`DEPT2_STATELESS`) | `M=0`, `O=1` | `PC-D2` (`Fa0/2`), `AP-D2` (`Fa0/7`, SSID `Depto2_IPv6`) |
| **Departamento 3** | `30` | `2001:DB8:ACAD:30::/64` | `2001:DB8:ACAD:30::1` | `FE80::1` | **DHCPv6 Stateful** (`DEPT3_STATEFUL`) | `M=1`, `O=0` | `PC-D3` (`Fa0/3`), `AP-D3` (`Fa0/8`, SSID `Depto3_IPv6`) |
| **Departamento 4** | `40` | `2001:DB8:ACAD:40::/64` | `2001:DB8:ACAD:40::1` | `FE80::1` | **DHCPv6 Stateless** (`DEPT4_STATELESS`) | `M=0`, `O=1` | `PC-D4` (`Fa0/4`), `AP-D4` (`Fa0/9`, SSID `Depto4_IPv6`) |
| **Departamento 5** | `50` | `2001:DB8:ACAD:50::/64` | `2001:DB8:ACAD:50::1` | `FE80::1` | **SLAAC** | `M=0`, `O=0` | `PC-D5` (`Fa0/5`), `AP-D5` (`Fa0/10`, SSID `Depto5_IPv6`) |
| **Servicios Comunes (DNS)** | N/A (`Gi0/1`) | `2001:DB8:ACAD:99::/64` | `2001:DB8:ACAD:99::1` | `FE80::1` | **Estático** (`SRV-DNS`: `::10/64`) | `M=0`, `O=0` | `SRV-DNS` (`FastEthernet0` → `R1 Gi0/1`) |
| **Enlace WAN ISP** | N/A (`Gi0/2`) | `2001:DB8:ACAD:FF::/64` | `2001:DB8:ACAD:FF::1` | `FE80::1` | **Estático** | `M=0`, `O=0` | `Cloud-PT` (`Ethernet6` → `R1 Gi0/2`) |

---

## 4. Guía de los 10 Hitos Pedagógicos y Evaluación Automática (194 Puntos)

Las instrucciones embebidas en el `.pka` están divididas en 10 páginas HTML navegables (`instrucciones/hito_01.html` a `hito_10.html`):

1. **Hito 1:** Reconocimiento de la Arquitectura Física y Planificación IPv6.
2. **Hito 2:** Segmentación L2 en `SW1`: Creación de VLANs 10–50, Puertos de Acceso y Enlace Troncal (`Gi0/1`).
3. **Hito 3:** Activación del Plano de Control IPv6 en `R1` (`ipv6 unicast-routing`) e Interfaz `Gi0/1` hacia `SRV-DNS`.
4. **Hito 4:** Implementación de **SLAAC** en los Departamentos 1 (VLAN 10) y 5 (VLAN 50).
5. **Hito 5:** Implementación de **DHCPv6 Stateless** (SLAAC + DNS) en los Departamentos 2 (VLAN 20) y 4 (VLAN 40).
6. **Hito 6:** Implementación de **DHCPv6 Stateful** en el Departamento 3 (VLAN 30).
7. **Hito 7:** Configuración del Servidor `SRV-DNS` (`2001:DB8:ACAD:99::10/64`) y sus 9 Registros `AAAA` (`propiedadhorizontal.local`).
8. **Hito 8:** Puesta en Marcha de los 5 Access Points (`AP-D1`..`AP-D5`) y Clientes `PC-D1`..`PC-D5` en Modo Automático.
9. **Hito 9:** Verificación Integral de Conectividad ICMPv6, Tablas de Vecinos NDP y Concesiones DHCPv6.
10. **Hito 10:** Escenario de Diagnóstico y Resolución de Problemas (*Troubleshooting* de 3 fallas inyectadas + **5 preguntas de reflexión técnica** con guía de respuestas).

### Distribución de Puntos en el Árbol de Evaluación (`scoring_ipv6.py`)

| Dispositivo | Ítems Evaluados (`checkType="1"`) | Qué se califica automáticamente |
| :--- | :---: | :--- |
| **`R1`** | **89** | `ipv6 unicast-routing`, `ip name-server`, pools DHCPv6 (`DEPT2_STATELESS`, `DEPT3_STATEFUL`, `DEPT4_STATELESS`), subinterfaces `Gi0/0.10..50` (VLAN Dot1Q, direcciones IPv6, Link-Local `FE80::1`, flags `other-config-flag` y `managed-config-flag`, vinculación `ipv6 dhcp server`), e interfaces `Gi0/0`, `Gi0/1`, `Gi0/2`. |
| **`SW1`** | **43** | Definición de VLANs `10, 20, 30, 40, 50` en la VLAN table, modo trunk Dot1Q en `Gi0/1`, y asignación de `Access VLAN` en `Fa0/1..Fa0/10` en `Running Config` y `Ports`. |
| **`SRV-DNS`** | **23** | `IPv6 Enabled`, dirección estática `2001:DB8:ACAD:99::10/64`, Link-Local `FE80::99:10`, Default Gateway `FE80::1`, servicio DNS activo y los **9 registros AAAA** (`dns`, `r1`, `depto1..5`, `gateway-d2`, `gateway-d3`). |
| **`PC-D1` .. `PC-D5`** | **39** | `IPv6 Enabled`, `IPv6 Auto Config` en todos los departamentos, `Use DHCPv6` en `PC-D2..D4`, y `Dynamic Address` en `PC-D3` (Stateful). |
| **Total** | **194** | **100% de cobertura sobre los objetivos del laboratorio.** |

---

## 5. Instrucciones de Ejecución (Windows PowerShell y Ubuntu WSL)

### Opción A: Ejecución Nativa en Windows PowerShell (Recomendada)

No requiere instalar librerías externas ni cambiar a Linux. Desde la raíz del workspace:

```powershell
# 1. Generar los 3 archivos .pkt, los 3 archivos .pka e informes en salida/
python IPV6_PROPIEDAD_HORIZONTAL/scripts/generar_pka.py --spec IPV6_PROPIEDAD_HORIZONTAL/escenario.json

# 2. Validar un archivo .pka específico (estructura XML, cifrado EAX y coherencia IPv6)
python IPV6_PROPIEDAD_HORIZONTAL/scripts/validar_pka.py IPV6_PROPIEDAD_HORIZONTAL/salida/Grupo_IPV6_Estudiante.pka
python IPV6_PROPIEDAD_HORIZONTAL/scripts/validar_ipv6.py --spec IPV6_PROPIEDAD_HORIZONTAL/escenario.json

# 3. Ejecutar la suite completa de 12 pruebas automatizadas
python -m unittest discover -s IPV6_PROPIEDAD_HORIZONTAL/pruebas -p "test_*.py" -v
```

### Opción B: Ejecución en Ubuntu WSL (22.04 o 24.04)

Los mismos comandos funcionan de manera idéntica en Ubuntu WSL:

```bash
python3 IPV6_PROPIEDAD_HORIZONTAL/scripts/generar_pka.py --spec IPV6_PROPIEDAD_HORIZONTAL/escenario.json
python3 -m unittest discover -s IPV6_PROPIEDAD_HORIZONTAL/pruebas -p "test_*.py" -v
```

---

## 6. Verificación en Cisco Packet Tracer (GUI)

Para inspeccionar visualmente las actividades generadas en **Cisco Packet Tracer 8.2+**:

1. Abra `IPV6_PROPIEDAD_HORIZONTAL/salida/Grupo_IPV6_Estudiante.pka`:
   - Verá la ventana paginada con los **10 Hitos** de instrucciones.
   - Al abrir **Check Results → Assessment Items**, el puntaje inicial es **0% (0/194)** con todos los ítems desglosados por dispositivo (`R1`, `SW1`, `SRV-DNS`, `PC-D1..PC-D5`).
2. Abra `IPV6_PROPIEDAD_HORIZONTAL/salida/Grupo_IPV6_Maestro.pka`:
   - Contiene la red completamente configurada como red activa: el indicador marca **100% (194/194)** desde el inicio.
3. Abra `IPV6_PROPIEDAD_HORIZONTAL/salida/Grupo_IPV6_Diagnostico_Hito10.pka`:
   - Contiene la red casi completa (~96% de avance) con las **3 fallas deliberadas del Hito 10** listas para ser diagnosticadas y corregidas hasta alcanzar el 100%.
