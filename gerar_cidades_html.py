# -*- coding: utf-8 -*-
"""Gera HTML: Cidades criadas + Especialidades por cidade + Exames por cidade."""
from __future__ import annotations

import html
import json
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook, load_workbook

BASE = Path(__file__).resolve().parent
EXAMES_JSON = BASE / "lista_exames.json"
EXAMES_PLAN_XLSX = BASE / "exames_por_cidade_pendentes.xlsx"
EXAMES_CRIADOS = True  # 38 cidades × 31 exames já gerados

# Especialidades removidas da tabela da unidade (ficam na lista em vermelho).
INDAIATUBA_REMOVIDAS = {
    "gastro",
    "gastroenterologista",
    "gastroenterologia",
    "neurologia",
    "neurologista",
    "nefrologista",
    "mastologia",
    "mastologista",
    "nutricionista",
    "pediatria",
    "pediatra",
    "psicologia",
    "psicologo",
    "neuropsicologia",
    "neuropsicologo",
    "proctologista",
}
INDAIATUBA_EXTRA_REMOVIDAS = [
    ("Mastologia", {"mastologia", "mastologista"}),
    ("Pediatria", {"pediatria", "pediatra"}),
    ("Neuropsicologia", {"neuropsicologia", "neuropsicologo"}),
]

# Especialidades adicionadas só em Campinas (fora do padrão das outras unidades).
CAMPINAS_ADICIONADAS = [
    ("Clínico Geral", "clinico-geral-em-campinas"),
    ("Infectologista", "infectologista-em-campinas"),
]

# Em Juazeiro, só estas permanecem ativas; o restante fica em vermelho.
JUAZEIRO_ATIVAS = {
    "oftalmologia",
    "oftalmologista",
    "ginecologia",
    "ginecologista",
    "clinico geral",
    "psiquiatria",
    "psiquiatra",
    "cardiologia",
    "cardiologista",
    "dermatologia",
    "dermatologista",
    "gastroenterologia",
    "gastroenterologista",
    "nutricionista",
    "endocrinologia",
    "endocrinologista",
    "ultrassom",
    "ultrassom doppler",
    "ultrassonografia doppler",
    "exames laboratoriais",
}
JUAZEIRO_EXTRA_ATIVAS = [
    ("Clínico Geral", "clinico-geral-em-juazeiro-do-norte"),
    ("Exames Laboratoriais", "exames-laboratoriais-em-juazeiro-do-norte"),
]


def norm_label(text: str) -> str:
    raw = unicodedata.normalize("NFKD", text or "")
    raw = "".join(c for c in raw if not unicodedata.combining(c))
    return " ".join(raw.lower().replace("-", " ").split())


def load_sheet(path: Path, sheet: str | None = None) -> list[dict]:
    wb = load_workbook(path, data_only=True)
    ws = wb[sheet] if sheet else wb.active
    headers = [c.value for c in ws[1]]
    rows = []
    for values in ws.iter_rows(min_row=2, values_only=True):
        if not values or values[0] is None:
            continue
        rows.append({headers[i]: values[i] for i in range(len(headers))})
    return rows


def load_exames() -> list[dict]:
    if not EXAMES_JSON.exists():
        return []
    payload = json.loads(EXAMES_JSON.read_text(encoding="utf-8"))
    return list(payload.get("exames") or [])


def status_kind(status: str) -> str:
    text = (status or "").strip().lower()
    if "conclu" in text:
        return "ok"
    if "sem url" in text or "no site" in text:
        return "warn"
    return "pend"


def status_label(status: str) -> str:
    kind = status_kind(status)
    if kind == "ok":
        return "Criada"
    if kind == "warn":
        return "No site / sem unidade"
    return "Pendente"


def slugify_city(cidade: str) -> str:
    text = unicodedata.normalize("NFKD", cidade)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower().strip()
    out = []
    for ch in text:
        if ch.isalnum():
            out.append(ch)
        elif ch in {" ", "-", "'"}:
            out.append("-")
    slug = "".join(out)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-")


