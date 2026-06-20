# Run Java CPLEX cork experiments (if needed) and write JAVA_CPLEX_CLP_cork_results.md at repo root.
param(
    [switch]$SkipRun,
    [switch]$ForceRun
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$dataDir = Join-Path $repoRoot 'external\jits2022\Code\data'
$codeDir = Join-Path $repoRoot 'external\jits2022\Code'
$mtdDir = Join-Path $codeDir 'MinimalTimetableDisruptions'
$cplexJar = 'C:\Program Files\IBM\ILOG\CPLEX_Studio2212\cplex\lib\cplex.jar'
$cplexLibPath = 'C:\Program Files\IBM\ILOG\CPLEX_Studio2212\cplex\bin\x64_win64'
$gsonJar = Join-Path $mtdDir 'jars\gson-2.6.2.jar'

$instances = @(
    @{ cork = 'Cork-1'; folder = 'cork-1-line'; param = 'experiment_parameters_cork1_20_0.txt'; variant = '20_0'; rest = '0' },
    @{ cork = 'Cork-1'; folder = 'cork-1-line'; param = 'experiment_parameters_cork1_20_5.txt'; variant = '20_5'; rest = '5' },
    @{ cork = 'Cork-1'; folder = 'cork-1-line'; param = 'experiment_parameters_cork1_20_10.txt'; variant = '20_10'; rest = '10' },
    @{ cork = 'Cork-1'; folder = 'cork-1-line'; param = 'experiment_parameters_cork1_20_20.txt'; variant = '20_20'; rest = '20' },
    @{ cork = 'Cork-2'; folder = 'cork-2-lines'; param = 'experiment_parameters_cork2_20_0.txt'; variant = '20_0'; rest = '0' },
    @{ cork = 'Cork-2'; folder = 'cork-2-lines'; param = 'experiment_parameters_cork2_20_5.txt'; variant = '20_5'; rest = '5' },
    @{ cork = 'Cork-2'; folder = 'cork-2-lines'; param = 'experiment_parameters_cork2_20_10.txt'; variant = '20_10'; rest = '10' },
    @{ cork = 'Cork-2'; folder = 'cork-2-lines'; param = 'experiment_parameters_cork2_20_20.txt'; variant = '20_20'; rest = '20' },
    @{ cork = 'Cork-3'; folder = 'cork-3-lines'; param = 'experiment_parameters_cork3_20_0.txt'; variant = '20_0'; rest = '0' },
    @{ cork = 'Cork-3'; folder = 'cork-3-lines'; param = 'experiment_parameters_cork3_20_5.txt'; variant = '20_5'; rest = '5' },
    @{ cork = 'Cork-3'; folder = 'cork-3-lines'; param = 'experiment_parameters_cork3_20_10.txt'; variant = '20_10'; rest = '10' },
    @{ cork = 'Cork-3'; folder = 'cork-3-lines'; param = 'experiment_parameters_cork3_20_20.txt'; variant = '20_20'; rest = '20' }
)

function Get-OutputPattern([string]$folder, [string]$rest) {
    # PrinterMTD label: folder_chargers_120000_{modelSpeed}_{restTime}_{dtmax}_...
    return "output_${folder}_chargers_120000_20_${rest}_4_"
}

function Test-CompleteOutput([string]$path) {
    if (-not (Test-Path $path)) { return $false }
    if ((Get-Item $path).Length -lt 5000) { return $false }
    $text = Get-Content $path -Raw
    return ($text -match 'Station\s+\d+\s*/' -and $text -match 'x=1\.0')
}

function Get-StationSelections([string[]]$lines) {
    $selections = @()
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match '^Station\s+(\d+)\s*/\s*(.+)$') {
            $stationId = [int]$matches[1]
            $stationName = $matches[2].Trim()
            $windowEnd = [Math]::Min($lines.Count - 1, $i + 12)
            for ($j = $i; $j -le $windowEnd; $j++) {
                if ($lines[$j] -match '^\s*x\s*=\s*1(?:\.0+)?\s*$') {
                    $hasCharge = $false
                    for ($k = $i; $k -le $windowEnd; $k++) {
                        if ($lines[$k] -match '^\s*ct\s*=\s*[1-9]' -or $lines[$k] -match '^\s*e\s*=\s*[1-9]' -or $lines[$k] -match '^\s*xBStop\s*=\s*1') {
                            $hasCharge = $true
                            break
                        }
                    }
                    if (-not $hasCharge) { continue }
                    $evidenceStart = [Math]::Max(0, $i - 1)
                    $evidenceEnd = [Math]::Min($lines.Count - 1, $j + 1)
                    $selections += [PSCustomObject]@{
                        id = $stationId
                        name = $stationName
                        lineStation = $i + 1
                        lineX = $j + 1
                        evidence = ($lines[$evidenceStart..$evidenceEnd] -join "`n")
                    }
                    break
                }
            }
        }
    }
    $unique = @{}
    foreach ($sel in $selections) {
        if (-not $unique.ContainsKey($sel.id)) { $unique[$sel.id] = $sel }
    }
    return ,@($unique.Values | Sort-Object id)
}

