---
date: 2026-10-22
tags:
  - diagnostico
  - fase-0
  - data-product
  - cirilo
  - euribia
  - ariadna
  - empalme
status: draft
type: diagnostico
project: sostrato
owner: Dirección de Ingeniería de Datos
author: Diego Evans Pérez Paz
version: "0.1"
fecha_creacion: 2026-10-22
ultima_actualizacion: 2026-10-22
---

# Sóstrato el Arquitecto · Fase 0 — Diagnóstico de empalme

> **En una línea:** Euribia y Cirilo empalman bien (misma llave, mismos inscritos 1:1, ~86 % de las sesiones-hora cubiertas en los períodos comunes) y ya permiten un **backtest inmediato sobre 202620**. La primera prueba muestra que el punto débil no es la demanda (WAPE 0,31) sino las **secciones** (WAPE 0,59, +19 % sobre lo programado). Ariadna empalma por período y campus, pero **no existe hoy el puente carrera → asignatura**. Además, la **planta física solo clasifica el 38 % de las sesiones-hora** como espacio físico propio.

Ver la idea y el roadmap en [[SOSTRATO_IDEA_Y_ROADMAP]]. Este documento cierra la fase 0 del roadmap.

---

## 1. Insumos revisados

| Producto | Archivo | Ubicación | Forma | Grano |
|---|---|---|---|---|
| **Cirilo** | `PROG_DETALLADA_PARA_HEATMAP.parquet` (25-09-2026) | `Heat-Map/dash_app/BBDD/` | 2.626.239 × 39 | NRC × día × bloque × sala (una fila = una sesión-hora) |
| **Euribia** · histórico | `SERIE_COMPLETA_REAL_VS_PROYECTADO.csv` (31-08-2026) | `Downloads/Proyección Demanda Asiganturas BBDD/` | `;` y coma decimal | período × asignatura × componente × campus |
| **Euribia** · proyección | `PROYECCION_INSCRITOS_2026_2027.csv` (31-08-2026; la copia `_CONGELADA_v1` del 28-09 tiene el mismo tamaño) | ídem | 22.142 × 36 | ídem, 202620–202725 |
| **Ariadna** | `PROYECCION_MATRICULA_2026_2031_28092026.parquet` | `Downloads/MODELO_PROYECCCIÓN_SIMPLE/` | 14.864 × 18 | período × condición × carrera × sede × nivel |

> [!warning] Euribia y Ariadna viven fuera del repo
> Sus entregables están en `Downloads/`, igual que los CSV crudos de Cirilo. Para Sóstrato el Arquitecto conviene fijar desde ya una carpeta `BBDD/` propia (fuera del control de versiones) con copias congeladas de estos tres archivos.

---

## 2. Llaves de cruce

| Dimensión | Cirilo | Euribia | Ariadna | Empalme |
|---|---|---|---|---|
| **Período** | `PERIODO` (código Banner) | `PERIODO` | `periodo` (viene como texto: castear) | ✅ mismo código Banner en los tres |
| **Asignatura** | `MATERIA` ‖ `N_CURSO` (código original) | `ASIGNATURA_REGLA` / `CODIGO_PROGRAMABLE` (homologado) + `CODIGOS_ORIGEN` (originales, separados por `\|`) | — | ✅ con una salvedad: en los períodos históricos hay que **explotar `CODIGOS_ORIGEN`** para encontrar el código con que se programó |
| **Componente** | `COMPONENTE` | `COMPONENTE` | — | ✅ mismos códigos (TEO, LAB, GRU, SSA, ELG, TAL, SIM, OCS, AYU, NPR) |
| **Campus** | `CAMPUS` (NRC) y `CAMPUS_AUX` (edificio real) | `CAMPUS` | `sede` | ✅ mismos códigos; Ariadna trae además C08, C09, C12, C13 y C11, que Euribia no tiene |
| **Carrera** | — | — | `cod_carrera` | ❌ **no hay puente**: ver §5 |
| **Nivel** | — (se infiere del sufijo del período) | sin `TT 00` | `nivel_academico` | 🟡 por sufijo: ver §2.1 |

**Inscritos:** sobre 22.121 series de un solo código, el ratio inscritos Cirilo ÷ Euribia tiene **mediana 1,000** (p10–p90 = 1,000). Ambos productos cuentan lo mismo, así que **no hace falta reconciliar la demanda**.

### 2.1 El sufijo del período ordena los niveles

En Ariadna, el sufijo del período separa los niveles casi sin mezcla (suma de `n` 2010–2031):

| Sufijo | UG | AV | MG | PH |
|---|---|---|---|---|
| `10` | 748.402 | — | 5 | — |
| `20` | 17.715 | — | 1 | — |
| `05` / `15` / `25` | — | 149.909 | — | — |
| `00` | — | — | 37.933 | 2.014 |

En Cirilo, los sufijos `10`/`20` concentran el 85 % de las sesiones-hora; el `00` (postgrado) suma **331.263 sesiones-hora (12,6 %)**, que Euribia no proyecta. Además hay sufijos menores (11, 12, 16, 21, 22, 26, 30, 31…) que suman ~65 mil sesiones-hora y tampoco están en Euribia.

---

## 3. Cobertura Euribia → Cirilo (períodos con dato real en ambos, 202205–202615)

Se cruzó cada NRC de Cirilo contra las series reales de Euribia por período × asignatura (original u homologada) × componente × campus.

| Medida | Cobertura |
|---|---|
| NRC | **81,2 %** de 151.401 |
| Inscritos | **80,1 %** |
| Sesiones-hora | **85,9 %** |
| Sesiones-hora en espacio físico (sala, laboratorio, espacio UNIV) | **82,7 %** |

**Por componente** (sesiones-hora): SSA 95 %, LAB 88 %, GRU 86 %, TEO 83 %, OCS 82 %, ELG 53 %, TAL 42 %, SIM 29 %, AYU 11 %. TAL y SIM son componentes chicos, pero son justo los que usan espacios especiales (talleres y simulación).

**Por campus** (sesiones-hora): C02 89 %, C01 88 %, C03 87 %, C04 80 %, C05 75 %, C10 64 %, C07 64 %, C06 20 %, C09 0 %.

**Por período:** 92–96 % en los semestrales de 2022–2023, pero **75–79 % entre 202510 y 202610**. La cobertura cae en los últimos años. Hipótesis: más asignaturas nuevas sin historia (el cold start del 19–29 % que Euribia ya declara). **Hay que confirmarlo antes de la fase 2.**

---

## 4. Backtest inmediato: Euribia 202620 vs programación real 202620

Cirilo ya trae la programación real de **202620**, y Euribia lo proyecta con horizonte 1 desde 202520. Esto es la fase 4 del roadmap adelantada, con una salvedad: el parquet es del 25-09, con el período en curso.

| Medida | Resultado |
|---|---|
| Combinaciones asignatura × componente × campus | 3.134 en ambos · 1.426 solo en Euribia (proyectadas, no programadas) · 1.575 solo en Cirilo (programadas sin proyección) |
| Sesiones-hora reales cubiertas por una proyección | **62,9 %** |
| Inscritos reales cubiertos | **73,1 %** |
| WAPE inscritos (P50 vs real, combinaciones en ambos) | **0,307**: en línea con el 0,34 declarado por Euribia |
| WAPE secciones (`N_SECCIONES_P50` vs NRC reales) | **0,59** |
| Total de secciones | P50 13.412 vs **11.263 NRC reales** (+19 %) |

**Lectura:** la demanda llega bien, pero **la conversión a secciones es el eslabón débil**, como ya anticipaba Euribia (techo de 65,8 %). Para un mapa de calor, las secciones son las que ocupan salas, así que este es el riesgo número uno del proyecto. Además, un tercio de las sesiones-hora de 202620 no tiene proyección (asignaturas nuevas, postgrado, componentes fuera de alcance).

---

## 5. Ariadna → Euribia: falta el puente carrera → asignatura

- Ariadna proyecta por **carrera × sede × nivel × período**. Euribia proyecta por **asignatura × componente × campus × período**. Ninguno de los dos entregables trae una columna que los una.
- El reporte de inscripción que usa Euribia (`REPORTE_INSCRIPCIÓ_FULL_2015_2026_22072026.csv`) trae `PERIODO, RUT, NRC, MATERIA, CURSO, COMPONENTE, CAMPUS`, **sin carrera**.
- **Lo que hace falta:** una tabla RUT × período → carrera (programa vigente del estudiante en el período), para construir el **mix de carreras por asignatura**. Puede salir del maestro de pregrado (V6.1 con mención) o de la misma base de Ariadna. Es el primer insumo nuevo del proyecto.
- **Crecimiento que trae Ariadna** (UG, sufijo 10, escenario base): 38.718 estudiantes en 2026 → **50.889 en 2031 (+31 %)**, con banda de 46.040 a 55.719.

> [!note] R8 del roadmap queda resuelto
> Ariadna **ya viene por período académico** (10/20 UG, 05/15/25 AV, 00 MG/PH), no por año. No hace falta partir el año.

---

## 6. La planta física: el denominador

Cada fila de Cirilo es una sesión-hora. Así se reparten según la clasificación de su espacio:

| Clasificación | Sesiones-hora | % | ¿Entra al denominador del mapa? |
|---|---|---|---|
| EXTERNO | 923.393 | 35 % | No: campos clínicos. El 90 % es componente GRU |
| Sin Clasificación | 616.648 | 23 % | **A resolver** |
| SALA | 552.759 | 21 % | Sí |
| LABORATORIO | 328.292 | 13 % | Sí |
| ESPACIO UNIV | 105.617 | 4 % | Sí (a revisar qué incluye) |
| SALA VIRTUAL | 99.530 | 4 % | No |

*(Total: 2.626.239 sesiones-hora del parquet del 25-09. En espacio físico propio: 986.668, el 37,6 %.)*

Dentro de **«Sin Clasificación»**, 132.763 sesiones-hora no tienen edificio ni sala asignados. El resto son **salas reales que no aparecen en la planta física**: `C02Q BOX1`, `C02B VB207`, `C02B VB101`, `C02Q Q001`, `C02S VS201`, y los edificios ECS (`C02ECS`, `C03ECS`, `C01ECS`, `C04ECS`). Mientras no se completen, el mapa proyectado **subestima la oferta** en C02 sobre todo (262 mil sesiones-hora sin clasificar, el campus más afectado).

### 6.1 Foto de saturación actual (202610)

Para cada campus y clase de espacio: el máximo de salas usadas a la vez en un bloque, contra las salas distintas usadas en todo el período:

| Campus | Clase | Bloque pico | Salas usadas | Salas en uso en el período | Uso pico |
|---|---|---|---|---|---|
| C01 | SALA | miércoles, bloque 3 | 109 | 109 | **100 %** |
| C04 | SALA | lunes, bloque 4 | 37 | 37 | **100 %** |
| C06 | SALA | lunes, bloque 9 | 29 | 29 | **100 %** |
| C02 | SALA | lunes, bloque 9 | 65 | 66 | 98 % |
| C03 | SALA | lunes, bloque 3 | 61 | 62 | 98 % |
| C05 | SALA | martes, bloque 8 | 50 | 56 | 89 % |
| C04 | LABORATORIO | miércoles, bloque 12 | 25 | 29 | 86 % |
| C02 | LABORATORIO | martes, bloque 11 | 34 | 42 | 81 % |
| C01 | LABORATORIO | jueves, bloque 3 | 56 | 75 | 75 % |

