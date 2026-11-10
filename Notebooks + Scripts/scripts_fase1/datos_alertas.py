"""Datos de la simulación de alertas (vistas A1–A4 de la demo) desde BBDD/, sin modificar BBDD.

Decisiones de visualización confirmadas por Diego el 27-10 (V1–V4):
  V1 semáforo sobre PROB_SATURA_TAMANO: vigilancia ≥ 10 %, ALERTA ≥ 25 % (la que se informa), crítica ≥ 50 %
  V2 escenario base por defecto · V3 reproductor común · V4 filtro de tamaño (OCUPACION_POR_RANGO, acumulado hacia arriba)
Cómo se cuenta: cada escenario por separado; nunca se suman P10/P90 entre celdas.
Déficit y sobrecupo: ponderados por PESO_SEMANAS (igual que el equipo de modelo), solo escenario base.

Salidas en Documentación/maquetas_visualizacion/datos/:
  alertas_celdas.json  · mapa de alertas: por campus × clase × período × escenario, 6 días × 20 bloques
  alertas_serie.json   · curva de alertas: celdas sobre cada umbral, y déficit / sobrecupo / déficit por rango
  prog_<CAMPUS>.json   · programación sintética (base, sufijos 10 y 20) sala por sala, para A3 y A4
Uso: py datos_alertas.py
"""
import json
import os
import re

import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.normpath(os.path.join(AQUI, "..", ".."))
BBDD = os.path.join(RAIZ, "BBDD")
OUT = os.path.join(RAIZ, "Documentación", "maquetas_visualizacion", "datos")
DIAS = ["LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES", "SABADO"]
RANGOS = ["0-20", "21-40", "41-60", "60 o más"]
CLASES = ["SALA", "LABORATORIO"]
NB = 20                                                     # bloques 0–19
UMBRALES = (0.10, 0.25, 0.50)
dump = lambda obj, nombre: json.dump(obj, open(os.path.join(OUT, nombre), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))

# ---------------------------------------------------------------- mapa y ocupación por rango
o = pd.read_parquet(os.path.join(BBDD, "OCUPACION_Y_DEFICIT.parquet"))
o = o[o.DIA.isin(DIAS) & o.CLASE.isin(CLASES)]
r = pd.read_parquet(os.path.join(BBDD, "OCUPACION_POR_RANGO.parquet"))
r = r[r.DIA.isin(DIAS) & r.CLASE.isin(CLASES)]
K = ["COD_CAMPUS_EDIFICIO", "CLASE", "PERIODO", "ESCENARIO", "DIA", "BLOQUE"]
pr = r.pivot_table(index=K, columns="RANGO_DESDE", values=["PROB_SATURA_ACUM", "DEMANDA_ACUM_P50"], aggfunc="first")
pr.columns = [f"{a}|{b}" for a, b in pr.columns]
o = o.merge(pr.reset_index(), on=K, how="left")
# oferta acumulada por rango: constante por campus × clase (se toma el máximo observado)
esp = r.groupby(["COD_CAMPUS_EDIFICIO", "CLASE", "RANGO_DESDE"]).ESPACIOS_ACUM.max()

campus = sorted(o.COD_CAMPUS_EDIFICIO.unique())
periodos = sorted(o.PERIODO.unique())
o["DI"] = o.DIA.map({d: i for i, d in enumerate(DIAS)})
o["RC"] = o.RANGO_CRITICO.map({x: i for i, x in enumerate(RANGOS)}).fillna(0).astype(int)
pct = lambda s: np.round(s.fillna(0) * 100).astype(int)
dec = lambda s: np.round(s.fillna(0) * 10).astype(int)
CAMPOS = ["PT", "RC", "P10", "P50", "P90", "A0", "A1", "A2", "A3", "D0", "D1", "D2", "D3"]   # 13 enteros por celda (A0 = PROB_SATURA, rango 0-20)
o["PT"], o["P10"], o["P50"], o["P90"] = pct(o.PROB_SATURA_TAMANO), dec(o.OCUPACION_P10), dec(o.OCUPACION_P50), dec(o.OCUPACION_P90)
o["A0"] = pct(o.PROB_SATURA)
for i, rg in enumerate(RANGOS):
    if i:
        o[f"A{i}"] = pct(o.get(f"PROB_SATURA_ACUM|{rg}", pd.Series(0, index=o.index)))
    o[f"D{i}"] = dec(o.get(f"DEMANDA_ACUM_P50|{rg}", pd.Series(0, index=o.index)))

