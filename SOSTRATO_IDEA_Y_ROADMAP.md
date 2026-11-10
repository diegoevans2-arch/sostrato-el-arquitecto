---
date: 2026-10-22
tags:
  - idea
  - roadmap
  - data-product
  - mapa-de-calor
  - ocupacion-espacios
  - programacion-academica
  - proyeccion-demanda
  - cirilo
  - euribia
  - ariadna
status: draft
type: propuesta
project: sostrato
owner: Dirección de Ingeniería de Datos
author: Diego Evans Pérez Paz
version: "0.1"
fecha_creacion: 2026-10-22
ultima_actualizacion: 2026-10-22
---

# Sóstrato el Arquitecto · Mapa de calor de la programación académica proyectada

> **Idea en una línea:** usar lo que ya proyectan **Ariadna** (cuántos estudiantes) y **Euribia** (cuántos inscritos y secciones por asignatura) para *fabricar* una programación académica futura, y pasarla por el motor de **Cirilo** (ocupación por día × bloque × espacio) para ver, antes de que ocurra, **dónde y cuándo la infraestructura se queda corta o sobra**, período a período, hasta 2031.

> [!note] Nombre y horizonte
> **Sóstrato el Arquitecto** (renombrado el 29-10-2026; antes «Cirilo 2049», y antes «Cirilo 2031»). Sóstrato de Cnido construyó el faro de Alejandría y, según la tradición, grabó su nombre bajo el yeso de la dedicatoria para que apareciera con los siglos: una obra pensada para el futuro, como esta proyección de la infraestructura. «Cirilo» sigue siendo el nombre del producto de programación real que alimenta al proyecto. El horizonte de proyección es **2031**, el de Ariadna.

> [!info] Estado
> Documento de **idea y roadmap** (v0.1). No hay código ni datos nuevos todavía. Las cifras citadas vienen de la documentación vigente de cada producto y se indican con su fuente; lo marcado como **hipótesis** se valida en la fase 0.

---

## 1. Los tres productos que se integran

| Producto | Carpeta | Qué entrega hoy | Grano | Horizonte |
|---|---|---|---|---|
| **Ariadna** · Proyección de Matrícula | `Proyección de Demanda Estudiantes/` | Estudiantes por carrera-campus, con banda baja–alta (ETS + tendencias) | carrera × campus × año | 2026–2031 (total 2031: 69.595; rango 59.818–79.374) |
| **Euribia** · Proyección de Demanda de Asignaturas | `Proyección de Demanda Asignaturas/` | Inscritos P10/P50/P90 por asignatura y **secciones** por escenario de percentil | período × asignatura × componente × campus | 1–2 períodos (el horizonte 2 degrada +16,5 %) |
| **Cirilo** · Ocupación de espacios | `Heat-Map/` | Mapa de calor y sunburst de ocupación real; dataset aperturado a sesión-hora × día × sala | NRC × día × bloque × sala | Histórico (lo que ya se programó) |

> [!note] Sobre los nombres
> El deck de Euribia está en `Proyección de Demanda Asignaturas/Documentación/EURIBIA_Iniciativa-de-Datos_2026-09.pptx`; la carpeta de Markov guarda una copia de referencia (`_REFERENCIA_EURIBIA_…`). Cirilo es el nombre del dashboard Dash de `Heat-Map/dash_app` («Cirilo · Ocupación de espacios académicos»).

**Lo que ninguno responde por sí solo:** *¿cabe la programación de 2028 (o 2031) en la planta física que tenemos?* Ariadna sabe cuántos vienen, Euribia sabe qué van a tomar y cuántas secciones abrir, Cirilo sabe cómo se ve la ocupación… pero solo de lo que ya pasó.

---

## 2. La idea

```
 ARIADNA                  EURIBIA                    PROGRAMACIÓN SINTÉTICA          CIRILO
 estudiantes      ──►     inscritos y        ──►     secciones repartidas      ──►   mapa de calor
 carrera×campus×año       secciones por              en día × bloque × tipo          proyectado vs
 (nivel, largo plazo)     asignatura×comp×campus     de espacio (perfil horario      capacidad de la
                          (distribución, corto)      histórico de cada asignatura)   planta física
```

