#!/usr/bin/env python3
"""Create a deterministic component/dependency diff for two CycloneDX CBOMs."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def identity(component: dict[str, Any], index: int) -> str:
    if component.get("bom-ref"):
        return component["bom-ref"]
    digest = hashlib.sha256(canonical(component).encode()).hexdigest()[:16]
    return f"__missing_bom_ref__:{index}:{digest}"


def asset_type(component: dict[str, Any]) -> str:
    return component.get("cryptoProperties", {}).get("assetType", component.get("type", "unknown"))


def load(path: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    bom = json.loads(path.read_text(encoding="utf-8"))
    indexed = {identity(component, index): component for index, component in enumerate(bom.get("components", []))}
    return bom, indexed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    before_bom, before = load(args.before)
    after_bom, after = load(args.after)
    before_refs, after_refs = set(before), set(after)
    added_refs = sorted(after_refs - before_refs)
    removed_refs = sorted(before_refs - after_refs)
    common_refs = sorted(before_refs & after_refs)
    modified_refs = [ref for ref in common_refs if canonical(before[ref]) != canonical(after[ref])]
    unchanged_refs = [ref for ref in common_refs if ref not in set(modified_refs)]
    added = [after[ref] for ref in added_refs]

    report = {
        "before": {"path": str(args.before), "sha256": sha256(args.before), "specVersion": before_bom.get("specVersion")},
        "after": {"path": str(args.after), "sha256": sha256(args.after), "specVersion": after_bom.get("specVersion")},
        "summary": {
            "beforeComponents": len(before),
            "afterComponents": len(after),
            "added": len(added_refs),
            "removed": len(removed_refs),
            "modified": len(modified_refs),
            "unchanged": len(unchanged_refs),
            "beforeDependencies": len(before_bom.get("dependencies", [])),
            "afterDependencies": len(after_bom.get("dependencies", [])),
        },
        "addedByAssetType": dict(sorted(Counter(asset_type(item) for item in added).items())),
        "added": [
            {
                "identity": ref,
                "bom-ref": after[ref].get("bom-ref"),
                "name": after[ref].get("name"),
                "assetType": asset_type(after[ref]),
            }
            for ref in added_refs
        ],
        "removedRefs": removed_refs,
        "modifiedRefs": modified_refs,
        "missingBomRefAfter": [item for item in added_refs if item.startswith("__missing_bom_ref__:")],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
