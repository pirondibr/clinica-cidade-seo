# -*- coding: utf-8 -*-
"""Consolidate DataForSEO results and generate HTML report for cardiologista."""
import json
from pathlib import Path
from datetime import date

OUT_DIR = Path(r"C:\Users\Usuario\Desktop\clinica cidade\Blog seo")

# Final curated set (aligned with gastro pattern)
TEMA = "cardiologista"

DIRETAS = [
    "o que é cardiologia",
    "o que faz o cardiologista",
    "quanto custa consulta cardiologista",
    "marcar consulta cardiologista",
    "quando procurar um cardiologista",
    "cardiologista unimed",
    "medico do coracao",
    "cardiologista esportivo",
]

INDIRETAS = [
    "pressao alta",
    "eletrocardiograma",
    "dor no peito",
    "infarto",
    "teste ergometrico",
    "colesterol alto",
    "angina",
    "holter 24 horas",
    "palpitação",
    "fibrilacao atrial",
]


def load_all():
    by_kw = {}
    for name in [
        "cardiologista_volumes.json",
        "cardiologista_volumes_v2.json",
        "cardiologista_volumes_v3.json",
    ]:
        path = OUT_DIR / name
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        for row in data:
            kw = (row.get("keyword") or "").lower()
            if not kw:
                continue
            # keep row with best volume info
            prev = by_kw.get(kw)
            if prev is None or (prev.get("search_volume") is None and row.get("search_volume") is not None):
                by_kw[kw] = row
            elif prev is not None and row.get("search_volume") and (prev.get("search_volume") or 0) < row.get("search_volume"):
                by_kw[kw] = row
    return by_kw


def fmt_num(n):
    if n is None:
        return "—"
    return f"{int(n):,}".replace(",", ".")


def fmt_pct(n):
    if n is None:
        return "—"
    sign = "+" if n > 0 else ""
    return f"{sign}{n:.1f}%"


def growth(monthly, months_back):
    if not monthly:
        return None
    keys = sorted(monthly.keys(), reverse=True)
    if len(keys) <= months_back:
        return None
    new = monthly.get(keys[0])
    old = monthly.get(keys[months_back])
    if old in (None, 0) or new is None:
        return None
    return round(((new - old) / old) * 100, 1)


def pick(by_kw, keyword):
    row = by_kw.get(keyword.lower())
    if not row:
        # try accent-insensitive simple fallbacks already curated
        return {
            "keyword": keyword,
            "search_volume": None,
            "cpc": None,
            "competition": None,
            "competition_index": None,
            "latest_month": None,
            "latest_volume": None,
            "monthly": {},
        }
    return row


def row_html(r, tipo):
    monthly = r.get("monthly") or {}
    g6 = growth(monthly, 6)
    g12 = growth(monthly, 12)
    vol = r.get("search_volume")
    latest = r.get("latest_volume")
    latest_m = r.get("latest_month") or "—"
    cpc = r.get("cpc")
    cpc_s = f"R$ {cpc:.2f}".replace(".", ",") if isinstance(cpc, (int, float)) else "—"
    comp = r.get("competition") or "—"
    idx = r.get("competition_index")
    idx_s = str(idx) if idx is not None else "—"

    g6_cls = "up" if (g6 or 0) > 0 else ("down" if (g6 or 0) < 0 else "")
    g12_cls = "up" if (g12 or 0) > 0 else ("down" if (g12 or 0) < 0 else "")

    # last 6 months sparkline-ish cells
    keys = sorted(monthly.keys(), reverse=True)[:6]
    keys = list(reversed(keys))
    months_cells = "".join(
        f'<td class="m">{fmt_num(monthly.get(k))}</td>' for k in keys
    )
    while months_cells.count("<td") < 6:
        months_cells = '<td class="m">—</td>' + months_cells
    month_headers = keys if len(keys) == 6 else (["—"] * (6 - len(keys)) + keys)

    return {
        "html": f"""
      <tr>
        <td><span class="badge {tipo}">{tipo}</span></td>
        <td class="kw">{r.get('keyword')}</td>
        <td class="num vol">{fmt_num(vol)}</td>
        <td class="num">{fmt_num(latest)}</td>
        <td class="muted">{latest_m}</td>
        <td class="num">{cpc_s}</td>
        <td>{comp}</td>
        <td class="num">{idx_s}</td>
        <td class="num {g6_cls}">{fmt_pct(g6)}</td>
        <td class="num {g12_cls}">{fmt_pct(g12)}</td>
        {months_cells}
      </tr>""",
        "month_headers": month_headers,
        "vol": vol or 0,
        "keyword": r.get("keyword"),
        "tipo": tipo,
        "cpc": cpc,
        "competition": comp,
        "g6": g6,
        "g12": g12,
        "latest": latest,
        "latest_m": latest_m,
    }