### 2.1 Tres piezas nuevas, el resto se reutiliza

1. **Puente de nivel Ariadna → Euribia (largo plazo).** Euribia es buena en 1–2 períodos; para llegar a 2031 no se encadenan predicciones (la degradación se acumula), sino que se usa Ariadna como **ancla de nivel**: el crecimiento de estudiantes por carrera-campus se traspasa a las asignaturas según el **mix de carreras** de sus inscritos históricos. Euribia aporta la distribución fina; Ariadna, el tamaño total.
2. **Generador de programación sintética.** Toma las secciones proyectadas (Euribia F7e: estándar + escenarios por percentil) y las reparte en el horario con el **perfil horario** de cada asignatura-componente-campus: horas semanales por sección, días y bloques en que suele dictarse, tipo de espacio que usa (sala, laboratorio, taller…) y rango de capacidad. Es la pieza central y la más nueva.
3. **Cirilo en modo proyección.** El mismo pipeline de ocupación (bloques estándar, planta física vigente, clasificación de espacios), pero alimentado con la programación sintética y con una métrica distinta: en vez de *qué sala está ocupada*, **cuántos espacios de cada tipo se necesitan por bloque vs cuántos hay**.

### 2.2 Qué muestra el mapa de calor

No es posible saber en qué sala exacta se dictará una sección de 2029, así que el mapa no baja a sala. El grano propuesto es:

```
campus × día × bloque × tipo de espacio × rango de capacidad × período (× escenario)
```

Con tres métricas por celda:

| Métrica | Fórmula | Lectura |
|---|---|---|
| **Tasa de uso de espacios** | espacios requeridos en el bloque ÷ espacios disponibles del tipo y rango | > 100 % = **déficit**: no cabe la programación |
| **Llenado esperado** | inscritos proyectados ÷ capacidad de los espacios usados | baja = salas grandes para secciones chicas |
| **Holgura / déficit absoluto** | espacios disponibles − requeridos | cuántas salas faltan o sobran en ese bloque |

Y tres escenarios, que heredan las bandas de los productos de origen: **bajo** (Ariadna bajo + P10/P50), **base** (Ariadna base + P50) y **alto** (Ariadna alto + P90). El mapa de calor de un bloque crítico se lee entonces como «en el escenario base, el martes 10:00 en campus X faltan 6 laboratorios desde 2028».

### 2.3 Preguntas de negocio que abre

- ¿Qué campus y qué franjas se saturan primero, y en qué año?
- ¿El cuello de botella es de **cantidad** de espacios o de **tipo** (faltan laboratorios, sobran salas)?
- ¿Cuánta capacidad se libera si se mueve programación de bloques punta a bloques valle?
- ¿Cuánto cambia el panorama entre escenario bajo y alto? (riesgo de invertir de más o de menos)
- Insumo para planificación de infraestructura, apertura de jornadas y — en una fase posterior — para la capa económica de Euribia (costo de la sala bloqueada y del alumno sin cupo).

---

## 3. Supuestos y riesgos conocidos

Heredados de los productos de origen (fuente entre paréntesis) y propios de la idea:

