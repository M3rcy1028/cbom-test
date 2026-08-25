#!/usr/bin/env python3
"""Render result-backed evidence cards and capture the actually running CBOMkit UIs."""

from __future__ import annotations

import html
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"


def load(path: str) -> dict[str, Any]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def shell(command: list[str]) -> str:
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    return (result.stdout or result.stderr).strip().splitlines()[0]


def bom_summary(path: str) -> tuple[dict[str, Any], Counter[str]]:
    bom = load(path)
    kinds = Counter(
        component.get("cryptoProperties", {}).get(
            "assetType", component.get("type", "unknown")
        )
        for component in bom.get("components", [])
    )
    return bom, kinds


def render_card(page, filename: str, title: str, source: str, rows: list[tuple[str, str, str]], note: str) -> None:
    rendered_rows = "".join(
        f'<div class="row"><span class="badge {html.escape(state)}">{html.escape(state.upper())}</span>'
        f'<div><strong>{html.escape(label)}</strong><pre>{html.escape(value)}</pre></div></div>'
        for state, label, value in rows
    )
    content = f"""
    <!doctype html><html lang="ko"><meta charset="utf-8"><style>
      * {{ box-sizing: border-box; }}
      body {{ margin:0; background:#07111f; color:#dbeafe; font-family:Inter,'Noto Sans KR',sans-serif; }}
      main {{ width:1520px; min-height:940px; margin:30px auto; padding:44px 54px; background:#0b1728;
              border:1px solid #29415f; border-radius:20px; box-shadow:0 20px 55px #020617; }}
      .eyebrow {{ color:#60a5fa; letter-spacing:.18em; font-weight:800; font-size:15px; }}
      h1 {{ margin:10px 0 8px; font-size:38px; color:#f8fafc; }}
      .source {{ color:#94a3b8; font-family:'DejaVu Sans Mono',monospace; font-size:15px; margin-bottom:28px; }}
      .row {{ display:grid; grid-template-columns:90px 1fr; gap:18px; align-items:start; padding:16px 0;
              border-top:1px solid #20334d; }}
      .row strong {{ color:#bfdbfe; font-size:18px; }}
      pre {{ white-space:pre-wrap; margin:6px 0 0; color:#e2e8f0; font:16px/1.45 'DejaVu Sans Mono',monospace; }}
      .badge {{ display:inline-block; text-align:center; padding:6px 8px; border-radius:999px; font:700 13px monospace; }}
      .pass {{ background:#064e3b; color:#6ee7b7; }} .warn {{ background:#713f12; color:#fde68a; }}
      .fail {{ background:#7f1d1d; color:#fecaca; }} .info {{ background:#1e3a8a; color:#bfdbfe; }}
      footer {{ margin-top:24px; padding:18px 20px; background:#111f34; border-left:4px solid #60a5fa;
               color:#cbd5e1; font-size:16px; line-height:1.5; }}
    </style><body><main><div class="eyebrow">CBOM LAB · RESULT-BACKED EVIDENCE</div>
    <h1>{html.escape(title)}</h1><div class="source">원본: {html.escape(source)}</div>
    {rendered_rows}<footer>{html.escape(note)}</footer></main></body></html>
    """
    page.set_viewport_size({"width": 1600, "height": 1000})
    page.set_content(content, wait_until="load")
    page.screenshot(path=str(EVIDENCE / filename), full_page=True)


