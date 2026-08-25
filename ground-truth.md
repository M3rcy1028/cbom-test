# CBOM Lab Ground Truth

> 이 파일은 scanner 실행 전에 고정한 정답표다. 결과를 본 뒤 기대값을 바꾸지 않는다.  
> 기준 revision: 초기 fixture, 2026-08-25. 소스 변경 시 새 revision 표를 추가한다.

## 1. 판정 규칙

- 하나의 고수준 자산이 여러 API call로 탐지되어도 asset identity가 같고 evidence가 모두 보존되면 TP 1개로 정규화한다.
- SHA-256이 RSA-OAEP, ECDSA, PBKDF2의 하위 파라미터로 등장한 경우 독립 digest 사용과 구분하여 relationship/property completeness에서 평가한다.
- family만 탐지되고 mode·size·padding이 빠지면 TP이지만 property incomplete로 기록한다.
- 지원 범위 밖 언어는 FN이 아니라 `UNSUPPORTED`로 별도 표시한다. 지원한다고 선언한 범위에서 누락된 경우만 FN이다.
- `implements`와 실제 call evidence가 있는 `uses`를 구분한다.

## 2. Java ground truth

파일: `java-app/src/main/java/lab/CryptoFixture.java`

| ID | line | 기대 자산 | primitive | 핵심 속성 | function | 정책 기대 |
|---|---:|---|---|---|---|---|
| J-A01 | 32 | AES-128-GCM | `ae` | size=128, mode=gcm, no padding | encrypt | NA |
| J-A02 | 39 | AES-128-CBC | `block-cipher` | size=128, mode=cbc, padding=pkcs5 | encrypt | NA |
| J-A03 | 48 | RSA-2048-OAEP | `pke` | size=2048, padding=oaep, SHA-256 MGF | encrypt | vulnerable |
| J-A04 | 54 | SHA-256 | `hash` | size=256 | digest | NA |
| J-A05 | 59 | MD5 | `hash` | size=128 | digest | NA/별도 금지정책 위반 |
| J-A06 | 64 | PBKDF2-HMAC-SHA256 | `kdf` | output=256, iterations=120000 | keyderive | NA |
| J-A07 | 73 | ECDSA/secp256r1/SHA-256 | `signature` | curve=secp256r1 | sign | vulnerable |
| J-A08 | 84 | ECDH/secp256r1 | `key-agree` | curve=secp256r1 | keyderive | vulnerable; 현 OPA 오분류 예상 |

## 3. Python ground truth

파일: `python-app/crypto_fixture.py`

| ID | line | 기대 자산 | primitive | 핵심 속성 | function | 정책 기대 |
|---|---:|---|---|---|---|---|
| P-A01 | 13 | AES-128-GCM | `ae` | size=128, mode=gcm | encrypt | NA |
| P-A02 | 19 | AES-128-CBC | `block-cipher` | size=128, mode=cbc | encrypt | NA |
| P-A03 | 24 | RSA-2048-OAEP | `pke` | size=2048, OAEP+SHA-256 | encrypt | vulnerable |
| P-A04 | 36 | SHA-256 | `hash` | size=256 | digest | NA |
| P-A05 | 42 | MD5 | `hash` | size=128 | digest | NA/별도 금지정책 위반 |
| P-A06 | 48 | PBKDF2-HMAC-SHA256 | `kdf` | output=256, iterations=120000 | keyderive | NA |
| P-A07 | 54-55 | ECDSA/secp256r1/SHA-256 | `signature` | curve=secp256r1 | sign | vulnerable |
| P-A08 | 59-61 | ECDH/secp256r1 | `key-agree` | curve=secp256r1 | keyderive | vulnerable; 현 OPA 오분류 예상 |

## 4. Go ground truth

파일: `go-app/main.go`

| ID | line | 기대 자산 | primitive | 핵심 속성 | function | 정책 기대 |
|---|---:|---|---|---|---|---|
| G-A01 | 19-20 | AES-128-GCM | `ae` | size=128, mode=gcm | encrypt | NA |
| G-A03 | 25-26 | RSA-2048-OAEP | `pke` | size=2048, SHA-256 | encrypt | vulnerable |
| G-A04 | 31 | SHA-256 | `hash` | size=256 | digest | NA |
| G-A05 | 32 | MD5 | `hash` | size=128 | digest | NA/별도 금지정책 위반 |
| G-A07 | 37-38 | ECDSA/P-256/SHA-256 | `signature` | curve=P-256 | sign | vulnerable |
| G-A08 | 44-47 | ECDH/P-256 | `key-agree` | curve=P-256 | keyderive | vulnerable; 현 OPA 오분류 예상 |

