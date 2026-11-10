"""Diagrama de flujo de datos DETALLADO de Sóstrato (instructivo v0.8, §2 «versión detallada» y §8.1).

Una caja por sub-paso que transforma el dato (decisión de Diego, 30-10): el modelo se abre en dos franjas,
VALIDACIÓN (banco walk-forward) y PROYECCIÓN (Modelos), y cada ficha nombra el método, sus parámetros reales
y la métrica con que se validó. Posiciones fijas (layout «none»): fuentes apiladas a la izquierda, conectores
azules con letra para los datos que cruzan franjas, modelo un escalón más abajo y a la derecha del pipeline.

Uso: py diagrama_flujo_detalle.py      (luego: verificar_diagrama.py sobre el .excalidraw.md)
"""
import os, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
HERR = os.path.normpath(os.path.join(AQUI, "..", "..", "..", "..", "Mantenedores Repo", "_HERRAMIENTAS_DIAGRAMA_EXCALIDRAW"))
sys.path.insert(0, HERR)
import canon_post  # noqa: E402  (deja importable excalidraw_kit)
from excalidraw_kit import Diagram, Editor, fractional_keys, save_scene, scene_to_markdown  # noqa: E402

OUT = os.path.normpath(os.path.join(AQUI, "..", "..", "SOSTRATO_flujo_pipeline-modelo-detalle_2026-10-30"))
VERSION = "v1.0 · 2026-10-30 · decisiones D14–D19 · cifras de la corrida del 29-10 (pregrado, 1.er semestre, escenario base)"

# ---------------------------------------------------------------- medidas (§8.1)
BW, BH = 300, 130          # bloque de proceso / predefinido
SW, SH = 300, 150          # fuente
UW = 44                    # nodo de unión
CW = 60                    # conector
GAP = 200                  # separación entre bloques con etiqueta (≥ 120)
F_BLOQUE, F_FUENTE, F_FLECHA, F_ZONA, F_CON = 20, 18, 18, 20, 22

d = Diagram(None, direction="LR", route="curved", rounded=False, label_font_size=F_FLECHA, font_size=F_BLOQUE)
AZUL = ("#1971c2", "#a5d8ff")


def blo(texto, color, x, y, **kw):
    return d.node(texto, color=color, x=x, y=y, w=BW, h=BH, font_size=F_BLOQUE, **kw)


def uni(x, y):
    return d.node("", shape="diamond", color="black", x=x, y=y, w=UW, h=UW, min_w=UW, min_h=UW)


def bar(x, y, h=70):
    return d.node("", shape="rect", color=("#1e1e1e", "#1e1e1e"), x=x, y=y, w=10, h=h, min_w=10, min_h=h)


def con(letra, x, y):
    return d.node(letra, shape="ellipse", color=AZUL, x=x, y=y, w=CW, h=CW, min_w=CW, min_h=CW, font_size=F_CON)


def fue(texto, y):
    return d.node(texto, color="gray", x=0, y=y, w=SW, h=SH, font_size=F_FUENTE)


# ---------------------------------------------------------------- fuentes (apiladas a la izquierda)
Y0 = 420
s_cir = fue("Cirilo · programación\nreal aperturada", Y0)
s_ath = fue("Athena · programación\ndetallada V2", Y0 + 220)
s_stv = fue("STVSUBJ · materias", Y0 + 440)
s_pf = fue("Planta física +\nbloques estándar", Y0 + 660)
s_eus = fue("Euribia · serie real\nvs proyectado", Y0 + 880)
s_abt = fue("Ariadna · backtest\npropio", Y0 + 1100)
s_ari = fue("Ariadna · matrícula\n2010–2031", Y0 + 1320)
s_eur = fue("Euribia · inscritos\nproyectados 2027", Y0 + 1540)

XC = 520                                   # columna de conectores de salida
u0 = uni(560, Y0 + 155)
a_o = con("A", XC, Y0 + 485); b_o = con("B", XC, Y0 + 705); c_o = con("C", XC, Y0 + 925); d_o = con("D", XC, Y0 + 1145)
b7 = bar(470, Y0 + 1360)
e_o = con("E", 600, Y0 + 1290); f_o = con("F", 600, Y0 + 1365); g_o = con("G", 600, Y0 + 1440)
h_o = con("H", XC, Y0 + 1585)

