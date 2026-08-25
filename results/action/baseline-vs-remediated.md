# Action baseline vs Action remediated

> 비교 키: asset type + 정규화한 이름 + crypto properties. 실행마다 바뀌는 bom-ref UUID는 제외했다.

- Components: 49 → 44
- Dependencies: 24 → 23
- Removed signatures: 4
- Added signatures: 0

| Semantic signature | Components | Occurrences |
|---|---:|---:|
| algorithm | AES-128-CBC-PKCS5 | block-cipher | 1 → 0 (-1) | 1 → 0 (-1) |
| algorithm | AES-128-GCM | ae | 1 → 1 (+0) | 1 → 2 (+1) |
| algorithm | AES-CBC | block-cipher | 1 → 0 (-1) | 1 → 0 (-1) |
| algorithm | AES-GCM | ae | 1 → 1 (+0) | 1 → 2 (+1) |
| algorithm | MD5 | hash | 3 → 0 (-3) | 3 → 0 (-3) |
| algorithm | SHA-256 | hash | 3 → 3 (+0) | 10 → 12 (+2) |
| related-crypto-material | iv | 1 → 0 (-1) | 1 → 0 (-1) |
| related-crypto-material | iv | 1 → 2 (+1) | 1 → 2 (+1) |
