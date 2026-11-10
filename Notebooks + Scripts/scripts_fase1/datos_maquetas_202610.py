"""Datos reales de 2026-1 para las maquetas de visualización (Documentación/maquetas_visualizacion/).

Semestre calendario (D1-bis): una fila de Cirilo cuenta en la semana si está activa según
FECHA_INI2 / FECHA_TERM2 y es de pregrado o AV (sufijos 05/10/15/20/25, D3).
Ocupación de una celda = salas distintas usadas a la vez ÷ salas de esa clase en la planta física vigente.
Solo SALA y LABORATORIO; lunes a sábado; 19 bloques estándar.

Salidas (JSON, en Documentación/maquetas_visualizacion/datos/):
  matriz_semanas.json  · uso por campus × clase × día × bloque: mediana, p10 y p90 entre semanas del semestre
  salas_semana.json    · una semana de referencia, sala por sala (para el unit chart)
  quiebre.json         · pico de uso 2026-1 por campus × clase escalado con el crecimiento UG de Ariadna (ilustrativo)
Uso: py datos_maquetas_202610.py
"""
import json
import os

import numpy as np
import pandas as pd

R = "C:/Users/usuario/Documents/GitHub/QUERYs/Data Products - Machine Learning/"
AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(AQUI, "..", "..", "Documentación", "maquetas_visualizacion", "datos"))
os.makedirs(OUT, exist_ok=True)

DIAS = ["LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES", "SABADO"]
CLASES = ["SALA", "LABORATORIO"]
SEMANAS = pd.date_range("2026-03-16", "2026-07-06", freq="W-MON")   # semestre 2026-1 sin la primera semana
SEMANA_REF = pd.Timestamp("2026-04-13")
SUF = [5, 10, 15, 20, 25]

# --- insumos
c = pd.read_parquet(R + "Heat-Map/dash_app/BBDD/PROG_DETALLADA_PARA_HEATMAP.parquet",
                    columns=["PERIODO", "NRC", "MATERIA", "N_CURSO", "COMPONENTE", "INSCRITOS", "EDIFICIO", "SALA",
                             "FECHA_INI2", "FECHA_TERM2", "DIA_SESION", "BLOQUE", "CLASIFICACIÓN", "CAMPUS_AUX",
                             "Capacidad Máxima Sala_pd1"])