# ---------------------------------------------------------------- PIPELINE (PIPELINES.ipynb)
YP = Y0 + 110
x = 720
b1 = blo("ACTUALIZACIÓN\nDESDE ATHENA", "green", x, YP); x += BW + GAP
b2 = blo("EMPALME\nllaves homologadas", "green", x, YP); x += BW + GAP - 40
u3 = uni(x, YP + 43); xu3 = x; x += UW + GAP - 40
b3 = blo("UNIDAD\nACADÉMICA", "green", x, YP); x += BW + GAP - 40
u4 = uni(x, YP + 43); xu4 = x; x += UW + GAP - 40
b4 = blo("OFERTA\nDE ESPACIOS", "green", x, YP); x += BW + GAP
b5 = blo("PLANTILLAS\nPOR NRC", "green", x, YP); x5 = x
a_i = con("A", xu3 - 80, YP - 150); e_i = con("E", xu3 + 60, YP - 150)
b_i = con("B", xu4 - 8, YP - 150)

# ---------------------------------------------------------------- MODELO · VALIDACIÓN (banco)
YV = YP + 480
x = x5
b6 = blo("PIEZAS POR ORIGEN\n10 orígenes", "violet", x, YV); x += BW + GAP - 40
u7 = uni(x, YV + 43); xu7 = x; x += UW + GAP - 40
b7_ = blo("CANDIDATOS\nnaive · Monte Carlo · H2", "violet", x, YV); x += BW + GAP
b8 = blo("COMBINACIÓN C1\nw calibrado", "violet", x, YV); x += BW + GAP
b9 = d.node("¿GANA AL NAIVE?\nregla de adopción", shape="diamond", color="yellow", x=x, y=YV - 55, w=380, h=240,
            font_size=F_BLOQUE); x += 380 + GAP
u10 = uni(x, YV + 43); xu10 = x; x += UW + GAP - 40
b10 = blo("BANDA\nCONFORMAL", "violet", x, YV); x += BW + GAP - 40
u11 = uni(x, YV + 43); xu11 = x; x += UW + GAP - 40
b11 = blo("PSEUDO-BACKTEST\nDE LARGO PLAZO", "violet", x, YV); x += BW + GAP
bv = bar(x, YV + 30); xbv = x; x += 10 + 130
b12 = blo("VALIDACIÓN\nDEL RANGO", "violet", x, YV - 120); x12 = x
diag = d.node("VALIDACION_RANGO\n(diagnóstico)", color="gray", x=x12 + 20, y=YV - 440, w=260, h=110, font_size=F_FUENTE)
c_i = con("C", xu7 - 8, YV - 170)
d_i = con("D", xu11 - 80, YV - 170); f_i = con("F", xu11 + 60, YV - 170)
p_o = con("P", xbv - 25, YV + 230)

# ---------------------------------------------------------------- MODELO · PROYECCIÓN (Modelos.ipynb)
YM = YV + 560
x = x5 - 140
g_i = con("G", x - 200, YM - 110); h_i = con("H", x - 200, YM + 35); p_i = con("P", x - 200, YM + 180)
u13 = uni(x, YM + 43); x += UW + GAP - 40
b13 = blo("VOLUMEN\nPROYECTADO", "violet", x, YM); x += BW + 110
bvol = bar(x, YM + 30); xbvol = x; x += 10 + 120
xs = x
b15 = blo("MONTE CARLO G1b\nbootstrap estratificado", "violet", x, YM); x += BW + GAP
b16 = blo("NAIVE ESTACIONAL\nescalado desde 2028", "violet", x, YM); x += BW + GAP
b17 = blo("COMBINACIÓN\nC1 · C1E", "violet", x, YM); x += BW + GAP
b18 = blo("BANDA × k_h\nP10 · P50 · P90", "violet", x, YM); x += BW + GAP
b19 = blo("REPARTO\nPOR RANGO", "violet", x, YM); x += BW + GAP - 40
u21 = uni(x, YM + 43); xu21 = x; x += UW + GAP - 40
b21 = blo("OCUPACIÓN\nY ALERTAS", "violet", x, YM); x21 = x
YL = YM + 260
b14 = blo("NÚMERO DE\nSECCIONES (H2)", "violet", xs, YL)
b20 = blo("PROGRAMACIÓN\nSINTÉTICA", "violet", xs + BW + GAP, YL)

