---
title: "Documento técnico-funcional · Modelo de Sóstrato el Arquitecto"
tags:
  - nota-tecnica
  - machine-learning
  - ocupacion-espacios
  - banner9
audiencias: [puente, ejecutivo, tecnico]
status: activo
type: documento-tecnico-funcional
project: sostrato
notebook: Notebooks + Scripts/Modelos.ipynb
entregable: BBDD/OCUPACION_Y_DEFICIT.parquet
version: "1.0"
fecha_creacion: 2026-11-05
ultima_actualizacion: 2026-11-05
owner: Dirección de Ingeniería de Datos
author: Diego Evans Pérez Paz
---

# Documento técnico-funcional · Modelo de Sóstrato el Arquitecto

> [!info] 📌 Ficha
> **Artefacto**: `Notebooks + Scripts/Modelos.ipynb` (19 celdas, 9 de código) y su banco `VALIDACION_WALKFORWARD.ipynb` (43 celdas, 25 de código)
> **Versión documentada**: commit `93dd390` · corrida del 2026-10-29 (`MODELO_METADATOS.json`)
> **Función**: proyecta la ocupación de salas y laboratorios de 2027 a 2031, por `período × escenario × campus × día × bloque × clase`
> **Insumos**: salidas de [[DOCUMENTO_TECNICO_FUNCIONAL_PIPELINE_SOSTRATO]] · Euribia · Ariadna
> **Salida**: `OCUPACION_Y_DEFICIT.parquet` — 147.000 × 23 · `OCUPACION_POR_RANGO.parquet` — 225.573 × 14 · `PROGRAMACION_SINTETICA.parquet` — 471.521 × 22
> **Resultado**: celdas en alerta (≥ 25 %) de **93 en 2027 a 297 en 2031**; clases sin sala de **5,3 % a 17,4 %** (pregrado, 1.er semestre, escenario base)
> **Consumidor**: planificación académica e infraestructura · informes · simulación
> **Tiempo de corrida**: no quedó registrado en el notebook (§17.2)

**Cómo leer este documento.** Está escrito para quien usa los resultados. Sigue la convención de la Guía Maestra DS: 👔 lectura ejecutiva · 🧭 puente entre negocio y técnica · 🔧 detalle técnico. §1–§2 bastan para entender qué entrega el modelo. §4–§8 explican cada etapa en lenguaje de negocio. §9 dice cuánto confiar. §12 recorre una celda real de punta a punta y responde preguntas frecuentes. §13–§24 son de consulta. Los términos y las columnas están en [[DICCIONARIO_USO_FUNCIONAL_SOSTRATO]]. Las cifras de resultados y la demostración de §12 se recalcularon sobre los parquet el 2026-11-05.

---

## 1 · Qué resuelve este modelo 👔

La pregunta de negocio es **en qué campus, día, bloque y tipo de espacio la programación académica proyectada dejará de caber en la planta física actual, de 2027 a 2031, y con qué probabilidad**, para anticipar decisiones de infraestructura y de programación.

El modelo responde en 5 pasos:

| # | Paso | Qué produce | Cifra de cierre (1.er semestre, base) |
|---:|---|---|---|
| 1 | **Volumen** | Inscritos proyectados | 329.627 en 2026 → 428.813 en 2031 (+30 %) |
| 2 | **Mapa de ocupación** | Espacios necesarios por celda | 26.419 en 2027 → 32.172 en 2031 |
| 3 | **Banda y probabilidad** | P10, P50, P90 y probabilidad de saturar | Cobertura de 75 % a 1 año |
| 4 | **Alerta por tamaño** | Celdas que no caben, según el tamaño de sala | 93 → 297 celdas en alerta |
| 5 | **Programación sintética** | Qué secciones quedan sin sala | 5,3 % → 17,4 % de las clases |

> [!abstract] 👔 En una frase
> El modelo no predice en qué sala estará cada curso. Funciona como un **parte meteorológico**: dice dónde y cuándo es probable que falten espacios y cómo crece ese riesgo. Lo firme es la tendencia y el riesgo por campus, no la hora exacta de cada alerta.

> [!danger] 🚨 Lo que no se puede leer mal
> **`Alerta = PROB_SATURA_TAMANO ≥ 25 %`, y cada escenario se cuenta por separado.**
> Una celda en alerta no significa que faltan salas con certeza: significa que hay al menos 1 posibilidad en 4. Tampoco se suman los P10 o P90 de varias celdas para armar un total: la banda se lee celda por celda.

> [!warning] ⚠️ La ventaja sobre el año anterior es pequeña
> A 1 año, el modelo apenas le gana a repetir el mapa del año anterior: su error relativo va de 0,97 a 1,15, y ni con el volumen real perfecto mejora más de 6 %. Su valor está en medir el crecimiento y el riesgo, no en afinar la ubicación (§9).

> [!tip] 💡 Dónde se concentra el problema
> En 2031, Campus 01 suma 93 celdas en alerta, Sede Sur 64 y Campus 06 50. Entre el 62 % y el 73 % de las clases sin sala piden salas de 60 asientos o más. Campus 05 no tiene alertas en el período.

### 1.1 · Qué técnica usa cada paso

| Paso | Nombre metodológico | En palabras simples |
|---|---|---|
| Línea de comparación | **Naive estacional** | Repetir el mismo semestre del año anterior |
| Crecimiento de secciones (G1b) | **Monte Carlo por bootstrap estratificado** | Sortear secciones reales de 2026 hasta llegar al volumen futuro |
| Mapa de 2027 (C1) | **Combinación de pronósticos** | Promedio ponderado entre el naive y G1b |
| Mapa de 2028–2031 (C1E) | **Naive estacional escalado** | El naive, multiplicado por el crecimiento de salas |
| Incertidumbre | **Predicción conforme dividida** | La banda se arma con los errores reales que tuvo el modelo |
| Validación | **Walk-forward** | Probar en el pasado usando solo lo que se sabía en ese momento |
| Programación | **Remuestreo por cuotas y asignación voraz** | Sortear secciones y darle a cada una la sala libre más chica que sirva |

**Referencias verificadas en la Guía Maestra:** Hyndman & Athanasopoulos (2021), naive estacional · Hyndman & Koehler (2006), medidas relativas · Vovk et al. (2005) y Angelopoulos & Bates (2023), predicción conforme · Tashman (2000), walk-forward.

---

## 2 · Alcance funcional 🧭

### 2.1 · Universo

| Dimensión | Valor | Regla |
|---|---|---|
| Niveles | Pregrado (UG) y Advance (AV) | Sufijos `10`, `20` (UG) y `05`, `15`, `25` (AV) |
| Período proyectado | 2027 a 2031 | 25 períodos en `PERIODO` |
| Base | Mismo sufijo de 2026 | `202605`, `202610`, `202615`, `202620`, `202625` |
| Campus | C01, C07, C04, C06, C02, C05 y C03 | `COD_CAMPUS_EDIFICIO` |
| Espacios | Sala y laboratorio | `CLASE` |
| Escenarios | Bajo, base y alto | `ESCENARIO` |
| **Grano** | `PERIODO × ESCENARIO × COD_CAMPUS_EDIFICIO × DIA × BLOQUE × CLASE` | Una fila es una celda del mapa |

