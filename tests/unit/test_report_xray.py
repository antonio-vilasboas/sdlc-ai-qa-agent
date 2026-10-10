"""Testes unitários da conversão JUnit XML → formato JSON do Xray (sem rede).

Executar: pytest tests/unit -v
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.report_xray import build_payload, junit_results  # noqa: E402

JUNIT = """<?xml version="1.0" encoding="utf-8"?>
<testsuites><testsuite name="pytest" tests="3">
  <testcase classname="test_qaagent_6" name="test_c01_login[chromium]" time="1.5"/>
  <testcase classname="test_qaagent_6" name="test_c02_resumo[chromium]" time="2.0">
    <failure message="AssertionError: Locator expected to have text 'Total: $32.39'">trace</failure>
  </testcase>
  <testcase classname="test_qaagent_6" name="test_c03_extra[chromium]" time="0.1"><skipped/></testcase>
</testsuite></testsuites>"""

MAPPING = {
    "C01": {"test_key": "QAAGENT-7", "issue_id": "1", "function": "test_c01_login"},
    "C02": {"test_key": "QAAGENT-8", "issue_id": "2", "function": "test_c02_resumo"},
    "C04": {"test_key": "QAAGENT-10", "issue_id": "4", "function": "test_c04_inexistente"},
}


def test_junit_remove_parametro_do_browser_e_classifica_estados(tmp_path: Path) -> None:
    f = tmp_path / "junit.xml"
    f.write_text(JUNIT, encoding="utf-8")
    r = junit_results(f)
    assert r["test_c01_login"]["status"] == "PASSED"
    assert r["test_c02_resumo"]["status"] == "FAILED"
    assert "Total: $32.39" in r["test_c02_resumo"]["message"]
    assert r["test_c03_extra"]["status"] == "TODO"


def test_payload_usa_chaves_xray_e_assinala_testes_sem_resultado(tmp_path: Path) -> None:
    f = tmp_path / "junit.xml"
    f.write_text(JUNIT, encoding="utf-8")
    payload, missing = build_payload("QAAGENT-6", MAPPING, junit_results(f), run_url="https://ci/run/1")
    assert [(t["testKey"], t["status"]) for t in payload["tests"]] == [("QAAGENT-7", "PASSED"), ("QAAGENT-8", "FAILED")]
    assert missing == ["C04 (test_c04_inexistente)"]
    assert "https://ci/run/1" in payload["info"]["description"]
