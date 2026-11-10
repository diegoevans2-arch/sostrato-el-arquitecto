---
title: "Documento técnico-funcional · Pipeline de Sóstrato el Arquitecto"
tags:
  - nota-tecnica
  - pipeline
  - ocupacion-espacios
  - banner9
audiencias: [puente, ejecutivo, tecnico]
status: activo
type: documento-tecnico-funcional
project: sostrato
notebook: Notebooks + Scripts/PIPELINES.ipynb
entregable: BBDD/PLANTILLAS_NRC.parquet
version: "1.0"
fecha_creacion: 2026-11-05
ultima_actualizacion: 2026-11-05
owner: Dirección de Ingeniería de Datos
author: Diego Evans Pérez Paz
---

# Documento técnico-funcional · Pipeline de Sóstrato el Arquitecto

> [!info] 📌 Ficha
> **Artefacto**: `Notebooks + Scripts/PIPELINES.ipynb` (39 celdas, 22 de código)
> **Versión documentada**: commit `93dd390` · corrida en Jupyter del 2026-10-29
> **Función**: deja lista la programación real y la planta física, con una fila por `NRC × día × bloque × tramo de fechas`
> **Insumos**: Cirilo (programación real) · Euribia · Ariadna · planta física · bloques estándar · STVSUBJ
> **Salida**: `PLANTILLAS_NRC.parquet` — 2.236.891 × 18 · `OFERTA_ESPACIOS.parquet` — 4.944 × 10 · `PROG_HIST_NRC.parquet` — 170.452 × 18
> **Resultado**: 170.452 NRC de 25 períodos y 653 salas y laboratorios activos en 7 campus
> **Consumidor**: [[DOCUMENTO_TECNICO_FUNCIONAL_MODELO_SOSTRATO]]
> **Tiempo de corrida**: no quedó registrado en el notebook (§16.2)

**Cómo leer este documento.** Está escrito para quien usa los resultados y necesita saber de dónde vienen. Sigue la convención de la Guía Maestra DS: 👔 lectura ejecutiva · 🧭 puente entre negocio y técnica · 🔧 detalle técnico. §1–§2 bastan para entender qué hace el pipeline. §4–§8 explican cada etapa con sus reglas. §11 enseña a reconstruir una cifra con filas reales. §12–§23 son de consulta. Los términos y las columnas están en [[DICCIONARIO_USO_FUNCIONAL_SOSTRATO]]. Las cifras de §1 a §10 vienen de las salidas guardadas en el notebook; las de §11 se recalcularon sobre los parquet el 2026-11-05.

---

## 1 · Qué resuelve este pipeline 👔

La pregunta de negocio es **cómo se usan hoy las salas y laboratorios, y cuántos hay de verdad**, para tener una base confiable sobre la que proyectar la ocupación hasta 2031.

Antes de proyectar hay que resolver un problema previo: Cirilo muestra lo programado, pero contar filas no equivale a contar salas ocupadas. Una misma clase puede tener varios códigos de asignatura, una sala puede estar compartida y una sección puede usar una sala solo algunas semanas.

El pipeline responde en 5 pasos:

| # | Paso | Qué produce | Cifra de cierre |
|---:|---|---|---|
| 1 | **Actualizar** los períodos en curso | Programación real con 202620 y 202625 recientes | 19.051 NRC actualizados |
| 2 | **Unir** programación e insumos | Una fila por NRC, solo pregrado y Advance | 170.452 NRC |
| 3 | **Clasificar** los espacios | Qué sala cuenta, de qué clase y si está en uso | 653 espacios activos |
| 4 | **Medir** el uso real | Semana tipo de cada NRC, con su peso | 2.236.891 filas |
| 5 | **Controlar** | La oferta alcanza para lo que ya se programó | 0 de 6.985 celdas sobre 100 % |

> [!abstract] 👔 En una frase
> El pipeline no proyecta nada. Fotografía cómo se usan hoy los espacios, para que el modelo parta de una base real. Si esta foto está mal, toda la proyección hereda el error.

> [!danger] 🚨 La regla que no se puede violar
> **Un espacio ocupado se cuenta por sala: en cada sala × día × bloque vale `min(1, Σ PESO_SEMANAS)`.**
> Si se suman NRC, una sala compartida se cuenta dos veces. La razón entre salas ocupadas y suma de NRC es 0,893: sumar NRC infla la ocupación en cerca de un 12 %.

> [!warning] ⚠️ Lo que el pipeline deja fuera
> El postgrado, los espacios externos, los «espacio UNIV» y las salas virtuales. La ocupación real de una sala incluye al postgrado, así que las cifras de este producto no equivalen al uso total del edificio.

---

## 2 · Alcance funcional 🧭

### 2.1 · Universo