Las cifras de este documento son de **pregrado, sufijo 10 (1.er semestre), escenario base**, salvo que se indique otra cosa.

### 2.2 · Qué queda fuera

| Exclusión | Regla | Efecto |
|---|---|---|
| Postgrado | Períodos terminados en `00` | La ocupación total de cada sala es mayor que la mostrada |
| Espacios externos, «espacio UNIV» y salas virtuales | Clasificación del pipeline | No cuentan como oferta |
| Obras futuras y cambios de horario | La planta y la forma de programar quedan fijas | No hay escenarios de oferta |
| Domingo en las vistas | `DIA = DOMINGO` existe en los parquet, sin alertas | 2031 muestra 465 celdas ≥ 10 % en las vistas y 466 en los parquet |
| Programación de escenarios bajo y alto | Solo existe para el escenario base | Salas y 3D siempre muestran el base |

### 2.3 · Glosario

| Término | Significado en este modelo |
|---|---|
| **Celda** | Campus × día × bloque × clase, en un período y escenario |
| **Bloque** | Módulo de 40 minutos. Son 19 bloques estándar, más el 0, «antes de las 08:00» |
| **Ocupación** | Espacios usados en la celda, ponderados por semanas |
| **H** | Años entre la base (2026) y el objetivo: 2027 = H+1 … 2031 = H+5 |
| **Naive** | El mapa real del mismo sufijo de 2026 |
| **MASE** | WAPE del modelo ÷ WAPE del naive en el mismo período. Bajo 1 le gana al naive. Es una medida relativa simple, no el MASE escalado dentro de muestra de la literatura |
| **Sesgo** | Cuánto se pasa (+) o se queda corto (−) el total proyectado |
| **Cobertura** | Porcentaje de celdas donde lo real cayó dentro de P10–P90. La meta es 80 % |

---

## 3 · Arquitectura y linaje de datos 🔧

```
┌─ FUENTES ──────────────────────────────────────────────────────────┐
│ PIPELINES: PROG_HIST_NRC · PLANTILLAS_NRC · OFERTA_ESPACIOS        │
│ Euribia: inscritos 2027 · Ariadna: matrícula hasta 2031            │
└──────────────────────────────┬─────────────────────────────────────┘
                               ▼
┌─ BANCO DE VALIDACIÓN (§9) ─────────────────────────────────────────┐
│ 10 orígenes a 1 año y pseudo-backtest de 1 a 4 años                │
│ Elige modelo, pesos, banda y ensanche por horizonte                │
└──────────────────────────────┬─────────────────────────────────────┘
                               ▼
┌─ A · VOLUMEN (§4) ─────────────────────────────────────────────────┐
│ Inscritos de 2026 × razón de crecimiento por campus y materia      │
│ VOLUMEN_PROYECTADO · 428.813 inscritos en 2031                     │
└───────────────┬──────────────────────────────┬─────────────────────┘
                ▼                              ▼
┌─ B · MAPA (§5) ───────────────┐  ┌─ E · PROGRAMACIÓN (§8) ─────────┐
│ C1 en 2027, C1E desde 2028    │  │ Inscritos ÷ estándar real       │
│ MAPA_PROYECTADO · 147.000     │  │ Una sala por sección, o déficit │
└───────────────┬───────────────┘  │ PROGRAMACION_SINTETICA 471.521  │
                ▼                  └────────────────┬────────────────┘
┌─ C · BANDA (§6) ──────────────┐                   │
│ P10, P50, P90 y simulaciones  │                   │
└───────────────┬───────────────┘                   │
                ▼                                   │
┌─ D · ALERTA (§7) ─────────────┐                   │
│ Demanda contra espacios,      │                   │
│ por tamaño de sala            │                   │
└───────────────┬───────────────┘                   │
                └───────────────┬───────────────────┘
                                ▼
┌─ ENTREGA ──────────────────────────────────────────────────────────┐
│ OCUPACION_Y_DEFICIT · OCUPACION_POR_RANGO · MODELO_METADATOS       │
│ Consumo: informes y simulación                                     │
└────────────────────────────────────────────────────────────────────┘
```

### 3.1 · Insumos

| # | Insumo | Qué aporta | Origen | En repo |
|---:|---|---|---|:---:|
| 1 | `PROG_HIST_NRC`, `PLANTILLAS_NRC`, `OFERTA_ESPACIOS`, `UNIDAD_ACADEMICA` | Secciones reales, uso de salas y oferta | `PIPELINES.ipynb` | ❌ |
| 2 | `BANDA_CUANTILES`, `BANDA_HORIZONTE`, `ARIADNA_ERROR_HORIZONTE`, `VALIDACION_RESULTADOS` | Modelo adoptado, pesos y banda | Banco | ❌ |
| 3 | `PROYECCION_INSCRITOS_2026_2027.csv` | Volumen AV de 2027 y banda de 2027 | Euribia | ❌ |
| 4 | `PROYECCION_MATRICULA_2026_2031_28092026.parquet` | Crecimiento de 2028 a 2031 | Ariadna, usada sin modificar | ❌ |

> [!warning] ⚠️ Euribia y Ariadna son insumos
> Sus errores se heredan. Ariadna subestima el crecimiento de pregrado: su error medio es −0,8 %, −4,4 % y −8,6 % a 1, 2 y 3 años. Se compensa con el ensanche de escenarios (§6.3) y con C1E (§5.3), sin tocar Ariadna.

### 3.2 · Código y orden de ejecución

| Orden | Notebook · sección | Qué hace | Salida |
|---:|---|---|---|
| 1 | `VALIDACION_WALKFORWARD` | Compara modelos y calibra | `VALIDACION_*`, `BANDA_*` |
| 2 | `Modelos` §3 | Volumen | `VOLUMEN_PROYECTADO` |
| 3 | `Modelos` §4 | Número de secciones | `SECCIONES_PROYECTADAS` |
| 4 | `Modelos` §5 | Mapa y banda | `MAPA_PROYECTADO` |
| 5 | `Modelos` §6 | Programación sintética | `PROGRAMACION_SINTETICA` |
| 6 | `Modelos` §7 | Ocupación contra oferta | `OCUPACION_Y_DEFICIT`, `OCUPACION_POR_RANGO` |
| 7 | `Modelos` §8 | Controles y metadatos | `MODELO_METADATOS.json` |

---

## 4 · Volumen: cuántos inscritos habrá 🧭

El volumen no se proyecta asignatura por asignatura. Se aplica una **razón de crecimiento** a los inscritos de 2026, por campus × materia × componente.

