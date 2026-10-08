"""Extração empírica do inventário de seletores e regras do Swag Labs.

Percorre a aplicação real com Playwright (headless) e regista, por ecrã:
  - todos os elementos com atributo `data-test` (tag, valor, texto visível);
  - mensagens de erro exatamente como surgem na interface;
  - comportamento observado (ordenação, contador do carrinho, cálculo da taxa).

O resultado (knowledge/swaglabs_dom_inventory.json) é a matéria-prima da página de
Confluence que alimenta o RAG. Nenhum seletor é escrito à mão: a navegação usa apenas
localizadores por papel/texto acessível (get_by_role / get_by_placeholder) e os
seletores registados são os que o próprio DOM expõe.

Uso:
    python scripts/extract_dom_inventory.py            # headless
    python scripts/extract_dom_inventory.py --headed   # ver o browser (WSLg)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from playwright.sync_api import Browser, Page, sync_playwright
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeout

BASE_URL = "https://www.saucedemo.com/"
OUTPUT = Path(__file__).resolve().parent.parent / "knowledge" / "swaglabs_dom_inventory.json"
TIMEOUT_MS = 10_000

Snapshot = list[dict[str, Any]]

# JavaScript executado no browser: lista todos os elementos com data-test.
_SNAPSHOT_JS = """
els => els.map(e => ({
  data_test: e.getAttribute('data-test'),
  tag: e.tagName.toLowerCase(),
  id: e.id || null,
  type: e.getAttribute('type'),
  placeholder: e.getAttribute('placeholder'),
  text: (e.innerText || e.value || '').trim().replace(/\\s+/g, ' ').slice(0, 120),
  visible: !!(e.offsetWidth || e.offsetHeight || e.getClientRects().length)
}))
"""


class Inventory:
    """Acumula o que é observado em cada ecrã e os avisos de passos falhados."""

    def __init__(self) -> None:
        self.screens: dict[str, dict[str, Any]] = {}
        self.messages: dict[str, str] = {}
        self.behaviour: dict[str, Any] = {}
        self.warnings: list[str] = []

    def capture(self, page: Page, screen: str, description: str) -> Snapshot:
        elements: Snapshot = page.eval_on_selector_all("[data-test]", _SNAPSHOT_JS)
        unique: dict[str, dict[str, Any]] = {}
        for el in elements:
            unique.setdefault(el["data_test"], el)  # mantém a 1.ª ocorrência de cada valor
        self.screens[screen] = {
            "url_path": page.url.replace(BASE_URL.rstrip("/"), "") or "/",
            "description": description,
            "elements": list(unique.values()),
        }
        return elements

    def step(self, name: str, fn: Callable[[], None]) -> None:
        """Executa um passo; uma falha fica registada e não interrompe a extração."""
        try:
            fn()
            print(f"  ✅ {name}")
        except (PlaywrightError, PlaywrightTimeout, ValueError, IndexError, KeyError, StopIteration) as exc:
            msg = f"{name}: {exc.__class__.__name__}: {str(exc).splitlines()[0]}"
            self.warnings.append(msg)
            print(f"  ⚠️  {msg}")


# --------------------------------------------------------------------------- #
# Utilitários
# --------------------------------------------------------------------------- #
def _texts(snapshot: Snapshot, contains: str, exclude: str | None = None) -> list[str]:
    """Textos dos elementos cujo data-test contém `contains` (e não contém `exclude`)."""
    return [
        e["text"]
        for e in snapshot
        if contains in (dt := e["data_test"] or "") and (exclude is None or exclude not in dt) and e["text"]
    ]


def _snapshot(page: Page) -> Snapshot:
    return page.eval_on_selector_all("[data-test]", _SNAPSHOT_JS)


def _error_text(page: Page) -> str:
    """Lê a mensagem de erro visível (o elemento é localizado pelo próprio snapshot)."""
    errors = [e for e in _snapshot(page) if e["visible"] and "error" in e["data_test"] and e["text"]]
    if not errors:
        raise ValueError("nenhum elemento de erro visível")
    return errors[0]["text"]


def _money(text: str) -> float:
    match = re.search(r"\$\s*([\d.]+)", text)
    if not match:
        raise ValueError(f"valor monetário não encontrado em '{text}'")
    return float(match.group(1))


def _login(page: Page, user: str, password: str) -> None:
    page.goto(BASE_URL)
    page.get_by_placeholder("Username").fill(user)
    page.get_by_placeholder("Password").fill(password)
    page.get_by_role("button", name="Login").click()


# --------------------------------------------------------------------------- #
# Percurso pela aplicação
# --------------------------------------------------------------------------- #
def crawl(browser: Browser, inv: Inventory) -> None:
    page = browser.new_page()
    page.set_default_timeout(TIMEOUT_MS)
    creds: dict[str, Any] = {}

    def login_page() -> None:
        page.goto(BASE_URL)
        snap = inv.capture(page, "login", "Página de autenticação (ponto de entrada da aplicação)")
        users = _texts(snap, "login-credentials")
        pwd = _texts(snap, "login-password")
        if users:
            creds["usernames"] = [u for u in re.split(r"\s+", users[0]) if u.endswith("_user")]
        if pwd:
            creds["password"] = pwd[0].split()[-1]
        if not creds.get("usernames") or not creds.get("password"):
            raise ValueError("credenciais de teste não encontradas na página de login")
        inv.behaviour["test_credentials"] = creds

    def login_errors() -> None:
        page.goto(BASE_URL)
        page.get_by_role("button", name="Login").click()
        inv.messages["login_username_required"] = _error_text(page)

        page.goto(BASE_URL)
        page.get_by_placeholder("Username").fill(creds["usernames"][0])
        page.get_by_role("button", name="Login").click()
        inv.messages["login_password_required"] = _error_text(page)

        page.goto(BASE_URL)
        page.get_by_placeholder("Username").fill(creds["usernames"][0])
        page.get_by_placeholder("Password").fill("password_errada")
        page.get_by_role("button", name="Login").click()
        inv.messages["login_invalid_credentials"] = _error_text(page)

        locked = next((u for u in creds["usernames"] if "locked" in u), None)
        if not locked:
            raise ValueError("utilizador bloqueado não listado na página de login")
        _login(page, locked, creds["password"])
        inv.messages["login_locked_out"] = _error_text(page)
        inv.capture(page, "login_error", "Página de autenticação com mensagem de erro visível")

    def inventory_page() -> None:
        standard = next(u for u in creds["usernames"] if u.startswith("standard"))
        _login(page, standard, creds["password"])
        page.wait_for_url("**/inventory.html")
        snap = inv.capture(page, "inventory", "Catálogo de produtos (após autenticação)")
        names, prices = _texts(snap, "inventory-item-name"), _texts(snap, "inventory-item-price")
        inv.behaviour["products"] = [{"name": n, "price": p} for n, p in zip(names, prices)]
        inv.behaviour["default_order"] = names

    def sorting() -> None:
        select = page.get_by_role("combobox")
        options = select.locator("option").evaluate_all("os => os.map(o => ({value: o.value, label: o.text}))")
        results: dict[str, Any] = {}
        for opt in options:
            select.select_option(opt["value"])
            snap = _snapshot(page)
            results[opt["value"]] = {
                "label": opt["label"],
                "names": _texts(snap, "inventory-item-name"),
                "prices": _texts(snap, "inventory-item-price"),
            }
        inv.behaviour["sort_options"] = results
        select.select_option(options[0]["value"])

    def cart() -> None:
        add_buttons = page.get_by_role("button", name="Add to cart")
        add_buttons.nth(0).click()
        snap1 = _snapshot(page)
        add_buttons.nth(0).click()  # o 1.º passou a "Remove": nth(0) é agora o 2.º produto
        snap2 = _snapshot(page)
        inv.behaviour["cart_badge_after_1"] = _texts(snap1, "shopping-cart-badge")
        inv.behaviour["cart_badge_after_2"] = _texts(snap2, "shopping-cart-badge")
        inv.capture(page, "inventory_with_cart", "Catálogo com dois produtos adicionados (botões passam a 'Remove')")

        # O contador é descoberto no snapshot (não é assumido); clicar nele abre o carrinho.
        badge = next(e["data_test"] for e in snap2 if "cart-badge" in e["data_test"])
        page.locator(f"[data-test='{badge}']").click()
        page.wait_for_url("**/cart.html")
        inv.capture(page, "cart", "Carrinho de compras")

        page.get_by_role("button", name="Remove").first.click()
        snap3 = _snapshot(page)
        inv.behaviour["cart_badge_after_remove"] = _texts(snap3, "shopping-cart-badge")
        inv.behaviour["cart_items_after_remove"] = _texts(snap3, "inventory-item-name")

    def checkout() -> None:
        page.get_by_role("button", name="Checkout").click()
        page.wait_for_url("**/checkout-step-one.html")
        inv.capture(page, "checkout_information", "Checkout passo 1: informação do cliente")

        page.get_by_role("button", name="Continue").click()
        inv.messages["checkout_first_name_required"] = _error_text(page)
        page.get_by_placeholder("First Name").fill("Ana")
        page.get_by_role("button", name="Continue").click()
        inv.messages["checkout_last_name_required"] = _error_text(page)
        page.get_by_placeholder("Last Name").fill("Silva")
        page.get_by_role("button", name="Continue").click()
        inv.messages["checkout_postal_code_required"] = _error_text(page)

        page.get_by_placeholder("Zip/Postal Code").fill("6000-767")
        page.get_by_role("button", name="Continue").click()
        page.wait_for_url("**/checkout-step-two.html")
        snap = inv.capture(page, "checkout_overview", "Checkout passo 2: resumo da encomenda")

        subtotal = _money(_texts(snap, "subtotal")[0])
        tax = _money(_texts(snap, "tax")[0])
        total = _money(_texts(snap, "total-label", exclude="sub")[0])
        inv.behaviour["checkout_amounts"] = {
            "subtotal": subtotal,
            "tax": tax,
            "total": total,
            "tax_rate_observed": round(tax / subtotal, 4),
            "total_equals_subtotal_plus_tax": round(subtotal + tax, 2) == round(total, 2),
        }

        page.get_by_role("button", name="Finish").click()
        page.wait_for_url("**/checkout-complete.html")
        snap = inv.capture(page, "checkout_complete", "Checkout concluído: confirmação da encomenda")
        inv.messages["checkout_complete_header"] = (_texts(snap, "complete-header") or [""])[0]
        inv.messages["checkout_complete_text"] = (_texts(snap, "complete-text") or [""])[0]

    def menu_and_logout() -> None:
        page.get_by_role("button", name="Open Menu").click()
        page.get_by_role("link", name="Logout").wait_for(state="visible")
        inv.capture(page, "side_menu", "Menu lateral aberto")
        page.get_by_role("link", name="Logout").click()
        page.wait_for_url(BASE_URL)
        page.goto(BASE_URL + "inventory.html")
        inv.messages["access_without_session"] = _error_text(page)
        inv.behaviour["access_without_session_redirects_to"] = page.url.replace(BASE_URL.rstrip("/"), "") or "/"

    for name, fn in (
        ("Página de login e credenciais de teste", login_page),
        ("Mensagens de erro do login", login_errors),
        ("Catálogo de produtos", inventory_page),
        ("Opções de ordenação", sorting),
        ("Carrinho (adicionar / remover)", cart),
        ("Checkout completo e validações", checkout),
        ("Menu lateral, logout e acesso sem sessão", menu_and_logout),
    ):
        inv.step(name, fn)
    page.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extrai o inventário de seletores do Swag Labs.")
    parser.add_argument("--headed", action="store_true", help="mostra o browser durante a extração")
    args = parser.parse_args(argv)

    inv = Inventory()
    print(f"→ A percorrer {BASE_URL}")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=not args.headed, slow_mo=300 if args.headed else 0)
        try:
            crawl(browser, inv)
        finally:
            browser.close()

    result = {
        "source": BASE_URL,
        "extracted_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "screens": inv.screens,
        "messages": inv.messages,
        "behaviour": inv.behaviour,
        "warnings": inv.warnings,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    n_selectors = sum(len(s["elements"]) for s in inv.screens.values())
    print(f"\n✅ {len(inv.screens)} ecrãs · {n_selectors} seletores data-test · {len(inv.messages)} mensagens")
    print(f"   → {OUTPUT.relative_to(Path.cwd()) if OUTPUT.is_relative_to(Path.cwd()) else OUTPUT}")
    if inv.warnings:
        print(f"⚠️  {len(inv.warnings)} passo(s) com aviso — rever antes de publicar no Confluence")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
