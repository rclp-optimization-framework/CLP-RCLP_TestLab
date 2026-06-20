# Java CPLEX CLP - Cork results

Solver: **CPLEX** via `core.Executor` (original JITS Java). Model: CLP / chargers objective, Laura extension, robust warm-start chain.

## Results

### Cork-1

#### Variant 20_0

- file: external/jits2022/Code/data/output_cork-1-line_chargers_120000_20_0_4_1_1_0_0_0_0_4_31-05-2026-11-24-34-p--m-_4_0.txt
- stations: 579
- buses: 4
- selected station id: 11
- selected station name: Togher Road (Deanwood)
- evidence lines: station block around line 122, x=1.0 around line 129

~~~
Bus 0, Stop 11
Station 11 / Togher Road (Deanwood)
original[0][11]=07:24 / 26640
 arrival=7:24 / 26623.0
 c=116799.0
 e=3201.0
 ct=60.0
 xBStop=1.0
 x=1.0

~~~

#### Variant 20_5

- file: external/jits2022/Code/data/output_cork-1-line_chargers_120000_20_5_4_1_1_0_0_0_0_4_31-05-2026-11-23-45-p--m-_3_0.txt
- stations: 579
- buses: 3
- selected station id: 19
- selected station name: CUH (A and E)
- evidence lines: station block around line 2721, x=1.0 around line 2728

~~~
Bus 0, Stop 271
Station 19 / CUH (A and E)
original[0][271]=16:20 / 58800
 arrival=16:24 / 59040.0
 c=15000.0
 e=16124.0
 ct=96.744
 xBStop=1.0
 x=1.0

~~~

#### Variant 20_10

- file: external/jits2022/Code/data/output_cork-1-line_chargers_120000_20_10_4_1_1_0_1_0_0_4_01-06-2026-01-09-46_3_0.txt
- stations: 579
- buses: 3
- selected station id: 0
- selected station name: St. Patrick St (Brown Thomas B)
- evidence lines: station block around line 8059, x=1.0 around line 8066

~~~
Bus 0, Stop 503
Station 0 / St. Patrick St (Brown Thomas B)
original[0][503]=23:40 / 85200
 arrival=23:44 / 85440.0
 c=15000.0
 e=81000.0
 ct=486.0
 xBStop=1.0
 x=1.0
backup arrival=23:44 / 85440.0
~~~

- selected station id: 19
- selected station name: CUH (A and E)
- evidence lines: station block around line 315, x=1.0 around line 322

~~~
Bus 0, Stop 19
Station 19 / CUH (A and E)
original[0][19]=07:40 / 27600
 arrival=7:36 / 27360.0
 c=47888.0
 e=0.0
 ct=60.0
 xBStop=1.0
 x=1.0
backup arrival=7:36 / 27360.0
~~~

#### Variant 20_20

- file: external/jits2022/Code/data/output_cork-1-line_chargers_120000_20_20_4_1_1_0_1_0_0_4_01-06-2026-01-14-28_3_0.txt
- stations: 579
- buses: 3
- selected station id: 0
- selected station name: St. Patrick St (Brown Thomas B)
- evidence lines: station block around line 667, x=1.0 around line 674

~~~
Bus 0, Stop 41
Station 0 / St. Patrick St (Brown Thomas B)
original[0][41]=08:20 / 30000
 arrival=8:16 / 29760.0
 c=73546.0
 e=0.0
 ct=60.0
 xBStop=1.0
 x=1.0
backup arrival=8:16 / 29760.0
~~~

- selected station id: 19
- selected station name: CUH (A and E)
- evidence lines: station block around line 15469, x=1.0 around line 15476

~~~
Bus 1, Stop 462
Station 19 / CUH (A and E)
original[1][462]=22:40 / 81600
 arrival=22:43 / 81804.0
 c=28062.0
 e=0.0
 ct=60.0
 xBStop=1.0
 x=1.0
backup arrival=22:44 / 81840.0
~~~

