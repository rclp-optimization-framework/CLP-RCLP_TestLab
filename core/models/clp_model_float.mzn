% -----------------------------
% PARAMETROS DEL PROBLEMA (FLOTANTE)
% -----------------------------

int: num_buses;
int: num_stations;

set of int: B = 1..num_buses;
set of int: ST = 1..num_stations;

array[B] of int: num_stops;
int: max_stops;
set of int: S = 1..max_stops;

array[B,S] of int: st_bi;
array[B,S] of float: tau_bi;
array[B,S] of float: D;
array[B,S] of int: T;

float: tau_max = max([tau_bi[b,i] | b in B, i in 1..num_stops[b]]);
float: t_upper_bound = tau_max + M + beta + SM + mu;

float: Cmin;
float: Cmax;
float: alpha;
float: mu;
float: SM;
float: M;
float: beta;
float: psi;

% -----------------------------
% VARIABLES DEL MODELO (FLOTANTE)
% -----------------------------

array[B,S] of var 0.0..Cmax: cbi;
array[B,S] of var 0.0..Cmax: ebi;
array[B,S] of var 0.0..beta: ctbi;
array[B,S] of var 0.0..t_upper_bound: tbi;
array[B,S] of var 0.0..mu: d_tbi;

array[B,S] of var 0..1: xbi;
array[ST] of var 0..1: xst;
array[B,B,S,S] of var 0..1: Zbdij;
array[B,B,S,S] of var 0..1: zbdi;

% -----------------------------
% A. CAPACIDAD DE BATERIA
% -----------------------------

constraint forall(b in B) (
    cbi[b,1] = Cmax /\
    tbi[b,1] = tau_bi[b,1]
);

constraint forall(b in B, i in 1..num_stops[b]) (
    cbi[b,i] >= Cmin /\
    cbi[b,i] + ebi[b,i] <= Cmax /\
    alpha * ctbi[b,i] >= ebi[b,i]
);

constraint forall(b in B, i in 2..num_stops[b]) (
    cbi[b,i] <= cbi[b,i-1] + ebi[b,i-1] - D[b,i]
);

% -----------------------------
% B. RESTRICCIONES DE TIEMPO
% -----------------------------

constraint forall(b in B, i in 2..num_stops[b]) (
    tbi[b,i] >= tbi[b,i-1] + ctbi[b,i-1] + T[b,i] /\
    tbi[b,i] >= tbi[b,i-1] + ctbi[b,i-1] + SM * xbi[b,i-1]
);

constraint forall(b in B, i in 1..num_stops[b]) (
    d_tbi[b,i] >= tbi[b,i] - tau_bi[b,i] /\
    d_tbi[b,i] >= tau_bi[b,i] - tbi[b,i] /\
    d_tbi[b,i] <= mu /\
    ctbi[b,i] >= psi * xbi[b,i]
);

% -----------------------------
% C. INSTALACION DE CARGADORES
% -----------------------------

constraint forall(b in B, i in 1..num_stops[b]) (
    beta * xbi[b,i] >= ctbi[b,i] /\
    xst[st_bi[b,i]] >= xbi[b,i]
);

% -----------------------------
% D. NO SOLAPAMIENTO DE CARGAS
% -----------------------------

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
% E. ENERGIA MINIMA REQUERIDA
% -----------------------------

constraint forall(b in B)(
    sum(i in 1..num_stops[b])(ebi[b,i]) >=
    sum(i in 1..num_stops[b])(D[b,i]) - Cmax + Cmin
);

% -----------------------------
% G. RESTRICCION DE PADDING
% -----------------------------

constraint forall(b in B, i in num_stops[b]+1..max_stops) (
    cbi[b,i] = 0.0 /\
    ebi[b,i] = 0.0 /\
    ctbi[b,i] = 0.0 /\
    tbi[b,i] = 0.0 /\
    d_tbi[b,i] = 0.0 /\
    xbi[b,i] = 0
);

% -----------------------------
% H. FUNCION OBJETIVO
% -----------------------------

solve :: int_search([xbi[b,i] | b in B, i in 1..max_stops], input_order, indomain_min, complete)
    minimize sum(st in ST)(xst[st]);

output [
"Estaciones instaladas: ", show(xst), "\n",
"Total estaciones: ", show(sum(s in ST)(xst[s])), "\n",
"Desviacion total: ",
show(sum(b in B, i in 1..num_stops[b])(d_tbi[b,i])),
"\n"
];