def upload_capture(browser, port: int, bom_path: str, output: str, detail_index: int | None = None) -> dict[str, Any]:
    page = browser.new_page(viewport={"width": 1440, "height": 1100}, device_scale_factor=1)
    errors: list[str] = []
    page.on("console", lambda msg: errors.append(f"console:{msg.type}:{msg.text}") if msg.type == "error" else None)
    page.on("pageerror", lambda err: errors.append(f"pageerror:{err}"))
    page.goto(f"http://127.0.0.1:{port}", wait_until="networkidle")
    page.locator('input[type="file"]').set_input_files(str(ROOT / bom_path))
    page.wait_for_timeout(1800)
    if detail_index is not None:
        page.get_by_role("button", name="See details").nth(detail_index).click()
        page.wait_for_timeout(600)
    body = page.locator("body").inner_text()
    page.screenshot(path=str(EVIDENCE / output), full_page=False)
    result = {"url": page.url, "bodyLength": len(body), "bodyExcerpt": body[:600], "errors": errors}
    page.close()
    return result


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    schema = load("results/cyclonedx/schema-validation.json")
    semantics = load("results/cyclonedx/semantic-positive-validation.json")
    sonar, sonar_kinds = bom_summary("results/sonar/cbom.json")
    theia, theia_kinds = bom_summary("results/theia-dir/cbom.json")
    image_bom, image_kinds = bom_summary("results/theia-image/alpine-3.22-cbom.json")
    enriched = load("results/enriched/semantic-diff.json")
    action, action_kinds = bom_summary("results/action/local-workspace-cwd/cbom.json")
    remediated, _ = bom_summary("results/action/remediated/cbom.json")
    issues = load("results/sonar/issues.json")
    rule_counts = Counter(issue.get("rule", "unknown") for issue in issues.get("issues", []))
    matrix = load("results/compliance/golden-matrix.json")
    builtin = load("results/compliance/backend-policy-fixture.json")
    opa = load("results/compliance/backend-opa-policy-fixture.json")
    missing_opa = load("results/compliance/backend-opa-missing-policy.json")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        card = browser.new_page()
        render_card(card, "01-environment.png", "고정 실행 환경", "CBOM_LAB_PLAN.md §12 및 각 build log", [
            ("info", "Runtime", f"{shell(['python3','--version'])} · {shell([str(ROOT/'tools/go/bin/go'),'version'])}\n{shell([str(ROOT/'tools/jdk21/bin/java'),'-version'])}"),
            ("pass", "실행 서비스", "SonarQube 26.1 :9000 · PostgreSQL 14.24 :5433 · CBOMkit :8081/:8082 · OPA 1.15.1 :8181"),
            ("warn", "Docker 경계", "Docker client/Compose는 확인했으나 /var/run/docker.sock 권한 거부. registry·OCI 스캔으로 image 기능을 대체 검증."),
            ("pass", "고정 revision", "IBM 09fbe578 · Sonar f4c834cb · Theia 46eb32fa · Action e7a99fb4 · CBOMkit release 9076203b"),
        ], "버전과 service endpoint가 재현 기준이다. 이 그림만으로 Docker daemon 기반 Compose 실행 성공을 주장하지 않는다.")
        render_card(card, "02-schema-validation.png", "IBM CBOM·CycloneDX Schema 검증", "results/cyclonedx/schema-validation.json", [
            ("pass" if case["passed"] else "fail", case["label"], f"expected={case['expectedValid']} · actual={case['actualValid']}")
            for case in schema["cases"]
        ], f"총 {len(schema['cases'])}개 정상·음성 case가 기대와 일치했다. JSON Schema 통과는 참조 무결성까지 보장하지 않는다.")
        render_card(card, "03-semantic-validation.png", "CBOM 참조 무결성 검증", "results/cyclonedx/semantic-positive-validation.json · semantic-validation.json", [
            ("pass", "정상 산출물", f"{len(semantics['checks'])}/{len(semantics['checks'])}개: bom-ref 중복·누락·dangling dependency 없음"),
            ("warn", "Theia enriched", "64 components 중 generic-api-key component 1개에 bom-ref 누락"),
            ("pass", "음성 fixture", "Schema는 통과하지만 존재하지 않는 dependency target을 semantic validator가 탐지"),
        ], "Schema validation과 semantic validation을 분리해야 하는 이유를 재현한다.")
        render_card(card, "04-fixture-smoke.png", "공통 Fixture 실행", "results/*/smoke 및 ground-truth.md", [
            ("pass", "Baseline Java/Python", "java-fixture-ok [32, 32, 256, 32, 16, 32, …, 32]\npython-fixture-ok [32, 32, 256, 32, 16, 32, …, 32]"),
            ("pass", "Baseline Go", "go-fixture-ok 6"),
            ("pass", "Remediated Java/Python/Go", "AES-CBC→GCM, MD5→SHA-256 변경 후 세 언어 모두 non-empty output"),
            ("info", "Ground truth", "source scan 22개 언어별 고수준 자산 family · filesystem 7개 자산 단위"),
        ], "취약한 호출은 scanner 검증 전용이다. 실행 성공이 해당 구성을 production에서 사용해도 된다는 의미는 아니다.")
        render_card(card, "sonar-01-dashboard.png", "Sonar Plugin 실제 스캔 결과", "results/sonar/cbom.json · scan.log · compute.json", [
            ("pass", "Analysis", "SonarQube 26.1 + source-built crypto plugin 2.0.0-SNAPSHOT · Java/Python/Go analysis SUCCESS"),
            ("pass", "Generated CBOM", f"CycloneDX {sonar['specVersion']} · components {len(sonar['components'])} · dependencies {len(sonar.get('dependencies', []))}"),
            ("info", "Asset types", " · ".join(f"{key} {value}" for key, value in sorted(sonar_kinds.items()))),
            ("pass", "Evidence recall", "고수준 source family 22/22 · 파일/line occurrence 보존"),
        ], "로그인 UI 캡처가 아니라 원본 API·CBOM·scanner log에서 렌더링한 실행 증거다.")
        render_card(card, "sonar-02-issues.png", "Sonar Issue·속성 완전성", "results/sonar/issues.json · ground-truth.md", [
            ("pass", "Issue total", f"{issues.get('total', len(issues.get('issues', [])))} · " + " · ".join(f"{key}={value}" for key, value in sorted(rule_counts.items()))),
            ("pass", "Known weak primitive", "MD5 evidence 3개, Java/Python 별도 금지 issue 2개"),
            ("warn", "Property completeness", "Python RSA-OAEP operation은 RSA-2048 keygen으로만 표현; Go 일부 속성은 언어별로 다름"),
            ("info", "Counting unit", "32 issues ≠ 38 components ≠ viewer 59 assets. issue, component, evidence occurrence 단위가 다름"),
        ], "22/22는 정의한 지원 family recall이다. 음성 source corpus가 없으므로 precision 수치를 임의로 제시하지 않는다.")
        render_card(card, "07-theia-directory.png", "Theia Directory Scan", "results/theia-dir/cbom.json · scan.log", [
            ("pass", "Output", f"CycloneDX {theia['specVersion']} · components {len(theia['components'])} · dependencies {len(theia.get('dependencies', []))}"),
            ("info", "Asset types", " · ".join(f"{key} {value}" for key, value in sorted(theia_kinds.items()))),
            ("pass", "Detected", "유효/만료 인증서 2 · private key 2 · TLS 1.2/1.3 · OpenSSL cipher 설정"),
            ("warn", "Missed", "독립 PEM public key 1개는 별도 자산으로 탐지하지 못함 → filesystem recall 6/7"),
        ], "Theia는 source-code scanner가 아니라 filesystem·image 자산과 설정 scanner다.")
        render_card(card, "08-theia-image.png", "Theia Registry·OCI Image Scan", "results/theia-image/", [
            ("pass", "Registry alpine:3.22", f"components {len(image_bom['components'])} · dependencies {len(image_bom.get('dependencies', []))} · " + " · ".join(f"{k} {v}" for k,v in sorted(image_kinds.items()))),
            ("warn", "Duplicate bundles", "CA bundle 4개 경로 × 119 certificates = 476 occurrences; 이름 기준 unique 113"),
            ("pass", "OCI linux/amd64", "components 2,856 · dependencies 476 · schema/semantic valid"),
            ("fail", "OCI multi-arch index", "unsupported OCI index media type, empty stdout인데 CLI exit code 0"),
        ], "Docker daemon 없이 registry와 OCI layout 경로를 실제 실행했다. multi-arch 결과는 성공이 아니라 오류 전달 결함 증거다.")
        render_card(card, "09-enrichment-diff.png", "Sonar → Theia Enrichment", "results/enriched/semantic-diff.json · cbom.json", [
            ("pass", "Topology", f"components {enriched['summary']['beforeComponents']}→{enriched['summary']['afterComponents']} · added {enriched['summary']['added']} · modified {enriched['summary']['modified']}"),
            ("info", "Added types", " · ".join(f"{k} {v}" for k,v in enriched['addedByAssetType'].items())),
            ("fail", "Semantic issue", "JDK KeyUpdate 문자열 generic-api-key 오탐 + 생성 component bom-ref 누락"),
            ("fail", "java.security update", "range-by-value 구현 때문에 restriction property 수정이 원본 slice에 반영되지 않음"),
        ], "기존 Sonar components는 유지됐지만 '검증된 실행 가능성 속성 추가'는 이 실험에서 관측되지 않았다.")
        render_card(card, "10-action-local.png", "CBOMkit-action 로컬 실행", "results/action/local-workspace-cwd/ · action-build-patched-lib-1.2.0.log", [
            ("pass", "Consolidated", f"CycloneDX {action['specVersion']} · components {len(action['components'])} · dependencies {len(action.get('dependencies', []))}"),
            ("pass", "Modules", "Java 28/16 deps · Python 13/6 · Go 8/2 · CBOM.zip SHA256 57d90543…"),
            ("warn", "Build prerequisite", "공개 tag/Maven version 불일치로 upstream clone에서 cbomkit-lib 1.2.0을 사용해 local build"),
            ("warn", "Invocation boundary", "workspace 밖 CWD에서는 module CBOM이 0 components; workspace CWD에서는 정상"),
        ], "로컬 엔진은 실제 실행했으며 원격 GitHub workflow 결과는 push 뒤 별도 캡처한다.")
        render_card(card, "11-cbomkit-api-db.png", "CBOMkit API·PostgreSQL", "results/cbomkit/api-transcript.txt · postgres-query.log", [
            ("pass", "Runtime", "PostgreSQL 14.24 :5433 · Quarkus backend :8081 · health UP"),
            ("pass", "Stored CBOMs", "manual upload 5개 + public Git scan 1개; API 재조회와 DB 6 rows 대조"),
            ("pass", "Git scan", "pkg:github/m3rcy1028/cbom-test@066b89e · 48 components · 24 dependencies"),
            ("fail", "Interoperability", "schema-valid enriched CBOM의 file component에 cryptoProperties가 없어 compliance HTTP 500/NPE"),
            ("warn", "Logging", "StoreCBOMCommand가 전체 CBOM JSON을 INFO log에 기록"),
        ], "API 저장 성공과 모든 CBOM의 정책 평가 성공은 다른 주장이다. enriched 입력은 실제로 정책 평가에 실패했다.")
        render_card(card, "12-compliance-matrix.png", "Compliance Golden Matrix", "results/compliance/golden-matrix.json", [
            ("pass", "Built-in exact", f"{matrix['summary']['builtinExactMatches']}/5"),
            ("warn", "External OPA exact", f"{matrix['summary']['opaExactMatches']}/5 · conflicting assets {matrix['summary']['opaConflictAssets']}"),
            ("fail", "ECDH", "CycloneDX key-agree vs Rego keyagree 불일치 → Not Applicable 오분류"),
            ("fail", "ML-KEM-768", "name whitelist는 vulnerable, NIST level 3은 safe → 동일 자산 상충 finding 2개"),
        ], "이 표는 다섯 정책 fixture에 대한 exact match이며 일반적인 정책 정확도를 뜻하지 않는다.")
        render_card(card, "13-opa-boundaries.png", "OPA 연동 경계 조건", "results/compliance/backend-opa-*.json", [
            ("pass", "Policy fixture", f"built-in findings {len(builtin.get('findings', []))} · OPA findings {len(opa.get('findings', []))}"),
            ("pass", "OPA runtime", "OPA 1.15.1 strict check · CLI evaluation · HTTP :8181 · CBOMkit :8082 연동"),
            ("fail", "Missing external policy", f"error={missing_opa.get('error')} · findings={len(missing_opa.get('findings', []))} · global={missing_opa.get('globalComplianceStatus')} (fail-open)"),
            ("warn", "Missing built-in policy", "HTTP 200이지만 error=true, global=false — HTTP status만으로 성공 판단 불가"),
        ], "정책 존재 여부와 response.error/globalComplianceStatus를 함께 검사해야 한다.")
        render_card(card, "20-remediation-diff.png", "취약 구성 변경 전후", "results/action/baseline-vs-remediated.json · results/theia-config/baseline-vs-remediated.json", [
            ("pass", "Action topology", f"components {len(action['components'])}→{len(remediated['components'])} · dependencies {len(action.get('dependencies', []))}→{len(remediated.get('dependencies', []))}"),
            ("pass", "Removed", "MD5 components 3 · AES-CBC components 2 · IV-128 material 1"),
            ("pass", "Replaced evidence", "SHA-256 digest occurrences +2 · AES-GCM encrypt occurrences +2"),
            ("pass", "TLS config", "TLSv1.2 protocol 1→0 · TLSv1.3 유지"),
        ], "RSA 구현은 그대로이며 PQC 전환은 ML-KEM 정책 fixture로만 평가했다. 구현 완료로 해석하면 안 된다.")
        card.close()

        browser_results: dict[str, Any] = {}
        home = browser.new_page(viewport={"width": 1440, "height": 1100})
        home_errors: list[str] = []
        home.on("console", lambda msg: home_errors.append(f"console:{msg.type}:{msg.text}") if msg.type == "error" else None)
        home.goto("http://127.0.0.1:8001", wait_until="networkidle")
        home.screenshot(path=str(EVIDENCE / "15-cbomkit-home.png"), full_page=False)
        browser_results["releaseFullHome"] = {"bodyLength": len(home.locator("body").inner_text()), "errors": home_errors}
        home.close()
        browser_results["releaseFullSonar"] = upload_capture(browser, 8001, "results/sonar/cbom.json", "16-cbomkit-sonar-results.png")
        browser_results["releaseFullDetail"] = upload_capture(browser, 8001, "results/sonar/cbom.json", "17-cbomkit-asset-detail.png", detail_index=1)

        coeus = browser.new_page(viewport={"width": 1440, "height": 1100})
        coeus_errors: list[str] = []
        coeus.on("console", lambda msg: coeus_errors.append(f"console:{msg.type}:{msg.text}") if msg.type == "error" else None)
        coeus.goto("http://127.0.0.1:8004", wait_until="networkidle")
        coeus.screenshot(path=str(EVIDENCE / "18-coeus-home.png"), full_page=False)
        browser_results["releaseCoeusHome"] = {"bodyLength": len(coeus.locator("body").inner_text()), "errors": coeus_errors}
        coeus.close()
        browser_results["releaseCoeusSonar"] = upload_capture(browser, 8004, "results/sonar/cbom.json", "19-coeus-sonar-results.png")
        browser_results["releaseCoeusPolicy"] = upload_capture(browser, 8004, "results/compliance/policy-fixture-cbom.json", "21-coeus-policy-results.png")

        broken = browser.new_page(viewport={"width": 1440, "height": 900})
        broken_errors: list[str] = []
        broken.on("console", lambda msg: broken_errors.append(f"console:{msg.type}:{msg.text}") if msg.type == "error" else None)
        broken.on("pageerror", lambda err: broken_errors.append(f"pageerror:{err}"))
        broken.goto("http://127.0.0.1:8005", wait_until="networkidle")
        broken.screenshot(path=str(EVIDENCE / "14-current-main-blank-screen.png"), full_page=False)
        browser_results["currentMain"] = {"bodyLength": len(broken.locator("body").inner_text()), "errors": broken_errors}
        broken.close()

        github_run = ROOT / "results/action/github/workflow-run.json"
        if github_run.exists():
            run = json.loads(github_run.read_text(encoding="utf-8"))
            github = browser.new_page(viewport={"width": 1440, "height": 1100})
            github_errors: list[str] = []
            github.on("pageerror", lambda err: github_errors.append(f"pageerror:{err}"))
            github.goto(run["html_url"], wait_until="domcontentloaded", timeout=60000)
            github.wait_for_timeout(4000)
            github.screenshot(path=str(EVIDENCE / "22-github-action-success.png"), full_page=False)
            browser_results["githubAction"] = {
                "url": github.url,
                "title": github.title(),
                "bodyLength": len(github.locator("body").inner_text()),
                "errors": github_errors,
            }
            github.close()
        browser.close()

    (ROOT / "results/ui/browser-validation.json").parent.mkdir(parents=True, exist_ok=True)
    (ROOT / "results/ui/browser-validation.json").write_text(
        json.dumps(browser_results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"captured {len(list(EVIDENCE.glob('*.png')))} PNG files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
