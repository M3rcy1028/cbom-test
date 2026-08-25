# Remediated fixture

이 디렉터리는 baseline을 덮어쓰지 않고 암호 자산 변경 전후를 비교하기 위한 입력이다.

- Java/Python의 AES-CBC를 AES-GCM으로 교체했다.
- Java/Python/Go의 MD5 직접 사용을 SHA-256으로 교체했다.
- OpenSSL 최소 프로토콜을 TLS 1.2에서 TLS 1.3으로 올렸다.
- RSA→PQC/hybrid는 구현체를 가장하지 않고 `results/compliance/policy-fixture-cbom.json`의 ML-KEM 명세 자산으로만 평가한다.