| Dimensión | Valor | Regla |
|---|---|---|
| Niveles | Pregrado (UG) y Advance (AV) | Períodos terminados en `10`, `20` (UG) y `05`, `15`, `25` (AV) |
| Períodos | 202205 a 202625 | 25 períodos en `PROG_HIST_NRC` |
| Campus con oferta | C01, C07, C04, C06, C02, C05 y C03 | `COD_CAMPUS_EDIFICIO`: el campus del edificio, no el del NRC |
| Espacios | Sala y laboratorio | `CLASE_MAPA` en `SALA`, `LABORATORIO` |
| **Grano de la salida principal** | `PERIODO × NRC × DIA × BLOQUE × tramo` | Una fila es un casillero de la semana tipo de un NRC |

### 2.2 · Qué queda fuera

| Exclusión | Regla | Dónde |
|---|---|---|
| Postgrado | Períodos terminados en `00` | Decisión D3 · §4 |
| Espacios externos, «espacio UNIV» y salas virtuales | `CLASE_MAPA = FUERA DEL MAPA` | Decisión D10 · §6 |
| Sesiones sin sala asignada | `CLASE_ESPACIO = SIN SALA` | Se informan en `DEMANDA_SIN_SALA` · §7 |
| Espacios sin uso en 2 años | `ACTIVO = False` | Se informan como capacidad ociosa · §6 |

### 2.3 · Glosario

| Término | Significado en este pipeline |
|---|---|
| **NRC** | Una sección programada en Banner, dentro de un período |
| **Asignatura** | `MATERIA` + `N_CURSO`, concatenados sin separador (`MT212G002`) |
| **Sesión-hora** | Fila de Cirilo: NRC × día × bloque × sala |
| **Lista cruzada (LC)** | Una misma cátedra con distintos códigos de asignatura. Es una sola clase y ocupa una sala |
| **Plantilla** | La semana tipo de un NRC: qué día y bloque usa, y en qué sala |
| **Campus real** | `COD_CAMPUS_EDIFICIO`, el campus donde está el edificio |
| **Espacio activo** | Sala o laboratorio usado al menos una vez en los últimos 2 años |

---

## 3 · Arquitectura y linaje de datos 🔧

```
┌─ FUENTES (6) ──────────────────────────────────────────────────────┐
│ Cirilo 2.643.862 filas · Euribia 22.142 y 78.125 filas             │
│ Ariadna 14.864 filas · STVSUBJ 1.118 filas                         │
│ Planta física · Bloques estándar                                   │
└──────────────────────────────┬─────────────────────────────────────┘
                               ▼
┌─ A · ACTUALIZACIÓN (§4) ───────────────────────────────────────────┐
│ Reemplaza 202620 y 202625 con una extracción reciente de Athena    │
│ Salida: 19.051 NRC convertidos al formato de Cirilo                │
└──────────────────────────────┬─────────────────────────────────────┘
                               ▼
┌─ B · EMPALME Y UNIDAD ACADÉMICA (§5) ──────────────────────────────┐
│ Una fila por NRC, listas cruzadas y facultad o departamento        │
│ Salida: PROG_HIST_NRC 170.452 · UNIDAD_ACADEMICA 154               │
└──────────────────────────────┬─────────────────────────────────────┘
                               ▼
┌─ C · OFERTA DE ESPACIOS (§6) ──────────────────────────────────────┐
│ Clase, rango de capacidad y si el espacio está activo              │
│ Salida: OFERTA_ESPACIOS 4.944 · 653 activos en el mapa             │
└──────────────────────────────┬─────────────────────────────────────┘
                               ▼
┌─ D · PLANTILLAS Y PESOS (§7) ──────────────────────────────────────┐
│ Semana tipo de cada NRC, semanas activas y sala compartida         │
│ Salida: PLANTILLAS_NRC 2.236.891 · FACTOR_COMPARTICION 14          │
└──────────────────────────────┬─────────────────────────────────────┘
                               ▼
┌─ E · CONTROLES (§8) ───────────────────────────────────────────────┐
│ Perfil horario medido en 202620 y oferta contra uso real           │
│ Cobertura del inventario 100 % · 0 de 6.985 celdas sobre 100 %     │
└──────────────────────────────┬─────────────────────────────────────┘
                               ▼
┌─ ENTREGA ──────────────────────────────────────────────────────────┐
│ Parquet en BBDD/ para VALIDACION_WALKFORWARD y Modelos             │
└────────────────────────────────────────────────────────────────────┘
```

### 3.1 · Insumos

| # | Insumo | Qué aporta | Origen | Volumen | En repo |
|---:|---|---|---|---:|:---:|
| 1 | `PROG_DETALLADA_PARA_HEATMAP_ACTUALIZADO.parquet` | Programación real por sesión-hora | Cirilo + §4 | 2.643.862 × 9 | ❌ |
| 2 | `PROG_DETALLADA_V2_202620_202625_20261026.csv` | Períodos en curso y listas cruzadas | Athena | 19.051 NRC | ❌ |
| 3 | `PROYECCION_INSCRITOS_2026_2027.csv` | Códigos de asignatura de Euribia | Euribia | 22.142 × 36 | ❌ |
| 4 | `SERIE_COMPLETA_REAL_VS_PROYECTADO.csv` | Historia de secciones de Euribia | Euribia | 78.125 × 35 | ❌ |
| 5 | `PROYECCION_MATRICULA_2026_2031_28092026.parquet` | Carrera y facultad | Ariadna | 14.864 × 18 | ❌ |
| 6 | `PLANTA_FISICA_PREPROCESADA.csv` | Capacidad y clase de cada espacio | `Heat-Map/BBDD` | — | ✅ |
| 7 | `BLOQUES_ESTANDAR_01122025.csv` | Hora de cada bloque | `Heat-Map/BBDD` | 19 bloques | ✅ |
| 8 | `stvsubj.csv` | Nombre de cada materia | `Heat-Map/BBDD` | 1.118 × 11 | ✅ |

