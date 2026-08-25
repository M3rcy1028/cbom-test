# Validation schema snapshots

`scripts/validate_schemas.py`를 새 clone에서도 네트워크 없이 실행하기 위해 검증에 필요한 schema만 추적한다. 전체 upstream repository와 build 결과는 포함하지 않는다.

| 경로 | 출처 | SHA-256 |
|---|---|---|
| `ibm-cbom/bom-1.4-cbom-1.0.schema.json` | IBM/CBOM commit `09fbe5781bfa90fba104846c90e0d1cb643a4d97` | `e10d831f62b5d1b7f56e441195385ac5728060dae7e5df94eac0e0638ba893ad` |
| `ibm-cbom/jsf-0.82.schema.json` | 같은 commit의 dependency | `fe9450c65b76d0d4fa3870886e9e75f984096cbbc64a71b62a51c2df1624ef99` |
| `ibm-cbom/spdx.schema.json` | 같은 commit의 dependency | `545e417341face10511651386d1ddd8e086113ec8669b24d8fd7a8221061e5ab` |
| `cyclonedx-schema/bom-1.6.schema.json` | `https://cyclonedx.org/schema/bom-1.6.schema.json` | `3e92dddbc30cf7f6a02b80f0942b1a4cfd4fb1c26f1dfc4310afa9d613cafb93` |
| `cyclonedx-schema/bom-1.7.schema.json` | `https://cyclonedx.org/schema/bom-1.7.schema.json` | `73308edec3ab2d38bfffd993e96a042b594314143b6971a6e9ed98bbb6bd76ce` |
| `cyclonedx-schema/jsf-0.82.schema.json` | CycloneDX schema dependency | `8bae002c25e723db7ee1f26afde680ae1a2b1a8f6b4b4b0fd65dc3becb090aae` |
| `cyclonedx-schema/spdx.schema.json` | CycloneDX schema dependency | `ea6e844ee6fba1e93473d94834d0ee0996970533497935f932f73d488ffdf4a3` |

IBM/CBOM과 CycloneDX schema는 각 schema의 `$comment`에 명시된 Apache License 2.0 조건을 따른다. IBM 원문의 `LICENSE`도 함께 보존한다.
