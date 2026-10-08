"""Conversão da página do Confluence (Storage Format, XHTML) em secções indexáveis.

Cada título H2 dá origem a uma secção autocontida (unidade de divisão / chunk do RAG).
O conteúdo é convertido para texto simples com tabelas em linhas "| a | b |" e código
inline entre acentos graves, preservando os seletores `data-test` tal como documentados.

Usa apenas a biblioteca padrão (html.parser) para tolerar o XHTML devolvido pelo
Confluence (atributos extra, <colgroup>, <p> dentro de células, etc.).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from html.parser import HTMLParser

_RULE_ID = re.compile(r"\bRN-[A-Z]+-\d{2}\b")
_URL_PATH = re.compile(r"URL:\s*`([^`]+)`")
_SECTION_NUMBER = re.compile(r"^(\d+)\.\s*")


@dataclass(frozen=True)
class Section:
    """Secção da base de conhecimento, pronta a indexar."""

    number: int
    title: str
    text: str
    rule_ids: tuple[str, ...] = field(default_factory=tuple)
    url_path: str | None = None

    @property
    def is_traceability(self) -> bool:
        """Secção de rastreabilidade: gabarito da avaliação, nunca entregue aos agentes."""
        return "Rastreabilidade" in self.title

    @property
    def chunk_id(self) -> str:
        return f"kb-s{self.number:02d}"

    @property
    def content(self) -> str:
        """Texto completo da secção, com o título (o que é embebido e devolvido ao agente)."""
        return f"## {self.title}\n{self.text}"


class _StorageToText(HTMLParser):
    _BLOCKS = frozenset({"p", "div", "ul", "ol", "table", "tbody", "thead", "br"})

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.sections: list[tuple[str, list[str]]] = []
        self._title_buf: list[str] | None = None
        self._buf: list[str] = []
        self._cells: list[str] | None = None
        self._cell_buf: list[str] | None = None

    # -- utilitários ---------------------------------------------------------
    def _out(self) -> list[str]:
        if self._title_buf is not None:
            return self._title_buf
        if self._cell_buf is not None:
            return self._cell_buf
        return self._buf

    def _newline(self) -> None:
        if self._cell_buf is None and self._title_buf is None and self._buf and self._buf[-1] != "\n":
            self._buf.append("\n")

    def _flush_section(self) -> None:
        if self.sections:
            self.sections[-1][1].extend(self._buf)
        self._buf = []

    # -- eventos do parser -----------------------------------------------------
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "h2":
            self._flush_section()
            self._title_buf = []
        elif tag == "tr":
            self._newline()
            self._cells = []
        elif tag in ("td", "th"):
            self._cell_buf = []
        elif tag == "li":
            self._newline()
            self._out().append("- ")
        elif tag == "code":
            self._out().append("`")
        elif tag in self._BLOCKS:
            self._newline()

    def handle_endtag(self, tag: str) -> None:
        if tag == "h2" and self._title_buf is not None:
            self.sections.append(("".join(self._title_buf).strip(), []))
            self._title_buf = None
        elif tag in ("td", "th") and self._cell_buf is not None and self._cells is not None:
            self._cells.append(re.sub(r"\s+", " ", "".join(self._cell_buf)).strip())
            self._cell_buf = None
        elif tag == "tr" and self._cells is not None:
            self._buf.append("| " + " | ".join(self._cells) + " |")
            self._buf.append("\n")
            self._cells = None
        elif tag == "code":
            self._out().append("`")
        elif tag in ("p", "li"):
            self._newline()

    def handle_data(self, data: str) -> None:
        self._out().append(data)

    def close(self) -> None:
        super().close()
        self._flush_section()


def parse_storage(xhtml: str) -> list[Section]:
    """Divide o XHTML da página em secções (uma por H2)."""
    parser = _StorageToText()
    parser.feed(xhtml)
    parser.close()

    sections: list[Section] = []
    for title, parts in parser.sections:
        match = _SECTION_NUMBER.match(title)
        if not match:
            raise ValueError(f"título de secção sem numeração: {title!r}")
        text = "\n".join(line.strip() for line in "".join(parts).splitlines() if line.strip())
        url = _URL_PATH.search(text)
        sections.append(
            Section(
                number=int(match.group(1)),
                title=title,
                text=text,
                rule_ids=tuple(dict.fromkeys(_RULE_ID.findall(text))),
                url_path=url.group(1) if url else None,
            )
        )
    if not sections:
        raise ValueError("nenhuma secção H2 encontrada na página")
    return sections


def traceability(sections: list[Section]) -> dict[str, set[int]]:
    """Lê a secção de rastreabilidade: {"QAAGENT-1": {1, 2, 3}, ...}."""
    trace = next((s for s in sections if s.is_traceability), None)
    if trace is None:
        raise ValueError("secção de rastreabilidade não encontrada")
    mapping: dict[str, set[int]] = {}
    for line in trace.text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and re.fullmatch(r"QAAGENT-\d+", cells[0]):
            mapping[cells[0]] = {int(n) for n in re.findall(r"\d+", cells[1])}
    if not mapping:
        raise ValueError("tabela de rastreabilidade vazia")
    return mapping