> [!warning] ⚠️ Insumos fuera del repositorio
> Los insumos 3, 4 y 5 viven en la carpeta `Downloads` del equipo de desarrollo, y `BBDD/` está excluida de git. Las cifras se pueden demostrar con los parquet actuales, pero otra persona no puede regenerarlas solo con el repositorio.

### 3.2 · Queries y extracciones

**Entorno**: Athena · perfil institucional `perfil-athena-prod`. La extracción está apagada por defecto (`EXTRAER = False`).

**`QUERY_PROGRAMACION_DETALLADA_V2`** — programación por sección en el DL nuevo. Se filtra en memoria a `PERIODOS_FRESCOS`; la query del repositorio no se modifica.

### 3.3 · Código y orden de ejecución

| Orden | Sección del notebook | Qué hace | Salida |
|---:|---|---|---|
| 1 | §0 · Configuración | Rutas y constantes | — |
| 2 | §0b · Actualización | Convierte la extracción reciente al formato de Cirilo | `PROG_DETALLADA_PARA_HEATMAP_ACTUALIZADO` |
| 3 | §1 · Carga | Lee los insumos | — |
| 4 | §2 · Empalme y §2b · LC | Una fila por NRC, con sus listas cruzadas | `PROG_HIST_NRC` |
| 5 | §3 · Unidad académica | Facultad o departamento de cada materia | `UNIDAD_ACADEMICA` |
| 6 | §4–§5 · Regla de secciones | Regla histórica y su control | `REGLA_SECCIONES` |
| 7 | §6 · Oferta | Clasifica los espacios | `OFERTA_ESPACIOS`, `OFERTA_CELDA` |
| 8 | §7 · Perfil horario | Plantillas, factor y perfiles | `PLANTILLAS_NRC`, `FACTOR_COMPARTICION`, `PERFIL_*`, `DEMANDA_SIN_SALA` |
| 9 | §8–§9 · Controles | Validan el perfil y la oferta | `COMPARTICION` |

---

## 4 · Actualización de los períodos en curso 🧭

Cirilo guardaba una foto del 25-09, con 202620 y 202625 todavía incompletos. Esta etapa toma una extracción reciente y la convierte con las mismas reglas de Cirilo:

1. Descarta las filas sin horario.
2. Ajusta cada hora al bloque estándar más cercano.
3. Abre un registro por día y por bloque.
4. Agrega la clase y el campus del edificio desde la planta vigente.

| Prueba de la conversión (202610, crudo de julio) | Convertido | Cirilo |
|---|---:|---:|
| Filas | 231.893 | 232.187 |
| NRC | 15.482 | 15.460 |
| Combinaciones NRC × día × bloque × sala en común | 99,6 % | — |

> [!important] 🎯 No toca a Cirilo
> Escribe una copia en `BBDD/insumos/`. El parquet de Heat-Map queda intacto.

> [!warning] ⚠️ 202625 sigue con la inscripción abierta
> La extracción es del 2026-10-26, con la inscripción de ese período todavía en curso. Por eso el volumen AV de ese período puede quedar bajo (§17).

---

## 5 · Empalme y unidad académica 🧭

### 5.1 · Una fila por NRC

Cirilo tiene una fila por sesión-hora. Aquí pasa a una fila por NRC, solo con pregrado y Advance. Resultado: **170.452 NRC y 2.240.875 sesiones-hora**. Cada NRC recibe también el código con que Euribia proyecta esa asignatura (`COD_ASIGNATURA_EURIBIA`).

### 5.2 · Listas cruzadas

Una lista cruzada es una sola clase con varios códigos, así que ocupa una sala y suma sus inscritos.

```
PESO_LC        = 1 ÷ número de NRC de la lista
N_INSCRITOS_LC = Σ inscritos de todos los NRC de la lista
```

| Métrica | Valor |
|---|---:|
| NRC encontrados en la programación cruda | 100,0 % |
| NRC con lista cruzada | 7,6 % |
| Listas cruzadas distintas | 7.282 |

### 5.3 · Unidad académica

Permite leer los resultados por facultad.

1. Si la `MATERIA` coincide con un `cod_carrera` de Ariadna, se usa la **facultad** de esa carrera.
2. Si no coincide, se usa el **departamento**: la propia materia, descrita con STVSUBJ.

| Tipo | Materias | Sesiones-hora en sala o laboratorio |
|---|---:|---:|
| Facultad | 103 | 77,8 % |
| Departamento | 51 | 22,2 % |

### 5.4 · Regla de secciones