**Lectura preliminar:** en los bloques punta de la mañana, **las salas ya están al límite hoy**. Con un +31 % de matrícula UG a 2031, la pregunta del proyecto no es *si* se satura sino **cuánta programación hay que mover a bloques valle o cuántas salas faltan**. El denominador usado aquí son las salas efectivamente programadas, no toda la planta física: en la fase 1 se reemplaza por el inventario de la planta.

---

## 7. Viabilidad del perfil horario (fase 1)

Series de Cirilo asignatura × componente × campus × sufijo según cuántos períodos tienen:

| Períodos con historia | Series |
|---|---|
| 1 | 12.437 (38 %) |
| 2 | 7.215 |
| 3 | 6.008 |
| 4 | 3.778 |
| 5 | 3.509 |

El 62 % de las series tiene al menos dos períodos para estimar su perfil horario. El 38 % restante necesita la cascada de respaldo (componente → materia → campus) prevista en el roadmap.

---

## 8. Cambios al roadmap y decisiones que se desprenden

| # | Qué cambia | Por qué |
|---|---|---|
| C1 | **El backtest pasa de la fase 4 a la fase 2**, y 202620 es el período de prueba | Ya existe la programación real y la proyección de Euribia del mismo período |
| C2 | ~~**Nueva tarea en la fase 1: modelo de secciones propio de Sóstrato el Arquitecto**~~ *Reemplazada el 24-10 por la regla de percentil de §10* (inscritos → NRC, calibrado contra los NRC reales de Cirilo) | Las secciones de Euribia tienen WAPE 0,59 y +19 % de sesgo |
| C3 | **Nueva tarea en la fase 0/1: completar la planta física** (salas de «Sin Clasificación» y los edificios ECS) | El denominador hoy cubre solo el 38 % de las sesiones-hora |
| C4 | **Nuevo insumo en la fase 5: tabla RUT × período → carrera** | Sin ella no hay puente Ariadna → Euribia |
| C5 | R8 (anual → semestral) se cierra | Ariadna ya viene por período |
| C6 | Investigar la caída de cobertura en 2025–2026 | Pasa del 92–96 % al 75–79 % |

**Propuestas que se le hicieron a Diego** (22-10; lo decidido está en §10):

- **D1 · grano:** se mantiene campus (`CAMPUS_AUX`) × día × bloque × clase de espacio × rango de capacidad. Los datos lo soportan.
- **D2 · secciones del escenario base:** usar **P50 de inscritos + un modelo propio de secciones** (C2), no el `N_SECCIONES_P50` de Euribia. *Reemplazada por la regla de percentil de §10.*
- **D3 · postgrado:** fuera de la v1, pero con su ocupación **real** sumada como carga fija (12,6 % de las sesiones-hora). *Reemplazada: el postgrado queda fuera, sin carga fija.*

---

## 9. Reproducibilidad

Los cálculos se hicieron con tres scripts de pandas sobre los archivos de §1, sin modificarlos. Los scripts quedaron en `Notebooks + Scripts/scripts_fase0/` (`esquemas.py`, `cruce.py`, `cruce2.py`; rutas absolutas a `Downloads/`) y se corren con `py <script>`. Las mediciones de §10 están en `Notebooks + Scripts/scripts_fase1/` (`seleccion_percentil.py`, `unidad_academica.py`, `correccion_sesgo.py`).

**Cálculos definitivos (24-10):** el empalme, la unidad académica (D7) y la regla de secciones (D2 + D8) pasaron a `Notebooks + Scripts/PIPELINES.ipynb`. El notebook escribe `PROG_HIST_NRC.parquet`, `UNIDAD_ACADEMICA.parquet` y `REGLA_SECCIONES.parquet` en `BBDD/`, que es local y está fuera de git. Su sección 5 revalida la regla contra las cifras de §10.4 y avisa si se alejan. Los scripts de esta carpeta quedan como registro de la exploración.

---

## 10. Decisiones del 24-10 y medición de D2

Diego respondió en `Respuestas  Sóstrato.md`:

| # | Decisión |
|---|---|
| D1 | Grano propuesto + eje por semestre calendario. La programación sintética debe analizarse por **facultad, campus, período académico, nivel y bloque**, para una vista *craft* de vanguardia |
| D2 | Las secciones de Euribia sirven si se usa **el percentil correcto**; por ejemplo, P75 en TEO para los períodos 10/20. Regla: la columna con mejor WAPE |
| D3 | **Solo pregrado y AV**. El postgrado queda fuera |

### 10.1 Qué columna gana por segmento

`N_SECCIONES_Pk` = `round(P50 / (tamaño de sección Pk × 1,10))` según el diccionario de Euribia. Un percentil más alto supone secciones más llenas y, por lo tanto, menos secciones. Se eligió por **tipo de período × componente**, con la historia de Euribia (filas REAL de `SERIE_COMPLETA` contra `N_SECCIONES_REALES`). `PROMEDIO` se descartó como candidata por dos razones:

1. **Viene vacía en la proyección.** `N_SECCIONES_PROMEDIO` = `round(P50 / [ESTANDAR_PROMEDIO × 1,10])`, y `ESTANDAR_PROMEDIO` es el tamaño de sección observado (Σ inscritos ÷ Σ secciones). En `PROYECCION_INSCRITOS_2026_2027.csv` solo 81 de 22.142 filas lo traen; el resto dice `ESTANDAR_PROM_FUENTE = sin_observacion`. Las secciones reales tampoco vienen (`N_SECCIONES_REALES` vacía en las 22.142). El diccionario de Euribia ya lo marca: «⚠️ Vacía en el entregable».
2. **Su ventaja en la historia es engañosa.** En el 89,4 % de las filas REAL, `ESTANDAR_PROMEDIO` = inscritos reales ÷ secciones reales **del mismo período** (`ESTANDAR_PROM_FUENTE = periodo_serie`). Es decir, se calcula con el resultado que pretende predecir. Por eso gana en LAB, OCS y GRU, pero esa ventaja no existiría al proyectar.

*Si se quisiera recuperarla, habría que recalcular `ESTANDAR_PROMEDIO` con los dos años anteriores a cada período (como dice el diccionario), sacándolo de los NRC reales de Cirilo, y volver a medirla fuera de muestra.*

| Segmento | Columna elegida |
|---|---|
| UG 10/20 · TEO, GRU, AYU | **P75** (confirma el ejemplo de Diego) |
| UG 10/20 · SSA | P50 |
| UG 10/20 · LAB, OCS, TAL, SIM, ELG | `TEORICAS_PROYECTADAS` |
| AV 05/15/25 · ELG, TEO, LAB | `TEORICAS_PROYECTADAS` |
| AV 05/15/25 · OCS, GRU / TAL | P75 / P90 |

### 10.2 Fuera de muestra: 202620 + 202625 contra los NRC reales de Cirilo

3.938 combinaciones asignatura × componente × campus con proyección y programación real.

| Criterio | WAPE total | Sesgo | WAPE UG | WAPE AV |
|---|---|---|---|---|
| P50 en todo | 0,578 | +21 % | 0,590 | 0,469 |
| P75 en todo | 0,394 | −25 % | 0,414 | 0,199 |
| **Regla por segmento** | **0,383** | **−24 %** | **0,405** | **0,169** |

**Lectura:**
- La regla baja el error en un tercio respecto de P50, como anticipó Diego.
- Queda un **sesgo de −24 %**: proyecta menos secciones que las abiertas, sobre todo en UG LAB (3.597 NRC reales) y GRU (2.496). Para el mapa eso significa **subestimar la ocupación**. Queda como D8 en el roadmap.
- GRU pesa poco en el mapa: el 90 % de sus sesiones-hora es EXTERNO (§6).

### 10.4 D8 · Corrección del sesgo (Diego, 24-10)

**Regla:** secciones = max(1, round(columna elegida en D2 × factor)). El factor es por tipo de período × componente y vale Σ `N_SECCIONES_REALES` ÷ Σ columna elegida, calibrado en la historia (filas REAL de `SERIE_COMPLETA`). Los segmentos con menos de 30 filas usan el factor de su tipo de período. Script: `Notebooks + Scripts/scripts_fase1/correccion_sesgo.py`.

**Factores** (los principales):

| Segmento | Columna (D2) | Factor |
|---|---|---|
| UG 10/20 · LAB | `TEORICAS_PROYECTADAS` | 1,597 |
| UG 10/20 · OCS | `TEORICAS_PROYECTADAS` | 1,401 |
| UG 10/20 · GRU | P75 | 1,394 |
| UG 10/20 · TEO | P75 | 1,238 |
| UG 10/20 · TAL | `TEORICAS_PROYECTADAS` | 1,219 |
| UG 10/20 · SSA | P50 | 1,079 |
| AV · ELG / TEO / LAB | `TEORICAS_PROYECTADAS` | 1,210 / 1,174 / 1,133 |

**Fuera de muestra (202620 + 202625, 3.938 combinaciones):**

| Criterio | WAPE por asignatura | Sesgo | WAPE período × campus | WAPE período × campus × componente |
|---|---|---|---|---|
| P50 en todo | 0,578 | +21 % | 0,276 | 0,326 |
| Regla D2 | 0,383 | −24 % | 0,241 | 0,253 |
| **Regla D2 + factor D8** | 0,431 | **−2,6 %** | **0,114** | **0,170** |

**Lectura:**
- El factor casi elimina el sesgo (UG −1,9 %, AV −8,8 %) y **reduce a la mitad el error agregado**, que es lo que ve el mapa (secciones sumadas por campus y bloque).
- A cambio, el WAPE por asignatura sube de 0,383 a 0,431. Casi todo viene de **UG LAB**: el factor histórico (1,597) sobrecorrige 202620 y lleva su sesgo de −31 % a +15 %.
- **Sensibilidad:** calibrar solo con 2024–2026 da prácticamente lo mismo (sesgo −1,6 %, WAPE 0,430). Los factores son estables en el tiempo.

### 10.3 Facultad (para D1)

Cirilo no trae facultad. Por la vía `MATERIA` = `cod_carrera` de Ariadna (197 carreras, cada una con una sola facultad), se asigna facultad al **78,7 %** de las sesiones-hora en espacio físico de UG y AV. El resto son asignaturas de departamentos de servicio: MT174 (37 mil), MT069 (30 mil), MT268, MT151, MT081, MT231, MT211 y otros.

**Decisión D7 (Diego, 24-10):** la facultad sale del match `MATERIA` = `cod_carrera`. Si no calza, la asignatura se carga **a su departamento**, que es la propia `MATERIA` descrita con STVSUBJ. Medido con `Notebooks + Scripts/scripts_fase1/unidad_academica.py`:

| Unidad | Sesiones-hora (espacio físico, UG + AV) |
|---|---|
| Facultad (`MATERIA` = carrera) | 78,7 % |
| Departamento (45 unidades, todas con descripción en STVSUBJ) | 21,3 % |
| Sin unidad | 0 % |

Los diez departamentos más grandes son MT174 (Química), MT069 (Biología), MT268 (Plan común Ingeniería), MT151 (Ciencias Morfológicas), MT081 (Ciencias Exactas), MT231 (Plan común Ing. Tecnológica Advance), MT211 (Plan común Educación), MT223 (Plan común Economía y Negocios Advance), MT230 (Formación sello institucional) y MT146 (Matemática y Estadística).

> [!note] Observación
> Algunos de estos «departamentos» son en realidad **planes comunes** de una facultad: MT268, MT231, MT211, MT210, MT223, MT218. Y MT414 (Trabajo Social) es una carrera que no calza con ningún código de Ariadna. Con la regla de D7 quedan como unidad propia. Si se prefiriera colgarlos de su facultad, bastaría una tabla de equivalencias de unas 7 filas.

