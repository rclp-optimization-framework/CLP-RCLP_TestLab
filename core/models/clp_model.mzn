% -----------------------------
% PARÁMETROS DEL PROBLEMA
% -----------------------------

int: num_buses;                 % Número total de buses
set of int: B = 1..num_buses;   % Conjunto de buses

int: num_stations;              % Número total de estaciones posibles
set of int: ST = 1..num_stations;

int: max_stops;                 % Máximo número de paradas por bus
array[B] of int: num_stops;     % Número real de paradas por bus

% Mapeo de cada parada del bus a una estación física
array[B,1..max_stops] of int: st_bi;

% -----------------------------
% ESCALA NUMÉRICA
% -----------------------------

% Diferenciada por dominio (energía vs tiempo):
% Energy (D, Cmax, Cmin, alpha): Valores enteros en unidades de 0.001 kWh (SCALE=1000)
%   Ejemplo: 100 kWh = 100000 unidades, 0.067 kWh × 1000 = 67 unidades (0% error)
%   Escalado aumentado de 50 a 1000 para minimizar error de truncamiento en cálculos acumulados
% Time (T, tau_bi, tbi, ctbi): Valores enteros en segundos (sin escala)
%   Ejemplo: 25200 segundos (07:00) = 25200 unidades, 60 s = 60 unidades

% -----------------------------
% CONSTANTES DEL MODELO
% Todos los parámetros están en unidades enteras coherentes con su dominio físico
% NO se usa escala global - cada magnitud tiene escala propia según necesidad
% -----------------------------

int: Cmax;   % Capacidad máxima de la batería (en unidades de 0.001 kWh, SCALE=1000)
int: Cmin;   % Nivel mínimo permitido de batería (en unidades de 0.001 kWh, SCALE=1000)
int: alpha;  % Tasa de carga energética (en unidades de 0.001 kWh/min, SCALE=1000)
int: mu;     % Desviación máxima permitida respecto al horario (en segundos)
int: SM;     % Margen de seguridad entre eventos de carga (en segundos)
int: psi;    % Tiempo mínimo de carga (en segundos)
int: beta;   % Tiempo máximo de carga (en segundos)
int: M;      % Constante grande para restricciones lógicas (Big-M, en segundos)

% -----------------------------
% DATOS DE LAS RUTAS
% -----------------------------

array[B,1..max_stops] of int: D;      % Energía consumida entre paradas
array[B,1..max_stops] of int: T;      % Tiempo de viaje entre paradas
array[B,1..max_stops] of int: tau_bi; % Horario planificado de llegada

int: tau_max = max([tau_bi[b,i] | b in B, i in 1..num_stops[b]]);
int: t_upper_bound = tau_max + M + beta + SM + mu;

% -----------------------------
% VARIABLES DE DECISIÓN
% -----------------------------

array[B,1..max_stops] of var 0..Cmax: cbi;   % Nivel de batería al llegar
array[B,1..max_stops] of var 0..Cmax: ebi;   % Energía cargada en la parada
array[B,1..max_stops] of var 0..beta: ctbi;   % Tiempo dedicado a cargar
array[B,1..max_stops] of var 0..t_upper_bound: tbi;   % Tiempo real de llegada
array[B,1..max_stops] of var 0..mu: d_tbi;  % Desviación respecto al horario

array[B,1..max_stops] of var 0..1: xbi;      % 1 si el bus carga en la parada

array[ST] of var 0..1: xst;                  % 1 si se instala estación

% Optional warm start hooks. The runner may materialize a temporary model with
% concrete values for these arrays when a warm-start JSON is provided. In the
% base model they default to zero so the model remains universally usable.
% Variables auxiliares para evitar solapamientos de carga
array[B,B,1..max_stops,1..max_stops] of var 0..1: Zbdij;
array[B,B,1..max_stops,1..max_stops] of var 0..1: zbdi;

% -----------------------------
% A. CAPACIDAD DE BATERÍA
% -----------------------------

% Initial conditions
constraint forall(b in B) (
    cbi[b,1] = Cmax /\           % Start with full charge
    tbi[b,1] = tau_bi[b,1]       % Actual arrival time matches schedule at first stop
);

% La batería debe permanecer dentro de límites seguros
constraint forall(b in B, i in 1..num_stops[b]) (
    cbi[b,i] >= Cmin /\                     % nivel mínimo
    cbi[b,i] + ebi[b,i] <= Cmax /\          % no exceder capacidad
    alpha * ctbi[b,i] >= ebi[b,i]
);

% Evolución del nivel de batería entre paradas
constraint forall(b in B, i in 2..num_stops[b]) (
    cbi[b,i] <= cbi[b,i-1] + ebi[b,i-1] - D[b,i]
);

