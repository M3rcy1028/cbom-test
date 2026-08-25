# ML-KEM-768 quantum-safe fixture

이 fixture는 Go 표준 라이브러리 `crypto/mlkem`의 NIST FIPS 203 ML-KEM-768 구현으로 다음 과정을 실제 수행한다.

1. decapsulation key 생성
2. public encapsulation key 도출
3. shared key 캡슐화
4. ciphertext 역캡슐화
5. 양쪽 shared key 일치 검증

실행:

```bash
../tools/go/bin/go run .
```

정상 출력:

```text
quantum-safe-fixture-ok algorithm=ML-KEM-768 shared-key-bytes=32
```

이 코드는 CBOM scanner와 Viewer 검증용 최소 fixture다. 실제 protocol 설계, key lifecycle, 인증과 hybrid migration을 대신하지 않는다.