def save_exames_plan(cidades_ok: list[dict], exames: list[dict]) -> None:
    """Registra matriz cidade × exame (pendente) para criação futura."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Pendentes"
    ws.append(
        [
            "cidade",
            "uf",
            "exame",
            "slug_exame",
            "url_exame_nacional",
            "slug_pagina_sugerido",
            "status",
        ]
    )
    for cidade_row in cidades_ok:
        cidade = str(cidade_row.get("Cidade") or "")
        uf = str(cidade_row.get("UF") or "")
        city_slug = slugify_city(cidade)
        for ex in exames:
            exam_slug = str(ex.get("slug") or "")
            ws.append(
                [
                    cidade,
                    uf,
                    ex.get("nome"),
                    exam_slug,
                    ex.get("url"),
                    f"{exam_slug}-em-{city_slug}",
                    "criado" if EXAMES_CRIADOS else "pendente_criacao",
                ]
            )
    wb.save(EXAMES_PLAN_XLSX)


def chip_esp(label: str, link: str = "", kind: str = "ok") -> str:
    """kind: ok | removed | added"""
    cls = "chip"
    title = ""
    if kind == "removed":
        cls += " chip-removido"
        title = ' title="Removida da tabela da unidade"'
    elif kind == "added":
        cls += " chip-add"
        title = ' title="Adicionada fora do padrão das outras unidades"'
    safe = html.escape(label)
    if link and kind != "removed":
        return (
            f'<a class="{cls}" href="{html.escape(link)}" target="_blank" '
            f'rel="noopener"{title}>{safe}</a>'
        )
    return f'<span class="{cls}"{title}>{safe}</span>'


def match_any(label: str, keys: set[str]) -> bool:
    n = norm_label(label)
    if n in keys:
        return True
    parts = set(n.split())
    for k in keys:
        if len(k) < 5:
            if n == k:
                return True
            continue
        if k == n or n.startswith(k + " ") or k in parts:
            return True
    return False


def main() -> Path:
    cidades = load_sheet(BASE / "lista_cidades_estados.xlsx", "Cidades")
    urls = load_sheet(BASE / "lista_todas_urls.xlsx", "URLs")
    exames = load_exames()

    paginas_esp = Counter(str(r.get("cidade") or "").strip() for r in urls)
    por_cidade: dict[str, list[dict]] = defaultdict(list)
    for row in urls:
        cidade = str(row.get("cidade") or "").strip()
        if cidade:
            por_cidade[cidade].append(row)

    total = len(cidades)
    feitas = sum(1 for r in cidades if status_kind(str(r.get("Status SEO") or "")) == "ok")
    pendentes = sum(1 for r in cidades if status_kind(str(r.get("Status SEO") or "")) == "pend")
    extra = sum(1 for r in cidades if status_kind(str(r.get("Status SEO") or "")) == "warn")
    cidades_ok = [r for r in cidades if status_kind(str(r.get("Status SEO") or "")) == "ok"]
    n_exames = len(exames)
    n_cidades_ok = len(cidades_ok)
    n_paginas_exames = n_exames * n_cidades_ok if EXAMES_CRIADOS else 0
    total_paginas_esp = sum(paginas_esp.values())
    total_paginas = total_paginas_esp + n_paginas_exames
    generated = datetime.now().strftime("%d/%m/%Y %H:%M")

    if exames and cidades_ok:
        save_exames_plan(cidades_ok, exames)

    body_cidades = []
    for r in cidades:
        cidade = str(r.get("Cidade") or "")
        uf = str(r.get("UF") or "")
        estado = str(r.get("Estado") or "")
        qtd = r.get("Qtd unidades") or 0
        status = str(r.get("Status SEO") or "")
        url = str(r.get("URL exemplo") or "").strip()
        kind = status_kind(status)
        n_esp = paginas_esp.get(cidade, 0)
        n_exam = n_exames if (kind == "ok" and EXAMES_CRIADOS) else 0
        n_pag = n_esp + n_exam
        pag_txt = str(n_pag) if n_pag else "—"
        cidade_link = (
            f'<a href="{html.escape(url)}" target="_blank" rel="noopener">{html.escape(cidade)}</a>'
            if url
            else html.escape(cidade)
        )
        kind_sort = {"ok": "2", "pend": "1", "warn": "0"}.get(kind, "0")
        body_cidades.append(
            f"""<tr class="{kind}">
  <td class="cidade" data-sort="{html.escape(cidade)}">{cidade_link}</td>
  <td data-sort="{html.escape(uf)}">{html.escape(uf)}</td>
  <td data-sort="{html.escape(estado)}">{html.escape(estado)}</td>
  <td class="num" data-sort="{qtd}">{qtd}</td>
  <td class="num" data-sort="{n_pag}">{pag_txt}</td>
  <td data-sort="{kind_sort}"><span class="badge {kind}">{status_label(status)}</span></td>
