# cbom-test

IBM/PQCA CBOM 생태계를 동일한 Java·Python·Go·인증서·TLS fixture로 실행하고 비교한 재현 lab이다. IBM schema, Sonar Cryptography Plugin, CBOMkit-action, CBOMkit-theia, CBOMkit full/coeus, PostgreSQL, built-in compliance와 OPA를 다룬다.

## 먼저 볼 문서

- [한눈에 보는 결과 요약](RESULTS_OVERVIEW.md): 결과 디렉터리, 핵심 수치, Viewer 입력 파일
- [통합 기능 명세 및 실증 보고서](CBOM_통합_기능_명세서.md): 도구별 20항목 명세, 결과 비교, 결함, 운영 권고
- [게시 계획과 현재 상태](plan.md): 사용자 지정 Git 게시 절차와 재개 지점
- [상세 실행 계획·작업 원장](CBOM_LAB_PLAN.md): revision, 실행 순서, 원본 결과와 차단 사유
- [Ground truth](ground-truth.md): scanner 실행 전에 고정한 기대 자산·line·정책
- [캡처 manifest](evidence/CAPTURE_MANIFEST.md): 각 그림이 증명하는 것과 증명하지 않는 것

## 대표 결과

| 대상 | 결과 |
|---|---:|
| Schema 정상·음성 case | 15/15 기대 일치 |
| 실제 quantum-safe code | ML-KEM-768 round-trip·탐지·Viewer 판정 성공 |
| Sonar source scan | 38 components, source family 22/22 |
| Action local scan | 49 components, Java/Python/Go module CBOM |
| Theia directory | 25 components, filesystem 6/7 |
| Theia `alpine:3.22` | 2,858 components |
| Sonar→Theia enrichment | 38→64 components |
| Built-in/OPA policy fixture | exact 5/5 vs 3/5 |
| 보완 후 Action | 49→44, MD5·CBC component 제거 |
| GitHub Action run | 전체 scan success + 격리 ML-KEM scan success |
| CBOMkit public Git scan | 48 components, DB 저장 성공 |

![CBOMkit result](evidence/16-cbomkit-sonar-results.png)

## 빠른 재현

```bash
mvn -f java-app/pom.xml clean package
mvn -f java-app/pom.xml exec:java
python3 python-app/crypto_fixture.py
tools/go/bin/go -C go-app run .
tools/go/bin/go -C quantum-safe-go run .

python3 scripts/validate_schemas.py
python3 scripts/capture_evidence.py
```

IBM Zurich Viewer에서 `Quantum Safe` 결과를 바로 확인하려면 [GitHub-hosted quantum-safe CBOM](results/quantum-safe/github/artifact/quantum-safe/cbom.json)을 다운로드해 업로드한다.

`tools/`와 `sources/`의 다운로드·upstream clone은 크기와 재배포 문제로 Git에서 제외한다. 단, offline schema 재검증에 필요한 JSON Schema snapshot과 출처 기록은 포함한다. 정확한 upstream URL과 commit은 [schema 출처](sources/SCHEMA_SOURCES.md), 작업 원장과 보고서에 기록했다.

## 안전 주의

이 repository의 MD5, AES-CBC, 고정 key/IV와 인증서는 scanner 검증용이며 production 예제가 아니다. 테스트 private key와 credential은 Git에서 제외한다. CBOM에는 source 위치·암호 구성·certificate metadata가 포함될 수 있으므로 실제 조직에서는 접근 제어와 log redaction이 필요하다.
