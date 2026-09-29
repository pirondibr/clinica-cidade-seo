# -*- coding: utf-8 -*-
"""
Keyword research for Clínica da Cidade specialties.
Fetches DataForSEO volumes and builds a single tabbed HTML.
"""
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, r"C:\Users\Usuario\.cursor\skills\pesquisa-marca-dataforseo\scripts")
from client import RestClient

OUT_DIR = Path(r"C:\Users\Usuario\Desktop\clinica cidade\Blog seo")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Each theme: 1 tema + 3-10 diretas + 3-10 indiretas (no brand/competitor terms like unimed)
THEMES = {
    "cardiologista": {
        "label": "Cardiologista",
        "tema": "cardiologista",
        "diretas": [
            "o que é cardiologia",
            "o que faz o cardiologista",
            "quanto custa consulta cardiologista",
            "marcar consulta cardiologista",
            "quando procurar um cardiologista",
            "medico do coracao",
            "cardiologista esportivo",
            "consulta cardiologista",
        ],
        "indiretas": [
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
        ],
        # alternates to improve volume hit rate
        "extras": [
            "pressão alta",
            "palpitacao",
            "fibrilação atrial",
            "insuficiencia cardiaca",
            "ecocardiograma com doppler",
            "sopro no coracao",
            "quando procurar cardiologista",
            "valor consulta cardiologista",
        ],
    },
    "dermatologista": {
        "label": "Dermatologista",
        "tema": "dermatologista",
        "diretas": [
            "o que é dermatologia",
            "o que faz o dermatologista",
            "quando procurar um dermatologista",
            "quanto custa consulta dermatologista",
            "marcar consulta dermatologista",
            "consulta dermatologista",
            "dermatologista particular",
            "melhor dermatologista",
        ],
        "indiretas": [
            "acne",
            "queda de cabelo",
            "manchas na pele",
            "psoriase",
            "dermatite",
            "melasma",
            "micose",
            "rosacea",
            "verruga",
            "biopsia de pele",
        ],
        "extras": [
            "psoríase",
            "rosácea",
            "biopsia pele",
            "biopsia de pele",
            "alopecia",
            "eczema",
            "herpes zoster",
            "o que e dermatologia",
            "valor consulta dermatologista",
            "quando procurar dermatologista",
        ],
    },
    "endocrinologista": {
        "label": "Endocrinologista",
        "tema": "endocrinologista",
        "diretas": [
            "o que é endocrinologia",
            "o que faz o endocrinologista",
            "quando procurar um endocrinologista",
            "quanto custa consulta endocrinologista",
            "marcar consulta endocrinologista",
            "consulta endocrinologista",
            "endocrinologista particular",
            "medico endocrinologista",
        ],
        "indiretas": [
            "diabetes",
            "hipotireoidismo",
            "hipertireoidismo",
            "tireoide",
            "obesidade",
            "resistencia a insulina",
            "sindrome metabolica",
            "hashimoto",
            "nodulo na tireoide",
            "colesterol alto",
        ],
        "extras": [
            "o que e endocrinologia",
            "quando procurar endocrinologista",
            "valor consulta endocrinologista",
            "resistência à insulina",
            "síndrome metabólica",
            "nódulo na tireoide",
            "diabetes tipo 2",
            "pre diabetes",
            "pré diabetes",
            "tiroide",
        ],
    },
    "ginecologista": {
        "label": "Ginecologista",
        "tema": "ginecologista",
        "diretas": [
            "o que é ginecologia",
            "o que faz o ginecologista",
            "quando procurar um ginecologista",
            "quanto custa consulta ginecologista",
            "marcar consulta ginecologista",
            "consulta ginecologista",
            "ginecologista particular",
            "primeira consulta ginecologista",
        ],
        "indiretas": [
            "papanicolau",
            "corrimento vaginal",
            "endometriose",
            "mioma",
            "sop",
            "ovario policistico",
            "candidiase",
            "colposcopia",
            "menopausa",
            "ciclo menstrual irregular",
        ],
        "extras": [
            "o que e ginecologia",
            "quando procurar ginecologista",
            "valor consulta ginecologista",
            "ovário policístico",
            "sindrome do ovario policistico",
            "candidíase",
            "dpi",
            "diu",
            "planejamento familiar",
            "ciclo menstrual irregular",
        ],
    },
    "oftalmologista": {
        "label": "Oftalmologista",
        "tema": "oftalmologista",
        "diretas": [
            "o que é oftalmologia",
            "o que faz o oftalmologista",
            "quando procurar um oftalmologista",
            "quanto custa consulta oftalmologista",
            "marcar consulta oftalmologista",
            "consulta oftalmologista",
            "oftalmologista particular",
            "exame de vista",
        ],
        "indiretas": [
            "miopia",
            "astigmatismo",
            "catarata",
            "glaucoma",
            "olho seco",
            "conjuntivite",
            "degeneracao macular",
            "retinopatia diabetica",
            "cirurgia de catarata",
            "grau de oculos",
        ],
        "extras": [
            "o que e oftalmologia",
            "quando procurar oftalmologista",
            "valor consulta oftalmologista",
            "degeneração macular",
            "retinopatia diabética",
            "grau de óculos",
            "exame oftalmologico",
            "fundo de olho",
            "ceratocone",
            "pterigio",
        ],
    },
}


