#!/usr/bin/env python3
"""Upload the generated ML-KEM CBOM to IBM Zurich Viewer and capture the result."""

from __future__ import annotations

import json
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
VIEWER_URL = "https://www.zurich.ibm.com/cbom/"
CBOM_PATH = ROOT / "results/quantum-safe/action/cbom.json"
SCREENSHOT_PATH = ROOT / "evidence/23-ibm-zurich-quantum-safe.png"
RESULT_PATH = ROOT / "results/quantum-safe/viewer-validation.json"


def main() -> int:
    errors: list[str] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1100})
        page.on(
            "console",
            lambda message: errors.append(f"console:{message.type}:{message.text}")
            if message.type == "error"
            else None,
        )
        page.on("pageerror", lambda error: errors.append(f"pageerror:{error}"))
        page.goto(VIEWER_URL, wait_until="domcontentloaded", timeout=60_000)
        page.locator('input[type="file"]').set_input_files(str(CBOM_PATH))
        page.wait_for_timeout(3_000)
        body = page.locator("body").inner_text()
        mlkem_visible = "ML-KEM-768" in body
        quantum_safe_visible = "Quantum Safe" in body
        if not mlkem_visible or not quantum_safe_visible:
            raise RuntimeError(
                "Viewer did not render the expected ML-KEM-768 Quantum Safe result"
            )
        required_only = page.get_by_role("button", name="Required only")
        if required_only.is_visible():
            required_only.click()
            page.wait_for_timeout(500)
        page.screenshot(path=str(SCREENSHOT_PATH), full_page=False)
        result = {
            "viewerUrl": VIEWER_URL,
            "input": str(CBOM_PATH.relative_to(ROOT)),
            "mlKem768Visible": mlkem_visible,
            "quantumSafeVisible": quantum_safe_visible,
            "bodyExcerpt": body[:1_200],
            "errors": errors,
        }
        browser.close()

    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULT_PATH.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        "viewer-validation-ok "
        f"ml-kem-768={mlkem_visible} quantum-safe={quantum_safe_visible}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
