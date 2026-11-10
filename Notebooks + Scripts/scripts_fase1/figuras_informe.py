"""Figuras del informe ejecutivo de alertas (PNG), desde los mismos JSON que la demo (datos_alertas.py).
Escenario base, pregrado, sufijo 10 salvo que se indique. Salida: Documentación/figuras_alertas/
Uso: py figuras_informe.py
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

AQUI = os.path.dirname(os.path.abspath(__file__))
DOC = os.path.normpath(os.path.join(AQUI, "..", "..", "Documentación"))
DAT = os.path.join(DOC, "maquetas_visualizacion", "datos")
OUT = os.path.join(DOC, "figuras_alertas")
os.makedirs(OUT, exist_ok=True)
S = json.load(open(os.path.join(DAT, "alertas_serie.json"), encoding="utf-8"))
A = json.load(open(os.path.join(DAT, "alertas_celdas.json"), encoding="utf-8"))
SEDES = json.load(open(os.path.join(DAT, "sedes.json"), encoding="utf-8"))
ANIOS = [2027, 2028, 2029, 2030, 2031]
CAMPUS = ["C01", "C02", "C03", "C04", "C05", "C06", "C07"]
AZUL, BANDA, TINTA, GRIS, MUTED = "#2a78d6", "#b7d3f6", "#0b0b0b", "#e4e3df", "#7a7974"
NIV = {"vigilancia": "#fab219", "alerta": "#ec835a", "crítica": "#d03b3b"}
RAMPA = ["#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]
plt.rcParams.update({"font.family": "Segoe UI", "font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": GRIS, "axes.labelcolor": "#52514e", "xtick.color": "#52514e", "ytick.color": "#52514e"})
nom = lambda c: SEDES.get(c, c).split("-", 1)[-1].strip().title().replace(" De ", " de ")
n25 = lambda c, a, e, cl="*", per=10: S["serie"].get(f"{c}|{cl}|{a * 100 + per}|{e}|todos", [0, 0, 0])
pie = "Fuente: Sóstrato el Arquitecto · Modelos.ipynb (28-10-2026; D19: naive escalado desde 2028) · escenario base, pregrado, 1.er semestre. Dirección de Ingeniería de Datos · UNIV"
cifras = {}

def guardar(fig, nombre):
    fig.text(0.01, 0.01, pie, fontsize=7.5, color=MUTED)
    fig.savefig(os.path.join(OUT, nombre), dpi=200, bbox_inches="tight", facecolor="white"); plt.close(fig)

# ---- F1 · cifra ancla: celdas en alerta por año, con rango de escenarios
base = [n25("TODOS", a, "base")[1] for a in ANIOS]
bajo = [n25("TODOS", a, "bajo")[1] for a in ANIOS]
alto = [n25("TODOS", a, "alto")[1] for a in ANIOS]
crit = [n25("TODOS", a, "base")[2] for a in ANIOS]
vig = [n25("TODOS", a, "base")[0] for a in ANIOS]
cifras["F1"] = {"base_≥25": dict(zip(ANIOS, base)), "bajo_≥25": dict(zip(ANIOS, bajo)), "alto_≥25": dict(zip(ANIOS, alto)),
                "base_≥10": dict(zip(ANIOS, vig)), "base_≥50": dict(zip(ANIOS, crit))}
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.axvspan(2030.5, 2031.4, color=GRIS, alpha=0.6, lw=0); ax.text(2031.35, max(alto) * 1.05, "extrapolado", ha="right", color=MUTED, fontsize=9)
ax.fill_between(ANIOS[1:], bajo[1:], alto[1:], color=BANDA, alpha=0.7, lw=0, label="rango bajo–alto")
ax.plot([2027, 2027], [bajo[0], alto[0]], color=BANDA, lw=9, alpha=0.55, solid_capstyle="butt")
ax.plot([2027, 2027], [bajo[0], alto[0]], color="#86b6ef", lw=1.2, ls=(0, (3, 3)))
ax.annotate("2027: banda de Euribia: otra definición,\nno comparable con 2028–2031", (2027, bajo[0]), xytext=(2027.1, max(alto) * 0.03), fontsize=8.5, color=MUTED)
ax.plot(ANIOS, base, color=AZUL, lw=2.5, marker="o", ms=6, label="escenario base", zorder=3)
for a, v in zip(ANIOS, base):
    ax.text(a, v + max(alto) * 0.04, str(v), ha="center", fontweight="bold", color=TINTA)
ax.set_xticks(ANIOS, [str(a) if a < 2031 else "2031*" for a in ANIOS]); ax.set_ylim(0, max(alto) * 1.15)
ax.set_ylabel("celdas en alerta (prob. de saturar ≥ 25 %)"); ax.grid(axis="y", color=GRIS)
fig.suptitle("Las horas sin espacio suficiente se triplican hacia 2031", x=0.01, ha="left", fontsize=13, fontweight="bold", color=TINTA)
ax.set_title("Celdas día × bloque × clase de espacio con probabilidad de saturar de 25 % o más (considera el tamaño de sala)", loc="left", fontsize=9, color="#52514e", pad=10)
ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(0, 0.93))
guardar(fig, "F1_celdas_en_alerta_por_anio.png")

# ---- F2 · déficit por tamaño demandado y sobrecupo
D = [S["deficit"][f"TODOS|{a * 100 + 10}"] for a in ANIOS]
cifras["F2"] = {a: {"deficit": d[0], "sobrecupo": d[1], "deficit_por_rango": dict(zip(S["rangos"][1:], d[2]))} for a, d in zip(ANIOS, D)}
fig, ax = plt.subplots(figsize=(8, 4.2))
for i, (a, d) in enumerate(zip(ANIOS, D)):
    acc = 0
    for r, sh in enumerate(d[2]):
        h = d[0] * sh * 100
        ax.bar(i, h, bottom=acc, color=RAMPA[r], width=0.55, alpha=0.65 if a == 2031 else 1, edgecolor="white", lw=1)
        acc += h
    ax.text(i, acc - 0.9, f"{d[0] * 100:.1f} %".replace(".", ","), ha="center", fontweight="bold", color="white")
ax.plot(range(5), [d[1] * 100 for d in D], color=NIV["alerta"], lw=2, marker="o", ms=6)
for i, d in enumerate(D):
    ax.text(i + 0.12, d[1] * 100 + 0.5, f"{d[1] * 100:.1f} %".replace(".", ","), color="#9c4a22", fontsize=8.5)
ax.set_xticks(range(5), [str(a) if a < 2031 else "2031*" for a in ANIOS]); ax.set_ylabel("% de los casilleros (ponderado por semanas)")
ax.grid(axis="y", color=GRIS)
fig.suptitle("Lo que falta son, sobre todo, salas grandes", x=0.01, y=1.07, ha="left", fontsize=13, fontweight="bold", color=TINTA)
ax.set_title(f"Déficit de la programación proyectada por tamaño que piden (barras) y sobrecupo tolerado (línea).\nEn 2027, {D[0][2][3] * 100:.0f} % del déficit pide salas de 60 o más", loc="left", fontsize=9, color="#52514e", pad=10)
ax.legend(handles=[Patch(color=RAMPA[i], label=f"déficit · {r}") for i, r in enumerate(S["rangos"][1:])] +
          [plt.Line2D([], [], color=NIV["alerta"], marker="o", label="sobrecupo tolerado")], frameon=False, ncol=2, fontsize=8, loc="upper left")
guardar(fig, "F2_deficit_y_sobrecupo.png")

# ---- F3 · dónde aparecen: celdas en alerta por campus y año
fig, axs = plt.subplots(1, 7, figsize=(12, 3.2), sharey=True)
orden = sorted(CAMPUS, key=lambda c: -n25(c, 2031, "base")[1])
cifras["F3"] = {}
for ax, c in zip(axs, orden):
    sal = [n25(c, a, "base", "SALA")[1] for a in ANIOS]
    lab = [n25(c, a, "base", "LABORATORIO")[1] for a in ANIOS]
    cifras["F3"][c] = {"salas": dict(zip(ANIOS, sal)), "laboratorios": dict(zip(ANIOS, lab))}
    ax.bar(range(5), sal, color=AZUL, width=0.6, label="salas")
    ax.bar(range(5), lab, bottom=sal, color="#86b6ef", width=0.6, label="laboratorios")
    ax.set_xticks(range(5), ["27", "28", "29", "30", "31*"], fontsize=8); ax.grid(axis="y", color=GRIS)
    pri = next((a for a, s, l in zip(ANIOS, sal, lab) if s + l > 0), None)
    ax.set_title(f"{nom(c)}\n{'1.ª alerta ' + str(pri) if pri else 'sin alertas'}", fontsize=9, loc="left")
    if c == "C01":
        ax.text(0, -0.40, "Atención: labs. 60+ a\nvalidar con infraestructura", transform=ax.transAxes, fontsize=7.5, color="#9c5a00")
axs[0].set_ylabel("celdas en alerta (≥ 25 %)")
fig.legend(*axs[0].get_legend_handles_labels(), frameon=False, fontsize=8, ncol=2, loc="upper right", bbox_to_anchor=(0.99, 0.99))
fig.suptitle("Dónde aparecen las alertas: por campus, de mayor a menor en 2031", x=0.01, ha="left", fontsize=13, fontweight="bold", color=TINTA)
fig.tight_layout(rect=(0, 0.04, 1, 0.95))
guardar(fig, "F3_alertas_por_campus.png")

# ---- F4 · mapa de alertas 2027 frente a 2030 (calendario día × bloque)
NC = len(A["campos"]); F = {c: i for i, c in enumerate(A["campos"])}
HORAS = ["<08:00", "08:00", "08:40", "09:30", "10:10", "11:00", "11:40", "12:30", "13:10", "14:40", "15:20", "16:10", "16:50", "17:35", "18:15", "19:00", "19:40", "20:25", "21:05", "21:50"]
def calendario(ax, c, cl, anio, titulo):
    arr = A["celdas"][f"{c}|{cl}|{anio * 100 + 10}|base"]
    cap = A["cap"][f"{c}|{cl}"]; n = 0
    for d in range(6):
        for b in range(20):
            o = (d * 20 + b) * NC; p = arr[o + F["PT"]]; uso = arr[o + F["P50"]] / 10 / max(cap, 1)
            col = NIV["crítica"] if p >= 50 else NIV["alerta"] if p >= 25 else NIV["vigilancia"] if p >= 10 else ["#eef3fa", "#cde2fb", "#9ec5f4", "#6da7ec"][min(3, int(uso * 4))]
            n += p >= 25
            ax.add_patch(plt.Rectangle((d, 19 - b), 0.92, 0.88, color=col, lw=0))
            if p >= 25 and arr[o + F["RC"]] >= 2:
                ax.plot(d + 0.46, 19 - b + 0.44, "o", color="white", ms=3)
    ax.set_xlim(0, 6); ax.set_ylim(0, 20); ax.set_xticks([i + 0.46 for i in range(6)], list("LMMJVS")); ax.set_yticks([19 - b + 0.44 for b in (1, 5, 9, 13, 17)], [HORAS[b] for b in (1, 5, 9, 13, 17)], fontsize=8)
    for s in ax.spines.values(): s.set_visible(False)
    ax.tick_params(length=0); ax.set_title(f"{titulo} · {n} celdas en alerta", fontsize=10, loc="left")
    return n
for c, cl, etiqueta in [("C04", "SALA", "salas"), ("C01", "LABORATORIO", "laboratorios")]:
    fig, axs = plt.subplots(1, 2, figsize=(7.5, 5.4))
    cifras[f"F4_{c}_{cl}"] = {a: calendario(ax, c, cl, a, str(a)) for ax, a in zip(axs, (2027, 2030))}
    fig.suptitle(f"{nom(c)} · {etiqueta}: cómo se extienden las alertas", x=0.01, ha="left", fontsize=13, fontweight="bold", color=TINTA)
    nota = "Punto blanco: lo que falta son salas grandes (41 o más). La hora exacta puede moverse: el valor está en el patrón."
    if c == "C01": nota += "\nAtención: laboratorios de 60 o más: a validar con infraestructura (puede ser gestión de grupos, no falta de espacio)."
    fig.legend(handles=[Patch(color=v, label=k) for k, v in NIV.items()] + [Patch(color="#9ec5f4", label="sin alerta (tono = uso esperado)")],
               frameon=False, ncol=4, fontsize=8, loc="lower left", bbox_to_anchor=(0.01, 0.10))
    fig.text(0.01, 0.045, nota, fontsize=7.5, color="#52514e")
    fig.tight_layout(rect=(0, 0.17, 1, 0.94))
    guardar(fig, f"F4_mapa_2027_vs_2030_{c}_{etiqueta}.png")

json.dump(cifras, open(os.path.join(OUT, "cifras_figuras.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print("figuras:", sorted(f for f in os.listdir(OUT)))
print(json.dumps({k: cifras[k] for k in ("F1",)}, ensure_ascii=False))
print({k: v for k, v in cifras.items() if k.startswith("F4")})