def all_keywords():
    kws = []
    for t in THEMES.values():
        kws.append(t["tema"])
        kws.extend(t["diretas"])
        kws.extend(t["indiretas"])
        kws.extend(t.get("extras", []))
    # unique preserve order
    seen = set()
    out = []
    for k in kws:
        kl = k.lower()
        if "unimed" in kl:
            continue
        if kl not in seen:
            seen.add(kl)
            out.append(k)
    return out


def fetch_volumes(keywords):
    client = RestClient("rafaelpiromdi@gmail.com", "def406af14eb9ac4")
    # DataForSEO allows large batches; chunk to be safe
    chunk_size = 100
    by_kw = {}
    for i in range(0, len(keywords), chunk_size):
        chunk = keywords[i : i + chunk_size]
        post_data = {
            0: {
                "location_code": 2076,
                "keywords": chunk,
                "date_from": "2020-01-01",
                "search_partners": False,
            }
        }
        response = client.post("/v3/keywords_data/google_ads/search_volume/live", post_data)
        print(
            f"batch {i // chunk_size + 1}: status={response.get('status_code')} "
            f"cost={response.get('cost')}"
        )
        tasks = response.get("tasks") or []
        if not tasks:
            print(json.dumps(response, ensure_ascii=False)[:1500])
            continue
        result = tasks[0].get("result") or []
        for r in result:
            kw = (r.get("keyword") or "").strip()
            if not kw:
                continue
            ms = r.get("monthly_searches") or []
            monthly = {
                f"{m['year']}-{int(m['month']):02d}": m["search_volume"] for m in ms
            }
            latest_keys = sorted(monthly.keys(), reverse=True)
            by_kw[kw.lower()] = {
                "keyword": kw,
                "search_volume": r.get("search_volume"),
                "cpc": r.get("cpc"),
                "competition": r.get("competition"),
                "competition_index": r.get("competition_index"),
                "latest_month": latest_keys[0] if latest_keys else None,
                "latest_volume": monthly[latest_keys[0]] if latest_keys else None,
                "monthly": monthly,
            }
            vol = r.get("search_volume")
            print(f"  {vol if vol is not None else '-':>8} | {kw}")
    return by_kw


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


def fmt_num(n):
    if n is None:
        return "—"
    return f"{int(n):,}".replace(",", ".")


def fmt_pct(n):
    if n is None:
        return "—"
    sign = "+" if n > 0 else ""
    return f"{sign}{n:.1f}%"


def pick(by_kw, keyword):
    row = by_kw.get(keyword.lower())
    if not row:
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
    # keep curated display keyword
    out = dict(row)
    out["keyword"] = keyword
    return out


def best_pick(by_kw, primary, alternates=None):
    """Prefer primary; if no volume, try alternates with volume."""
    primary_row = pick(by_kw, primary)
    if primary_row.get("search_volume") is not None:
        return primary_row
    for alt in alternates or []:
        alt_row = pick(by_kw, alt)
        if alt_row.get("search_volume") is not None:
            # show curated primary label, keep alt metrics
            alt_row = dict(alt_row)
            alt_row["keyword"] = primary
            alt_row["matched_as"] = alt
            return alt_row
    return primary_row