def main():
    by_kw = load_all()

    tema_row = pick(by_kw, TEMA)
    diretas_rows = [pick(by_kw, k) for k in DIRETAS]
    indiretas_rows = [pick(by_kw, k) for k in INDIRETAS]

    # ensure display keyword matches curated label
    for curated, row in zip(DIRETAS, diretas_rows):
        row["keyword"] = curated
    for curated, row in zip(INDIRETAS, indiretas_rows):
        row["keyword"] = curated
    tema_row["keyword"] = TEMA

    built = []
    built.append(row_html(tema_row, "tema"))
    for r in diretas_rows:
        built.append(row_html(r, "direta"))
    for r in indiretas_rows:
        built.append(row_html(r, "indireta"))

    # month headers from tema (most complete)
    month_headers = built[0]["month_headers"]
    month_th = "".join(f"<th>{h}</th>" for h in month_headers)

    body_rows = "\n".join(b["html"] for b in built)

    # summary cards
    all_with_vol = [b for b in built if b["vol"]]
    top = sorted(all_with_vol, key=lambda x: -x["vol"])[:5]
    top_html = "".join(
        f'<div class="chip"><strong>{fmt_num(t["vol"])}</strong><span>{t["keyword"]}</span></div>'
        for t in top
    )

    total_diretas = sum(1 for b in built if b["tipo"] == "direta")
    total_indiretas = sum(1 for b in built if b["tipo"] == "indireta")
    com_volume = sum(1 for b in built if b["vol"])

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>SEO Keywords — Cardiologista | Clínica da Cidade</title>
  <style>
    :root {{
      --bg: #f3f6f8;
      --ink: #14212b;
      --muted: #5b6b76;
      --line: #d7e0e6;
      --card: #ffffff;
      --tema: #0b6e4f;
      --direta: #1d4e89;
      --indireta: #9a3412;
      --up: #0b6e4f;
      --down: #b42318;
      --accent: #0e7c7b;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
      color: var(--ink);
      background:
        radial-gradient(1200px 500px at 10% -10%, #d7f0ea 0%, transparent 55%),
        radial-gradient(900px 400px at 100% 0%, #d9e7f5 0%, transparent 50%),
        var(--bg);
      line-height: 1.45;
    }}
    .wrap {{ max-width: 1180px; margin: 0 auto; padding: 32px 20px 64px; }}
    header {{
      margin-bottom: 28px;
    }}
    .eyebrow {{
      text-transform: uppercase;
      letter-spacing: .12em;
      font-size: 12px;
      color: var(--accent);
      font-weight: 700;
      margin: 0 0 8px;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: clamp(1.6rem, 2.5vw, 2.2rem);
      letter-spacing: -0.02em;
    }}
    .sub {{
      margin: 0;
      color: var(--muted);
      max-width: 62ch;
    }}
    .meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 16px;
    }}
    .pill {{
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 6px 12px;
      font-size: 13px;
      color: var(--muted);
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
      margin: 24px 0;
    }}
    @media (max-width: 800px) {{
      .grid {{ grid-template-columns: repeat(2, 1fr); }}
    }}
    .stat {{
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 16px;
    }}
    .stat .label {{ font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: .06em; }}
    .stat .value {{ font-size: 1.6rem; font-weight: 700; margin-top: 4px; }}
    .section {{
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 18px 18px 8px;
      margin-bottom: 18px;
      overflow: auto;
    }}
    .section h2 {{
      margin: 0 0 4px;
      font-size: 1.05rem;
    }}
    .section p {{
      margin: 0 0 14px;
      color: var(--muted);
      font-size: 14px;
    }}
    .chips {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 18px;
    }}
    .chip {{
      background: #eef7f6;
      border: 1px solid #cfe6e3;
      border-radius: 12px;
      padding: 10px 12px;
      min-width: 140px;
    }}
    .chip strong {{ display: block; font-size: 1.1rem; }}
    .chip span {{ color: var(--muted); font-size: 13px; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13.5px;
      min-width: 980px;
    }}
    th, td {{
      padding: 10px 8px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: middle;
    }}
    th {{
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: .05em;
      color: var(--muted);
      font-weight: 650;
      position: sticky;
      top: 0;
      background: #fbfcfd;
    }}
    .kw {{ font-weight: 600; }}
    .num {{ text-align: right; font-variant-numeric: tabular-nums; }}
    .vol {{ font-weight: 700; }}
    .muted {{ color: var(--muted); }}
    .m {{ text-align: right; color: var(--muted); font-variant-numeric: tabular-nums; }}
    .badge {{
      display: inline-block;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: .04em;
      padding: 3px 8px;
      border-radius: 999px;
      color: #fff;
    }}
    .badge.tema {{ background: var(--tema); }}
    .badge.direta {{ background: var(--direta); }}
    .badge.indireta {{ background: var(--indireta); }}
    .up {{ color: var(--up); font-weight: 650; }}
    .down {{ color: var(--down); font-weight: 650; }}
    .lists {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 18px;
      margin-bottom: 18px;
    }}
    @media (max-width: 800px) {{
      .lists {{ grid-template-columns: 1fr; }}
    }}
    .list-card {{
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 18px;
    }}
    .list-card h3 {{ margin: 0 0 10px; font-size: 1rem; }}
    .list-card ol, .list-card ul {{ margin: 0; padding-left: 18px; }}
    .list-card li {{ margin: 6px 0; }}
    .list-card .v {{ color: var(--muted); font-size: 13px; }}
    footer {{
      margin-top: 20px;
      color: var(--muted);
      font-size: 12px;
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <p class="eyebrow">Blog SEO · Clínica da Cidade</p>
      <h1>Rodada 1 — Tema: Cardiologista</h1>
      <p class="sub">
        Pesquisa de palavras-chave para <strong>clinicadacidade.com.br</strong>
        (Brasil), com volume mensal via DataForSEO Google Ads Search Volume.
      </p>
      <div class="meta">
        <span class="pill">Local: Brasil (2076)</span>
        <span class="pill">Fonte: DataForSEO · Google Ads</span>
        <span class="pill">Gerado em: {date.today().isoformat()}</span>
        <span class="pill">Último mês nos dados: {tema_row.get('latest_month') or '—'}</span>
      </div>
    </header>

    <div class="grid">
      <div class="stat">
        <div class="label">Volume do tema</div>
        <div class="value">{fmt_num(tema_row.get('search_volume'))}</div>
      </div>
      <div class="stat">
        <div class="label">Palavras diretas</div>
        <div class="value">{total_diretas}</div>
      </div>
      <div class="stat">
        <div class="label">Palavras indiretas</div>
        <div class="value">{total_indiretas}</div>
      </div>
      <div class="stat">
        <div class="label">Com volume</div>
        <div class="value">{com_volume}/{len(built)}</div>
      </div>
    </div>

    <h2 style="margin:0 0 10px;font-size:1rem;">Maiores volumes desta rodada</h2>
    <div class="chips">{top_html}</div>

    <div class="lists">
      <div class="list-card">
        <h3>Palavras diretas</h3>
        <ol>
          {''.join(f"<li>{k} <span class='v'>({fmt_num(pick(by_kw,k).get('search_volume'))}/mês)</span></li>" for k in DIRETAS)}
        </ol>
      </div>
      <div class="list-card">
        <h3>Palavras indiretas</h3>
        <ol>
          {''.join(f"<li>{k} <span class='v'>({fmt_num(pick(by_kw,k).get('search_volume'))}/mês)</span></li>" for k in INDIRETAS)}
        </ol>
      </div>
    </div>

    <div class="section">
      <h2>Tabela completa — volume, CPC, competição e tendência</h2>
      <p>Volume médio mensal (Google Ads). Crescimento 6m/12m comparado ao mês mais recente disponível.</p>
      <table>
        <thead>
          <tr>
            <th>Tipo</th>
            <th>Palavra</th>
            <th>Vol. médio</th>
            <th>Último mês</th>
            <th>Ref.</th>
            <th>CPC</th>
            <th>Competição</th>
            <th>Idx</th>
            <th>Δ 6m</th>
            <th>Δ 12m</th>
            {month_th}
          </tr>
        </thead>
        <tbody>
          {body_rows}
        </tbody>
      </table>
    </div>

    <footer>
      Padrão editorial: 1 tema (especialidade) + 3–10 diretas + 3–10 indiretas.
      Próximos temas: dermatologista, endocrinologista, ginecologista, oftalmologista.
      Termos sem volume no Google Ads aparecem como "—".
    </footer>
  </div>
</body>
</html>
"""

    out_html = OUT_DIR / "cardiologista_keywords.html"
    out_html.write_text(html, encoding="utf-8")
    print("HTML:", out_html)

    # also save curated JSON summary
    summary = {
        "tema": TEMA,
        "site": "clinicadacidade.com.br",
        "location": "Brasil (2076)",
        "diretas": DIRETAS,
        "indiretas": INDIRETAS,
        "rows": [
            {
                "tipo": b["tipo"],
                "keyword": b["keyword"],
                "search_volume": b["vol"] or None,
                "latest_volume": b["latest"],
                "latest_month": b["latest_m"],
                "cpc": b["cpc"],
                "competition": b["competition"],
                "growth_6m": b["g6"],
                "growth_12m": b["g12"],
            }
            for b in built
        ],
    }
    out_json = OUT_DIR / "cardiologista_resumo.json"
    out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print("JSON:", out_json)


if __name__ == "__main__":
    main()
