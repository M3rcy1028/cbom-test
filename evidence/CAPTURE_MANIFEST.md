# CBOM Lab 실행 증거 Manifest

## 캡처 분류와 진실성 원칙

- `실행 증거 요약 카드`: 원본 JSON·로그를 스크립트가 읽어 핵심 수치를 PNG로 렌더링한 그림이다. 실제 terminal 창처럼 가장하지 않으며 그림 상단에 원본 경로를 표시한다.
- `실제 UI 캡처`: 로컬에서 실행 중인 공식 CBOMkit release 2.2.0 full/coeus build 또는 current main build를 Playwright로 직접 캡처한 그림이다.
- 일반 캡처 재현은 `scripts/capture_evidence.py`, IBM Zurich quantum-safe 캡처는 `scripts/capture_quantum_safe_viewer.py`를 사용한다. 브라우저 검증 JSON은 `results/ui/browser-validation.json`과 `results/quantum-safe/viewer-validation.json`에 있다.
- 기존 시험 중 만들어진 `full-*`, `ui-*` 이미지는 최종 증거가 아니므로 `.gitignore`로 제외한다.

## 그림별 해석

### 01. 고정 실행 환경 — `01-environment.png`

1. 무엇을 실행했는가: 각 도구의 build/runtime 버전과 listen endpoint를 확인했다.
2. 어디를 볼 것인가: Runtime, 실행 서비스, Docker 경계, 고정 revision 행이다.
3. 결론: Docker 외 경로에서 Sonar, PostgreSQL, CBOMkit, OPA를 실제로 기동했고 upstream commit을 고정했다.
4. 결론낼 수 없는 것: Docker daemon/Compose가 정상 실행됐다는 증거는 아니다. socket 권한이 없어 registry·OCI 경로로 대체했다.

### 02. Schema validation — `02-schema-validation.png`

1. 무엇을 실행했는가: IBM CBOM 1.0, CycloneDX 1.6/1.7 공식 JSON Schema에 정상·음성 문서 15개를 검증했다.
2. 어디를 볼 것인가: 각 case의 expected/actual 값과 PASS badge다.
3. 결론: Sonar, Action, Theia directory/image 산출물이 대응 schema를 통과했고 음성 fixture는 의도대로 실패했다.
4. 결론낼 수 없는 것: Schema 통과만으로 bom-ref나 dependency 참조가 존재한다고 보장하지 않는다.

### 03. Semantic validation — `03-semantic-validation.png`

1. 무엇을 실행했는가: component bom-ref와 dependency root/target의 중복·누락·dangling 참조를 검사했다.
2. 어디를 볼 것인가: 정상 14/14, Theia enriched 누락, schema-positive 음성 fixture 행이다.
3. 결론: 핵심 원본 산출물은 참조 무결성이 있고, enrichment 결과에는 bom-ref 없는 component가 1개 있다.
4. 결론낼 수 없는 것: 알고리즘 속성의 암호학적 정확성까지 검증하는 도구는 아니다.

### 04. Fixture smoke — `04-fixture-smoke.png`

1. 무엇을 실행했는가: Java·Python·Go baseline과 보완본의 실제 암호 호출을 build/run했다.
2. 어디를 볼 것인가: 언어별 `fixture-ok`와 output length다.
3. 결론: scanner 입력 소스가 compile/runtime 오류 없이 해당 API 경로를 호출한다.
4. 결론낼 수 없는 것: 고정 키·IV, MD5, CBC가 안전하다는 의미가 아니다. 전부 탐지 실험용이다.

### 05–06. Sonar scan·issues — `sonar-01-dashboard.png`, `sonar-02-issues.png`

1. 무엇을 실행했는가: SonarQube 26.1에 source-built crypto plugin을 설치하고 Java·Python·Go를 분석했다.
2. 어디를 볼 것인가: 38 components/23 dependencies, 32 issues, MD5 issue, 22/22 evidence recall 행이다.
3. 결론: 세 언어의 고수준 fixture family를 모두 찾고 파일·line evidence를 생성했다.
4. 결론낼 수 없는 것: 음성 source corpus가 없으므로 precision은 수치화하지 않았다. 또한 22/22 family recall이 모든 property의 완전성을 뜻하지 않는다.

### 07. Theia directory — `07-theia-directory.png`