`REGLA_SECCIONES` calibra, por tipo de período y componente, qué columna de secciones de Euribia se acerca más a lo real. Su control fuera de muestra (202620 + 202625) da sesgo −2,3 % y WAPE 0,112 por período × campus.

> [!warning] ⚠️ El modelo vigente ya no la usa
> Desde la decisión D13, el número de secciones sale del estándar real de 2026. La regla queda como referencia histórica (§9.5).

---

## 6 · Oferta de espacios 🧭

### 6.1 · Qué espacio cuenta

| Regla | Detalle |
|---|---|
| **Solo sala y laboratorio** | Externos, «espacio UNIV» y salas virtuales quedan fuera |
| **Sala en uso que no está en la planta** | Toma la clase más común de su edificio |
| **Edificio que tampoco está en la planta** | Se decide por el componente más dictado: `TEO` → sala; `LAB`, `SIM`, `SSA` → laboratorio; el resto queda fuera |
| **Activo** | Usado al menos una vez en los últimos 2 años |
| **Ocioso** | Sin uso en 2 años: no entra en la oferta y se informa aparte |

| Métrica | Valor |
|---|---:|
| Espacios en total | 4.944 |
| Sala o laboratorio | 702 |
| **Activos** | **653** |
| Ociosos | 49 |

| Campus | Salas activas | Laboratorios activos | Total |
|---|---:|---:|---:|
| C01 · Campus 01 | 112 | 85 | 197 |
| C02 · Campus 02 | 71 | 55 | 126 |
| C05 · Campus 05 | 88 | 27 | 115 |
| C03 · Sede Austral | 62 | 30 | 92 |
| C04 · Sede Sur | 39 | 32 | 71 |
| C06 · Campus 06 | 29 | 7 | 36 |
| C07 · Campus 07 | 8 | 8 | 16 |
| **Total** | **409** | **244** | **653** |

### 6.2 · Rango de capacidad

Cada espacio cae en un rango: 0-20, 21-40, 41-60 o 60 o más. La oferta se acumula hacia arriba, porque una sala grande sirve para una sección chica, pero no al revés. Sede Sur tiene 2, 9, 7 y 21 salas por rango, es decir, 39 salas sirven desde 0-20 y solo 21 sirven para 60 o más.

> [!warning] ⚠️ La capacidad registrada está por validar
> La capacidad sale de la planta física y no se contrastó con infraestructura. Es la base de todas las alertas por tamaño (§17).

---

## 7 · Plantillas y pesos 🧭

### 7.1 · La semana tipo de cada NRC

Cada NRC histórico queda como una fila por día × bloque × tramo de fechas. De ahí salen tres pesos, que se aplican en cadena:

```
PESO_SEMANAS   = semanas del tramo ÷ semanas del período  (tope 1)
PESO_OCUPACION = PESO_SEMANAS × PESO_LC
PESO_MAPA      = PESO_OCUPACION × FACTOR_COMPARTICION
```

| Peso | Qué corrige |
|---|---|
| `PESO_SEMANAS` | Una sección que usa la sala solo unas semanas no cuenta como semestre completo |
| `PESO_LC` | Una lista cruzada cuenta una sola vez |
| `FACTOR_COMPARTICION` | Salas compartidas que desde 2025 casi no se codifican como lista cruzada |

| Clase del espacio | % del peso total |
|---|---:|
| Sala | 48,7 % |
| Laboratorio | 21,4 % |
| Fuera del mapa | 27,5 % |
| Sin sala | 2,4 % |

### 7.2 · Factor de compartición

```
FACTOR_COMPARTICION = salas reales ÷ Σ PESO_OCUPACION   (últimos 2 años, por campus × clase)
```

| Campus | Laboratorio | Sala |
|---|---:|---:|
| C01 | 0,668 | 0,981 |
| C02 | 0,661 | 0,970 |
| C05 | 0,934 | 0,988 |
| C03 | 0,950 | 0,975 |
| C04 | 0,826 | 0,992 |
| C06 | 1,000 | 0,989 |
| C07 | 0,998 | 0,979 |
| **Todos** | **0,743** | **0,981** |

Un factor de 0,66 significa que los laboratorios de ese campus se comparten mucho: 100 secciones ocupan cerca de 66 laboratorios.

### 7.3 · Demanda sin sala

Las sesiones sin sala asignada no entran al mapa, porque inventarles una sala inflaría la ocupación. Se informan en `DEMANDA_SIN_SALA`. En 202610 pesan 1.027 sesiones-hora en C04, 411 en C01, 26 en C02, 15 en C03 y 8 en C06.

### 7.4 · Perfil horario

`PERFIL_HORARIO` y `PERFIL_RESUMEN` describen cómo se dicta cada serie: días, bloques, semanas activas y estabilidad. Solo el 32,9 % de las 18.602 series tiene perfil propio (3 NRC o más), y la inestabilidad día × bloque tiene mediana 0,762: el horario de una misma asignatura cambia bastante de un año a otro.