```
Inscritos proyectados = Inscritos de la base × razón
```

| Período | Pregrado | Advance | Por qué |
|---|---|---|---|
| **2027** | **TEN**: tendencia del campus entre 2025 y 2026 | **EUR**: crecimiento de Euribia | Son las variantes que ganan en el banco (D15) |
| **2028–2031** | Razón de 2027 × crecimiento anual de Ariadna, por carrera y sede | Igual | Euribia solo sirve a 1–2 semestres (D12) |

| Escenario | 2027 | 2028–2031 |
|---|---|---|
| **Bajo y alto** | Cuantiles P10 y P90 de Euribia, por tipo de curso | Escenarios de Ariadna, ensanchados según su propio error |

> [!warning] ⚠️ Los rangos de 2027 y de 2028–2031 no son comparables
> En 2027, bajo y alto suponen que todos los cursos caen o suben a la vez. Desde 2028 son escenarios de matrícula. El rango de 2027 no es más estrecho porque haya menos incertidumbre: se construye distinto.

| Período (sufijo 10, base) | Inscritos | Sobre 2026 |
|---|---:|---:|
| 2026 (real) | 329.627 | — |
| 2027 | 345.663 | +4,9 % |
| 2028 | 364.946 | +10,7 % |
| 2029 | 385.183 | +16,9 % |
| 2030 | 406.469 | +23,3 % |
| 2031 | 428.813 | +30,1 % |

La razón se acota entre 0,25 y 4. No se usa TEN en Advance porque en 2026 su matrícula se trasladó de Campus 02 a Campus 05, y la tendencia extrapolaría ese traslado como si se repitiera.

---

## 5 · Mapa: cuántos espacios se necesitan 🧭

### 5.1 · Las dos piezas

**El naive** es el mapa real de 2026: cuántas salas se ocuparon en cada celda, contadas por sala.

**G1b** responde qué pasaría con más alumnos. Sortea secciones físicas reales de 2026 por estrato (campus × unidad × clase × componente) hasta alcanzar el volumen futuro, y las ubica en sus horarios reales.

> [!tip] 💡 Por qué las secciones crecen menos que los inscritos
> Cuando hay más alumnos, parte del crecimiento llena las secciones que ya existen. Por eso los espacios crecen como `razón^β`, con β = 0,82 en el sufijo 10 y 0,80 en el 20: si los inscritos suben 10 %, las salas suben cerca de 8 %.

### 5.2 · 2027: C1

```
C1 = w × naive + (1 − w) × G1b
```

| Nivel | Modelo | w |
|---|---|---:|
| Pregrado | `C1-TEN` | 0,8 |
| Advance | `C1-EUR` | 0,0 |

### 5.3 · 2028–2031: C1E

```
C1E = w × naive escalado + (1 − w) × G1b           (w = 1,0)
naive escalado = naive × crecimiento de salas del campus × clase
```

El naive solo es una copia que no crece: con C1, el centro del mapa crecía 4 % entre 2027 y 2031, mientras los inscritos crecían 24 %. C1E corrige ese sesgo.

| Período | Factor de escala (mediana) | Centro del mapa |
|---|---:|---:|
| 2027 | 1,00 | 26.419 |
| 2028 | 1,07 | 28.183 |
| 2029 | 1,12 | 29.459 |
| 2030 | 1,17 | 30.790 |
| 2031 | 1,22 | 32.172 |

> [!warning] ⚠️ Aviso declarado de C1E
> En 2028 (H+2), C1E empeora el MASE en 0,011 frente a C1, dentro del ruido de ±0,02. La ganancia aparece desde H+3. Se decidió usarlo desde 2028 para que el mapa no salte entre 2028 y 2029 (D19).

---

## 6 · Banda: cuánta incertidumbre hay 🧭

### 6.1 · Cómo se calcula

La banda se arma con los errores que el modelo tuvo en el pasado, separados por nivel, clase y tamaño de la celda.

```
e       = (real − punto) ÷ √(punto + 1)                   error normalizado
P       = punto + q × √(punto + 1)                        q sale de los errores
q largo = q50 + k_h × (q − q50)                           ensanche por horizonte
```

| Tramo del punto | Salas |
|---:|---|
| 0 | 0–5 |
| 1 | 5–20 |
| 2 | 20–50 |
| 3 | Más de 50 |

### 6.2 · Más lejos, más ancha

| Horizonte | Año | k_h pregrado | k_h Advance | Estado |
|---|---|---:|---:|---|
| H+1 | 2027 | 1,00 | 1,00 | Medido |
| H+2 | 2028 | 1,31 | 1,26 | Medido, 6 pares |
| H+3 | 2029 | 1,44 | 1,43 | Medido, 4 pares |
| H+4 | 2030 | 1,72 | 1,67 | Medido, 2 pares |
| H+5 | 2031 | 1,82 | 1,76 | **Extrapolado** |

### 6.3 · Escenarios de Ariadna

Desde 2028, bajo y alto se ensanchan alrededor del base cuando el backtest de Ariadna muestra que su banda no cubre el error real.

| Nivel | H+1 | H+2 | H+3 |
|---|---:|---:|---:|
| Pregrado | 1,13 | 1,34 | 1,76 |
| Advance | 1,00 | 1,44 | 1,52 |

### 6.4 · Probabilidad de saturar

Se simula la ocupación de cada celda sorteando errores de la misma distribución de la banda. La probabilidad es el porcentaje de simulaciones en que la demanda supera los espacios: 100 simulaciones en 2027 y 50 en 2028–2031.

> [!warning] ⚠️ Lo que significa «2031 extrapolado»
> 2031 se proyecta con el mismo método. Lo que no se pudo medir es su error, porque el historial alcanza hasta H+4. Por eso `VALIDADO = False` solo en 2031 y su ensanche se extrapoló.

---

## 7 · Alerta: la sala tiene que ser del tamaño necesario 🧭

Contar salas contra salas esconde el problema: una sección de 80 no cabe en una sala libre de 20. Por eso la alerta se calcula por rango de capacidad.

### 7.1 · La regla

```
Para cada rango r (0-20, 21-40, 41-60, 60 o más):
  demanda de r o más  contra  espacios de r o más

PROB_SATURA_TAMANO = la mayor probabilidad entre los rangos
RANGO_CRITICO      = el rango donde ocurre (ante empate, el mayor)
```

Es **anidada**: una sala grande sirve para una sección chica, pero no al revés. El rango `0-20` equivale a la celda completa.

### 7.2 · Cómo se determina el tamaño que pide una sección

