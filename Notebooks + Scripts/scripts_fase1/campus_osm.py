"""Plantas reales de un campus desde OpenStreetMap (© colaboradores de OpenStreetMap, licencia ODbL) para la maqueta 4.

1. Contorno: el polígono amenity=university de la UNIV que contiene el punto (o el más cercano a menos de 200 m).
   Si OSM no tiene contorno (Campus 06), se envuelven los edificios de la UNIV con una franja de 8 m.
2. Edificios del campus: los que caen dentro del contorno (más 25 m).
3. Calce con la planta física (campus3d_<CAMPUS>.json, correr antes datos_prototipo_3d.py):
   - por nombre «Edificio X» de OSM (Campus 01, Campus 02);
   - si no hay nombres, por tamaño: el edificio con más salas va al edificio de OSM de mayor superficie. Se marca «aprox».
Convierte lat/lon a metros locales (x = este, y = norte). Guarda la respuesta cruda de Overpass para no repetir consultas.
Salida: Documentación/maquetas_visualizacion/datos/osm_<CAMPUS>.json
Uso: py campus_osm.py [CAMPUS LAT LON]     (por defecto C01, Calle Ficticia 100)
"""
import json
import math
import os
import re
import sys
import urllib.parse
import urllib.request

CAMPUS, LAT, LON = (sys.argv[1], float(sys.argv[2]), float(sys.argv[3])) if len(sys.argv) > 3 else ("C01", -00.000000, -00.000000)
AQUI = os.path.dirname(os.path.abspath(__file__))
DATOS = os.path.normpath(os.path.join(AQUI, "..", "..", "Documentación", "maquetas_visualizacion", "datos"))
CRUDO = os.path.join(DATOS, f"osm_{CAMPUS}_overpass.json")

if not os.path.exists(CRUDO):
    q = (f'[out:json][timeout:60];(way(around:450,{LAT},{LON})["building"];'
         f'way(around:450,{LAT},{LON})["amenity"="university"];'
         f'relation(around:450,{LAT},{LON})["amenity"="university"];);out body geom;')
    req = urllib.request.Request("https://overpass-api.de/api/interpreter",
                                 data=urllib.parse.urlencode({"data": q}).encode(), headers={"User-Agent": "UNIV-DID-Cirilo2049/0.1"})
    open(CRUDO, "wb").write(urllib.request.urlopen(req, timeout=90).read())
els = json.load(open(CRUDO, encoding="utf-8"))["elements"]

K = 111320.0
def xy(p):
    return [(p["lon"] - LON) * K * math.cos(math.radians(LAT)), (p["lat"] - LAT) * K]

def dentro(pt, poly):
    x, y, c = pt[0], pt[1], False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c

def area(poly):
    return abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]))) / 2

def centroide(poly):
    return [sum(p[0] for p in poly) / len(poly), sum(p[1] for p in poly) / len(poly)]

def dist_poly(pt, poly):
    return min(math.hypot(pt[0] - x, pt[1] - y) for x, y in poly)

def envolvente(pts):                                         # casco convexo (monotone chain)
    pts = sorted(map(tuple, pts))
    cruz = lambda o, a, b: (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for p in pts:
        while len(lo) >= 2 and cruz(lo[-2], lo[-1], p) <= 0: lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) >= 2 and cruz(hi[-2], hi[-1], p) <= 0: hi.pop()
        hi.append(p)
    return [list(p) for p in lo[:-1] + hi[:-1]]

def holgura(poly, m):                                        # agranda un polígono convexo m metros desde su centroide
    cx, cy = centroide(poly)
    return [[x + (x - cx) / (math.hypot(x - cx, y - cy) or 1) * m, y + (y - cy) / (math.hypot(x - cx, y - cy) or 1) * m] for x, y in poly]

UNIV = re.compile(r"Ficticia|\bUSS\b", re.I)
geo = [dict(e, P=[xy(p) for p in e["geometry"]][:-1]) for e in els if e["type"] == "way" and "geometry" in e]
uni = [g for g in geo if g.get("tags", {}).get("amenity") in ("university", "college") and UNIV.search(g["tags"].get("name", "") + g["tags"].get("operator", ""))]
campus = next((u for u in uni if dentro([0, 0], u["P"])), None)
if campus is None and uni:
    u = min(uni, key=lambda u: dist_poly([0, 0], u["P"]))
    campus = u if dist_poly([0, 0], u["P"]) < 200 else None
