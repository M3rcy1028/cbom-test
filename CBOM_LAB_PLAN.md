# CBOM 전체 도구 통합 실험 계획 및 작업 원장

> 이 파일은 `cbom-lab` 실험의 단일 작업 기준 문서다.  
> 모든 단계 시작 전에 다시 읽고, 실행 직후 상태·명령·결과·차단 사유·증거 경로를 갱신한다.  
> 대화 컨텍스트가 축약되더라도 이 파일과 `results/`, `evidence/`를 읽으면 작업을 이어갈 수 있어야 한다.

## 1. 최종 목표

IBM CBOM 생태계의 모든 주요 도구를 동일한 테스트 프로젝트에 적용하고, 도구별 입력·처리 과정·출력·연계 방식·탐지 차이·한계를 실제 실행 결과와 캡처로 검증한 통합 기능 명세서를 작성한다.

핵심 연구 질문:

> CBOM 생태계의 각 도구는 소스, 빌드, 디렉터리, 컨테이너, CI/CD, 시각화, 저장, 정책 평가 중 어느 계층을 담당하며, 결합했을 때 암호 인벤토리와 양자 안전 전환에 충분한 정보를 제공하는가?

## 2. 대상 도구

| ID | 도구 | 역할 | 공식 저장소 |
|---|---|---|---|
| T0 | IBM CBOM | 초기 CBOM 1.0 스키마·예제 검증 | https://github.com/IBM/CBOM |
| T1 | Sonar Cryptography Plugin / hyperion | 빌드된 소스 분석, evidence 포함 CBOM 생성 | https://github.com/cbomkit/sonar-cryptography |
| T2 | CBOMkit | Git/PURL scan, 저장, API, viewer, compliance | https://github.com/cbomkit/cbomkit |
| T3 | CBOMkit-coeus | 기존 CBOM의 독립 viewer·local compliance | CBOMkit frontend viewer profile |
| T4 | CBOMkit-theia | 디렉터리·컨테이너·인증서·키·설정 탐지 및 enrichment | https://github.com/cbomkit/cbomkit-theia |
| T5 | CBOMkit-action | GitHub Actions에서 모듈별·통합 CBOM 생성 | https://github.com/cbomkit/cbomkit-action |
| T6 | OPA | 외부 Rego compliance 평가 | CBOMkit `opa/quantum_safe.rego` |

## 3. 통합 실험 흐름

```text
공통 cbom-lab 테스트 프로젝트와 ground truth
    ├─ IBM CBOM/CycloneDX Schema 검증
    ├─ Sonar Cryptography Plugin source scan
    ├─ CBOMkit-action CI scan
    ├─ CBOMkit-theia directory scan
    ├─ container build → theia image scan
    ├─ Sonar/Action CBOM → theia enrichment
    └─ 모든 CBOM → CBOMkit/coeus upload
                         ├─ API/DB/viewer 검증
                         ├─ backend/local/OPA 정책 비교
                         └─ 취약 암호 변경 전후 semantic diff
```

## 4. 공통 테스트 fixture

예정 구조:

```text
cbom-lab/
├─ java-app/                    # JCA 기반 암호 사용
├─ python-app/                  # pyca/cryptography 기반 암호 사용
├─ go-app/                      # Go crypto 표준 라이브러리
├─ config/openssl.cnf           # TLS protocol/cipher suite
├─ certs/                       # 테스트 전용 인증서와 키
├─ Dockerfile                   # image scan 대상
├─ .github/workflows/cbom.yml   # CBOMkit-action
├─ ground-truth.md              # 탐지 정답표
├─ results/                     # 원본 JSON·로그
├─ evidence/                    # 실제 실행 캡처
├─ scripts/                     # 검증·비교·캡처 자동화
└─ CBOM_LAB_PLAN.md             # 이 작업 원장
```

의도적으로 포함할 자산:

| ID | 자산 | 기대 primitive/종류 | 실험 목적 |
|---|---|---|---|
| A01 | AES-128-GCM | `ae` | mode·key size·encrypt/decrypt |
| A02 | AES-CBC/PKCS5 | `block-cipher` | 구식 구성과 padding |
| A03 | RSA-2048/OAEP | `pke` | 양자 취약 공개키 암호 |
| A04 | SHA-256 | `hash` | digest 탐지 |
| A05 | MD5 | `hash` | 금지·구식 알고리즘 |
| A06 | PBKDF2 | `kdf` | KDF와 iteration/parameter |
| A07 | ECDSA | `signature` | EC 서명 |
| A08 | ECDH | `key-agree` | OPA `keyagree` 오타 회귀 |
| A09 | ML-KEM 명세 fixture | `kem` | PQC policy 비교 |
| C01 | 유효 X.509 인증서 | `certificate` | certificate parser |
| C02 | 만료 X.509 인증서 | `certificate` | 만료 상태 |
| K01 | 테스트 공개키 | `public-key` | 관련 암호 재료 |
| K02 | 테스트 개인키 | `private-key` | theia secret/key 탐지 |
| P01 | TLS 1.2 설정 | `protocol` | legacy protocol/suite |
| P02 | TLS 1.3 설정 | `protocol` | 현대 protocol/suite |

