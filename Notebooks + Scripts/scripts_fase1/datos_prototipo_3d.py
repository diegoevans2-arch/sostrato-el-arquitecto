"""Datos del prototipo 3D de un campus (maqueta 4), a partir de la semana de referencia de la maqueta 3.

Piso de cada sala: regla sobre el código de sala de la planta física.
  código = letras del edificio + dígitos; el PRIMER DÍGITO es el piso (B105 → 1, C502 → 5, F001 → 0, ECD110 → 1).
  Sufijos de subdivisión (C310A, D404-A, Q002-B) no cambian el piso.
Es una inferencia: no hay planos que la confirmen. El script informa cuántas salas la cumplen.
Correr antes: datos_maquetas_202610.py. Uso: py datos_prototipo_3d.py [CAMPUS]   (por defecto C01)
"""
import json
import os
import re
import sys

import pandas as pd

CAMPUS = sys.argv[1] if len(sys.argv) > 1 else "C01"
AQUI = os.path.dirname(os.path.abspath(__file__))
DATOS = os.path.normpath(os.path.join(AQUI, "..", "..", "Documentación", "maquetas_visualizacion", "datos"))
PATRON = re.compile(r"^([A-Z]+) ?(\d)(\d*)([-A-Z]*)$")   # admite «D 102»

d = json.load(open(os.path.join(DATOS, "salas_semana.json"), encoding="utf-8"))
salas = pd.DataFrame(d["salas"])
salas = salas[salas.CAMPUS == CAMPUS].copy()
salas["CODIGO"] = salas.SALA_ID.str.split("·").str[1]
m = salas.CODIGO.str.extract(PATRON)
salas["PISO"] = pd.to_numeric(m[1])
salas["REGLA_OK"] = m[0].notna()

ok = salas.REGLA_OK.mean()
print(f"{CAMPUS}: {len(salas)} salas · cumplen la regla de piso: {salas.REGLA_OK.sum()} ({ok:.0%})")
print("sin piso:", salas.loc[~salas.REGLA_OK, "SALA_ID"].tolist())
print(salas.groupby(["EDIFICIO", "PISO"]).size().unstack(fill_value=0).to_string())

salas = salas[salas.REGLA_OK]
ids = set(salas.SALA_ID)
oc = [o for o in d["ocupacion"] if o["SALA_ID"] in ids]
json.dump({"campus": CAMPUS, "semana": d["semana"], "dias": d["dias"],
           "salas": salas[["SALA_ID", "EDIFICIO", "CLASE", "CAPACIDAD", "CODIGO", "PISO"]].to_dict(orient="records"),
           "ocupacion": oc},
          open(os.path.join(DATOS, f"campus3d_{CAMPUS}.json"), "w", encoding="utf-8"), ensure_ascii=False, default=float)
print("ocupaciones:", len(oc))
