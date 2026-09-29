# -*- coding: utf-8 -*-
import json
import sys
from pathlib import Path

sys.path.insert(0, r"C:\Users\Usuario\.cursor\skills\pesquisa-marca-dataforseo\scripts")
from client import RestClient

OUT_DIR = Path(r"C:\Users\Usuario\Desktop\clinica cidade\Blog seo")

KEYWORDS = [
    # Tema
    "cardiologista",
    # Diretas
    "o que é cardiologia",
    "quando procurar um cardiologista",
    "qual valor da consulta com cardiologista",
    "o que faz um cardiologista",
    "consulta cardiologista",
    "cardiologista particular",
    "exame cardiologista",
    "sintomas para ir ao cardiologista",
    "melhor cardiologista",
    # Indiretas
    "pressão alta",
    "infarto",
    "arritmia cardíaca",
    "dor no peito",
    "ecocardiograma",
    "insuficiência cardíaca",
    "colesterol alto",
    "palpitação",
    "eletrocardiograma",
    "angina",
]

DIRECT = {
    "o que é cardiologia",
    "quando procurar um cardiologista",
    "qual valor da consulta com cardiologista",
    "o que faz um cardiologista",
    "consulta cardiologista",
    "cardiologista particular",
    "exame cardiologista",
    "sintomas para ir ao cardiologista",
    "melhor cardiologista",
}

INDIRECT = {
    "pressão alta",
    "infarto",
    "arritmia cardíaca",
    "dor no peito",
    "ecocardiograma",
    "insuficiência cardíaca",
    "colesterol alto",
    "palpitação",
    "eletrocardiograma",
    "angina",
}


def classify(kw: str) -> str:
    k = kw.lower()
    if k == "cardiologista":
        return "tema"
    if k in {x.lower() for x in DIRECT}:
        return "direta"
    if k in {x.lower() for x in INDIRECT}:
        return "indireta"
    # fuzzy fallback by content
    if "cardiolog" in k or "cardiologia" in k:
        return "direta"
    return "indireta"


def calculate_growth(new, old):
    if old in (None, 0) or new is None:
        return None
    return round(((new - old) / old) * 100, 2)


def main():
    client = RestClient("rafaelpiromdi@gmail.com", "def406af14eb9ac4")
    post_data = {
        0: {
            "location_code": 2076,
            "keywords": KEYWORDS,
            "date_from": "2020-01-01",
            "search_partners": False,
        }
    }
    response = client.post("/v3/keywords_data/google_ads/search_volume/live", post_data)
    print("status:", response.get("status_code"), response.get("status_message"))
    print("cost:", response.get("cost"))

    tasks = response.get("tasks") or []
    if not tasks:
        print(json.dumps(response, ensure_ascii=False, indent=2)[:3000])
        raise SystemExit(1)

    task = tasks[0]
    print("task:", task.get("status_code"), task.get("status_message"))
    result = task.get("result") or []
    print("n results:", len(result))

    rows = []
    for r in result:
        kw = r.get("keyword") or ""
        vol = r.get("search_volume")
        cpc = r.get("cpc")
        competition = r.get("competition")
        competition_index = r.get("competition_index")
        ms = r.get("monthly_searches") or []

        monthly = {}
        for m in ms:
            key = f"{m['year']}-{int(m['month']):02d}"
            monthly[key] = m["search_volume"]

        # snapshot months used by skill (best-effort)
        snap = {
            "2026-03": monthly.get("2026-03"),
            "2025-10": monthly.get("2025-10"),
            "2025-01": monthly.get("2025-01"),
            "2024-01": monthly.get("2024-01"),
            "2023-11": monthly.get("2023-11"),
            "2023-06": monthly.get("2023-06"),
            "2023-01": monthly.get("2023-01"),
            "2022-01": monthly.get("2022-01"),
            "2021-01": monthly.get("2021-01"),
            "2020-01": monthly.get("2020-01"),
        }

        latest_keys = sorted(monthly.keys(), reverse=True)
        latest_vol = monthly.get(latest_keys[0]) if latest_keys else vol
        latest_month = latest_keys[0] if latest_keys else None

        growth_6m = calculate_growth(snap["2026-03"], snap["2025-10"])
        growth_1y = calculate_growth(snap["2026-03"], snap["2025-01"])
        growth_2y = calculate_growth(snap["2026-03"], snap["2024-01"])

        # if 2026-03 missing, use latest vs ~6/12/24 months back
        if growth_6m is None and latest_month and len(latest_keys) >= 7:
            growth_6m = calculate_growth(monthly.get(latest_keys[0]), monthly.get(latest_keys[6]))
        if growth_1y is None and latest_month and len(latest_keys) >= 13:
            growth_1y = calculate_growth(monthly.get(latest_keys[0]), monthly.get(latest_keys[12]))

        row = {
            "keyword": kw,
            "tipo": classify(kw),
            "search_volume": vol,
            "latest_month": latest_month,
            "latest_volume": latest_vol,
            "cpc": cpc,
            "competition": competition,
            "competition_index": competition_index,
            "snapshots": snap,
            "growth_6m": growth_6m,
            "growth_1y": growth_1y,
            "growth_2y": growth_2y,
            "monthly": monthly,
        }
        rows.append(row)
        print(f"{row['tipo']:8} | {kw} | vol={vol} | latest={latest_month}:{latest_vol}")

    # preserve intended order
    order = {k.lower(): i for i, k in enumerate(KEYWORDS)}
    rows.sort(key=lambda x: order.get(x["keyword"].lower(), 999))

    out_json = OUT_DIR / "cardiologista_volumes.json"
    out_json.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print("saved", out_json)


if __name__ == "__main__":
    main()
