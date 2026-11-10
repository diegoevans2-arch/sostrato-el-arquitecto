"""Lámina explicativa de la programación sintética de Sóstrato, pensada para directivos (30-10).

No es un diagrama de flujo de datos (ese es SOSTRATO_flujo_pipeline-modelo-detalle): son cinco viñetas que muestran
cómo se construye la programación proyectada, con un horario semanal dibujado y las cifras reales de la corrida del
29-10 (pregrado, 1.er semestre, escenario base). Los ejemplos de clases son ilustrativos.

Uso: py diagrama_programacion_sintetica.py
"""
import os, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
HERR = os.path.normpath(os.path.join(AQUI, "..", "..", "..", "..", "Mantenedores Repo", "_HERRAMIENTAS_DIAGRAMA_EXCALIDRAW"))
sys.path.insert(0, HERR)
import _kit  # noqa: E402,F401  (deja importable excalidraw_kit)
from excalidraw_kit import Diagram  # noqa: E402

OUT = os.path.normpath(os.path.join(AQUI, "..", "..", "Documentación", "SOSTRATO_programacion-sintetica_explicacion_2026-10-30"))

d = Diagram(None, rounded=True, font_size=24, label_font_size=22)
T, S, P = 40, 26, 22                      # títulos de viñeta, texto, texto chico
PW, PH, GX, GY = 1180, 1000, 130, 140     # viñeta
VERDE, NARANJA, ROJO, GRIS = ("#2f9e44", "#b2f2bb"), ("#e8590c", "#ffd8a8"), ("#e03131", "#ffc9c9"), ("#868e96", "#f1f3f5")
AZUL, VIOLETA = ("#1971c2", "#a5d8ff"), ("#9c36b5", "#eebefa")


def txt(t, x, y, font_size=24, max_width=2000, color="#1e1e1e"):
    # texto libre como nodo «text»: así se mueve con el resto si el layout normaliza posiciones
    return d.node(t, shape="text", x=x, y=y, font_size=font_size, max_width=max_width, align="left", valign="top",
                  text_color=color)


def vineta(n, titulo, x, y, w=PW, h=PH, color=GRIS):
    marco = d.node("", color=(color[0], "#ffffff"), x=x, y=y, w=w, h=h, stroke_style="dashed")
    d.node(str(n), shape="ellipse", color=color, x=x - 36, y=y - 36, w=80, h=80, font_size=40)
    txt(titulo, x=x + 60, y=y + 30, font_size=T, max_width=w - 100)
    return marco


def texto(t, x, y, w, size=S):
    return txt(t, x=x, y=y, font_size=size, max_width=w)


def horario(x, y, celdas, cw=150, ch=64, horas=("08:00", "09:30", "11:00", "14:40", "17:35")):
    dias = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"]
    for j, dia in enumerate(dias):
        txt(dia, x=x + 90 + j * (cw + 8) + cw / 2 - 22, y=y, font_size=P)
    for i, h in enumerate(horas):
        txt(h, x=x, y=y + 44 + i * (ch + 8) + ch / 2 - 14, font_size=P)
        for j in range(len(dias)):
            lbl, col = celdas.get((i, j), ("", ("#dee2e6", "#f8f9fa")))
            d.node(lbl, color=col, x=x + 90 + j * (cw + 8), y=y + 44 + i * (ch + 8), w=cw, h=ch, font_size=18)


# ---------------------------------------------------------------- encabezado
txt("Sóstrato · cómo se construye la programación proyectada", x=0, y=-330, font_size=64, max_width=2400)
sub = txt("Programación sintética · pregrado, 1.er semestre, escenario base · cifras de la corrida del 29-10-2026 · "
          "los nombres de clases son ejemplos ilustrativos", x=0, y=-235, font_size=24, color="#868e96", max_width=2400)
d.node("Dirección de Ingeniería de Datos", color=("#2f9e44", "#ebfbee"), x=3 * PW + 2 * GX - 1300, y=-345, w=1300, h=110,
       font_size=56, stroke_style="dashed")
texto("La pregunta: si se sigue programando como hoy, ¿en qué horarios y campus faltarán salas? Para responderla se arma, "
      "clase por clase, la programación de cada semestre futuro y se le busca sala en la planta física actual.",
      0, -150, 3 * PW + 2 * GX, 28)

