# -*- coding: utf-8 -*-
import json
import sys
from pathlib import Path

sys.path.insert(0, r"C:\Users\Usuario\.cursor\skills\pesquisa-marca-dataforseo\scripts")
from client import RestClient

KEYWORDS = [
    # more diretas
    "cardiologista online",
    "cardiologista infantil",
    "cardiologista esportivo",
    "cardiologista quanto custa",
    "quanto custa consulta cardiologista",
    "valor da consulta cardiologista",
    "cardiologista sus",
    "cardiologista unimed",
    "medico do coracao",
    "médico do coração",
    "especialista do coracao",
    "especialista do coração",
    # more indiretas common
    "arritmia",
    "arritmias",
    "fibrilacao atrial",
    "fibrilação atrial",
    "ecocardiograma",
    "ecocardiograma com doppler",
    "teste ergometrico",
    "teste ergométrico",
    "holter 24 horas",
    "mapas 24 horas",
    "mapa 24 horas",
    "taquicardia",
    "bradicardia",
    "sopros cardiacos",
    "sopro cardiaco",
    "sopro no coracao",
    "insuficiencia cardiaca congestiva",
    "doenca coronariana",
    "doença coronariana",
    "avc",
    "derrame",
    "miocardite",
    "pericardite",
    "varizes",
    "trombose",
    "falta de ar",
    "cansaco excessivo",
    "cansaço excessivo",
    "inchaço nas pernas",
    "inchaco nas pernas",
    "pressao arterial",
    "pressão arterial",
    "hipertensao arterial",
    "hipertensão arterial",
    "infarto do miocardio",
    "infarto do miocárdio",
    "ataque cardiaco",
    "ataque cardíaco",
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
print("status:", response.get("status_code"), "cost:", response.get("cost"))
result = (response.get("tasks") or [{}])[0].get("result") or []
rows = []
for r in sorted(result, key=lambda x: -(x.get("search_volume") or 0)):
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
    mark = f"{vol:>8}" if vol is not None else "       -"
    print(f"{mark} | {kw}")

out = Path(r"C:\Users\Usuario\Desktop\clinica cidade\Blog seo\cardiologista_volumes_v3.json")
out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
print("saved", out)
