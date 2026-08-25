# Theia TLS baseline vs Theia TLS remediated

> 비교 키: asset type + 정규화한 이름 + crypto properties. 실행마다 바뀌는 bom-ref UUID는 제외했다.

- Components: 11 → 6
- Dependencies: 2 → 1
- Removed signatures: 1
- Added signatures: 0

| Semantic signature | Components | Occurrences |
|---|---:|---:|
| algorithm | AES128 GCM | block-cipher | 2 → 1 (-1) | 2 → 1 (-1) |
| algorithm | AES256 GCM | block-cipher | 2 → 1 (-1) | 2 → 1 (-1) |
| algorithm | SHA256 | hash | 2 → 1 (-1) | 2 → 1 (-1) |
| algorithm | SHA384 | hash | 2 → 1 (-1) | 2 → 1 (-1) |
| protocol | TLSv1.2 | 1 → 0 (-1) | 1 → 0 (-1) |