function Get-Counts([string]$outputPath, [string]$datasetPath) {
    $stations = 579
    $buses = 'N/A'
    $stationsFile = Join-Path $datasetPath 'stations_input.csv'
    if (Test-Path $stationsFile) {
        $rows = Get-Content $stationsFile | Where-Object { $_.Trim() -ne '' }
        $stations = [Math]::Max(0, $rows.Count - 1)
    }
    if ($outputPath -and (Test-Path $outputPath)) {
        $lines = Get-Content $outputPath -ErrorAction SilentlyContinue
        $busLines = $lines | Where-Object { $_ -match '^Bus \d+:\s+\d+$' }
        if ($busLines) { $buses = $busLines.Count }
        elseif ($lines -match '^Bus 0$') {
            $buses = ($lines | Where-Object { $_ -match '^Bus \d+$' }).Count
        }
    }
    return @{ stations = $stations; buses = $buses }
}

function Find-BestOutput([string]$pattern) {
    $candidates = Get-ChildItem -Path $dataDir -File |
        Where-Object { $_.Name -like "${pattern}*" -and $_.Name -like 'output_*' } |
        Where-Object { Test-CompleteOutput $_.FullName }
    if (-not $candidates) { return $null }
    # Prefer primary solve output (..._0_0_0_0_4_...); fall back to robust phase (..._0_1_0_0_4_...).
    $primary = $candidates | Where-Object { $_.Name -match '_0_0_0_0_4_' } | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($primary) { return $primary }
    $robust = $candidates | Where-Object { $_.Name -match '_0_1_0_0_4_' } | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($robust) { return $robust }
    return $candidates | Sort-Object LastWriteTime -Descending | Select-Object -First 1
}

function Invoke-JavaExperiment([string]$paramFile) {
    # Use UTF-8 without BOM so Java does not prefix dataset folder with U+FEFF.
    $cleanParam = "$paramFile.clean"
    $lines = Get-Content $paramFile | Where-Object { $_.Trim() -ne '' }
    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllLines($cleanParam, $lines, $utf8NoBom)
    $session = (Get-Date).ToString('dd-MM-yyyy-HH-mm-ss')
    $javaArgs = @(
        "-Djava.library.path=$cplexLibPath",
        '-Dfile.encoding=UTF-8',
        '-cp', "bin;$cplexJar;$gsonJar",
        'core.Executor', $cleanParam, $session
    )
    Write-Host ">> java $($javaArgs -join ' ')"
    & java @javaArgs
    Remove-Item -Force $cleanParam -ErrorAction SilentlyContinue
}

