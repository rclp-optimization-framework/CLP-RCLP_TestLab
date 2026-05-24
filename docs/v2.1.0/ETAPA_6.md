# ETAPA 6

## Estado actual

- La interfaz del runner ya no expone parámetros de CPLEX al usuario.
- El runner sigue usando CPLEX de forma interna con valores por defecto ocultos.
- `scripts/check_java_equivalence.py` ya apunta a `experiments/instances/Battery-Decided`.
- El chequeo de equivalencia ya no depende de parámetros manuales de CPLEX.
- El chequeo de equivalencia ya no impone timeout interno en `MiniZincExecutor`.

## Hallazgos confirmados

- La referencia Java para `Battery-Decided` indica:
  - `20_0` -> estación 11 en el texto Java, pero el JSON de referencia guarda la posición 20 como one-hot.
  - `20_5` -> estación 19.
  - `20_10` -> estación 19.
- Los modelos MiniZinc activos siguen sin reproducir esa selección de manera estable en todas las variantes.
- El desajuste no parece venir del conversor DZN en el estado actual; el punto activo sigue siendo el modelo/solver.
- La validación actual contra `Battery-Decided` muestra que el modelo activo sigue escogiendo estaciones distintas de la referencia Java.

## Próximos pasos sugeridos

- Comparar la salida completa del modelo MiniZinc contra el JSON de referencia de `Battery-Decided`.
- Revisar si el solver wrapper o el orden de búsqueda de MiniZinc/CPLEX altera la estación elegida.
- Si hace falta, introducir una restricción o preferencia secundaria controlada para fijar la misma estación que Java.