def build_theme_payload(key, cfg, by_kw):
    # alias map for common accent/no-accent swaps
    aliases = {
        "pressao alta": ["pressão alta"],
        "palpitação": ["palpitacao"],
        "fibrilacao atrial": ["fibrilação atrial"],
        "psoriase": ["psoríase"],
        "rosacea": ["rosácea"],
        "biopsia de pele": ["biopsia pele"],
        "resistencia a insulina": ["resistência à insulina"],
        "sindrome metabolica": ["síndrome metabólica"],
        "nodulo na tireoide": ["nódulo na tireoide"],
        "endomometriose": ["endometriose"],  # typo guard
        "endometriose": ["endomometriose"],
        "ovario policistico": ["ovário policístico", "sindrome do ovario policistico"],
        "candidiase": ["candidíase"],
        "degeneracao macular": ["degeneração macular"],
        "retinopatia diabetica": ["retinopatia diabética"],
        "grau de oculos": ["grau de óculos"],
        "o que é cardiologia": ["o que e cardiologia"],
        "o que é dermatologia": ["o que e dermatologia"],
        "o que é endocrinologia": ["o que e endocrinologia"],
        "o que é ginecologia": ["o que e ginecologia"],
        "o que é oftalmologia": ["o que e oftalmologia"],
        "quando procurar um cardiologista": ["quando procurar cardiologista"],
        "quando procurar um dermatologista": ["quando procurar dermatologista"],
        "quando procurar um endocrinologista": ["quando procurar endocrinologista"],
        "quando procurar um ginecologista": ["quando procurar ginecologista"],
        "quando procurar um oftalmologista": ["quando procurar oftalmologista"],
        "quanto custa consulta cardiologista": ["valor consulta cardiologista"],
        "quanto custa consulta dermatologista": ["valor consulta dermatologista"],
        "quanto custa consulta endocrinologista": ["valor consulta endocrinologista"],
        "quanto custa consulta ginecologista": ["valor consulta ginecologista"],
        "quanto custa consulta oftalmologista": ["valor consulta oftalmologista"],
    }

    # filter out endomometriose typo from display if both exist - use endometriose only
    diretas = [k for k in cfg["diretas"] if "unimed" not in k.lower()]
    indiretas = []
    for k in cfg["indiretas"]:
        if "unimed" in k.lower():
            continue
        if k.lower() == "endomometriose":
            continue  # skip typo variant in display
        indiretas.append(k)

    tema = best_pick(by_kw, cfg["tema"])
    diretas_rows = [best_pick(by_kw, k, aliases.get(k.lower(), [])) for k in diretas]
    indiretas_rows = [best_pick(by_kw, k, aliases.get(k.lower(), [])) for k in indiretas]

    return {
        "key": key,
        "label": cfg["label"],
        "tema": tema,
        "diretas": diretas_rows,
        "indiretas": indiretas_rows,
    }


def month_headers_from(row):
    monthly = row.get("monthly") or {}
    keys = sorted(monthly.keys(), reverse=True)[:6]
    keys = list(reversed(keys))
    if len(keys) < 6:
        keys = ["—"] * (6 - len(keys)) + keys
    return keys


def table_row(r, tipo):
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

    keys = sorted(monthly.keys(), reverse=True)[:6]
    keys = list(reversed(keys))
    cells = "".join(f'<td class="m">{fmt_num(monthly.get(k))}</td>' for k in keys)
    while cells.count("<td") < 6:
        cells = '<td class="m">—</td>' + cells

    matched = ""
    if r.get("matched_as") and r.get("matched_as").lower() != r.get("keyword", "").lower():
        matched = f'<div class="match">via: {r["matched_as"]}</div>'

    return f"""
      <tr>
        <td><span class="badge {tipo}">{tipo}</span></td>
        <td class="kw">{r.get('keyword')}{matched}</td>
        <td class="num vol">{fmt_num(vol)}</td>
        <td class="num">{fmt_num(latest)}</td>
        <td class="muted">{latest_m}</td>
        <td class="num">{cpc_s}</td>
        <td>{comp}</td>
        <td class="num">{idx_s}</td>
        <td class="num {g6_cls}">{fmt_pct(g6)}</td>
        <td class="num {g12_cls}">{fmt_pct(g12)}</td>
        {cells}
      </tr>"""


