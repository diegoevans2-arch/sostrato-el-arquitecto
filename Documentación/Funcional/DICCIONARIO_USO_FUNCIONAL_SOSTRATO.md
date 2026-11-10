---
title: "Diccionario de uso funcional · Sóstrato el Arquitecto"
tags:
  - diccionario-datos
  - ocupacion-espacios
  - uso-funcional
  - banner9
  - entregable
audiencias: [puente, ejecutivo, tecnico]
status: activo
type: diccionario-datos
project: sostrato
notebook: Notebooks + Scripts/Modelos.ipynb
entregable: BBDD/OCUPACION_Y_DEFICIT.parquet
version: "1.0"
fecha_creacion: 2026-11-05
ultima_actualizacion: 2026-11-05
owner: Dirección de Ingeniería de Datos
author: Diego Evans Pérez Paz
---

# 📊 Diccionario de uso funcional · Sóstrato el Arquitecto

**Navegación:** [[DOCUMENTO_TECNICO_FUNCIONAL_PIPELINE_SOSTRATO]] · [[DOCUMENTO_TECNICO_FUNCIONAL_MODELO_SOSTRATO]] · [[INFORME_EJECUTIVO_ALERTAS_2027_2031]]

**Cómo leer este documento.** Es la referencia para usar los resultados sin abrir el código. §1 dice qué archivo abrir según la pregunta. §2 y §3 definen los términos y sus valores. §4 explica cada número de la simulación. §5 describe las columnas. §6 y §7 enseñan a leer una fila y advierten las lecturas equivocadas. Marcas: 👔 lectura ejecutiva · 🧭 puente entre negocio y técnica · 🔧 detalle técnico.

---

> [!abstract] 👔 Qué permite responder
> **¿Dónde y cuándo faltarán salas o laboratorios hasta 2031, de qué tamaño y con qué probabilidad?**
>
> - **Decisiones que habilita:** priorizar campus y franjas horarias, validar con infraestructura y preparar escenarios.
> - **Costo de leerlo mal:** tratar una alerta como una certeza, sumar bandas entre celdas o leer una sala de la programación como una predicción.

> [!tip] 💡 Analogía general: el parte meteorológico
> «62 % de probabilidad de saturar» es como «62 % de probabilidad de lluvia». No dice que va a faltar sala con certeza, ni exactamente a qué hora. Dice dónde conviene prepararse.

---

## 1 · Qué mirar según la pregunta 🧭

### 1.1 · Preguntas frecuentes de uso

| Quiero saber… | En la simulación | En los datos | Columna clave |
|---|---|---|---|
| ¿Cuánto crece el riesgo por año? | Curva de alertas · Panorama | `OCUPACION_Y_DEFICIT` | `PROB_SATURA_TAMANO ≥ 0,25` |
| ¿Qué campus se satura primero? | Lista de campus + línea de tiempo | `OCUPACION_Y_DEFICIT` | `COD_CAMPUS_EDIFICIO`, `PERIODO` |
| ¿En qué días y horas? | Mapa de alertas · Semana | `OCUPACION_Y_DEFICIT` | `DIA`, `BLOQUE` |
| ¿Faltan salas o laboratorios? | Filtro de clase en Semana | `OCUPACION_Y_DEFICIT` | `CLASE` |
| ¿De qué tamaño? | Filtro de tamaño · hover | `OCUPACION_POR_RANGO` | `RANGO_CRITICO`, `PROB_SATURA_ACUM` |
| ¿Qué porcentaje de clases queda sin sala? | Panorama | `PROGRAMACION_SINTETICA` | `DEFICIT`, `PESO_SEMANAS` |
| ¿Cómo se vería una semana concreta? | Salas · 3D | `PROGRAMACION_SINTETICA` | `DIA`, `BLOQUE`, `SALA` |
| ¿Por facultad? | No disponible en las vistas | `PROGRAMACION_SINTETICA` | `UNIDAD` |
| ¿Cuántos inscritos y secciones habrá? | No disponible en las vistas | `VOLUMEN_PROYECTADO`, `SECCIONES_PROYECTADAS` | `INSCRITOS_PROY`, `SECCIONES_PROY` |
| ¿Cuántos espacios hay hoy? | Título de Salas | `OFERTA_ESPACIOS` | `ACTIVO`, `CLASE_MAPA` |
| ¿Cuánta capacidad está ociosa? | No disponible en las vistas | `OFERTA_CELDA` | `N_OCIOSOS` |
| ¿Cuántas sesiones no tienen sala asignada hoy? | No disponible en las vistas | `DEMANDA_SIN_SALA` | `SESIONES_HORA_SIN_SALA` |
| ¿Cuánto confiar? | Ayuda (`?`) | [[DOCUMENTO_TECNICO_FUNCIONAL_MODELO_SOSTRATO]] §9 | `VALIDADO`, `H` |