</tr>"""
        )

    uf_by_city = {str(r.get("Cidade") or ""): str(r.get("UF") or "") for r in cidades}
    body_esp = []
    for cidade in sorted(por_cidade, key=lambda s: s.lower()):
        rows_esp = sorted(
            por_cidade[cidade],
            key=lambda r: str(r.get("especialidade") or "").lower(),
        )
        uf = uf_by_city.get(cidade, "")
        exemplo = next((str(r.get("url") or "") for r in rows_esp if r.get("url")), "")
        cidade_link = (
            f'<a href="{html.escape(exemplo)}" target="_blank" rel="noopener">{html.escape(cidade)}</a>'
            if exemplo
            else html.escape(cidade)
        )
        chips = []
        labels_present = set()
        for r in rows_esp:
            esp = str(r.get("especialidade") or "").strip()
            link = str(r.get("url") or "").strip()
            if not esp:
                continue
            labels_present.add(norm_label(esp))
            kind_chip = "ok"
            if cidade == "Indaiatuba" and match_any(esp, INDAIATUBA_REMOVIDAS):
                kind_chip = "removed"
            elif cidade == "Campinas" and match_any(
                esp, {norm_label(x[0]) for x in CAMPINAS_ADICIONADAS}
            ):
                kind_chip = "added"
            elif cidade == "Juazeiro do Norte" and not match_any(esp, JUAZEIRO_ATIVAS):
                kind_chip = "removed"
            chips.append(chip_esp(esp, link, kind_chip))

        if cidade == "Indaiatuba":
            for extra, aliases in INDAIATUBA_EXTRA_REMOVIDAS:
                if not (labels_present & aliases):
                    chips.append(chip_esp(extra, "", "removed"))
                    labels_present.add(norm_label(extra))
        if cidade == "Campinas":
            for label, slug in CAMPINAS_ADICIONADAS:
                if norm_label(label) not in labels_present:
                    link = f"https://www.clinicadacidade.com.br/centro/{slug}/"
                    chips.append(chip_esp(label, link, "added"))
                    labels_present.add(norm_label(label))
        if cidade == "Juazeiro do Norte":
            for label, slug in JUAZEIRO_EXTRA_ATIVAS:
                if norm_label(label) not in labels_present:
                    link = f"https://www.clinicadacidade.com.br/centro/{slug}/"
                    chips.append(chip_esp(label, link, "ok"))
                    labels_present.add(norm_label(label))

        # Ordena chips pelo texto visível
        chips_sorted = sorted(
            chips,
            key=lambda c: re.sub(r"<[^>]+>", "", c).lower(),
        )
        n = len(chips_sorted)
        search_names = re.findall(r">([^<]+)<", "".join(chips_sorted))
        search_blob = html.escape(" ".join([cidade, uf] + search_names).lower())
        body_esp.append(
            f"""<tr data-search="{search_blob}">
  <td class="cidade" data-sort="{html.escape(cidade)}">{cidade_link}</td>
  <td data-sort="{html.escape(uf)}">{html.escape(uf)}</td>
  <td class="num" data-sort="{n}">{n}</td>
  <td data-sort="{n}"><div class="chips">{''.join(chips_sorted)}</div></td>