1. 무엇을 실행했는가: lab directory를 certificate, secret, OpenSSL config plugin 등으로 스캔했다.
2. 어디를 볼 것인가: 25 components, certificate/private key/TLS 탐지와 public key 누락 행이다.
3. 결론: filesystem 자산 7단위 중 6단위를 찾았다.
4. 결론낼 수 없는 것: Theia는 source scanner가 아니므로 Java/Python/Go 호출 탐지 성능을 이 결과로 평가할 수 없다.

### 08. Theia image·OCI — `08-theia-image.png`

1. 무엇을 실행했는가: registry의 `alpine:3.22`, single-platform OCI layout, multi-arch OCI index를 스캔했다.
2. 어디를 볼 것인가: registry 2,858 components, OCI amd64 2,856, multi-arch 오류/exit 0 행이다.
3. 결론: daemon 없는 image 입력 두 종류는 성공했고 multi-arch index의 오류 전달 결함을 재현했다.
4. 결론낼 수 없는 것: 이 결과는 Docker daemon 입력 자체를 검증하지 않는다.

### 09. Enrichment — `09-enrichment-diff.png`

1. 무엇을 실행했는가: Sonar CBOM을 Theia의 filesystem·java.security 결과로 enrichment했다.
2. 어디를 볼 것인가: 38→64, added 26, modified 0, 오탐·bom-ref 누락 행이다.
3. 결론: 기존 source 자산을 유지하면서 filesystem 자산을 합칠 수 있다.
4. 결론낼 수 없는 것: java.security restriction 속성이 정상 반영됐다고 볼 수 없다. 실제로 구현 결함 때문에 수정 0개였다.

### 10. Action local — `10-action-local.png`

1. 무엇을 실행했는가: source-built CBOMkit-action 엔진을 GitHub 환경 변수로 Java·Python·Go에 실행했다.
2. 어디를 볼 것인가: 통합 49 components, 모듈별 수치, build/CWD 전제 행이다.
3. 결론: 모듈·통합 CBOM 및 `CBOM.zip` 등가 artifact를 로컬에서 생성했다.
4. 결론낼 수 없는 것: 이 그림은 GitHub-hosted runner 성공 증거가 아니다. 원격 workflow 결과는 push 뒤 별도로 기록한다.

### 11. CBOMkit API·DB — `11-cbomkit-api-db.png`

1. 무엇을 실행했는가: Quarkus backend와 PostgreSQL을 기동해 네 CBOM을 저장·재조회하고 정책 API를 호출했다.
2. 어디를 볼 것인가: 저장 row, enriched HTTP 500/NPE, 전체 JSON INFO log 행이다.
3. 결론: CRUD와 DB 영속화는 성공했고 schema-valid 혼합 CBOM에서 정책 상호운용성 결함이 있다.
4. 결론낼 수 없는 것: 모든 유효 CycloneDX 문서가 compliance API에서 처리된다고 일반화할 수 없다.

### 12–13. Compliance·OPA — `12-compliance-matrix.png`, `13-opa-boundaries.png`

1. 무엇을 실행했는가: 동일 5자산 fixture를 built-in, coeus local, OPA CLI/HTTP/backend에서 평가했다.
2. 어디를 볼 것인가: built-in 5/5, OPA 3/5, ECDH spelling, ML-KEM 상충, missing policy fail-open 행이다.
3. 결론: policy engine은 교체 가능하지만 규칙·enum·오류 계약이 같지 않다.
4. 결론낼 수 없는 것: 5개 fixture 결과를 전체 cryptographic policy 정확도로 확대할 수 없다.

### 14. Current main frontend 회귀 — `14-current-main-blank-screen.png`

1. 무엇을 실행했는가: 2026-08-25 current main frontend를 build해 브라우저로 열었다.
2. 어디를 볼 것인가: 빈 body 자체와 `browser-validation.json`의 `Vue.use` page error다.
3. 결론: build 성공과 runtime 성공은 다르며 current dependency 조합은 blank screen을 만든다.
4. 결론낼 수 없는 것: 서버/backend 장애가 원인이라는 증거가 아니다. 동일 backend에서 release 2.2.0 UI는 정상이다.

### 15–17. CBOMkit full 실제 화면 — `15-cbomkit-home.png`, `16-cbomkit-sonar-results.png`, `17-cbomkit-asset-detail.png`