---

## 11. Perfil horario (fase 1 · 24-10)

**Método aprobado por Diego:** (A) simulación por plantillas reales; (B) ventana con los últimos 2 años del mismo sufijo, el reciente con peso 2/3 y el anterior con 1/3; (C) peso por semanas activas. Está en `PIPELINES.ipynb`: §7 perfil y §8 validación. Desde el 25-10 la clase de cada fila sale de la clasificación de espacios de §12.

> [!note] Cifras de §11.2–11.3
> Las cifras siguientes son las del 24-10, cuando «físico» incluía ESPACIO UNIV. Con la definición del 25-10 (solo SALA y LABORATORIO, más la clase heredada de §12), la validación de §11.3 da: 1.399 celdas activas, WAPE por celda **0,190**, WAPE campus × día × bloque **0,133**, sesgo +5,2 %, correlación **0,970**, top-30 83 %, cobertura P10–P90 63,1 %.

### 11.1 Lo que condicionó el diseño

- **Tramos de fechas.** El 36 % de las combinaciones NRC × día × bloque tiene más de una fila. Casi siempre son tramos sucesivos del semestre en salas distintas: solo el 0,9 % se solapa en fechas. Cada tramo queda como una fila de la plantilla, con su sala y su peso, y no se suman como horas extra. El campo `REG_UNICO_LLAV2` de Cirilo **no sirve** para esto: su llave usa la hora de inicio de la sesión, no el bloque, así que marca una sola fila por sesión.
- **Semanas del período.** La mediana de duración de los NRC es muy estable: ~19 semanas en 10/20 y ~13 en AV. `PESO_SEMANAS` = semanas del tramo ÷ semanas del período.
- **OCS.** Euribia proyecta miles de secciones OCS, pero en Cirilo casi no tienen horario (203 NRC en cinco años). Quedan como «sin horario en la base» y no suman al mapa: 2,6–5,3 % de lo proyectado según el período.

### 11.2 Salidas en `BBDD/`

| Archivo | Contenido |
|---|---|
| `PLANTILLAS_NRC.parquet` | 2.221.247 filas · 170.322 NRC. Una fila por NRC × día × bloque × tramo, con clase, rango y `PESO_SEMANAS` |
| `PERFIL_HORARIO.parquet` | Proporción de cada serie por día × bloque × clase × rango (ventana de la próxima proyección) |
| `PERFIL_RESUMEN.parquet` | 18.593 series: horas semanales, semanas activas, proporción física, inestabilidad y si tiene perfil propio |

**Perfil típico por componente** (mediana de las series):

| Componente | Horas/semana | Semanas activas | En espacio físico |
|---|---|---|---|
| TEO | 4 | 100 % | 100 % |
| LAB | 2 | 100 % | 100 % |
| TAL | 2 | 100 % | 100 % |
| SIM | 4 | 39 % | 100 % |
| SSA | 6 | 6 % | 100 % |
| GRU | 5 | 31 % | 0 % (externo) |
| ELG | 2 | 33 % | 0 % (virtual) |

**Cascada** (lo que proyecta Euribia, según el nivel del perfil): con perfil propio de la serie, 10–40 %; de la misma serie en otro campus, 30–40 %; por materia, 17–27 %; por componente × campus, 1–28 % (sube en AV); sin horario en la base, 0–5 % (OCS). Solo el 32,8 % de las series tiene 3 o más NRC propios en la ventana.

### 11.3 Validación aislada en 202620

Los **NRC reales** de 202620 (16.774) se ubicaron con plantillas de 202520 + 202420, 100 simulaciones, y se compararon con el mapa real. La celda es campus del edificio × día × bloque × clase física.

| Métrica | Valor |
|---|---|
| Celdas activas | 2.095 |
| WAPE por celda (media simulada) | **0,234** |
| WAPE campus × día × bloque | **0,131** |
| Sesgo total | +3,5 % |
| Correlación mapa simulado vs real | **0,967** |
| Coincidencia en las 30 celdas más cargadas | **83 %** |
| Cobertura P10–P90 | 57,6 % |

**Lectura:**
- El perfil reproduce bien **la forma** del mapa: correlación de 0,967 y 25 de las 30 celdas más cargadas acertadas.
- La **banda P10–P90 es demasiado angosta**: cubre el 58 % de las celdas cuando debería cubrir cerca del 80 %. La simulación solo varía qué plantilla se sortea; no incluye cambios de política horaria ni la incertidumbre del número de secciones. Al juntarla con los escenarios de secciones se ensancha. Si sigue angosta, habrá que calibrarla.
- **El horario de cada asignatura cambia mucho de un año a otro**, aunque el mapa agregado se mantiene. La inestabilidad día × bloque (distancia de variación total, de 0 a 1) tiene mediana **0,78** y p75 1,0 entre las series con los dos años. Parte es ruido de series con pocos NRC. Confirma el riesgo R6 del roadmap: el mapa sirve para ver **dónde y cuándo se satura la institución**, no para anticipar el horario de una asignatura en particular.

---

## 12. Oferta de espacios (fase 1 · 25-10)

**Decisiones de Diego (25-10):**
- **A:** el mapa solo cuenta **SALA y LABORATORIO**. EXTERNO, ESPACIO UNIV y SALA VIRTUAL quedan fuera. Las salas usadas que no están en la planta heredan la clase de su edificio; si el edificio no está, se usa el componente.
- **B:** las sesiones sin sala quedan fuera del mapa y se informan aparte.
- **C:** la oferta base es el inventario efectivo (usado en los últimos 2 años); lo no usado es capacidad ociosa.

Está en `PIPELINES.ipynb`: §6 oferta y §9 control.

### 12.1 Lo que mostró la revisión (pregrado y AV, 2025–2026)

- **La planta clasifica bien.** Sus espacios físicos tienen capacidad en el 99,9 % y **todas las salas de clases ya se usan**. Lo que queda ocioso son laboratorios.
- **«Sin clasificación» era chico:** 9,8 % de las sesiones-hora. El 80 % de eso no tenía sala asignada (83 % GRU, clínico) y solo 80 salas reales faltaban en la planta, casi todas en edificios que sí están en ella. Los edificios ECS (C04ECS, C03ECS, C01ECS, C02ECS) son campos clínicos: heredan EXTERNO y quedan fuera.
- **En C02 entran** C02E E103–E108, E205 y E206, C02D D101 y D002, C02Q Q001 y Q242 (laboratorio), y C02O O91 y O92, C02B VB207 y VB101, C02S VS202 (sala). **Quedan fuera** C02ECS (externo) y C02G G201–G203, C02A A001 y C02C VARQT (espacio UNIV). C02CS Q200 no tiene edificio en la planta; por su componente (SSA) queda como laboratorio.
- **Horario de funcionamiento:** todos los campus usan hasta el bloque 19, salvo C07 (hasta el 16).

### 12.2 Salidas en `BBDD/`

| Archivo | Contenido |
|---|---|
| `OFERTA_ESPACIOS.parquet` | Un espacio por fila (planta + complemento): clase en el mapa, capacidad, rango, si está activo y de dónde salió la clase |
| `OFERTA_CELDA.parquet` | Campus × clase × rango: activos, ociosos, acumulados hacia arriba y bloque máximo |
| `DEMANDA_SIN_SALA.parquet` | Sesiones-hora sin sala, por campus y período (decisión B) |
| `COMPARTICION.parquet` | Salas ocupadas ÷ Σ NRC por campus y clase |

**Inventario en el mapa:** 697 espacios, 648 activos y 49 ociosos (casi todos laboratorios: 19 en C03, 15 en C04, 9 en C01). El complemento aporta 53 salas activas que no estaban en la planta: 27 en C05, 17 en C02, 3 en C01 y otras.

### 12.3 Control con la programación real

- **Cobertura:** el 100 % de las sesiones-hora en sala o laboratorio de 2025–2026 cae en un espacio del inventario.
- **Uso ≤ 100 %:** 0 de 6.949 celdas campus × día × bloque × clase lo superan, contando cada sala una vez por bloque.
- **Uso en el bloque pico de 202610 (salas):** C04 95 %, C06 97 %, C01 92 %, C03 87 %, C02 85 %, C05 59 %. Laboratorios: C01 60 %, C04 67 %, C02 58 %.

### 12.4 Hallazgo: salas compartidas

El **24 %** de las sesiones-hora en sala o laboratorio ocurre en una sala que usan **dos o más NRC en el mismo bloque**: secciones espejo o ligadas, por ejemplo dos NRC de MT2310078 en C03P P204. Contados por separado, inflan la ocupación: salas ocupadas ÷ Σ NRC = **0,895**. La primera versión del control daba 18 celdas «sobre 100 %» por esto. Corregido en §9 contando por sala; queda como **D11** cómo tratarlo en la proyección.

### 12.5 Listas cruzadas (D11, 25-10)

**Definición de Diego:** una LC es una misma cátedra con distintos códigos de asignatura. En la práctica es una sola clase: cuenta **una** sala y su tamaño es la **suma de inscritos**. El código es único por período + campus.

**Implementado** en `PIPELINES.ipynb` §2b. La LC sale de la programación detallada cruda (Cirilo la descarta), y se encontró el 98,9 % de los NRC. Cada NRC lleva:
- `COD_LC` = período-campus-LC;
- `N_NRC_LC`, contado con todos los niveles del crudo;
- `N_INSCRITOS_LC`, la suma de inscritos;
- `PESO_LC` = 1 ÷ `N_NRC_LC`.

Las plantillas llevan `PESO_OCUPACION` = `PESO_SEMANAS` × `PESO_LC`, y la validación de §8 compara contra el mapa real **contado por sala**.

**Resultado: la LC explica bien la compartición hasta 2024, pero no desde 2025.**

| Período | NRC con LC | NRC ÷ salas reales | Con peso LC ÷ salas reales |
|---|---|---|---|
| 202420 | 11,0 % | 1,159 | 1,086 |
| 202520 | 2,2 % | 1,145 | 1,133 |
| 202620 | 1,5 % | 1,144 | 1,136 |

En los casilleros donde dos o más NRC usan la misma sala al mismo tiempo, la parte explicada por una misma LC cae de 57,5 % (202420) a 18,0 % (202520) y 11,8 % (202610). En cambio, sigue siendo frecuente que compartan **nombre de asignatura** (38–50 %), **asignatura homologada** (37–47 %) o **docente** (23–37 %). Ejemplo de 202520: tres talleres distintos de Diseño, todos sección B50, en C05PA A5 el jueves en los bloques 8–10, sin LC.

**Validación de §8 contra salas reales (202620):** con peso LC, sesgo **+17,7 %**, WAPE campus × día × bloque 0,225 y correlación 0,941. Sin peso LC: +20,3 %, 0,245 y 0,941. La forma del mapa se mantiene, pero el nivel queda alto por la compartición que no está codificada como LC.

### 12.6 Factor residual de compartición (D11 cerrada, 25-10)

**Decisión de Diego:** sobre el peso LC se aplica un factor por **campus × clase** = salas reales ÷ Σ `PESO_OCUPACION`, calibrado en los últimos 2 años (`PIPELINES.ipynb` §7.1b → `FACTOR_COMPARTICION.parquet`). La ocupación del mapa usa `PESO_MAPA` = `PESO_OCUPACION` × factor.

**Factores** (calibrados con 202505 a 202625):

| Campus | Laboratorio | Sala |
|---|---|---|
| C02 | 0,657 | 0,977 |
| C01 | 0,666 | 0,982 |
| C04 | 0,829 | 0,994 |
| C05 | 0,935 | 0,992 |
| C03 | 0,950 | 0,975 |
| C07 | 0,998 | 0,979 |
| C06 | 1,000 | 0,989 |
| **Todas** | **0,741** | **0,984** |

