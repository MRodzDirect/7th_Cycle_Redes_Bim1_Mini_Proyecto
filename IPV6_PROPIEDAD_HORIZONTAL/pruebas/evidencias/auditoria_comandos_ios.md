# IOS command attestation audit

Corpus: `GENERADOR\packet-tracer-pkt-format\corpus\samples` — 2 files decoded, 0 failed, 61 attested signatures (1.68s).

* `IPV6_PROPIEDAD_HORIZONTAL\salida\topologia_resuelta.pkt` — 2 devices with a RUNNINGCONFIG, 216 config lines, 45 distinct signatures (sha256 `f32984dca0d7…`)
* `IPV6_PROPIEDAD_HORIZONTAL\salida\Grupo_IPV6_Estudiante.pka` — 6 devices with a RUNNINGCONFIG, 236 config lines, 45 distinct signatures (sha256 `8593d675e3da…`)

## Summary

| metric | value |
| --- | ---: |
| distinct signatures | 45 |
| attested signatures | 17 |
| unattested signatures | 28 |
| unattested standard | 25 |
| unattested suspicious | 3 |
| unattested emissions | 226 |
| suspicious emissions | 14 |

## Suspicious UNATTESTED signatures (exit non-zero)

| signature | emitted | devices | reason | example |
| --- | ---: | ---: | --- | --- |
| `global|dns-server <ip6>` | 6 | 2 | unrecognised-command-verb:dns-server | `dns-server 2001:DB8:ACAD:99::10` |
| `global|domain-name propiedadhorizontal.local` | 6 | 2 | unrecognised-command-verb:domain-name | `domain-name propiedadhorizontal.local` |
| `global|address prefix <ip6> lifetime <n> <n>` | 2 | 2 | unrecognised-command-verb:address | `address prefix 2001:DB8:ACAD:30::/64 lifetime 172800 86400` |

## UNATTESTED signatures (first 28)

| signature | emitted | corpus files | category | reason |
| --- | ---: | ---: | --- | --- |
| `interface|description <text>` | 38 | 0 | standard | standard-verb:description |
| `interface|no shutdown` | 28 | 0 | standard | standard-verb:shutdown |
| `interface|spanning-tree portfast` | 20 | 0 | standard | standard-verb:spanning-tree |
| `interface|switchport access vlan <n>` | 20 | 0 | standard | standard-verb:switchport |
| `interface|ipv6 address <ip6>` | 14 | 0 | standard | standard-verb:ipv6 |
| `interface|ipv6 address <ip6> link-local` | 14 | 0 | standard | standard-verb:ipv6 |
| `interface|ipv6 enable` | 14 | 0 | standard | standard-verb:ipv6 |
| `interface|encapsulation dot1q <n>` | 10 | 0 | standard | standard-verb:encapsulation |
| `vlan|name <text>` | 10 | 0 | standard | standard-verb:name |
| `vlan|vlan <n>` | 10 | 0 | standard | standard-verb:vlan |
| `global|dns-server <ip6>` | 6 | 0 | suspicious | unrecognised-command-verb:dns-server |
| `global|domain-name propiedadhorizontal.local` | 6 | 0 | suspicious | unrecognised-command-verb:domain-name |
| `global|no service password-encryption` | 4 | 0 | standard | standard-verb:service |
| `interface|ipv6 nd other-config-flag` | 4 | 0 | standard | standard-verb:ipv6 |
| `global|address prefix <ip6> lifetime <n> <n>` | 2 | 0 | suspicious | unrecognised-command-verb:address |
| `global|ip cef` | 2 | 0 | standard | standard-verb:ip |
| `global|ip name-server <ip6>` | 2 | 0 | standard | standard-verb:ip |
| `global|ipv6 dhcp pool dept2_stateless` | 2 | 0 | standard | standard-verb:ipv6 |
| `global|ipv6 dhcp pool dept3_stateful` | 2 | 0 | standard | standard-verb:ipv6 |
| `global|ipv6 dhcp pool dept4_stateless` | 2 | 0 | standard | standard-verb:ipv6 |
| `global|ipv6 unicast-routing` | 2 | 0 | standard | standard-verb:ipv6 |
| `global|no ip domain-lookup` | 2 | 0 | standard | standard-verb:ip |
| `interface|ipv6 dhcp server dept2_stateless` | 2 | 0 | standard | standard-verb:ipv6 |
| `interface|ipv6 dhcp server dept3_stateful` | 2 | 0 | standard | standard-verb:ipv6 |
| `interface|ipv6 dhcp server dept4_stateless` | 2 | 0 | standard | standard-verb:ipv6 |
| `interface|ipv6 nd managed-config-flag` | 2 | 0 | standard | standard-verb:ipv6 |
| `interface|switchport mode trunk` | 2 | 0 | standard | standard-verb:switchport |
| `interface|switchport trunk allowed vlan <text>` | 2 | 0 | standard | standard-verb:switchport |

