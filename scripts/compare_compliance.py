#!/usr/bin/env python3
"""Normalize CBOMkit built-in and OPA compliance findings into a golden matrix."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


LEVEL = {1: "quantum-vulnerable", 2: "unknown", 3: "quantum-safe", 4: "not-applicable"}
ASSETS = [
    ("policy:rsa-2048", "RSA-2048", "quantum-vulnerable"),
    ("policy:ecdh-p256", "ECDH-P256", "quantum-vulnerable"),
    ("policy:aes-128-gcm", "AES-128-GCM", "not-applicable"),
    ("policy:unknown", "Vendor-Algorithm-X", "unknown"),
    ("policy:ml-kem-768", "ML-KEM-768", "quantum-safe"),
]


def findings(path: Path) -> tuple[dict[str, list[str]], dict]:
    value = json.loads(path.read_text(encoding="utf-8"))
    grouped: dict[str, list[str]] = defaultdict(list)
    for finding in value.get("findings", []):
        grouped[finding["bomRef"]].append(LEVEL.get(finding["levelId"], f"level-{finding['levelId']}"))
    return grouped, value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--builtin", required=True, type=Path)
    parser.add_argument("--opa", required=True, type=Path)
    parser.add_argument("--json", required=True, type=Path)
    parser.add_argument("--markdown", required=True, type=Path)
    args = parser.parse_args()
    builtin, builtin_raw = findings(args.builtin)
    opa, opa_raw = findings(args.opa)
    rows = []
    for ref, name, expected in ASSETS:
        built = sorted(set(builtin.get(ref, [])))
        external = sorted(set(opa.get(ref, [])))
        rows.append(
            {
                "bomRef": ref,
                "asset": name,
                "groundTruth": expected,
                "builtin": built,
                "opa": external,
                "builtinMatches": built == [expected],
                "opaMatches": external == [expected],
                "opaConflict": len(external) > 1,
            }
        )
    report = {
        "builtinService": builtin_raw.get("complianceServiceName"),
        "opaService": opa_raw.get("complianceServiceName"),
        "rows": rows,
        "summary": {
            "assetCount": len(rows),
            "builtinExactMatches": sum(row["builtinMatches"] for row in rows),
            "opaExactMatches": sum(row["opaMatches"] for row in rows),
            "opaConflictAssets": sum(row["opaConflict"] for row in rows),
        },
    }
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Compliance Golden Matrix",
        "",
        "| Asset | Ground truth | Built-in | External OPA | Built-in exact | OPA exact |",
        "|---|---|---|---|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['asset']} | {row['groundTruth']} | {', '.join(row['builtin']) or '∅'} | "
            f"{', '.join(row['opa']) or '∅'} | {'O' if row['builtinMatches'] else 'X'} | "
            f"{'O' if row['opaMatches'] else 'X'} |"
        )
    lines.extend(
        [
            "",
            f"- Built-in exact matches: {report['summary']['builtinExactMatches']}/{len(rows)}",
            f"- External OPA exact matches: {report['summary']['opaExactMatches']}/{len(rows)}",
            f"- OPA conflicting assets: {report['summary']['opaConflictAssets']}",
            "",
        ]
    )
    args.markdown.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