| Regla | Detalle |
|---|---|
| **Inscritos proyectados** | Los de 2026 × razón del estrato^(1 − β) |
| **Tolerancia por clase** | Percentil 90 de inscritos ÷ capacidad en 2026. Sala 1,00; laboratorio 1,33 (sufijo 10) y 1,32 (sufijo 20); Advance 1,00 |
| **Capacidad necesaria** | Inscritos proyectados ÷ el mayor entre la tolerancia y el sobrecupo que la sección ya tenía |
| **Oferta efectiva**, desde 21-40 | El mayor entre el inventario activo y lo que 2026 ya usa |

> [!important] 🎯 Por qué existen la tolerancia y la oferta efectiva
> Sin ellas, el modelo inventaría déficit que hoy no existe: los laboratorios que ya funcionan sobre su capacidad nominal aparecían pidiendo laboratorios de 60 o más, y las alertas de 2027 subían de 93 a 199. Con estas reglas, el año base no queda en alerta y solo el crecimiento genera falta.

### 7.3 · Semáforo

| Nivel | `PROB_SATURA_TAMANO` | Lectura |
|---|---:|---|
| Sin alerta | Menos de 10 % | Se muestra el uso esperado |
| ▲ Vigilancia | 10 % o más | Conviene mirarla |
| ◆ **Alerta** | **25 % o más** | **La cifra que se informa** |
| ● Crítica | 50 % o más | Es más probable que falte a que alcance |

Los umbrales y las reglas fueron decisiones de diseño (V1 y D18). Si se cambian, cambian todos los conteos.

---

## 8 · Programación sintética: quién queda sin sala 🧭

El mapa dice cuántos espacios faltan. La programación sintética muestra **qué tamaño falta**, sección por sección.

> [!important] 🎯 No predice cursos
> Genera secciones físicas anónimas con características reales. Una fila que dice `MT308 TEO` indica el tipo de sección que se sorteó, no que ese curso se dictará ese día.

### 8.1 · Cómo se construye

| Paso | Qué hace | Regla |
|---:|---|---|
| 1 | **Calcula cuántas secciones habrá** | Inscritos ÷ estándar real. El estándar es el percentil de tamaño que reproduce lo programado en 2026, por sede × componente |
| 2 | **Sortea secciones reales** | Por sede × componente, hasta el número del paso 1 |
| 3 | **Escala sus inscritos** | Con la razón de su tipo |
| 4 | **Busca sala** | Se queda en la suya si cabe. Si no, toma la sala libre más chica que sirva, primero en su edificio y después en su campus |
| 5 | **Marca el resultado** | Sin sala: `DEFICIT`. Cabe por tolerancia, pero supera la capacidad nominal: `SOBRECUPO` |

Existe solo para el escenario base y es **una realización con semilla fija**, no un promedio de simulaciones.

```
Clases sin sala = Σ PESO_SEMANAS de los casilleros en déficit ÷ Σ PESO_SEMANAS de todos
```

### 8.2 · Por qué el mapa y la programación no coinciden

| | Mapa | Programación |
|---|---|---|
| Qué compara | Totales por rango en cada bloque | Sección contra sala específica |
| Oferta | Efectiva: incluye lo que 2026 ya usa | Solo inventario activo |
| Se usa para | **Decidir dónde y cuándo** | **Ver qué tamaño falta** |

En Campus 02, por ejemplo, las clases sin sala crecen desde 2027, pero el mapa no da alerta hasta 2029: hay salas en uso fuera de la planta y mucha compartición de laboratorios.

---

## 9 · Validación y desempeño del modelo 🧭

### 9.1 · Scorecard a 1 año

MASE por celda contra el naive, en los orígenes de pregrado que deciden. Bajo 1 le gana al naive.

| Modelo | 202410 | 202420 | 202520 | 202610 | 202620 |
|---|---:|---:|---:|---:|---:|
| C1 con volumen real (techo) | 1,000 | 0,992 | 0,987 | 0,959 | 0,944 |
| **C1-TEN (adoptado en 2027)** | **1,000** | **0,971** | **1,152** | **0,996** | **0,996** |
| C1-EUR | 1,000 | 1,016 | 1,047 | 1,000 | 1,000 |
| C1E-TEN | 0,942 | 0,946 | 1,232 | 1,046 | 1,124 |

> [!important] 🎯 Regla de adopción
> Ganarle al naive en la mayoría de los orígenes que deciden, tanto por celda como por campus × día × bloque. C1-TEN la cumple, con 3 de 5 en ambos granos, pero por poco y con una pérdida marcada en 202520.

| Medida del naive y de C1-TEN | 202410 | 202420 | 202520 | 202610 | 202620 |
|---|---:|---:|---:|---:|---:|
| WAPE del naive, por celda | 0,147 | 0,178 | 0,228 | 0,188 | 0,166 |
| WAPE de C1-TEN, por celda | 0,147 | 0,173 | 0,262 | 0,187 | 0,165 |
| Sesgo de C1-TEN | −7,9 % | −1,1 % | +8,2 % | −0,3 % | −0,1 % |
| Correlación de C1-TEN con lo real | 0,984 | 0,969 | 0,932 | 0,960 | 0,974 |

### 9.2 · Esquema de validación

Cada origen se proyecta usando solo lo disponible antes de ese período.

```
202410: [████ historia ████][objetivo]
202420: [█████ historia █████][objetivo]
202620: [████████ historia ████████][objetivo]
```

| Métrica | Fórmula | Uso |
|---|---|---|
| WAPE | `Σ\|real − proyectado\| ÷ Σ real` | Error por celda |
| MASE | `WAPE modelo ÷ WAPE naive` | Compara contra el baseline |
| Sesgo | `Σ proyectado ÷ Σ real − 1` | Dirección del error |
| Cobertura | % de celdas con lo real entre P10 y P90 | Calidad de la banda |

### 9.3 · Largo plazo

Pseudo-backtest con bases de 2022 a 2024, usando la matrícula real de Ariadna. Mide el mejor caso del volumen; el error de Ariadna se agrega aparte (§6.3).

| | H+1 | H+2 | H+3 | H+4 |
|---|---:|---:|---:|---:|
| Pares de pregrado | 6 | 6 | 4 | 2 |
| MASE C1 | 1,009 | 1,001 | 0,995 | 0,993 |
| **MASE C1E** | 1,053 | **1,012** | **0,959** | **0,962** |
| Sesgo C1 | −0,8 % | −2,5 % | −5,0 % | −7,6 % |
| **Sesgo C1E** | +3,0 % | +2,7 % | −0,2 % | **−2,7 %** |

### 9.4 · Evolución de versiones

MASE medio de pregrado, con volumen real, en los dos granos (D14).

| Versión | Qué es | MASE medio | ¿Adoptado? |
|---|---|---:|:---:|
| H1 | Hábito de sala, estándar por materia | 1,428 | No |
| H2 | Hábito de sala, estándar real | 1,212 | No |
| G1 | Bootstrap por estrato, sin elasticidad | 1,151 | No |
| P1 | Perfil horario, con NRC reales | 1,126 | No |
| G1b | Bootstrap por estrato, con elasticidad β | 1,064 | No |
| N1 | Naive ponderado de 2 años | 1,033 | No |
| C2 | Naive + hábito de sala | 0,974 | Sí, descartado por C1 |
| **C1** ⭐ | **Naive + G1b** | **0,964** | **Sí** |
| *Naive* | *Mismo semestre del año anterior* | *1,000* | — |