# ---------------------------------------------------------------- fila 1
x1, x2, x3, y1 = 0, PW + GX, 2 * (PW + GX), 0
v1 = vineta(1, "Se parte de la programación real de 2026", x1, y1, color=VERDE)
c = {(0, 0): ("Anatomía\n45", VIOLETA), (0, 2): ("Química\n48", AZUL), (1, 1): ("Cálculo\n60", NARANJA),
     (1, 3): ("Anatomía\n45", VIOLETA), (2, 0): ("Derecho\n70", VERDE), (2, 4): ("Química\n48", AZUL),
     (3, 2): ("Inglés\n25", GRIS), (3, 5): ("Taller\n18", GRIS), (4, 1): ("Derecho\n70", VERDE)}
horario(x1 + 60, y1 + 150, c)
texto("9.397 clases (secciones) en el 1.er semestre de 2026. De cada una se sabe el día, la hora, la sala y cuántos "
      "alumnos tiene.", x1 + 60, y1 + 560, PW - 120)
texto("Es la base: el futuro se arma con estas mismas clases.", x1 + 60, y1 + 720, PW - 120, P)

v2 = vineta(2, "¿Cuántas clases harán falta?", x2, y1, color=AZUL)
base_y, esc = y1 + 760, 0.042
for k, (anio, n, ins) in enumerate([("2026", 9397, "329.627"), ("2027", 9885, "345.663"), ("2031*", 12263, "428.813")]):
    h = n * esc
    bx = x2 + 120 + k * 340
    d.node(f"{n:,}".replace(",", ".") + "\nclases", color=AZUL, x=bx, y=base_y - h, w=240, h=h, font_size=24)
    txt(anio, x=bx + 85, y=base_y + 15, font_size=S)
    txt(f"{ins} alumnos", x=bx + 10, y=base_y + 55, font_size=P)
texto("Clases = alumnos inscritos proyectados ÷ tamaño típico de una clase, por sede y tipo de clase "
      "(teórica, laboratorio, taller…). El tamaño típico es el que reproduce lo que se programó en 2026.",
      x2 + 60, y1 + 130, PW - 120, P)
texto("* 2031 sin validar", x2 + 60, y1 + 930, PW - 120, 20)

v3 = vineta(3, "Las clases nuevas son copias de clases reales", x3, y1, color=VIOLETA)
orig = d.node("Kinesiología · teórica\nviernes 08:40\n52 alumnos (2026)", color=VIOLETA, x=x3 + 90, y=y1 + 220, w=380, h=150,
              font_size=24)
cop1 = d.node("Kinesiología · teórica\nviernes 08:40\n61 alumnos (2030)", color=VIOLETA, x=x3 + 680, y=y1 + 160, w=400, h=150,
              font_size=24, stroke_style="dashed")
cop2 = d.node("Kinesiología · teórica (copia)\nviernes 08:40\n61 alumnos (2030)", color=VIOLETA, x=x3 + 680, y=y1 + 380, w=400,
              h=150, font_size=24, stroke_style="dashed")
d.edge(orig, cop1, "crece", font_size=P)
d.edge(orig, cop2, "se copia", font_size=P, dst_side="left")
texto("Si hacen falta más clases, se copian clases que ya existen en la misma sede y del mismo tipo, elegidas al azar. "
      "La copia mantiene el día y la hora de la original, y los alumnos de cada clase crecen con la proyección.",
      x3 + 60, y1 + 600, PW - 120)

# ---------------------------------------------------------------- fila 2
y2 = PH + GY
W4 = int(1.55 * PW)
v4 = vineta(4, "A cada clase se le busca sala", 0, y2, w=W4, color=NARANJA)
clase = d.node("61 alumnos\nviernes 08:40", color=VIOLETA, x=120, y=y2 + 160, w=300, h=110, font_size=26)
salas = [(20, "sala de 20"), (40, "sala de 40\nno cabe"), (65, "sala de 65\n✓ la más chica\nque sirve"), (100, "sala de 100\nsobra espacio")]
sx = 120
ids = {}
for cap, lbl in salas:
    w = 120 + cap * 3.2
    col = VERDE if cap == 65 else GRIS
    ids[cap] = d.node(lbl, color=col, x=sx, y=y2 + 520 - cap * 2, w=w, h=cap * 2 + 60, font_size=22)
    sx += w + 50