> [!tip] 💡 Por qué importa este hallazgo
> Esta inestabilidad explica por qué el modelo vigente no intenta predecir qué asignatura se dicta en cada bloque. Trabaja con secciones físicas anónimas ([[DOCUMENTO_TECNICO_FUNCIONAL_MODELO_SOSTRATO]] §5).

---

## 8 · Controles del pipeline 🧭

### 8.1 · Validación aislada del perfil (202620)

Ubica los NRC reales de 202620 con plantillas sorteadas de la ventana anterior, 100 veces, y compara contra lo real.

| Métrica | Sin corrección | Solo LC | LC + factor |
|---|---:|---:|---:|
| WAPE por celda | 0,294 | 0,281 | **0,186** |
| WAPE campus × día × bloque | 0,238 | 0,218 | **0,129** |
| Sesgo total | +19,9 % | +17,3 % | **+4,4 %** |
| Correlación con el mapa real | 0,943 | 0,943 | **0,974** |
| Cobertura P10–P90 | 59,2 % | 60,1 % | **64,3 %** |

### 8.2 · La oferta alcanza para lo ya programado

| Control | Resultado |
|---|---:|
| Sesiones reales de los últimos 2 años que caen en un espacio del inventario | 100,00 % |
| Celdas con uso sobre 100 % | 0 de 6.985 |
| Salas ocupadas ÷ suma de NRC | 0,893 |

---

## 9 · Grano, cobertura y trazabilidad 🔧🧭

### 9.1 · Grano

```
grano PROG_HIST_NRC  = PERIODO × NRC
grano PLANTILLAS_NRC = PERIODO × NRC × DIA × BLOQUE × tramo de fechas
```

### 9.2 · Filas por etapa

| Etapa | Filas | Δ |
|---|---:|---|
| Cirilo actualizado (sesión-hora) | 2.643.862 | — |
| Sesiones-hora de pregrado y AV | 2.240.875 | Sale el postgrado y otros niveles |
| `PLANTILLAS_NRC` | 2.236.891 | Se consolidan filas al armar la semana tipo |
| `PROG_HIST_NRC` | 170.452 | Una fila por NRC |

### 9.3 · Cobertura y nulos

| Familia de columnas | Nulos | Interpretación |
|---|---:|---|
| Llaves, inscritos y campus | 0,0 % | Íntegras |
| `COD_ASIGNATURA_EURIBIA` | 20,5 % | Asignaturas que Euribia no proyecta. No es un error |
| `COD_LC` | 92,4 % | NRC sin lista cruzada. El 7,6 % restante sí la tiene |
| `COD_LIGA` | 43,4 % | NRC sin liga |

> [!warning] ⚠️ Euribia cubre menos en lo reciente
> La parte de las sesiones-hora con código en Euribia baja de 92,1 % en 202210 a 79,0 % en 202610 y 63,1 % en 202620. No afecta al mapa, que trabaja con secciones físicas, pero sí a cualquier análisis por asignatura.

### 9.4 · Trazabilidad al origen

Desde una fila de `PLANTILLAS_NRC`, `PERIODO` + `NRC` lleva al NRC en Cirilo y en Banner. `EDIFICIO` + `SALA` llevan a la planta física.

### 9.5 · Consumo aguas abajo

| Consumidor | Qué usa | Para qué |
|---|---|---|
| `Modelos.ipynb` | `PROG_HIST_NRC`, `PLANTILLAS_NRC`, `OFERTA_ESPACIOS`, `UNIDAD_ACADEMICA` | Mapa real, estratos y oferta |
| `VALIDACION_WALKFORWARD.ipynb` | Los mismos | Banco de validación |
| Nadie en el modelo vigente | `REGLA_SECCIONES`, `PERFIL_HORARIO`, `PERFIL_RESUMEN`, `OFERTA_CELDA` | Referencia y análisis |

---

## 10 · Reglas de negocio que implementa 🧭

| Regla | Enunciado | Dónde vive |
|---|---|---|
| **D1** | La ocupación se carga al campus del edificio, no al del NRC | §2 |
| **D3** | Solo pregrado y Advance | §5 |
| **D7** | Materia = carrera → facultad; si no, departamento | §5.3 |
| **D9** | Cada NRC se guarda como semana tipo real, con peso por semanas | §7.1 |
| **D10** | Solo sala y laboratorio; la oferta es el inventario usado en 2 años | §6 |
| **D11** | Una lista cruzada cuenta una sala y suma inscritos; factor por campus × clase | §5.2, §7.2 |

---

## 11 · Cómo demostrar un cálculo 🧭

Se trabaja con los parquet de `BBDD/`, ubicando las filas por su llave.

### 11.1 · Qué se demuestra con la salida y qué requiere los insumos

| Factor | Columnas | ¿Se demuestra con la salida? | Para reconstruirlo desde el origen |
|---|---|---|---|
| Inscritos de un NRC | `N_INSCRITOS` | Sí | Cirilo |
| Pesos | `PESO_SEMANAS`, `PESO_LC`, `PESO_MAPA` | Sí | Fechas del NRC |
| Clase de un espacio | `CLASE_MAPA`, `FUENTE` | Sí | Planta física |
| Espacio activo | `ACTIVO` | Parcial | Uso de los últimos 2 años en `PLANTILLAS_NRC` |