1. 무엇을 실행했는가: release 2.2.0 full profile을 backend·DB와 연결하고 Sonar CBOM을 업로드했다.
2. 어디를 볼 것인가: 최근 scan 목록, 59 assets 통계, Backend Compliance, ECDH detail·relationship·bom-ref다.
3. 결론: 저장 CBOM 탐색, 업로드, occurrence 전개, 통계, 상세, dependency, backend policy UI가 실제 동작한다.
4. 결론낼 수 없는 것: UI의 59는 CBOM component 38과 같은 counting unit이 아니다.

### 18–19. coeus 실제 화면 — `18-coeus-home.png`, `19-coeus-sonar-results.png`

1. 무엇을 실행했는가: release 2.2.0 coeus profile에서 backend 없이 Sonar CBOM을 업로드했다.
2. 어디를 볼 것인가: viewer-only home, `Basic Local Compliance Service`, illustrative disclaimer다.
3. 결론: coeus는 별도 제품 다운로드가 아니라 CBOMkit frontend의 local viewer profile이다.
4. 결론낼 수 없는 것: coeus는 CBOM 생성·DB 저장·server policy 기능을 제공하지 않는다.

### 20. 변경 전후 — `20-remediation-diff.png`

1. 무엇을 실행했는가: MD5→SHA-256, AES-CBC→GCM, TLS 1.2→1.3 변경 뒤 Action·Theia를 재실행했다.
2. 어디를 볼 것인가: Action 49→44, 제거 component, 대체 occurrence, TLSv1.2 1→0 행이다.
3. 결론: 설정·코드 변경이 CBOM topology/evidence에 예상 방향으로 반영됐다.
4. 결론낼 수 없는 것: 별도 ML-KEM fixture는 있지만 baseline RSA를 PQC로 교체한 것은 아니므로 전체 양자 안전 전환 완료를 주장할 수 없다.

### 21. coeus policy fixture — `21-coeus-policy-results.png`

1. 무엇을 실행했는가: RSA, ECDH, AES, unknown, ML-KEM 5자산 fixture를 coeus local service로 평가했다.
2. 어디를 볼 것인가: 5개 자산의 네 compliance category와 우상단 `Invalid CBOM` 경고다.
3. 결론: local engine은 ML-KEM을 safe로 표시하고, 동시에 frontend validator가 `serialNumber` 누락을 경고하면서도 결과를 렌더링한다.
4. 결론낼 수 없는 것: 경고가 있는 fixture를 완전한 CycloneDX production 문서로 간주할 수 없다. Schema validator와 frontend validation contract 차이를 별도로 다뤄야 한다.

### 22. GitHub-hosted Action — `22-github-action-success.png`

1. 무엇을 실행했는가: `main`의 최초 commit `066b89e`에서 workflow_dispatch로 `cbomkit-action@v2.1.1`을 실행했다.
2. 어디를 볼 것인가: Status Success, 48초 duration, artifact 1개, CBOM digest다.
3. 결론: GitHub-hosted runner에서 build·Java/Python scan·artifact upload가 모두 성공했고 공식 `CBOM.zip`을 회수했다.
4. 결론낼 수 없는 것: workflow success가 모든 module의 non-empty CBOM을 뜻하지 않는다. 실제 artifact에는 build하지 않은 보완 Java module의 0-component CBOM이 포함됐다.

### 23. IBM Zurich Viewer quantum-safe — `23-ibm-zurich-quantum-safe.png`

1. 무엇을 실행했는가: Go 표준 `crypto/mlkem`으로 ML-KEM-768 round-trip을 실행하고 CBOMkit-action으로 만든 1-component CBOM을 IBM Zurich Viewer에 업로드했다.
2. 어디를 볼 것인가: `Compliant`, 녹색 `Quantum Safe` 100%, `ML-KEM-768`, `KEM`, `main.go:13`이다.
3. 결론: 실제 source 호출→scanner evidence→CycloneDX CBOM→공개 Viewer local policy의 end-to-end 경로가 동작한다.
4. 결론낼 수 없는 것: standalone KEM 성공이 기존 애플리케이션의 RSA 교체, hybrid protocol, 인증·상호운용성·성능 검증 완료를 뜻하지 않는다.