인증서와 키는 실험 전용으로 생성하며 실제 credential을 사용하지 않는다.

## 5. Ground truth와 평가 방법

도구 실행 전에 `ground-truth.md`에 다음 열을 확정한다.

| 필드 | 설명 |
|---|---|
| ID | 자산 고유 실험 ID |
| 파일·라인 | 의도적으로 넣은 위치 |
| 언어·라이브러리 | JCA, pyca, Go crypto 등 |
| expected asset | 표준화한 알고리즘/자산명 |
| expected properties | primitive, parameter, mode, padding, function |
| expected relationship | algorithm-key/protocol/component 연결 |
| expected policy | vulnerable/safe/NA/unknown |

평가식:

```text
Precision = TP / (TP + FP)
Recall    = TP / (TP + FN)
```

정확도 외에 property completeness, evidence coverage, dependency/reference integrity도 별도 평가한다.

## 6. 실행 단계와 완료 조건

### P0. 환경과 버전 고정

- [ ] Docker daemon 접근 — 클라이언트 설치 확인, 현재 사용자는 `docker` 그룹이 아니어서 socket 접근 거부
- [ ] Compose 실행 — v2.35.1 확인, daemon 권한 때문에 실제 기동 대기
- [x] JDK 21·Maven
- [x] Python·Go 1.25+
- [x] GitHub Actions 실행 가능한 테스트 저장소
- [x] 각 저장소 commit 고정
- [x] 환경 캡처

### P1. 공통 fixture와 ground truth

- [x] Java 앱 build/test
- [x] Python 앱 실행/test
- [x] Go 앱 build/test
- [x] 유효·만료 인증서와 키 생성
- [x] OpenSSL 설정 작성
- [ ] container image build
- [x] ground truth 파일·라인 고정

### P2. IBM 및 CycloneDX 스키마

- [x] IBM CBOM 정상·음성 검증
- [x] CycloneDX 1.6 정상·음성 검증
- [x] fixture를 표현한 최소 수동 CBOM
- [x] schema와 semantic validation 분리 — JSON Schema와 참조 무결성 검사를 별도 실행

### P3. Sonar Cryptography Plugin

- [x] 호환 SonarQube 기동
- [x] source-built plugin 설치·재시작
- [x] Cryptographic Inventory rule 활성화
- [x] Java/Python/Go scan
- [x] `cbom.json` 확보
- [x] Sonar issue와 CBOM evidence 대조
- [x] ground truth 대조 — 지원 범위의 고수준 언어별 자산 family 22/22, 속성 완전성은 별도 평가

### P4. CBOMkit-action

- [x] 테스트 GitHub 저장소와 workflow
- [x] build-before-scan — Java build 선행 후 세 언어 로컬 Action 엔진 실행
- [x] workflow_dispatch 실행 — run `32826680204`, success
- [x] 모듈별 CBOM과 consolidated `cbom.json` — 로컬 Action 엔진 기준 확보
- [x] 로컬 `CBOM.zip` 등가물과 원격 공식 artifact 확보
- [x] Sonar 결과와 비교 — Action은 언어 간 동일 알고리즘을 병합하지 않아 49개, Sonar는 38개

### P5. CBOMkit-theia

- [x] binary/container 빌드 또는 release 설치
- [x] `dir` scan
- [x] registry image scan — `alpine:3.22`, 2,858 components
- [x] OCI 입력 추가 검증 — multi-arch index 실패·exit 0 결함과 amd64 layout 성공을 모두 기록
- [x] certificate/key/secret/opensslconf 결과
- [x] Sonar CBOM enrichment
- [x] enrichment 전후 semantic diff — 기존 38 유지, 26 추가, 0 수정

### P6. CBOMkit·coeus·API·DB

- [x] `production` profile — standalone Quarkus API 2개 기동(내장 정책 8081, OPA 외부 정책 8082)
- [x] health와 CBOM CRUD API
- [x] sonar/action/theia/enriched/policy CBOM 업로드와 public Git scan 저장
- [x] inventory, detail, evidence 화면 — release 2.2.0 full/coeus 실제 화면 캡처
- [x] PostgreSQL 저장·재조회
- [x] `coeus` viewer-only profile 비교 — CBOMkit frontend의 별도 build profile이며 독립 저장소가 아님을 확인

### P7. Compliance

