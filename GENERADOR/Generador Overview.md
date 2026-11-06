# Overview



`packet-tracer-pkt-format` is an offline, byte-exact codec and authoring toolkit for Cisco Packet Tracer `.pkt` and `.pka` files. It supports container families spanning Cisco Packet Tracer versions 4.1 through 9.0.1 [README.md:3-8]. The toolkit enables reading, inspecting, diffing, exporting, and programmatically authoring complex network topologies, IOS configurations, and scored lab activities entirely offline without requiring an installation of Cisco Packet Tracer [README.md:3-8, pyproject.toml:5-10].

Sources: `README.md:3-8`, `pyproject.toml:5-10`

------

## High-Level Architecture

The library is organized around a deterministic transformation pipeline. Raw encrypted containers are decoded via `pkt_core.codec.container` into byte streams, parsed into tolerant XML via `pkt_core.xml`, mapped to type-safe Python structures via `pkt_core.models`, and authored or modified through `pkt_core.builder` [src/pkt_core/**init**.py:22-44, README.md:117-157].

```

```

Sources: `src/pkt_core/__init__.py:22-44`, `README.md:117-157`

The codebase separates the entry-point CLI (`pkt_core.cli.main`), the core codec and cryptography packages (`pkt_core.codec`, `pkt_core.crypto`), schema models (`pkt_core.models`), and the mutation/authoring framework (`pkt_core.builder`) [src/pkt_core/**init**.py:22-44].

```

```

Sources: `src/pkt_core/__init__.py:22-44`, `pyproject.toml:66-67`

------

## Repository Layout

The project layout divides core library source code, test suites, verification scripts, and documentation resources:

| Directory / Path        | Responsibility                                               |
| ----------------------- | ------------------------------------------------------------ |
| `src/pkt_core/`         | Main package containing the codec, cryptography engine, models, and builder API [src/pkt_core/**init**.py:22-44] |
| `src/pkt_core/codec/`   | Container decoding, format detection, and zlib/`qCompress` framing [src/pkt_core/**init**.py:31-32] |
| `src/pkt_core/crypto/`  | Twofish, Serpent, CAST-256 ciphers, EAX AEAD mode, key schedules, and stream obfuscation [README.md:148-151] |
| `src/pkt_core/models/`  | Pydantic typed representations (`Lab`, `Device`, `Link`, `RunningConfig`) [README.md:151] |
| `src/pkt_core/builder/` | Authoring API, coordinate mapping, and device/module insertion [src/pkt_core/**init**.py:44] |
| `tests/`                | Unit tests, round-trip tests, and coverage suites [pyproject.toml:119] |
| `tools/`                | Standalone authoring utilities, validators, and audit scripts [README.md:88] |

Sources: `src/pkt_core/__init__.py:22-44`, `pyproject.toml:119`, `README.md:88`

------

## Child Pages

For detailed specifications and architectural deep-dives, refer to the child pages:

- **[Getting Started](https://deepwiki.com/aacanadaa/packet-tracer-pkt-format/1.1-getting-started)** — Installation instructions (`pip`, `pyproject.toml` metadata), invocation of the standalone `pt9.py` script, basic decode/unpack/pack CLI commands, and documentation usage guides [pyproject.toml:5-46, README.md:32-54].
- **[Project History and Roadmap](https://deepwiki.com/aacanadaa/packet-tracer-pkt-format/1.2-project-history-and-roadmap)** — `CHANGELOG` history, details on the `pkt_core.builder` port, known limitations, and deferred work items [pyproject.toml:91-94, pyproject.toml:99-104].

Sources: `pyproject.toml:5-46`, `pyproject.toml:91-104`, `README.md:32-54`