Al pasar a volumen proyectado, la ganancia casi desaparece: C1-TEN promedia 1,011. El costo de proyectar el volumen es de unos +0,05 de MASE (D15). Lo que falla es qué materia crece o cae, no el total.

### 9.5 · Incertidumbre

| Criterio | C1-TEN (2027) | C1E-TEN (2028–2031) | Objetivo |
|---|---:|---:|---|
| Cobertura media de la banda | 75,2 % | 76,0 % | 80 % |
| Rango entre orígenes | 62,6 %–80,9 % | 61,6 %–82,6 % | 75 %–85 % |

| Cobertura de C1E con el ensanche k_h | H+2 | H+3 | H+4 |
|---|---:|---:|---:|
| Sin ensanche | 69,7 % | 64,3 % | 56,3 % |
| Con ensanche | 83,0 % | 82,8 % | 87,0 % |

> [!warning] ⚠️ La banda es algo optimista a 1 año
> Cubre 75 %, bajo el 80 % buscado, sobre todo en los orígenes con poca historia (202420 y 202520). Se aceptó porque sin calibrar cubría entre 3 % y 9 %. Mejorará a medida que entren orígenes nuevos.

### 9.6 · A qué nivel leer

| Nivel | Confianza | Uso recomendado |
|---|---|---|
| Total y por campus, tendencia por año | Alta | Decidir |
| Campus × franja horaria | Media | Priorizar |
| Celda exacta | Baja | Orientar; validar antes de actuar |
| Sala y asignatura en la programación | No es una predicción | Solo para ver el tipo de falta |

Tamaño de sala: el MASE por rango queda entre 0,98 y 1,03, sin mejorar la ubicación, pero el reparto entre rangos sí acierta. En 202620, proyectado contra real: 40 % y 40 % en 0-20, 31 % y 30 % en 21-40, 13 % y 16 % en 41-60, 16 % y 14 % en 60 o más.

---

## 10 · Anti-leakage 🔧

> [!danger] 🚨 Todo mira solo al pasado
> **Ningún parámetro de un origen usa información del período que se valida.** Eso incluye secciones, volumen, β, tolerancia, clasificación de salas y calibración de la banda.

| Elemento | Riesgo | Cómo se evita |
|---|---|---|
| Banda | Calibrar con el período objetivo | Solo orígenes anteriores del mismo nivel; los primeros usan el naive de años previos |
| Peso w | Elegirlo viendo el resultado | Se calibra con orígenes anteriores |
| Clasificación de salas | Usar las salas del propio período | Se recalcula por origen |
| Matrícula de Ariadna en el pseudo-backtest | Es real, no un pronóstico | Se declara: mide el mejor caso. El error de Ariadna se suma aparte |

---

## 11 · Reglas de negocio que implementa 🧭

| Regla | Enunciado | Dónde vive |
|---|---|---|
| **D12** | Euribia solo se usa a 1–2 semestres; hasta 2031 manda Ariadna | §4 |
| **D13** | La programación usa secciones físicas anónimas, no predice asignaturas | §8 |
| **D14** | El mapa combina naive y G1b | §5.2 |
| **D15** | 2027: tendencia en pregrado y Euribia en Advance | §4 |
| **D16** | Banda calibrada con errores pasados | §6.1 |
| **D17** | Ensanche por horizonte y escenarios de Ariadna ensanchados | §6.2, §6.3 |
| **D18** | Alerta por tamaño, anidada, con tolerancia y oferta efectiva | §7 |
| **D19** | 2028–2031 con naive escalado | §5.3 |
| **V1** | Semáforo 10 / 25 / 50 %; se informa el 25 % | §7.3 |

---

## 12 · Cómo demostrar un cálculo 🧭

Se trabaja con los parquet de `BBDD/`, ubicando las filas por su llave.

### 12.1 · Qué se demuestra con el entregable y qué requiere los insumos

| Factor | Columnas | ¿Se demuestra con el entregable? | Para reconstruirlo |
|---|---|---|---|
| Inscritos | `INSCRITOS_BASE`, `RAZON`, `INSCRITOS_PROY` | Sí | — |
| Número de secciones | `INSCRITOS_PROY`, `ESTANDAR`, `SECCIONES_PROY` | Sí | — |
| Ocupación puntual | `OCUPACION_PUNTUAL`, `ESCALA_NAIVE`, `W_NAIVE` | Sí con w = 1; parcial con w < 1 | Sorteo de G1b |
| P10, P50 y P90 | `OCUPACION_P*`, `BANDA_CUANTILES`, `BANDA_HORIZONTE` | Sí | — |
| Probabilidad | `PROB_SATURA*` | Parcial: es un conteo sobre simulaciones que no se guardan | Correr `Modelos.ipynb` |
| Clases sin sala | `DEFICIT`, `PESO_SEMANAS` | Sí | — |

### 12.2 · Procedimiento para cualquier celda

| Paso | Qué mirar | Cómo se verifica |
|---:|---|---|
| 1 | Ubicar la celda | Filtrar `OCUPACION_Y_DEFICIT` por período, escenario, campus, día, bloque y clase |
| 2 | Tasa de uso | `OCUPACION_P50 ÷ CAPACIDAD` debe dar `TASA_USO_P50` |
| 3 | Nivel | Comparar `PROB_SATURA_TAMANO` con 10, 25 y 50 % |
| 4 | Tamaño | Filtrar `OCUPACION_POR_RANGO` por la misma celda: la mayor `PROB_SATURA_ACUM` es `PROB_SATURA_TAMANO` |
| 5 | Sin sala | `Σ PESO_SEMANAS` con `DEFICIT = True` en la celda debe dar `DEFICIT_SALAS` |

### 12.3 · Demostración completa: Sede Sur, salas, martes 09:30, 2029

**Celda**: `PERIODO = 202910` · `ESCENARIO = base` · `C04` · `SALA` · `MARTES` · `BLOQUE = 3`. Es la que aparece como crítica en la simulación.

**Paso 1 · Volumen de un tipo de curso del campus**

Psicología, cátedra, en Sede Sur.

```
Razón 2027       = tendencia del campus = 38.715 ÷ 35.689     = 1,0848
Ariadna 2029/27  = MT405 en C04          = 808 ÷ 723           = 1,1176
Razón 2029       = 1,0848 × 1,1176                            = 1,2123
Inscritos 2029   = 2.680 × 1,2123                             = 3.249,0
```

**Paso 2 · Número de secciones**

Cátedras de Sede Sur: 22.954 inscritos ÷ estándar real de 41 = **560 secciones**, contra 458 en 2026.