- [x] backend basic
- [x] frontend local — coeus의 `Basic Local Compliance Service` 실제 실행 확인
- [x] external OPA
- [x] RSA, ECDH, AES, unknown, ML-KEM 결과 비교 — 원시 결과 확보, golden matrix 정규화 중
- [x] 빈 finding·없는 policy·충돌 field 경계 테스트
- [x] engine 간 golden matrix — 내장 5/5, OPA 3/5, 상충 1개

### P8. 변경 전후 비교

- [x] MD5 → SHA-256
- [x] AES-CBC → AES-GCM
- [x] TLS 1.2 → TLS 1.3
- [x] RSA → PQC/hybrid 명세 fixture — 실제 구현 교체가 아니라 ML-KEM 정책 평가 fixture로 범위를 명시
- [ ] 모든 생성기 재실행 — Action·Theia 완료, Sonar 재실행은 로컬 관리 credential 유실로 제외
- [x] asset·property·relationship·policy semantic diff — 정규화 JSON·Markdown 완료

### P9. 통합 기능 명세서

- [x] 도구별 20개 항목 명세
- [x] 기능 비교표
- [x] 실제 캡처와 4문장 해석
- [x] 정확도·완전성·상호운용성 평가
- [x] 설치·보안·운영 한계
- [x] 재현 명령·버전·commit·로그

### P10. GitHub 결과 공개

- [x] 최종 README 제목을 `cbom-test`로 정리
- [x] 대용량 도구·upstream clone·개인키·credential 제외 확인
- [x] 결과 JSON·로그·캡처·보고서·재현 스크립트 추적
- [x] `git init`, 기본 branch `main`, 최초 commit `first commit` — `066b89e`
- [x] remote `https://github.com/M3rcy1028/cbom-test.git` 설정
- [x] `git push -u origin main`
- [x] 원격 commit과 workflow 실행 상태 확인 — remote hash 일치, run success, artifact 확보

## 7. 도구별 기능 명세 템플릿

각 도구에 동일한 양식을 적용한다.

1. 목적
2. 담당 분석 계층
3. 입력
4. 출력
5. 설치 조건
6. 실행 명령
7. 내부 처리 흐름
8. 지원 언어·라이브러리·형식
9. 주요 옵션
10. 생성·소비하는 CBOM 요소
11. 다른 도구와 연계 방식
12. 정상 실행 캡처
13. 오류 실행 캡처
14. 결과 해석
15. ground truth 비교
16. 장점
17. 한계
18. 보안 주의사항
19. 적합한 사용 시나리오
20. 사용 버전·commit

## 8. 캡처 원칙

도구마다 최소 설치/버전, 실행, 생성 결과, 결과 해석 화면을 남긴다. 각 캡처 아래에는 다음을 답한다.

1. 무엇을 실행했는가?
2. 어디를 확인해야 하는가?
3. 무엇을 결론낼 수 있는가?
4. 무엇은 결론낼 수 없는가?

PAT, 비밀번호, 실제 개인키 내용, 내부 주소는 마스킹한다. 실행하지 못한 화면은 목업으로 대체하지 않는다.

## 9. 결과 디렉터리 규칙

```text
results/<tool>/<phase>-<input>-<timestamp-or-commit>.*
evidence/<tool>/<figure-number>-<short-description>.png
```

원본 결과는 수정하지 않는다. 정규화·비교 결과는 별도 파일로 생성하고 source path와 hash를 기록한다.

## 10. 현재 상태

마지막 갱신: 2026-08-25 KST

| 단계 | 상태 | 핵심 결과/차단 |
|---|---|---|
| 계획 원장 | 완료 | 원격 증거 검증·push·remote hash 대조까지 기록 |
| 환경 점검 | 부분 완료 | Docker 29.1.3/Compose 2.35.1 확인; `/var/run/docker.sock` 접근 거부 |
| fixture | 부분 완료 | Java·Python·Go 실행 성공, 인증서·키·OpenSSL 설정 완료; image build만 Docker 권한 대기 |
| IBM/CycloneDX | 완료 | IBM 1.0·CycloneDX 1.6/1.7 schema 정상/음성 및 schema-vs-semantic 분리 검증 |
| Sonar | 완료 | standalone SonarQube 26.1, source-built plugin, 3언어 scan, 38-component CBOM·32 issues |
| Action | 완료 | local 3언어 + GitHub run 32826680204 success; artifact·로그 확보, empty module 경계 확인 |
| theia | 완료 | dir·registry image·OCI amd64·enrichment 성공; multi-arch exit-code, secret 오탐, 수정 유실 결함 확인 |
| CBOMkit | 완료 | API·DB·release UI/coeus + public Git scan 48 components; current main blank-screen 회귀 확인 |
| Compliance | 완료 | 내장·frontend local·OPA CLI/HTTP/backend 연동과 golden matrix 완료 |
| 변경 전후 | 범위 완료 | Action 49→44, MD5 3·CBC 2 제거; Theia TLS 1.2 제거와 정규화 diff 완료 |
| 최종 명세 | 완료 | 도구별 20항목, 실제 캡처, 비교·결함·운영 권고·재현 명령 작성 |
| GitHub 공개 | 완료 | 최초 `066b89e`, 원격 증거 `fe54298` push; 원격 Action success와 remote hash 일치 확인 |