### 11.2 · Procedimiento para cualquier fila

| Paso | Qué mirar | Cómo se verifica |
|---:|---|---|
| 1 | Ubicar el NRC | Filtrar `PROG_HIST_NRC` por `PERIODO` y `NRC` |
| 2 | Ver su semana | Filtrar `PLANTILLAS_NRC` por las mismas columnas |
| 3 | Verificar el peso | `PESO_MAPA` debe dar `PESO_SEMANAS × PESO_LC × factor` |
| 4 | Contar la sala | En cada sala × día × bloque, `min(1, Σ PESO_SEMANAS)` |

### 11.3 · Demostración completa: una cátedra de Enfermería en Sede Sur

**Fila**: `PERIODO = 202610` · `NRC = 5863`. Se eligió por ser la cátedra más grande de Sede Sur en ese período.

**Paso 1 · El NRC**

| Qué | Valor | Columna |
|---|---:|---|
| Asignatura | `MT212G002` | `COD_ASIGNATURA` |
| Componente | `TEO` | `COD_COMPONENTE` |
| Inscritos | 103 | `N_INSCRITOS` |
| Casilleros en la semana | 6 | `N_SESIONES_HORA` |
| Lista cruzada | no tiene | `COD_LC` vacío, `PESO_LC = 1` |

**Paso 2 · Su semana**

Usa la sala `E301` del edificio `C04E`, los lunes en los bloques 1, 2, 11, 12, 13 y 14. Dura todo el semestre, así que `PESO_SEMANAS = 1`.

**Paso 3 · El peso en el mapa**

```
PESO_MAPA = PESO_SEMANAS × PESO_LC × FACTOR_COMPARTICION
          = 1 × 1 × 0,992                      (C04 · SALA)
          = 0,992                              (columna PESO_MAPA)
```

**Paso 4 · De la fila a la celda**

| Nivel | Cálculo | Valor |
|---|---|---:|
| Una sala con una sección de todo el semestre | `min(1; 1,000)` | 1,00 |
| Sala `CECS` con secciones parciales | Suma sus `PESO_SEMANAS`; sobre 1 queda en 1 | Máx. 1,00 |
| Celda C04 · sala · martes · bloque 3 · 202610 | 53 filas, 44 NRC y 38 salas | **37,05 salas** |

La celda tiene 39 salas activas y usa 37,05. Ese valor es el punto de partida del modelo para esa celda.

**Paso 5 · Variante con lista cruzada**

`202205 · NRC 1739 · MT2310008 · C01`: tiene 25 inscritos, pero pertenece a la lista `202205-C01-A3`, con 2 NRC y 33 inscritos. Por eso `PESO_LC = 0,5` y `N_INSCRITOS_LC = 33`: la clase real es de 33 personas y ocupa una sola sala.

### 11.4 · Preguntas frecuentes de cálculo

**¿Por qué los inscritos de un NRC no son el tamaño de la clase?**
Porque el NRC puede pertenecer a una lista cruzada. El tamaño real está en `N_INSCRITOS_LC`, como en el ejemplo con 25 y 33 (§11.3).

**¿Por qué Sede Sur tiene 39 salas y no todas las de la planta?**
Porque solo cuentan las salas usadas en los últimos 2 años y clasificadas como sala (§6.1).

**¿Por qué suman más de lo real los NRC de una celda?**
Porque varios NRC pueden compartir sala. En C04, 44 NRC ocupan 38 salas en esa celda. Hay que contar por sala (§1).

**¿Una sala usada una semana cuenta como ocupada?**
Para el mapa real, cuenta según sus semanas: una sección de 17 % del semestre aporta 0,17. La vista Salas de la simulación es distinta: marca ocupada cualquier sala con una sección (ver [[DICCIONARIO_USO_FUNCIONAL_SOSTRATO]] §7).

**¿Por qué no están las horas de postgrado?**
Por decisión D3: el alcance es pregrado y Advance. Eso significa que una sala puede estar más ocupada de lo que muestra el producto ([[DOCUMENTO_TECNICO_FUNCIONAL_MODELO_SOSTRATO]] §18).

**¿Qué significa un laboratorio con factor 0,66?**
Que las secciones de ese campus comparten mucho sus laboratorios: 100 secciones ocupan cerca de 66 (§7.2).

**¿Se perdió información al actualizar 202620?**
La conversión se probó contra lo que Cirilo había procesado: −0,13 % de filas y 99,6 % de combinaciones en común (§4).

**¿Por qué hay salas en el mapa que no están en la planta?**
Porque se usan en la programación real. Heredan la clase de su edificio o la del componente (§6.1). La columna `FUENTE` lo indica.

---

## 12 · Especificación del entregable 🔧