**Paso 3 · Ocupación puntual**

En 2026 esa celda ocupó **37,05 salas** ([[DOCUMENTO_TECNICO_FUNCIONAL_PIPELINE_SOSTRATO]] §11.3). 2029 usa C1E con w = 1, así que es el naive escalado:

```
OCUPACION_PUNTUAL = 37,05 × 1,169 = 43,3 salas
```

**Paso 4 · Banda**

El punto cae en el tramo 20–50 salas, con q10 = −1,427, q50 = −0,229 y q90 = 1,698. En H+3, k_h = 1,443.

```
√(43,3 + 1) = 6,656

P50 = 43,30 + (−0,229) × 6,656                       = 41,77
P10 = 43,30 + (−0,229 + 1,443 × (−1,198)) × 6,656    = 30,26
P90 = 43,30 + (−0,229 + 1,443 × ( 1,927)) × 6,656    = 60,28
```

**Paso 5 · Alerta por tamaño**

| Rango desde | Demanda P50 | Espacios | Probabilidad |
|---|---:|---:|---:|
| 0-20 | 42,25 | 39 | **62 %** |
| 21-40 | 36,52 | 37 | 50 % |
| 41-60 | 21,35 | 28 | 10 % |
| 60 o más | 7,96 | 21 | 0 % |

`PROB_SATURA_TAMANO = 62 %` y `RANGO_CRITICO = 0-20`: es **crítica**, y faltan salas de cualquier tamaño.

**Paso 6 · Programación sintética de esa celda**

| Qué | Valor |
|---|---:|
| Casilleros | 52 |
| Con sala | 42, en 37 salas |
| Sin sala | 10: 6 piden 60 o más, 2 piden 41-60, 1 pide 21-40 y 1 pide 0-20 |
| `Σ PESO_SEMANAS` sin sala | 9,8 = `DEFICIT_SALAS` |

**Paso 7 · De la celda al total**

| Nivel | Cálculo | Valor |
|---|---|---:|
| Celda | ≥ 25 % | Cuenta 1 |
| Sede Sur, salas y laboratorios, 2029 | Celdas ≥ 25 % | 52 |
| Todos los campus, 2029 | Suma de campus | 179 |

**Paso 8 · Qué mueve el resultado**

| Escenario | Punto | P50 | Probabilidad |
|---|---:|---:|---:|
| Bajo | 37,9 | 36,5 | 40 % |
| **Base** | **43,3** | **41,8** | **62 %** |
| Alto | 48,5 | 46,9 | 78 % |

La celda queda en alerta incluso en el escenario bajo.

### 12.4 · Variantes

| Caso | Celda | P50 total | Probabilidad | Tamaño crítico | Lección |
|---|---|---:|---:|---|---|
| Faltan salas a secas | C04 · sala · martes 09:30 · 2029 | 41,8 de 39 | 62 % | Todos | La demanda supera al total |
| El total alcanza, falta tamaño | C04 · sala · miércoles 11:00 · 2029 | 35,7 de 39 | 38 % | 21-40 o más | 33,3 secciones piden 21 o más, y hay 37 salas |
| Falta solo lo grande | C01 · laboratorio · lunes 08:00 · 2031 | 44,3 de 85 | 62 % | 60 o más | Piden 2,3 laboratorios de 60 o más, y hay 2 |

> [!warning] ⚠️ Dos medianas para la misma celda
> `OCUPACION_P50` sale de la fórmula de la banda (41,77). `DEMANDA_ACUM_P50` es la mediana de las simulaciones (42,25), que en 2029 son 50. Son el mismo concepto medido de dos formas. En celdas en alerta difieren 1,4 salas en promedio y hasta 8,9.

### 12.5 · Preguntas frecuentes de cálculo

**¿Cómo verifico la tasa de uso?**
`OCUPACION_P50 ÷ CAPACIDAD`. En el ejemplo, 41,77 ÷ 39 = 1,071 (§12.3).

**¿Por qué una celda con 44 de 85 laboratorios está en alerta?**
Porque la alerta mira el tamaño. Campus 01 tiene 85 laboratorios, pero solo 2 de 60 o más (§12.4). Conviene validar esos casos con infraestructura: puede ser gestión de grupos y no falta de espacio.

**¿Por qué bajo, base y alto no siempre van en orden?**
Los totales sí. En 2 de 175 combinaciones de campus y período, el base queda fuera: Campus 06 2028-2 (0, 2, 0) y Campus 07 2028-2 (6, 10, 9). Cada escenario se simula por separado.

**¿Por qué 2027 tiene un rango más estrecho que 2028?**
Es una diferencia de definición, no de incertidumbre (§4).

**¿Por qué el informe dice 466 y la simulación 465 en 2031?**
La celda de diferencia es de un domingo, que las vistas no muestran (§2.2).

**¿Por qué Campus 02 tiene clases sin sala sin alertas en 2027?**
Mapa y programación miden cosas distintas (§8.2).

**¿Por qué crecen 30 % los inscritos y 22 % el mapa?**
Son períodos distintos: +30 % es desde 2026 y +24 % desde 2027. Desde 2027, el mapa crece 22 % porque las salas crecen menos que los inscritos (§5.1).

**¿Por qué la vista Salas muestra más ocupación que Semana?**
Salas cuenta toda sección asignada, aunque dure pocas semanas, por decisión de diseño del 2026-11-05. En Sede Sur, el ejemplo da 37 salas ocupadas y 10 sin sala, es decir 47 contra un P50 de 41,8. Ponderado por semanas serían 34,2 y 9,8.

**¿Puedo sumar los P90 para saber cuántas salas construir?**
No. La banda se lee celda por celda, y sumar P90 supondría que todas las celdas fallan a la vez (§1).

**¿Qué significa que no haya alerta en Campus 05?**
Que con la planta actual y este crecimiento no se proyecta falta en ninguna celda. No significa que no haya clases sin sala: en 2031 son 7,8 %.

**¿Por qué no se usa solo el modelo más nuevo?**
Porque a 1 año C1E pierde contra C1-TEN en 3 de 5 orígenes (§9.1).

---

## 13 · Especificación del entregable 🔧

| Archivo | Filas | Columnas | Peso | Consumidor |
|---|---:|---:|---:|---|
| `OCUPACION_Y_DEFICIT.parquet` | 147.000 | 23 | 1,8 MB | Informes y simulación |
| `OCUPACION_POR_RANGO.parquet` | 225.573 | 14 | 5,0 MB | Simulación |
| `PROGRAMACION_SINTETICA.parquet` | 471.521 | 22 | 3,5 MB | Simulación |
| `MAPA_PROYECTADO.parquet` | 147.000 | 17 | 1,4 MB | Paso intermedio |
| `VOLUMEN_PROYECTADO.parquet` | 31.830 | 12 | 0,5 MB | Paso intermedio |
| `SECCIONES_PROYECTADAS.parquet` | 2.130 | 10 | < 0,1 MB | Paso intermedio |
| `MODELO_METADATOS.json` | 1 corrida | — | — | Trazabilidad |

