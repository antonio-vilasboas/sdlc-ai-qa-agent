"""Verificação cruzada da base de conhecimento contra a recolha manual (DevTools).

Garante que a página do Confluence não contém erros de transcrição:
  1. todos os seletores `data-test` documentados existem na recolha
     (os padrões `<produto>` são expandidos com os sufixos da tabela de produtos);
  2. todas as mensagens documentadas como "Texto exato" aparecem, carácter a carácter,
     num elemento recolhido;
  3. os produtos e preços documentados coincidem com os do catálogo recolhido.

Fonte de verdade: knowledge/recolha_devtools.json (recolha manual na aplicação real).
Não acede à rede.

Uso:
    python scripts/verify_kb.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
KB = ROOT / "knowledge" / "swaglabs_knowledge_base.md"
RECOLHA = ROOT / "knowledge" / "recolha_devtools.json"

# Mensagens observadas fora da consola (captura de ecrã após logout; ver 6.5 do relatório).
OBSERVED_OUTSIDE_CONSOLE: frozenset[str] = frozenset(
    {"Epic sadface: You can only access '/inventory.html' when you are logged in."}
)

_SECTION = re.compile(r"^## .+$", re.M)
_TABLE_ROW = re.compile(r"^\|(.+)\|\s*$", re.M)
_CODE = re.compile(r"`([^`]+)`")


def _rows(md: str) -> list[list[str]]:
    return [[c.strip() for c in m.group(1).split("|")] for m in _TABLE_ROW.finditer(md)]


def _sections(md: str) -> dict[str, str]:
    parts = _SECTION.split(md)
    titles = _SECTION.findall(md)
    return {t[3:].strip(): body for t, body in zip(titles, parts[1:])}


def load_recolha() -> tuple[set[str], set[str], list[tuple[str, str]]]:
    raw: dict[str, Any] = json.loads(RECOLHA.read_text(encoding="utf-8"))
    selectors: set[str] = set()
    texts: set[str] = set()
    for screen in raw.values():
        for _tag, data_test, text in screen["elementos"]:
            selectors.add(data_test)
            if text:
                texts.add(text)
    cat = raw["catalogo"]["elementos"]
    names = [t for _, dt, t in cat if dt == "inventory-item-name"]
    prices = [t for _, dt, t in cat if dt == "inventory-item-price"]
    return selectors, texts, list(zip(names, prices))


def main() -> int:
    md = KB.read_text(encoding="utf-8")
    selectors, texts, catalog = load_recolha()
    sections = _sections(md)
    errors: list[str] = []

    # Sufixos de produto documentados (tabela de produtos, 3.ª coluna)
    product_rows = [r for r in _rows(sections["3. Catálogo de Produtos"]) if len(r) == 3 and r[1].startswith("$")]
    suffixes = [_CODE.findall(r[2])[0] for r in product_rows]

    # 1. Seletores: 2.ª coluna das tabelas cujo cabeçalho é "Elemento | data-test | ..."
    #    Um padrão `<produto>` é válido se pelo menos uma expansão foi observada;
    #    as expansões não observadas são reportadas como inferidas (aviso).
    checked_selectors = 0
    warnings: list[str] = []
    for title, body in sections.items():
        rows = _rows(body)
        if not any(len(r) == 4 and r[1] == "data-test" for r in rows):
            continue
        for row in rows:
            if len(row) != 4 or row[1] in ("data-test", "---"):
                continue
            for sel in _CODE.findall(row[1]):
                if "<produto>" in sel:
                    expanded = [sel.replace("<produto>", s) for s in suffixes]
                    observed = [c for c in expanded if c in selectors]
                    checked_selectors += 1
                    if not observed:
                        errors.append(f"[{title}] padrão sem nenhuma ocorrência observada: {sel}")
                    elif len(observed) < len(expanded):
                        warnings.append(f"[{title}] padrão {sel}: observado em {len(observed)}/{len(expanded)} produtos (restantes inferidos)")
                else:
                    checked_selectors += 1
                    if sel not in selectors:
                        errors.append(f"[{title}] seletor inexistente na recolha: {sel}")

    # 2. Mensagens: 2.ª coluna das tabelas "Situação | Texto exato"
    checked_messages = 0
    for title, body in sections.items():
        if "| Texto exato |" not in body:
            continue
        for row in _rows(body):
            if len(row) != 2 or row[1] in ("Texto exato", "---"):
                continue
            msg = _CODE.findall(row[1])[0]
            checked_messages += 1
            if msg not in texts and msg not in OBSERVED_OUTSIDE_CONSOLE:
                errors.append(f"[{title}] mensagem não encontrada na recolha: {msg!r}")

    # 3. Produtos e preços
    documented = [(r[0], r[1]) for r in product_rows]
    if documented != catalog:
        errors.append(f"[Catálogo] produtos/preços divergentes: documentado={documented} recolhido={catalog}")

    print(f"Seletores verificados: {checked_selectors}")
    print(f"Mensagens verificadas: {checked_messages}")
    print(f"Produtos verificados:  {len(documented)}")
    for w in dict.fromkeys(warnings):
        print(f"⚠️  {w}")
    if errors:
        print(f"\n❌ {len(errors)} divergência(s):")
        for e in errors:
            print(f"   - {e}")
        return 1
    print("\n✅ 0 divergências entre a base de conhecimento e a recolha manual")
    return 0


if __name__ == "__main__":
    sys.exit(main())