celdas, meta_val, cap = {}, {}, {}
for (c, cl, per, esc), g in o.groupby(["COD_CAMPUS_EDIFICIO", "CLASE", "PERIODO", "ESCENARIO"]):
    flat = np.zeros((len(DIAS), NB, len(CAMPOS)), dtype=int)
    flat[g.DI.values, g.BLOQUE.values] = g[CAMPOS].values
    celdas[f"{c}|{cl}|{per}|{esc}"] = flat.ravel().tolist()
    meta_val[str(per)] = bool(g.VALIDADO.iloc[0])
    cap[f"{c}|{cl}"] = int(g.CAPACIDAD.max())
espd = {f"{c}|{cl}": [int(esp.get((c, cl, rg), 0)) for rg in RANGOS] for c in campus for cl in CLASES}
dump({"campus": campus, "clases": CLASES, "periodos": [int(p) for p in periodos], "escenarios": ["bajo", "base", "alto"],
      "dias": DIAS, "rangos": RANGOS, "campos": CAMPOS, "validado": meta_val, "cap": cap, "esp": espd, "celdas": celdas},
     "alertas_celdas.json")

# ---------------------------------------------------------------- curva: celdas sobre cada umbral
serie = {}
for i, rg in enumerate(["todos"] + RANGOS):
    col = "PROB_SATURA_TAMANO" if rg == "todos" else ("PROB_SATURA" if rg == "0-20" else f"PROB_SATURA_ACUM|{rg}")
    v = o[col].fillna(0)
    for u in UMBRALES:
        o[f"U{int(u*100)}"] = v >= u
    for clave, g in [(k, g) for k, g in o.groupby(["COD_CAMPUS_EDIFICIO", "CLASE", "PERIODO", "ESCENARIO"])]:
        serie[f"{clave[0]}|{clave[1]}|{clave[2]}|{clave[3]}|{rg}"] = [int(g[f"U{int(u*100)}"].sum()) for u in UMBRALES]
    for clave, g in o.groupby(["PERIODO", "ESCENARIO"]):
        serie[f"TODOS|*|{clave[0]}|{clave[1]}|{rg}"] = [int(g[f"U{int(u*100)}"].sum()) for u in UMBRALES]
    for clave, g in o.groupby(["COD_CAMPUS_EDIFICIO", "PERIODO", "ESCENARIO"]):
        serie[f"{clave[0]}|*|{clave[1]}|{clave[2]}|{rg}"] = [int(g[f"U{int(u*100)}"].sum()) for u in UMBRALES]

p = pd.read_parquet(os.path.join(BBDD, "PROGRAMACION_SINTETICA.parquet"))
p = p[p.CLASE.isin(CLASES)]
def tasas(g):
    w = g.PESO_SEMANAS
    dr = g[g.DEFICIT].groupby("RANGO_DEMANDADO").PESO_SEMANAS.sum()
    tot = dr.sum() or 1
    return [round(float((w * g.DEFICIT).sum() / w.sum()), 4), round(float((w * g.SOBRECUPO).sum() / w.sum()), 4),
            [round(float(dr.get(rg, 0) / tot), 3) for rg in RANGOS]]
deficit = {}
for (c, per), g in p.groupby(["COD_CAMPUS_EDIFICIO", "PERIODO"]):
    deficit[f"{c}|{per}"] = tasas(g)
for per, g in p.groupby("PERIODO"):
    deficit[f"TODOS|{per}"] = tasas(g)
dump({"umbrales": [10, 25, 50], "rangos": ["todos"] + RANGOS, "validado": meta_val, "serie": serie, "deficit": deficit},
     "alertas_serie.json")