## 11. 다음 작업

1. [x] 원격 Action·CBOMkit Git scan 결과를 schema/semantic validator와 보고서에 반영한다.
2. [x] 후속 변경의 민감정보·크기·링크를 재검증한다.
3. [x] 원격 증거 후속 commit을 push하고 최종 remote 상태를 확인한다.

## 12. 실행 로그

### 2026-08-25 — 작업 시작

- `cbom-lab/` 생성.
- 전체 도구 통합 계획과 완료 조건을 본 파일에 고정.
- 아직 외부 시스템 변경, GitHub workflow 실행, container 기동은 수행하지 않음.

### 2026-08-25 — 환경·fixture 고정

- 환경: Docker 29.1.3, Compose 2.35.1, Python 3.11.14, OpenSSL 3.0.18, Maven 3.6.3.
- Docker daemon은 `/var/run/docker.sock` 권한 거부로 접근할 수 없으며 현재 사용자는 `docker` 그룹에 속하지 않음.
- lab 로컬 도구로 Temurin JDK 21.0.12.1, Go 1.27.0/1.26.7/1.25.14를 설치함.
- Java fixture 성공: `java-fixture-ok [32, 32, 256, 32, 16, 32, 71, 32]`.
- Python fixture 성공: `python-fixture-ok [32, 32, 256, 32, 16, 32, 71, 32]`.
- Go fixture 성공: `go-fixture-ok 6`.
- 유효 인증서, 명시적으로 만료된 인증서, 공개키와 테스트 전용 개인키를 생성하고 개인키 권한을 0600으로 설정함.
- `ground-truth.md`에 scanner 실행 전 기대 자산·파일·라인·속성·정책 결과를 고정함.

### 2026-08-25 — CBOMkit-theia 빌드와 디렉터리 스캔

- 고정 commit: `46eb32fa981e10bab88e1996336e10e9e3b18178` (2026-08-18).
- Go 1.27에서는 의존성의 `http2.TrailerPrefix` 오류, Go 1.25에서는 현재 `go.mod`의 `go 1.26.1` 요구로 빌드 실패함.
- Go 1.26.7에서는 `tools/cbomkit-theia` 빌드 성공. 즉 현재 소스 기준 실제 최소 Go 요구는 README의 `1.25+` 설명과 일치하지 않음.
- `dir` scan 성공: `results/theia-dir/cbom.json`, `results/theia-dir/scan.log`.
- 결과는 CycloneDX `specVersion: 1.7`, components 25개, dependencies 4개이며 공식 1.7 JSON schema 검증을 통과함.
- 구성: algorithm 16, certificate 2, protocol 2, related-crypto-material 4, OpenSSL config file 1.
- 인증서 2개와 개인키 2개, TLS 1.2/1.3 및 AES-GCM cipher 설정을 탐지함. 독립 `test-public-key.pem`은 별도 자산으로 탐지하지 않음.
- 입력 CBOM이 없으므로 `javasecurity` plugin은 비활성화되었고, 이는 뒤의 enrichment 실험에서 별도로 검증함.
- CLI 도움말/README의 CycloneDX 1.6 설명과 실제 1.7 출력 사이에도 버전 불일치를 확인함.

### 2026-08-25 — Sonar Cryptography Plugin 빌드

- 고정 commit: `f4c834cb1a15fce4fa8e1cd478b35ca78daf2133` (2026-08-21).
- Temurin JDK 21로 전체 12개 Maven module을 `-DskipTests` 빌드하여 `BUILD SUCCESS` 확인.
- 산출물: `sources/sonar-cryptography/sonar-cryptography-plugin/target/sonar-cryptography-plugin-2.0.0-SNAPSHOT.jar`.
- plugin key `crypto`, 지원 언어 metadata `java,jsp,py,ipynb,go,cs`, 최소 JRE 17을 확인함.
- Docker 기반 공식 Compose 실행 대신 standalone SonarQube 실행을 다음 단계에서 시도함.

### 2026-08-25 — CBOMkit-action 준비

- 고정 commit: `e7a99fb41b2041c400ebd8f942b7f2c88cf2c8ae` (2026-02-05).
- `.github/workflows/cbom.yml`을 작성하여 Java build 후 Java/Python CBOM 생성 및 artifact 업로드 절차를 고정함.
- clone 과정에서 Bouncy Castle JAR 2개가 LFS pointer가 아니라는 경고가 발생했으므로 local Action 재현 전 무결성 확인이 필요함.
- GitHub Actions의 실제 실행은 외부 저장소 생성·push 권한이 필요하므로 현재는 수행하지 않음.

