# ETAPA 7.3 - Runner universal con warm-start opcional

## Objetivo
Revisar a fondo el flujo de ejecución para que el runner funcione correctamente con:

- instancias Cork,
- instancias reales,
- instancias sintéticas,
- modelo entero,
- modelo flotante,
- y warm-start solo cuando exista un caso de referencia útil.

La prioridad fue mantener el sistema modular, estable y usable sin depender de ejemplos previos.

## Diagnóstico

La solución anterior de warm-start funcionaba para la instancia de referencia 20_0, pero dejó dos riesgos:

- el modelo entero terminó dependiendo de datos de warm-start que no siempre existen,
- y eso podía romper ejecuciones normales del runner en otras instancias.

Eso era un problema para un sistema general, porque el runner debe poder resolver cualquier instancia sin pedir una semilla previa.

## Qué se corrigió

### 1. Modelo entero
Archivo: `core/models/clp_model.mzn`

Se restauró un comportamiento universal para que el modelo entero vuelva a correr sin depender de warm-start.

- `xst_init` y `xst_pref` quedaron como vectores normales por defecto.
- El objetivo sigue incorporando el desempate débil que ya existía, pero ahora solo se activa de forma útil cuando el runner materializa una versión temporal del modelo.
- El archivo base vuelve a ser seguro para cualquier instancia, incluso cuando no existe JSON previo de referencia.

### 2. Runner
Archivo: `scripts/run_with_cplex.py`

Se cambió el enfoque de warm-start para que sea opcional y no invada el flujo normal.

- Si no se pasa `--warm-start-json`, el runner ejecuta el modelo base directamente.
- Si se pasa `--warm-start-json`, el runner crea un modelo temporal en `experiments/tmp/` con los valores de warm-start incrustados.
- Eso evita el error de MiniZinc por doble asignación y no obliga a pasar datos auxiliares al modelo base.
- El runner sigue sirviendo para cualquier instancia con el mismo comportamiento de siempre.

### 3. Ejecutor
Archivo: `core/runner/core/executor.py`

El ejecutor sigue soportando el flujo normal con una sola DZN y mantiene compatibilidad con el uso general del runner.

- Se conservó el parseo de salida.
- Se mantuvo la extracción de metadatos desde el DZN principal.
- No se introdujo ninguna dependencia extra para la interfaz de usuario.

## Validación realizada

Se verificó el sistema con CPLEX sobre instancias de Battery-Decided y con ambos modelos.

### Caso base sin warm-start
- `cork-1-line_Battery-Decided20_5.dzn`
- `cork-1-line_Battery-Decided20_10.dzn`

Resultado:

- el modelo entero resolvió correctamente,
- el modelo flotante resolvió correctamente,
- el runner generó JSON válidos en ambos casos.

### Caso con warm-start
- `cork-1-line_Battery-Decided20_0.dzn`
- usando como referencia `cplex_float_20_0.json`

Resultado:

- el runner creó un modelo temporal de warm-start,
- CPLEX resolvió correctamente,
- el resultado entero coincidió con la solución flotante en la estación instalada y en la desviación total.

## Resultado funcional

El sistema quedó en un estado más robusto:

- el runner funciona para casos normales sin requerir warm-start,
- el warm-start se usa solo cuando aporta valor,
- el modelo flotante no fue alterado,
- el modelo entero sigue siendo ejecutable para todo el catálogo de instancias,
- y no se agregó ninguna modificación a la UI.

## Archivos clave

- `core/models/clp_model.mzn`
- `core/models/clp_model_float.mzn`
- `scripts/run_with_cplex.py`
- `core/runner/core/executor.py`

## Conclusión

La estrategia correcta para este sistema no era hacer el warm-start obligatorio, sino mantener el runner universal y usar una plantilla temporal solo cuando existe una referencia previa confiable. Eso preserva la modularidad y evita romper el uso general del sistema.
