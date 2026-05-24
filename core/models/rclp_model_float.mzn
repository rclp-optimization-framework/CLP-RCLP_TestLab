include "globals.mzn";

% -------------------------------
% PARAMETROS (FLOTANTE)
% -------------------------------

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

% -------------------------------
% VARIABLES RCLP (FLOTANTE)
% -------------------------------

array[B,S] of var 0.0..Cmax: c;
array[B,S] of var 0.0..Cmax: e;
array[B,S] of var 0.0..beta: ct;
array[B,S] of var 0.0..t_upper_bound: t;

array[B,S] of var 0.0..mu: dt;
array[B,S] of var 0..1: x;
array[ST] of var 0..1: xst;

array[B,B,S,S] of var 0..1: Z;
array[B,B,S,S] of var 0..1: z;
array[B,B,S,S] of var 0..1: z2;

% -------------------------------
% VARIABLES BACKUP
% -------------------------------

array[B,S] of var 0.0..Cmax: c_p;
array[B,S] of var 0.0..Cmax: e_p;
array[B,S] of var 0.0..beta: ct_p;
array[B,S] of var 0.0..t_upper_bound: t_p;

array[B,S] of var 0.0..mu: dt_p;
array[B,S] of var 0..1: x_p;
array[B,B,S,S] of var 0..1: Zpp;
array[B,B,S,S] of var 0..1: zp1;
array[B,B,S,S] of var 0..1: zp2;

% -------------------------------
% 1. CAPACIDAD BATERIA
% -------------------------------

constraint
forall(b in B, i in 2..num_stops[b])(
    Cmin <= c[b,i] /\
    c[b,i] + e[b,i] <= Cmax /\
    c[b,i] <= c[b,i-1] + e[b,i-1] - D[b,i] /\
    alpha * ct[b,i] >= e[b,i]
);

% -------------------------------
% 2. TIEMPO Y DESVIACION
% -------------------------------

constraint
forall(b in B, i in 2..num_stops[b])(
    t[b,i] >= t[b,i-1] + ct[b,i-1] + T[b,i] /\
    t[b,i] >= t[b,i-1] + ct[b,i-1] + SM * x[b,i-1] /\
    dt[b,i] >= t[b,i] - tau_bi[b,i] /\
    dt[b,i] >= tau_bi[b,i] - t[b,i] /\
    dt[b,i] <= mu /\
    ct[b,i] >= psi * x[b,i]
);

% -------------------------------
% 3. INSTALACION CARGADORES
% -------------------------------

constraint
forall(b in B, i in 1..num_stops[b])(
    beta * x[b,i] >= ct[b,i] /\
    xst[st_bi[b,i]] >= x[b,i]
);

% -------------------------------
% 4. NO SOLAPAMIENTO
% -------------------------------

constraint
forall(b,d in B where b!=d)(
forall(i in 1..num_stops[b], j in 1..num_stops[d] where st_bi[b,i]==st_bi[d,j])(
    Z[b,d,i,j] <= x[b,i] /\
    Z[b,d,i,j] <= x[d,j] /\
    x[b,i] + x[d,j] <= Z[b,d,i,j] + 1 /\
    t[b,i] >= t[d,j] + ct[d,j] + SM - M*z[b,d,i,j] /\
    t[d,j] >= t[b,i] + ct[b,i] + SM - M*z2[b,d,i,j] /\
    z[b,d,i,j] + z2[b,d,i,j] - (1 - Z[b,d,i,j]) <= 1
));

% -------------------------------
% 5. ENERGIA MINIMA
% -------------------------------

constraint
forall(b in B)(
    sum(i in 1..num_stops[b])(e[b,i])
    >=
    sum(i in 1..num_stops[b]-1)(D[b,i+1])
    - Cmax + Cmin
);

% -------------------------------
% OBJETIVO
% -------------------------------

solve minimize sum(s in ST)(xst[s]);

output [
"Estaciones instaladas: ", show(xst), "\n",
"Total estaciones: ", show(sum(s in ST)(xst[s])), "\n",
"Desviacion total: ",
show(sum(b in B, i in 1..max_stops)(dt[b,i])),
"\n"
];