if campus is not None:
    contorno, origen = campus["P"], f"OSM: {campus['tags'].get('name')}"
else:                                                        # sin contorno: envolver los edificios de la UNIV cercanos
    propios = [g for g in geo if "building" in g.get("tags", {}) and dist_poly([0, 0], g["P"]) < 300
               and (UNIV.search(g["tags"].get("name", "")) or g["tags"].get("building") == "university")]
    contorno, origen = holgura(envolvente([p for g in propios for p in g["P"]]), 8), "envolvente de los edificios UNIV (+8 m)"
print(f"{CAMPUS} · contorno: {origen} · {area(contorno):,.0f} m²")

edif = []
for g in geo:
    t = g.get("tags", {})
    if "building" not in t:
        continue
    c = centroide(g["P"])
    if not (dentro(c, contorno) or dist_poly(c, contorno) < 25):
        continue
    nombre = t.get("name", "")
    m = re.match(r"Edificio ([A-Z])\b", nombre)
    edif.append({"osm_id": g["id"], "nombre": nombre, "letra": m.group(1) if m else None, "aprox": False,
                 "niveles": int(t["building:levels"]) if t.get("building:levels", "").isdigit() else None,
                 "area": round(area(g["P"])), "P": [[round(x, 2), round(y, 2)] for x, y in g["P"]]})

# una letra con varias partes en OSM (E: «Pisos 1 y 2» y «Piso 3»): se usa la de mayor área
por_letra = {}
for b in edif:
    if b["letra"] and (b["letra"] not in por_letra or b["area"] > por_letra[b["letra"]]["area"]):
        por_letra[b["letra"]] = b
for b in edif:
    b["usar"] = bool(b["letra"]) and por_letra[b["letra"]] is b

# calce aproximado por tamaño para los edificios de la planta física que no tienen nombre en OSM
f3d = os.path.join(DATOS, f"campus3d_{CAMPUS}.json")
if os.path.exists(f3d):
    salas = json.load(open(f3d, encoding="utf-8"))["salas"]
    letra = lambda ed: ed[len(CAMPUS):] if ed.startswith(CAMPUS) else ed[2:]
    n_salas = {}
    for s in salas:
        n_salas[letra(s["EDIFICIO"])] = n_salas.get(letra(s["EDIFICIO"]), 0) + 1
    # los espacios externos (EC…: estadio, campos clínicos) no se ubican por tamaño
    pendientes = sorted([l for l in n_salas if l not in por_letra and not l.startswith("EC")], key=lambda l: -n_salas[l])
    # solo edificios sin nombre o con nombre de la UNIV (no los de otras instituciones dentro del contorno)
    libres = sorted([b for b in edif if not b["letra"] and b["area"] >= 150 and (not b["nombre"] or UNIV.search(b["nombre"]))
                     and not re.search(r"gimnasio|casino|capilla|iglesia", b["nombre"], re.I)], key=lambda b: -b["area"])
    for l, b in zip(pendientes, libres):
        b.update(letra=l, aprox=True, usar=True)
    sin = [l for l in pendientes if l not in {b["letra"] for b in edif}]
    print(f"  por nombre: {sorted(por_letra)} · aproximados por tamaño: {[(b['letra'], b['area']) for b in edif if b['aprox']]} · sin ubicación: {sin}")

# --- entorno (capas opcionales de la maqueta): calles, edificios vecinos, áreas verdes y agua en un radio mayor
CRUDO_E = os.path.join(DATOS, f"osm_{CAMPUS}_entorno_overpass.json")
R_ENT = 700
if not os.path.exists(CRUDO_E):
    q = (f'[out:json][timeout:90];('
         f'way(around:{R_ENT},{LAT},{LON})["highway"];'
         f'way(around:{R_ENT},{LAT},{LON})["building"];'
         f'way(around:{R_ENT},{LAT},{LON})["leisure"~"park|garden|pitch|playground|recreation_ground"];'
         f'way(around:{R_ENT},{LAT},{LON})["landuse"~"grass|forest|recreation_ground|meadow|village_green"];'
         f'way(around:{R_ENT},{LAT},{LON})["natural"~"wood|scrub|grassland|water|wetland"];'
         f'relation(around:{R_ENT},{LAT},{LON})["natural"="water"];'
         f'relation(around:{R_ENT},{LAT},{LON})["leisure"="park"];'
         f');out body geom;')
    req = urllib.request.Request("https://overpass-api.de/api/interpreter",
                                 data=urllib.parse.urlencode({"data": q}).encode(), headers={"User-Agent": "UNIV-DID-Cirilo2049/0.1"})
    open(CRUDO_E, "wb").write(urllib.request.urlopen(req, timeout=120).read())
