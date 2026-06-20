# Explainable Optimization Plan for CLP-RCLP

## Objetivo

Este documento define un plan de trabajo para evolucionar el sistema actual de generación de instancias y variantes hacia un flujo de **Explainable Optimization**.

La meta no es solo producir instancias válidas, sino generar familias de instancias con trazabilidad suficiente para responder preguntas como:

- por qué una instancia es satisfacible o no,
- qué parámetro o restricción dispara el cambio de comportamiento,
- qué diferencia real existe entre una instancia base y sus variantes,
- qué partes del modelo explican la decisión del solver.

## Punto de partida del sistema actual

El repositorio ya tiene una base útil para este objetivo:

- un generador central en `core/generator/` con parámetros consolidados en `core/generator/config.py`,
- validación automática con MiniZinc,
- patrones de rutas y lógica de repetición/descubrimiento de instancias factibles,
- scripts de generación de variantes, especialmente para casos Cork y Battery-Decided,
- un flujo de resultados que ya organiza instancias y salidas por familias.

Lo que todavía falta para explainability es convertir esa capacidad de generación en una capacidad de **explicación reproducible**.

## Qué significa explainability aquí

En este proyecto, explainability debe entenderse como la capacidad de:

1. construir instancias comparables entre sí,
2. controlar qué factor cambia entre una instancia base y su variante,
3. registrar el motivo de diseño de cada variante,
4. conservar evidencia suficiente para reconstruir la decisión del solver,
5. medir el efecto de cada perturbación sobre factibilidad, coste, tiempo y patrón de solución.

## Brechas del sistema actual

Hoy el generador está optimizado para producir instancias útiles y viables, pero no necesariamente explicables. Las brechas principales son:

- falta una taxonomía explícita de variantes orientadas a análisis causal,
- falta metadata estructurada por instancia y por familia,
- falta registrar el “factor perturbado” y el “factor controlado” en cada variación,
- falta separar claramente instancias base, variantes de sensibilidad y variantes de estrés,
- falta una capa de reporte que resuma por qué una instancia cambió de estado o de solución,
- falta una noción de “explicación esperada” asociada a cada variante.

## Principios de diseño

El rediseño debe seguir estos principios:

- **Un cambio por variante**: cada variante debe modificar un solo eje explicativo principal.
- **Reproducibilidad total**: cada instancia debe poder regenerarse con seed, perfil y versión.
- **Trazabilidad de parentesco**: toda variante debe conocer su instancia padre.
- **Estabilidad comparativa**: las familias deben mantenerse comparables en tamaño, estructura y escala.
- **Interpretabilidad de metadata**: los nombres y campos deben ser legibles por humanos y máquinas.
- **Compatibilidad retroactiva**: las instancias actuales deben seguir funcionando sin romper el flujo existente.

## Mejoras necesarias por subsistema

### 1. Generador de instancias

El generador debe pasar de “crear instancias válidas” a “crear instancias explicables”.

Mejoras propuestas:

- introducir perfiles de generación explícitos, por ejemplo `baseline`, `boundary`, `stress`, `counterfactual`, `robustness`,
- separar parámetros estructurales de parámetros explicativos,
- fijar semillas por familia y por variante,
- registrar el margen de factibilidad esperado,
- generar instancias base con una configuración canónica de referencia,
- construir variantes a partir de una base estable en lugar de generar cada archivo desde cero.

### 2. Sistema de variantes

Las variantes deben dejar de ser solo “otras instancias” y convertirse en experimentos controlados.

Taxonomía recomendada:

- **Variantes estructurales**: cambian buses, estaciones, ciclos o densidad de red.
- **Variantes energéticas**: cambian consumo, capacidad, tasa de carga o reserva mínima.
- **Variantes temporales**: cambian ventanas, tiempos de viaje, retardos o secuenciación.
- **Variantes topológicas**: cambian patrones de ruta, conectividad o cobertura de estaciones.
- **Variantes de robustez**: introducen incertidumbre controlada o perturbación en parámetros críticos.
- **Variantes contrafactuales**: mantienen todo igual salvo un único factor para explicar sensibilidad.

Cada variante debe incluir una etiqueta de explicación, por ejemplo:

- `why=capacity_limit`
- `why=time_window_conflict`
- `why=route_symmetry_break`
- `why=robustness_margin`
- `why=solver_boundary_case`

### 3. Metadatos y trazabilidad

Sin metadata, la explicabilidad se pierde aunque la instancia esté bien generada.

Campos mínimos recomendados por instancia:

- `instance_id`
- `parent_id`
- `family_id`
- `variant_type`
- `explanation_tag`
- `seed`
- `generator_version`
- `model_version`
- `num_buses`
- `num_stations`
- `route_pattern`
- `consumption_factor`
- `travel_time_factor`
- `feasibility_margin`
- `expected_solver_behavior`
- `validation_status`
- `created_at`

Campos recomendados por variable perturbada:

- valor base,
- valor nuevo,
- delta absoluto,
- delta relativo,
- justificación de cambio.

### 4. Exportación a DZN y JSON