**La compartición sin LC es casi toda de laboratorios**, sobre todo en C02 y C01. Es consistente con varios grupos de laboratorio que usan el mismo espacio a la vez. En salas, la corrección es menor al 3 %.

**Validación fuera de muestra (202620):** el factor se recalibró solo con 202425–202615, sin incluir 202620.

| Métrica | Sin corrección | Solo LC | **LC + factor** |
|---|---|---|---|
| Sesgo contra salas reales | +20,3 % | +17,7 % | **+4,7 %** |
| WAPE por celda | 0,300 | 0,286 | **0,192** |
| WAPE campus × día × bloque | 0,245 | 0,225 | **0,133** |
| Correlación | 0,941 | 0,941 | **0,972** |
| Cobertura P10–P90 | 57,4 % | 58,3 % | 62,4 % |
| Top-30 celdas | 83 % | 83 % | 83 % |

---

## 13. Banco de walk-forward (25-10)

Responde al informe de El Experto (H1–H3). Está en `Notebooks + Scripts/VALIDACION_WALKFORWARD.ipynb` → `BBDD/VALIDACION_RESULTADOS.parquet`.

**Diseño aprobado por Diego:**
- **Orígenes:** 202520, 202610 y 202620 deciden; los de AV son informativos.
- **Punta a punta:** completa en 202620 y 202625; con grilla conocida (optimista) en 202520 y 202610.
- **Grano informativo:** unidad × bloque.
- **Sin información del objetivo:** todo parámetro se recalcula solo con períodos anteriores. Eso incluye la clasificación de salas, otra fuga que tenía el pipeline: usaba las salas del propio período.

**Dos correcciones hechas al construirlo:**
1. **Código de serie de Euribia:** la historia (filas `REAL`) usa `ASIGNATURA_REGLA` y la proyección usa `CODIGO_PROGRAMABLE`, igual que el empalme. Con el código equivocado, en 202520 solo calzaba el 50 % de los NRC; con el correcto, el 78 %.
2. **OCS fuera de la punta a punta:** Euribia proyecta unas 3.000 secciones OCS por período, que en Cirilo casi no tienen horario. Si quedan, la cascada las amontona en las pocas plantillas OCS de la ventana: en 202520 la correlación caía a 0,44. **Es una falla del método vigente**, que queda dentro del trabajo de H2.

**MASE** (WAPE del modelo ÷ WAPE del naive; < 1 = gana):

| Modelo | Grano | 202520 | 202610 | 202620 | 202525 | 202615 | 202625 |
|---|---|---|---|---|---|---|---|
| N1 (naive ponderado) | celda | 1,018 | 1,045 | 1,036 | 1,015 | 0,984 | 1,118 |
| N1 | campus × día × bloque | 1,013 | 1,041 | 1,033 | 1,023 | 1,003 | 1,135 |
| **P1** (perfil, NRC reales) | celda | 1,131 | 1,275 | 1,200 | 1,213 | 1,016 | 0,887 |
| P1 | campus × día × bloque | 1,010 | 1,209 | 1,157 | 1,157 | 1,016 | 0,867 |
| P1 | unidad × bloque | 0,910 | 1,169 | 1,075 | 0,711 | 0,593 | 0,516 |
| **E1** (punta a punta actual) | celda | 1,362 | 1,294 | 1,315 | 1,386 | 1,376 | 1,054 |
| E1 | campus × día × bloque | 1,377 | 1,320 | 1,473 | 1,373 | 1,453 | 1,082 |
| **E1s** (sin la fuga de H3) | celda | 1,300 | 1,188 | 1,346 | 1,389 | 1,381 | 1,047 |
| E1s | campus × día × bloque | 1,279 | 1,181 | 1,431 | 1,382 | 1,458 | 1,076 |

Los AV (202525, 202615, 202625) son informativos. En 202520 y 202610, E1 y E1s usan la grilla conocida, así que son optimistas.

**Veredicto con la regla de adopción** (MASE < 1 en ≥ 2 de 3 orígenes de pregrado, en celda y en campus × día × bloque): **ningún modelo reemplaza al naive.**
- P1: media 1,16;
- E1: media 1,36;
- E1s: media 1,29;
- N1: media 1,03.

**Lectura:**
- **Confirma H1 sin fugas.** Aun conociendo los NRC reales, el perfil pierde contra «el mismo semestre del año anterior», con MASE de 1,01 a 1,28 en los granos para decidir.
- **Confirma H2.** En 202620, el 72,9 % de la verdad viene de NRC con proyección.
- **Quitar la fuga de H3 ayuda un poco:** E1s le gana a E1 en 4 de los 6 casos de decisión.
- **Un hallazgo a favor del perfil:** en el grano **unidad × bloque** le gana al naive en 4 de 6 orígenes (0,52–0,91). El naive copia bien la geografía del año anterior, pero reparte peor por unidad académica.
- **CRPS:** el CRPS relativo de P1 (0,104–0,153 por campus × día × bloque) es menor que el error del naive (0,121–0,194). No es una victoria limpia: el naive se evaluó como pronóstico de punto, sin banda. Para comparar justo, el naive también debe llevar una banda (con los errores del walk-forward), y eso queda pendiente con H5.
- **Las cifras del banco difieren levemente de las de El Experto** (P1 en 202620: 0,199 / 0,140 contra 0,190 / 0,133), porque el banco clasifica las salas sin información del período objetivo.

**Siguiente paso:** conectar al banco la reformulación **«naive + Δ»** (P2) y la punta a punta corregida (E2: `PROB_SE_DICTA`, bolsa de demanda no asignada y la falla de OCS), y medirlas con la misma regla.

### 13.1 G1 · Programación sintética por estrato (D13, 26-10)

Diego replanteó la programación sintética: no hace falta saber qué asignatura se dicta, sino que habrá una clase de tantos inscritos en tal horario y en tal sala (roadmap D13). Antes de eso, la rotación de códigos lo justificaba con datos: por asignatura, entre el 28 % y el 41 % de la ocupación física está en series «nuevas» de un año a otro; por materia o unidad × componente × campus, solo entre el 2 % y el 19 %.

**G1 aislado** usa el volumen real de inscritos por estrato como oráculo. MASE contra el naive:

| Grano | 202520 | 202610 | 202620 | 202525 | 202615 | 202625 |
|---|---|---|---|---|---|---|
| celda | 1,021 | **0,976** | 1,313 | **0,853** | **0,985** | 1,257 |
| campus × día × bloque | **0,984** | 1,063 | 1,261 | **0,790** | 1,001 | 1,295 |
| unidad × bloque | **0,796** | **0,898** | **0,968** | **0,620** | **0,840** | 1,117 |

- **Es el primer modelo que empata o le gana al naive:** en 202520 y 202610 queda en 0,98–1,06; en AV le gana en 202525 y empata en 202615; en el grano de unidad le gana en 5 de 6.
- **No pasa la regla de adopción** (gana 1 de 3 orígenes de pregrado en cada grano) por **202620**, con sesgo **+6,2 %**. Causa medida: los inscritos crecen más que la ocupación de salas. En 202620, inscritos +6,2 % y NRC +7,5 %, pero la ocupación física solo +2,4 % y las salas-bloque +2,5 %. En 202610: inscritos +8,3 % y salas +1,4 %. G1 escala 1:1 por inscritos y se pasa.
- **202625 no sirve como origen:** la foto del 25-09 lo toma con la inscripción abierta (inscritos −38 %, 9,6 % de los NRC con 0 inscritos). Sus cifras se descartan.
- **202620 también es una foto con el semestre en curso** (2,5 % de sesiones sin sala, contra 1,1 % en 202520). El resultado de ese origen es provisional hasta tener el período cerrado.
- **Déficit de salas tras la reasignación:** 2,3 % en 202520, 2,7 % en 202610 y 3,8 % en 202620. Es razonable para un método que todavía no optimiza la asignación.
- **Cobertura P10–P90:** 23–28 %. La banda de G1 es todavía más angosta, porque el volumen es fijo (oráculo) y solo varía qué secciones se sortean. Se calibra con H5.

### 13.2 G1b · Elasticidad salas/inscritos (26-10)

**Regla:** un estrato crece en salas como (inscritos objetivo ÷ inscritos base)^β. β se estima por mínimos cuadrados ponderados con los pares (P, P−100) de los 2 años anteriores al objetivo, del mismo nivel, **sin usar el período objetivo**.

**β estimado:** pregrado 0,98 (202520), 0,92 (202610) y 0,92 (202620); AV 0,71–0,74.

| Grano | 202520 | 202610 | 202620 | 202525 | 202615 |
|---|---|---|---|---|---|
| celda | 1,011 | **0,965** | 1,237 | **0,768** | **0,907** |
| campus × día × bloque | **0,976** | 1,052 | 1,163 | **0,718** | **0,899** |
| unidad × bloque | **0,788** | **0,886** | **0,891** | **0,500** | **0,706** |

- **Mejora a G1 en todos los orígenes:** media 1,068 contra 1,103 en los granos para decidir. En 202620 el sesgo baja de +6,2 % a +4,4 %.
- **Sigue sin pasar la regla de adopción** (1 de 3 orígenes de pregrado por grano). 202620 continúa perdiendo (1,16–1,24).
- **Dentro de un estrato, la elasticidad en pregrado es casi 1.** El desfase agregado de 202620 (inscritos +6,2 %, salas +2,5 %) viene de la **composición**: el crecimiento cae en estratos que usan pocas salas. No es que las clases se llenen más dentro de cada estrato.
- **En AV, G1b le gana al naive en los dos orígenes válidos y en los tres granos.**
- **Pendiente:** 202620 es una foto del 25-09 con el semestre en curso. Antes de seguir afinando conviene refrescarla desde Athena (query `QUERY_PROGRAMACION_DETALLADA_V2`, DL nuevo) y sumar orígenes al banco.

### 13.3 Más orígenes y datos frescos (26-10)

**Cambios en los insumos:**
- **Datos frescos:** 202620 y 202625 se re-extrajeron de Athena (query V2, DL nuevo) y se convirtieron con las reglas de Cirilo en `PIPELINES.ipynb` §0b. La conversión reproduce a Cirilo en 202610: −0,13 % de filas y 99,6 % de llaves en común. La LC queda completa (100 % de los NRC encontrados).
  - La extracción cruda traía +25 % de NRC, pero casi todos sin horario. Tras las reglas de Cirilo, 202620 + 202625 pasan de 18.921 a 19.051 NRC.
  - Las referencias de regresión de §5 se actualizaron: 3.952 combinaciones, sesgo −0,023, WAPE 0,112 y 0,173.
- **Más orígenes:** el banco sumó 202410 y 202420 (deciden) y 202415 y 202425 (AV). La regla pasa a ser por **mayoría de los 5 orígenes de pregrado**.

**MASE contra el naive, granos para decidir (celda / campus × día × bloque), pregrado:**

| Modelo | 202410 | 202420 | 202520 | 202610 | 202620 | Media |
|---|---|---|---|---|---|---|
| N1 | 1,02 / 1,10 | 1,01 / 1,02 | 1,02 / 1,01 | 1,05 / 1,04 | 1,04 / 1,04 | 1,03 |
| P1 | 1,04 / 0,98 | 1,16 / 1,17 | 1,13 / 1,01 | 1,28 / 1,21 | 1,16 / 1,12 | 1,13 |
| G1 | 1,27 / 1,35 | 1,14 / 0,99 | 1,02 / 0,98 | 0,98 / 1,06 | 1,31 / 1,25 | 1,14 |
| G1b | 1,27 / 1,34 | 1,18 / 1,04 | 1,01 / 0,98 | 0,97 / 1,05 | 1,24 / 1,16 | 1,13 |
| E1s | 0,96 / 0,97 | 1,25 / 1,24 | 1,30 / 1,28 | 1,19 / 1,18 | 1,34 / 1,43 | 1,21 |