% -----------------------------
% B. RESTRICCIONES DE TIEMPO
% -----------------------------

% Tiempo de llegada considerando viaje y carga
constraint forall(b in B, i in 2..num_stops[b]) (
    tbi[b,i] >= tbi[b,i-1] + ctbi[b,i-1] + T[b,i] /\   % tiempo de viaje
    tbi[b,i] >= tbi[b,i-1] + ctbi[b,i-1] + SM * xbi[b,i-1] % margen si hay carga
);

% Cálculo de desviación respecto al horario planificado
constraint forall(b in B, i in 1..num_stops[b]) (
    d_tbi[b,i] >= tbi[b,i] - tau_bi[b,i] /\  % retraso
    d_tbi[b,i] >= tau_bi[b,i] - tbi[b,i] /\  % adelanto
    d_tbi[b,i] <= mu /\                      % límite máximo permitido
    ctbi[b,i] >= psi * xbi[b,i]              % tiempo mínimo si se carga
);

% -----------------------------
% C. INSTALACIÓN DE CARGADORES
% -----------------------------

% Solo se puede cargar si hay estación instalada
% NOTA: st_bi es 1-indexed (1..num_stations), válido para todos los stops en num_stops[b]
constraint forall(b in B, i in 1..num_stops[b]) (
    beta * xbi[b,i] >= ctbi[b,i] /\          % límite de tiempo de carga
    xst[st_bi[b,i]] >= xbi[b,i]              % la estación debe existir
);

% -----------------------------
% D. NO SOLAPAMIENTO DE CARGAS
% -----------------------------

% Evita que dos buses carguen simultáneamente en la misma estación
constraint forall(b,d in B where b < d)(
    forall(i in 1..num_stops[b], j in 1..num_stops[d]
    where st_bi[b,i] == st_bi[d,j])(

        Zbdij[b,d,i,j] <= xbi[b,i] /\
        Zbdij[b,d,i,j] <= xbi[d,j] /\
        xbi[b,i] + xbi[d,j] <= Zbdij[b,d,i,j] + 1 /\

        tbi[b,i] >= tbi[d,j] + ctbi[d,j] + SM - M * zbdi[b,d,i,j] /\
        tbi[d,j] >= tbi[b,i] + ctbi[b,i] + SM - M * zbdi[d,b,j,i] /\

        zbdi[b,d,i,j] + zbdi[d,b,j,i] - (1 - Zbdij[b,d,i,j]) <= 1
    )
);

% -----------------------------
% E. ENERGÍA MÍNIMA REQUERIDA
% -----------------------------

% Garantiza que el bus reciba suficiente energía durante la ruta
constraint forall(b in B)(
    sum(i in 1..num_stops[b])(ebi[b,i]) >=
    sum(i in 1..num_stops[b])(D[b,i]) - Cmax + Cmin
);

% -----------------------------
% G. RESTRICCIÓN DE PADDING (LIMPIEZA)
% Fija a cero todas las variables para paradas más allá de num_stops[b]
% Esto mejora la eficiencia del solver eliminando variables "muertas"
% y es esencial para obtener resultados consistentes
% -----------------------------

constraint forall(b in B, i in num_stops[b]+1..max_stops) (
    cbi[b,i] = 0 /\
    ebi[b,i] = 0 /\
    ctbi[b,i] = 0 /\
    tbi[b,i] = 0 /\
    d_tbi[b,i] = 0 /\
    xbi[b,i] = 0
);

% Asegurar que st_bi tiene valores válidos en padding (no 0, pero no relevante)
% Las restricciones anteriores hacen que xbi[b,i]=0 para padding, entonces
% la restricción xst[st_bi[b,i]] >= xbi[b,i] se cumple trivialmente.

% -----------------------------
% H. FUNCIÓN OBJETIVO
% -----------------------------

% Lexicographic tie-breaker, still fully integer:
% 1) minimize number of installed stations
% 2) among ties, prefer the smallest indexed station set

% Weak bias: prefer stations marked in xst_pref among tied optimal solutions.
% Primary objective: minimize number of stations (dominant via TIE_BREAK_WEIGHT)
% Secondary bias: minimize sum of (1 - xst_pref[st]) * xst[st]
solve :: int_search([xbi[b,i] | b in B, i in 1..max_stops], input_order, indomain_min, complete)
    minimize sum(st in ST)(xst[st]);

% -----------------------------
% SALIDA DE RESULTADOS
% -----------------------------

output [
"Estaciones instaladas: ", show(xst), "\n",
"Total estaciones: ", show(sum(s in ST)(xst[s])), "\n",
"Desviacion total: ",
show(sum(b in B, i in 1..num_stops[b])(d_tbi[b,i])),
"\n"
];