# -*- coding: utf-8 -*-
"""Final rebuild: stronger curated lists + theme fallbacks. No new API calls."""
import json
import sys
from pathlib import Path

sys.path.insert(0, r"C:\Users\Usuario\Desktop\clinica cidade\Blog seo")
sys.path.insert(0, r"C:\Users\Usuario\.cursor\skills\pesquisa-marca-dataforseo\scripts")

import build_all_themes as bat

OUT_DIR = Path(r"C:\Users\Usuario\Desktop\clinica cidade\Blog seo")
by_kw = json.loads((OUT_DIR / "todos_temas_volumes.json").read_text(encoding="utf-8"))

# Final curated sets — prefer terms with volume, still on-pattern, no unimed
bat.THEMES = {
    "cardiologista": {
        "label": "Cardiologista",
        "tema": "cardiologista",
        "tema_fallbacks": [],
        "diretas": [
            "o que é cardiologia",
            "o que faz o cardiologista",
            "quanto custa consulta cardiologista",
            "marcar consulta cardiologista",
            "medico do coracao",
            "cardiologista esportivo",
            "quando procurar um cardiologista",
            "consulta cardiologista",
        ],
        "indiretas": [
            "eletrocardiograma",
            "pressao alta",
            "dor no peito",
            "infarto",
            "teste ergometrico",
            "colesterol alto",
            "angina",
            "holter 24 horas",
            "palpitação",
            "fibrilacao atrial",
        ],
    },
    "dermatologista": {
        "label": "Dermatologista",
        "tema": "dermatologista",
        "tema_fallbacks": [],
        "diretas": [
            "o que é dermatologia",
            "o que faz o dermatologista",
            "quando procurar dermatologista",
            "dermatologista perto de mim",
            "biopsia de pele",
            "consulta dermatologista",
            "quanto custa consulta dermatologista",
            "dermatologista particular",
        ],
        "indiretas": [
            "dermatite",
            "alopecia",
            "psoriase",
            "micose",
            "rosacea",
            "melasma",
            "verruga",
            "acne",
            "queda de cabelo",
            "manchas na pele",
        ],
    },
    "endocrinologista": {
        "label": "Endocrinologista",
        "tema": "endocrinologista",
        "tema_fallbacks": ["endocrino", "endocrinologia"],
        "diretas": [
            "o que é endocrinologia",
            "o que faz o endocrinologista",
            "medico endocrinologista",
            "endocrinologista perto de mim",
            "endocrinologia",
            "quando procurar um endocrinologista",
            "consulta endocrinologista",
            "quanto custa consulta endocrinologista",
        ],
        "indiretas": [
            "diabetes",
            "diabetes tipo 2",
            "diabetes mellitus",
            "hipertireoidismo",
            "resistencia a insulina",
            "bocio",
            "tsh alto",
            "pre diabetes",
            "sindrome metabolica",
            "insulina alta",
        ],
    },
    "ginecologista": {
        "label": "Ginecologista",
        "tema": "ginecologista",
        "tema_fallbacks": ["ginecologia", "obstetra"],
        "diretas": [
            "o que é ginecologia",
            "obstetra",
            "ginecologia",
            "primeira consulta ginecologista",
            "quando procurar um ginecologista",
            "consulta ginecologista",
            "quanto custa consulta ginecologista",
            "ginecologista particular",
        ],
        "indiretas": [
            "candidiase",
            "hpv",
            "diu",
            "sop",
            "papanicolau",
            "menopausa",
            "tpm",
            "dismenorreia",
            "planejamento familiar",
            "ovario policistico",
        ],
    },
    "oftalmologista": {
        "label": "Oftalmologista",
        "tema": "oftalmologista",
        "tema_fallbacks": [],
        "diretas": [
            "o que é oftalmologia",
            "o que faz o oftalmologista",
            "consulta oftalmologista",
            "exame de vista",
            "valor consulta oftalmologista",
            "melhor oftalmologista",
            "quando procurar um oftalmologista",
            "oftalmologista particular",
        ],
        "indiretas": [
            "conjuntivite",
            "astigmatismo",
            "lentes de contato",
            "oculos de grau",
            "miopia",
            "estrabismo",
            "daltonismo",
            "olho seco",
            "pterigio",
            "fundo de olho",
        ],
    },
}