**Veredicto:** **ningún modelo pasa la regla.** El naive (el mapa real del mismo semestre del año anterior) sigue siendo el mejor predictor del mapa a nivel de campus y celda.

**Lectura:**
- **202620 casi no cambia con los datos frescos** (naive 0,122; G1b 0,141). La foto del 25-09 no era la causa de que perdiera.
- **El mapa de salas es muy persistente.** De un año a otro las salas-bloque se mueven pocos puntos, aunque inscritos y NRC cambien bastante y en distinta dirección por estrato. Cualquier modelo que traslade el cambio de volumen a salas agrega más ruido que señal en ese grano.
- **Donde los modelos sí aportan:** en el grano **unidad × bloque** (G1b le gana al naive en 7 de 10 orígenes) y en **AV** (G1b le gana en 4 de 5). El naive copia bien la geografía, pero reparte peor entre unidades.
- 202625 mejora con los datos frescos (G1b de 1,12 a 1,06), pero sigue con muchos NRC sin inscritos (9,8 %): la inscripción de AV podría no estar cerrada.

### 13.4 C1 · Combinación naive + G1b: primer modelo adoptado (26-10)

**Regla:** mapa = w · N0 + (1 − w) · G1b. w (de 0 a 1, en pasos de 0,1) minimiza el WAPE medio de los dos granos para decidir, usando **solo los orígenes anteriores del mismo nivel**. En el primer origen de cada nivel (202410, 202415) no hay con qué calibrar, w = 1 y C1 es igual al naive.

**w elegido:** pregrado 1,0 → 0,7 (desde 202520, estable); AV 0,4 → 0,3–0,4. En pregrado el naive pesa 70 % y en AV pesa menos, porque ahí G1b gana solo.

**MASE contra el naive:**

| Grano | 202410 | 202420 | 202520 | 202610 | 202620 | 202425 | 202525 | 202615 | 202625 |
|---|---|---|---|---|---|---|---|---|---|
| celda | 1 (sin calibrar) | 1 (w = 1) | **0,959** | **0,949** | **0,942** | **0,934** | **0,743** | **0,814** | **0,893** |
| campus × día × bloque | 1 | 1 | **0,952** | **0,976** | **0,882** | **0,909** | **0,695** | **0,759** | **0,824** |
| unidad × bloque | 1 | 1 | **0,836** | **0,909** | **0,797** | **0,624** | **0,554** | **0,718** | **0,767** |

En 202420, w quedó en 1 con un solo origen previo, así que no pudo ganar.

**Veredicto: C1 pasa la regla de adopción.** Gana en 3 de 5 orígenes de pregrado en los dos granos para decidir, que son todos los orígenes donde se pudo calibrar. MASE medio 0,966.
- Detalle en 202620 (campus × día × bloque): WAPE 0,107 contra 0,122 del naive, sesgo −0,7 %, correlación 0,989, top-30 87 %.
- La mejora es **modesta pero consistente** en pregrado (2–12 %) y **grande en AV y por unidad** (16–45 %).

> [!note] Corrección del conteo
> La primera lectura contaba como «gana» los MASE iguales a 1 por redondeo (los orígenes con w = 1). El banco ahora exige MASE < 1 − 10⁻⁹.

**Pendientes de C1:**
- **La banda no sirve todavía:** cobertura P10–P90 de 1–23 %, porque la parte del naive no tiene incertidumbre. Se calibra con H5, usando los errores del walk-forward.
- **El volumen es oráculo:** C1 se probó con los inscritos reales por estrato. Falta la versión con volumen proyectado (Euribia en el corto plazo; Ariadna en el largo).
- **Llevarlo a `Modelos.ipynb`** como paso definitivo.

### 13.5 H1 · Programación sintética por hábito de sala (26-10)

**Idea de Diego:** si una sala tuvo una cátedra TEO de 8:00 a 9:30 durante varios años, lo más probable es que la siga teniendo. Así se construye la programación sintética desde los hábitos de sala, y la demanda (Ariadna) y el estándar de sección (Euribia) deciden cuántas secciones hay.

**Diseño:**
- **Tipo de sección** = campus × materia × componente.
- **Patrones habituales:** sala × (día, bloque), con su fuerza en los años anteriores del mismo sufijo (pesos 1 · 0,75 · 0,5 · 0,25).
- **Secciones necesarias** = inscritos ÷ estándar. El estándar es el percentil del tamaño de sección por componente del homólogo anterior, elegido con orígenes previos.
- **Asignación:** se llenan los patrones de más fuerte a más débil. Está en `VALIDACION_WALKFORWARD.ipynb` §4c.

**Resultados en 202620** (MASE contra el naive, campus × día × bloque):

| Variante | Cómo se cuentan las secciones | Error en secciones por tipo | MASE celda | MASE campus × día × bloque |
|---|---|---|---|---|
| H1 | inscritos reales ÷ estándar | 41 % | 1,627 | 1,334 |
| H1A | inscritos × crecimiento Ariadna ÷ estándar | — | 1,853 | 1,745 |
| Hábito + **N real** (oráculo) | las secciones físicas reales | 0 % | 1,101 | **0,936** |
| Hábito + N persistencia × crecimiento | secciones del año anterior × crecimiento de inscritos | 17–30 % | 1,15–1,33 | 1,14–1,25 |
| Hábito + N del año anterior | las mismas secciones del año anterior | — | 1,01–1,04 | 1,00–1,05 |

Las dos últimas filas cubren los orígenes 202520, 202610 y 202620.

**Lectura:**
- **La asignación por hábito es sólida.** Con el número correcto de secciones le gana al naive por campus (0,936). Con las mismas secciones del año anterior queda igual al naive. Es decir, el hábito de varios años no agrega por sí solo sobre «copiar el año anterior», pero **sí aprovecha bien la información de cuántas secciones habrá**.
- **El cuello de botella es contar bien las secciones por tipo.** El estándar por percentil se equivoca en 33–42 % (SIM: 852 estimadas contra 144 reales; TEO: 2.180 contra 3.036). Escalar las secciones del año anterior por el crecimiento de inscritos baja el error a 17–30 %, pero infla las salas (sesgo +5–7 %), el mismo fenómeno de G1.
- **Conclusión:** el valor está en **proyectar el número de secciones por tipo con más precisión que copiar el año anterior**. Hoy ninguna fuente lo logra: ni el estándar, ni Euribia (D2 + D8), ni el escalamiento por inscritos.
- **C1 sigue siendo el modelo adoptado.** H1 queda como el generador explícito de la programación sintética (sala, día, bloque, tipo), que puede alimentarse con el número de secciones que mejor se proyecte.

### 13.6 Estándar real de programación por sede × componente (26-10)

**Precisión de Diego:** el estándar teórico (TEO = 80, LAB = 30…) no es como programan los campus. El **estándar real** es el percentil del tamaño de sección que reproduce el número de secciones que se programan de verdad. Usar ese dato real de años anteriores **no es fuga** (la fuga de H3 era que Euribia calculaba el percentil con el mismo período que proyectaba). Con los estudiantes por sede se obtiene el número de secciones por componente y se insertan en la programación sintética.

**Prueba** (con secciones físicas):
- **Estándar(sede, componente)** = el percentil Pk del tamaño de sección del año anterior cuyo número implícito de secciones (inscritos ÷ Pk) reproduce las secciones reales de ese año.
- **Secciones del objetivo** = inscritos reales del objetivo ÷ estándar.
- **Reparto** por hábito de sala dentro de cada sede × componente.

| Origen | Error en N (sede × componente) | Sesgo de N | MASE celda | MASE campus × día × bloque | Con N real (oráculo): celda / campus |
|---|---|---|---|---|---|
| 202520 | 23 % | +15,6 % | 1,21 | 1,24 | 0,95 / **0,83** |
| 202610 | 12 % | +1,4 % | 1,04 | 1,08 | 1,17 / 1,19 |
| 202620 | 19 % | +11,1 % | 1,28 | 1,12 | 1,17 / 0,98 |

**Lectura:**
- **Los percentiles elegidos rondan P45–P65** en TEO y LAB, no P75. Con secciones físicas (las LC y las salas compartidas ya unidas) el estándar real queda cerca de la mediana. El P75 que se ajusta en Euribia está medido sobre NRC sueltos, donde las listas cruzadas dejan secciones más chicas.
- **El estándar del año anterior proyecta demasiadas secciones (+11 % a +16 %)** cuando los inscritos crecen. Es el mismo fenómeno de G1: **las secciones se llenan más de un año a otro**, así que el tamaño real sube y el estándar del año pasado queda corto.
- **Repartir por hábito dentro de sede × componente pierde información de materia:** aun con el N real por sede × componente, el mapa solo le gana al naive en 202520 (0,83). Con N real por materia daba 0,936 en 202620 (§13.5).
- **Siguiente ajuste natural:** un **estándar con tendencia** (el tamaño de sección crece año a año), calibrado con el crecimiento del tamaño en los años anteriores, y repartir las secciones de sede × componente entre materias según el peso de cada una en los inscritos.

### 13.7 Corrección: unión transitiva de secciones físicas (26-10)

> [!warning] Afecta las cifras de §13.1 a §13.6
> La **sección física** (D13) unía los NRC que comparten sala en el mismo bloque. Con «cualquier casillero compartido», y después con «≥ 80 % de los casilleros de la más chica», la unión era **transitiva**. Una sección de un solo bloque servía de puente, y un laboratorio o auditorio muy usado encadenaba cientos de secciones en una sola, con hasta 1.890 casilleros semanales. Se detectó al probar el reparto por materia: 202610 daba MASE 7,7.
>
> **Regla corregida:** se unen solo las LC codificadas y las secciones con **horario prácticamente idéntico**, es decir, que comparten ≥ 80 % de los casilleros **de la más grande**. Ahora la sección más pesada tiene 39 casilleros (p99 = 9).
>
> Las cifras de §13.1–13.6 se calcularon con la regla anterior. Las vigentes son las de esta sección.

**Banco recalculado** (MASE contra el naive, celda / campus × día × bloque):

| Modelo | 202410 | 202420 | 202520 | 202610 | 202620 | Media (5 de pregrado) | Adopta |
|---|---|---|---|---|---|---|---|
| **C1** | 1,00 / 1,00 | **0,99 / 0,97** | **0,99 / 0,98** | **0,96 / 0,95** | **0,94 / 0,87** | **0,964** | **Sí (4 de 5)** |
| G1b | 1,10 / 1,15 | 1,15 / 1,06 | 1,14 / 1,08 | 1,01 / 0,96 | 1,06 / 0,94 | 1,064 | No |
| G1 | 1,15 / 1,22 | 1,24 / 1,15 | 1,23 / 1,20 | 1,06 / 1,06 | 1,14 / 1,06 | 1,151 | No |
| N1 | 1,02 / 1,10 | 1,01 / 1,02 | 1,02 / 1,01 | 1,05 / 1,04 | 1,04 / 1,04 | 1,033 | No |
| P1 | 1,04 / 0,98 | 1,16 / 1,17 | 1,13 / 1,01 | 1,28 / 1,21 | 1,16 / 1,12 | 1,126 | No |
| H1 (estándar por materia, §13.5) | 1,30 / 1,41 | 1,46 / 1,54 | 1,24 / 1,17 | 1,53 / 1,49 | 1,65 / 1,49 | 1,428 | No |