</tr>"""
        )

    exam_chip_cls = "chip" if EXAMES_CRIADOS else "chip chip-pend"
    exam_chips_catalog = []
    for ex in exames:
        nome = str(ex.get("nome") or "")
        link = str(ex.get("url") or "")
        if link:
            exam_chips_catalog.append(
                f'<a class="{exam_chip_cls}" href="{html.escape(link)}" target="_blank" rel="noopener">{html.escape(nome)}</a>'
            )
        else:
            exam_chips_catalog.append(f'<span class="{exam_chip_cls}">{html.escape(nome)}</span>')

    body_exames = []
    for r in sorted(cidades_ok, key=lambda x: str(x.get("Cidade") or "").lower()):
        cidade = str(r.get("Cidade") or "")
        uf = str(r.get("UF") or "")
        url = str(r.get("URL exemplo") or "").strip()
        cidade_link = (
            f'<a href="{html.escape(url)}" target="_blank" rel="noopener">{html.escape(cidade)}</a>'
            if url
            else html.escape(cidade)
        )
        city_slug = slugify_city(cidade)
        chips = []
        for ex in exames:
            nome = str(ex.get("nome") or "")
            exam_slug = str(ex.get("slug") or "")
            if EXAMES_CRIADOS and exam_slug:
                page = f"https://www.clinicadacidade.com.br/centro/{exam_slug}-em-{city_slug}/"
                chips.append(
                    f'<a class="chip" href="{html.escape(page)}" target="_blank" rel="noopener" title="Criado">{html.escape(nome)}</a>'
                )
            else:
                chips.append(
                    f'<span class="chip chip-pend" title="Pendente de criação">{html.escape(nome)}</span>'
                )
        search_blob = html.escape(
            " ".join([cidade, uf] + [str(e.get("nome") or "") for e in exames]).lower()
        )
        if EXAMES_CRIADOS:
            status_cell = '<span class="badge ok">Criado</span>'
            status_sort = "2"
        else:
            status_cell = '<span class="badge pend">Pendente criação</span>'
            status_sort = "0"
        body_exames.append(
            f"""<tr data-search="{search_blob}">
  <td class="cidade" data-sort="{html.escape(cidade)}">{cidade_link}</td>
  <td data-sort="{html.escape(uf)}">{html.escape(uf)}</td>
  <td class="num" data-sort="{n_exames}">{n_exames}</td>
  <td data-sort="{status_sort}">{status_cell}</td>
  <td data-sort="{n_exames}"><div class="chips">{''.join(chips)}</div></td>