d.edge(clase, ids[65], "", font_size=P, src_side="right", dst_side="top")
texto("Se busca una sala libre a esa hora, del tipo correcto (sala o laboratorio), primero en el mismo edificio y "
      "después en el campus. Se elige la más chica en que la clase cabe.", 520, y2 + 150, W4 - 600, P)
yo = y2 + 680
d.node("Tiene sala", color=VERDE, x=120, y=yo, w=300, h=80, font_size=26)
texto("la clase cabe en una sala libre.", 450, yo + 22, 520, P)
d.node("Sobrecupo", color=NARANJA, x=120, y=yo + 100, w=300, h=80, font_size=26)
texto("cabe con la holgura con que hoy se usan los espacios (laboratorios hasta ×1,33), pero supera la capacidad nominal.",
      450, yo + 112, W4 - 520, P)
d.node("Sin sala (déficit)", color=ROJO, x=120, y=yo + 200, w=300, h=80, font_size=26)
texto("todas las salas del tamaño necesario ya están ocupadas a esa hora. Ej.: Psicología teórica, 75 alumnos, "
      "lunes 10:10, sin sala de 60 o más libre.", 450, yo + 212, W4 - 520, P)

x5 = W4 + GX
W5 = 3 * PW + 2 * GX - x5
v5 = vineta(5, "Resultado: dónde no cabe", x5, y2, w=W5, color=ROJO)
c5 = {(0, 0): ("", VERDE), (0, 1): ("", ROJO), (0, 2): ("", NARANJA), (0, 3): ("", ROJO), (0, 4): ("", VERDE),
      (1, 0): ("", ROJO), (1, 1): ("", ROJO), (1, 2): ("", ROJO), (1, 3): ("", NARANJA), (1, 4): ("", ROJO),
      (2, 0): ("", NARANJA), (2, 1): ("", VERDE), (2, 2): ("", ROJO), (2, 3): ("", VERDE), (2, 4): ("", NARANJA),
      (3, 0): ("", VERDE), (3, 2): ("", VERDE), (3, 4): ("", NARANJA), (4, 1): ("", VERDE), (4, 3): ("", VERDE)}
horario(x5 + 60, y2 + 150, c5, cw=110, ch=56)
kx = x5 + 900
d.node("Clases sin sala\n5,3 % (2027) → 17,4 % (2031*)", color=ROJO, x=kx, y=y2 + 170, w=W5 - 960, h=130, font_size=28)
d.node("Sobrecupo\n8,8 % → 14,9 %", color=NARANJA, x=kx, y=y2 + 330, w=W5 - 960, h=110, font_size=28)
d.node("7 de cada 10 clases sin sala\npiden salas de 60 o más asientos", color=GRIS, x=kx, y=y2 + 470, w=W5 - 960, h=120,
       font_size=26)
texto("Así se ve en un campus: cada casillero es una hora de la semana; rojo, donde quedan clases sin sala. "
      "Sumado por campus y hora, esto dice qué tamaño de sala falta y dónde.", x5 + 60, y2 + 640, W5 - 120, P)

# flechas entre viñetas (orden de lectura, no flujo de datos)
for a, b in ((v1, v2), (v2, v3)):
    d.edge(a, b, width=4)
d.edge(v3, v4, width=4, src_side="bottom", dst_side="top")
d.edge(v4, v5, width=4)

# ---------------------------------------------------------------- lo que conviene saber
y3 = y2 + PH + 110
d.node("Lo que conviene saber\n"
       "• Los horarios no se mueven: el déficit mide la falta de salas si se programa con los horarios de hoy; "
       "reorganizar horarios podría reducirlo.\n"
       "• Es una sola simulación y la asignación es simple (no busca la combinación óptima): la cifra de clases sin sala "
       "es prudente, tiende a ser algo alta.\n"
       "• Esta programación sirve para ver QUÉ TAMAÑO de sala falta. Para decidir DÓNDE y CUÁNDO se usa el mapa de alertas, "
       "que sí tiene margen de error y está validado con años anteriores.\n"
       "• 2031* es una proyección sin validar: se lee como tendencia.",
       color=("#f08c00", "#fff9db"), x=0, y=y3, w=3 * PW + 2 * GX, h=250, font_size=26, align="left", valign="top")

d.layout("none")
print("check:", d.check())
d.save(OUT)
print("guardado:", OUT)
