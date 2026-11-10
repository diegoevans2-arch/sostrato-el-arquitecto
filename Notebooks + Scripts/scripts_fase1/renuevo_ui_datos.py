"""Propuesta de renuevo UI: saca los datos ya incrustados en las maquetas A1 y A2 a un solo archivo.

Entrada:  Documentación/maquetas_visualizacion/A1_curva_alertas.html y A2_mapa_alertas.html
Salida:   Documentación/renuevo_ui/renuevo_datos.js

Los espacios por tamaño (A.esp) se rehacen desde BBDD: la maqueta toma el máximo de ESPACIOS_ACUM, que queda en 0 donde no hay
filas (laboratorios sin demanda de ese tamaño) y por encima de los activos donde el modelo usa una oferta efectiva por celda.
"""
import json
import pathlib
import re

import pandas as pd

RAIZ = pathlib.Path(__file__).resolve().parents[2]
BASE, BBDD = RAIZ / "Documentación", RAIZ / "BBDD"
ORIGEN, DESTINO = BASE / "maquetas_visualizacion", BASE / "renuevo_ui"


def constante(texto, nombre):
    return re.search(rf"^const {nombre} = (.*?);?\s*$", texto, re.M).group(1)


def oferta(A):
    """Espacios activos por tamaño (r o más) y, aparte, las celdas donde el modelo usa una oferta efectiva mayor."""
    f = pd.read_parquet(BBDD / "OFERTA_ESPACIOS.parquet")
    f = f[f.ACTIVO & f.CLASE_MAPA.isin(A["clases"])].drop_duplicates(["EDIFICIO", "SALA"])
    rg = A["rangos"]
    esp = {f"{c}|{cl}": [int(((f.COD_CAMPUS_EDIFICIO == c) & (f.CLASE_MAPA == cl) & f.RANGO_CAPACIDAD.isin(rg[i:])).sum()) for i in range(len(rg))]
           for c in A["campus"] for cl in A["clases"]}
    r = pd.read_parquet(BBDD / "OCUPACION_POR_RANGO.parquet")
    r = r[r.DIA.isin(A["dias"]) & r.CLASE.isin(A["clases"]) & (r.RANGO_DESDE != rg[0])]
    efectiva = {}
    for t in r.itertuples():
        i = rg.index(t.RANGO_DESDE)
        if t.ESPACIOS_ACUM > esp[f"{t.COD_CAMPUS_EDIFICIO}|{t.CLASE}"][i] + 1e-6:
            efectiva[f"{t.COD_CAMPUS_EDIFICIO}|{t.CLASE}|{i}|{t.PERIODO % 100}|{A['dias'].index(t.DIA)}|{t.BLOQUE}"] = round(float(t.ESPACIOS_ACUM), 1)
    return esp, efectiva


def main():
    a1 = (ORIGEN / "A1_curva_alertas.html").read_text(encoding="utf-8")
    a2 = (ORIGEN / "A2_mapa_alertas.html").read_text(encoding="utf-8")
    A = json.loads(constante(a2, "A"))
    A["esp"], efectiva = oferta(A)
    print(len(efectiva), "celdas con oferta efectiva mayor que los activos")
    salida = [f"window.S = {constante(a1, 'S')};", f"window.SEDES = {constante(a1, 'SEDES')};",
              f"window.A = {json.dumps(A, ensure_ascii=False, separators=(',', ':'))};",
              f"window.OFERTA_EFECTIVA = {json.dumps(efectiva, separators=(',', ':'))};"]
    salida += [f"window.{n} = {re.search(rf'\b{n} = (\[.*?\])', a2).group(1)};" for n in ("HORAS", "DCORTO", "DLARGO")]
    DESTINO.mkdir(exist_ok=True)
    (DESTINO / "renuevo_datos.js").write_text("\n".join(salida) + "\n", encoding="utf-8", newline="")
    print((DESTINO / "renuevo_datos.js").stat().st_size // 1024, "KB")
    # la programación sintética pesa, así que va un archivo por campus y se carga al entrar a él
    for f in sorted(ORIGEN.glob("A3_programacion_proyectada_*.html")):
        campus = f.stem.rsplit("_", 1)[1]
        p = constante(f.read_text(encoding="utf-8"), "P")
        (DESTINO / f"salas_{campus}.js").write_text(f"window.PROG = window.PROG || {{}}; window.PROG.{campus} = {p};\n", encoding="utf-8", newline="")


if __name__ == "__main__":
    main()