c = c.rename(columns={"CLASIFICACIÓN": "CLASE", "CAMPUS_AUX": "CAMPUS", "Capacidad Máxima Sala_pd1": "CAPACIDAD"})
c = c[(c.PERIODO // 100 == 2026) & (c.PERIODO % 100).isin(SUF) & c.CLASE.isin(CLASES) & c.DIA_SESION.isin(DIAS)]
c["SALA_ID"] = c.EDIFICIO.astype(str) + "·" + c.SALA.astype(str)

pf = pd.read_csv(R + "Heat-Map/dash_app/BBDD/PLANTA_FISICA_PREPROCESADA.csv", sep=None, engine="python")
pf = pf[(pf.Es_Mas_Actualizado == 1) & pf["CLASIFICACIÓN"].isin(CLASES) & (pf["Estado Sala"] == "ACTIVO")]
pf = pf.assign(CAMPUS=pf["Campus Edificio"], CLASE=pf["CLASIFICACIÓN"],
               SALA_ID=pf["Código Edificio"].astype(str) + "·" + pf["Número Sala"].astype(str),
               CAPACIDAD=pf["Capacidad Máxima Sala"])
inv = pf.groupby(["CAMPUS", "CLASE"]).SALA_ID.nunique().rename("DISPONIBLES")


def activas(semana):
    fin = semana + pd.Timedelta(days=5)
    return c[(c.FECHA_INI2 <= fin) & (c.FECHA_TERM2 >= semana)]


def uso_semana(semana):
    a = activas(semana)
    u = a.groupby(["CAMPUS", "CLASE", "DIA_SESION", "BLOQUE"]).SALA_ID.nunique().rename("USADAS")
    return u


# --- 1) matriz: variación entre semanas
filas = []
for s in SEMANAS:
    u = uso_semana(s).reset_index()
    u["SEMANA"] = s
    filas.append(u)
U = pd.concat(filas)
grid = pd.MultiIndex.from_product([inv.index.get_level_values(0).unique(), CLASES, DIAS, range(1, 20), SEMANAS],
                                  names=["CAMPUS", "CLASE", "DIA_SESION", "BLOQUE", "SEMANA"]).to_frame(index=False)
grid = grid.merge(inv.reset_index(), on=["CAMPUS", "CLASE"])
U = grid.merge(U, how="left", on=["CAMPUS", "CLASE", "DIA_SESION", "BLOQUE", "SEMANA"]).fillna({"USADAS": 0})
U["USO"] = U.USADAS / U.DISPONIBLES
M = (U.groupby(["CAMPUS", "CLASE", "DIA_SESION", "BLOQUE"])
     .agg(DISP=("DISPONIBLES", "first"), MED=("USO", "median"),
          P10=("USO", lambda x: x.quantile(.1)), P90=("USO", lambda x: x.quantile(.9)),
          USADAS_MED=("USADAS", "median"))
     .reset_index())
M = M[M.DISP >= 5]                                                      # campus × clase con al menos 5 salas
json.dump({"semanas": [s.strftime("%Y-%m-%d") for s in SEMANAS], "dias": DIAS,
           "celdas": M.round(4).to_dict(orient="records")},
          open(os.path.join(OUT, "matriz_semanas.json"), "w", encoding="utf-8"), ensure_ascii=False)

# --- 2) unit chart: semana de referencia, sala por sala
a = activas(SEMANA_REF)
oc = (a.groupby(["CAMPUS", "CLASE", "SALA_ID", "DIA_SESION", "BLOQUE"])
      .agg(INSCRITOS=("INSCRITOS", "max"), CAP=("CAPACIDAD", "first"), ASIG=("MATERIA", "first"),
           CURSO=("N_CURSO", "first"), COMP=("COMPONENTE", "first"))
      .reset_index())
oc["ASIG"] = oc.ASIG.astype(str) + oc.CURSO.astype(str)
salas = pf[["CAMPUS", "CLASE", "SALA_ID", "CAPACIDAD"]].drop_duplicates("SALA_ID")
salas["EDIFICIO"] = salas.SALA_ID.str.split("·").str[0]
json.dump({"semana": SEMANA_REF.strftime("%Y-%m-%d"), "dias": DIAS,
           "salas": salas.to_dict(orient="records"),
           "ocupacion": oc[["SALA_ID", "DIA_SESION", "BLOQUE", "INSCRITOS", "ASIG", "COMP"]].to_dict(orient="records")},
          open(os.path.join(OUT, "salas_semana.json"), "w", encoding="utf-8"), ensure_ascii=False, default=float)

# --- 3) año de quiebre (ilustrativo): pico de la mediana semanal × crecimiento UG de Ariadna por sede
ari = pd.read_parquet("C:/Users/usuario/Downloads/MODELO_PROYECCCIÓN_SIMPLE/PROYECCION_MATRICULA_2026_2031_28092026.parquet")
ari["periodo"] = ari.periodo.astype(int)
sedes = ari.drop_duplicates("sede").set_index("sede").desc_sede.str.strip().to_dict()
json.dump(sedes, open(os.path.join(OUT, "sedes.json"), "w", encoding="utf-8"), ensure_ascii=False)
ug = ari[(ari.periodo % 100 == 10) & (ari.nivel_academico == "UG") & (ari.tipo != "REAL")]
ug = ug.assign(ANIO=ug.periodo // 100).groupby(["sede", "ANIO"])[["n", "n_bajo", "n_alto"]].sum()
base26 = ug.xs(2026, level="ANIO").n
crec = ug.div(base26, axis=0, level="sede")
pico = M.groupby(["CAMPUS", "CLASE"]).agg(PICO=("MED", "max"), DISP=("DISP", "first")).reset_index()
serie = []
for r in pico.itertuples():
    if r.CAMPUS not in crec.index.get_level_values(0):
        continue
    g = crec.xs(r.CAMPUS, level="sede")
    for anio, f in g.iterrows():
        serie.append({"CAMPUS": r.CAMPUS, "CLASE": r.CLASE, "ANIO": int(anio), "DISP": int(r.DISP),
                      "BASE": r.PICO * f.n, "BAJO": r.PICO * f.n_bajo, "ALTO": r.PICO * f.n_alto})
json.dump({"serie": pd.DataFrame(serie).round(4).to_dict(orient="records")},
          open(os.path.join(OUT, "quiebre.json"), "w", encoding="utf-8"), ensure_ascii=False)

# --- control
print("inventario (SALA / LAB):"); print(inv.unstack().fillna(0).astype(int).to_string())
print("filas activas en la semana de referencia:", len(a), "· salas con uso:", a.SALA_ID.nunique())
fuera = set(a.SALA_ID) - set(pf.SALA_ID)
print("salas usadas que no están en la planta vigente:", len(fuera))
print("pico de la mediana semanal por campus × clase:")
print(pico.assign(PICO=lambda x: (x.PICO * 100).round(0)).to_string(index=False))
print("crecimiento UG 2031/2026 por sede (base):", crec.xs(2031, level="ANIO").n.round(3).to_dict())
