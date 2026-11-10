"""Arma las maquetas HTML autocontenidas (datos incrustados) en Documentación/maquetas_visualizacion/.
Correr antes: datos_maquetas_202610.py. Uso: py construir_maquetas.py
"""
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
PLANT = os.path.join(AQUI, "maquetas_plantillas")
DEST = os.path.normpath(os.path.join(AQUI, "..", "..", "Documentación", "maquetas_visualizacion"))
DATOS = os.path.join(DEST, "datos")
MAQUETAS = {"M1_linea_tiempo_quiebre.html": "quiebre.json",
            "M2_matriz_incertidumbre.html": "matriz_semanas.json",
            "M3_unit_chart_salas.html": "salas_semana.json",
            "M4_campus_3d.html": None,                     # M4 junta todos los campus (ver abajo)
            "A1_curva_alertas.html": "alertas_serie.json",  # simulación de alertas (datos_alertas.py)
            "A2_mapa_alertas.html": "alertas_celdas.json",
            "DEMO_SOSTRATO.html": None}                 # demo: pestañas con las vistas y filtros comunes

leer = lambda p: open(p, encoding="utf-8").read()
css, sedes = leer(os.path.join(PLANT, "_base.css")), leer(os.path.join(DATOS, "sedes.json"))
estado_js = leer(os.path.join(PLANT, "_estado.js"))
for html, js in MAQUETAS.items():
    t = leer(os.path.join(PLANT, html))
    t = t.replace("/*__CSS__*/", css).replace("/*__SEDES__*/", sedes).replace("/*__ESTADO_JS__*/", estado_js)
    if "/*__OSM__*/" in t:                       # M4: todos los campus con datos 3D y plantas de OSM (datos_prototipo_3d.py + campus_osm.py)
        camp = [f[len("osm_"):-len(".json")] for f in os.listdir(DATOS) if f.startswith("osm_") and f.endswith(".json") and "overpass" not in f]
        camp = [c for c in camp if os.path.exists(os.path.join(DATOS, f"campus3d_{c}.json"))]
        t = t.replace("/*__DATOS__*/", "{" + ",".join(f'"{c}":' + leer(os.path.join(DATOS, f"campus3d_{c}.json")) for c in camp) + "}")
        t = t.replace("/*__OSM__*/", "{" + ",".join(f'"{c}":' + leer(os.path.join(DATOS, f"osm_{c}.json")) for c in camp) + "}")
    if js:
        t = t.replace("/*__DATOS__*/", leer(os.path.join(DATOS, js)))
    open(os.path.join(DEST, html), "w", encoding="utf-8").write(t)
    print(f"{html}: {len(t) / 1e6:.2f} MB")

# simulación de alertas · A3 y A4: un archivo por campus (programación sintética de ese campus; A4 además su planta de OSM)
POR_CAMPUS = {"A3_programacion_proyectada.html": "A3_programacion_proyectada_{}.html",
              "A4_campus_3d_proyectado.html": "A4_campus_3d_proyectado_{}.html"}
for plantilla, salida in POR_CAMPUS.items():
    base = leer(os.path.join(PLANT, plantilla)).replace("/*__CSS__*/", css).replace("/*__SEDES__*/", sedes).replace("/*__ESTADO_JS__*/", estado_js)
    for c in ["C01", "C02", "C03", "C04", "C05", "C06", "C07"]:
        prog = os.path.join(DATOS, f"prog_{c}.json")
        if not os.path.exists(prog):
            continue
        t = base.replace("/*__DATOS__*/", leer(prog))
        if "/*__OSM__*/" in t:
            t = t.replace("/*__OSM__*/", leer(os.path.join(DATOS, f"osm_{c}.json")))
        open(os.path.join(DEST, salida.format(c)), "w", encoding="utf-8").write(t)
        print(f"{salida.format(c)}: {len(t) / 1e6:.2f} MB")