### 2026-08-25 — IBM/CycloneDX schema 재현

- IBM CBOM 고정 commit: `09fbe5781bfa90fba104846c90e0d1cb643a4d97` (2025-02-13).
- `results/ibm/valid-cbom-1.0.json`은 IBM `1.4-cbom-1.0` schema를 통과함.
- `results/ibm/invalid-cbom-1.0.json`의 `block-cipher`는 구 IBM enum의 `blockcipher`와 달라 의도대로 실패함.
- Sonar 생성 CycloneDX 1.6과 Theia 생성 CycloneDX 1.7은 각각 공식 schema를 통과함.
- CycloneDX 1.6의 존재하지 않는 primitive 음성 fixture도 의도대로 실패함.
- 결과: `results/cyclonedx/schema-validation.json`, 실행기: `scripts/validate_schemas.py`.
- 핵심 호환성 차이: IBM 1.0은 `blockcipher/keyagree/relatedCryptoMaterial`, CycloneDX 1.6은 `block-cipher/key-agree/related-crypto-material` 표기를 사용함.

### 2026-08-25 — standalone SonarQube 실제 분석

- Docker 대신 공식 standalone SonarQube `26.1.0.118079`를 H2 평가 DB로 기동하고 서버 상태 `UP`을 확인함.
- source-built `Sonar Crypto Plugin 2.0.0-SNAPSHOT` 설치 및 web/compute engine 초기화 성공.
- Java/Python/Go용 `CBOM Lab` quality profile을 만들고 Inventory 규칙을 활성화함. Java/Python은 별도 MD5 금지 규칙도 활성화함.
- SonarScanner CLI `8.1.0.6389`로 세 언어 소스 3개를 한 프로젝트로 분석함.
- 분석 성공, Sonar issue 32개: Inventory 30개와 MD5 금지 issue 2개.
- `results/sonar/cbom.json`: CycloneDX 1.6, components 38개(algorithm 20, related crypto material 18), dependencies 23개.
- Sonar CBOM의 38 components는 scanner 통계의 탐지 이벤트 32개와 동일한 단위가 아니다. supporting algorithm/material과 통합 evidence 때문에 수가 늘어남.
- ground truth의 고수준 22개 언어별 자산 family는 모두 탐지됐으나 Python RSA-OAEP operation은 RSA-2048 key 탐지에 그쳐 property/operation completeness가 낮음.
- 원본 로그/API: `results/sonar/scan.log`, `plugin-build.log`, `issues.json`, `project.json`, `compute.json`.

### 2026-08-25 — Theia enrichment 및 결함 확인

- Sonar CycloneDX 1.6을 입력으로 lab directory를 enrichment하여 `results/enriched/cbom.json` 생성 및 1.6 schema 검증 성공.
- 기존 38개를 유지하고 filesystem 자산 26개를 추가하여 총 64 components, 27 dependencies가 됨.
- 실제 JDK 21 `java.security`를 `runtime/conf/security/java.security`에 배치해 Java evidence 기반 검증 경로를 실행함.
- 기본 JDK 설정에서 제한에 걸린 자산은 없어 기존 38개 component 변경은 0개였음.
- secret plugin이 JDK 설정 975행 부근의 `jdk.tls.keyLimits=...KeyUpdate...`를 `generic-api-key`로 오탐했으며 생성 component에 `bom-ref`가 없음.
- 별도 `enrichment-fixture`에서 `MD5, RSA keySize < 3072, EC keySize < 384`를 강제했지만 출력 component property 변경은 여전히 0개였음.
- 현재 `javasecurity.UpdateBOM`은 `for _, component := range *bom.Components`로 값 복사본의 주소를 수정하므로 `ibm:cryptography:restriction:*` property가 원본 slice에 반영되지 않는 구현 결함과 관측 결과가 일치함.
- CLI 설명의 “executability/confidence 추가”와 실제 구현은 차이가 있음. 구현은 `jdk.tls.disabledAlgorithms`만 평가하며, 제한된 경우에만 restriction rule/reason/confidence를 추가하려 함.
- 결과: `results/enriched/cbom.json`, `scan.log`, `restricted-cbom.json`, `restricted-scan.log`.

### 2026-08-25 — GitHub 전달 요청 반영

- 사용자 지정 원격: `https://github.com/M3rcy1028/cbom-test.git`.
- 모든 결과 생성이 끝난 뒤 저장소 초기화, `main` branch, `first commit`, upstream push를 수행하도록 P10에 고정함.
- 기존 README가 있으므로 GitHub의 빈 저장소 안내 명령을 그대로 중복 실행하지 않고, 최종 제목을 `cbom-test`로 정리함.
- commit 전 `tools/`, `sources/`, 생성 binary, 테스트 개인키, token/password가 추적되지 않는지 별도 검증함.
- 이 push 권한은 지정 저장소에 이번 CBOM lab 산출물을 게시하는 범위로 한정함.