### Cork-2

#### Variant 20_0

- file: external/jits2022/Code/data/output_cork-2-lines_chargers_120000_20_0_4_1_1_0_0_0_0_4_31-05-2026-10-58-36-p--m-_10_0.txt
- stations: 579
- buses: 10
- selected station id: 39
- selected station name: South Mall (VHI House Stop A)
- evidence lines: station block around line 838, x=1.0 around line 845

~~~
Bus 0, Stop 82
Station 39 / South Mall (VHI House Stop A)
original[0][82]=09:35 / 34500
 arrival=9:37 / 34633.0
 c=94202.0
 e=10000.0
 ct=60.0
 xBStop=1.0
 x=1.0

~~~

#### Variant 20_5

- file: external/jits2022/Code/data/output_cork-2-lines_chargers_120000_20_5_4_1_1_0_0_0_0_4_01-06-2026-01-18-49_9_0.txt
- stations: 579
- buses: 9
- selected station id: 39
- selected station name: South Mall (VHI House Stop A)
- evidence lines: station block around line 837, x=1.0 around line 844

~~~
Bus 0, Stop 82
Station 39 / South Mall (VHI House Stop A)
original[0][82]=09:35 / 34500
 arrival=9:31 / 34260.0
 c=94202.0
 e=25798.0
 ct=241.0
 xBStop=1.0
 x=1.0

~~~

#### Variant 20_10

- file: external/jits2022/Code/data/output_cork-2-lines_chargers_120000_20_10_4_1_1_0_0_0_0_4_01-06-2026-02-30-07_8_0.txt
- stations: 579
- buses: 8
- selected station id: 39
- selected station name: South Mall (VHI House Stop A)
- evidence lines: station block around line 1256, x=1.0 around line 1263

~~~
Bus 0, Stop 124
Station 39 / South Mall (VHI House Stop A)
original[0][124]=11:15 / 40500
 arrival=11:17 / 40614.0
 c=81140.0
 e=38860.0
 ct=233.16
 xBStop=1.0
 x=1.0

~~~

#### Variant 20_20

- file: (no complete output)
- stations: 579
- buses: N/A
- selected station id: (none parsed)
- selected station name: (none parsed)
- evidence lines: _status: missing_

### Cork-3

#### Variant 20_0

- file: external/jits2022/Code/data/output_cork-3-lines_chargers_120000_20_0_4_1_1_0_0_0_0_4_31-05-2026-11-25-35-p--m-_15_0.txt
- stations: 579
- buses: 15
- selected station id: 39
- selected station name: South Mall (VHI House Stop A)
- evidence lines: station block around line 2943, x=1.0 around line 2950

~~~
Bus 0, Stop 292
Station 39 / South Mall (VHI House Stop A)
original[0][292]=16:15 / 58500
 arrival=16:11 / 58260.0
 c=28892.0
 e=71104.0
 ct=426.624
 xBStop=1.0
 x=1.0

~~~

- selected station id: 78
- selected station name: St. Patrick Street (Marks and Spencer)
- evidence lines: station block around line 19881, x=1.0 around line 19888

~~~
Bus 4, Stop 117
Station 78 / St. Patrick Street (Marks and Spencer)
original[4][117]=09:42 / 34920
 arrival=9:38 / 34680.0
 c=20924.66666666667
 e=25666.666666666664
 ct=154.0
 xBStop=1.0
 x=1.0

~~~

#### Variant 20_5

- file: (no complete output)
- stations: 579
- buses: N/A
- selected station id: (none parsed)
- selected station name: (none parsed)
- evidence lines: _status: missing_

#### Variant 20_10

- file: (no complete output)
- stations: 579
- buses: N/A
- selected station id: (none parsed)
- selected station name: (none parsed)
- evidence lines: _status: missing_

#### Variant 20_20

- file: (no complete output)
- stations: 579
- buses: N/A
- selected station id: (none parsed)
- selected station name: (none parsed)
- evidence lines: _status: missing_