- **C1 se mantiene y mejora:** ahora gana en 4 de 5 orígenes de pregrado (también 202420). w en pregrado: 0,8 → 0,7. En AV: 0,71–0,94.
- **G1b mejora** (media 1,10 → 1,06), pero solo no alcanza.

**Estándar real por sede × componente (§13.6) con la regla corregida:**

| Origen | Error en N (sede × componente) | Sesgo de N | Hábito + estándar real: celda / campus | Hábito + N real por materia: celda / campus |
|---|---|---|---|---|
| 202520 | 14 % | +9,9 % | 1,22 / 1,17 | 1,05 / 0,98 |
| 202610 | **8 %** | −0,4 % | 1,19 / 1,16 | 1,22 / 1,19 |
| 202620 | **7 %** | −1,7 % | 1,31 / 1,04 | 1,18 / 0,95 |

- **El estándar real de Diego cuenta muy bien las secciones:** 7–14 % de error por sede × componente. Los percentiles elegidos rondan P45–P50 en C01 (TEO P45, LAB P50).
- **El límite ahora es la ubicación por hábito:** aun con el N real por materia, queda cerca del naive por campus (0,95–1,19) y peor por celda. El naive tiene la ventaja de copiar las salas exactas del año anterior.

### 13.8 C2 · Naive + hábito con el estándar real, comparado con C1 (26-10)

**H2** (banco §4d):
- **Estándar real** por sede × componente: el percentil que reproduce las secciones programadas en el homólogo anterior.
- **Secciones** = inscritos ÷ estándar, repartidas entre materias según sus inscritos.
- **Ubicación** por hábito de sala.
- **Error en N por sede × componente:** 7–20 % según el origen (202620: 6,9 %; 202610: 8,3 %).

**C2** = w · N0 + (1 − w) · H2, con w calibrado igual que C1.

**MASE contra el naive (celda / campus × día × bloque):**

| Origen | C1 | C2 | H2 solo |
|---|---|---|---|
| 202420 | 0,99 / 0,97 | 1,00 / **0,96** | 1,38 / 1,33 |
| 202520 | 0,99 / 0,98 | 0,99 / 0,98 | 1,22 / 1,17 |
| 202610 | **0,96** / 0,95 | 0,98 / **0,94** | 1,18 / 1,15 |
| 202620 | **0,94 / 0,87** | 0,99 / 0,90 | 1,31 / 1,03 |
| AV (202425 → 202625) | **0,71–0,94** | 0,82–0,98 | 1,12–1,58 |
| Media de pregrado (5 orígenes, 2 granos) | **0,964** | 0,974 | 1,212 |
| ¿Adopta? | Sí (4 de 5) | Sí (4 de 5) | No |

w elegido: C1 → 0,7–0,8 en pregrado y 0,3–0,4 en AV; C2 → 0,8 en pregrado y 0,7–0,8 en AV.

**Lectura:**
- **Los dos pasan la regla y están muy parejos en pregrado.** C2 gana por poco en 202420 y 202610 (por campus); C1 gana en 202620 y por celda.
- **C1 es claramente mejor en AV y en el grano de unidad:** G1b aporta más que H2 cuando el año anterior es menos confiable.
- **H2 solo es peor que G1b solo** (1,21 contra 1,06). La ubicación por hábito multianual no supera el remuestreo del año anterior, aunque el número de secciones sea bueno.
- **Lo que H2 sí aporta:** una programación sintética **explícita** («cátedra TEO de unos 45 inscritos, martes 8:00, en tal sala») con un número de secciones por sede × componente bien estimado (7–20 % de error). G1b también la genera, pero por remuestreo.


## 14. Modelos.ipynb · primera proyección (26-10)

Decisiones de Diego del 26-10:
- **Mapa:** C1.
- **Número de secciones de la programación explícita:** el estándar real (H2).
- **Programación explícita:** las secciones físicas del último período real se remuestrean hasta ese número y luego se reasignan las salas.
- **Horizonte:** 2027 con Euribia y 2028–2031 con Ariadna, marcado **NO VALIDADO**.
- **Funciones definitivas:** viven en `Modelos.ipynb`; el banco conserva su copia validada.

**Base por sufijo:** 202610, 202620, 202605, 202615 y 202625. Esta última es una extracción con la inscripción todavía abierta.

**Volumen.** Es una razón de crecimiento por campus × materia × componente que se aplica a los inscritos de la base. Dos correcciones surgieron en la primera corrida:

1. **Euribia: no se usa `P50_ESPERADO`** (P50 × `PROB_SE_DICTA`).
   - Descuenta los cursos que podrían cerrarse sin sumar los cursos nuevos que Euribia no ve.
   - En el agregado encoge el volumen de 303.848 inscritos (202620) a 271.486 y luego a 249.819 (202720): −18 % en dos pasos, contra +5 % anual en la historia.
   - Se usa su crecimiento interno: Σ Pk ÷ Σ `ins_lag_1y` por tipo. Euribia cubre el 87–100 % de los inscritos base.
2. **Ariadna: razón anual, no semestral.**
   - La matrícula se registra casi entera en el período 10 (202620 tiene 739 personas contra 38.718 en 202610), así que por semestre los sufijos 20 y 15 eran ruido (+31 % y +36 % en 2028).
   - Razón = matrícula anual del año T ÷ matrícula anual 2027, por carrera × sede; los departamentos usan la de su sede. Se **encadena** a la razón base de Euribia 2027, sin salto entre 2027 y 2028.
   - El 59–70 % de los tipos encuentra su carrera en Ariadna.

| Período | Base real | Bajo | Base | Alto |
|---|---:|---:|---:|---:|
| 202710 | 329.627 | 233.929 | 324.742 | 437.028 |
| 202720 | 309.211 | 215.039 | 307.203 | 424.060 |
| 202810 | 329.627 | 319.534 | 342.875 | 366.231 |
| 203110 | 329.627 | 360.057 | 402.941 | 445.927 |

La banda de 2027 suma P10 y P90 por tipo, así que equivale a que todos los cursos caigan o suban a la vez: es más extrema que la de Ariadna y que un cuantil del total.

**Secciones (estándar real) y programación sintética, escenario base:**

| Período | Secciones | Déficit de casilleros |
|---|---:|---:|
| 202710 | 9.265 | 2,9 % |
| 202720 | 8.856 | 2,5 % |
| 202810 | 9.787 | 3,2 % |
| 203110 | 11.500 | 8,4 % |
| 203120 | 10.991 | 6,8 % |

- En AV el déficit es ≈ 0 %.
- La base real es de 9.397 secciones físicas (202610) y 8.954 (202620).

**Mapa C1:**
- w = 0,7 (UG) y 0,4 (AV), tomado del origen más reciente del banco.
- β = 0,82 (10), 0,80 (20) y 0,69 (AV).
- Tasa de uso pico P50 en 2027: 87–97 % de las salas en el período 10 de los campus grandes (C01, C04, C06, C03).

**Control de consistencia:** C1 en 202620 con las funciones de `Modelos.ipynb` y el volumen real da MASE 0,942 en celda, contra 0,944 del banco (**OK**, tolerancia ±0,02).

**Salidas en `BBDD/`:** `VOLUMEN_PROYECTADO`, `SECCIONES_PROYECTADAS`, `MAPA_PROYECTADO`, `PROGRAMACION_SINTETICA` y `OCUPACION_Y_DEFICIT` (`.parquet`), más `MODELO_METADATOS.json`.

**Pendiente:**
- validar en el banco el volumen proyectado (hoy validado solo con el volumen real como oráculo);
- calibrar la banda (H5);
- pseudo-backtest de largo plazo;
- rango de capacidad.


## 15. Volumen proyectado en el banco: Euribia, persistencia y tendencia (26-10)

**Pregunta.** C1 se adoptó (D14) creciendo hasta los inscritos **reales** del objetivo, que funcionan como oráculo. ¿Cuánto se pierde al usar un volumen **proyectado**? Diseño aprobado por Diego, con sección 4e en `VALIDACION_WALKFORWARD.ipynb`:
- **Volumen:** las secciones físicas de T−100 escaladas por una razón por tipo (campus × materia × componente). Hay tres fuentes:
  - **EUR:** Euribia, Σ P50 ÷ Σ inscritos del año anterior dentro de su propia serie;
  - **PER:** persistencia, razón 1;
  - **TEN:** tendencia, el crecimiento de los inscritos del campus entre T−100 y T−200.
- **Fuente de Euribia:**
  - 202410–202615: filas `REAL` de `SERIE_COMPLETA`, cada año reentrenado solo con años anteriores. La razón se calcula sobre las asignaturas dictadas en T y en T−100.
  - 202620 y 202625: el entregable.
- **Peso del naive (w):** se recalibra por variante, solo con los orígenes anteriores del mismo nivel.

**Ventajas de Euribia en la historia** (su resultado antes de 2026 es una cota optimista):
- La serie usa la grilla que se dictó, y la intersección con T−100 solo lo neutraliza en parte.
- Su nivel agregado se fija con `TASA_NIVEL` (0,9878), la media de 11 años cerrados que incluye el año objetivo. En consecuencia, **el total de Euribia es casi persistencia −1,2 %** y su aporte está en la composición.

**MASE en los orígenes que deciden** (celda / campus × día × bloque):

| Modelo | 202410 | 202420 | 202520 | 202610 | 202620 | Victorias | Media | ¿Adopta? |
|---|---|---|---|---|---|---|---|---|
| C1 (oráculo) | 1,000 / 1,000 | 0,992 / 0,970 | 0,987 / 0,981 | 0,959 / 0,946 | 0,944 / 0,866 | 4 / 4 | 0,964 | sí (referencia) |
| C1-EUR | 1,000 / 1,000 | 1,016 / 1,002 | 1,047 / 1,050 | 1,000 / 1,000 | 1,000 / 1,000 | 0 / 0 | 1,011 | **no** |
| C1-PER | 1,000 / 1,000 | 1,010 / 0,993 | 1,036 / 1,036 | 1,000 / 1,000 | 1,000 / 1,000 | 0 / 1 | 1,007 | no |
| C1-TEN | 1,000 / 1,000 | 0,971 / 0,904 | 1,152 / 1,181 | 0,996 / 0,978 | 0,996 / 0,935 | 3 / 3 | 1,011 | **sí, por poco** |

**Lectura**
- **Con volumen proyectado, C1 vuelve casi al naive.** El w recalibrado sube a 0,8–1,0 y la ganancia del oráculo (media 0,964) se pierde. El costo de proyectar es de unos +0,05 de MASE.
- **Ninguna fuente de volumen es claramente mejor.** El error de inscritos por tipo es de 0,26–0,30 para EUR, PER y TEN en pregrado, y en el total el sesgo de Euribia es −5 % a −12 %. Lo que falla es la **composición** (qué materia crece o cae), no el total.
- **C1-TEN pasa la regla** (3 de 5 en ambos granos), pero con ganancias chicas (0,90–0,996) y una pérdida grande en 202520 (1,15–1,18). Su media es peor que el naive.
- **En AV, Euribia sí aporta.** C1-EUR gana 202525, 202615 y 202625 (0,95–0,97), que son orígenes informativos. TEN y PER quedan en el naive.
- **Error del número de secciones con el estándar real:** 0,13–0,17 en pregrado con cualquier fuente (con volumen real era 0,07–0,20).
- **Banda de Euribia por tipo:** cubre el real en el 72–90 % de los inscritos en pregrado.

