#!/usr/bin/env python3
"""Compare CBOMs by stable semantic signatures instead of generated bom-ref UUIDs."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)


def replace_generated_refs(value: Any) -> Any:
    """Keep relationship shape while removing run-specific UUID values."""
    if isinstance(value, str):
        return "<generated-ref>" if UUID.fullmatch(value) else value
    if isinstance(value, list):
        return [replace_generated_refs(item) for item in value]
    if isinstance(value, dict):
        return {key: replace_generated_refs(item) for key, item in value.items()}
    return value


def signature(component: dict[str, Any]) -> tuple[str, str, str]:
    crypto = component.get("cryptoProperties", {})
    asset_type = crypto.get("assetType", component.get("type", "unknown"))
    name = component.get("name", "")
    if asset_type == "related-crypto-material":
        # Generated material names end in a bom-ref UUID. The material kind and
        # properties are the stable part for cross-run comparisons.
        name = name.split("@", 1)[0]
        properties = crypto.get("relatedCryptoMaterialProperties", {})
    elif asset_type == "algorithm":
        properties = crypto.get("algorithmProperties", {})
    elif asset_type == "protocol":
        properties = replace_generated_refs(crypto.get("protocolProperties", {}))
    elif asset_type == "certificate":
        properties = crypto.get("certificateProperties", {})
    else:
        # A file/config component remains the same asset when its extracted
        # properties change. Property-level differences are discussed using
        # the raw CBOM and are not treated as component add/remove events.
        properties = {}
    return asset_type, name, canonical(properties)


def label(sig: tuple[str, str, str]) -> str:
    asset_type, name, properties = sig
    prop = json.loads(properties)
    primitive = prop.get("primitive", "") if isinstance(prop, dict) else ""
    return " | ".join(item for item in (asset_type, name, primitive) if item)


def profile(path: Path) -> tuple[dict[str, Any], dict[tuple[str, str, str], dict[str, Any]]]:
    bom = json.loads(path.read_text(encoding="utf-8"))
    grouped: dict[tuple[str, str, str], dict[str, Any]] = defaultdict(
        lambda: {"components": 0, "occurrences": 0, "locations": []}
    )
    for component in bom.get("components", []):
        item = grouped[signature(component)]
        item["components"] += 1
        occurrences = component.get("evidence", {}).get("occurrences", [])
        item["occurrences"] += len(occurrences)
        item["locations"].extend(
            sorted(
                f"{occ.get('location', '?')}:{occ.get('line', '?')}"
                for occ in occurrences
            )
        )
    return bom, grouped


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    parser.add_argument("--before-label", default="before")
    parser.add_argument("--after-label", default="after")
    parser.add_argument("--json", required=True, type=Path)
    parser.add_argument("--markdown", required=True, type=Path)
    args = parser.parse_args()

    before_bom, before = profile(args.before)
    after_bom, after = profile(args.after)
    keys = sorted(set(before) | set(after))
    rows = []
    for key in keys:
        left = before.get(key, {"components": 0, "occurrences": 0, "locations": []})
        right = after.get(key, {"components": 0, "occurrences": 0, "locations": []})
        rows.append(
            {
                "signature": label(key),
                "properties": json.loads(key[2]),
                "beforeComponents": left["components"],
                "afterComponents": right["components"],
                "componentDelta": right["components"] - left["components"],
                "beforeOccurrences": left["occurrences"],
                "afterOccurrences": right["occurrences"],
                "occurrenceDelta": right["occurrences"] - left["occurrences"],
                "beforeLocations": sorted(set(left["locations"])),
                "afterLocations": sorted(set(right["locations"])),
            }
        )

    def summary(path: Path, bom: dict[str, Any]) -> dict[str, Any]:
        types = Counter(
            component.get("cryptoProperties", {}).get(
                "assetType", component.get("type", "unknown")
            )
            for component in bom.get("components", [])
        )
        return {
            "path": str(path),
            "sha256": sha256(path),
            "specVersion": bom.get("specVersion"),
            "components": len(bom.get("components", [])),
            "dependencies": len(bom.get("dependencies", [])),
            "assetTypes": dict(sorted(types.items())),
        }

    report = {
        "comparisonMethod": "asset type + normalized name + canonical crypto properties; bom-ref UUID excluded",
        "beforeLabel": args.before_label,
        "afterLabel": args.after_label,
        "before": summary(args.before, before_bom),
        "after": summary(args.after, after_bom),
        "summary": {
            "semanticSignatures": len(rows),
            "removedSignatures": sum(row["afterComponents"] == 0 for row in rows),
            "addedSignatures": sum(row["beforeComponents"] == 0 for row in rows),
            "changedComponentCounts": sum(row["componentDelta"] != 0 for row in rows),
            "changedOccurrenceCounts": sum(row["occurrenceDelta"] != 0 for row in rows),
        },
        "rows": rows,
    }
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        f"# {args.before_label} vs {args.after_label}",
        "",
        "> 비교 키: asset type + 정규화한 이름 + crypto properties. 실행마다 바뀌는 bom-ref UUID는 제외했다.",
        "",
        f"- Components: {report['before']['components']} → {report['after']['components']}",
        f"- Dependencies: {report['before']['dependencies']} → {report['after']['dependencies']}",
        f"- Removed signatures: {report['summary']['removedSignatures']}",
        f"- Added signatures: {report['summary']['addedSignatures']}",
        "",
        "| Semantic signature | Components | Occurrences |",
        "|---|---:|---:|",
    ]
    for row in rows:
        if row["componentDelta"] or row["occurrenceDelta"]:
            lines.append(
                f"| {row['signature']} | {row['beforeComponents']} → {row['afterComponents']} "
                f"({row['componentDelta']:+d}) | {row['beforeOccurrences']} → "
                f"{row['afterOccurrences']} ({row['occurrenceDelta']:+d}) |"
            )
    lines.append("")
    args.markdown.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