| # | Riesgo | Impacto en el mapa | Cómo se aborda |
|---|---|---|---|
| R1 | **Asignaturas nuevas** sin historia: 19–29 % de las series del período destino (Euribia, resumen ejecutivo) | El mapa subestima la ocupación futura | Bolsa de «demanda no asignada» por campus, repartida con el perfil horario promedio del componente; se muestra aparte |
| R2 | **Conversión a secciones** con techo 65,8 % de acierto (Euribia) | Error en el número de espacios requeridos | Usar los escenarios por percentil y reportar banda, no punto |
| R3 | **Postgrado (`TT 00`) fuera** de Euribia | Falta ocupación, sobre todo en vespertino y sábado | Declararlo como exclusión en v1; incorporarlo cuando Euribia lo haga |
| R4 | **Planta física futura desconocida** (edificios nuevos, cierres) | La oferta del denominador es la de hoy | La planta vigente es el escenario por defecto; se permite cargar escenarios de oferta |
| R5 | `OCUPACIÓN_SALA` de Cirilo está **truncada a 1** e imputa capacidad (nota técnica del pipeline) | El histórico de llenado está sesgado a la baja en salas sobrepobladas | Recalcular sin truncar para calibrar; leer la sección «Aritmética de OCUPACIÓN_SALA» antes de reutilizar |
| R6 | **Perfil horario estable** (hipótesis): las asignaturas se siguen dictando en franjas parecidas | Si la programación cambia de política, el mapa se equivoca en el *cuándo*, no en el *cuánto* | Backtest (fase 4) y escenarios de redistribución |
| R7 | **Cambios de campus** de carreras (83 entre 2023 y 2026, Ariadna) | Demanda asignada al campus equivocado | Usar la tabla `CAMPUS_ACTUAL` / `CAMBIOS_CAMPUS.csv` de Ariadna |
| R8 | Ariadna es **anual** y la programación es **semestral** | Falta partir el año en períodos | Proporción histórica por período (es la «fase período académico» pendiente de Ariadna) |
| R9 | Programación cross-campus y espacios externos (Cirilo `CAMPUS_AUX`, `EXTERNO`) | Ocupación imputada al campus equivocado | Usar campus real del edificio; excluir externos del denominador |

---

## 4. Roadmap

Fases incrementales: cada una cierra con un entregable usable aunque la siguiente no se haga.

| Fase | Nombre | Qué se hace | Entregable | Criterio de salida | Esfuerzo estimado |
|---|---|---|---|---|---|
| **0** | Diagnóstico de empalme | Inventario de granos y llaves de los tres productos; verificar que asignatura (`MATERIA‖N_CURSO`), componente, campus y período empalman; medir cobertura cruzada (qué % de la programación real de Cirilo tiene proyección en Euribia) | `DIAGNOSTICO_EMPALME.md` + tabla de cobertura | Cobertura medida y llaves de cruce definidas; decisiones D1–D5 tomadas | 1 semana |
| **1** | Perfil horario | Desde el histórico de Cirilo: por asignatura-componente-campus, distribución de horas semanales por sección, día × bloque, tipo y rango de espacio; reglas de respaldo cuando hay poca historia (componente → materia → campus) | `PERFIL_HORARIO.parquet` + nota técnica | Perfil estable entre períodos (comparar 2 períodos consecutivos) | 1–2 semanas |
| **2** | Generador de programación sintética · corto plazo | Secciones de Euribia (período +1) × perfil horario → programación sintética con el mismo esquema que la programación detallada que consume Cirilo | `PROG_SINTETICA_<periodo>.parquet` | Total de horas-sección consistente con Euribia; esquema compatible con el pipeline de Cirilo | 2 semanas |
| **3** | Cirilo en modo proyección | Adaptar el pipeline y el dashboard: grano campus × día × bloque × tipo × rango; métricas de tasa de uso, llenado y holgura; selector de escenario y período; vista real vs proyectado | Pestaña nueva en el Dash de Cirilo (o app hermana) | Mapa de calor proyectado navegable para el período +1 | 2 semanas |
| **4** | Backtest | Proyectar un período ya ocurrido (ej. 2026-1 con datos hasta 2025-2) y comparar celda a celda contra el mapa real | Informe de validación | Métricas acordadas en D4 (ej. WAPE por celda, acierto en el top de bloques saturados) | 1–2 semanas |
| **5** | Puente Ariadna → largo plazo | Factor de crecimiento por carrera-campus traspasado a asignaturas según mix de carreras; partición anual → semestral; escenarios bajo / base / alto hasta 2031 | Programación sintética 2027–2031 por escenario | Totales de inscritos coherentes con Ariadna; bandas monótonas (bajo ≤ base ≤ alto) | 2–3 semanas |
| **6** | Panorama 2031 | Mapa de calor por año y escenario; ranking de bloques y campus en déficit; año de quiebre por tipo de espacio; escenarios de oferta (planta física modificada) y de redistribución horaria | Dashboard Sóstrato el Arquitecto + resumen ejecutivo | Validado con un usuario de planificación académica / infraestructura | 2 semanas |
| **7** | Documentación y deploy | Documento técnico-funcional según la plantilla de Data Products, diccionario de entregables, manual de usuario; materialización (Athena/S3) y frecuencia de actualización | Documentación + entregables materializados | Checklist de cumplimiento de la plantilla | 1–2 semanas |