**D15 (26-10, decisión 3 de Diego: «si C1-Euribia pierde, Modelos usa la variante ganadora»):**
- `Modelos.ipynb` elige la variante **por nivel**, automáticamente:
  - **pregrado:** la que pasa la regla (hoy **C1-TEN**, w = 0,8). Si ninguna pasara, usa el naive;
  - **AV:** sus orígenes son informativos, así que usa la de menor MASE medio en ellos (hoy **C1-EUR**).
- **No se usa TEN en AV.** En 2026 la matrícula AV se trasladó de C02 a C05 (C02 ×0,4 y C05 ×1,7 en el mismo sufijo), y la tendencia por campus lo extrapolaría como si se repitiera, inflando el volumen AV 2027 en +16–24 % cuando el total AV estuvo plano.
- Euribia queda como **banda** bajo/alto: base × P10/P50 y base × P90/P50, por tipo.
- El aviso de ganancia marginal queda en los metadatos. En AV, w = 0 se calibra en el origen 202625, que es la foto con la inscripción abierta: hay que vigilarlo.

**Efecto en `Modelos.ipynb` (escenario base 2027):** 202710 = 345.663 inscritos (+4,9 % sobre 202610, antes 324.742 con Euribia) y 9.885 secciones con 4,4 % de déficit; 202720 = 327.739 (+6,0 %) y 9.389 secciones con 3,0 % de déficit; AV casi plano (Euribia). 203110 = 12.263 secciones con 11,4 % de déficit (NO VALIDADO). Consistencia con el banco sin cambios (0,942 frente a 0,944).

**Salidas:** `VALIDACION_RESULTADOS.parquet` (nuevos G1b-EUR/PER/TEN y C1-EUR/PER/TEN) y `VALIDACION_VOLUMEN.parquet`.


## 16. H5 · Banda P10–P90 calibrada con predicción conforme (26-10)

**Problema.** La banda de C1 solo medía el ruido del remuestreo de G1b, reducido además a (1 − w): cubría el real en el 1–12 % de las celdas (C1-TEN), con un ancho de ~1 sala.

**Método aprobado por Diego** (banco §5b):
- **Residuos normalizados:** e = (real − punto) ÷ √(punto + 1).
- **Estratos:** nivel × clase × tramo del punto (0–5, 5–20, 20–50 y más de 50 salas).
- **Calibración del origen T:** solo los orígenes anteriores del mismo nivel. El primer origen de cada nivel usa los residuos del naive en T−100 y T−200.
- **Granos:** celda y campus × día × bloque se calibran por separado.
- **Objetivo:** 80 %, aceptable entre 75 % y 85 %.
- **Largo plazo:** sin agrandar la banda por el horizonte.

**Cobertura P10–P90 de C1-TEN en los orígenes que deciden** (sin calibrar → conformal):

| Grano | 202410 | 202420 | 202520 | 202610 | 202620 | Dentro de [75 %, 85 %] |
|---|---|---|---|---|---|---|
| celda | 3 % → **80 %** | 9 % → 71 % | 9 % → 63 % | 3 % → **81 %** | 6 % → **81 %** | 3 de 5 |
| campus × día × bloque | 1 % → **79 %** | 10 % → 69 % | 12 % → 60 % | 3 % → **84 %** | 3 % → 87 % | 2 de 5 |

**Lectura**
- **La regla estricta no se cumple:** pasa en celda, pero no en campus × día × bloque, donde 202620 se pasa por poco.
- **La mejora es grande:** la cobertura media en pregrado sube del 6 % al 75 %. La puntuación de intervalo relativa de Winkler baja de 1,57 a 0,93 (C1-TEN) y de 1,48 a 0,84 (C1).
- **El ancho medio sube a ~13 salas** en campus × día × bloque.
- **Donde cubre de menos:** en 202420 y 202520, calibrados con solo 1–2 orígenes previos. 202520 es además el origen donde C1-TEN pierde con el naive. Con más orígenes la calibración se estabiliza.
- **En AV (C1-EUR, informativo):** cobertura 56–80 %, también por debajo del objetivo.

**Aplicación en `Modelos.ipynb` §5** (se aplica aunque no pase la regla estricta, porque es claramente mejor que la banda sin calibrar; **Diego la aceptó el 27-10** y queda como aviso en los metadatos):
- **Cuantiles:** salen de `BANDA_CUANTILES.parquet`, calibrados con todos los orígenes del modelo adoptado por nivel.
- **Banda por celda:** P10 / P50 / P90 = punto + q × √(punto + 1). Se agrega la columna `OCUPACION_PUNTUAL`.
- **Simulaciones de §7:** se rehacen sorteando residuos de la grilla q05…q95, de modo que la probabilidad de saturar es coherente con la banda.
- **Restricción física:** si el campus no tiene espacios activos de esa clase, la ocupación es 0. Sin ella, el q90 positivo del tramo 0–5 ponía ~2 salas en celdas imposibles (C10, C09) y probabilidades de saturar de 0,64.

**Resultado 202710 (escenario base):**
- 1.960 celdas posibles, con un ancho medio de banda de 8,1 salas.
- 127 celdas con probabilidad de saturar ≥ 10 % y 2 con ≥ 50 %. Las de mayor riesgo son salas de C06 y C04 en las mañanas (P50 de 28 sobre 29 activas y de 38 sobre 39).
- Consistencia con el banco sin cambios (0,942 frente a 0,944).

**Pendiente:**
- Recalibrar a medida que entren orígenes nuevos, porque los primeros cubren de menos.
- ~~2028–2031 sigue NO VALIDADO, también en la banda.~~ Resuelto en §17 (D17, 27-10).
- La banda supone residuos independientes entre celdas. Sirve para la probabilidad por celda, no para sumar celdas.

## 17. Largo plazo: pseudo-backtest por horizonte (27-10)

**Pregunta.** ¿Cuánto se equivoca el mapa de 2028–2031? Diseño aprobado por Diego el 27-10 (banco §7):
- **Pares:** bases 2022–2024 proyectadas en cadena a 1–4 años, contra el real. En pregrado hay 6 pares en H+1 y H+2, 4 en H+3 y 2 en H+4; AV es informativo.
- **Volumen:**
  - **ARI-REAL** es la mecánica de Modelos (razón de 1 año × matrícula anual de Ariadna) alimentada con la matrícula **real** de Ariadna, que tiene filas `REAL` desde 2010;
  - PER y TEN (compuesta) son los rivales ingenuos;
  - ORA (inscritos reales) es el piso.
- **Modelo:** w es el de Modelos (UG 0,8; AV 0). β sale de la base; en la base 2022 no hay pares previos y se usa β = 1.
- **Error de Ariadna:** su propio backtest (`DIAGNOSTICO_BACKTEST_28092026.csv`, método vigente por nivel), contrastado con su banda `n_bajo` / `n_alto`.

**MASE de pregrado contra el naive de la base** (media de los pares; celda / campus × día × bloque):

| Modelo | H+1 | H+2 | H+3 | H+4 |
|---|---|---|---|---|
| C1-ARI-REAL | 1,009 / 1,006 | 1,001 / 1,001 | 0,995 / 0,987 | 0,993 / 0,987 |
| C1-ORA (volumen perfecto) | 0,991 / 0,987 | 0,977 / 0,964 | 0,973 / 0,962 | 0,972 / 0,954 |
| C1-PER | 1,007 / 1,006 | 1,005 / 1,008 | 1,007 / 1,007 | 1,003 / 1,003 |
| C1-TEN compuesta | 1,009 / 1,005 | 1,030 / 1,044 | 1,017 / 1,019 | — |

**Lectura**
- **A largo plazo, C1 sigue pegado al naive.** Ni con volumen perfecto gana más de un 3–5 %. El error está en **dónde** caen las secciones, no en cuántas hay. La matrícula real de Ariadna recupera la mitad de esa ganancia desde H+3.
- **La TEN compuesta empeora con el horizonte.** Hace bien en no usarse a largo plazo.
- **Modelo por horizonte con la regla aprobada:**
  - **pregrado:** H+1 naive, H+2 C1 (4/6 en ambos granos), H+3 naive (celda 2/4), H+4 C1 (2/2) y H+5 hereda C1;
  - **AV:** C1 en H+1 a H+3 y naive en H+4 y H+5.
  - Las victorias y derrotas están dentro de ±0,02. H+1 lo sigue decidiendo el banco principal (D15: C1-TEN).
- **Banda:** la de 1 año, sin ensanchar, cubre el 69 / 62 / 55 % en H+2 / H+3 / H+4 (pregrado, celda).
  - **k_h** (Q80 de |e| contra H+1) es 1,34 / 1,56 / 1,83 en H+2 a H+4. H+5 se extrapola a 1,94 (k = h^γ). Con k_h la cobertura vuelve al 80–88 %, medido dentro de la muestra.
  - En AV, k_h es 1,20 / 1,39 / 1,80 / 1,97.
- **Ariadna en pregrado (MA_TASAS) subestima el crecimiento:** −0,8 % en H+1, −4,4 % en H+2 y −8,6 % en H+3. Su banda cubre el real en el 80 %, 50 % y 33 % de los casos. Factor de ensanche de bajo/alto: 1,13 / 1,34 / 1,76.
  - **AV (HOLT):** 1,00 / 1,44 / 1,52.
  - MG lo necesita aún más (hasta 3,5), pero el mapa no usa MG.

**Aplicación en `Modelos.ipynb` (D17):**
- **Modelo del año:** C1 con el w del banco en **todos** los años (decisión de Diego del 27-10, ver abajo). La regla por horizonte de `BANDA_HORIZONTE.parquet` queda solo como informativa.
- **Banda:** los cuantiles se ensanchan alrededor de la mediana con el k_h de C1.
- **Escenarios:** bajo y alto de 2028–2031 = base ± factor × (banda de Ariadna − base). H+4 y H+5 usan el factor de H+3.
- **Columnas:** `H` y `VALIDADO` = H ≤ 4. 2031 queda como extrapolado.

**Resultado, escenario base, pregrado:**

| Período | H | w | Ancho medio de la banda | Celdas con prob. de saturar ≥ 10 % / ≥ 50 % |
|---|---|---|---|---|
| 202710 | 1 | 0,8 | 8,1 | 127 / 2 |
| 202810 | 2 | 0,8 | 10,8 | 213 / 4 |
| 202910 | 3 | 0,8 | 12,3 | 263 / 3 |
| 203010 | 4 | 0,8 | 14,8 | 327 / 11 |
| 203110 | 5 | 0,8 | 15,8 | 355 / 16 |

- **Volumen base de 202x10:** 345,7 mil, 364,9 mil, 385,2 mil, 406,5 mil y 428,8 mil.
- **Déficit de la programación explícita:** 4,4 % → 5,3 % → 7,4 % → 9,3 % → 11,4 %.
- **Consistencia con el banco:** sin cambios (0,942 frente a 0,944).

**D17 · decisión de Diego (27-10): C1 en todo el largo plazo.** La regla por horizonte daba C1 en 2028, naive en 2029 y C1 en 2030–2031. Así, en 2029 el mapa era una copia del de 2026 aunque el volumen sube un 17 %, y las celdas en saturación bajaban de 4 a 1 para volver a 11 en 2030. Ese vaivén era ruido, porque las diferencias son de ±0,02. Se usa C1 en todos los años, con el aviso en los metadatos de que su ventaja sobre el naive es marginal (MASE 0,99–1,01). Así 2029 queda en 263 / 3 celdas y la serie crece de forma monótona.

