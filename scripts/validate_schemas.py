#!/usr/bin/env python3
"""Run reproducible positive and negative CBOM schema checks."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft7Validator, RefResolver


ROOT = Path(__file__).resolve().parents[1]


def check(label: str, schema_path: Path, document_path: Path, expect_valid: bool) -> dict:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    document = json.loads(document_path.read_text(encoding="utf-8"))
    resolver = RefResolver(base_uri=schema_path.resolve().as_uri(), referrer=schema)
    errors = sorted(
        Draft7Validator(schema, resolver=resolver).iter_errors(document),
        key=lambda error: list(error.absolute_path),
    )
    actual_valid = not errors
    return {
        "label": label,
        "schema": str(schema_path.relative_to(ROOT)),
        "document": str(document_path.relative_to(ROOT)),
        "expectedValid": expect_valid,
        "actualValid": actual_valid,
        "passed": actual_valid == expect_valid,
        "errors": [
            {
                "path": "/" + "/".join(str(item) for item in error.absolute_path),
                "message": error.message,
            }
            for error in errors[:10]
        ],
    }


def main() -> int:
    cases = [
        check(
            "IBM CBOM 1.0 positive",
            ROOT / "sources/ibm-cbom/bom-1.4-cbom-1.0.schema.json",
            ROOT / "results/ibm/valid-cbom-1.0.json",
            True,
        ),
        check(
            "IBM CBOM 1.0 negative: CycloneDX-style primitive spelling",
            ROOT / "sources/ibm-cbom/bom-1.4-cbom-1.0.schema.json",
            ROOT / "results/ibm/invalid-cbom-1.0.json",
            False,
        ),
        check(
            "CycloneDX 1.6 positive: Sonar-generated CBOM",
            ROOT / "sources/cyclonedx-schema/bom-1.6.schema.json",
            ROOT / "results/sonar/cbom.json",
            True,
        ),
        check(
            "CycloneDX 1.6 negative: unknown primitive",
            ROOT / "sources/cyclonedx-schema/bom-1.6.schema.json",
            ROOT / "results/cyclonedx/invalid-primitive-1.6.json",
            False,
        ),
        check(
            "CycloneDX 1.6 schema-positive but semantically dangling dependency",
            ROOT / "sources/cyclonedx-schema/bom-1.6.schema.json",
            ROOT / "results/cyclonedx/semantic-invalid-dangling-ref.json",
            True,
        ),
        check(
            "CycloneDX 1.7 positive: Theia-generated CBOM",
            ROOT / "sources/cyclonedx-schema/bom-1.7.schema.json",
            ROOT / "results/theia-dir/cbom.json",
            True,
        ),
        check(
            "CycloneDX 1.6 positive: local Action consolidated CBOM",
            ROOT / "sources/cyclonedx-schema/bom-1.6.schema.json",
            ROOT / "results/action/local-workspace-cwd/cbom.json",
            True,
        ),
        check(
            "CycloneDX 1.6 positive: remediated Action CBOM",
            ROOT / "sources/cyclonedx-schema/bom-1.6.schema.json",
            ROOT / "results/action/remediated/cbom.json",
            True,
        ),
        check(
            "CycloneDX 1.7 positive: Theia registry image CBOM",
            ROOT / "sources/cyclonedx-schema/bom-1.7.schema.json",
            ROOT / "results/theia-image/alpine-3.22-cbom.json",
            True,
        ),
        check(
            "CycloneDX 1.7 positive: Theia OCI amd64 CBOM",
            ROOT / "sources/cyclonedx-schema/bom-1.7.schema.json",
            ROOT / "results/theia-image/alpine-3.22-oci-amd64-cbom.json",
            True,
        ),
        check(
            "CycloneDX 1.7 positive: remediated Theia directory CBOM",
            ROOT / "sources/cyclonedx-schema/bom-1.7.schema.json",
            ROOT / "results/remediated-theia/cbom.json",
            True,
        ),
    ]
    output = {"allPassed": all(case["passed"] for case in cases), "cases": cases}
    result_path = ROOT / "results/cyclonedx/schema-validation.json"
    result_path.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for case in cases:
        state = "PASS" if case["passed"] else "FAIL"
        print(f"[{state}] {case['label']}: actualValid={case['actualValid']}")
        for error in case["errors"][:2]:
            print(f"  {error['path']}: {error['message']}")
    return 0 if output["allPassed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