## 5. Filesystem/container ground truth

| ID | path | 기대 자산 | 기대 속성 |
|---|---|---|---|
| C01 | `certs/valid-cert.pem` | X.509 certificate | subject `cbom-lab-valid`, 유효기간 2026-08-25~2027-08-25 |
| C02 | `certs/expired-cert.pem` | X.509 certificate | subject `cbom-lab-expired`, 이미 만료 |
| K01 | `certs/test-public-key.pem` | RSA public key | size=2048, PEM |
| K02 | `certs/test-private-key.pem` | RSA private key | size=2048, PEM, test-only |
| K03 | `certs/expired-private-key.pem` | RSA private key | size=2048, PEM, test-only |
| P01 | `config/openssl.cnf` | TLS protocol config | min TLS1.2, max TLS1.3 |
| P02 | `config/openssl.cnf` | TLS cipher suites | AES-128/256-GCM, SHA-256/384, ECDHE-RSA |

## 6. Policy-only PQC fixture

실제 구현을 가장하지 않고 `results/compliance/policy-fixture-cbom.json`에 명세 입력으로 둔다.

| ID | 기대 자산 | primitive | 핵심 속성 | 기대 결과 |
|---|---|---|---|---|
| Q-A09 | ML-KEM-768 | `kem` | `nistQuantumSecurityLevel=3` | quantum-safe |

## 7. 실제 quantum-safe source revision

초기 baseline 평가가 끝난 뒤 별도 디렉터리에 실제 실행 fixture를 추가했다. 기존 Java·Python·Go 22개 family recall 수치는 변경하지 않고 독립 실험으로 평가한다.

파일: `quantum-safe-go/main.go`

| ID | line | 기대 자산 | primitive | 핵심 속성 | function | 정책 기대 |
|---|---:|---|---|---|---|---|
| Q-A10 | 13, 18-20 | ML-KEM-768 | `kem` | parameter set 768, NIST OID `2.16.840.1.101.3.4.4.2` | keygen, encapsulate, decapsulate | quantum-safe |

완료 조건:

- Go `crypto/mlkem`으로 양쪽 32-byte shared key가 실제로 일치한다.
- scanner CBOM에 `ML-KEM-768`, `primitive=kem`, source occurrence가 존재한다.
- CBOM은 CycloneDX 1.6 schema와 semantic validation을 통과한다.
- IBM Zurich Viewer와 built-in policy가 자산을 `Quantum Safe`로 표시한다.

## 8. 예상 도구 범위

| 도구 | Java | Python | Go | 인증서/키 | OpenSSL config | container |
|---|---:|---:|---:|---:|---:|---:|
| Sonar Plugin | O | O | O | 소스 참조만 | 제한적 | X |
| CBOMkit-action | O | O | `e7a99fb` Go integration에서 O; v2.1.1 README는 미지원 표기 | X | X | X |
| CBOMkit service scanner | O | O | O | X | X | X |
| CBOMkit-theia | source scan X | source scan X | source scan X | O | O | O |

## 9. 실행 결과 기입 표

| 도구 | 지원 대상 수 | TP | FP | FN | Precision | Recall | property completeness | evidence coverage |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Sonar Plugin | 22 | 22 | 미산정¹ | 0 | 미산정¹ | 100% | 부분 충족² | 22/22 |
| CBOMkit-action | 22 | 22 | 미산정¹ | 0 | 미산정¹ | 100% | 부분 충족² | 22/22 |
| CBOMkit service | 해당 없음³ | 해당 없음 | 해당 없음 | 해당 없음 | 해당 없음 | 해당 없음 | 생성기 결과 보존 | API 입력 기준 |
| CBOMkit-theia | 7 | 6 | 미산정¹ | 1 | 미산정¹ | 85.7% | 부분 충족⁴ | 6/7 |

1. 보조 알고리즘·키 재료도 실제 암호 자산이므로 이를 FP로 세지 않았다. 비암호 음성 corpus를 두지 않았기 때문에 precision을 임의로 제시하지 않는다.
2. family와 evidence는 모두 탐지했으나 Python RSA-OAEP가 RSA key 생성으로만 표현되는 등 operation·parameter 완전성은 일관되지 않다.
3. CBOMkit API/viewer는 이 실험에서 입력 CBOM의 소비·저장·정책 평가 계층으로 사용했으므로 source 탐지 recall 대상이 아니다.
4. 인증서 2, 개인키 2, TLS 설정 2는 탐지했으나 독립 공개키 1개를 놓쳤다. enrichment에서는 JDK 설정의 `KeyUpdate` 문자열을 API key로 오탐한 사례도 별도로 관측했다.