La exportación debe incluir evidencia legible y estructurada.

Mejoras propuestas:

- escribir encabezados de metadata en cada archivo generado,
- guardar un JSON paralelo con la ficha explicativa de la instancia,
- incluir comentarios de generación en el archivo DZN,
- mantener referencia al padre y a la variante en el nombre del archivo,
- preservar hashes o fingerprints para detectar duplicados.

### 5. Validador y orquestador

La validación no debe limitarse a SAT/UNSAT.

Debe capturar:

- tiempo de validación,
- causa probable de fallo si la instancia es inviable,
- número de intentos,
- cambios entre reintentos,
- relación entre configuración y resultado.

Además, el orquestador debería producir un resumen explicable por instancia:

- qué se intentó,
- qué cambió,
- qué se esperaba,
- qué ocurrió,
- por qué la instancia se conservó o descartó.

### 6. Resultados y análisis

Los resultados deben poder agregarse por familia explicativa.

Se recomienda almacenar:

- solución obtenida,
- coste o métrica objetivo,
- estaciones activadas,
- tiempo de ejecución,
- estado SAT/UNSAT/UNKNOWN,
- contraste con la instancia base,
- explicación resumida de la diferencia.

## Tipos de instancias que conviene generar

Para que la explicabilidad sea útil, no basta con generar instancias aleatorias. Hay que generar conjuntos con propósito.

### A. Instancias base

Sirven como referencia estable. Deben ser equilibradas, reproducibles y fáciles de resolver.

### B. Instancias límite

Se diseñan cerca del umbral de factibilidad para estudiar sensibilidad.

Ejemplos:

- consumo total cercano a capacidad usable,
- tiempos de viaje que casi rompen la ventana,
- número de buses que casi satura estaciones.

### C. Instancias de perturbación aislada

Solo cambia un parámetro por vez.

Ejemplos:

- +5% de consumo,
- -1 estación,
- +10 minutos en una ventana,
- cambio de patrón de ruta.

### D. Instancias contrafactuales

Permiten responder “qué tendría que cambiar para que la solución fuera distinta”.

### E. Instancias robustas

Introducen incertidumbre controlada para explicar resiliencia del plan.

## Roadmap recomendado

### Fase 1: Instrumentación mínima

Objetivo: que cada instancia tenga identidad y trazabilidad.

Entregables:

- metadata JSON por instancia,
- identificador de padre e hijo,
- seed registrada,
- versión de generador y modelo,
- nomenclatura consistente.

### Fase 2: Taxonomía de variantes

Objetivo: separar familias explicativas.

Entregables:

- perfiles `baseline`, `boundary`, `stress`, `counterfactual`, `robustness`,
- reglas de perturbación por perfil,
- validación de que solo cambia el factor previsto.

### Fase 3: Explicación automática

Objetivo: producir resumen humano de cada instancia.

Entregables:

- ficha explicativa por archivo,
- resumen de diferencia contra la base,
- etiquetas de causa probable para SAT/UNSAT.

### Fase 4: Análisis comparativo

Objetivo: medir sensibilidad y estabilidad.

Entregables:

- tablas de comparación por familia,
- análisis de umbrales,
- informes por solver y por patrón.

### Fase 5: Integración visual

Objetivo: que el sistema permita explorar explicaciones sin abrir archivos manualmente.

Entregables:

- panel en GUI para seleccionar familia y variante,
- visor de metadata y diferencias,
- exportación de reportes en Markdown o JSON.

## Métricas de éxito

La evolución hacia explainability debe medirse con indicadores concretos:

- porcentaje de instancias con parent_id y explanation_tag,
- reproducibilidad por seed,
- proporción de variantes con un único factor modificado,
- número de familias comparables por perfil,
- tiempo de generación por instancia,
- tasa de validación satisfactoria,
- capacidad de explicar cambios SAT/UNSAT con metadata disponible.

## Reglas prácticas para generar variantes explicables

- no mezclar en una misma variante cambios de capacidad, tiempo y topología si el objetivo es explicabilidad,
- no reutilizar nombres genéricos como “variant_1” sin contexto,
- no borrar la instancia base cuando se crea una variación,
- no ocultar el seed ni el perfil de generación,
- no dejar que la validación automática regenere sin registrar el motivo del cambio,
- no comparar instancias de familias distintas como si fueran equivalentes.

## Secuencia de implementación sugerida

1. Definir la taxonomía de variantes.
2. Añadir metadata obligatoria al generador.
3. Introducir parent-child tracking entre base y variantes.
4. Hacer que el exportador escriba fichas explicativas.
5. Guardar resultados agregados por familia.
6. Generar reportes comparativos automáticos.
7. Añadir visualización en la interfaz.

## Resultado esperado

Al finalizar este plan, el sistema debería poder responder, para cada instancia:

- de dónde salió,
- qué cambió respecto a la base,
- por qué existe esa variante,
- qué comportamiento esperábamos,
- qué comportamiento produjo el solver,
- qué aprendizaje deja para la siguiente iteración.

Eso convierte la generación de instancias en una herramienta de investigación explicable, no solo en un generador de archivos.