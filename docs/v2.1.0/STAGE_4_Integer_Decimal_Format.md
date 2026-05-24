# Por qué la corrección usa enteros y no decimales

El converter trabaja con enteros porque el flujo CLP-RCLP + MiniZinc necesita datos estables, comparables y compatibles con el modelo de Java que ya funciona.

## Idea principal

Los valores del dominio real vienen en magnitudes decimales o mixtas, pero el modelo final no debe depender de aritmética en coma flotante. En su lugar, se aplica una escala fija para convertir todo a enteros:

- Energía: se escala por 1000
- Tiempo: se expresa en segundos o minutos enteros, según el parámetro

Eso permite conservar precisión sin introducir errores de redondeo acumulados.

## Por qué no usar decimales directamente

Usar decimales parece más natural, pero en este caso genera problemas prácticos:

- MiniZinc y CPLEX trabajan mejor cuando las restricciones usan enteros consistentes.
- Las comparaciones con umbrales son más frágiles con floats.
- El modelo Java original ya define una convención de escala entera.
- Diferencias mínimas en coma flotante pueden cambiar la factibilidad del problema.

## Qué hace la escala

Con `SCALE_ENERGY = 1000`:

- `120.0 kWh` pasa a `120000`
- `15.0 kWh` pasa a `15000`
- `10 kWh/min` pasa a `167` unidades por segundo después de convertir de minutos a segundos y redondear

Con esto, el converter mantiene la misma semántica que la instancia Java-aligned.

## Por qué los tiempos también son enteros

Los tiempos del modelo se expresan en segundos para evitar mezclar unidades fraccionarias en restricciones de programación.

Ejemplos:

- `dt_max = 4 min` → `mu = 240`
- `sm = 1 min` → `SM = 60`
- `min_ct = 1 min` → `psi = 60`

## Resultado

El uso de enteros no es una simplificación arbitraria. Es la forma de:

- preservar precisión,
- reproducir exactamente la versión que resuelve bien,
- y evitar que el solver vea una versión numéricamente distinta del mismo problema.

En resumen: el converter usa enteros porque esa es la representación correcta para que el modelo sea estable y reproduzca el comportamiento del Java original.