# ---------------------------------------------------------------- programación proyectada por campus (A3, A4)
f = pd.read_parquet(os.path.join(BBDD, "OFERTA_ESPACIOS.parquet"))
f = f[f.ACTIVO & f.CLASE_MAPA.isin(CLASES)]
PATRON = re.compile(r"^([A-Z]+) ?(\d)(\d*)([-A-Z]*)$")
def piso(cod):
    m = PATRON.match(str(cod)); return int(m.group(2)) if m else 1
ps = p[(p.PERIODO % 100).isin([10, 20]) & p.DIA.isin(DIAS)]     # vistas sala por sala: lunes a sábado (los % de arriba usan todo)
for c in campus:
    inv = f[f.COD_CAMPUS_EDIFICIO == c].copy()
    inv["SALA_ID"] = inv.EDIFICIO + "·" + inv.SALA
    inv = inv.drop_duplicates("SALA_ID").sort_values(["CLASE_MAPA", "EDIFICIO", "SALA"])
    idx = {s: i for i, s in enumerate(inv.SALA_ID)}
    g = ps[ps.COD_CAMPUS_EDIFICIO == c]
    materias = sorted(g.MATERIA.dropna().unique())
    mi = {m: i for i, m in enumerate(materias)}
    ocup, defi = {}, {}
    for per, h in g.groupby("PERIODO"):
        a = h[~h.DEFICIT]
        ids = (a.EDIFICIO + "·" + a.SALA).map(idx)
        a = a[ids.notna()]; ids = ids[ids.notna()].astype(int)
        ocup[str(per)] = np.column_stack([ids, a.DIA.map(DIAS.index), a.BLOQUE, a.INSCRITOS_EST, a.MATERIA.map(mi), a.SOBRECUPO.astype(int)]).ravel().tolist()
        d = h[h.DEFICIT]
        defi[str(per)] = np.column_stack([d.DIA.map(DIAS.index), d.BLOQUE, d.RANGO_DEMANDADO.map(RANGOS.index).fillna(0).astype(int),
                                          d.INSCRITOS_EST, d.MATERIA.map(mi), d.CLASE.map(CLASES.index)]).ravel().tolist()
    salas = [{"SALA_ID": s, "EDIFICIO": e, "CODIGO": cod, "CLASE": cl, "CAPACIDAD": int(cp), "PISO": piso(cod), "RANGO": rg}
             for s, e, cod, cl, cp, rg in zip(inv.SALA_ID, inv.EDIFICIO, inv.SALA, inv.CLASE_MAPA, inv.CAPACIDAD, inv.RANGO_CAPACIDAD)]
    dump({"campus": c, "dias": DIAS, "rangos": RANGOS, "clases": CLASES, "materias": materias, "salas": salas,
          "validado": {k: v for k, v in meta_val.items() if int(k) % 100 in (10, 20)}, "ocup": ocup, "deficit": defi,
          "campos_ocup": ["sala", "dia", "bloque", "inscritos", "materia", "sobrecupo"],
          "campos_deficit": ["dia", "bloque", "rango", "inscritos", "materia", "clase"]}, f"prog_{c}.json")
    print(f"prog_{c}: {len(salas)} salas · {sum(len(v) for v in ocup.values()) // 6} asignaciones · {sum(len(v) for v in defi.values()) // 6} en déficit")

# ---------------------------------------------------------------- control contra las cifras ancla del equipo de modelo
b = {int(k.split("|")[2]) // 100: v for k, v in serie.items() if k.startswith("TODOS|*|") and k.endswith("|base|todos") and int(k.split("|")[2]) % 100 == 10}
print("celdas ≥10/25/50 % (base, sufijo 10, todos los tamaños):", dict(sorted(b.items())))
print("déficit / sobrecupo (base, sufijo 10):", {int(k.split("|")[1]) // 100: v[:2] for k, v in deficit.items() if k.startswith("TODOS|") and int(k.split("|")[1]) % 100 == 10})
for n in ("alertas_celdas.json", "alertas_serie.json"):
    print(n, f"{os.path.getsize(os.path.join(OUT, n)) / 1e6:.2f} MB")
