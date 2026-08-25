# Sonar Plugin current vs CBOMkit-action current

> 비교 키: asset type + 정규화한 이름 + crypto properties. 실행마다 바뀌는 bom-ref UUID는 제외했다.

- Components: 38 → 49
- Dependencies: 23 → 24
- Removed signatures: 0
- Added signatures: 5

| Semantic signature | Components | Occurrences |
|---|---:|---:|
| algorithm | AES-128-GCM | ae | 1 → 1 (+0) | 2 → 1 (-1) |
| algorithm | AES-128-GCM | ae | 0 → 1 (+1) | 0 → 1 (+1) |
| algorithm | EC-secp256r1 | pke | 1 → 2 (+1) | 3 → 3 (+0) |
| algorithm | ECDH | key-agree | 0 → 1 (+1) | 0 → 1 (+1) |
| algorithm | ECDH | key-agree | 0 → 1 (+1) | 0 → 1 (+1) |
| algorithm | ECDH | key-agree | 1 → 1 (+0) | 3 → 1 (-2) |
| algorithm | MD5 | hash | 1 → 3 (+2) | 3 → 3 (+0) |
| algorithm | RSA-2048 | pke | 1 → 2 (+1) | 3 → 2 (-1) |
| algorithm | RSA-2048 | pke | 0 → 1 (+1) | 0 → 1 (+1) |
| algorithm | RSA-OAEP | pke | 1 → 1 (+0) | 2 → 1 (-1) |
| algorithm | RSA-OAEP | pke | 0 → 1 (+1) | 0 → 1 (+1) |
| algorithm | SHA-256 | hash | 1 → 3 (+2) | 10 → 10 (+0) |