</tr>"""
        )

    out = BASE / "cidades_paginas.html"
    out.write_text(
        f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cidades, especialidades e exames — Clínica da Cidade</title>
<style>
  :root {{
    --bg: #f3f6f5; --card: #fff; --ink: #14221f; --muted: #5d6e6a; --line: #dde7e4; --teal: #0f766e;
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; font-family: "Segoe UI", Arial, sans-serif; background: var(--bg); color: var(--ink); }}
  header {{ background: #0f766e; color: #fff; padding: 28px 20px; }}
  header h1 {{ margin: 0 0 6px; font-size: 1.45rem; }}
  header p {{ margin: 0; opacity: .92; }}
  .wrap {{ max-width: 1180px; margin: 0 auto; padding: 18px; }}
  .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin: 16px 0; }}
  .card {{ background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 14px; }}
  .card .k {{ font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; }}
  .card .v {{ font-size: 1.5rem; font-weight: 700; margin-top: 4px; }}
  .filters {{ display: flex; gap: 8px; flex-wrap: wrap; margin: 0 0 12px; }}
  input[type=search] {{ flex: 1; min-width: 200px; padding: 10px 12px; border: 1px solid var(--line); border-radius: 8px; font-size: 14px; }}
  button {{ border: 1px solid var(--line); background: #fff; border-radius: 8px; padding: 10px 12px; cursor: pointer; font-size: 13px; }}
  button.active {{ background: #0f766e; color: #fff; border-color: #0f766e; }}
  .tabs {{ display: flex; gap: 0; margin: 0 0 16px; border-bottom: 2px solid var(--line); flex-wrap: wrap; }}
  .tabs button {{ border: none; border-radius: 0; background: transparent; padding: 12px 18px; font-size: 14px; font-weight: 600; color: var(--muted); }}
  .tabs button.active {{ background: transparent; color: var(--teal); border-bottom: 2px solid var(--teal); margin-bottom: -2px; }}
  .panel {{ display: none; }}
  .panel.active {{ display: block; }}
  table {{ width: 100%; border-collapse: collapse; background: var(--card); border: 1px solid var(--line); border-radius: 12px; overflow: hidden; }}
  th, td {{ padding: 11px 12px; text-align: left; border-bottom: 1px solid var(--line); font-size: 14px; vertical-align: top; }}
  th {{ background: #ecf5f3; font-size: 12px; text-transform: uppercase; letter-spacing: .03em; color: #345; }}
  th.sortable {{ cursor: pointer; user-select: none; white-space: nowrap; }}
  th.sortable:hover {{ background: #dceae6; }}
  th.sortable::after {{ content: " \\2195"; opacity: .35; font-size: 11px; }}
  th.asc::after {{ content: " \\2191"; opacity: 1; }}
  th.desc::after {{ content: " \\2193"; opacity: 1; }}
  .cidade {{ font-weight: 700; white-space: nowrap; }}
  .cidade a {{ color: inherit; text-decoration: none; }}
  .cidade a:hover {{ color: var(--teal); text-decoration: underline; }}
  .num {{ font-variant-numeric: tabular-nums; }}
  .badge {{ display: inline-block; padding: 3px 8px; border-radius: 999px; font-size: 12px; font-weight: 600; white-space: nowrap; }}
  .ok {{ background: #d1fae5; color: #047857; }}
  .pend {{ background: #ffedd5; color: #b45309; }}
  .warn {{ background: #e2e8f0; color: #334155; }}
  .chips {{ display: flex; flex-wrap: wrap; gap: 6px; }}
  .chip {{ display: inline-block; padding: 4px 10px; border-radius: 999px; background: #ecf5f3; color: #0f766e; font-size: 12px; font-weight: 600; text-decoration: none; border: 1px solid #cfe3df; }}
  a.chip:hover {{ background: #0f766e; color: #fff; border-color: #0f766e; }}
  .chip-pend {{ background: #fff7ed; color: #c2410c; border-color: #fed7aa; }}
  .chip-removido {{ background: #fee2e2; color: #b91c1c; border-color: #fecaca; text-decoration: line-through; }}
  .chip-add {{ background: #ede9fe; color: #5b21b6; border-color: #ddd6fe; }}
  a.chip-add:hover {{ background: #5b21b6; color: #fff; border-color: #5b21b6; }}
  .note {{ background: #fff7ed; border: 1px solid #fed7aa; color: #9a3412; border-radius: 10px; padding: 12px 14px; font-size: 13px; margin: 0 0 14px; }}
  .note-ok {{ background: #ecfdf5; border: 1px solid #a7f3d0; color: #065f46; }}
  .note-info {{ background: #f5f3ff; border: 1px solid #ddd6fe; color: #4c1d95; }}
  .legend {{ display: flex; flex-wrap: wrap; gap: 10px; align-items: center; font-size: 12px; color: var(--muted); margin: 0 0 12px; }}
  .catalog {{ background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 14px; margin-bottom: 16px; }}
  .catalog h3 {{ margin: 0 0 10px; font-size: 14px; }}
  footer {{ color: var(--muted); font-size: 12px; padding: 16px 0; }}
</style>
</head>
<body>
<header>
  <div class="wrap">
    <h1>Cidades, especialidades e exames — Clínica da Cidade</h1>
    <p>Cidades criadas, especialidades por cidade e exames gerados (texto-novo)</p>
  </div>
</header>
<div class="wrap">
  <div class="tabs">
    <button type="button" class="tab active" data-tab="cidades">Cidades criadas</button>
    <button type="button" class="tab" data-tab="especialidades">Especialidades por cidade</button>
    <button type="button" class="tab" data-tab="exames">Exames por cidade</button>
  </div>

  <section id="panel-cidades" class="panel active">
  <div class="cards">
    <div class="card"><div class="k">Cidades</div><div class="v">{total}</div></div>
    <div class="card"><div class="k">Criadas</div><div class="v">{feitas}</div></div>
    <div class="card"><div class="k">Pendentes</div><div class="v">{pendentes}</div></div>
    <div class="card"><div class="k">Sem unidade local</div><div class="v">{extra}</div></div>
    <div class="card"><div class="k">Páginas geradas</div><div class="v">{total_paginas}</div></div>
  </div>
  <div class="filters">
    <input type="search" id="q-cidades" placeholder="Filtrar por cidade, UF ou estado...">
    <button type="button" data-filter="all" class="active">Todas</button>
    <button type="button" data-filter="ok">Criadas</button>
    <button type="button" data-filter="pend">Pendentes</button>
  </div>
  <table>
    <thead>
      <tr><th>Cidade</th><th>UF</th><th>Estado</th><th>Unidades</th><th>Páginas SEO</th><th>Status</th></tr>
    </thead>
    <tbody id="tbody-cidades">{''.join(body_cidades)}</tbody>
  </table>
  </section>

  <section id="panel-especialidades" class="panel">
  <div class="cards">
    <div class="card"><div class="k">Cidades com páginas</div><div class="v">{len(por_cidade)}</div></div>
    <div class="card"><div class="k">Páginas especialidades</div><div class="v">{total_paginas_esp}</div></div>
    <div class="card"><div class="k">Total (esp+exames)</div><div class="v">{total_paginas}</div></div>
  </div>
  <div class="legend">
    <span class="chip">Ativa</span>
    <span class="chip chip-removido">Removida da tabela (mantida no relatório)</span>
    <span class="chip chip-add">Adicionada fora do padrão</span>
  </div>
  <div class="filters">
    <input type="search" id="q-esp" placeholder="Filtrar por cidade ou especialidade...">
  </div>
  <table>
    <thead>
      <tr><th>Cidade</th><th>UF</th><th>Qtd</th><th>Especialidades criadas</th></tr>
    </thead>
    <tbody id="tbody-esp">{''.join(body_esp)}</tbody>
  </table>
  </section>

  <section id="panel-exames" class="panel">
  <div class="note {'note-ok' if EXAMES_CRIADOS else ''}">
    {"Exames <b>criados</b> por cidade (31 × 38 = 1178 páginas). Links apontam para /centro/{{slug}}-em-{{cidade}}/." if EXAMES_CRIADOS else "Exames ainda <b>não criados</b> por cidade — só registrados para a fila de criação."}
    Catálogo de <a href="https://www.clinicadacidade.com.br/exames/" target="_blank" rel="noopener">clinicadacidade.com.br/exames</a>.
  </div>
  <div class="cards">
    <div class="card"><div class="k">Exames no catálogo</div><div class="v">{n_exames}</div></div>
    <div class="card"><div class="k">Cidades criadas</div><div class="v">{n_cidades_ok}</div></div>
    <div class="card"><div class="k">{"Páginas criadas" if EXAMES_CRIADOS else "Páginas a criar"}</div><div class="v">{n_paginas_exames if EXAMES_CRIADOS else n_exames * n_cidades_ok}</div></div>
    <div class="card"><div class="k">Status</div><div class="v" style="font-size:1rem;margin-top:10px">{"Criado" if EXAMES_CRIADOS else "Pendente"}</div></div>
  </div>
  <div class="catalog">
    <h3>Catálogo de exames (nacional)</h3>
    <div class="chips">{''.join(exam_chips_catalog) or '<span class="badge pend">Rode extrair_exames.py</span>'}</div>
  </div>
  <div class="filters">
    <input type="search" id="q-exames" placeholder="Filtrar por cidade, UF ou exame...">
  </div>
  <table>
    <thead>
      <tr><th>Cidade</th><th>UF</th><th>Qtd exames</th><th>Status</th><th>Exames {"(criados)" if EXAMES_CRIADOS else "(pendentes)"}</th></tr>
    </thead>
    <tbody id="tbody-exames">
      {''.join(body_exames) if body_exames else '<tr><td colspan="5" style="text-align:center;color:#5d6e6a;padding:24px">Nenhuma cidade criada ou catálogo de exames vazio.</td></tr>'}
    </tbody>
  </table>
  </section>

  <footer>Gerado em {generated} a partir de lista_cidades_estados.xlsx, lista_todas_urls.xlsx e lista_exames.json.</footer>
</div>
<script>
document.querySelectorAll('.tab').forEach(btn => {{
  btn.addEventListener('click', () => {{
    document.querySelectorAll('.tab').forEach(b => b.classList.toggle('active', b === btn));
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    document.getElementById('panel-' + btn.dataset.tab).classList.add('active');
  }});
}});
let filter = 'all';
const qCidades = document.getElementById('q-cidades');
function applyCidades() {{
  const v = qCidades.value.toLowerCase();
  document.querySelectorAll('#tbody-cidades tr').forEach(tr => {{
    const matchText = tr.innerText.toLowerCase().includes(v);
    const matchFilter = filter === 'all' || tr.classList.contains(filter);
    tr.style.display = matchText && matchFilter ? '' : 'none';
  }});
}}
qCidades.addEventListener('input', applyCidades);
document.querySelectorAll('#panel-cidades button[data-filter]').forEach(btn => {{
  btn.addEventListener('click', () => {{
    filter = btn.dataset.filter;
    document.querySelectorAll('#panel-cidades button[data-filter]').forEach(b => b.classList.toggle('active', b === btn));
    applyCidades();
  }});
}});
document.getElementById('q-esp').addEventListener('input', () => {{
  const v = document.getElementById('q-esp').value.toLowerCase();
  document.querySelectorAll('#tbody-esp tr').forEach(tr => {{
    const blob = (tr.dataset.search || tr.innerText).toLowerCase();
    tr.style.display = blob.includes(v) ? '' : 'none';
  }});
}});
document.getElementById('q-exames').addEventListener('input', () => {{
  const v = document.getElementById('q-exames').value.toLowerCase();
  document.querySelectorAll('#tbody-exames tr').forEach(tr => {{
    const blob = (tr.dataset.search || tr.innerText).toLowerCase();
    tr.style.display = blob.includes(v) ? '' : 'none';
  }});
}});
function enableTableSort(table) {{
  table.querySelectorAll('thead th').forEach((th, idx) => {{
    th.classList.add('sortable');
    th.title = 'Clique para ordenar';
    th.addEventListener('click', () => {{
      const tbody = table.tBodies[0];
      const rows = Array.from(tbody.querySelectorAll('tr'));
      const asc = th.dataset.dir !== 'asc';
      table.querySelectorAll('thead th').forEach((h) => {{
        h.dataset.dir = '';
        h.classList.remove('asc', 'desc');
      }});
      th.dataset.dir = asc ? 'asc' : 'desc';
      th.classList.add(asc ? 'asc' : 'desc');
      const val = (tr) => {{
        const td = tr.children[idx];
        return td && td.dataset.sort !== undefined ? td.dataset.sort : (td ? td.innerText.trim() : '');
      }};
      rows.sort((a, b) => {{
        const va = val(a), vb = val(b);
        const na = parseFloat(va), nb = parseFloat(vb);
        const bothNum = va !== '' && vb !== '' && !isNaN(na) && !isNaN(nb);
        const cmp = bothNum ? na - nb : String(va).localeCompare(String(vb), 'pt-BR', {{numeric: true, sensitivity: 'base'}});
        return asc ? cmp : -cmp;
      }});
      rows.forEach((r) => tbody.appendChild(r));
    }});
  }});
}}
document.querySelectorAll('table').forEach(enableTableSort);
</script>
</body>
</html>
""",
        encoding="utf-8",
    )
    return out


if __name__ == "__main__":
    path = main()
    print(path)
    if EXAMES_PLAN_XLSX.exists():
        print(EXAMES_PLAN_XLSX)