ALIASES = {
    "pressao alta": ["pressão alta"],
    "palpitação": ["palpitacao"],
    "fibrilacao atrial": ["fibrilação atrial"],
    "psoriase": ["psoríase"],
    "rosacea": ["rosácea"],
    "biopsia de pele": ["biopsia pele"],
    "resistencia a insulina": ["resistência à insulina"],
    "sindrome metabolica": ["síndrome metabólica"],
    "ovario policistico": ["ovário policístico", "ovarios policisticos"],
    "candidiase": ["candidíase"],
    "grau de oculos": ["grau de óculos"],
    "oculos de grau": ["óculos de grau"],
    "o que é cardiologia": ["o que e cardiologia"],
    "o que é dermatologia": ["o que e dermatologia"],
    "o que é endocrinologia": ["o que e endocrinologia", "endocrinologia"],
    "o que é ginecologia": ["o que e ginecologia", "ginecologia"],
    "o que é oftalmologia": ["o que e oftalmologia"],
    "quando procurar um cardiologista": ["quando procurar cardiologista"],
    "quando procurar dermatologista": ["quando procurar um dermatologista"],
    "quando procurar um endocrinologista": ["quando procurar endocrinologista"],
    "quando procurar um ginecologista": ["quando procurar ginecologista"],
    "quando procurar um oftalmologista": ["quando procurar oftalmologista"],
    "quanto custa consulta cardiologista": ["valor consulta cardiologista"],
    "quanto custa consulta dermatologista": ["valor consulta dermatologista"],
    "quanto custa consulta endocrinologista": ["valor consulta endocrinologista"],
    "quanto custa consulta ginecologista": ["valor consulta ginecologista"],
    "valor consulta oftalmologista": ["quanto custa consulta oftalmologista"],
    "bocio": ["bócio"],
}


def best_pick(primary, fallbacks=None):
    return bat.best_pick(by_kw, primary, list(fallbacks or []) + ALIASES.get(primary.lower(), []))


def build_theme(key, cfg):
    tema = best_pick(cfg["tema"], cfg.get("tema_fallbacks", []))
    # If theme itself has no volume but fallback matched, keep display as specialty name
    tema["keyword"] = cfg["tema"]

    diretas = [best_pick(k) for k in cfg["diretas"] if "unimed" not in k.lower()]
    indiretas = [best_pick(k) for k in cfg["indiretas"] if "unimed" not in k.lower()]
    return {
        "key": key,
        "label": cfg["label"],
        "tema": tema,
        "diretas": diretas,
        "indiretas": indiretas,
    }


order = [
    "cardiologista",
    "dermatologista",
    "endocrinologista",
    "ginecologista",
    "oftalmologista",
]
payloads = [build_theme(k, bat.THEMES[k]) for k in order]

for p in payloads:
    tv = p["tema"].get("search_volume")
    matched = p["tema"].get("matched_as")
    dv = sum(1 for r in p["diretas"] if r.get("search_volume") is not None)
    iv = sum(1 for r in p["indiretas"] if r.get("search_volume") is not None)
    print(
        f"{p['key']}: tema={tv}"
        + (f" (via {matched})" if matched else "")
        + f" | diretas {dv}/{len(p['diretas'])} | indiretas {iv}/{len(p['indiretas'])}"
    )
    for r in p["diretas"]:
        print(f"    D {r.get('search_volume') or '-':>8} | {r['keyword']}")
    for r in p["indiretas"]:
        print(f"    I {r.get('search_volume') or '-':>8} | {r['keyword']}")

summary = [
    {
        "tema": p["key"],
        "volume_tema": p["tema"].get("search_volume"),
        "volume_via": p["tema"].get("matched_as"),
        "diretas": [{"keyword": r["keyword"], "volume": r.get("search_volume")} for r in p["diretas"]],
        "indiretas": [{"keyword": r["keyword"], "volume": r.get("search_volume")} for r in p["indiretas"]],
    }
    for p in payloads
]
(OUT_DIR / "todos_temas_resumo.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
)

html = bat.build_html(payloads)
html_path = OUT_DIR / "seo_keywords_especialidades.html"
html_path.write_text(html, encoding="utf-8")
print("HTML:", html_path)