Las columnas están en [[DICCIONARIO_USO_FUNCIONAL_SOSTRATO]] §5.

---

## 14 · Parámetros y flags 🔧

| Parámetro | Valor vigente | Efecto |
|---|---|---|
| Semáforo | 10 / 25 / 50 % | Cambia todos los conteos |
| `w_naive` 2027 | UG 0,8 · AV 0,0 | Lo elige el banco |
| `w_naive` 2028–2031 | UG 1,0 · AV 1,0 | Lo elige el banco |
| `beta` | 0,82 (10) · 0,80 (20) · 0,69 (AV) | Velocidad a la que crecen los espacios |
| Tolerancia | Sala 1,00 · lab. 1,33 y 1,32 · AV 1,00 | Déficit y tamaño |
| `RAZON_MIN`, `RAZON_MAX` | 0,25 · 4,0 | Topes del crecimiento |
| `N_SIM` | 100 (2027) · 50 (2028–2031) | Precisión de la probabilidad |
| `SEMILLA` | 2049 | Reproducibilidad |

> [!warning] ⚠️ La probabilidad avanza a saltos
> Con 50 simulaciones, sube de 2 en 2 puntos. No conviene interpretar diferencias pequeñas: 62 % y 64 % son lo mismo a efectos prácticos.

---

## 15 · Controles, guards y validaciones 🔧🧭

### 15.1 · Durante la corrida

| Control | Condición | Resultado 2026-10-29 |
|---|---|---|
| Consistencia con el banco | MASE de C1 en 202620 dentro de ±0,02 | OK: 0,942 contra 0,944 |
| Rango 0-20 | Debe coincidir con `PROB_SATURA` | OK |
| Cuadratura del volumen | Base 2027 contra 2026 | 329.627 → 345.663 |

### 15.2 · Verificados sobre el entregable (2026-11-05)

| Control | Resultado |
|---|---:|
| Pantalla de la simulación contra parquet, en cifras de curva y lista de campus | 8.250 de 8.250 |
| Clases sin sala y sobrecupo, contra parquet | 170 de 170 |
| Celdas del mapa, 13 campos | 126.000 de 126.000 |
| `PROB_SATURA_TAMANO` = máximo de los rangos | 126.000 de 126.000 |
| P10 ≤ P50 ≤ P90 | Sin excepciones |
| Celdas duplicadas | 0 |

---

## 16 · Resultados de referencia 📊

### 16.1 · Totales (pregrado, sufijo 10, base)

| | 2027 | 2028 | 2029 | 2030 | 2031* |
|---|---:|---:|---:|---:|---:|
| **Celdas en alerta (≥ 25 %)** | **93** | **125** | **179** | **251** | **297** |
| Rango bajo–alto | 50–144 | 66–186 | 80–274 | 120–344 | 156–381 |
| Celdas en vigilancia o más (≥ 10 %) | 181 | 297 | 366 | 427 | 466 |
| Celdas críticas (≥ 50 %) | 17 | 33 | 58 | 94 | 136 |
| Clases sin sala | 5,3 % | 7,6 % | 10,7 % | 13,9 % | 17,4 % |
| Sobrecupo tolerado | 8,8 % | 11,9 % | 13,4 % | 14,5 % | 14,9 % |
| Centro del mapa | 26.419 | 28.183 | 29.459 | 30.790 | 32.172 |
| Secciones | 9.885 | 10.434 | 11.015 | 11.626 | 12.263 |

\* 2031 extrapolado. La base real de 2026 tiene 9.397 secciones.

### 16.2 · Por campus en 2031

| Campus | Salas | Laboratorios | Total | Sin sala | Primer año en alerta |
|---|---:|---:|---:|---:|---|
| C01 · Campus 01 | 46 | 47 | 93 | 18,3 % | 2027 (lab.) · 2028 (sala) |
| C04 · Sede Sur | 62 | 2 | 64 | 16,9 % | 2027 (sala) · 2031 (lab.) |
| C06 · Campus 06 | 32 | 18 | 50 | 8,6 % | 2027 |
| C03 · Sede Austral | 33 | 4 | 37 | 17,5 % | 2028 |
| C02 · Campus 02 | 32 | 0 | 32 | 23,6 % | 2029 (sala) |
| C07 · Campus 07 | 16 | 5 | 21 | 2,6 % | 2027 (sala) · 2030 (lab.) |
| C05 · Campus 05 | 0 | 0 | 0 | 7,8 % | Sin alerta |
| **Total** | **221** | **76** | **297** | **17,4 %** | |

### 16.3 · Por sufijo y tamaño

| Período | 2027 | 2028 | 2029 | 2030 | 2031 |
|---|---:|---:|---:|---:|---:|
| Alertas 2.º semestre | 67 | 87 | 125 | 190 | 237 |
| Sin sala 2.º semestre | 4,6 % | 6,8 % | 9,5 % | 12,5 % | 15,7 % |
| Parte del déficit que pide 60 o más (1.er semestre) | 62 % | 71 % | 68 % | 73 % | 73 % |

En Advance prácticamente no hay alertas (a lo más 2 celdas ≥ 10 % por período y ninguna ≥ 25 %) y las clases sin sala no pasan de 0,5 %.

En las 297 alertas de 2031, el tamaño crítico es la celda completa en 230, 21 o más en 5, 41 o más en 20 y 60 o más en 42.

---

## 17 · Volumetría y performance 🔧🧭

### 17.1 · Volumen

Ver §13. El insumo más pesado es `PLANTILLAS_NRC`, con 2.236.891 filas y 22,4 MB.

### 17.2 · Tiempo de corrida

No medido: los notebooks no guardan tiempos por celda. Conviene cronometrar la próxima corrida.

### 17.3 · Memoria

No medida en esta versión.

---

## 18 · Supuestos, limitaciones y riesgos ⚠️

