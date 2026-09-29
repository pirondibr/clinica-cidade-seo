# -*- coding: utf-8 -*-
"""Gap-fill keywords that returned null, then rebuild HTML."""
import json
import sys
from pathlib import Path

sys.path.insert(0, r"C:\Users\Usuario\Desktop\clinica cidade\Blog seo")
sys.path.insert(0, r"C:\Users\Usuario\.cursor\skills\pesquisa-marca-dataforseo\scripts")

from client import RestClient
import build_all_themes as bat

OUT_DIR = Path(r"C:\Users\Usuario\Desktop\clinica cidade\Blog seo")

GAP_KEYWORDS = [
    # themes missing
    "endocrinologista",
    "ginecologista",
    "endocrino",
    "ginecologia",
    "endocrinologia",
    # cardio fill diretas
    "cardiologista particular",
    "exame cardiologista",
    "sintomas cardiologista",
    # derm fill diretas
    "dermatologia",
    "clinica dermatologica",
    "dermatologista infantil",
    "tratamento acne dermatologista",
    "preco consulta dermatologista",
    "dermatologista perto de mim",
    # endo
    "hipotireoidismo",
    "hipotiroidismo",
    "tireoide",
    "tiroide",
    "obesidade",
    "hashimoto",
    "doenca de hashimoto",
    "nódulo tireoide",
    "nodulo tireoide",
    "bócio",
    "bocio",
    "tsh alto",
    "insulina alta",
    "diabetes mellitus",
    "endocrinologista infantil",
    "endocrinologista perto de mim",
    "melhor endocrinologista",
    # gineco
    "endometriose",
    "mioma",
    "mioma uterino",
    "corrimento vaginal",
    "colposcopia",
    "ovarios policisticos",
    "sindrome dos ovarios policisticos",
    "sop ovario",
    "candidiase vaginal",
    "fluxo vaginal",
    "tpm",
    "dismenorreia",
    "sangramento uterino",
    "hpv",
    "ginecologista perto de mim",
    "melhor ginecologista",
    "obstetra",
    # oftalmo
    "catarata",
    "glaucoma",
    "cirurgia de catarata",
    "cirurgia catarata",
    "ceratocone",
    "degeneracao macular",
    "dmri",
    "retinopatia",
    "retinopatia diabetica",
    "pressao intraocular",
    "daltonismo",
    "estrabismo",
    "lentes de contato",
    "oculos de grau",
    "óculos de grau",
    "oftalmologista perto de mim",
    "melhor oftalmologista",
]