# ---------------------------------------------------------------- ENTREGA
YE = YL + 330
x = x21 - 2 * (BW + GAP)
b22 = blo("DATOS DE LA\nSIMULACIÓN", "orange", x, YE); x += BW + GAP
b23 = blo("SIMULACIÓN\nY FIGURAS", "orange", x, YE); x += BW + GAP
b24 = blo("INFORMES\nejecutivo y técnico", "orange", x, YE); x += BW + GAP + 120
ent = d.node("ALERTAS 2027–2031\nsimulación + figuras +\n2 informes", color="orange", x=x, y=YE - 15, w=330, h=160,
             stroke_width=4, font_size=16)
fin = d.node("FIN · dirección e\ninfraestructura", shape="ellipse", color="gray", stroke_style="dashed",
             x=x + 330 + 160, y=YE, w=320, h=130, font_size=20)

# ---------------------------------------------------------------- flechas
E = d.edge
E(s_cir, u0, "prog_real"); E(s_ath, u0, "prog_v2"); E(u0, b1)
E(s_stv, a_o, "stvsubj"); E(s_pf, b_o, "planta"); E(s_eus, c_o, "euribia_serie"); E(s_abt, d_o, "ariadna_backtest")
E(s_ari, b7, "matricula"); E(b7, e_o); E(b7, f_o); E(b7, g_o); E(s_eur, h_o, "euribia_2027")
E(b1, b2, "prog_cirilo"); E(b2, u3, "prog_hist")
E(a_i, u3, "stvsubj", dst_side="top"); E(e_i, u3, "matricula", dst_side="top"); E(u3, b3)
E(b3, u4, "prog_unidad"); E(b_i, u4, "planta", dst_side="top"); E(u4, b4)
E(b4, b5, "oferta")
E(b5, b6, "base_fisica", src_side="bottom", dst_side="top")
E(b6, u7, "piezas_origen"); E(c_i, u7, "euribia_serie", dst_side="top"); E(u7, b7_)
E(b7_, b8, "predicciones"); E(b8, b9, "resultados")
E(b9, u10, "sí")
E(b9, u10, "no · naive (w = 1)", style="dashed", color="red", src_side="bottom", dst_side="bottom",
  via=[(xu10 - 150 - 300 // 2 + 150, YV + 260), (xu10 + UW / 2, YV + 260)])
E(u10, b10)
E(b10, u11, "banda"); E(d_i, u11, "ariadna_backtest", dst_side="top"); E(f_i, u11, "matricula", dst_side="top"); E(u11, b11)
E(b11, bv, "parametros_lp")
E(bv, b12, dst_side="left"); E(bv, p_o, src_side="bottom", dst_side="top")
E(b12, diag, "VALIDACION_RANGO", src_side="top", dst_side="bottom")
E(g_i, u13, "matricula"); E(h_i, u13, "euribia_2027"); E(p_i, u13, "parametros_lp"); E(u13, b13)
E(b13, bvol, "volumen"); E(bvol, b15); E(bvol, b14, src_side="bottom", dst_side="left", via=[(xbvol + 5, YL + BH / 2)])
E(b15, b16, "sims_mc"); E(b16, b17, "naive_esc"); E(b17, b18, "punto"); E(b18, b19, "mapa_proyectado")
E(b19, u21, "mapa_rango"); E(b14, b20, "secciones_proy"); E(b20, u21, "prog_sintetica", dst_side="bottom", via=[(xu21 + UW / 2, YL + BH / 2)]); E(u21, b21)
E(b21, b22, "ocupacion_alertas", src_side="bottom", dst_side="top",
  route="elbow")
E(b22, b23, "datos_demo"); E(b23, b24, "demo_figuras"); E(b24, ent, "alertas_2027_2031")
E(ent, fin, style="dashed")

d.zone("PIPELINE · PIPELINES.ipynb", [b1, b2, u3, b3, u4, b4, b5, a_i, e_i, b_i], color="green", font_size=F_ZONA)
d.zone("MODELO · VALIDACIÓN · VALIDACION_WALKFORWARD.ipynb", [b6, u7, b7_, b8, b9, u10, b10, u11, b11, bv, b12, c_i, d_i, f_i, p_o],
       color="violet", font_size=F_ZONA, padding=60)
d.zone("MODELO · PROYECCIÓN · Modelos.ipynb", [g_i, h_i, p_i, u13, b13, bvol, b15, b16, b17, b18, b19, u21, b21, b14, b20],
       color="violet", font_size=F_ZONA, padding=50)
d.zone("ENTREGA · scripts_fase1", [b22, b23, b24], color="orange", font_size=F_ZONA, padding=50)

d.layout("none")
print("check etapa 1:", d.check())

CANON = {s: "parallelogram" for s in (s_cir, s_stv, s_pf, s_eus, s_abt, s_ari, s_eur, ent, diag)}
CANON[s_ath] = "cylinder"
for b in (b7_, b8, b10, b11, b12, b15, b16, b17, b18, b20):
    CANON[b] = "predefined"
sc, probs = canon_post.finish(d, CANON, OUT, legend_anchor=s_eur, legend_xy=(0, 160), legend_title_size=24, legend_item_size=20,
                              legend_items=["cylinder", "parallelogram", "rect", "predefined", "diamond", "merge", "fork", "ellipse"])
print("finish:", probs)

# ---------------------------------------------------------------- etapa 2: posición fija
FICHAS = [
    ("1 · ACTUALIZACIÓN DESDE ATHENA", "Athena · QUERY_PROGRAMACION_DETALLADA_V2 (126.661 filas) + Cirilo PROG_DETALLADA",
     ["202620 y 202625 se reemplazan por la extracción fresca de Athena",
      "horarios ajustados al bloque estándar más cercano (19 bloques)",
      "una fila por día marcado, en el formato de Cirilo"],
     "→ 2 · prog_cirilo · 2.643.862 sesiones-hora"),
    ("2 · EMPALME", "prog_cirilo",
     ["llave período × MATERIA‖N_CURSO × componente × campus",
      "listas cruzadas con peso por inscritos (D11)",
      "solo pregrado (10/20) y advance (05/15/25) (D3)"],
     "→ 3 · prog_hist · 170.452 NRC × período (25 períodos)"),
    ("3 · UNIDAD ACADÉMICA", "prog_hist + STVSUBJ (conector A) + carrera → facultad de Ariadna (conector E)",
     ["materia que es carrera → su facultad", "si no calza → departamento con la descripción de STVSUBJ (D7)",
      "control: 77,8 % de las sesiones-hora queda en facultad"],
     "→ 4 · prog_unidad · 154 materias clasificadas"),
    ("4 · OFERTA DE ESPACIOS", "prog_unidad + planta física y bloques estándar (conector B)",
     ["clase sala / laboratorio, capacidad y rango 0-20 · 21-40 · 41-60 · 60 o más",
      "fuera: espacios externos, espacio UNIV y salas virtuales",
      "salas en uso fuera de la planta: clase del edificio o del componente"],
     "→ 5 · oferta · 4.944 espacios (1.177 activos)"),
    ("5 · PLANTILLAS POR NRC", "oferta + prog_hist",
     ["cada NRC: día × bloque × sala con PESO_SEMANAS (semanas de uso)",
      "compartición de laboratorios corregida (varios grupos en una sala)",
      "perfil horario por estrato para los orígenes del banco (D9)"],
     "→ 6 · base_fisica · 2.236.891 filas de plantilla"),
    ("6 · PIEZAS POR ORIGEN (banco §0–§2)", "base_fisica",
     ["evaluación walk-forward de origen rodante (Tashman, 2000)",
      "10 orígenes a 1 año: UG 202410, 202420, 202520, 202610, 202620 deciden; AV informa",
      "cada origen ve solo la información anterior a su objetivo",
      "estratos: campus × unidad × clase × componente"],
     "→ 7 · piezas_origen · un juego por origen"),
    ("7 · CANDIDATOS (banco §3–§4e)", "piezas_origen + Euribia serie (conector C)",
     ["naive estacional N0: el mismo semestre del año anterior (Hyndman & Athanasopoulos, 2021)",
      "Monte Carlo G1b: bootstrap estratificado de secciones × razón^β, 100 simulaciones",
      "H2 (estándar real) y volumen EUR, PER, TEN y ORA (real, techo)",
      "WAPE relativo al naive, celda: G1b 1,09 · H2 1,25 · C1-PER 1,01 · C1-EUR 1,01"],
     "→ 8 · predicciones · origen × modelo × grano"),
    ("8 · COMBINACIÓN C1 (banco §5)", "predicciones",
     ["combinación de pronósticos (Bates & Granger, 1969)",
      "C1 = w · naive + (1 − w) · Monte Carlo",
      "w por búsqueda en grilla 0–1 (paso 0,1) que minimiza el WAPE de los orígenes previos",
      "métricas: WAPE y WAPE relativo al naive, en celda y campus × día × bloque"],
     "→ 9 · resultados · VALIDACION_RESULTADOS 660 filas"),
    ("9 · ¿GANA AL NAIVE? (regla de adopción)", "resultados",
     ["gana si el WAPE relativo < 1 en la mayoría de los 5 orígenes UG, en los dos granos",
      "con volumen proyectado pasa C1-TEN (3 de 5; WAPE relativo medio 1,02 en celda)",
      "AV (informativo): la variante de menor error, C1-EUR",
      "no → naive (w = 1)"],
     "→ 10 · modelo_adoptado · UG C1-TEN (w 0,8) · AV C1-EUR (w 0)"),
    ("10 · BANDA CONFORMAL (banco §5b)", "modelo_adoptado (o el naive si no pasa)",
     ["predicción conforme dividida (Vovk et al., 2005; Angelopoulos & Bates, 2023)",
      "residuo normalizado e = (real − punto) ÷ √(punto + 1)",
      "cuantiles por nivel × clase × tramo, calibrados con orígenes previos",
      "cobertura P10–P90: 75 % (objetivo 80 %; la serie no es intercambiable)"],
     "→ 11 · banda · BANDA_CUANTILES 192 filas"),
    ("11 · PSEUDO-BACKTEST DE LARGO PLAZO (banco §7)", "banda + matrícula real de Ariadna (conector F) + su backtest (conector D)",
     ["bases 2022–2024 proyectadas a 1–4 años con la matrícula real (36 pares)",
      "k_h = Q80 |error| a h años ÷ a 1 año: UG 1,31 · 1,44 · 1,72; 2031: 1,82 extrapolado (h^γ)",
      "C1E corrige el sesgo: H+4 −7,6 % → −2,7 %; H+2 empeora 0,011 (D19)",
      "ensanche de los escenarios de Ariadna por su backtest: UG 1,13 · 1,34 · 1,76"],
     "→ 12 y P · parametros_lp · BANDA_HORIZONTE 60 · VALIDACION_HORIZONTE 584"),
    ("12 · VALIDACIÓN DEL RANGO (banco §8, informativa)", "parametros_lp",
     ["reparte la demanda por el rango de sala que necesitan las secciones",
      "WAPE relativo por rango: 0,98–1,03",
      "acierta el reparto: 202620 proyectado 40/31/13/16 % · real 40/30/16/14 %"],
     "→ diagnóstico · VALIDACION_RANGO 20 filas (no alimenta otro bloque)"),
    ("13 · VOLUMEN PROYECTADO (Modelos §3)", "parametros_lp (conector P) + Euribia 2027 (conector H) + Ariadna (conector G)",
     ["2027: UG extrapolación de tendencia por campus (TEN); AV pronóstico de Euribia",
      "2028–2031: crecimiento anual de Ariadna por carrera × sede, encadenado a 2027",
      "bajo / alto: Euribia en 2027; Ariadna ensanchada por su backtest desde 2028",
      "razones acotadas entre 0,25 y 4"],
     "→ 14 y 15 · volumen · 31.830 filas (UG: 345.663 → 428.813 inscritos)"),
    ("14 · NÚMERO DE SECCIONES (Modelos §4)", "volumen",
     ["regla de dimensionamiento (H2): estándar = percentil del tamaño que reproduce lo programado en 2026",
      "por sede × componente: secciones = inscritos ÷ estándar"],
     "→ 20 · secciones_proy · 2.130 filas (UG: 9.885 → 12.263 secciones)"),
    ("15 · MONTE CARLO G1b (Modelos §5)", "volumen",
     ["simulación Monte Carlo por bootstrap estratificado de las secciones de 2026 (Efron, 1979)",
      "salas del estrato ∝ razón^β; β por elasticidad log-log: UG 0,82 / 0,80 · AV 0,69",
      "100 simulaciones en 2027 y 50 en 2028–2031; cada una es un mapa posible"],
     "→ 16 · sims_mc · simulación × celda"),
    ("16 · NAIVE ESTACIONAL (Modelos §5)", "sims_mc + mapa real de 2026",
     ["naive = mapa real del mismo semestre de 2026",
      "desde 2028 se escala por el crecimiento de salas del Monte Carlo, por campus × clase (D19)",
      "factor mediano UG: 1,07 (2028) → 1,22 (2031)"],
     "→ 17 · naive_esc · celda"),
    ("17 · COMBINACIÓN C1 · C1E (Modelos §5)", "naive_esc + sims_mc",
     ["2027: C1 = 0,8 · naive + 0,2 · Monte Carlo (UG); AV: Monte Carlo (w 0)",
      "2028–2031: C1E = naive escalado (w 1,0)",
      "punto = media de las simulaciones combinadas"],
     "→ 18 · punto · celda"),
    ("18 · BANDA × k_h (Modelos §5)", "punto + banda + parametros_lp",
     ["cuantiles conformes del tramo de la celda",
      "desde 2028 ensanchados alrededor de la mediana: q' = q50 + k_h · (q − q50)",
      "solo celdas físicamente posibles (el campus tiene ese tipo de espacio)",
      "conjunto calibrado: un residuo por simulación y celda"],
     "→ 19 · mapa_proyectado · MAPA_PROYECTADO 147.000 filas"),
    ("19 · REPARTO POR RANGO (Modelos §5, D18)", "mapa_proyectado",
     ["tolerancia = P90 de inscritos ÷ capacidad en 2026 (sala 1,00; laboratorio 1,33)",
      "tamaño necesario = inscritos proyectados ÷ máx(tolerancia, sobrecupo histórico)",
      "parte de la demanda de cada celda en 0-20 · 21-40 · 41-60 · 60 o más"],
     "→ 21 · mapa_rango · celda × rango"),
    ("20 · PROGRAMACIÓN SINTÉTICA (Modelos §6)", "secciones_proy",
     ["remuestreo por cuotas de secciones reales de 2026 (originales + copias) hasta el número de 14",
      "cada una hereda el horario de su sección de origen; inscritos × razón de su tipo",
      "asignación voraz de mejor ajuste: la sala libre más chica que sirve (edificio → campus)",
      "una realización, horarios fijos; sin sala = déficit, sobre la capacidad nominal = sobrecupo"],
     "→ 21 · prog_sintetica · 471.521 filas (déficit 5,3 % → 17,4 %)"),
    ("21 · OCUPACIÓN Y ALERTAS (Modelos §7–§8)", "mapa_rango + prog_sintetica",
     ["alerta anidada: demanda de rango r o más contra espacios de r o más (oferta efectiva)",
      "PROB_SATURA_TAMANO = probabilidad de excedencia por Monte Carlo, la mayor entre rangos",
      "semáforo 10 / 25 / 50 %; UG: 93 → 297 celdas ≥ 25 % (2027 → 2031)",
      "control contra el banco en 202620: 0,942 contra 0,944"],
     "→ 22 · ocupacion_alertas · 147.000 celdas + 225.573 celda × rango"),
    ("22 · DATOS DE LA SIMULACIÓN (datos_alertas.py)", "ocupacion_alertas",
     ["serie de alertas por año, campus y escenario", "celdas con semáforo para el mapa semanal",
      "programación proyectada por campus para la vista 3D"],
     "→ 23 · datos_demo · JSON de la demo"),
    ("23 · SIMULACIÓN Y FIGURAS", "datos_demo",
     ["construir_maquetas.py: DEMO_SOSTRATO.html con reproductor 2027–2031",
      "figuras_informe.py: F1–F5 para los informes"],
     "→ 24 · demo_figuras · demo + 5 figuras"),
    ("24 · INFORMES", "demo_figuras + ocupacion_alertas",
     ["informe ejecutivo (dirección hacia arriba)", "informe técnico de resultados",
      ".md para Obsidian + PDF con figuras"],
     "→ ENTREGABLE · alertas_2027_2031 · simulación + figuras + 2 informes"),
]
NUM = {"1": b1, "2": b2, "3": b3, "4": b4, "5": b5, "6": b6, "7": b7_, "8": b8, "9": b9, "10": b10, "11": b11, "12": b12,
       "13": b13, "14": b14, "15": b15, "16": b16, "17": b17, "18": b18, "19": b19, "20": b20, "21": b21, "22": b22,
       "23": b23, "24": b24}
COLOR = {n: ("green" if int(n) <= 5 else "yellow" if n == "9" else "orange" if int(n) >= 22 else "violet") for n in NUM}
INSUMOS_DL = [
    ("QUERY_PROGRAMACION_DETALLADA_V2.txt", "programación detallada de 202620 y 202625",
     "126.661 filas · sin datos personales", "→ bloque 1"),
]
INSUMOS_ARCH = [
    ("PROG_DETALLADA_PARA_HEATMAP_ACTUALIZADO.parquet", "Cirilo · NRC × día × bloque × sala",
     "2.643.862 filas · sin datos personales", "→ bloque 1"),
    ("stvsubj.csv", "Banner · descripción de materias", "1.118 filas · sin datos personales", "→ bloque 3 (conector A)"),
    ("PLANTA_FISICA_PREPROCESADA.csv + BLOQUES_ESTANDAR_01122025.csv", "espacios con capacidad y clase · 19 bloques",
     "4.862 espacios · sin datos personales", "→ bloque 4 (conector B)"),
    ("SERIE_COMPLETA_REAL_VS_PROYECTADO.csv", "Euribia · histórico real vs proyectado",
     "78.125 filas · sin datos personales", "→ bloque 7 (conector C)"),
    ("DIAGNOSTICO_BACKTEST_28092026.csv", "Ariadna · error de su propio backtest", "462 filas · sin datos personales",
     "→ bloque 11 (conector D)"),
    ("PROYECCION_MATRICULA_2026_2031_28092026.parquet", "Ariadna · período × carrera × sede (real y proyectado)",
     "14.864 filas · sin datos personales", "→ bloques 3, 11 y 13 (conectores E, F, G)"),
    ("PROYECCION_INSCRITOS_2026_2027.csv", "Euribia · inscritos P10 / P50 / P90", "22.142 filas · sin datos personales",
     "→ bloque 13 (conector H)"),
]

ed = Editor.load(OUT + ".excalidraw")
sh = [e for e in ed.scene["elements"] if e["type"] != "text" and not e.get("isDeleted")]
x0 = min(e["x"] for e in sh); x1 = max(e["x"] + e["width"] for e in sh)
y0 = min(e["y"] for e in sh); y_flujo = max(e["y"] + e["height"] for e in sh)

# bloque de insumos a la derecha del flujo, bajo el recuadro DID
XI, WI = x1 + 180, 1700
ed.add_node("Dirección de Ingeniería de Datos", x=XI + WI - 1500, y=y0 - 330, w=1500, h=150, font_size=84,
            color=("#2f9e44", "#ebfbee"), stroke_style="dashed", rounded=True)

for n, b in NUM.items():                                         # insignias de 48 px sobre la esquina
    el = ed.get(b)
    dx, dy = (el["width"] / 4, el["height"] / 4) if el["type"] == "diamond" else (0, 0)
    r_ = 48 if len(n) == 1 else 80                              # dos dígitos no caben en 48 px a 20 px
    ed.add_node(n, shape="ellipse", x=el["x"] + dx - r_ / 2, y=el["y"] + dy - r_ / 2, w=r_, h=r_, min_w=r_, min_h=r_,
                font_size=20, color=COLOR[n], max_width=80)

n_ins = len(INSUMOS_DL) + len(INSUMOS_ARCH)
YI, HI = y0 - 120, 260 + n_ins * 165
ed.add_node("", x=XI, y=YI, w=WI, h=HI, color=("#343a40", "#e9ecef"), stroke_style="dashed")

# fichas: 5 columnas de ~1.480 × 640 con 52 px entre columnas (§8.1)
W, Hf, G = 1480, 430, 52
y_b = max(y_flujo, YI + HI) + 260
for i, (t, ins, log, sal) in enumerate(FICHAS):
    c, r = i % 5, i // 5
    body = "\n".join([t, "", "INSUMO", f"  {ins}", "LÓGICA"] + [f"  • {l}" for l in log] + [f"SALIDA {sal}"])
    ed.add_node(body, x=x0 + c * (W + G), y=y_b + 140 + r * (Hf + G), w=W, h=Hf, font_size=20,
                align="left", valign="top", color=COLOR[t.split(" ")[0]], max_width=W - 40)
y_c = y_b + 140 + 5 * (Hf + G) + 40

NOTA = [
    "NOTA / HALLAZGO · modelo vigente al 30-10 (D14–D19)",
    "• Método en una frase: un pronóstico ingenuo estacional combinado con una simulación Monte Carlo por bootstrap estratificado,"
    " con el peso calibrado por validación walk-forward y la incertidumbre cuantificada con predicción conforme.",
    "• A 1 año el modelo le gana al naive por poco (WAPE relativo de C1-TEN 0,97–1,15): lo firme es el crecimiento y el riesgo por campus,"
    " no la hora exacta de cada alerta.",
    "• «WAPE relativo al naive» = WAPE del modelo ÷ WAPE del naive en el mismo período (medida relativa, Hyndman & Koehler, 2006);"
    " no es el MASE escalado dentro de la muestra.",
    "• 2028–2030 validados con pocos pares y 2031 sin validar (k_h extrapolado). La banda cubre 75 % frente al 80 % buscado:"
    " la garantía del conformal supone intercambiabilidad, que una serie de tiempo no cumple del todo.",
    "• La programación sintética es una sola realización con horarios fijos y asignación voraz: el déficit es conservador y no tiene banda.",
    "• Ariadna se usa tal cual; su error entra por su propio backtest. Capacidad de la planta y laboratorios de C01 por validar con infraestructura.",
    "• Fuera del flujo (diagnóstico, no alimentan el entregable): PIPELINES §4–§5 y §8 (regla de secciones, control y validación aislada del perfil).",
]
ed.add_node("\n".join(NOTA), x=x0, y=y_c, w=3 * W + 2 * G, font_size=22, align="left", valign="top", color="yellow",
            max_width=3 * W + 2 * G - 60)
print("check etapa 2:", ed.check())

# textos libres: título, subtítulo, títulos de sección, insumos y leyenda de colores (§8.1)
Es = ed.scene["elements"]
GR, GF = "#343a40", "#e9ecef"
Es.append(canon_post._text(x0, y0 - 330, "Sóstrato · flujo detallado del pipeline y del modelo", 84))
sub = canon_post._text(x0, y0 - 210, f"SOSTRATO · flujo pipeline-modelo-detalle · {VERSION}", 22)
sub["strokeColor"] = "#868e96"; Es.append(sub)
Es.append(canon_post._text(x0, y_b, "Detalle por bloque · insumo → lógica → salida", 64))
Es.append(canon_post._text(XI + 30, YI + 24, f"INSUMOS · bases y archivos que usa el análisis ({n_ins})", 24))
py_ = YI + 80
Es.append(canon_post._text(XI + 30, py_, f"Data Lake nuevo · Athena · datalake_stage ({len(INSUMOS_DL)})", 24))
py_ += 50
for arch, que, grano, dest in INSUMOS_DL:
    Es.extend(canon_post.shapes_for("cylinder", XI + 40, py_, 130, 95, GR, GF, "solid", 2, []))
    Es.append(canon_post._text(XI + 200, py_ - 4, f"{arch}\n{que}\n{grano}\n{dest}", 18))
    py_ += 170
Es.append(canon_post._text(XI + 30, py_, f"Archivos ({len(INSUMOS_ARCH)})", 24))
py_ += 50
for arch, que, grano, dest in INSUMOS_ARCH:
    Es.extend(canon_post.shapes_for("parallelogram", XI + 40, py_, 130, 80, GR, GF, "solid", 2, []))
    Es.append(canon_post._text(XI + 200, py_ - 4, f"{arch}\n{que}\n{grano}\n{dest}", 18))
    py_ += 160

# cierre: leyenda de colores y convenciones
xl, yl = x0 + 3 * (W + G) + 40, y_c
Es.append(canon_post._text(xl, yl, "Leyenda", 22))
proto = next(e for e in Es if e["type"] == "rectangle")
for k, (st, fi, nombre) in enumerate([("#343a40", "#e9ecef", "Fuente, diagnóstico o consumo externo"),
                                      ("#2f9e44", "#b2f2bb", "Pipeline"), ("#9c36b5", "#eebefa", "Modelo"),
                                      ("#f08c00", "#ffec99", "Validación, decisión y notas"),
                                      ("#e8590c", "#ffd8a8", "Entrega y entregable"),
                                      ("#e03131", "#ffc9c9", "Rama «no» de la decisión"),
                                      ("#1971c2", "#a5d8ff", "Conector: el dato cruza franjas")]):
    Es.append(canon_post._rect_like(proto, xl, yl + 50 + k * 46, 48, 32, st, fi, "rectangle"))
    Es.append(canon_post._text(xl + 64, yl + 52 + k * 46, nombre, 22))
CONV = ("Convenciones: relleno sólido = construido y corrido · ◇ = unión · barra negra = bifurcación · círculo azul con letra = conector"
        " (sale en la columna de fuentes y entra donde está la misma letra) · una flecha entra y una sale (solo el rombo tiene dos) ·"
        " círculo con número = bloque y su ficha.")
Es.append(canon_post._text(x0, y_c + 560, CONV, 22))
for el, k in zip(Es, fractional_keys(len(Es))):
    el["index"] = k
save_scene(ed.scene, OUT + ".excalidraw")
open(OUT + ".excalidraw.md", "w", encoding="utf-8").write(scene_to_markdown(ed.scene))
print("guardado:", OUT)
