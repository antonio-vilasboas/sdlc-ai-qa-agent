"""Envia ao Xray os resultados da execução dos testes (relatório JUnit XML do pytest).

Uso:
    python scripts/report_xray.py QAAGENT-6 --junit results/junit.xml
    python scripts/report_xray.py QAAGENT-6 --junit results/junit.xml --evidence results/evidencias
    python scripts/report_xray.py QAAGENT-6 --junit results/junit.xml --dry-run   (só mostra o envio)

Com --evidence, a captura de ecrã final de cada teste (pytest --screenshot=on) é anexada
ao respetivo resultado no Xray como evidência.

Lê outputs/<KEY>/xray.json (função pytest → teste Xray), converte o JUnit XML para o formato
JSON do Xray e cria uma Test Execution com o estado de cada teste. Se as credenciais do
Jira estiverem disponíveis, move a User Story para "Done" (todos os testes com sucesso) ou
de volta para "In Review" (há falhas a analisar). Corre localmente ou na
pipeline do GitHub Actions; só precisa das variáveis XRAY_CLIENT_ID e XRAY_CLIENT_SECRET
(lidas do ambiente ou do .env), sem as restantes credenciais do projeto.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.sanity_check import build_session  # noqa: E402
from src.integrations.jira_board import DONE, IN_REVIEW, credentials_from_env, try_move  # noqa: E402
from src.integrations.xray_client import XrayClient, XrayError  # noqa: E402

OUTPUTS = ROOT / "outputs"
_PARAM = re.compile(r"\[.*\]$")  # pytest-playwright acrescenta [chromium] ao nome do teste


def junit_results(path: Path) -> dict[str, dict[str, Any]]:
    """{função: {status, time, message}} a partir do JUnit XML do pytest."""
    results: dict[str, dict[str, Any]] = {}
    for case in ET.parse(path).getroot().iter("testcase"):
        name = _PARAM.sub("", case.get("name", ""))
        failure = case.find("failure")
        if failure is None:
            failure = case.find("error")
        if failure is not None:
            status, message = "FAILED", (failure.get("message") or "")[:1000]
        elif case.find("skipped") is not None:
            status, message = "TODO", "ignorado na execução"
        else:
            status, message = "PASSED", ""
        results[name] = {"status": status, "time": float(case.get("time", 0)), "message": message}
    return results


def find_evidence(evidence_dir: Path | None, function: str) -> list[Path]:
    """Capturas de ecrã do pytest-playwright para uma função de teste.

    O plugin cria uma pasta por teste cujo nome contém o nome da função com hífenes
    (ex.: ...-test-c01-iniciar-checkout-chromium/test-finished-1.png).
    """
    if evidence_dir is None or not evidence_dir.is_dir():
        return []
    token = function.replace("_", "-")
    return sorted(p for d in evidence_dir.iterdir() if d.is_dir() and token in d.name for p in d.glob("*.png"))


def build_payload(key: str, mapping: dict[str, dict[str, str]], results: dict[str, dict[str, Any]],
                  run_url: str | None, evidence_dir: Path | None = None) -> tuple[dict[str, Any], list[str]]:
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    tests: list[dict[str, Any]] = []
    missing: list[str] = []
    for scenario_id, ref in sorted(mapping.items()):
        result = results.get(ref["function"])
        if result is None:
            missing.append(f"{scenario_id} ({ref['function']})")
            continue
        comment = f"{ref['function']} · {result['time']:.1f} s"
        if result["message"]:
            comment += f"\n{result['message']}"
        test: dict[str, Any] = {"testKey": ref["test_key"], "status": result["status"], "comment": comment}
        shots = find_evidence(evidence_dir, ref["function"])
        if shots:
            test["evidence"] = [
                {"data": base64.b64encode(p.read_bytes()).decode(), "filename": f"{scenario_id}_{p.name}",
                 "contentType": "image/png"}
                for p in shots
            ]
        tests.append(test)
    description = f"Execução automática dos testes gerados para {key}."
    if run_url:
        description += f" Pipeline: {run_url}"
    payload = {
        "info": {
            "summary": f"[{key}] Execução automática dos testes gerados",
            "description": description,
            "project": key.rsplit("-", 1)[0],
            "finishDate": now,
        },
        "tests": tests,
    }
    return payload, missing


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Resultados JUnit → Test Execution no Xray.")
    parser.add_argument("key", help="chave da User Story no Jira (ex.: QAAGENT-6)")
    parser.add_argument("--junit", type=Path, required=True, help="relatório JUnit XML do pytest")
    parser.add_argument("--dry-run", action="store_true", help="mostrar o envio sem o fazer")
    parser.add_argument("--evidence", type=Path, help="pasta de saída do pytest-playwright (capturas de ecrã)")
    parser.add_argument("--no-board", action="store_true", help="não mover a User Story no quadro do Jira")
    args = parser.parse_args(argv)
    load_dotenv(ROOT / ".env")

    mapping_file = OUTPUTS / args.key / "xray.json"
    if not mapping_file.exists():
        print(f"❌ {mapping_file.relative_to(ROOT)} inexistente: correr primeiro scripts/publish_tests_xray.py")
        return 1
    if not args.junit.exists():
        print(f"❌ relatório JUnit inexistente: {args.junit}")
        return 1

    mapping = json.loads(mapping_file.read_text(encoding="utf-8"))["tests"]
    results = junit_results(args.junit)
    run_url = None
    if os.getenv("GITHUB_RUN_ID"):
        run_url = f"{os.getenv('GITHUB_SERVER_URL')}/{os.getenv('GITHUB_REPOSITORY')}/actions/runs/{os.getenv('GITHUB_RUN_ID')}"
    payload, missing = build_payload(args.key, mapping, results, run_url, args.evidence)

    print(f"→ 1/2 Resultados lidos de {args.junit}")
    for t in payload["tests"]:
        shots = f" · {len(t['evidence'])} captura(s)" if t.get("evidence") else ""
        print(f"  {'✅' if t['status'] == 'PASSED' else '❌'} {t['testKey']}  {t['status']}  {t['comment'].splitlines()[0]}{shots}")
    if missing:
        print(f"  ⚠️  sem resultado no JUnit: {', '.join(missing)}")
    if not payload["tests"]:
        print("❌ nenhum resultado corresponde aos testes registados no Xray")
        return 1

    if args.dry_run:
        print("\n→ 2/2 --dry-run: conteúdo que seria enviado ao Xray (capturas omitidas)")
        preview = {**payload, "tests": [{k: v for k, v in t.items() if k != "evidence"} for t in payload["tests"]]}
        print(json.dumps(preview, ensure_ascii=False, indent=2))
        return 0

    client_id, client_secret = os.getenv("XRAY_CLIENT_ID"), os.getenv("XRAY_CLIENT_SECRET")
    if not client_id or not client_secret:
        print("❌ XRAY_CLIENT_ID e XRAY_CLIENT_SECRET não definidos")
        return 1
    http = build_session()
    xray = XrayClient(http, os.getenv("XRAY_BASE_URL", "https://xray.cloud.getxray.app"),
                      client_id, client_secret)
    print("→ 2/2 A enviar os resultados para o Xray")
    try:
        execution = xray.import_execution(payload)
    except (XrayError, requests.RequestException) as exc:
        print(f"❌ {exc}")
        return 1
    passed = sum(t["status"] == "PASSED" for t in payload["tests"])
    print(f"  ✅ Test Execution {execution.key} criada: {passed}/{len(payload['tests'])} testes com sucesso")

    board = credentials_from_env()
    if board and not args.no_board:
        all_passed = passed == len(payload["tests"]) and not missing
        try_move(http, board[0], board[1], args.key, DONE if all_passed else IN_REVIEW)
    return 0


if __name__ == "__main__":
    sys.exit(main())