def main():
    raw_path = OUT_DIR / "todos_temas_volumes.json"
    by_kw = json.loads(raw_path.read_text(encoding="utf-8"))

    client = RestClient("rafaelpiromdi@gmail.com", "def406af14eb9ac4")
    # only fetch missing / new
    to_fetch = []
    seen = set()
    for k in GAP_KEYWORDS:
        kl = k.lower()
        if kl in seen:
            continue
        seen.add(kl)
        existing = by_kw.get(kl)
        if existing and existing.get("search_volume") is not None:
            continue
        to_fetch.append(k)

    print(f"Fetching {len(to_fetch)} gap keywords...")
    if to_fetch:
        post_data = {
            0: {
                "location_code": 2076,
                "keywords": to_fetch,
                "date_from": "2020-01-01",
                "search_partners": False,
            }
        }
        response = client.post("/v3/keywords_data/google_ads/search_volume/live", post_data)
        print("status", response.get("status_code"), "cost", response.get("cost"))
        result = (response.get("tasks") or [{}])[0].get("result") or []
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

    raw_path.write_text(json.dumps(by_kw, ensure_ascii=False, indent=2), encoding="utf-8")

    # Improve curated lists: replace weak/null diretas with stronger alternates where needed
    # Update THEMES indiretas aliases via best_pick extras in rebuild

    # Swap weak cardio direta
    bat.THEMES["cardiologista"]["diretas"] = [
        "o que é cardiologia",
        "o que faz o cardiologista",
        "quanto custa consulta cardiologista",
        "marcar consulta cardiologista",
        "quando procurar um cardiologista",
        "medico do coracao",
        "cardiologista esportivo",
        "cardiologista particular",
    ]

    bat.THEMES["dermatologista"]["diretas"] = [
        "o que é dermatologia",
        "o que faz o dermatologista",
        "quando procurar dermatologista",
        "quanto custa consulta dermatologista",
        "marcar consulta dermatologista",
        "consulta dermatologista",
        "dermatologista particular",
        "dermatologista infantil",
    ]

    bat.THEMES["endocrinologista"]["diretas"] = [
        "o que é endocrinologia",
        "o que faz o endocrinologista",
        "quando procurar um endocrinologista",
        "quanto custa consulta endocrinologista",
        "medico endocrinologista",
        "endocrinologista particular",
        "endocrinologista infantil",
        "melhor endocrinologista",
    ]
    bat.THEMES["endocrinologista"]["indiretas"] = [
        "diabetes",
        "hipertireoidismo",
        "resistencia a insulina",
        "sindrome metabolica",
        "diabetes tipo 2",
        "pre diabetes",
        "tiroide",
        "tsh alto",
        "bocio",
        "colesterol alto",
    ]

    bat.THEMES["ginecologista"]["diretas"] = [
        "o que é ginecologia",
        "o que faz o ginecologista",
        "quando procurar um ginecologista",
        "quanto custa consulta ginecologista",
        "primeira consulta ginecologista",
        "ginecologista particular",
        "melhor ginecologista",
        "obstetra",
    ]
    bat.THEMES["ginecologista"]["indiretas"] = [
        "candidiase",
        "diu",
        "sop",
        "papanicolau",
        "menopausa",
        "hpv",
        "ovario policistico",
        "planejamento familiar",
        "tpm",
        "ciclo menstrual irregular",
    ]

    bat.THEMES["oftalmologista"]["diretas"] = [
        "o que é oftalmologia",
        "o que faz o oftalmologista",
        "consulta oftalmologista",
        "exame de vista",
        "valor consulta oftalmologista",
        "quando procurar um oftalmologista",
        "oftalmologista particular",
        "melhor oftalmologista",
    ]
    bat.THEMES["oftalmologista"]["indiretas"] = [
        "conjuntivite",
        "astigmatismo",
        "miopia",
        "olho seco",
        "grau de oculos",
        "fundo de olho",
        "pterigio",
        "lentes de contato",
        "oculos de grau",
        "estrabismo",
    ]

    # extend aliases
    extra_aliases = {
        "cardiologista particular": ["cardiologista particular"],
        "quando procurar dermatologista": ["quando procurar um dermatologista"],
        "dermatologista infantil": [],
        "medico endocrinologista": [],
        "endocrinologista infantil": [],
        "melhor endocrinologista": [],
        "tiroide": ["tireoide"],
        "tsh alto": [],
        "bocio": ["bócio"],
        "obstetra": [],
        "melhor ginecologista": [],
        "hpv": [],
        "tpm": [],
        "diu": [],
        "valor consulta oftalmologista": ["quanto custa consulta oftalmologista"],
        "melhor oftalmologista": [],
        "lentes de contato": [],
        "oculos de grau": ["óculos de grau"],
        "estrabismo": [],
        "pterigio": [],
        "fundo de olho": [],
    }

    # monkeypatch best_pick aliases by injecting into build_theme_payload via THEMES extras already used
    # Rebuild using updated aliases dict inside build_theme_payload — patch function
    original_build = bat.build_theme_payload

    def build_theme_payload(key, cfg, data):
        # temporarily expand aliases used inside by wrapping best_pick calls
        payloads_aliases = extra_aliases

        def best_pick(data_map, primary, alternates=None):
            alts = list(alternates or []) + list(payloads_aliases.get(primary.lower(), []))
            return bat.best_pick(data_map, primary, alts)

        # replicate original with our best_pick
        aliases = {
            "pressao alta": ["pressão alta"],
            "palpitação": ["palpitacao"],
            "fibrilacao atrial": ["fibrilação atrial"],
            "psoriase": ["psoríase"],
            "rosacea": ["rosácea"],
            "biopsia de pele": ["biopsia pele"],
            "resistencia a insulina": ["resistência à insulina"],
            "sindrome metabolica": ["síndrome metabólica"],
            "nodulo na tireoide": ["nódulo na tireoide", "nodulo tireoide"],
            "endometriose": [],
            "ovario policistico": ["ovário policístico", "ovarios policisticos"],
            "candidiase": ["candidíase", "candidiase vaginal"],
            "degeneracao macular": ["degeneração macular", "dmri"],
            "retinopatia diabetica": ["retinopatia diabética", "retinopatia"],
            "grau de oculos": ["grau de óculos"],
            "o que é cardiologia": ["o que e cardiologia"],
            "o que é dermatologia": ["o que e dermatologia"],
            "o que é endocrinologia": ["o que e endocrinologia"],
            "o que é ginecologia": ["o que e ginecologia"],
            "o que é oftalmologia": ["o que e oftalmologia"],
            "quando procurar um cardiologista": ["quando procurar cardiologista"],
            "quando procurar um dermatologista": ["quando procurar dermatologista"],
            "quando procurar dermatologista": ["quando procurar um dermatologista"],
            "quando procurar um endocrinologista": ["quando procurar endocrinologista"],
            "quando procurar um ginecologista": ["quando procurar ginecologista"],
            "quando procurar um oftalmologista": ["quando procurar oftalmologista"],
            "quanto custa consulta cardiologista": ["valor consulta cardiologista"],
            "quanto custa consulta dermatologista": ["valor consulta dermatologista", "preco consulta dermatologista"],
            "quanto custa consulta endocrinologista": ["valor consulta endocrinologista"],
            "quanto custa consulta ginecologista": ["valor consulta ginecologista"],
            "quanto custa consulta oftalmologista": ["valor consulta oftalmologista"],
            "valor consulta oftalmologista": ["quanto custa consulta oftalmologista"],
            "oculos de grau": ["óculos de grau"],
            "bocio": ["bócio"],
        }
        aliases.update(extra_aliases)

        diretas = [k for k in cfg["diretas"] if "unimed" not in k.lower()]
        indiretas = [k for k in cfg["indiretas"] if "unimed" not in k.lower()]

        tema = best_pick(data, cfg["tema"])
        diretas_rows = [best_pick(data, k, aliases.get(k.lower(), [])) for k in diretas]
        indiretas_rows = [best_pick(data, k, aliases.get(k.lower(), [])) for k in indiretas]

        return {
            "key": key,
            "label": cfg["label"],
            "tema": tema,
            "diretas": diretas_rows,
            "indiretas": indiretas_rows,
        }

    order = [
        "cardiologista",
        "dermatologista",
        "endocrinologista",
        "ginecologista",
        "oftalmologista",
    ]
    payloads = [build_theme_payload(k, bat.THEMES[k], by_kw) for k in order]

    for p in payloads:
        tv = p["tema"].get("search_volume")
        dv = sum(1 for r in p["diretas"] if r.get("search_volume") is not None)
        iv = sum(1 for r in p["indiretas"] if r.get("search_volume") is not None)
        print(f"{p['key']}: tema={tv} | diretas com vol {dv}/{len(p['diretas'])} | indiretas {iv}/{len(p['indiretas'])}")

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
    (OUT_DIR / "todos_temas_resumo.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    html = bat.build_html(payloads)
    html_path = OUT_DIR / "seo_keywords_especialidades.html"
    html_path.write_text(html, encoding="utf-8")
    print("HTML:", html_path)


if __name__ == "__main__":
    main()
