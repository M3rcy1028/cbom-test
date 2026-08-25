#!/usr/bin/env python3
"""CycloneDX CBOM reference-integrity checks that JSON Schema does not cover."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


def validate(path: Path) -> dict[str, Any]:
    bom = json.loads(path.read_text(encoding="utf-8"))
    components = bom.get("components", [])
    dependencies = bom.get("dependencies", [])
    refs = [item.get("bom-ref") for item in components if item.get("bom-ref")]
    counts = Counter(refs)
    duplicate_refs = sorted(ref for ref, count in counts.items() if count > 1)
    missing_component_refs = [
        {"index": index, "name": item.get("name"), "type": item.get("type")}
        for index, item in enumerate(components)
        if not item.get("bom-ref")
    ]

    known_refs = set(refs)
    metadata_component = bom.get("metadata", {}).get("component", {})
    if metadata_component.get("bom-ref"):
        known_refs.add(metadata_component["bom-ref"])

    dangling_dependency_roots: list[dict[str, Any]] = []
    dangling_dependency_targets: list[dict[str, Any]] = []
    duplicate_dependency_roots: list[str] = []
    dependency_root_counts = Counter()
    for dependency in dependencies:
        root = dependency.get("ref")
        if root:
            dependency_root_counts[root] += 1
            if root not in known_refs:
                dangling_dependency_roots.append({"ref": root})
        for target in dependency.get("dependsOn", []):
            if target not in known_refs:
                dangling_dependency_targets.append({"ref": root, "dependsOn": target})
    duplicate_dependency_roots = sorted(
        ref for ref, count in dependency_root_counts.items() if count > 1
    )

    issues = {
        "missingComponentBomRefs": missing_component_refs,
        "duplicateComponentBomRefs": duplicate_refs,
        "danglingDependencyRoots": dangling_dependency_roots,
        "danglingDependencyTargets": dangling_dependency_targets,
        "duplicateDependencyRoots": duplicate_dependency_roots,
    }
    issue_count = sum(len(value) for value in issues.values())
    return {
        "path": str(path),
        "specVersion": bom.get("specVersion"),
        "componentCount": len(components),
        "dependencyCount": len(dependencies),
        "semanticValid": issue_count == 0,
        "issueCount": issue_count,
        "issues": issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = {"checks": [validate(path) for path in args.paths]}
    report["allValid"] = all(item["semanticValid"] for item in report["checks"])
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