**Límites**
- H+4 tiene 2 pares, ambos con objetivo 2026.
- k_h y la cobertura con k se miden dentro de la misma muestra.
- La matrícula real valida la mecánica, no el pronóstico de Ariadna, que entra solo por su backtest agregado (H+1 a H+3).
- **Salidas:** `VALIDACION_HORIZONTE.parquet`, `BANDA_HORIZONTE.parquet` y `ARIADNA_ERROR_HORIZONTE.parquet`.

## 18. Rango de capacidad: alerta anidada por tamaño de sala (27-10)

**Problema.** Hasta el 27-10 el mapa y la probabilidad de saturar contaban salas contra salas, sin importar su tamaño: una sección de 80 «cabía» en una sala libre de 20. La programación explícita sí buscaba sala con capacidad, pero tenía dos huecos:
- las secciones que venían del período base se quedaban en su sala sin revisar si cabían;
- las copias comparaban la capacidad contra los inscritos de la base, no contra los proyectados.

Resultado: el 23 % de las asignaciones dejaba más inscritos que la capacidad de la sala.

**Diseño aprobado por Diego (27-10, D18):**
- **Rangos:** los 4 de la planta: 0-20, 21-40, 41-60 y 60 o más.
- **Alerta anidada hacia arriba:** para cada rango r, la demanda que necesita r o más contra los espacios de r o más. Una sección chica puede usar una sala grande, pero no al revés.
- **Banco:** validación solo informativa (§8).

**Reglas de implementación** (las dos últimas se agregaron al probar, con datos):

1. **Tolerancia por clase.** Es el percentil 90 de inscritos ÷ capacidad por sala-bloque en el período base, con piso 1. En 2026 el 6–9 % de las salas-bloque y el ~20 % de los laboratorios-bloque superan su capacidad nominal (rotaciones, grupos, capacidad mal registrada). Con capacidad estricta, el modelo inventaría déficit que hoy no existe.
   - Base 2026: SALA 1,00 y LABORATORIO 1,33 / 1,32 en los sufijos 10 / 20.
   - AV: 1,00.
2. **Inscritos proyectados por sección** = los de la base × razón del estrato^(1 − β). G1b agrega secciones al ritmo razón^β, así que el resto del crecimiento engorda las secciones.
3. **Capacidad que necesita una sección** = inscritos proyectados ÷ el mayor entre la tolerancia y el sobrecupo que ya tenía en su sala de la base.
   - **Corrección:** con solo la tolerancia, los laboratorios que ya funcionan sobre su capacidad aparecían pidiendo laboratorios de 60 o más, que casi no existen (hay 4). Las alertas por tamaño de 2027 se inflaban de 93 a 199.
4. **Oferta efectiva por rango** (desde 21-40) = el mayor entre el inventario activo y lo que el período base ya usa.
   - Corrige 20 celdas-rango en 202610 y 74 en 202620, que corresponden a salas en uso que no están activas en la planta o que la planta clasifica distinto.
   - El rango 0-20, es decir la celda completa, no se toca: es la `PROB_SATURA` de siempre. Hay un control impreso que lo verifica.
5. **Programación explícita:**
   - una sección se queda en su sala si sus inscritos proyectados no superan la capacidad × tolerancia, o lo que ya tenía en la base;
   - si no, y en el caso de las copias siempre, busca la sala libre más chica que sirva, de la misma clase, primero en su edificio y después en su campus;
   - columnas nuevas: `CAPACIDAD_SALA`, `RANGO_DEMANDADO` y `SOBRECUPO` (cabe por tolerancia, pero supera la capacidad nominal).

**Validación informativa (banco §8, `VALIDACION_RANGO.parquet`).**
- **MASE de C1 por rango contra el naive:** 0,98–1,03 en los 10 orígenes. No mejora la ubicación, igual que en el grano celda.
- **El reparto de la demanda entre rangos sí acierta.** Ejemplo, 202620:

  | | 0-20 | 21-40 | 41-60 | 60 o más |
  |---|---|---|---|---|
  | Proyectado | 40 % | 31 % | 13 % | 16 % |
  | Real | 40 % | 30 % | 16 % | 14 % |

**Resultado, escenario base, pregrado:**

| Período | Celdas ≥ 25 %, sin tamaño | Celdas ≥ 25 %, con tamaño | Déficit de la programación (antes → ahora) |
|---|---|---|---|
| 202710 | 48 | **93** | 4,4 % → **5,3 %** |
| 202810 | 76 | **121** | 5,3 % → **7,6 %** |
| 202910 | 87 | **138** | 7,4 % → **10,7 %** |
| 203010 | 130 | **179** | 9,3 % → **13,9 %** |
| 203110 | 156 | **211** | 11,4 % → **17,4 %** |

**Lectura**
- **Al considerar el tamaño, las alertas casi se duplican en 2027.** Aparecen faltas que el conteo de salas escondía:
  - laboratorios grandes de C01 (27 celdas en «60 o más» y 16 en «41-60»);
  - salas de C07 en 41-60.
- Las salas de C04 y C06 en 0-20 siguen siendo las de siempre: no faltan salas grandes, faltan salas a secas.
- **El déficit de la programación se concentra en salas grandes.** En 2027, el 62 % de los casilleros sin sala piden «60 o más». Por campus: C01 613, C02 502, C04 195 y C03 194 sesiones-casillero.
- Un 8,8 % de los casilleros de 2027 (ponderado por `PESO_SEMANAS`, sufijo 10; 14,9 % en 2031) queda en **sobrecupo tolerado**: cabe por la tolerancia de su clase, pero supera la capacidad nominal.

**Para validar con infraestructura**
- Los laboratorios de 60 o más en C01: si en la práctica se dividen en grupos, la alerta es de gestión, no de espacio.
- La capacidad registrada en la planta, que es la base de la tolerancia.

**Salidas:**
- `OCUPACION_POR_RANGO.parquet` (nuevo): demanda acumulada P10 / P50 / P90, espacios acumulados y `PROB_SATURA_ACUM` por rango.
- En `OCUPACION_Y_DEFICIT.parquet`: `PROB_SATURA_TAMANO` y `RANGO_CRITICO`.
- En `PROGRAMACION_SINTETICA.parquet`: `CAPACIDAD_SALA`, `RANGO_DEMANDADO` y `SOBRECUPO`.

## 19. Naive escalado en el largo plazo (C1E, 28-10)

**Problema.** A largo plazo el naive es una copia del período base que no crece. Con w = 0,8, el centro del mapa (pregrado, sufijo 10, escenario base) crecía solo un 4 % entre 2027 y 2031 (26.419 → 27.516), mientras los inscritos crecían un 24 % (345.663 → 428.813). En el pseudo-backtest (§17), C1 quedaba bajo lo real en un 0,8 / 2,5 / 5,0 / 7,6 % en H+1 … H+4.

**Diseño.** **C1E** = w · naive escalado + (1 − w) · G1b.
- El naive de cada campus × clase se multiplica por el crecimiento de salas que implica el objetivo de G1b: Σ volumen objetivo con β ÷ Σ volumen base de sus estratos.
- Solo cuentan los estratos del período base, porque el naive es su mapa. Los que vienen de T−200 o se prestan de un estrato grueso no entran, y los que desaparecen suman su volumen base con objetivo 0.
  - **Corrección del 28-10:** la primera corrida contaba también los estratos prestados. El volumen del estrato grueso se repetía en el denominador y la variante ORA daba un sesgo de −57 %. Las variantes por razón (TEN, EUR, PER, ARI-REAL) no cambiaron, porque todos sus estratos vienen de la base.
- w se recalibra en el banco igual que en C1. En pregrado queda en 1,0: el mapa de largo plazo es el naive escalado puro.

**Banco (pregrado, orígenes que deciden).**

*A 1 año*, C1E-TEN pierde contra C1-TEN en 3 de 5 orígenes:

| Modelo | MASE en celda |
|---|---|
| C1E-TEN | 0,94–1,23 |
| C1-TEN | 0,97–1,15 |

*A largo plazo*, pseudo-backtest ARI-REAL en celda:

| | H+1 | H+2 | H+3 | H+4 |
|---|---|---|---|---|
| Sesgo C1 | −0,8 % | −2,5 % | −5,0 % | −7,6 % |
| Sesgo C1E | +3,0 % | +2,7 % | −0,2 % | −2,7 % |
| MASE C1 | 1,009 | 1,001 | 0,995 | 0,993 |
| MASE C1E | 1,053 | **1,012** | **0,959** | **0,962** |

- En campus × día × bloque, C1E queda en 1,056 / 1,015 / 0,931 / 0,943.
- La banda calibrada cubre lo mismo que con C1.
- En AV, C1E-ARI-REAL queda en 0,951 / 0,816 / 0,766 / 0,945, contra 0,967 / 0,799 / 0,754 / 1,083 de C1.

**Decisión de Diego (28-10, D19):**
- **2027 sigue con C1-TEN** (UG, w = 0,8) **y C1-EUR** (AV, w = 0).
- **2028–2031 pasa a C1E** (UG C1E-TEN, AV C1E-EUR, w = 1,0), con la banda de C1E y su k_h: UG 1,31 / 1,44 / 1,72, H5 1,82 extrapolado.
- **Aviso declarado:** en H+2 (2028), C1E empeora el MASE en 0,011 (1,012 contra 1,001), dentro del ruido de ±0,02. La ganancia aparece desde H+3.
- La alternativa estricta, C1E desde 2029, hacía saltar el mapa entre 2028 y 2029. Se descartó.

**Nota sobre ORA.** Con el volumen real, C1E-ORA mejora a C1 en H+1 y H+2 (0,956 / 0,917), pero no en H+3 y H+4 (1,006 / 1,024, sesgo −17 / −20 %). El factor solo escala los estratos que ya existen, y con el volumen real parte del crecimiento llega por estratos nuevos (carreras o unidades que no estaban en la base). En las variantes por razón eso no pasa, porque proyectan sobre las secciones de la base.

**Resultado (pregrado, sufijo 10, escenario base):**

| Período | Centro del mapa | Factor de escala (mediana) | Alertas ≥ 25 %, con tamaño (antes D19) | ≥ 10 % | ≥ 50 % |
|---|---|---|---|---|---|
| 202710 | 26.419 | 1,00 | 93 (93) | 181 | 17 |
| 202810 | 28.183 | 1,07 | 125 (121) | 297 | 33 |
| 202910 | 29.459 | 1,12 | 179 (138) | 366 | 58 |
| 203010 | 30.790 | 1,17 | 251 (179) | 427 | 94 |
| 203110 | 32.172 | 1,22 | 297 (211) | 466 | 136 |

- El centro del mapa crece un 22 % entre 2027 y 2031, en línea con los inscritos (+24 %) elevados a β.
- Alertas ≥ 25 % por campus en 2031:

  | C01 | C04 | C06 | C03 | C02 | C07 |
  |---|---|---|---|---|---|
  | 93 | 64 | 50 | 37 | 32 | 21 |

- La programación explícita (§6) no cambia: su número de secciones viene del estándar real H2. Siguen el déficit de 5,3 % → 17,4 % y el sobrecupo de 8,8 % → 14,9 %.

**Salidas.** `MAPA_PROYECTADO` y `OCUPACION_Y_DEFICIT` traen las columnas nuevas `MODELO` (C1 o C1E) y `ESCALA_NAIVE`. `MODELO_METADATOS.json` trae `modelo_largo_plazo` y el aviso de H+2.

---

> **Dirección de Ingeniería de Datos — Universidad Ficticia**
> Responsable: Diego Evans Pérez Paz