### 2026-08-25 — CBOMkit API·DB·내장 compliance

- Docker 없이 portable PostgreSQL 14.24를 `127.0.0.1:5433`에, source-built CBOMkit 2.0.0-SNAPSHOT prod profile을 `127.0.0.1:8081`에 기동함.
- 최신 backend는 GitHub Packages의 `cbomkit-lib` 인증이 필요해 초기 build가 401로 실패함. 공개 tag `cbomkit-lib 1.2.0`과 `sonar-cryptography 1.6.1`을 로컬 Maven repository에 build/install한 후 backend build에 성공함.
- `lab-sonar`(38), `lab-theia`(25), `lab-enriched`(64), `lab-policy`(5)를 API로 저장하고 PostgreSQL `cbomreadmodel`의 4개 row와 재조회 JSON을 대조함.
- 내장 `quantum_safe` 정책에서 RSA·ECDH level 1, AES level 4, unknown level 2, ML-KEM-768 level 3을 확인함.
- 없는 내장 policy는 HTTP 200이지만 `error:true`, 빈 CBOM은 HTTP 200·finding 0·global true로 응답함.
- Theia enriched CBOM은 `file` component에 `cryptoProperties`가 없어 `BasicQuantumSafeComplianceService.java:168` NPE로 HTTP 500이 발생함. 스키마 유효 CBOM 전체를 처리하지 못하는 상호운용성 결함임.
- backend이 `StoreCBOMCommand` 전체 JSON을 INFO log에 기록하므로, 실제 운영에서는 소스 evidence·인증서 metadata의 기밀성과 log volume을 검토해야 함.

### 2026-08-25 — OPA 외부 정책 연동

- 공식 OPA 1.15.1의 `check --strict`를 통과하고 CBOMkit `opa/quantum_safe.rego`를 CLI·HTTP `127.0.0.1:8181`로 실행함.
- 정책 fixture 5개에서 finding 6개: RSA 취약, AES NA, unknown, ECDH NA, ML-KEM 취약+안전 동시 판정.
- ECDH는 CycloneDX 1.6 enum `key-agree`와 Rego의 `keyagree`가 달라 대칭키가 아닌 자산으로 분류되어 NA가 됨.
- `ML-KEM-768`은 exact/case-sensitive 이름 whitelist `ml-kem`에 없어 name 규칙은 취약, `nistQuantumSecurityLevel=3`은 안전으로 동시 판정함. backend도 두 finding을 모두 전달하고 global false로 평가함.
- OPA 외부 모드 CBOMkit를 `127.0.0.1:8082`에 별도 기동하여 service 선택이 `Open Policy Agent Compliance Service`로 되는 것을 확인함.
- 없는 OPA policy는 HTTP 200·`findings:[]`·`error:false`·`globalComplianceStatus:true`를 반환함. 정책 부재를 준수로 오인할 fail-open 경계 결함임.
- 원시 증거: `results/compliance/opa-cli-policy-fixture.json`, `opa-http-policy-fixture.json`, `backend-opa-policy-fixture.json`, `backend-opa-missing-policy.json`, `backend-opa-empty.json`.

### 2026-08-25 — Theia registry image·OCI 입력 검증

- Docker daemon 없이 Theia의 registry 입력으로 `alpine:3.22`를 직접 스캔함. `results/theia-image/alpine-3.22-cbom.json`은 CycloneDX 1.7, components 2,858개, dependencies 476개임.
- 구성은 algorithm 1,904, certificate 476, related crypto material 476, file 2임. 동일 CA bundle이 네 경로에서 각각 119개씩 탐지되어 인증서 이름 113종이 경로 간 중복 제거되지 않음을 확인함.
- `crane v0.20.6`으로 만든 multi-arch OCI index는 `unexpected media type application/vnd.oci.image.index.v1+json`로 실패했지만 Theia CLI exit code는 0이고 stdout은 비어 있었음. 자동화에서 빈 CBOM을 성공으로 오인할 수 있는 오류 전달 결함임.
- `linux/amd64` 단일 platform OCI layout은 정상 스캔되어 components 2,856개와 dependencies 476개를 생성함. 원시 산출물과 hash는 `results/theia-image/`에 보존함.

### 2026-08-25 — CBOMkit full UI·coeus·current main 회귀 검증

