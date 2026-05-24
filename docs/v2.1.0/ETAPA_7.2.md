# ETAPA 7.2 - Alineación del modelo entero con warm-start CPLEX

## Objetivo
Alinear el modelo entero con la solución de referencia flotante sin tocar el modelo flotante, manteniendo la ejecución exclusivamente con CPLEX.

## Qué se cambió

### 1. Modelo entero
Archivo: `core/models/clp_model.mzn`

- Se incorporó soporte de warm-start para CPLEX.
- Se introdujeron arrays auxiliares `xst_init_ws` y `xst_pref_ws` para cargar una semilla externa sin provocar errores de doble asignación.
- Se derivaron las variables efectivas `xst_init` y `xst_pref` a partir de esos arrays auxiliares.
- Se mantuvo el objetivo entero, con una preferencia débil para desempatar entre soluciones óptimas equivalentes y favorecer el conjunto de estaciones elegido por la solución flotante.

### 2. Runner de CPLEX
Archivo: `scripts/run_with_cplex.py`

- Se agregó la lectura de un JSON de referencia flotante mediante `--warm-start-json`.
- Se generó un DZN temporal de warm-start con los arrays auxiliares esperados por el modelo.
- Se corrigió el flujo para que el runner siga usando el DZN de instancia original y agregue el DZN auxiliar como segundo archivo de datos.
- Se preservó el archivo temporal en `experiments/tmp/` cuando hay fallo, para poder depurar el contenido exacto que recibió MiniZinc.

### 3. Ejecutor MiniZinc
Archivo: `core/runner/core/executor.py`

- Se corrigió el soporte para múltiples archivos DZN.
- Se reparó una referencia rota a `dzn_path` al parsear la salida, usando el DZN principal de la instancia para extraer metadatos.
- Con eso, el runner volvió a funcionar sin scripts externos de comparación.

## Resultado validado

- La instancia `Battery-Decided20_0` se ejecutó correctamente con CPLEX.
- La versión con warm-start produjo una solución coherente con la flotante en la estación instalada para esa instancia.
- El runner generó JSON válidos y el parseo de salida volvió a funcionar.

Archivo de resultado: `experiments/results/cplex_int_20_0_ws.json`

## Observación importante

La solución original del modelo entero y la flotante ya tenían la misma función objetivo, pero diferían por desempate entre óptimos. La corrección aplicada no cambia la formulación flotante y está enfocada en hacer determinista la selección del conjunto de estaciones del modelo entero.

## Validación completada

Se ejecutó la comparación directa sobre el conjunto disponible `Battery-Decided` usando el runner y CPLEX, sin scripts de comparación externos.

Casos validados:

- `cork-1-line_Battery-Decided20_0.dzn`: entero con warm-start y flotante coinciden en la estación 20 y en la desviación total.
- `cork-1-line_Battery-Decided20_5.dzn`: entero y flotante coinciden en la estación 20 y en la desviación total.
- `cork-1-line_Battery-Decided20_10.dzn`: entero y flotante coinciden en la estación 20 y en la desviación total.

Resultado global:

- el modelo entero sigue funcionando con CPLEX,
- el modelo flotante sigue funcionando con CPLEX,
- el runner procesa ambos modelos correctamente,
- y el warm-start no rompe la ejecución normal cuando no se usa.
