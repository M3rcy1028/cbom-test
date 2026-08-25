# Quantum-safe execution results

`quantum-safe-go/`의 실제 ML-KEM-768 코드를 CBOMkit-action으로 스캔하고 정책·Viewer에서 검증한 결과다.

| 경로 | 내용 |
|---|---|
| `runtime.log` | ML-KEM 캡슐화·역캡슐화 shared key 일치 실행 결과 |
| `test.log` | `go test` round-trip 자동 검증 결과 |
| `action/cbom.json` | IBM Zurich Viewer에 넣을 CycloneDX 1.6 CBOM |
| `action/scan.log` | CBOMkit-action이 ML-KEM-768을 탐지한 원본 log |
| `action/github-output.txt` | Action-compatible artifact pattern 출력 |
| `compliance.json` | Built-in policy의 level 3 `Quantum Safe` 판정 |
| `viewer-validation.json` | IBM Zurich Viewer에서 ML-KEM·Quantum Safe 표시를 확인한 결과 |
| `SHA256SUMS.txt` | CBOM·semantic·compliance 핵심 산출물 hash |

Viewer 입력은 `action/cbom.json` 하나다. 이 CBOM은 schema와 semantic validation을 모두 통과했고, `ML-KEM-768`, `primitive=kem`, parameter set `768`, NIST OID와 `main.go:13` evidence를 포함한다.