| Archivo | Filas | Columnas | Peso | Consumidor |
|---|---:|---:|---:|---|
| `PLANTILLAS_NRC.parquet` | 2.236.891 | 18 | 22,4 MB | Modelo y banco |
| `PROG_HIST_NRC.parquet` | 170.452 | 18 | 1,7 MB | Modelo y banco |
| `OFERTA_ESPACIOS.parquet` | 4.944 | 10 | < 0,1 MB | Modelo y banco |
| `UNIDAD_ACADEMICA.parquet` | 154 | 5 | < 0,1 MB | Modelo y banco |
| `FACTOR_COMPARTICION.parquet` | 14 | 3 | < 0,1 MB | Referencia |
| `DEMANDA_SIN_SALA.parquet` | 117 | 3 | < 0,1 MB | Análisis |
| `OFERTA_CELDA.parquet` | 48 | 8 | < 0,1 MB | Análisis |
| `COMPARTICION.parquet` | 14 | 3 | < 0,1 MB | Control |
| `REGLA_SECCIONES.parquet` | 16 | 7 | < 0,1 MB | Referencia |
| `PERFIL_HORARIO.parquet` | 194.597 | 9 | 0,6 MB | Análisis |
| `PERFIL_RESUMEN.parquet` | 18.602 | 10 | 0,2 MB | Análisis |

Las columnas están en [[DICCIONARIO_USO_FUNCIONAL_SOSTRATO]] §5.

---

## 13 · Parámetros y flags 🔧

| Parámetro | Valor vigente | Efecto |
|---|---|---|
| `EXTRAER` | `False` | `True` vuelve a consultar Athena |
| `PERIODOS_FRESCOS` | `202620`, `202625` | Períodos que se reemplazan |
| `MIN_FILAS_FACTOR` | `30` | Con menos filas, `REGLA_SECCIONES` usa el factor del tipo de período |
| `MIN_NRC_PERFIL` | `3` | Mínimo de NRC para tener perfil propio |
| Ventana de actividad | 2 años | Define qué espacio está activo |

---

## 14 · Controles, guards y validaciones 🔧🧭

| Control | Condición | Resultado 2026-10-29 |
|---|---|---|
| Regla de secciones fuera de muestra | Sesgo y WAPE contra las cifras de referencia | OK: −0,023 y 0,112 |
| Cobertura del inventario | Toda sesión real cae en un espacio | 100,00 % |
| Uso real sobre 100 % | Ninguna celda sobre 100 % | 0 de 6.985 |
| Búsqueda de LC | Todo NRC está en la programación cruda | 100,0 % |
| Descripción de unidades | Toda materia tiene nombre | 0 sin descripción |

El notebook se puede volver a correr sin dañar nada: reescribe las salidas de `BBDD/` y no toca el parquet de Cirilo.

---

## 15 · Resultados de referencia 📊

Cifras contra las que se comparará la próxima corrida.

| Salida | Medida | Valor |
|---|---|---:|
| `PROG_HIST_NRC` | NRC | 170.452 |
| `PROG_HIST_NRC` | Sesiones-hora | 2.240.875 |
| `PLANTILLAS_NRC` | Filas | 2.236.891 |
| `OFERTA_ESPACIOS` | Espacios activos en el mapa | 653 |
| `UNIDAD_ACADEMICA` | Materias | 154 |
| `FACTOR_COMPARTICION` | Laboratorio · sala | 0,743 · 0,981 |

| Período | NRC | Parte de las sesiones-hora con código en Euribia |
|---|---:|---:|
| 202610 | 15.460 | 79,0 % |
| 202620 | 16.835 | 63,1 % |
| 202605 | 2.262 | 67,1 % |
| 202615 | 2.258 | 66,3 % |
| 202625 | 2.216 | 60,0 % |

---

## 16 · Volumetría y performance 🔧🧭

### 16.1 · Volumen

| Objeto | Filas | Columnas | Peso |
|---|---:|---:|---:|
| Cirilo actualizado | 2.643.862 | 9 | 69,2 MB |
| Extracción de Athena | 19.051 NRC | — | 60,9 MB |
| `PLANTILLAS_NRC` | 2.236.891 | 18 | 22,4 MB |

### 16.2 · Tiempo de corrida

No medido: el notebook no guarda tiempos por celda. Conviene cronometrar la próxima corrida.

### 16.3 · Memoria

No medida en esta versión.

---

## 17 · Supuestos, limitaciones y riesgos ⚠️

| # | Supuesto, limitación o riesgo | Impacto | Estado |
|---:|---|---|---|
| 1 | **Capacidad registrada en la planta** | Es la base de la tolerancia y de la alerta por tamaño | A validar con infraestructura |
| 2 | **Postgrado fuera** | El uso real de cada sala es mayor que el mostrado | Decisión de diseño (D3) |
| 3 | **Salas compartidas no codificadas** | Se corrigen con un factor por campus × clase, no sala por sala | Aceptado |
| 4 | **202625 con la inscripción abierta** | La base de AV de ese período queda baja | Repetir con el período cerrado |
| 5 | **Horario inestable entre años** | Mediana 0,762: no se puede proyectar el horario de una asignatura | Considerado en el modelo |
| 6 | **Insumos fuera del repositorio** | No se puede regenerar sin la carpeta `Downloads` | Pendiente |

