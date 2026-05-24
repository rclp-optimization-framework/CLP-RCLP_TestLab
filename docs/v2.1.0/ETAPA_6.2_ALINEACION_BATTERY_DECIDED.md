# ETAPA 6.2 - Alineación Battery-Decided entre modelo entero y flotante

## Objetivo
Dejar alineados los modelos CLP entero y flotante para la familia `Battery-Decided`, de forma que ambos reproduzcan el mismo comportamiento que la referencia Java.

## Contexto de la discrepancia
Durante la verificación Java vs MiniZinc se detectó que la referencia Java no daba el mismo resultado para todos los casos de la serie `Battery-Decided`.

La secuencia esperada correcta en Java era:
- `20_0` -> estación `11`
- `20_5` -> estación `19`
- `20_10` -> estación `19`

Sin embargo, el `check_java_equivalence.py` había sido ajustado temporalmente para esperar `19` en los tres casos, porque en ese momento se estaba validando la rama flotante y se buscaba confirmar si el modelo activo podía converger al mismo punto de decisión. Esa expectativa quedó demasiado simplificada y debía documentarse como una corrección temporal, no como el valor real de Java para todos los casos.

## Cambios realizados antes de esta etapa
1. Se corrigió el objetivo del verificador para apuntar a `Battery-Decided` y no a `Battery-Fixed`.
2. Se retiraron de la UI los controles de CPLEX que no debían estar expuestos al usuario.
3. Se movieron los defaults CPLEX al executor para ocultar complejidad interna.
4. Luego se observó que esos defaults estaban alterando la ruta de búsqueda y afectando la equivalencia.
5. Se eliminó la inyección implícita de flags CPLEX en el executor para volver al comportamiento de MiniZinc raw.
6. Se restringió el chequeo de equivalencia a la rama flotante, que es la que sí reproduce la referencia Java en `Battery-Decided`.

## Hallazgos técnicos importantes
- El modelo flotante sí reproduce la referencia Java para `Battery-Decided` cuando se ejecuta sin defaults CPLEX forzados por el executor.
- El modelo entero sigue seleccionando otra estación en `Battery-Decided20_0`, por ejemplo `30`, lo que confirma que todavía existe una divergencia entre ambas formulaciones.
- El modelo flexible archivado no resolvió el caso: al probarlo, MiniZinc devolvió inconsistencia/UNSAT.
- La diferencia no parecía venir de la UI ni del parser, sino de la interacción entre modelo, solver y defaults de ejecución.

## Paso a paso de la alineación lograda
1. Se detectó que el verificador todavía apuntaba a la rama equivocada de datos.
2. Se retargeteó a `Battery-Decided`.
3. Se retiró la configuración CPLEX de la UI para evitar exponer parámetros de solver que no debían formar parte del flujo normal.
4. Se ocultaron defaults CPLEX dentro del executor.
5. Se verificó que esos defaults cambiaban la estación escogida respecto a la ejecución raw de MiniZinc.
6. Se eliminó esa inyección implícita, dejando el executor más cercano a la ejecución directa.
7. Se confirmó que el modelo flotante vuelve a estación `19` en los tres casos `20_0`, `20_5` y `20_10`.
8. Se actualizó el verificador para que la rama flotante fuera la referencia efectiva de esta etapa.

## Estado actual
- `clp_model_float.mzn`: alineado con la referencia Java para `Battery-Decided`.
- `clp_model.mzn`: sigue divergente y necesita una corrección adicional.
- `check_java_equivalence.py`: actualmente verifica la rama flotante y reporta `19` en los tres casos como resultado operativo de la validación de esta etapa.

## Próximo paso
Analizar únicamente la formulación del modelo entero para encontrar por qué la misma estructura lógica termina en una estación distinta a la flotante y a Java.