ent = json.load(open(CRUDO_E, encoding="utf-8"))["elements"]
ids_campus = {b["osm_id"] for b in edif}
r2 = lambda P: [[round(x, 1), round(y, 1)] for x, y in P]
ANCHO = {"motorway": 16, "trunk": 14, "primary": 12, "secondary": 10, "tertiary": 8, "unclassified": 6, "residential": 6,
         "living_street": 5, "service": 4, "pedestrian": 4, "footway": 2, "path": 2, "cycleway": 2, "steps": 2}

def anillos(e):
    """Polígonos cerrados de un way o de los 'outer' de una relación (encadena tramos abiertos)."""
    if e["type"] == "way":
        return [[xy(p) for p in e["geometry"]][:-1]] if e["geometry"][0] == e["geometry"][-1] else []
    tramos = [[(p["lon"], p["lat"]) for p in m["geometry"]] for m in e.get("members", []) if m.get("role") == "outer" and m.get("geometry")]
    out = []
    while tramos:
        a = tramos.pop(0)
        cambio = True
        while a[0] != a[-1] and cambio:
            cambio = False
            for i, t in enumerate(tramos):
                if t[0] == a[-1]: a += t[1:]
                elif t[-1] == a[-1]: a += t[::-1][1:]
                elif t[-1] == a[0]: a = t[:-1] + a
                elif t[0] == a[0]: a = t[::-1][:-1] + a
                else: continue
                tramos.pop(i); cambio = True; break
        if a[0] == a[-1] and len(a) > 3:
            out.append([xy({"lon": x, "lat": y}) for x, y in a][:-1])
    return out

calles, vecinos, verde, agua = [], [], [], []
for e in ent:
    t = e.get("tags", {})
    if "highway" in t and e["type"] == "way" and t["highway"] in ANCHO:
        calles.append({"tipo": t["highway"], "ancho": ANCHO[t["highway"]], "nombre": t.get("name", ""),
                       "L": r2([xy(p) for p in e["geometry"]])})
    elif "building" in t and e["type"] == "way" and e["id"] not in ids_campus:
        for P in anillos(e):
            vecinos.append({"P": r2(P), "niveles": int(t["building:levels"]) if t.get("building:levels", "").isdigit() else None,
                            "area": round(area(P))})
    elif t.get("natural") in ("water", "wetland"):
        agua += [{"P": r2(P), "nombre": t.get("name", "")} for P in anillos(e)]
    elif any(k in t for k in ("leisure", "landuse", "natural")):
        verde += [{"P": r2(P)} for P in anillos(e)]
print(f"entorno ({R_ENT} m): {len(calles)} tramos de calle · {len(vecinos)} edificios vecinos · "
      f"{len(verde)} áreas verdes · {len(agua)} cuerpos de agua {[a['nombre'] for a in agua if a['nombre']]}")

json.dump({"campus": CAMPUS, "centro": [LAT, LON], "atribucion": "© colaboradores de OpenStreetMap (ODbL)",
           "contorno": [[round(x, 2), round(y, 2)] for x, y in contorno], "origen_contorno": origen, "edificios": edif,
           "entorno": {"radio": R_ENT, "calles": calles, "vecinos": vecinos, "verde": verde, "agua": agua}},
          open(os.path.join(DATOS, f"osm_{CAMPUS}.json"), "w", encoding="utf-8"), ensure_ascii=False)
for b in sorted(edif, key=lambda b: (b["letra"] is None, b["letra"] or "", -b["area"])):
    print(f"  {b['letra'] or '·'}  {'✓' if b['usar'] else ' '}  {b['area']:>6} m²  {b['nombre'] or '(sin nombre)'}")