def theme_panel_html(payload):
    tema = payload["tema"]
    all_rows = [("tema", tema)] + [("direta", r) for r in payload["diretas"]] + [
        ("indireta", r) for r in payload["indiretas"]
    ]
    headers = month_headers_from(tema)
    month_th = "".join(f"<th>{h}</th>" for h in headers)

    with_vol = [(t, r) for t, r in all_rows if r.get("search_volume")]
    top = sorted(with_vol, key=lambda x: -(x[1].get("search_volume") or 0))[:5]
    top_html = "".join(
        f'<div class="chip"><strong>{fmt_num(r.get("search_volume"))}</strong><span>{r.get("keyword")}</span></div>'
        for _, r in top
    )

    diretas_list = "".join(
        f"<li>{r.get('keyword')} <span class='v'>({fmt_num(r.get('search_volume'))}/mês)</span></li>"
        for r in payload["diretas"]
    )
    indiretas_list = "".join(
        f"<li>{r.get('keyword')} <span class='v'>({fmt_num(r.get('search_volume'))}/mês)</span></li>"
        for r in payload["indiretas"]
    )

    body = "\n".join(table_row(r, t) for t, r in all_rows)
    com_vol = sum(1 for _, r in all_rows if r.get("search_volume") is not None)

    return f"""
    <section class="panel" id="panel-{payload['key']}" role="tabpanel" hidden>
      <div class="panel-head">
        <h2>Tema: {payload['label']}</h2>
        <p>1 especialidade + {len(payload['diretas'])} diretas + {len(payload['indiretas'])} indiretas · {com_vol}/{len(all_rows)} com volume</p>
      </div>

      <div class="grid">
        <div class="stat">
          <div class="label">Volume do tema</div>
          <div class="value">{fmt_num(tema.get('search_volume'))}</div>
        </div>
        <div class="stat">
          <div class="label">Diretas</div>
          <div class="value">{len(payload['diretas'])}</div>
        </div>
        <div class="stat">
          <div class="label">Indiretas</div>
          <div class="value">{len(payload['indiretas'])}</div>
        </div>
        <div class="stat">
          <div class="label">Com volume</div>
          <div class="value">{com_vol}/{len(all_rows)}</div>
        </div>
      </div>

      <h3 class="subh">Maiores volumes</h3>
      <div class="chips">{top_html}</div>

      <div class="lists">
        <div class="list-card">
          <h3>Palavras diretas</h3>
          <ol>{diretas_list}</ol>
        </div>
        <div class="list-card">
          <h3>Palavras indiretas</h3>
          <ol>{indiretas_list}</ol>
        </div>
      </div>

      <div class="section">
        <h3>Tabela — volume, CPC, competição e tendência</h3>
        <p>Volume médio mensal (Google Ads / DataForSEO · Brasil). Δ6m / Δ12m vs. mês mais recente.</p>
        <div class="table-wrap">
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
              {body}
            </tbody>
          </table>
        </div>
      </div>
    </section>
    """