**Total orientativo:** 12–16 semanas de trabajo efectivo. Fases 0–4 forman un MVP de **corto plazo** (período +1) que ya tiene valor por sí solo; 5–6 suman el **largo plazo**, hasta 2031 (el horizonte de Ariadna).

```
F0 Diagnóstico ─► F1 Perfil horario ─► F2 Prog. sintética ─► F3 Cirilo proyección ─► F4 Backtest
                                                                                         │
                                         MVP corto plazo (período +1) ◄──────────────────┘
                                                                                         │
                         F5 Puente Ariadna (2027–2031) ─► F6 Panorama 2031 ─► F7 Docs y deploy
```

---

## 5. Decisiones

### 5.1 Tomadas (Diego, 24-10-2026 · `Respuestas  Sóstrato.md`)

| # | Decisión | Qué se decidió |
|---|---|---|
| D1 | **Grano** | Celda del mapa = campus real (`CAMPUS_AUX`) × día × bloque × clase de espacio × rango de capacidad. Déficit **acumulado** por capacidad hacia arriba. Eje de tiempo = **semestre calendario**: suma 10/20 con 05/15/25 según las fechas. La programación sintética debe poder analizarse por **facultad, campus, período académico, nivel y bloque horario**, para una vista *craft* de vanguardia |
| D2 | **Secciones** | Se usan las secciones de Euribia, pero con la columna (`N_SECCIONES_*`) de **mejor WAPE por segmento** (tipo de período × componente), no P50 en todo. Medido el 24-10: WAPE 0,383 contra 0,578 de P50 en 202620 + 202625 (ver [[DIAGNOSTICO_EMPALME#10. Decisiones del 24-10 y medición de D2]]) |
| D3 | **Niveles** | **Solo pregrado y AV** (Advance). El postgrado queda fuera, sin carga fija |
| D7 | **Unidad académica** (24-10) | `MATERIA` = `cod_carrera` de Ariadna → facultad de esa carrera. Si no calza → **el departamento**, es decir, la propia `MATERIA` descrita con STVSUBJ (MT174, MT069, MT151…). Cubre el 100 %: con sala o laboratorio, 77,8 % por facultad y 22,2 % por departamento (con la definición del 24-10, que incluía ESPACIO UNIV, era 78,7 % / 21,3 %) |
| D8 | **Sesgo de secciones** (24-10) | La columna elegida en D2 se multiplica por un **factor por tipo de período × componente** = Σ secciones reales ÷ Σ columna elegida en la historia (segmentos con menos de 30 filas usan el factor del tipo de período). En 202620 + 202625 el sesgo pasa de −24 % a −2,6 % y el WAPE por campus de 0,241 a 0,114 |
| D9 | **Perfil horario** (24-10) | Simulación por plantillas reales; ventana de los últimos 2 años del mismo sufijo (2/3 el reciente, 1/3 el anterior); peso por semanas activas |
| D10 | **Oferta de espacios** (25-10) | **El mapa solo cuenta SALA y LABORATORIO**: EXTERNO, ESPACIO UNIV y SALA VIRTUAL quedan fuera. Esto ajusta D1, que tenía tres clases. Las salas usadas que no están en la planta toman la clase de su edificio, o la del componente si el edificio no está. Las sesiones sin sala quedan fuera y se informan aparte. La oferta base es el inventario usado en los últimos 2 años; lo no usado se informa como capacidad ociosa |
| D11 | **Salas compartidas** (25-10) | Las listas cruzadas (LC: una misma cátedra con distintos códigos de asignatura) cuentan **una** sala, repartida entre sus NRC, y **suman inscritos** (`PESO_LC`). La compartición que desde 2025 no se codifica como LC se corrige con un **factor residual por campus × clase** (salas reales ÷ Σ `PESO_OCUPACION`, últimos 2 años): 0,74 en laboratorios y 0,98 en salas. Fuera de muestra en 202620, el sesgo contra salas reales pasa de +20,3 % a +4,7 % |
| D12 | **Euribia no se extiende hasta 2031** (26-10) | Descartada como motor y como retadora del largo plazo. Euribia queda solo para la demanda de **1–2 semestres**; 2027–2031 sale del **top-down con Ariadna** (etapa 1b). Razones: (1) el error crece con el horizonte (+16,5 % de degradación ya en h = 2, y a 10 pasos se acumula); (2) su base es el *seasonal naive* y los árboles no extrapolan tendencia (T17 §6), mientras Ariadna proyecta +31 % de matrícula de pregrado al 2031; (3) no proyecta asignaturas nuevas (19–29 % por período) ni cambios de malla; (4) el cuello de botella medido está en la conversión demanda → secciones → salas, no en la demanda (2025→2026: NRC +14 %, salas-bloque +2,5 %) |
| D13 | **Programación sintética por estrato** (26-10) | La programación sintética **no predice qué asignatura se dicta**: genera **secciones físicas anónimas** (campus, edificio, sala, clase, día y bloques, inscritos, unidad, nivel, componente). **Estrato** = campus × unidad académica × nivel × clase de espacio × componente × período académico (mismo sufijo del año anterior). **Volumen** = inscritos. Se **remuestrean las secciones reales del año anterior** del estrato hasta el volumen objetivo. Cada sección se **reasigna a una sala libre equivalente** (mismo edificio y, si no, mismo campus; misma clase; capacidad ≥ inscritos); lo que no cabe es **déficit**. La sección física une los NRC de una LC y los que comparten sala al mismo tiempo, y suma sus inscritos. Reemplaza a la cascada por asignatura y deja la regla de secciones (D2, D8) fuera del mapa |
| D14 | **Modelo adoptado: C1** (26-10) | Mapa = w · naive (mapa real del mismo semestre del año anterior) + (1 − w) · G1b (programación sintética por estrato con elasticidad salas/inscritos). w se calibra en walk-forward solo con orígenes anteriores del mismo nivel: hoy ~0,7 en pregrado y ~0,3–0,4 en AV. Es el **único modelo que pasa la regla** del banco: tras la corrección de secciones físicas (diagnóstico §13.7), MASE < 1 en **4 de 5** orígenes de pregrado, en celda y en campus × día × bloque, con media 0,964. Llevado a `Modelos.ipynb` el 26-10 (diagnóstico §14): 2027 con Euribia, 2028–2031 con Ariadna NO VALIDADO, estándar real para el número de secciones; consistencia con el banco OK (0,942 vs 0,944). Pendiente: banda calibrada (H5), volumen proyectado validado en el banco y pseudo-backtest de largo plazo |
| D15 | **Volumen proyectado en el banco y fuente por nivel** (26-10) | Con volumen proyectado C1 vuelve casi al naive: C1-EUR no gana en pregrado (0/5, media 1,011), C1-PER 1,007 y C1-TEN pasa la regla por poco (3/5, media 1,011, pierde 202520). El error de inscritos por tipo es 0,26–0,30 con cualquier fuente: falla la composición. Decisión 3 de Diego («si C1-Euribia pierde, la variante ganadora»): pregrado = **C1-TEN** (w 0,8); AV = **C1-EUR** (mejor en orígenes AV, 0,976); Euribia queda como banda bajo/alto. TEN no se usa en AV (traslado C02→C05 de 2026). `Modelos.ipynb` lo elige del banco automáticamente (diagnóstico §15) |
| D16 | **Banda P10–P90 conformal (H5)** (26-10) | Residuos normalizados (real − punto)/√(punto+1) por nivel × clase × tramo, calibrados solo con orígenes previos (naive para el primero). La cobertura de C1-TEN en pregrado pasa del 1–12 % al 60–87 % (media 75 %) y la puntuación de intervalo de 1,57 a 0,93. Cumple en celda (3/5) y no en campus × día × bloque (2/5): cubre de menos en los orígenes con poca historia. **Aceptada por Diego el 27-10 con aviso** y aplicada en `Modelos.ipynb`, más la restricción física (sin espacios activos = 0). Diagnóstico §16 |
| D17 | **Largo plazo por horizonte** (27-10) | Pseudo-backtest de bases 2022–2024 a 1–4 años con la matrícula REAL de Ariadna (ARI-REAL), PER, TEN y ORA. C1 queda pegado al naive (MASE 0,99–1,01; ni el volumen perfecto gana más de 3–5 %). **C1 en todos los años** (Diego, 27-10: la regla por horizonte alternaba C1/naive por ±0,02 y dejaba 2029 sin crecer; queda como aviso de ventaja marginal), banda ensanchada por k_h (1,34 / 1,56 / 1,83; H5 1,94 extrapolado) y escenarios de Ariadna ensanchados según su backtest (UG 1,13 / 1,34 / 1,76: subestima el crecimiento). 2028–2030 validados con muestra chica, 2031 extrapolado. Diagnóstico §17 |
| D18 | **Rango de capacidad** (27-10) | 4 rangos de la planta (0-20, 21-40, 41-60, 60 o más) con alerta anidada hacia arriba. Tolerancia por clase = P90 de inscritos/capacidad de la base (sala 1,00; laboratorio 1,33); la sección necesita inscritos proyectados ÷ max(tolerancia, su sobrecupo histórico); la oferta efectiva por rango = max(inventario activo, lo que la base ya usa). La programación explícita usa los inscritos proyectados. Alertas ≥ 25 % por tamaño: 93 en 2027 → 211 en 2031 (sin tamaño: 48 → 156); déficit 5,3 % → 17,4 %, sobre todo de salas de 60 o más. Banco §8 informativo: MASE 0,98–1,03; acierta el reparto por rango. Diagnóstico §18 |
| D19 | **Naive escalado en el largo plazo (C1E)** (28-10) | El naive de cada campus × clase se escala por el crecimiento de salas que implica G1b. 2027 sigue con C1-TEN/C1-EUR (a 1 año C1E pierde); **2028–2031 con C1E** (w = 1,0) por decisión de Diego: corrige el sesgo (H+4 −7,6 % → −2,7 %) y mejora el MASE desde H+3 (0,959 / 0,962), **aviso: en H+2 empeora 0,011**. Centro del mapa 2027→2031 +22 % (antes +4 %); alertas ≥ 25 % por tamaño 93 → 297. Diagnóstico §19 |

### 5.2 Abiertas

| # | Decisión | Opciones | Cuándo |
|---|---|---|---|
| D4 | **Vara del backtest** | WAPE por celda, correlación del mapa, acierto en top-N bloques saturados | Antes de la fase 4 |
| D5 | **Dónde vive el producto** | Pestaña dentro del Dash de Cirilo / app separada / reutilizar el `hf_space` de Euribia. D1 pide una vista *craft* de vanguardia | Fase 3 |
| D6 | **Rol de Markov** (trayectorias) | Fuera / usarlo para repartir la matrícula de Ariadna por nivel de la malla (mejora el mix de asignaturas a largo plazo) | Fase 5 |

---

## 6. Próximo paso concreto

> [!success] Fase 0 hecha (22-10-2026)
> Ver [[DIAGNOSTICO_EMPALME]] (cobertura, backtest 202620, planta física y cambios C1–C6 a este roadmap) y el diagrama de flujo:
>
> ![[SOSTRATO_flujo_pipeline-modelo_2026-10-22.excalidraw]]

> [!info] Diagrama vigente: versión detallada (v1.0, 30-10-2026 · D14–D19)
> El de arriba es el de la fase 0. El flujo actual, con una caja por sub-paso del modelo (banco walk-forward, Monte Carlo G1b, naive estacional, C1/C1E, banda conformal, rango de capacidad y programación sintética) y el método de cada paso en su ficha, está aquí (generado con `Notebooks + Scripts/scripts_fase1/diagrama_flujo_detalle.py`):
>
> ![[SOSTRATO_flujo_pipeline-modelo-detalle_2026-10-30.excalidraw]]
>
> El compacto del 28-10 (`SOSTRATO_flujo_pipeline-modelo_2026-10-28`) queda reemplazado por este.

> [!example] Para directivos: cómo se construye la programación proyectada (30-10-2026)
> Lámina explicativa en cinco viñetas, sin notación de flujo (generada con `Notebooks + Scripts/scripts_fase1/diagrama_programacion_sintetica.py`):
>
> ![[SOSTRATO_programacion-sintetica_explicacion_2026-10-30.excalidraw]]

Texto original del paso:

Arrancar la **fase 0**: levantar los esquemas de los entregables de Euribia (`SERIE_COMPLETA_REAL_VS_PROYECTADO.csv`, ver `DICCIONARIO_ENTREGABLES_PROYECCION.md`), Ariadna (`PROYECCION_MATRICULA_2026_2031_28092026.csv`, ver `DICCIONARIO_ENTREGABLES_PROYECCION_MATRICULA.md`) y Cirilo (`PROG_DETALLADA_PARA_HEATMAP.parquet`), y medir cuánto empalman antes de diseñar nada más.

---

## 7. Arquitectura del modelo (aprobada por Diego el 25-10-2026)

> [!warning] En revisión tras la validación independiente (25-10)
> El informe de El Experto ([[INFORME_VALIDACION_EL_EXPERTO_2026-10-25]]) encontró tres problemas graves:
> - **H1:** el **naive** (mapa real del mismo semestre del año anterior) le gana al perfil en los tres períodos de prueba (MASE 1,13–1,23). Lo verificó también esta sesión: en 202620, naive 0,166 / 0,121 contra perfil 0,190 / 0,133.
> - **H2:** la prueba punta a punta acierta el nivel por compensación de errores.
> - **H3:** hay fuga de información en la elección de columna de D2.
>
> La etapa 3 y la regla de secciones se reformulan antes de seguir con las fases 5–6. Ver el plan de correcciones en la conversación del 25-10.

**Modelo:** simulación **Monte Carlo en cadena** de cuatro etapas. La incertidumbre de cada etapa pasa a la siguiente por simulación, y el entregable es una **distribución por celda**: P10, P50 y P90 de la tasa de uso y la **probabilidad de saturar**. La decisión de capacidad se toma en un cuantil alto, no en la media (Guía Maestra, Tomo 17 §9).

| Etapa | Modelo | Tipo | Respaldo en la Guía Maestra | Estado |
|---|---|---|---|---|
| 1a · Demanda de corto plazo (1–2 semestres) | **Euribia**: *seasonal naive* + corrección con CatBoost global + cuantiles P10/P50/P90 + reconciliación | ML global probabilístico | T17 §6 y §11: modelo global para miles de series relacionadas, con *seasonal naive* como vara | ✅ existe |
| 1b · Demanda de largo plazo (hasta 2031) | **Top-down jerárquico**: Ariadna (ETS por carrera) da el total y el mix histórico carrera → asignatura lo reparte. MinT como mejora posterior si los niveles no cuadran. Extender Euribia hasta 2031 se descartó (D12) | Series de tiempo + reconciliación | T17 §7: top-down da un total estable; MinT (Wickramasuriya et al., 2019) es el estado del arte | ⏳ falta la tabla RUT → carrera |
| 2 · Secciones | **Conversión calibrada**: columna de Euribia con mejor WAPE por segmento × factor de sesgo (D2, D8) | Regla calibrada | Validada fuera de muestra (sesgo −2,6 %, WAPE por campus 0,114) | ✅ `PIPELINES.ipynb` §4 |
| 3 · Programación sintética | **Remuestreo de plantillas reales**, ventana ponderada hacia lo reciente y cascada para asignaturas nuevas (D9) | Generador no paramétrico de datos sintéticos | T25 §4: entre cópulas, GAN y difusión, se elige remuestrear lo real porque conserva estructura (bloques consecutivos, sala por sesión) y la privacidad no es restricción. T17 §8: arranque en frío con series hermanas | ✅ `PIPELINES.ipynb` §7 |
| 4 · Ocupación vs oferta | **Agregación por sala** con LC + factor de compartición, contra el inventario efectivo acumulado por capacidad (D10, D11) | Determinístico calibrado | Validado: sesgo +4,7 %, correlación 0,972 | ✅ `PIPELINES.ipynb` §6–9 |

**Propagación:** en cada simulación se sortea la demanda (distribución de Euribia o banda de Ariadna), se convierte a secciones, se sortean sus plantillas y se agrega. Con ~500 simulaciones, bajo, base y alto se leen como cortes de esa distribución.

### 7.1 Protocolo de validación

1. **Baseline naive obligatorio** (T17 §10, regla de oro 1): el mapa real del mismo semestre del año anterior; para el largo plazo, ese mapa × el crecimiento de Ariadna. El modelo vale solo si le gana: WAPE del modelo ÷ WAPE del naive < 1, al estilo MASE.
2. **Walk-forward al horizonte real** (T10; T17 §10): varios orígenes (por ejemplo, proyectar 202520, 202610 y 202620 solo con lo anterior), a 1 y 2 semestres. Primero cada etapa por separado y después de punta a punta.
3. **Calibración probabilística** (T17 §9): cobertura empírica + ancho + CRPS por celda. Meta: cobertura P10–P90 cercana al 80 % (hoy el perfil solo cubre el 62 %). Si sumar la incertidumbre de la demanda no alcanza, se recalibra con conformal adaptativo (Gibbs & Candès, 2021).
4. **Fidelidad de la programación sintética** (T25 §4.5): distancia de variación total en día × bloque, preservación de la estructura y **utilidad**: que la decisión (celdas más cargadas, % de celdas sobre 90 %) salga igual que con lo real.

### 7.2 Redes neuronales

- **Demanda, como retadoras** (decisión del 25-10): primero un **foundation model zero-shot** (Chronos o TimesFM: sin entrenamiento, baseline adicional según T17 §6), y **DeepAR o TFT** solo si el primero muestra señal. Entran al mismo walk-forward que Euribia y el naive (WAPE/MASE, cobertura, CRPS). Se adoptan, solas o en combinación, **solo si mejoran** (T17 §6: combinar gana). Advertencia de T23: con ~5 puntos por serie, lo esperable es que el boosting global no pierda.
- **Programación sintética, como experimento** (decisión del 25-10): una **red generativa condicional** compite contra el remuestreo de plantillas, en un notebook separado del pipeline. Se adopta (completa o solo para asignaturas nuevas) **solo si le gana** en utilidad sin generar horarios inválidos. Diseño en `EXPERIMENTO_RED_GENERATIVA` (por definir).

---

## Anexo · Campus

Coordenadas entregadas por Diego el 25-10-2026; el código se cruzó con `desc_sede` de Ariadna.

| Código | Campus | Latitud | Longitud |
|---|---|---|---|
| C01 | Sede Norte · Campus 01 | -00.000000 | -00.000000 |
| C07 | Sede Norte · Campus 07 | -00.000000 | -00.000000 |
| C04 | Sede Sur | -00.000000 | -00.000000 |
| C03 | Sede Austral · Sede Austral (Campus 03) | -00.000000 | -00.000000 |
| C02 | Sede Centro · Campus 02 | -00.000000 | -00.000000 |
| C05 | Sede Centro · Campus 05 | -00.000000 | -00.000000 |
| C06 | Sede Centro · Campus 06 | -00.000000 | -00.000000 |

Sin coordenadas: C08 (Sede Lagos), C09 (Sede Valle) y C10 (virtual).

---

> **Dirección de Ingeniería de Datos — Universidad Ficticia**
> Responsable: Diego Evans Pérez Paz