if (-not $SkipRun) {
    if (-not (Test-Path $cplexJar)) { throw "CPLEX not found: $cplexJar" }
    Push-Location $mtdDir
    if (Test-Path files.lst) { Remove-Item files.lst -Force }
    Get-ChildItem -Recurse -Filter *.java -File | ForEach-Object { $_.FullName } | Set-Content files.lst
    $fileArgs = Get-Content files.lst
    & javac -classpath "$cplexJar;$gsonJar" -d bin @fileArgs
    if ($LASTEXITCODE -ne 0) { Pop-Location; throw "javac failed with exit $LASTEXITCODE" }

    foreach ($inst in $instances) {
        $pattern = Get-OutputPattern $inst.folder $inst.rest
        $existing = Find-BestOutput $pattern
        if ($ForceRun -or -not $existing) {
            $paramPath = Join-Path $dataDir $inst.param
            if (-not (Test-Path $paramPath)) { Write-Warning "Missing param file $paramPath"; continue }
            Write-Host "Running $($inst.cork) variant $($inst.variant) ..."
            Invoke-JavaExperiment $paramPath
        } else {
            Write-Host "Skip run $($inst.cork) $($inst.variant) - output exists: $($existing.Name)"
        }
    }
    Pop-Location
}

$parsed = @()
foreach ($inst in $instances) {
    $pattern = Get-OutputPattern $inst.folder $inst.rest
    $file = Find-BestOutput $pattern
    $relPath = if ($file) { $file.FullName.Substring($repoRoot.Length).TrimStart('\', '/') -replace '\\', '/' } else { '(no complete output)' }
    $datasetPath = Join-Path $dataDir $inst.folder

    if (-not $file) {
        $parsed += [PSCustomObject]@{
            cork = $inst.cork
            variant = $inst.variant
            file = $relPath
            stations = (Get-Counts '' $datasetPath).stations
            buses = (Get-Counts '' $datasetPath).buses
            selections = @()
            status = 'missing'
        }
        continue
    }

    $lines = Get-Content $file.FullName
    $counts = Get-Counts $file.FullName $datasetPath
    $selections = Get-StationSelections $lines
    $parsed += [PSCustomObject]@{
        cork = $inst.cork
        variant = $inst.variant
        file = $relPath
        stations = $counts.stations
        buses = $counts.buses
        selections = $selections
        status = if ($selections.Count -gt 0) { 'ok' } else { 'no_selection' }
    }
}

$mdPath = Join-Path $repoRoot 'JAVA_CPLEX_CLP_cork_results.md'
$sb = New-Object System.Text.StringBuilder
[void]$sb.AppendLine('# Java CPLEX CLP - Cork results')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('Solver: **CPLEX** via `core.Executor` (original JITS Java). Model: CLP / chargers objective, Laura extension, robust warm-start chain.')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('## Results')
[void]$sb.AppendLine('')

$currentCork = ''
foreach ($row in $parsed) {
    if ($row.cork -ne $currentCork) {
        $currentCork = $row.cork
        [void]$sb.AppendLine("### $currentCork")
        [void]$sb.AppendLine('')
    }
    [void]$sb.AppendLine("#### Variant $($row.variant)")
    [void]$sb.AppendLine('')
    [void]$sb.AppendLine("- file: $($row.file)")
    [void]$sb.AppendLine("- stations: $($row.stations)")
    [void]$sb.AppendLine("- buses: $($row.buses)")
    if ($row.selections.Count -eq 0) {
        [void]$sb.AppendLine("- selected station id: (none parsed)")
        [void]$sb.AppendLine("- selected station name: (none parsed)")
        [void]$sb.AppendLine("- evidence lines: _status: $($row.status)_")
        [void]$sb.AppendLine('')
        continue
    }
    foreach ($sel in $row.selections) {
        [void]$sb.AppendLine("- selected station id: $($sel.id)")
        [void]$sb.AppendLine("- selected station name: $($sel.name)")
        [void]$sb.AppendLine("- evidence lines: station block around line $($sel.lineStation), x=1.0 around line $($sel.lineX)")
        [void]$sb.AppendLine('')
        [void]$sb.AppendLine('~~~')
        [void]$sb.AppendLine($sel.evidence)
        [void]$sb.AppendLine('~~~')
        [void]$sb.AppendLine('')
    }
}

$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText($mdPath, $sb.ToString(), $utf8NoBom)
Write-Host "Wrote $mdPath"
