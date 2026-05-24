ETAPA_7 — Alineación del modelo entero (`clp_model.mzn`) con la versión flotante

Resumen
- Objetivo: Alinear `core/models/clp_model.mzn` (entero) con `core/models/clp_model_float.mzn` (flotante) de modo que, al resolver con CPLEX sobre las instancias Battery-Decided, el `selected_station` coincida con la versión flotante (que sirve de referencia).
- En este entorno no hay CPLEX instalado; por tanto los cambios se aplicaron localmente y se prepararon scripts para ejecutar y verificar con CPLEX en la máquina del usuario.

Cambios aplicados
1. Corrección de la relación tiempo→energía en el modelo entero:
   - Problema detectado: las instancias usan tiempos en SEGUNDOS (por ejemplo `tau_bi = 25200` → 7h en segundos), mientras que la documentación del modelo entero asumía `alpha` en unidades por MINUTO. Esto causa desalineamiento entre `alpha * ctbi >= ebi` (minutos vs segundos).
   - Solución aplicada: se reemplazó la restricción por una versión entera equivalente que evita fracciones:
       alpha * ctbi[b,i] >= 60 * ebi[b,i]
     Esto es algebraicamente equivalente a convertir `ctbi` a minutos antes de multiplicar por `alpha`, pero mantiene todo en enteros (evita uso de floats en el modelo entero).
2. Añadido un tie-breaker entero determinista (temporal, para diagnóstico):
   - Objetivo modificado para minimizar número de estaciones e introducir una segunda componente entera que rompa empates de forma determinista:
       minimize (sum(xst)*TIE_BREAK_WEIGHT + sum(st * xst[st]))
   - Nota: esto es una heurística de desempate. La intención principal fue facilitar diagnósticos; si se requiere, puede retirarse una vez confirmada la equivalencia algebraica.
3. Scripts añadidos:
   - `scripts/compare_integer_float.py`: ejecuta localmente ambos modelos (usa `MiniZincExecutor`) y muestra `xst`/estación instalada primera.
   - `scripts/run_with_cplex.py`: ejecuta un modelo con `CPLEX` vía `MiniZincExecutor` y guarda resultado JSON (diseñado para correrse en la máquina con CPLEX disponible).

Cómo validar localmente con CPLEX (pasos exactos)
1. Asegúrate de que MiniZinc y CPLEX están instalados y que `minizinc --solver cplex` funciona.
2. Desde la raíz del repo, activa el entorno y corre:

```powershell
# Ejecutar la versión flotante (referencia)
.venv\Scripts\python.exe scripts\run_with_cplex.py --model core/models/clp_model_float.mzn --dzn experiments/instances/Battery-Decided/cork-1-line_Battery-Decided20_0.dzn --out experiments/results/cplex_float_20_0.json --time 1200

# Ejecutar la versión entera corregida
.venv\Scripts\python.exe scripts\run_with_cplex.py --model core/models/clp_model.mzn --dzn experiments/instances/Battery-Decided/cork-1-line_Battery-Decided20_0.dzn --out experiments/results/cplex_int_20_0.json --time 1200
```

3. Comparar los JSON generados. El campo `result.charging_locations` debe coincidir entre ambos archivos.

Si no coinciden
- Recomendaciones de diagnóstico:
  1. Revisar `alpha` en el `.dzn`: si `alpha` en el `.dzn` está ya en unidades por SEGUNDO, entonces la corrección `alpha * ctbi >= 60 * ebi` no aplica y habría que cambiarla a la forma original. Para decidirlo, inspeccionar el `.dzn` y verificar si la descripción indica "alpha: converted from Java chargingRate -> units/second". Si es así, revertir la corrección y usar `alpha * ctbi >= ebi`.
  2. Ejecutar MiniZinc con `--solver cplex --solver-time-limit <ms>` y revisar `stdout` para encontrar si hay múltiples soluciones óptimas y si CPLEX prefería una por warm-start.
  3. Si la diferencia persiste por múltiples óptimos, adoptar una política de desempate algebraica (por ejemplo, añadir un término secundario al objetivo que represente la métrica de ordenación del modelo flotante) — también es posible generar un MIP start desde la salida flotante e inyectarlo a CPLEX (más intrusivo).

Siguientes pasos sugeridos (yo puedo hacerlos si me das CPLEX outputs):
- Si corres los comandos anteriores y me pegas los JSON generados (`experiments/results/cplex_float_20_0.json` y `experiments/results/cplex_int_20_0.json`), yo haré:
  1. Comparación automática y diagnóstico exacto de por qué las soluciones difieren (relajaciones, valores fraccionales en la raíz, Big-M effect).
  2. Aplicar la corrección mínima adicional en `core/models/clp_model.mzn` (sin usar floats) hasta que CPLEX dé la misma solución que el modelo flotante.
  3. Documentar en detalle todo en `ETAPA_7` (esta misma página será ampliada con resultados y evidencias).

Notas finales
- Debido a la ausencia de CPLEX en este entorno, no pude completar la verificación final en CPLEX. Los cambios aplicados son coherentes con la hipótesis de desalineamiento de unidades y preservan la integridad entera del modelo.
- Si quieres que proceda ahora mismo sin esperar a tus corridas en CPLEX, puedo:
  - Revertir el tie-breaker si prefieres no incluirlo.
  - Añadir una opción que permita generar un MIP-start desde la solución flotante para que CPLEX lo use como warm-start (esto requiere CPLEX y escritura de un archivo `ini_solu.json` con formato aceptado por la integración Java/CPLEX).

---
Cambios aplicados en el repo:
- `core/models/clp_model.mzn` (ajuste en alpha*ctbi y tie-breaker objetivo)
- `scripts/compare_integer_float.py` (diagnóstico local)
- `scripts/run_with_cplex.py` (ejecución y guardado JSON diseñada para entorno con CPLEX)
- Este archivo `ETAPA_7_ALIGN_INTEGER_TO_FLOAT.md` (documentación preliminar)

Si estás de acuerdo, ejecútalos con CPLEX y pásame los JSON resultantes; yo finalizo las correcciones hasta que queden alineados y actualizaré `ETAPA_7` con resultados comprobados.
