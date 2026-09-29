# -*- coding: utf-8 -*-
import json
import sys
from pathlib import Path

sys.path.insert(0, r"C:\Users\Usuario\.cursor\skills\pesquisa-marca-dataforseo\scripts")
from client import RestClient

# Round of alternate / cleaned keywords to fill nulls
KEYWORDS = [
    # tema
    "cardiologista",
    "cardiologia",
    # diretas - variations
    "o que e cardiologia",
    "o que é cardiologia",
    "quando procurar cardiologista",
    "quando procurar um cardiologista",
    "valor consulta cardiologista",
    "preco consulta cardiologista",
    "preço consulta cardiologista",
    "consulta com cardiologista",
    "o que faz o cardiologista",
    "o que faz um cardiologista",
    "consulta cardiologista",
    "cardiologista particular",
    "exame com cardiologista",
    "cardiologista perto de mim",
    "melhor cardiologista",
    "sintomas cardiologista",
    "marcar consulta cardiologista",
    "cardiologista convenio",
    "cardiologista convênio",
    # indiretas
    "pressao alta",
    "pressão alta",
    "hipertensao",
    "hipertensão",
    "infarto",
    "infarto agudo do miocardio",
    "arritmia",
    "arritmia cardiaca",
    "arritmia cardíaca",
    "dor no peito",
    "dor no peito lado esquerdo",
    "ecocardiograma",
    "eco cardiograma",
    "insuficiencia cardiaca",
    "insuficiência cardíaca",
    "colesterol alto",
    "colesterol",
    "palpitacao",
    "palpitação",
    "palpitacoes",
    "palpitações",
    "eletrocardiograma",
    "ecg",
    "angina",
    "angina no peito",
    "taquicardia",
    "sopros no coracao",
    "sopro no coração",
]

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
print("status:", response.get("status_code"), response.get("status_message"), "cost:", response.get("cost"))
result = (response.get("tasks") or [{}])[0].get("result") or []
rows = []
for r in result:
    kw = r.get("keyword")
    vol = r.get("search_volume")
    ms = r.get("monthly_searches") or []
    monthly = {f"{m['year']}-{int(m['month']):02d}": m["search_volume"] for m in ms}
    latest = sorted(monthly.keys(), reverse=True)
    rows.append({
        "keyword": kw,
        "search_volume": vol,
        "cpc": r.get("cpc"),
        "competition": r.get("competition"),
        "competition_index": r.get("competition_index"),
        "latest_month": latest[0] if latest else None,
        "latest_volume": monthly[latest[0]] if latest else None,
        "monthly": monthly,
    })
    print(f"{vol if vol is not None else '-':>8} | {kw}")

out = Path(r"C:\Users\Usuario\Desktop\clinica cidade\Blog seo\cardiologista_volumes_v2.json")
out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
print("saved", out, "n=", len(rows))