> [!warning] ⚠️ Lo que este pipeline no cubre
> No dice qué edificios se construirán ni cómo cambiará la forma de programar. Tampoco mide si la sala estuvo físicamente ocupada: mide lo programado.

---

## 18 · Pendientes de negocio y de datos 🧭

| # | Pendiente | Tipo | Qué destraba |
|---|---|---|---|
| P-01 | Validar la capacidad de la planta con infraestructura (C01, C04, C06) | Datos | Alertas por tamaño |
| P-02 | Validar si los laboratorios de 60 o más de C01 se dividen en grupos | Negocio | Alertas de laboratorios en C01 |
| P-03 | Repetir la extracción de 202625 con la inscripción cerrada | Datos | Base de AV |
| P-04 | Evaluar la planta más reciente (`ESPACIOS_FISICOS_20261030.csv`), que este pipeline todavía no lee | Datos | Oferta vigente |
| P-05 | Confirmar el significado de los componentes `AYU`, `GRU`, `OCS` y `SSA` | Negocio | Glosario |

---

## 19 · Observaciones del levantamiento 🔎

> [!important] 🎯 Alcance
> Revisión del notebook y sus salidas al 2026-11-05. No se modificó ningún archivo del pipeline.

| # | Hallazgo | Evidencia | Impacto | Sugerencia |
|---|---|---|---|---|
| O-01 | **El informe técnico dice 21 bloques por día** | Los datos tienen 20 (`BLOQUE` 0 a 19), y el estándar tiene 19 más el «antes de las 08:00» | Bajo: texto | Corregir el informe |
| O-02 | **La portada del notebook describe solo las secciones 0 a 5** | Celda 0 de `PIPELINES.ipynb` | Bajo: orientación | Completar la tabla |
| O-03 | **Hay salidas sin consumidor en el modelo vigente** | §9.5 | Bajo: mantención | Marcarlas como históricas |

---

## 20 · Cómo re-ejecutar 🔧

**Requisitos**

1. Python de Anaconda: `AppData\Local\anaconda3`.
2. Insumos de Euribia y Ariadna en `Downloads`, con los nombres de §3.1.
3. Sesión institucional de Athena, solo si se refresca la extracción.

| Paso | Acción | Cuándo |
|---:|---|---|
| 1 | Activar `EXTRAER = True` y ajustar `PERIODOS_FRESCOS` | Si hay un período nuevo |
| 2 | Ejecutar `PIPELINES.ipynb` de principio a fin | Siempre |
| 3 | Revisar §14 de este documento | Siempre |
| 4 | Ejecutar `VALIDACION_WALKFORWARD.ipynb` y luego `Modelos.ipynb` | Siempre que cambie la base |

> [!warning] ⚠️ El orden importa
> `Modelos.ipynb` lee del banco el modelo adoptado, los pesos y la banda. Correrlo antes que el banco deja una proyección con parámetros viejos.

---

## 21 · Documentos relacionados

| Documento | Qué aporta | Vigencia |
|---|---|---|
| [[DOCUMENTO_TECNICO_FUNCIONAL_MODELO_SOSTRATO]] | El modelo que usa estas salidas | Vigente |
| [[DICCIONARIO_USO_FUNCIONAL_SOSTRATO]] | Términos, columnas y lectura de resultados | Vigente |
| [[INFORME_EJECUTIVO_ALERTAS_2027_2031]] | Resultados para directivos | Vigente |
| [[INFORME_TECNICO_RESULTADOS_ALERTAS_2027_2031]] | Resultados y método | Vigente |
| [[SOSTRATO_IDEA_Y_ROADMAP]] | Decisiones D1 a D19 | Vigente |
| [[DIAGNOSTICO_EMPALME]] | Mediciones de cada decisión | Vigente |
| [[SOSTRATO_flujo_pipeline-modelo-detalle_2026-10-30.excalidraw]] | Diagrama de flujo detallado | Vigente |

---

## 22 · Consideraciones de Uso Funcional

- La **Dirección de Ingeniería de Datos no se responsabiliza** de entregar las reglas de negocio para los análisis a los que se aplique este entregable.
- El usuario que utilice de forma independiente este entregable es **responsable de evaluar la consistencia de los parámetros y supuestos** declarados en §13 y §17 en función de su objetivo particular.
- Ante cualquier duda que no esté resuelta en este documento, consultar a través del canal **Data Request** de la Dirección General de Control de Gestión y Análisis Institucional.

---

## 23 · Historial de versiones

| Versión | Fecha | Artefacto documentado | Cambios |
|---|---|---|---|
| 1.0 | 2026-11-05 | Commit `93dd390`, corrida del 2026-10-29 | Versión inicial del documento. |

---

*Documento generado el 2026-11-05 a partir de la corrida del 2026-10-29 de `PIPELINES.ipynb` y de los parquet de `BBDD/`. La demostración de §11 y los conteos de §6 y §12 se recalcularon sobre esos parquet. Las cifras de §4 y §8 provienen de las salidas guardadas en el notebook.*

---

> **Dirección de Ingeniería de Datos — Universidad Ficticia**
> Responsable: Diego Evans Pérez Paz