### 1.2 · Los archivos

**Ruta común:** `Sóstrato el Arquitecto - (Euribia + Cirilo + Ariadna)\BBDD\`. La carpeta no está en git.

| Archivo | Qué es | Grano | Filas | Para quién |
|---|---|---|---:|---|
| **`OCUPACION_Y_DEFICIT`** ⭐ | **El resultado principal** | Período × escenario × celda | 147.000 | Todo análisis |
| **`OCUPACION_POR_RANGO`** | Alerta por tamaño | Período × escenario × celda × rango | 225.573 | Análisis de tamaño |
| **`PROGRAMACION_SINTETICA`** | Secciones simuladas, con sala o déficit | Sección × casillero | 471.521 | Análisis de falta y facultad |
| `MAPA_PROYECTADO` | Mapa antes de comparar con la oferta | Período × escenario × celda | 147.000 | Trazabilidad |
| `VOLUMEN_PROYECTADO` | Inscritos | Campus × materia × componente × período × escenario | 31.830 | Volumen |
| `SECCIONES_PROYECTADAS` | Número de secciones | Campus × componente × período × escenario | 2.130 | Volumen |
| `OFERTA_ESPACIOS` | Inventario de espacios | Edificio × sala | 4.944 | Oferta |
| `OFERTA_CELDA` | Oferta resumida | Campus × clase × rango | 48 | Oferta |
| `PROG_HIST_NRC` | Programación real | Período × NRC | 170.452 | Historia |
| `PLANTILLAS_NRC` | Semana tipo real | NRC × día × bloque × tramo | 2.236.891 | Historia |
| `DEMANDA_SIN_SALA` | Sesiones reales sin sala | Período × campus | 117 | Historia |
| `UNIDAD_ACADEMICA` | Materia → facultad o departamento | Materia | 154 | Catálogo |
| `FACTOR_COMPARTICION` | Factor de sala compartida | Campus × clase | 14 | Referencia |
| `MODELO_METADATOS.json` | Parámetros de la corrida | Corrida | — | Trazabilidad |

Los `.parquet` conservan los tipos de datos. Se abren en Python, Power BI o DuckDB; para Excel hay que exportarlos primero.

---

## 2 · Glosario funcional 🧭

| Término | Qué significa | Dónde aparece |
|---|---|---|
| **Alerta** | Probabilidad de saturar de 25 % o más. Es la cifra que se informa | `PROB_SATURA_TAMANO` |
| **Banda P10–P90** | Rango probable de la demanda: 10 % de las veces queda bajo el P10 y 10 % sobre el P90 | `OCUPACION_P10`, `OCUPACION_P90` |
| **Base** | Período real de 2026 desde el que se proyecta | `BASE` |
| **Bloque** | Módulo horario de 40 minutos (§3.3) | `BLOQUE` |
| **Casillero** | Una sección en un día y bloque | Fila de `PROGRAMACION_SINTETICA` |
| **Celda** | Campus × día × bloque × clase, en un período y escenario | Fila de `OCUPACION_Y_DEFICIT` |
| **Clase de espacio** | Sala o laboratorio | `CLASE` |
| **Clases sin sala (déficit)** | Parte de la programación, ponderada por semanas, que no encuentra sala de su tamaño | `DEFICIT` |
| **Crítica** | Probabilidad de saturar de 50 % o más | `PROB_SATURA_TAMANO` |
| **Demanda** | Espacios que se necesitarían a la vez en la celda | `OCUPACION_P50`, `DEMANDA_ACUM_P50` |
| **Escenario** | Bajo, base o alto de crecimiento. Cada uno se cuenta por separado | `ESCENARIO` |
| **Espacio activo** | Sala o laboratorio usado en los últimos 2 años | `ACTIVO` |
| **Espacio ocioso** | Sala o laboratorio sin uso en 2 años. No cuenta como oferta | `N_OCIOSOS` |
| **Estándar real** | Tamaño de sección que reproduce lo programado en 2026 | `ESTANDAR` |
| **Extrapolado** | Se proyecta igual, pero el error no se pudo medir. Solo 2031 | `VALIDADO = False` |
| **Horizonte (H)** | Años desde la base: 2027 = 1 … 2031 = 5 | `H` |
| **Hora en alerta** | Nombre provisorio de la celda en alerta en la simulación renovada. Cada bloque dura 40 minutos | `renuevo_ui` |
| **Lista cruzada (LC)** | Una misma clase con varios códigos. Ocupa una sala | `COD_LC` |
| **Naive** | Repetir el mapa real del mismo semestre de 2026. Es la vara con que se mide el modelo | [[DOCUMENTO_TECNICO_FUNCIONAL_MODELO_SOSTRATO]] §5.1 |
| **NRC** | Una sección programada en Banner | `NRC` |
| **Oferta efectiva** | Desde 21-40, el mayor entre el inventario activo y lo que 2026 ya usa | `ESPACIOS_ACUM` |
| **Probabilidad de saturar** | Porcentaje de simulaciones en que la demanda supera a los espacios | `PROB_SATURA` |
| **Programación sintética** | Secciones simuladas a partir de secciones reales. No predice cursos | `PROGRAMACION_SINTETICA` |
| **Rango de capacidad** | Tamaño de sala: 0-20, 21-40, 41-60 o 60 o más | `RANGO_CAPACIDAD` |
| **Rango crítico** | El tamaño donde la falta es más probable | `RANGO_CRITICO` |
| **Sobrecupo tolerado** | Cabe por la tolerancia de su clase, pero supera la capacidad nominal | `SOBRECUPO` |
| **Sufijo** | Los últimos dígitos del período (§3.2) | `PERIODO` |
| **Tasa de uso** | Demanda P50 ÷ espacios | `TASA_USO_P50` |
| **Vigilancia** | Probabilidad de saturar de 10 % o más | `PROB_SATURA_TAMANO` |

---

## 3 · Catálogos 🧭

### 3.1 · Campus

| Código | Campus | Salas activas | Laboratorios activos |
|---|---|---:|---:|
| `C01` | Sede Norte · Campus 01 | 112 | 85 |
| `C07` | Sede Norte · Campus 07 | 8 | 8 |
| `C04` | Sede Sur | 39 | 32 |
| `C03` | Sede Austral · Sede Austral (Campus 03) | 62 | 30 |
| `C02` | Sede Centro · Campus 02 | 71 | 55 |
| `C05` | Sede Centro · Campus 05 | 88 | 27 |
| `C06` | Sede Centro · Campus 06 | 29 | 7 |

`COD_CAMPUS_EDIFICIO` es el campus donde está el edificio. `COD_CAMPUS` es el campus de la sección y además incluye `C10` en el volumen, que no llega al mapa.

### 3.2 · Períodos y escenarios

| Sufijo | Nivel | Lectura en la simulación |
|---:|---|---|
| `10` | Pregrado | 1.er semestre |
| `20` | Pregrado | 2.º semestre |
| `05` | Advance | AV · T1 |
| `15` | Advance | AV · T2 |
| `25` | Advance | AV · T3 |

Ejemplo: `202910` es el 1.er semestre de 2029.

| Año | H | `VALIDADO` | Modelo | Lectura |
|---:|---:|:---:|---|---|
| 2027 | 1 | ✅ | C1 | Validado con 10 orígenes |
| 2028 | 2 | ✅ | C1E | Validado con 6 pares |
| 2029 | 3 | ✅ | C1E | Validado con 4 pares |
| 2030 | 4 | ✅ | C1E | Validado con solo 2 pares |
| 2031 | 5 | ❌ | C1E | Extrapolado: leer como tendencia |

| `ESCENARIO` | 2027 | 2028–2031 |
|---|---|---|
| `bajo` | Cuantil P10 de Euribia, por tipo de curso | Escenario bajo de Ariadna, ensanchado |
| `base` | Tendencia del campus (pregrado) o Euribia (Advance) | Matrícula de Ariadna |
| `alto` | Cuantil P90 de Euribia, por tipo de curso | Escenario alto de Ariadna, ensanchado |

### 3.3 · Bloques

Fuente: `BLOQUES_ESTANDAR_01122025.csv`. El bloque 0 agrupa lo anterior a las 08:00.

| Bloque | Inicio | Fin | | Bloque | Inicio | Fin |
|---:|---:|---:|---|---:|---:|---:|
| 1 | 08:00 | 08:40 | | 11 | 16:10 | 16:50 |
| 2 | 08:40 | 09:20 | | 12 | 16:50 | 17:30 |
| 3 | 09:30 | 10:10 | | 13 | 17:35 | 18:15 |
| 4 | 10:10 | 10:50 | | 14 | 18:15 | 18:55 |
| 5 | 11:00 | 11:40 | | 15 | 19:00 | 19:40 |
| 6 | 11:40 | 12:20 | | 16 | 19:40 | 20:20 |
| 7 | 12:30 | 13:10 | | 17 | 20:25 | 21:05 |
| 8 | 13:10 | 13:50 | | 18 | 21:05 | 21:45 |
| 9 | 14:40 | 15:20 | | 19 | 21:50 | 22:30 |
| 10 | 15:20 | 16:00 | | | | |

### 3.4 · Semáforo y tamaño

| Nivel | Probabilidad | Ícono |
|---|---:|:---:|
| Sin alerta | Menos de 10 % | — |
| Vigilancia | 10 % o más | ▲ |
| **Alerta** | **25 % o más** | ◆ |
| Crítica | 50 % o más | ● |

| Rango | Qué cuenta en la alerta | En el hover |
|---|---|---|
| `0-20` | Todo espacio. Equivale a la celda completa | «todos los tamaños» |
| `21-40` | Salas de 21 o más | «21-40 o más» |
| `41-60` | Salas de 41 o más | «41-60 o más» |
| `60 o más` | Salas de más de 60 | «60 o más» |

### 3.5 · Componentes

| Código | Significado |
|---|---|
| `TEO` | Cátedra teórica |
| `LAB` | Laboratorio |
| `TAL` | Taller |
| `SIM` | Simulación |
| `ELG` | Electivo |
| `AYU`, `GRU`, `OCS`, `SSA` | Código de horario de Banner (`ssbsect_schd_code`). Su significado no consta en la documentación revisada: pendiente de confirmar |

---

## 4 · Cada número de la simulación 🧭

Vigente para la propuesta renovada (`Documentación/renuevo_ui/`). Entre paréntesis, el nombre en la demo anterior (`DEMO_SOSTRATO.html`).

> [!warning] ⚠️ «Hora» es un nombre provisorio
> La simulación renovada dice «horas en alerta» donde los informes dicen «celdas en alerta». Es lo mismo: una celda es un **bloque de 40 minutos**, de una clase de espacio, en un campus. 297 «horas» son 297 bloques. Queda pendiente decidir el nombre definitivo.

### 4.1 · Panorama (Curva de alertas)

| Número | Qué es | Cálculo | ¿Responde a los filtros? |
|---|---|---|---|
| **Número grande** | Celdas en alerta | Cuenta de `PROB_SATURA_TAMANO ≥ 0,25` | Campus, año, período, escenario y tamaño |
| **Críticas** | Celdas críticas | Cuenta de `≥ 0,50`. Están incluidas en el número grande | Los mismos |
| **Clases sin sala** | Parte de la programación sin sala | `Σ PESO_SEMANAS en déficit ÷ Σ PESO_SEMANAS` | Campus, año y período. **Siempre escenario base y todos los tamaños** |
| **En sobrecupo** | Parte de la programación en sobrecupo | `Σ PESO_SEMANAS en sobrecupo ÷ Σ PESO_SEMANAS` | Los mismos que clases sin sala |
| **Curva** | Celdas en alerta por año | Una línea por el escenario elegido | Sí |
| **Área** | Rango bajo–alto | Desde 2028. 2027 se muestra como línea punteada porque tiene otra definición | Sí |
| **Barras** | Clases sin sala, por tamaño pedido | Reparto del déficit entre los 4 rangos | Campus y período |

### 4.2 · Lista de campus y línea de tiempo

| Número | Qué es |
|---|---|
| **Número de cada campus** | Celdas en alerta de salas y laboratorios, en el año elegido |
| **Barras pequeñas** | Las mismas celdas, de 2027 a 2031 |
| **Línea de tiempo** | Celdas en alerta por año, del campus elegido |

### 4.3 · Semana (Mapa de alertas)

| Número | Qué es | Cálculo |
|---|---|---|
| **Número grande** | Celdas en alerta, de la clase elegida | Cuenta de la probabilidad ≥ 25 % |
| **Color de la celda** | Semáforo; sin alerta, el tono muestra el uso | `P50 ÷ espacios` en 4 tramos |
| **Punto blanco** | Faltan salas grandes | En alerta o crítica, con tamaño crítico de 41 o más |
| **Rayado** | 2031 extrapolado | — |
| **Horas más exigidas** | Las 9 celdas de mayor probabilidad | Con probabilidad ≥ 10 % |

**El hover de una celda:**

| Línea | Qué significa | Columna |
|---|---|---|
| Prob. de saturar | Probabilidad en el tamaño más exigido | `PROB_SATURA_TAMANO` |
| Tamaño más exigido | El rango donde se alcanza esa probabilidad | `RANGO_CRITICO` |
| Salas necesarias: P50 x de y | Mediana de la demanda total contra los espacios activos | `OCUPACION_P50`, `CAPACIDAD` |
| Banda P10–P90 | Rango probable de la demanda total | `OCUPACION_P10`, `OCUPACION_P90` |
| Oferta efectiva del modelo | Aparece si el modelo usa más espacios que los activos | `ESPACIOS_ACUM` |

Con filtro de tamaño, la probabilidad y el P50 son de ese tamaño o más: `PROB_SATURA_ACUM` y `DEMANDA_ACUM_P50`.

### 4.4 · Salas y 3D (Programación proyectada · Dónde no cabe)

| Número | Qué es | Cálculo |
|---|---|---|
| **x de y espacios ocupados** | Espacios con al menos una sección en ese bloque, y total de activos | Sin ponderar por semanas |
| **Secciones sin sala** | Filas en déficit de ese bloque | Sin ponderar por semanas |
| **% de ocupación** | x ÷ y | — |
| **Barras del día** | Ocupados y sin sala por bloque, con los activos como línea punteada | — |
| **Bandeja «Sin sala»** | Secciones sin sala, por tamaño pedido | — |
| **Color de la sala** | Llenado: inscritos ÷ capacidad, en 3 tramos, y sobrecupo | `INSCRITOS_EST`, `CAPACIDAD_SALA` |

> [!warning] ⚠️ Salas y 3D son solo escenario base y semestres de pregrado
> Si se elige otro escenario o un período de Advance, se muestra el base y el 1.er semestre, y aparece una etiqueta que lo avisa.

---

## 5 · Diccionario de columnas 🔧🧭

### 5.1 · `OCUPACION_Y_DEFICIT` ⭐

147.000 filas × 23 columnas. Sin nulos. `MAPA_PROYECTADO` tiene las primeras 17.

| # | Columna | Tipo | Qué significa | Ejemplo |
|---:|---|---|---|---|
| 1 | `PERIODO` | int | Período proyectado | `202910` |
| 2 | `ESCENARIO` | string | `bajo`, `base`, `alto` | `base` |
| 3 | `PLAZO` | string | `corto` (2027) o `largo` (2028–2031) | `largo` |
| 4 | `H` | int | Años desde la base | `3` |
| 5 | `VALIDADO` | bool | `False` solo en 2031 | `True` |
| 6 | `COD_CAMPUS_EDIFICIO` | string | Campus del edificio | `C04` |
| 7 | `DIA` | string | `LUNES` a `DOMINGO`, sin tildes | `MARTES` |
| 8 | `BLOQUE` | int | 0 a 19 | `3` |
| 9 | `CLASE` | string | `SALA` o `LABORATORIO` | `SALA` |
| 10 | `OCUPACION_PUNTUAL` | float | Centro del mapa, en espacios | `43,298` |
| 11 | `OCUPACION_P10` | float | Demanda, percentil 10 | `30,263` |
| 12 | `OCUPACION_P50` | float | Demanda, mediana | `41,773` |
| 13 | `OCUPACION_P90` | float | Demanda, percentil 90 | `60,283` |
| 14 | `W_NAIVE` | float | Peso del naive | `1,0` |
| 15 | `BETA` | float | Elasticidad entre salas e inscritos | `0,821` |
| 16 | `MODELO` | string | `C1` (2027) o `C1E` (2028–2031) | `C1E` |
| 17 | `ESCALA_NAIVE` | float | Crecimiento de salas aplicado al naive | `1,169` |
| 18 | `PROB_SATURA` | float | Probabilidad de saturar, sin mirar tamaño, de 0 a 1 | `0,62` |
| 19 | `CAPACIDAD` | float | Espacios activos de esa clase en el campus. **No son asientos** | `39` |
| 20 | `TASA_USO_P50` | float | `OCUPACION_P50 ÷ CAPACIDAD` | `1,071` |
| 21 | `DEFICIT_SALAS` | float | Casilleros sin sala, ponderados. Solo escenario base | `9,765` |
| 22 | `PROB_SATURA_TAMANO` | float | **Probabilidad del semáforo**, de 0 a 1 | `0,62` |
| 23 | `RANGO_CRITICO` | string | Tamaño donde se alcanza. En celdas sin riesgo no tiene lectura | `0-20` |

### 5.2 · `OCUPACION_POR_RANGO`

225.573 filas × 14 columnas. Una celda puede no tener todos los rangos: si no hay demanda ni espacios de ese tamaño, no hay fila.

| # | Columna | Tipo | Qué significa | Ejemplo |
|---:|---|---|---|---|
| 1 | `PERIODO`, `ESCENARIO`, `COD_CAMPUS_EDIFICIO`, `DIA`, `BLOQUE`, `CLASE`, `H`, `VALIDADO` | — | Igual que en §5.1 | — |
| 2 | `RANGO_DESDE` | string | Rango desde el que se acumula | `21-40` |
| 3 | `DEMANDA_ACUM_P10` | float | Demanda de ese tamaño o más, percentil 10 | `27,22` |
| 4 | `DEMANDA_ACUM_P50` | float | Demanda de ese tamaño o más, mediana | `36,52` |
| 5 | `DEMANDA_ACUM_P90` | float | Demanda de ese tamaño o más, percentil 90 | `47,16` |
| 6 | `ESPACIOS_ACUM` | float | Oferta efectiva de ese tamaño o más. Puede tener decimales | `37` |
| 7 | `PROB_SATURA_ACUM` | float | Probabilidad de que la demanda supere esa oferta | `0,50` |

### 5.3 · `PROGRAMACION_SINTETICA`

471.521 filas × 22 columnas. Solo escenario base.

| # | Columna | Tipo | Qué significa | Ejemplo |
|---:|---|---|---|---|
| 1 | `SECCION_SINTETICA` | int | Identificador dentro del período | `10208` |
| 2 | `COD_CAMPUS` | string | Campus de la sección | `C04` |
| 3 | `UNIDAD` | string | Facultad o departamento | `FACULTAD 10` |
| 4 | `MATERIA` | string | Materia de la sección de origen | `MT308` |
| 5 | `COMPONENTE` | string | Componente | `TEO` |
| 6 | `INSCRITOS_EST` | int | Inscritos estimados | `91` |
| 7 | `COD_CAMPUS_EDIFICIO` | string | Campus del edificio | `C04` |
| 8 | `CLASE` | string | Clase que necesita | `SALA` |
| 9 | `EDIFICIO` | string | Edificio asignado. Vacío si hay déficit (8,4 %) | `C04E` |
| 10 | `SALA` | string | Sala asignada. Vacía si hay déficit | `E403` |
| 11 | `CAPACIDAD_SALA` | float | Capacidad de esa sala. Vacía si hay déficit | `64` |
| 12 | `RANGO_DEMANDADO` | string | Tamaño que necesita | `60 o más` |
| 13 | `DIA` | string | Día | `MARTES` |
| 14 | `BLOQUE` | int | 1 a 19 | `3` |
| 15 | `PESO_SEMANAS` | float | Parte del semestre que dura, de 0 a 1 | `0,765` |
| 16 | `DEFICIT` | bool | `True` si no encontró sala | `True` |
| 17 | `SOBRECUPO` | bool | `True` si cabe por tolerancia, pero supera la capacidad | `False` |
| 18 | `PERIODO` | int | Período | `202910` |
| 19 | `PLAZO` | string | `corto` o `largo` | `largo` |
| 20 | `H` | int | Años desde la base | `3` |
| 21 | `VALIDADO` | bool | `False` solo en 2031 | `True` |
| 22 | `NIVEL` | string | `UG` o `AV` | `UG` |

### 5.4 · `VOLUMEN_PROYECTADO` y `SECCIONES_PROYECTADAS`

| Columna | Archivo | Qué significa | Ejemplo |
|---|---|---|---|
| `COD_CAMPUS`, `MATERIA`, `COMPONENTE`, `PERIODO`, `PLAZO`, `ESCENARIO`, `H`, `VALIDADO` | Volumen | Llaves | `C04`, `MT405`, `TEO` |
| `BASE` | Volumen | Período real de referencia | `202610` |
| `INSCRITOS_BASE` | Volumen | Inscritos del período base | `2680` |
| `RAZON` | Volumen | Crecimiento aplicado, entre 0,25 y 4 | `1,212` |
| `INSCRITOS_PROY` | Ambos | `INSCRITOS_BASE × RAZON` | `3.249,0` |
| `COD_CAMPUS`, `COMPONENTE`, `PERIODO`, `ESCENARIO`, `PLAZO` | Secciones | Llaves | `C04`, `TEO` |
| `SECCIONES_BASE` | Secciones | Secciones físicas en la base | `458` |
| `PERCENTIL` | Secciones | Percentil de tamaño que reproduce la base | `50` |
| `ESTANDAR` | Secciones | Tamaño de sección de ese percentil | `41` |
| `SECCIONES_PROY` | Secciones | `INSCRITOS_PROY ÷ ESTANDAR`, redondeado | `560` |

### 5.5 · `OFERTA_ESPACIOS` y `OFERTA_CELDA`

| Columna | Archivo | Qué significa | Ejemplo |
|---|---|---|---|
| `EDIFICIO`, `SALA`, `COD_CAMPUS_EDIFICIO` | Espacios | Identifican el espacio | `C04E`, `E301`, `C04` |
| `CATEGORIA_SALA`, `CLASE_PLANTA` | Espacios | Clasificación en la planta. Vacías si no está en ella (1,8 %) | `SALA` |
| `CAPACIDAD` | Espacios | Asientos registrados | `115` |
| `FUENTE` | Espacios | `planta` o cómo se completó si no estaba | `planta` |
| `CLASE_MAPA` | Espacios | `SALA`, `LABORATORIO` o `FUERA DEL MAPA` | `SALA` |
| `RANGO_CAPACIDAD` | Ambos | Rango del espacio | `60 o más` |
| `ACTIVO` | Espacios | Usado en los últimos 2 años | `True` |
| `N_ACTIVOS`, `N_OCIOSOS` | Celda | Espacios exactos de ese rango | `21`, `0` |
| `N_ACTIVOS_ACUM`, `N_OCIOSOS_ACUM` | Celda | Espacios de ese rango o más | `21`, `0` |
| `BLOQUE_MAX` | Celda | Último bloque que usa el campus | `19` |

### 5.6 · `PROG_HIST_NRC` y `PLANTILLAS_NRC`

| Columna | Archivo | Qué significa | Ejemplo |
|---|---|---|---|
| `PERIODO`, `NRC` | Ambos | Identifican la sección | `202610`, `5863` |
| `COD_ASIGNATURA`, `COD_SERIE` | Historia · plantillas | Asignatura: materia + curso, sin separador | `MT212G002` |
| `COD_MATERIA`, `COD_COMPONENTE`, `COD_CAMPUS`, `COD_CAMPUS_EDIFICIO` | Ambos | Materia, componente y campus | `MT212`, `TEO`, `C04` |
| `N_INSCRITOS` | Historia | Inscritos del NRC | `103` |
| `N_SESIONES_HORA`, `N_SESIONES_HORA_FISICAS` | Historia | Casilleros de la semana y los que están en espacio físico | `6` |
| `TIPO_PERIODO` | Historia | `UG 10/20` o `AV 05/15/25` | `UG 10/20` |
| `COD_ASIGNATURA_EURIBIA`, `EN_EURIBIA` | Historia | Código en Euribia y si lo tiene (79,5 %) | `MT212G002` |
| `COD_LC`, `N_NRC_LC`, `N_INSCRITOS_LC`, `PESO_LC` | Historia | Lista cruzada: código, NRC, inscritos totales y peso | `202205-C01-A3`, `2`, `33`, `0,5` |
| `COD_LIGA` | Historia | Liga: componentes cursados por un mismo grupo. No es lista cruzada ni sala compartida | `T1` |
| `DIA`, `BLOQUE`, `EDIFICIO`, `SALA` | Plantillas | Casillero | `LUNES`, `1`, `C04E`, `E301` |
| `CLASE_ESPACIO`, `RANGO_CAPACIDAD` | Plantillas | Clase y tamaño. Puede ser `FUERA DEL MAPA` o `SIN SALA` | `SALA` |
| `PESO_SEMANAS` | Plantillas | Parte del semestre que usa la sala | `1,0` |
| `PESO_OCUPACION` | Plantillas | `PESO_SEMANAS × PESO_LC` | `1,0` |
| `PESO_MAPA` | Plantillas | `PESO_OCUPACION × FACTOR_COMPARTICION` | `0,992` |

### 5.7 · Otros archivos

| Archivo | Columnas | Qué significan |
|---|---|---|
| `DEMANDA_SIN_SALA` | `PERIODO`, `COD_CAMPUS`, `SESIONES_HORA_SIN_SALA` | Sesiones reales sin sala, ponderadas |
| `UNIDAD_ACADEMICA` | `COD_MATERIA`, `DESC_MATERIA`, `DESC_FACULTAD`, `TIPO_UNIDAD`, `DESC_UNIDAD_ACADEMICA` | Materia y su facultad o departamento. `DESC_FACULTAD` vacía en departamentos (33,1 %) |
| `FACTOR_COMPARTICION` | `COD_CAMPUS_EDIFICIO`, `CLASE_ESPACIO`, `FACTOR_COMPARTICION` | Salas reales ÷ suma de pesos. Bajo 1 significa que se comparten |

---

## 6 · Cómo leer una fila 🧭

**Ejemplo**: Sede Sur, salas, martes 09:30, 1.er semestre de 2029, escenario base. En `OCUPACION_Y_DEFICIT`: `PERIODO = 202910`, `COD_CAMPUS_EDIFICIO = C04`, `CLASE = SALA`, `DIA = MARTES`, `BLOQUE = 3`, `ESCENARIO = base`.

| Columna | Valor | Lectura |
|---|---:|---|
| `OCUPACION_P50` | 41,8 | Lo más probable es necesitar unas 42 salas a la vez |
| `CAPACIDAD` | 39 | Sede Sur tiene 39 salas activas |
| `TASA_USO_P50` | 1,07 | Se necesitaría un 107 % de las salas |
| `OCUPACION_P10`, `OCUPACION_P90` | 30,3 y 60,3 | Lo probable es que necesite entre 30 y 60 |
| `PROB_SATURA_TAMANO` | 0,62 | **Crítica**: 62 % de probabilidad de que no alcance |
| `RANGO_CRITICO` | `0-20` | Faltan salas de cualquier tamaño |
| `DEFICIT_SALAS` | 9,8 | En la programación simulada, unas 10 secciones quedan sin sala |
| `VALIDADO` | `True` | Validado, con pocos pares a este horizonte |

**Conclusión que se puede sostener:** «Sede Sur presenta un riesgo alto de falta de salas los martes en la mañana hacia 2029». No se puede afirmar: «el martes 09:30 de 2029 faltarán exactamente 3 salas».

La demostración completa de esta celda está en [[DOCUMENTO_TECNICO_FUNCIONAL_MODELO_SOSTRATO]] §12.3.

---

## 7 · Lecturas correctas y trampas 🧭

| Lectura equivocada | Lectura correcta | Por qué |
|---|---|---|
| «Alerta significa que faltan salas» | Hay al menos 25 % de probabilidad de que falten | Es una probabilidad (§3.4) |
| «Sumo los P90 de todas las celdas» | La banda se lee celda por celda | Supondría que todas fallan a la vez |
| «Sumo bajo, base y alto» | Cada escenario se cuenta por separado | Son futuros alternativos |
| «`CAPACIDAD` son asientos» | Son espacios | En `OCUPACION_Y_DEFICIT`, 39 son 39 salas. Los asientos están en `OFERTA_ESPACIOS` |
| «El 62 % sale de comparar 41,8 con 39» | Solo si el tamaño crítico es «todos los tamaños» | En otras celdas sale de un rango específico |
| «Hay salas libres, entonces no hay problema» | Pueden no ser del tamaño necesario | C01, 2031: 44 de 85 laboratorios en uso y 62 % de alerta en los de 60 o más |
| «El rango de 2027 es estrecho, así que es más seguro» | Se construye distinto al de 2028–2031 | No son comparables |
| «2031 no se proyectó» | Se proyectó, pero su error no se pudo medir | `VALIDADO = False` |
| «La fila dice MT308: se dictará ese curso» | Es una sección anónima, sorteada | La programación no predice cursos |
| «Ese martes faltará la sala E403» | La sala es una realización del modelo | Sirve para ver el tipo de falta |
| «Campus 05 no tiene problemas» | No tiene alertas, pero sí clases sin sala: 7,8 % en 2031 | Mapa y programación miden cosas distintas |
| «17,4 % de los alumnos queda sin sala» | 17,4 % de los casilleros ponderados | La unidad no son personas |
| «Incluye toda la ocupación de la sala» | Falta el postgrado | Está fuera de alcance |

> [!warning] ⚠️ Salas y Semana no calzan directamente
> **Semana** muestra la mediana del modelo, ponderada por semanas. **Salas** muestra una realización, y cuenta como ocupada toda sala con alguna sección, aunque dure pocas semanas (decisión de diseño del 2026-11-05).
>
> En Sede Sur, martes 09:30 de 2029: Semana indica 41,8 salas necesarias. Salas indica 37 ocupadas y 10 sin sala, en total 47. Ponderado por semanas serían 34,2 y 9,8. Lo mismo ocurre con el 17,4 % de Panorama, que sí está ponderado.

> [!warning] ⚠️ Mapa y programación pueden contradecirse por campus
> Campus 02 tiene 9,2 % de clases sin sala en 2027 y ninguna alerta hasta 2029. Para decidir dónde y cuándo se usa el mapa; para ver qué tamaño falta, la programación.

> [!warning] ⚠️ Pendiente de validar con infraestructura
> Las alertas de laboratorios grandes de Campus 01 (47 en 2031) pueden ser gestión de grupos y no falta de espacio. La capacidad de la planta tampoco se ha contrastado.

---

## 8 · Consideraciones de Uso Funcional

- La **Dirección de Ingeniería de Datos no se responsabiliza** de entregar las reglas de negocio para los análisis a los que se aplique este entregable.
- El usuario que utilice de forma independiente este entregable es **responsable de evaluar la consistencia de los parámetros y supuestos** declarados en [[DOCUMENTO_TECNICO_FUNCIONAL_MODELO_SOSTRATO]] §14 y §18 en función de su objetivo particular.
- Ante cualquier duda que no esté resuelta en este documento, consultar a través del canal **Data Request** de la Dirección General de Control de Gestión y Análisis Institucional.

---

## 9 · Historial de versiones

| Versión | Fecha | Artefacto documentado | Cambios |
|---|---|---|---|
| 1.0 | 2026-11-05 | Commit `93dd390`, corrida del 2026-10-29 | Versión inicial del documento. |

---

*Documento generado el 2026-11-05 a partir de los parquet de `BBDD/` de la corrida del 2026-10-29. Filas, nulos y ejemplos se recalcularon sobre esos archivos. La descripción de las vistas corresponde a `Documentación/renuevo_ui/index.html` y a `DEMO_SOSTRATO.html`.*

---

> **Dirección de Ingeniería de Datos — Universidad Ficticia**
> Responsable: Diego Evans Pérez Paz
