---
date: 2026-10-28
tags:
  - figuras
  - alertas
  - sostrato
status: draft
type: indice
project: sostrato
owner: Dirección de Ingeniería de Datos
author: Diego Evans Pérez Paz
version: "1.3"
---

# Sóstrato el Arquitecto · Figuras para el informe de alertas

Generadas con `Notebooks + Scripts/scripts_fase1/figuras_informe.py`, a partir de los mismos datos que la demo (`datos_alertas.py` sobre `BBDD/`). Salvo que se indique otra cosa: **escenario base, pregrado, 1.er semestre (sufijo 10)**. Las cifras exactas están en `cifras_figuras.json`.

| Versión | Fecha | Cambio |
|---|---|---|
| 1.3 | 29-10 | Renombre a Sóstrato el Arquitecto + F5 recapturada con la demo nueva (`DEMO_SOSTRATO.html`); mismas cifras y mismo encuadre |
| 1.2 | 28-10 | Rótulo del rango de 2027: «banda de Euribia, extrema» pasa a «**banda de Euribia: otra definición, no comparable con 2028–2031**» en la demo y en F1 (pedido del equipo de modelo). El aviso 2 explica cómo se construye cada banda |
| 1.1 | 28-10 | Regeneradas con **D19**: en 2028–2031 el modelo usa el naive escalado (C1E) en vez de C1; 2027 no cambia. Suben las alertas desde 2028; el déficit, el sobrecupo y la programación sintética no cambian. El título de F1 pasa de «se duplican» a «se triplican» |
| 1.0 | 27-10 | Primera versión, con D18 (tamaño de sala) |

Decisiones que aplican (confirmadas por Diego el 27-10):
- **V1:** alerta = `PROB_SATURA_TAMANO` ≥ 25 %; vigilancia desde 10 % y crítica desde 50 %;
- **V2:** escenario base por defecto;
- **V4:** el tamaño de sala se considera.

| Figura | Mensaje | Cifras (v1.1) |
|---|---|---|
| `F1_celdas_en_alerta_por_anio.png` | Las horas sin espacio suficiente **se triplican** hacia 2031 | Celdas en alerta: **93 → 125 → 179 → 251 → 297**. Rango bajo–alto de 2028 a 2031: 66–186, 80–274, 120–344 y 156–381. 2027 bajo/alto (50–144) va marcado como «banda de Euribia: otra definición, no comparable con 2028–2031». Críticas (≥ 50 %): 17 → 33 → 58 → 94 → 136. Con ≥ 10 %: 181 → 297 → 366 → 427 → 465 (lunes a sábado; con domingo, 466 en 2031) |
| `F2_deficit_y_sobrecupo.png` | Lo que falta son, sobre todo, salas grandes | Sin cambio respecto de la v1.0. Déficit **5,3 % → 7,6 % → 10,7 % → 13,9 % → 17,4 %**. Sobrecupo tolerado **8,8 % → 14,9 %**. En 2027, el 62 % del déficit pide salas de 60 o más. Base: sufijo 10, ponderado por `PESO_SEMANAS` |
| `F3_alertas_por_campus.png` | Dónde aparecen: C01, C04 y C06 primero; C02 entra desde 2029 | En 2031: C01 93, C04 64, C06 50, C03 37, C02 32, C07 21, C05 0. Primera alerta: C01, C04, C06 y C07 en 2027; C03 en 2028; C02 en 2029 |
| `F4_mapa_2027_vs_2030_C04_salas.png` | Cómo se extienden las alertas en las salas de Sede Sur | 24 celdas en alerta en 2027 → **60** en 2030, desde las mañanas hacia la tarde |
| `F4_mapa_2027_vs_2030_C01_laboratorios.png` | Laboratorios de Campus 01: la alerta nueva por tamaño | 43 en 2027 (27 en 60+ y 16 en 41-60) → 46 en 2030. **A validar con infraestructura** |
| `F5_portada_3d_C01_2030.jpg` | Portada: «Dónde no cabe», Campus 01, miércoles 9:30 de 2030 | Recapturada el 29-10 desde `DEMO_SOSTRATO.html#sim/nube/C01/2030/10/base/todos`, con el encabezado «Sóstrato el Arquitecto» (sin «Cirilo 2049»). Cifras sin cambio: 181 de 197 espacios ocupados y 34 secciones sin sala, la mayoría pidiendo 60 o más. Tamaño 800 × 585, el máximo que entrega el navegador integrado; un intento de mayor resolución uniendo cuadrantes dejó una costura en el 3D y se descartó |

**Avisos que deben acompañar las figuras:**
1. **2031 es extrapolado** (`VALIDADO = False`); en las figuras va con «*» y sombreado.
2. **Los escenarios bajo y alto no se construyen igual en 2027 que en 2028–2031**, así que el rango de 2027 no es comparable con el de los años siguientes. El rótulo es «banda de Euribia: otra definición, no comparable con 2028–2031».
   - **2027:** suma los cuantiles de Euribia (P10/P90) por tipo de curso, lo que equivale a suponer que todos los cursos suben o bajan a la vez.
   - **2028–2031:** son los escenarios de Ariadna ensanchados según su backtest, más el factor k_h del naive escalado (C1E, D19).
   - Con D19, el rango de 2028–2031 es más ancho que el de 2027. La diferencia es de definición, no de amplitud.
3. **La banda P10–P90 se lee celda por celda:** las cifras cuentan celdas por escenario y nunca suman bandas.
4. **El valor del modelo está en el crecimiento y el riesgo, no en la ubicación fina:** la hora exacta de una alerta puede moverse.
5. **Laboratorios de 60 o más en C01:** a validar con infraestructura; puede ser gestión de grupos y no falta de espacio.
6. **El sobrecupo no es déficit:** la sección cabe por tolerancia, pero supera la capacidad nominal.
7. **D19 en 2028:** en H+2, el naive escalado empeora el MASE en 0,011 frente a C1 (dentro del ruido); la ganancia del cambio es desde 2029 (detalle en DIAGNOSTICO_EMPALME §19).

---

> **Dirección de Ingeniería de Datos — Universidad Ficticia**
> Responsable: Diego Evans Pérez Paz