def build_html(payloads):
    tabs = (
        '<button class="tab" role="tab" id="tab-home" data-target="home" '
        'aria-selected="true">Início</button>'
        + "".join(
            f'<button class="tab" role="tab" id="tab-{p["key"]}" data-target="{p["key"]}" '
            f'aria-selected="false">{p["label"]}</button>'
            for p in payloads
        )
    )
    panels = "\n".join(theme_panel_html(p) for p in payloads)

    # overview cards
    overview = "".join(
        f"""
        <button class="overview-card" data-target="{p['key']}">
          <span class="oc-label">{p['label']}</span>
          <span class="oc-vol">{fmt_num(p['tema'].get('search_volume'))}<small>/mês</small></span>
          <span class="oc-meta">{len(p['diretas'])} diretas · {len(p['indiretas'])} indiretas</span>
        </button>
        """
        for p in payloads
    )

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>SEO Keywords — 5 especialidades | Clínica da Cidade</title>
  <style>
    :root {{
      --bg: #f2f5f7;
      --ink: #132029;
      --muted: #5a6a75;
      --line: #d5dee4;
      --card: #ffffff;
      --tema: #0b6e4f;
      --direta: #1d4e89;
      --indireta: #9a3412;
      --up: #0b6e4f;
      --down: #b42318;
      --accent: #0e7c7b;
      --tab: #e8eef2;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
      color: var(--ink);
      background:
        radial-gradient(1100px 480px at 8% -8%, #d8f1eb 0%, transparent 55%),
        radial-gradient(900px 420px at 100% 0%, #d7e6f4 0%, transparent 50%),
        var(--bg);
      line-height: 1.45;
    }}
    .wrap {{ max-width: 1200px; margin: 0 auto; padding: 28px 18px 72px; }}
    .eyebrow {{
      text-transform: uppercase; letter-spacing: .12em; font-size: 12px;
      color: var(--accent); font-weight: 700; margin: 0 0 8px;
    }}
    h1 {{
      margin: 0 0 8px; font-size: clamp(1.55rem, 2.4vw, 2.15rem);
      letter-spacing: -0.02em;
    }}
    .sub {{ margin: 0; color: var(--muted); max-width: 70ch; }}
    .meta {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }}
    .pill {{
      background: var(--card); border: 1px solid var(--line); border-radius: 999px;
      padding: 6px 12px; font-size: 13px; color: var(--muted);
    }}

    .nav-shell {{
      margin-top: 22px;
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 14px;
      position: sticky;
      top: 8px;
      z-index: 20;
      box-shadow: 0 8px 24px rgba(19, 32, 41, 0.04);
    }}
    .tabs {{
      display: flex; flex-wrap: wrap; gap: 8px;
    }}
    .tab {{
      border: 1px solid var(--line);
      background: var(--tab);
      color: var(--ink);
      border-radius: 999px;
      padding: 9px 14px;
      font-size: 14px;
      font-weight: 650;
      cursor: pointer;
    }}
    .tab[aria-selected="true"] {{
      background: var(--accent);
      border-color: var(--accent);
      color: #fff;
    }}
    .tab:hover {{ filter: brightness(0.98); }}

    .overview {{
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 10px;
      margin: 18px 0 8px;
    }}
    @media (max-width: 980px) {{
      .overview {{ grid-template-columns: repeat(2, 1fr); }}
    }}
    @media (max-width: 560px) {{
      .overview {{ grid-template-columns: 1fr; }}
    }}
    .overview-card {{
      text-align: left;
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 14px;
      cursor: pointer;
    }}
    .overview-card:hover {{ border-color: #9fc4c2; }}
    .oc-label {{ display: block; font-weight: 700; }}
    .oc-vol {{ display: block; font-size: 1.35rem; font-weight: 750; margin-top: 4px; }}
    .oc-vol small {{ font-size: 12px; color: var(--muted); font-weight: 600; margin-left: 2px; }}
    .oc-meta {{ display: block; color: var(--muted); font-size: 12px; margin-top: 4px; }}

    .panel {{ margin-top: 18px; }}
    .panel[hidden] {{ display: none !important; }}
    .panel-head h2 {{ margin: 0 0 4px; font-size: 1.25rem; }}
    .panel-head p {{ margin: 0 0 14px; color: var(--muted); font-size: 14px; }}

    .grid {{
      display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 14px;
    }}
    @media (max-width: 800px) {{ .grid {{ grid-template-columns: repeat(2, 1fr); }} }}
    .stat {{
      background: var(--card); border: 1px solid var(--line); border-radius: 14px; padding: 14px;
    }}
    .stat .label {{
      font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: .06em;
    }}
    .stat .value {{ font-size: 1.45rem; font-weight: 700; margin-top: 4px; }}

    .subh {{ margin: 8px 0 8px; font-size: .95rem; }}
    .chips {{ display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 14px; }}
    .chip {{
      background: #eef7f6; border: 1px solid #cfe6e3; border-radius: 12px;
      padding: 10px 12px; min-width: 130px;
    }}
    .chip strong {{ display: block; font-size: 1.05rem; }}
    .chip span {{ color: var(--muted); font-size: 13px; }}

    .lists {{
      display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 14px;
    }}
    @media (max-width: 800px) {{ .lists {{ grid-template-columns: 1fr; }} }}
    .list-card {{
      background: var(--card); border: 1px solid var(--line); border-radius: 14px; padding: 14px;
    }}
    .list-card h3 {{ margin: 0 0 8px; font-size: .95rem; }}
    .list-card ol {{ margin: 0; padding-left: 18px; }}
    .list-card li {{ margin: 5px 0; }}
    .list-card .v {{ color: var(--muted); font-size: 13px; }}

    .section {{
      background: var(--card); border: 1px solid var(--line); border-radius: 14px;
      padding: 14px 14px 6px;
    }}
    .section h3 {{ margin: 0 0 4px; font-size: .95rem; }}
    .section p {{ margin: 0 0 10px; color: var(--muted); font-size: 13px; }}
    .table-wrap {{ overflow: auto; }}
    table {{
      width: 100%; border-collapse: collapse; font-size: 13px; min-width: 980px;
    }}
    th, td {{
      padding: 9px 7px; border-bottom: 1px solid var(--line);
      text-align: left; vertical-align: middle;
    }}
    th {{
      font-size: 11px; text-transform: uppercase; letter-spacing: .04em;
      color: var(--muted); font-weight: 650; background: #fbfcfd;
    }}
    .kw {{ font-weight: 600; }}
    .match {{ font-size: 11px; color: var(--muted); font-weight: 500; }}
    .num {{ text-align: right; font-variant-numeric: tabular-nums; }}
    .vol {{ font-weight: 700; }}
    .muted {{ color: var(--muted); }}
    .m {{ text-align: right; color: var(--muted); font-variant-numeric: tabular-nums; }}
    .badge {{
      display: inline-block; font-size: 10px; font-weight: 700; text-transform: uppercase;
      letter-spacing: .04em; padding: 3px 7px; border-radius: 999px; color: #fff;
    }}
    .badge.tema {{ background: var(--tema); }}
    .badge.direta {{ background: var(--direta); }}
    .badge.indireta {{ background: var(--indireta); }}
    .up {{ color: var(--up); font-weight: 650; }}
    .down {{ color: var(--down); font-weight: 650; }}
    footer {{
      margin-top: 18px; color: var(--muted); font-size: 12px;
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <p class="eyebrow">Blog SEO · Clínica da Cidade</p>
    <h1>Pesquisa de palavras — 5 especialidades</h1>
    <p class="sub">
      Temas para <strong>clinicadacidade.com.br</strong>: 1 especialidade por rodada,
      com 3–10 palavras diretas e 3–10 indiretas. Volumes mensais via DataForSEO (Google Ads · Brasil).
      Termos de marca concorrente (ex.: Unimed) foram excluídos.
    </p>
    <div class="meta">
      <span class="pill">Local: Brasil (2076)</span>
      <span class="pill">Fonte: DataForSEO · Google Ads</span>
      <span class="pill">Gerado em: {date.today().isoformat()}</span>
      <span class="pill">5 temas</span>
    </div>

    <div class="nav-shell">
      <div class="tabs" role="tablist" aria-label="Especialidades">
        {tabs}
      </div>
    </div>

    <section class="panel" id="panel-home" role="tabpanel">
      <div class="panel-head">
        <h2>Navegação pelos temas</h2>
        <p>Escolha uma especialidade nas abas acima ou clique em um card para abrir a pesquisa completa.</p>
      </div>
      <div class="overview" id="overview">
        {overview}
      </div>
    </section>

    {panels}

    <footer>
      Navegue pela aba <strong>Início</strong> ou pelas especialidades. Padrão: 1 tema + 3–10 diretas + 3–10 indiretas. Termos Unimed excluídos.
    </footer>
  </div>

  <script>
    function activate(key) {{
      document.querySelectorAll('.tab').forEach(btn => {{
        const on = btn.dataset.target === key;
        btn.setAttribute('aria-selected', on ? 'true' : 'false');
      }});
      document.querySelectorAll('.panel').forEach(panel => {{
        panel.hidden = panel.id !== 'panel-' + key;
      }});
      const el = document.getElementById('panel-' + key);
      if (el) el.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
    }}

    document.querySelectorAll('.tab').forEach(btn => {{
      btn.addEventListener('click', () => activate(btn.dataset.target));
    }});
    document.querySelectorAll('.overview-card').forEach(btn => {{
      btn.addEventListener('click', () => activate(btn.dataset.target));
    }});

    // start on home navigation
    activate('home');
  </script>
</body>
</html>
"""


def main():
    keywords = all_keywords()
    print(f"Total unique keywords: {len(keywords)}")
    by_kw = fetch_volumes(keywords)

    # save raw
    raw_path = OUT_DIR / "todos_temas_volumes.json"
    raw_path.write_text(json.dumps(by_kw, ensure_ascii=False, indent=2), encoding="utf-8")
    print("saved raw", raw_path)

    order = [
        "cardiologista",
        "dermatologista",
        "endocrinologista",
        "ginecologista",
        "oftalmologista",
    ]
    payloads = [build_theme_payload(k, THEMES[k], by_kw) for k in order]

    summary = []
    for p in payloads:
        summary.append(
            {
                "tema": p["key"],
                "volume_tema": p["tema"].get("search_volume"),
                "diretas": [
                    {"keyword": r["keyword"], "volume": r.get("search_volume")}
                    for r in p["diretas"]
                ],
                "indiretas": [
                    {"keyword": r["keyword"], "volume": r.get("search_volume")}
                    for r in p["indiretas"]
                ],
            }
        )
    summary_path = OUT_DIR / "todos_temas_resumo.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    html = build_html(payloads)
    html_path = OUT_DIR / "seo_keywords_especialidades.html"
    html_path.write_text(html, encoding="utf-8")
    print("HTML:", html_path)


if __name__ == "__main__":
    main()
