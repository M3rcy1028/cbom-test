# Compliance Golden Matrix

| Asset | Ground truth | Built-in | External OPA | Built-in exact | OPA exact |
|---|---|---|---|---:|---:|
| RSA-2048 | quantum-vulnerable | quantum-vulnerable | quantum-vulnerable | O | O |
| ECDH-P256 | quantum-vulnerable | quantum-vulnerable | not-applicable | O | X |
| AES-128-GCM | not-applicable | not-applicable | not-applicable | O | O |
| Vendor-Algorithm-X | unknown | unknown | unknown | O | O |
| ML-KEM-768 | quantum-safe | quantum-safe | quantum-safe, quantum-vulnerable | O | X |

- Built-in exact matches: 5/5
- External OPA exact matches: 3/5
- OPA conflicting assets: 1