- 공식 CBOMkit release `2.2.0` commit `9076203bf5...`의 frontend를 full/coeus 두 profile로 source build하고 실제 브라우저에서 실행함.
- full profile은 PostgreSQL/API에 저장된 최근 scan과 backend compliance를 사용하며, coeus는 업로드한 CBOM을 브라우저에서 처리하고 `Basic Local Compliance Service`를 사용함. 따라서 coeus는 별도 저장소·서버가 아니라 CBOMkit frontend의 viewer-only build profile임.
- Sonar CBOM 업로드 시 두 profile 모두 59 cryptographic assets로 표현함. 원본 component 38개와 다른 이유는 UI가 evidence occurrence를 자산 단위로 펼치기 때문임.
- current main frontend는 build에 성공하지만 Vue 3 dependency에서 Vue 2 방식인 `Vue.use`와 `new Vue`를 호출하여 `Cannot read properties of undefined (reading 'use')`로 blank screen이 됨. release 2.2.0의 Vue 2.7 조합에서는 정상 동작함.
- current main `npm audit`: 48건(critical 2, high 24 포함), release 설치 시 audit: 25건(high 10 포함). 실제 배포 전 frontend dependency와 취약점 정리가 필요함.

### 2026-08-25 — CBOMkit-action 로컬 엔진 검증

- 공식 action commit `e7a99fb...`을 로컬 build함. 선언된 `cbomkit-lib:1.1`은 공개 tag의 실제 Maven version과 맞지 않아 실패했으며, 분석을 위해 무시되는 upstream clone의 dependency를 로컬 설치한 `cbomkit-lib:1.2.0`으로 바꾼 뒤 fat JAR build에 성공함.
- lab root를 `GITHUB_WORKSPACE`로 설정하고 그 workspace에서 실행했을 때 Java/Python/Go 모듈 CBOM과 통합 `cbom.json`을 생성함. 통합 결과는 CycloneDX 1.6, components 49개, dependencies 24개이며 semantic validation을 통과함.
- 다른 현재 디렉터리에서 실행하면 통합 CBOM은 생성되지만 모듈 CBOM이 빈 파일이 되는 working-directory 민감성을 확인함. GitHub runner에서는 보통 workspace가 현재 디렉터리지만 로컬·custom runner 재현 시 명시해야 할 실행 전제임.
- Action 엔진은 동일 알고리즘을 언어 간 병합하지 않아 Sonar current plugin의 38 components보다 11개 많음. 반면 고수준 언어별 fixture family는 모두 포함함.
- README/workflow 예제는 `CBOMKIT_WRITE_EMTPY_CBOMS`로 오타가 있지만 코드는 `CBOMKIT_WRITE_EMPTY_CBOMS`를 읽음. 기본값이 true이므로 기본 실행에서는 드러나지 않음.

### 2026-08-25 — 취약 구성 변경 전후 재검증

- `remediated/`에 원본과 나란히 비교 가능한 보완 fixture를 작성함. MD5를 SHA-256으로, AES-CBC를 AES-GCM으로, OpenSSL 최소 protocol을 TLS 1.2에서 TLS 1.3으로 바꿈.
- Java·Python·Go 보완 fixture를 각각 build·실행하여 비어 있지 않은 암호 연산 결과를 확인함. 실제 PQC library 구현은 추가하지 않았고 RSA→PQC 전환 판단은 별도 ML-KEM 정책 fixture로만 검증함.
- Action 3언어 재스캔 결과 components 49→44, dependencies 24→23. MD5 component 3개와 CBC component 2개가 정확히 제거되고 SHA-256/AES-GCM evidence occurrence로 흡수됨.
- Theia의 설정 전용 비교에서 components 11→6, dependencies 2→1이며 TLSv1.2 protocol component가 제거되고 TLSv1.3만 남음. 중복 알고리즘 component도 줄었지만 이는 입력 설정의 protocol section 수 차이에 따른 부수 효과임.

### 2026-08-25 — 실행 캡처·통합 기능 명세 완성

- `scripts/capture_evidence.py`로 JSON·로그 기반 실행 증거 카드와 실제 CBOMkit/coeus 브라우저 화면을 생성함.
- 각 그림마다 실행 내용, 확인 지점, 가능한 결론, 결론낼 수 없는 내용을 `evidence/CAPTURE_MANIFEST.md`에 기록함.
- misleading한 Sonar consent/login 화면은 실제 scanner log·issue API·CBOM 기반 결과 카드로 덮어씀. Sonar UI 성공 화면으로 가장하지 않음.
- `CBOM_통합_기능_명세서.md`에 CBOM 정의·요소·생태계 설치 관계, 도구 7종의 20항목 명세, 정량 비교, compliance matrix, 변경 전후, 15개 결함, 운영 gate와 재현 명령을 작성함.
- CBOMkit release 2.2.0 full/coeus 화면은 실제 실행 화면이며 current main blank screen은 별도 console error JSON과 함께 보존함.
- 별도 `npm audit --json` 재측정은 current main 48건(critical 2/high 24), release 2.2.0 worktree 59건(critical 3/high 27)을 보고함. release 설치 직후 summary 25건과 차이가 있어 npm version·audit 시점·scope도 결과와 함께 고정해야 함.

### 2026-08-25 — Git 게시 전 안전성 검증

