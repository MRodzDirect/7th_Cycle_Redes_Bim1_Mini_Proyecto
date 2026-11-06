# Implementación de la solución 1: generador automático de archivos `.pka` con Python

La solución 1 se puede adaptar a tu proyecto de direccionamiento dinámico IPv6. Mi propuesta es utilizar el repositorio `packet-tracer-pkt-format` como motor de generación y desarrollar un pequeño programa adicional para construir nuestra actividad.

No necesitamos programar Packet Tracer desde cero. Aprovecharemos el generador existente y ampliaremos las partes que necesita nuestro proyecto.

Hay una precisión importante: el generador ya puede producir archivos `.pka`, pero su evaluación automática actual no interpreta todos los parámetros IPv6 que necesitamos. Por eso, tendremos que desarrollar una adaptación del evaluador antes de considerar terminada la actividad.

![img](https://www.google.com/s2/favicons?domain=https://github.com&sz=32)

GitHub+2

## 1. ¿Qué necesitamos para implementar esta solución?

Voy a separar los requisitos en cuatro grupos.

### A. Software necesario

![Python logo Icons, Logos, Symbols – Free Download PNG, SVG](https://images.openai.com/static-rsc-4/DmsB8FS-GP7uphH6D36okAKArZlBuv18j7laB7MGQztxtnElBP3iuvRtFFsgJN3_CMjTR795lNP5nkz0C0O5HRM_6vUhOfMDScUzQErc9yfIrgdVyj38VLAdNtbsn3vWhJAUhRcvYx9LUssqXM5zJvcGr4rSiP0dNojMqKdTlnc?purpose=inline)

Checking Favorites status

Python 3.10 o superior

Lenguaje principal para generar los archivos.

[Descargar Python](https://www.python.org/downloads/?utm_source=chatgpt.com)

Obligatorio

![Anakin.ai - 10x Your Productivity with AI](https://images.openai.com/static-rsc-4/Si2y7ezRjaY6Do1dHDKkpXuqW5koVvaCx7qGxMj3nFsCdtMchtJmEJgVaHrMoo7A_224NFlsWoOGsm7gwx0RiDENIE31vKT2paingEeG86qUw1bvNlPV12HTxEI5P0pfbUyR41MVvXxFkYsiGbX5pb8piec95SSWAbKR3d_NVRo?purpose=inline)

Checking Favorites status

Git

Descargar el repositorio del generador.

[Descargar Git](https://git-scm.com/downloads?utm_source=chatgpt.com)

Obligatorio

![Cisco Packet Tracer: Simulator Jaringan Wajib Buat Anak IT - Joker Laptop Aplikasi](https://images.openai.com/static-rsc-4/NZO5632nTC79Hk3M8oKi0HXoc7XwEhw38CsBxEPYZ1mjg7GPUTWHxA7YcLeqBbLwp1smyXyiilJyfs0JcMu06AQxPOoOMbJlrlYWv68j_OGLMJuK9y-uKIe1c2sY2xMUb2JwX1-w-bQt5GxqpYV7PV5rBZtOogwKv-fFj-AqfaY?purpose=inline)

Checking Favorites status

Cisco Packet Tracer

Abrir, ejecutar y comprobar los archivos generados.

[Cisco Networking Academy](https://www.netacad.com/?utm_source=chatgpt.com)

Validación

![precis0x (@precisox) on X](https://images.openai.com/static-rsc-4/6UGebdew9WxthPsgkQBRJ_JmTfWW_y7agnczvltWrIQT3Fya6scbDbI6iPx5bLk5AYaAZn6vZ0m2arJ8MWgkkjeh-UTDFj7T_xmY-oHzvDmme3uha0Wp-xi3VPGSmRx9jEKG5QFBxu5oc1sgdei7nH2rGCbyU3I1ifuv0lVXmu0?purpose=inline)

Checking Favorites status

Visual Studio Code

Editar Python, JSON, HTML y archivos de configuración.

[Descargar VS Code](https://code.visualstudio.com/?utm_source=chatgpt.com)

Recomendado

El repositorio indica que necesita Python 3.10 como mínimo y que su dependencia principal de ejecución es Pydantic. La generación puede realizarse sin tener Packet Tracer instalado, pero necesitaremos Packet Tracer para abrir y validar el resultado.

![img](https://www.google.com/s2/favicons?domain=https://github.com&sz=32)

GitHub+1

### B. Hardware necesario

No hace falta ningún equipo de Cisco físico.

Podemos desarrollar todo en tu computadora:

| Recurso                | Necesidad                   |
| ---------------------- | --------------------------- |
| Computadora Windows    | Sí                          |
| Conexión a Internet    | Para descargar herramientas |
| Router físico SKYWORTH | No                          |
| Switch físico          | No                          |
| Repetidores TP-Link    | No                          |
| Cableado de red real   | No                          |

Nuestra infraestructura será completamente virtual.

### C. Versión de Packet Tracer

El repositorio indica que sus archivos generados han sido probados con:

Cisco Packet Tracer 9.0.1.0858.

Mi recomendación es utilizar esa misma versión como referencia para desarrollar y verificar el generador. El formato tiene compatibilidad documentada con otras versiones, pero no debemos asumir que todas sus funciones de actividad se comportarán exactamente igual.

![img](https://www.google.com/s2/favicons?domain=https://github.com&sz=32)

GitHub+1

### D. Repositorio que necesitamos

![Download Free GitHub Logo PNG and SVG Icons](https://images.openai.com/static-rsc-4/8nknb6NuCMNhuQpeaE5AO-_eYwNXh1OHakGI0r_IDIZepaBhi_UZGvBXivBYBguyokple8rmnfaDPDkxmbOu8bYyMnevYNVvD_YSYfKqt3e55ODyi8NKVs5dM4yXbIpjsZmcMAWWWmEIfqDpr_UGeNUijwlN0JOhZbQKaCakRM8?purpose=inline)

Checking Favorites status

packet-tracer-pkt-format

Motor principal

[Abrir repositorio oficial del proyecto](https://github.com/aacanadaa/packet-tracer-pkt-format?utm_source=chatgpt.com)

Este es el proyecto que descargaremos completo. No basta con descargar únicamente el archivo `make_scored_lab.py`, porque depende de otras bibliotecas, plantillas y archivos auxiliares.

Licencia del código: GPL-3.0 o posterior.

![img](https://www.google.com/s2/favicons?domain=https://github.com&sz=32)

GitHub+1

## 2. ¿Qué estructura de archivos se espera?

Esta es una de las partes más importantes.

El generador original tiene una estructura propia que debemos conservar. Encima de ella construiremos la estructura específica de nuestro proyecto IPv6.

Mi recomendación es mantener ambos proyectos separados dentro de una carpeta principal.

### Estructura general propuesta

```
PROYECTO_IPV6/
│
├── GENERADOR/
│   │
│   └── packet-tracer-pkt-format/
│       │
│       ├── pt9.py
│       ├── pyproject.toml
│       ├── README.md
│       ├── LICENSE
│       │
│       ├── src/
│       │   └── pkt_core/
│       │
│       └── tools/
│           ├── make_scored_lab.py
│           ├── build_configured_lab.py
│           ├── lab_api.py
│           ├── activity.py
│           ├── scoring.py
│           │
│           ├── network_seed.xml
│           ├── device_templates.json
│           ├── device_shapes.json
│           ├── activity_skeleton.xml
│           │
│           └── harvest_library.py
│
├── IPV6_PROPIEDAD_HORIZONTAL/
│   │
│   ├── escenario.json
│   │
│   ├── configuraciones/
│   │
│   ├── instrucciones/
│   │
│   ├── plantillas/
│   │
│   ├── scripts/
│   │
│   ├── pruebas/
│   │
│   └── salida/
│
└── README_PROYECTO.md
```

Esta estructura es una propuesta de organización nuestra, no una exigencia del repositorio.

### ¿Para qué sirve cada archivo del generador?

| Archivo                   | Función                                             |
| ------------------------- | --------------------------------------------------- |
| `make_scored_lab.py`      | Programa principal que genera el `.pka`.            |
| `build_configured_lab.py` | Construye redes con configuraciones.                |
| `lab_api.py`              | Permite agregar dispositivos, módulos y conexiones. |
| `activity.py`             | Construye la estructura de Activity Wizard.         |
| `scoring.py`              | Construye los árboles de evaluación.                |
| `pt9.py`                  | Codifica y decodifica archivos de Packet Tracer.    |
| `network_seed.xml`        | Plantilla base de la red.                           |
| `device_templates.json`   | Plantillas de dispositivos y módulos.               |
| `device_shapes.json`      | Estructuras de elementos evaluables.                |
| `activity_skeleton.xml`   | Estructura inicial de una actividad `.pka`.         |

Estos archivos son utilizados directamente por el generador original.

![img](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com&sz=32)

GitHub+2

### ¿Qué archivos serán nuestros?

Ahora viene la parte personalizada.

Dentro de `IPV6_PROPIEDAD_HORIZONTAL` vamos a crear los siguientes archivos:

| Archivo                    | Contenido                                           |
| -------------------------- | --------------------------------------------------- |
| `escenario.json`           | Inventario y conexiones de la topología.            |
| `config_router.txt`        | Configuración IPv6 del router.                      |
| `config_switch.txt`        | VLAN y puertos del switch.                          |
| `dhcpv6_stateless.txt`     | Configuración para DHCPv6 sin estado.               |
| `dhcpv6_stateful.txt`      | Configuración para DHCPv6 con estado.               |
| `scoring_ipv6.py`          | Adaptación del evaluador para IPv6.                 |
| `hito_01.html`             | Instrucciones del primer hito.                      |
| ...                        | ...                                                 |
| `hito_10.html`             | Instrucciones del décimo hito.                      |
| `actividad_referencia.pka` | Plantilla de evaluación creada con Activity Wizard. |
| `generar_pka.py`           | Nuestro programa principal.                         |

Una precisión: el generador original espera las configuraciones IOS dentro del campo `config` del JSON, como una lista de comandos. Los archivos `.txt` separados serían para organizar nuestro trabajo; `generar_pka.py` los leerá y los incorporará al JSON antes de invocar el generador.

## 3. ¿Cómo se adapta al documento que analizamos?

Aquí es donde conectamos el generador con el diseño de la propiedad horizontal.

He tomado como referencia las secciones 5 a 10 de tu documento:

- Arquitectura lógica IPv6.
- Construcción de la topología en Packet Tracer.
- Organización del Activity Wizard.
- Plan de pruebas.
- Organización de los archivos de entrega.
- Decisiones técnicas finales.
  1. Escenario real corregido.md

La adaptación sería la siguiente.

### A. Sección 5: arquitectura lógica IPv6

Esta será la información que introduciremos en `escenario.json` y en los archivos de configuración.

| Departamento | VLAN | Prefijo IPv6            | Mecanismo        |
| ------------ | ---- | ----------------------- | ---------------- |
| D1           | 10   | `2001:DB8:ACAD:10::/64` | SLAAC            |
| D2           | 20   | `2001:DB8:ACAD:20::/64` | DHCPv6 Stateless |
| D3           | 30   | `2001:DB8:ACAD:30::/64` | DHCPv6 Stateful  |
| D4           | 40   | `2001:DB8:ACAD:40::/64` | DHCPv6 Stateless |
| D5           | 50   | `2001:DB8:ACAD:50::/64` | SLAAC            |

Cada interfaz de gateway tendrá su dirección `::1`, tal como propone el documento.

El generador podrá introducir configuraciones IOS en el router mediante el campo `config`. El repositorio documenta que escribe el contenido de `RUNNINGCONFIG` línea por línea y Packet Tracer aplica esa configuración al abrir el archivo.

![img](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com&sz=32)

GitHub+1

### B. Sección 6: construcción de la topología

La topología que generaremos será la misma propuesta en el documento.

## Topología automatizada

Cloud-PT — Proveedor de Internet

R1 — Cisco 2911

Enrutamiento IPv6 · RA · DHCPv6

Trunk 802.1Q

SW1 — Cisco 2960

VLAN 10 · 20 · 30 · 40 · 50

D1

VLAN 10

SLAAC

AP + PC

D2

VLAN 20

Stateless

AP + PC

D3

VLAN 30

Stateful

AP + PC

D4

VLAN 40

Stateless

AP + PC

D5

VLAN 50

SLAAC

AP + PC

El inventario será:

| Dispositivo     | Cantidad |
| --------------- | -------- |
| Cloud-PT        | 1        |
| Router 2911     | 1        |
| Switch 2960     | 1        |
| Access Point-PT | 5        |
| PC-PT           | 5        |
| Server-PT       | 1        |

Hay dos cuestiones que debemos comprobar antes de generar los archivos definitivos:

1. Que las plantillas disponibles contengan los modelos exactos de AP-PT, Cloud-PT y Server-PT que utilizaremos.
2. Que Packet Tracer abra correctamente la configuración de los puntos de acceso y sus conexiones.

El repositorio indica que la creación de dispositivos, cableado Ethernet y configuración IOS está verificada, mientras que algunas funciones inalámbricas aparecen documentadas pero todavía no verificadas.

![img](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com&sz=32)

GitHub+1

Para evitar que una limitación inalámbrica afecte al laboratorio, utilizaremos los cinco PC como clientes de prueba de sus VLAN. Los AP pueden conservarse como representación de los TP-Link; si queremos demostrar conectividad inalámbrica real, necesitaremos una prueba adicional con clientes inalámbricos.

### C. Sección 7: los diez hitos de Activity Wizard

Esta será la correspondencia entre tus diez hitos y la automatización.

| Hito del documento | Lo que programaremos                          |
| ------------------ | --------------------------------------------- |
| 1. Reconocimiento  | Crear los dispositivos y sus nombres.         |
| 2. Segmentación    | Generar instrucciones y evaluación de VLAN.   |
| 3. Troncal         | Configurar el trunk entre R1 y SW1.           |
| 4. Protocolo IPv6  | Configurar enrutamiento y gateways.           |
| 5. SLAAC D1        | Configurar RA para VLAN 10.                   |
| 6. Stateless D2    | Configurar DHCPv6 y el indicador O.           |
| 7. Stateful D3     | Configurar DHCPv6 y el indicador M.           |
| 8. D4 y D5         | Configurar Stateless y SLAAC.                 |
| 9. Conectividad    | Incorporar las verificaciones IPv6 y DNS.     |
| 10. Diagnóstico    | Introducir una falla y evaluar su corrección. |

Las instrucciones serán páginas HTML que el generador integrará en el `.pka`. Su documentación admite una cadena HTML o una lista de páginas de instrucciones.

![img](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com&sz=32)

GitHub+1

Una limitación importante respecto a los hitos: la versión original de `make_scored_lab.py` crea una red inicial con la topología pero sin configuraciones y otra red con la solución completa. No crea automáticamente diez estados intermedios de la misma actividad.

Por tanto, podemos generar una actividad con los diez hitos explicados en sus páginas y una evaluación final. Para conseguir que cada hito se desbloquee, se califique y habilite el siguiente, tendremos que ampliar la programación de Activity Wizard o generar actividades separadas por etapas. No debemos confundir ambas modalidades.

![img](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com&sz=32)

GitHub+1

### D. Sección 8: pruebas de funcionamiento

Aquí desarrollaremos un archivo adicional:

```
validar_ipv6.py
```

Este programa nos ayudará a comprobar los resultados esperados después de abrir la actividad.

| Comprobación | Resultado esperado                              |
| ------------ | ----------------------------------------------- |
| PC1          | Dirección SLAAC de VLAN 10                      |
| PC2          | Dirección SLAAC y DNS mediante DHCPv6           |
| PC3          | Dirección asignada por DHCPv6 Stateful          |
| PC4          | Dirección SLAAC y DNS mediante DHCPv6           |
| PC5          | Dirección SLAAC de VLAN 50                      |
| Gateway      | Comunicación IPv6 en cada segmento              |
| VLAN         | Separación correcta de departamentos            |
| DNS          | Resolución desde los segmentos correspondientes |
| Diagnóstico  | Corrección de la falla introducida              |

El programa Python puede inspeccionar configuraciones y resultados exportados, pero las pruebas reales de asignación dinámica, conectividad y comportamiento RA deben ejecutarse dentro de Packet Tracer.

### E. Secciones 9 y 10: archivos finales

Mantendremos los entregables del documento:

```
GRUPO_IPV6/
│
├── Grupo_IPV6.pka
│   └── Actividad para el estudiante.
│
├── Grupo_Editable.pka
│   └── Copia maestra editable.
│
├── Guion_Practica.pdf
│
├── Guion_Practica.docx
│
└── Evidencias/
    ├── topologia.png
    ├── ipv6_slaac.png
    ├── dhcpv6_stateless.png
    ├── dhcpv6_stateful.png
    └── conectividad.png
```

La diferencia es que nuestros archivos `.pka` se generarán mediante programación y no tendrán que construirse manualmente desde cero en Activity Wizard.

## 4. Una adaptación imprescindible: el evaluador IPv6

Hay un inconveniente que debemos resolver antes de generar la actividad definitiva.

El código actual de `scoring.py` extrae principalmente:

- Dirección IPv4.
- Máscara de subred.
- Estado de puerto.
- Gateway de los dispositivos finales.
- Modelo del dispositivo.

No extrae directamente todos los valores de IPv6, DHCPv6 y RA que necesitamos.

![img](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com&sz=32)

GitHub+1

Por eso, nuestro proyecto necesitará esta modificación:

scoring_ipv6.py — Evaluador personalizado

| Elemento     | Qué tendrá que comprobar                 |
| ------------ | ---------------------------------------- |
| VLAN         | Identificador y puertos asociados        |
| Trunk        | VLAN permitidas y modo troncal           |
| IPv6         | Prefijos y direcciones de las interfaces |
| SLAAC        | Anuncio del prefijo y autoconfiguración  |
| Stateless    | Pool DHCPv6 e indicador O                |
| Stateful     | Pool DHCPv6 e indicador M                |
| Conectividad | Comunicación con gateways y clientes     |

Estrategia recomendada

Crear una actividad de referencia en Activity Wizard con routers, switches y clientes que contenga los elementos IPv6 que queremos evaluar.

Después utilizaremos sus nodos de evaluación completos como plantillas para generar los criterios de nuestra actividad.

Esto es necesario porque Packet Tracer comprueba la estructura interna de los nodos y no acepta necesariamente nodos de evaluación XML inventados.

![img](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com&sz=32)

GitHub+1

También conservaremos las cinco preguntas de reflexión de tu documento. Estas se incorporarán a las instrucciones y al guion, pero no asumiremos que Activity Wizard puede calificarlas automáticamente como respuestas de texto.

1. Escenario real corregido.md

## 5. ¿Cómo empezamos a instalarlo y ponerlo en funcionamiento?

Te propongo hacerlo en Windows, utilizando PowerShell.

### Paso 1. Comprobar Python y Git

Abre PowerShell y ejecuta:

PowerShell

```
py --version
git --version
```

Python debe ser 3.10 o superior.

### Paso 2. Crear la carpeta del proyecto

PowerShell

```
mkdir C:\PROYECTO_IPV6
cd C:\PROYECTO_IPV6

mkdir GENERADOR
mkdir IPV6_PROPIEDAD_HORIZONTAL
```

### Paso 3. Descargar el generador

PowerShell

```
cd C:\PROYECTO_IPV6\GENERADOR

git clone https://github.com/aacanadaa/packet-tracer-pkt-format.git
```

Esto descargará las herramientas y plantillas originales.

### Paso 4. Preparar el entorno de Python

PowerShell

```
cd packet-tracer-pkt-format

py -m venv .venv

.\.venv\Scripts\Activate.ps1

py -m pip install --upgrade pip

py -m pip install -e .
```

El repositorio también documenta la instalación mediante `pip install packet-tracer-pkt-format`. Nosotros utilizaremos la instalación editable desde el repositorio para trabajar con sus archivos auxiliares y desarrollar nuestras modificaciones.

![img](https://www.google.com/s2/favicons?domain=https://github.com&sz=32)

GitHub+1

### Paso 5. Comprobar el generador

Ejecuta:

PowerShell

```
py tools/make_scored_lab.py --help
```

Deberían aparecer las opciones de generación, incluyendo:

- `--out`
- `--spec`
- `--password`
- `--instructions`
- `--prune-seed`
- `--feedback`

Estas son las opciones documentadas por el programa.

![img](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com&sz=32)

GitHub

Una adaptación necesaria para Windows: el script original utiliza rutas temporales `/tmp/_pt9_initial.pkt` y `/tmp/_pt9_answer.pkt`. Para evitar problemas en Windows, recomiendo modificar esas rutas para utilizar `tempfile.gettempdir()` de Python antes de ejecutar el generador.

![img](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com&sz=32)

GitHub

### Paso 6. Crear nuestro primer escenario JSON

Un ejemplo reducido de la estructura que espera el generador sería:

JSON

```
{
  "devices": [
    {
      "model": "2911",
      "name": "R1",
      "x": 300,
      "y": 200,
      "config": [
        "hostname R1",
        "ipv6 unicast-routing",
        "interface GigabitEthernet0/0",
        "no shutdown"
      ]
    },
    {
      "model": "2960-24TT",
      "name": "SW1",
      "x": 500,
      "y": 350
    }
  ],
  "links": [
    {
      "a": "R1",
      "aport": "GigabitEthernet0/0",
      "b": "SW1",
      "bport": "GigabitEthernet0/1",
      "kind": "copper"
    }
  ],
  "instructions": [
    "<h2>Hito 1</h2><p>Reconocer la topología.</p>",
    "<h2>Hito 2</h2><p>Configurar las VLAN.</p>"
  ]
}
```

Este ejemplo solamente ilustra el formato de entrada; todavía no representa nuestra topología terminada ni una configuración IPv6 validada.

El generador permite especificar dispositivos, coordenadas, configuraciones, conexiones e instrucciones HTML.

![img](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com&sz=32)

GitHub+2

## 6. Plan de implementación definitivo

No recomiendo intentar generar los diez hitos de una sola vez. Es mejor desarrollar el proyecto mediante pruebas sucesivas.

1. Fase 1. Preparar el generador

   Instalar Python, descargar el repositorio y comprobar que `make_scored_lab.py` funciona.

   Primera meta

2. Fase 2. Crear una prueba pequeña

   Generar un `.pka` con un router, un switch y dos PC. Abrirlo y comprobar Activity Wizard.

3. Fase 3. Incorporar IPv6

   Implementar SLAAC, DHCPv6 Stateless y DHCPv6 Stateful. Comprobar cada mecanismo antes de construir la actividad completa.

4. Fase 4. Construir la propiedad horizontal

   Generar los cinco departamentos, las VLAN y todos los dispositivos del escenario.

5. Fase 5. Adaptar la evaluación

   Incorporar las reglas de puntuación IPv6 y probar Check Results.

6. Fase 6. Generar Activity Wizard

   Incorporar los diez hitos, instrucciones y retroalimentación.

7. Fase 7. Entregar

   Generar los dos archivos PKA, preparar el guion y documentar las pruebas.

## 7. ¿Qué resultado esperamos obtener?

# Producto final

generar_pka.py

Programa que construye la actividad.

escenario.json

Descripción de toda la propiedad horizontal.

Grupo_IPV6.pka

Actividad generada para los estudiantes.

Grupo_Editable.pka

Copia maestra editable.

Guion_Practica.pdf y DOCX

Documentación y evidencias del proyecto.

## Mi recomendación definitiva

La solución 1 es apropiada y se acopla al documento que analizamos. No cambiaría la arquitectura de cinco departamentos ni los mecanismos de direccionamiento.

Pero hay una decisión de desarrollo que considero fundamental:

Primero debemos conseguir que Python genere correctamente un `.pka` sencillo y que Packet Tracer lo abra. Después adaptamos el evaluador IPv6 y finalmente generamos la práctica completa.

Así no desarrollamos diez hitos sobre un generador que todavía no hemos validado.

Hay una última información que necesitamos comprobar en tu computadora: tu versión instalada de Cisco Packet Tracer, porque debemos utilizarla para verificar la compatibilidad de las plantillas, las configuraciones y los criterios de evaluación antes de construir el archivo definitivo.

If you want, I can:

- Continuar con el paso 7 para configurar VLANs y trunk
- Describir cómo modificar el evaluador para incluir IPv6 y DHCPv6
- Iniciar ejemplos concretos de JSON para un escenario IPv6 completo