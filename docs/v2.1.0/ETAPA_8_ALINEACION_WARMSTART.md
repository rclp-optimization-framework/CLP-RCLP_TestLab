# ETAPA 8 — Alineación entero/flotante y flujo de Warm‑Start

**Resumen**
- **Objetivo:** Documentar la decisión de alinear el modelo entero con el modelo flotante y describir el flujo reproducible de warm‑start.
- **Estado:** Implementado; warm‑start es opcional y se materializa en `scripts/warm_start/generated/` cuando se solicita.

**Decisiones clave**
- Se eliminó el tie‑breaker lexicográfico del modelo entero (`core/models/clp_model.mzn`) para que la función objetivo sea equivalente a la del modelo flotante: minimizar `sum(st in ST)(xst[st])`.
- Se eliminaron placeholders y directivas de warm‑start del modelo base para evitar asignaciones DZN duplicadas.

**Diseño del warm‑start**
- El warm‑start se genera sólo cuando se pasa `--warm-start-json` al runner (`scripts/run_with_cplex.py`).
- Flujo: primero obtener la salida del modelo flotante (JSON), luego pasar ese JSON al runner para generar un modelo temporal y un `.dzn` de warm‑start que se ejecutan contra el modelo entero.
- Los artefactos generados se guardan en `scripts/warm_start/generated/` con nombres del estilo:
  - `clp_model_<instance>_warmstart.mzn`
  - `<instance>_warmstart.dzn`

**Cómo reproducir (ejemplos)**
- Ejecutar el modelo flotante (genera un JSON de referencia):
  `python scripts/run_with_cplex.py --model core/models/clp_model_float.mzn --dzn <instance.dzn> --out experiments/results/cplex_float_<id>.json --time 1200`
- Ejecutar el modelo entero SIN warm‑start:
  `python scripts/run_with_cplex.py --model core/models/clp_model.mzn --dzn <instance.dzn> --out experiments/results/post_int_<id>.json --time 1200`
- Ejecutar el modelo entero CON warm‑start (usa el JSON generado por el flotante):
  `python scripts/run_with_cplex.py --model core/models/clp_model.mzn --dzn <instance.dzn> --warm-start-json experiments/results/cplex_float_<id>.json --out experiments/results/post_int_<id>_ws.json --time 1200`

**Instancias validadas**
- Se verificó la igualdad de `charging_locations` entre modelos entero y flotante en las instancias: `Battery-Decided20_0`, `Battery-Decided20_5`, `Battery-Decided20_10` (conocidas como `cork-1-line_...`).

**Cambios técnicos relevantes**
- `core/runner/core/executor.py`: corrección en el parseo de salida usando `dzn_paths[0]` para evitar error `dzn_path` no definido.
- `core/models/clp_model.mzn`: removidos placeholders de warm‑start y tie‑breaker lexicográfico; objetivo alineado al modelo flotante.
- `scripts/run_with_cplex.py`: implementación de la generación de modelo y `.dzn` de warm‑start en `scripts/warm_start/generated/` sólo cuando se solicita.

**Notas y recomendaciones**
- No modificar los modelos base para incluir valores de warm‑start por defecto; siempre materializar artefactos en `scripts/warm_start/generated/` para reproducibilidad.
- Próximo paso sugerido: revisar `ConverterEngine/DataLoader` para asegurar que no hay regresiones en la preparación de instancias.

Si quieres, puedo:
- Ejecutar una validación exhaustiva sobre todo el conjunto Battery‑Decided.
- Revisar y documentar `ConverterEngine/DataLoader`.
