"""Prueba de paleta: copia las maquetas con la paleta «Arena» sin tocar las originales.

Entrada:  Documentación/maquetas_visualizacion/*.html
Salida:   Documentación/maquetas_visualizacion_arena/*.html

La paleta sale de la página de referencia (Codebase City): arena, tierra y terracota.
Semáforo y rampa de ocupación son propios, validados con el validador de dataviz:
el azul pizarra sigue siendo «ocupado» y los cálidos siguen siendo «alerta».
No cambia datos ni lógica: solo colores, tipografía y el trazado (hatching) del 3D.
"""
import pathlib
import re

BASE = pathlib.Path(__file__).resolve().parents[2] / "Documentación"
ORIGEN, DESTINO = BASE / "maquetas_visualizacion", BASE / "maquetas_visualizacion_arena"

# tokens que comparten valor con otros colores: se resuelven antes del mapa general
TOKENS = {
    "--neutral: #f0efec": "--neutral: #d8cfb0",
    "--accent: #2a78d6": "--accent: #8a4b2a",
    "--accent: #3987e5": "--accent: #8a4b2a",
}
COLORES = {
    # superficies y texto (referencia; secundario y tenue oscurecidos para que se lean sobre arena)
    "#f6f5f2": "#ddd3b4", "#fcfcfb": "#e9e1c8", "#0b0b0b": "#33301f", "#52514e": "#5f5940", "#7a7974": "#6f6849",
    "#e4e3df": "#cfc5a5", "#e9e8e4": "#d3c9a8", "#cfcec9": "#bfb493", "#b7d3f6": "#cdb795",
    # semáforo
    "#fab219": "#c9ae1e", "#ec835a": "#c8621a", "#d03b3b": "#962018", "#ff8f8f": "#962018",
    # avisos
    "#fff4e5": "#e4d3a8", "#7a4a00": "#6b4210", "#f3c978": "#b4690e", "#9c5a00": "#8a5208",
    # rampa de ocupación, de claro a oscuro
    "#e8f0fb": "#dcd8c8", "#cde2fb": "#b3bbc6", "#9ec5f4": "#919eb6", "#86b6ef": "#8391ad", "#6da7ec": "#7285ad",
    "#3987e5": "#5f78a8", "#2a78d6": "#4f6aa0", "#256abf": "#445c90", "#1c5cab": "#38507f", "#184f95": "#314670",
    "#104281": "#2a3b60", "#0d366b": "#212d48",
}
# la escena 3D nació oscura: aquí esos tonos pasan a su equivalente claro
COLORES_3D = {
    "#111318": "#ddd3b4", "#f0efec": "#33301f", "#b9b8b0": "#5f5940", "#7d7c76": "#6f6849",
    "#1d2027f2": "#e9e1c8f2", "#1d2027": "#e9e1c8", "#33363e": "#bfb493", "#262931": "#d3c9a8",
    "#23402d": "#8f9a6e", "#3b3f48": "#c9be9c", "#1b3a5c": "#7f93a8", "#343740": "#c4b996",
    "#3a3e47": "#bdb18f", "#1a1c21": "#d8cfb0", "#ffd38a": "#6b4210", "#3a2a0d": "#e4d3a8", "#6b4a14": "#b4690e",
    "#1a1c22": "#8a7f5f", "#dfe8ff": "#fff6e0", "#8d8f96": "#bfb493", "#9a9ca3": "#c9be9c", "#4a4d55": "#a89c78",
    "#262a31": "#cfc5a5", "#6d6f76": "#a89c78", "#5a5d66": "#bfb493", "#4a0b0b": "#2a0503",
}

FUENTES = ('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
           '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400;600'
           '&family=Geist+Mono:wght@400;500;600&display=swap">')
MONO = '"Geist Mono", ui-monospace, SFMono-Regular, Menlo, monospace'
SANS = '"Geist", "Segoe UI", system-ui, sans-serif'
CSS = f"""
/* paleta Arena: prosa en Geist; títulos, controles, cifras y rótulos en Geist Mono */
html, body, .viz-root {{ font-family: {SANS}; }}
h1, h3, .marca, nav button, .filtros, .modo, .play, .anios, .seg, .pill, .hero .n, .kicker, .tr .n, .ley, .sem, .tip {{ font-family: {MONO}; }}
.seg, .anios, .card, .ctl-sel, .filtros select, .play {{ border-radius: 4px; }}
.card {{ border: 1px solid var(--grid); }}
.seg button[aria-pressed="true"], .anios button[aria-pressed="true"], .modo button[aria-pressed="true"],
.pill[aria-pressed="true"] {{ background: #8a4b2a; color: #f6f1e0; border-color: #8a4b2a; }}
.marca .t::after {{ content: " · paleta Arena"; font-weight: 400; color: var(--text-muted); font-size: 12px; }}
"""
# trazado diagonal de la referencia, sobre las salas del 3D
HATCH = """const HATCH = (() => { const c = document.createElement("canvas"); c.width = c.height = 64; const x = c.getContext("2d");
  x.fillStyle = "#fff"; x.fillRect(0, 0, 64, 64); x.strokeStyle = "rgba(51,48,31,.28)"; x.lineWidth = 3;
  for (let i = -64; i < 128; i += 16) { x.beginPath(); x.moveTo(i, 64); x.lineTo(i + 64, 0); x.stroke(); }
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(2, 2); return t; })();
const roomMeshes = [];"""


def reemplaza(texto, mapa):
    patron = re.compile("|".join(re.escape(k) for k in sorted(mapa, key=len, reverse=True)))
    return patron.sub(lambda m: mapa[m.group(0)], texto)


def transforma(nombre, t):
    es_3d = nombre.startswith(("A4_", "M4_"))
    t = t.replace('<html lang="es">', '<html lang="es" data-theme="light">', 1)     # la paleta no tiene modo oscuro
    t = reemplaza(t, TOKENS)
    if es_3d:
        t = reemplaza(t, COLORES_3D)
        hex_3d = {k[0:7].replace("#", "0x"): v[0:7].replace("#", "0x") for k, v in {**COLORES_3D, **COLORES}.items()}
        t = reemplaza(t, hex_3d)
        # sobre fondo claro la escena necesita más luz ambiente para que el suelo no se ensucie
        t = t.replace("new THREE.HemisphereLight(0xfff6e0, 0x8a7f5f, 0.85)", "new THREE.HemisphereLight(0xffffff, 0xd8cfb0, 2.1)", 1)
        t = t.replace("new THREE.DirectionalLight(0xfff4e5, 1.6)", "new THREE.DirectionalLight(0xffffff, 1.0)", 1)
        t = t.replace("const roomMeshes = [];", HATCH, 1)
        t = t.replace("new THREE.MeshStandardMaterial({ color: COL_LIBRE,", "new THREE.MeshStandardMaterial({ map: HATCH, color: COL_LIBRE,", 1)
    t = reemplaza(t, COLORES)
    t = re.sub(r"<title>(.*?)</title>", r"<title>\1 · Arena</title>", t, count=1)
    t = t.replace("</head>", FUENTES + "<style>" + CSS + "</style></head>", 1)
    return t


def main():
    DESTINO.mkdir(exist_ok=True)
    archivos = sorted(ORIGEN.glob("*.html"))
    for f in archivos:
        (DESTINO / f.name).write_text(transforma(f.name, f.read_text(encoding="utf-8")), encoding="utf-8", newline="")
    print(len(archivos), "maquetas en", DESTINO)


if __name__ == "__main__":
    main()