- 추적 대상은 186개, 약 11 MiB이며 10 MiB 초과 단일 파일은 없음.
- `tools/` 약 4.8 GiB, `sources/` 약 2.8 GiB, UI build bundle 48 MiB, target/binary, Action 임시 workspace를 `.gitignore`로 제외함.
- 테스트 private key 2개는 제외했고 public certificate/public key만 추적함.
- tracked content에서 private-key PEM header, GitHub token, Sonar token, Bearer authorization, AWS key 형태를 파일 내용 노출 없이 검사했으며 hit 0개임.
- Python script compile, local Markdown link, schema 13 cases, semantic positive set을 재검증해 모두 통과함.

### 2026-08-25 — 최초 push·GitHub Action·CBOMkit public Git scan

- 최초 commit `066b89efca6623f15f380478752e7c1e188047e2`를 정확히 `first commit` 메시지로 만들고 지정한 `origin/main`에 push함. `git ls-remote` hash와 로컬 hash가 일치함.
- GitHub REST API로 workflow_dispatch를 실행함. run `32826680204`는 48초에 success, 모든 job step success, `CBOM` artifact ID `9555171808`, size 8,307 bytes임.
- 원격 artifact digest는 `8fb665a1dbdeb3a6873061dc3896e95d7f0ce74ab759d6c5cb6d98f7fad6a74d`로 GitHub log와 다운로드 파일이 일치함.
- artifact는 통합 41 components/22 dependencies, Java 29/16, Python 12/6, 미빌드 보완 Java module 0/0을 포함함. workflow success가 모든 module의 non-empty inventory를 보장하지 않음을 확인함.
- 공개 저장소 URL을 CBOMkit `/api/v1/scan`에 POST해 HTTP 202를 받고 commit `066b89e`를 clone·scan함. DB key는 `pkg:github/m3rcy1028/cbom-test@066b89e`, 통합 48 components/24 dependencies임.
- Git scan language row: Java 2 files/212 lines/28 components, Python 1/68/13, Go 4/129/7. evidence에는 보완 Go만 포함되고 보완 Java/Python이 없어 module/language coverage assertion의 필요성을 확인함.
- 원격 Action CBOM을 `lab-action-github`로 API 저장·재조회하고 built-in compliance를 실행함. 41 findings, `error:false`, global false임.
- 실제 GitHub run 화면은 `evidence/22-github-action-success.png`, raw API·artifact·logs는 `results/action/github/`, public Git scan 원본은 `results/cbomkit/git-scan-*`에 보존함.

### 2026-08-25 — 원격 증거 게시 전 최종 검증

- GitHub Action artifact ZIP과 추출한 CBOM 4개를 `SHA256SUMS.txt`로 대조해 모두 일치함.
- 원격 Action CBOM과 CBOMkit public Git scan CBOM을 schema 검증군과 semantic positive 검증군에 추가함. 최종 결과는 schema 13/13, semantic 12/12임.
- Python script compile, workflow YAML parse, Markdown local link 34개, staged file 10 MiB 상한을 검사해 모두 통과함.
- staged content에서 private-key PEM, GitHub/Sonar/AWS token 형태와 unredacted Bearer credential hit가 모두 0개임.
- 새 clone에서도 schema 검증을 재현할 수 있도록 전체 upstream clone 대신 Apache-2.0 JSON Schema snapshot 7개, IBM license와 SHA-256 출처표만 추적함.
- staged tree를 임시 디렉터리에 독립 전개하고 upstream clone 없이 schema 13건과 semantic 12건을 다시 실행해 통과함.
- GitHub에서 받은 원본 log/header의 후행 공백과 CRLF는 증거 원형 보존을 위해 정규화하지 않음.

### 2026-08-25 — 원격 증거 후속 push 완료

- 원격 Action artifact·CBOMkit public Git scan·갱신 보고서·캡처·재현 schema를 commit `fe54298394571ca90da14a674059e0e753fe309f` (`docs: add remote CBOM validation evidence`)로 생성함.
- `origin/main` push 후 `git rev-parse HEAD`와 `git ls-remote origin refs/heads/main`이 모두 위 해시로 일치함을 확인함.
- 사용자 지정 최초 commit `066b89e`와 메시지 `first commit`은 변경하지 않고 후속 실행 증거를 별도 commit으로 보존함.

### 2026-08-25 — 한눈에 보는 결과 요약 추가

- 영어 파일명 `RESULTS_OVERVIEW.md`로 도구 흐름, 핵심 수치, `results/` 디렉터리 역할, IBM Zurich Viewer 입력 파일과 주요 한계를 한 문서에 요약함.
- README와 `plan.md`에서 결과 요약으로 바로 이동할 수 있도록 링크함.
- 이번 사용자 요청 범위는 local commit까지이며 원격 push는 포함하지 않음.
