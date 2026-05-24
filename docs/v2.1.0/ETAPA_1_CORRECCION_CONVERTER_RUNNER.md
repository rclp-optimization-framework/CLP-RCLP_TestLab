# Correccion de conversion y runner

Este documento resume la correccion aplicada para que la conversion de Cork quede alineada con el baseline de Java y el runner devuelva el resultado esperado en MiniZinc.

## Que se corrigio

- Se restauro la conversion `original` en `core/converter/core/converter_engine.py`.
- Se mantuvo el modo `java` para generar instancias equivalentes al baseline de Java.
- Se corrigio la generacion de parametros en modo `java` para Cork:
  - `Cmax` y `Cmin` quedan en la misma escala que la instancia Java-aligned.
  - `alpha` se emite en unidades por segundo, como espera el modelo.
  - `mu`, `SM`, `psi`, `beta` y `M` se generan con la misma convencion temporal usada por Java.
- Se mejoro la deteccion de `UNSATISFIABLE` en el executor para que el runner reporte el estado correcto.

## Resultado verificado

Se valido el caso `cork-1-line` `20_0` con la configuracion real de JITS:

- Convertidor: `output_format="java"`
- Archivo fuente: `external/jits2022/Code/data/cork-1-line/buses_input_20_0.json`
- Parametros: `external/jits2022/Code/data/experiment_parameters_cork1_20_0.txt`
- Modelo MiniZinc: `core/models/clp_model_float.mzn`

El resultado obtenido fue:

- `Total estaciones: 1`
- `Estaciones instaladas` con una sola estacion activa

El runner tambien fue validado sobre la instancia corregida:

```powershell
python scripts/testing/run_battery_project_tests.py --data-dir experiments/instances/battery-java-aligned --pattern "cork-1-line_battery-java20_0.dzn" --limit 1 --solver cplex --time-limit 300000
```

Resultado:

- `Solution: OPTIMAL`
- `Stations: 1`

## Ejemplo de instancia corregida

Una instancia corregida debe verse con esta logica de encabezado:

```dzn
num_buses = 4;
num_stations = 40;

Cmax = 120000;
Cmin = 15000;
alpha = 167;

mu = 240;
SM = 60;
psi = 60;
beta = 600;
M = 100000;
```

Y sus matrices deben conservar la misma semantica que Java:

- `D`: consumo energetico en unidades enteras equivalentes al baseline
- `T`: tiempos de viaje enteros
- `tau_bi`: horarios de llegada en segundos o minutos segun la convension del dataset corregido

## Como reproducir

1. Generar la instancia con el convertidor.
2. Ejecutar el runner sobre el directorio generado.
3. Confirmar que el caso Cork `20_0` reporta una sola estacion.

Si quieres regenerar la instancia manualmente, usa el JSON de Cork y la configuracion real del experimento JITS.