| # | Supuesto, limitación o riesgo | Impacto | Estado |
|---:|---|---|---|
| 1 | **Ventaja marginal sobre el naive a 1 año** | MASE 0,97–1,15: lo firme es la tendencia | Aceptado; leer por campus y franja |
| 2 | **C1E empeora 0,011 en 2028** | Dentro del ruido de ±0,02 | Declarado; revisar con un origen más |
| 3 | **2030 con 2 pares y 2031 extrapolado** | 2031 se lee como tendencia | Repetir el banco cada semestre |
| 4 | **La banda cubre 75 %, bajo el 80 %** | Los rangos son algo optimistas | Aceptado el 2026-10-27; recalibrar |
| 5 | **Capacidad de la planta sin validar** | Base de la tolerancia y de la alerta | A validar (P-01) |
| 6 | **Laboratorios de 60 o más en C01** | 47 alertas de laboratorio en 2031 pueden ser gestión de grupos | A validar (P-02) |
| 7 | **Base AV 202625 con la inscripción abierta** | Volumen AV bajo | Repetir con el período cerrado |
| 8 | **Ariadna subestima el crecimiento** | −8,6 % a 3 años | Compensado; Ariadna no se toca |
| 9 | **Planta y forma de programar fijas** | No refleja obras ni cambios de horario | Fuera de alcance |
| 10 | **Programación de una sola realización** | Sala y asignatura exactas no son predicción | Decisión de diseño |
| 11 | **Salas y 3D sin ponderar por semanas** | C01, miércoles 09:30 de 2031: 185 ocupados y 44 sin sala; ponderado, 173 y 36,2 | Decisión del 2026-11-05 |
| 12 | **Postgrado fuera** | La ocupación real es mayor | Decisión de diseño (D3) |

> [!warning] ⚠️ Lo que este modelo no cubre
> No recomienda obras ni dice cuántas salas construir. No considera costos, ni postgrado, ni cambios de malla o de jornada. Tampoco distingue si una alerta se resuelve con infraestructura o moviendo horarios.

---

## 19 · Pendientes de negocio y de datos 🧭

| # | Pendiente | Tipo | Qué destraba |
|---|---|---|---|
| P-01 | Validar la capacidad de la planta con infraestructura (C01, C04, C06) | Datos | Alertas por tamaño |
| P-02 | Validar si los laboratorios de 60 o más de C01 se dividen en grupos | Negocio | 47 alertas de 2031 |
| P-03 | Validación del modelo final por Diego | Negocio | Cierre de esta versión |
| P-04 | Elegir entre «horas» y «bloques» en la simulación renovada | Negocio | Nombre del indicador principal |
| P-05 | Repetir el banco con cada período nuevo | Datos | Banda y H+4 |
| P-06 | Modelar escenarios de obras y de horarios | Diseño | Evaluar soluciones |

---

## 20 · Observaciones del levantamiento 🔎

> [!important] 🎯 Alcance
> Revisión de notebooks, parquet e informes al 2026-11-05. No se modificaron el modelo ni sus salidas.

| # | Hallazgo | Evidencia | Impacto | Sugerencia |
|---|---|---|---|---|
| O-01 | **El informe técnico dice 21 bloques por día** | Hay 20 valores de `BLOQUE` (0 a 19) | Bajo: texto | Corregir el informe |
| O-02 | **El título de la §5 de `Modelos.ipynb` dice «Mapa con C1»** | Desde 2028 es C1E | Bajo: orientación | Actualizar el título |
| O-03 | **Dos medianas para una misma celda** | Hasta 8,9 salas de diferencia (§12.4) | Medio: al comparar vistas | Definir una sola para el hover con filtro |
| O-04 | **Secciones repetidas sin sala** | 2031-1: 7.210 filas y 7.090 únicas (1,7 %) | Bajo: conteo de la vista Salas | Contar secciones únicas |
| O-05 | **El generador de la simulación da otra oferta en laboratorios con filtro de tamaño** | `datos_alertas.py`: C06 0 contra 1 activo, C01 5 contra 3 | Bajo: solo hover con filtro | Ya corregido en `renuevo_ui`; falta en el generador |

---

## 21 · Cómo re-ejecutar 🔧

**Requisitos**

1. Python de Anaconda: `AppData\Local\anaconda3`.
2. Salidas de `PIPELINES.ipynb` en `BBDD/`.
3. Entregables de Euribia y Ariadna en `Downloads`.

| Paso | Acción | Cuándo |
|---:|---|---|
| 1 | Ejecutar `VALIDACION_WALKFORWARD.ipynb` | Si cambió la base |
| 2 | Ejecutar `Modelos.ipynb` | Siempre |
| 3 | Revisar §15.1 | Siempre |
| 4 | Ejecutar `scripts_fase1/datos_alertas.py` y `construir_maquetas.py` | Para actualizar la simulación |
| 5 | Comparar con §16 | Siempre |

> [!warning] ⚠️ Al cambiar de año
> Hay que actualizar los períodos base, y las cifras dejarán de ser comparables con §16 porque cambia el origen de H.

---

## 22 · Documentos relacionados

| Documento | Qué aporta | Vigencia |
|---|---|---|
| [[DOCUMENTO_TECNICO_FUNCIONAL_PIPELINE_SOSTRATO]] | Cómo se prepara la base | Vigente |
| [[DICCIONARIO_USO_FUNCIONAL_SOSTRATO]] | Términos, columnas y lectura de resultados | Vigente |
| [[INFORME_EJECUTIVO_ALERTAS_2027_2031]] | Resultados para directivos | Vigente |
| [[INFORME_TECNICO_RESULTADOS_ALERTAS_2027_2031]] | Resultados y método | Vigente |
| [[SOSTRATO_IDEA_Y_ROADMAP]] | Decisiones D1 a D19 | Vigente |
| [[DIAGNOSTICO_EMPALME]] | Mediciones de cada decisión | Vigente |
| [[SOSTRATO_flujo_pipeline-modelo-detalle_2026-10-30.excalidraw]] | Diagrama de flujo detallado | Vigente |
| [[SOSTRATO_programacion-sintetica_explicacion_2026-10-30.excalidraw]] | Lámina sobre la programación sintética | Vigente |

---

## 23 · Consideraciones de Uso Funcional

- La **Dirección de Ingeniería de Datos no se responsabiliza** de entregar las reglas de negocio para los análisis a los que se aplique este entregable.
- El usuario que utilice de forma independiente este entregable es **responsable de evaluar la consistencia de los parámetros y supuestos** declarados en §14 y §18 en función de su objetivo particular.
- Ante cualquier duda que no esté resuelta en este documento, consultar a través del canal **Data Request** de la Dirección General de Control de Gestión y Análisis Institucional.
- Los resultados orientan decisiones de planificación. Antes de comprometer inversión, validar la capacidad y el uso real con infraestructura (§19).

---

## 24 · Historial de versiones

| Versión | Fecha | Artefacto documentado | Cambios |
|---|---|---|---|
| 1.0 | 2026-11-05 | Commit `93dd390`, corrida del 2026-10-29 | Versión inicial del documento. |

---

*Documento generado el 2026-11-05 a partir de la corrida del 2026-10-29 de `Modelos.ipynb` y `VALIDACION_WALKFORWARD.ipynb`, y de los parquet de `BBDD/`. Los resultados de §16, la demostración de §12 y los controles de §15.2 se recalcularon sobre esos parquet. Las cifras de los scorecards de §9.1, §9.3 y §9.4 provienen del banco y de `DIAGNOSTICO_EMPALME.md`.*

---

> **Dirección de Ingeniería de Datos — Universidad Ficticia**
> Responsable: Diego Evans Pérez Paz
