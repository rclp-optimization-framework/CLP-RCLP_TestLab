# Run Java MinimalTimetableDisruptions for cork instances and collect results
# Usage:
#   .\scripts\run_java_cork_runs.ps1 [-Dataset cork1|cork2|cork3|all]

param(
    [ValidateSet('cork1', 'cork2', 'cork3', 'all')]
    [string]$Dataset = 'all',
    [switch]$SkipCompile
)

$repoRoot = Split-Path -Parent $PSScriptRoot
$codeDir = Join-Path $repoRoot "external\jits2022\Code\MinimalTimetableDisruptions"
$dataDir = Join-Path $repoRoot "external\jits2022\Code\data"
$cplexJar = "C:\Program Files\IBM\ILOG\CPLEX_Studio2212\cplex\lib\cplex.jar"
$cplexLibPath = "C:\Program Files\IBM\ILOG\CPLEX_Studio2212\cplex\bin\x64_win64"
$gsonJar = Join-Path $codeDir "jars\gson-2.6.2.jar"

if (-not (Test-Path $cplexJar)) { Write-Host "CPLEX jar not found at $cplexJar. Update path in the script." ; exit 1 }
if (-not (Test-Path $codeDir)) { Write-Host "Code dir not found: $codeDir" ; exit 1 }

Push-Location $codeDir
if (-not $SkipCompile) {
    # Build files.lst (PowerShell-friendly)
    if (Test-Path files.lst) { Remove-Item files.lst -Force }
    Get-ChildItem -Recurse -Filter *.java -File | ForEach-Object { $_.FullName } | Set-Content files.lst
    # Compile: collect file list and pass as arguments to javac
    $fileArgs = Get-Content files.lst
    if ($fileArgs.Count -eq 0) { Write-Host "No Java source files found" ; Pop-Location ; exit 1 }
    & javac -classpath "$cplexJar;$gsonJar" -d bin @fileArgs
    if ($LASTEXITCODE -ne 0) { Write-Host "Compilation failed (javac exit code $LASTEXITCODE)" ; Pop-Location ; exit $LASTEXITCODE }
}

# Run only the requested cork experiment parameter files, in the requested order.
$paramPaths = @(
    (Join-Path $dataDir "experiment_parameters_cork1_20_0.txt"),
    (Join-Path $dataDir "experiment_parameters_cork1_20_5.txt"),
    (Join-Path $dataDir "experiment_parameters_cork1_20_10.txt"),
    (Join-Path $dataDir "experiment_parameters_cork1_20_20.txt"),
    (Join-Path $dataDir "experiment_parameters_cork2_20_0.txt"),
    (Join-Path $dataDir "experiment_parameters_cork2_20_5.txt"),
    (Join-Path $dataDir "experiment_parameters_cork2_20_10.txt"),
    (Join-Path $dataDir "experiment_parameters_cork2_20_20.txt"),
    (Join-Path $dataDir "experiment_parameters_cork3_20_0.txt"),
    (Join-Path $dataDir "experiment_parameters_cork3_20_5.txt"),
    (Join-Path $dataDir "experiment_parameters_cork3_20_10.txt"),
    (Join-Path $dataDir "experiment_parameters_cork3_20_20.txt")
)
$paramPaths = switch ($Dataset) {
    'cork1' { $paramPaths | Where-Object { $_ -match 'experiment_parameters_cork1_20_' } }
    'cork2' { $paramPaths | Where-Object { $_ -match 'experiment_parameters_cork2_20_' } }
    'cork3' { $paramPaths | Where-Object { $_ -match 'experiment_parameters_cork3_20_' } }
    default { $paramPaths }
}
$paramFiles = foreach ($path in $paramPaths) {
    if (Test-Path $path) { Get-Item $path }
}
if ($paramFiles.Count -eq 0) { Write-Host "No cork experiment parameter files found in $dataDir" ; Pop-Location ; exit 0 }

$results = @()
foreach ($pf in $paramFiles) {
    Write-Host "Running experiment file: $($pf.Name)"
    $outName = "output_$($pf.BaseName)_java.txt"
    $outPath = Join-Path $dataDir $outName
    # Execute Java with proper argument array to avoid shell parsing issues
    $timestamp = (Get-Date).ToString()
    $javaArgs = @("-Djava.library.path=$cplexLibPath", "-Dfile.encoding=UTF-8", "-cp", "bin;$cplexJar;$gsonJar", "core.Executor", $pf.FullName, $timestamp)
    # Create a cleaned copy of the parameter file without blank/comment-only lines to avoid parsing errors
    $cleanParam = "$($pf.FullName).clean"
    Get-Content $pf.FullName | Where-Object { $_.Trim() -ne "" } | Set-Content $cleanParam
    # replace the parameter file argument with the cleaned path
    $javaArgs[-2] = $cleanParam
    Write-Host "Executing: java $($javaArgs -join ' ')"
    & java @javaArgs > $outPath
    # remove temporary cleaned file
    Remove-Item -Force $cleanParam -ErrorAction SilentlyContinue

    # parse selected station info from output
    $outText = Get-Content $outPath -Raw -ErrorAction SilentlyContinue
    $selId = $null; $selName = $null; $evidence = $null
    if ($outText) {
        if ($outText -match "selected station id[:\s]*([0-9]+)") { $selId = $matches[1] }
        if ($outText -match "selected station name[:\s]*(.+)") { $selName = $matches[1].Trim() }
        # fallback: look for pattern 'x=1.0' and capture nearby lines
        if ($outText -match "x=1.0") {
            $lines = $outText -split "\r?\n"
            $idx = [Array]::IndexOf($lines, ($lines | Where-Object { $_ -match "x=1.0" } | Select-Object -First 1))
            if ($idx -ge 0) {
                $start = [Math]::Max(0, $idx-5); $end = [Math]::Min($lines.Length-1, $idx+5)
                $evidence = ($lines[$start..$end] -join "\n")
            }
        }
    }

    # determine dataset folder and counts
    $firstLine = (Get-Content $pf.FullName -TotalCount 1) -split "#" | Select-Object -First 1
    $datasetName = $firstLine.Trim()
    $dsPath = Join-Path $dataDir $datasetName
    $stationsCount = "N/A"; $busesCount = "N/A"
    if (Test-Path (Join-Path $dsPath "stations_input.csv")) {
        $stations = Get-Content (Join-Path $dsPath "stations_input.csv") | Where-Object { $_.Trim() -ne "" }
        # assume first line is header
        $stationsCount = [Math]::Max(0, $stations.Count - 1)
    }
    if ($datasetName -eq 'cork-1-line') { $busesCount = 1 }
    elseif ($datasetName -eq 'cork-2-lines') { $busesCount = 2 }
    elseif ($datasetName -eq 'cork-3-lines') { $busesCount = 3 }

    $results += [PSCustomObject]@{
        paramFile = $pf.FullName
        outputFile = $outPath
        dataset = $datasetName
        selectedStationId = $selId
        selectedStationName = $selName
        stations = $stationsCount
        buses = $busesCount
        evidence = $evidence
    }
}
Pop-Location

# write Markdown
$mdPath = Join-Path $repoRoot "JAVA_CPLEX_CLP_cork_results.md"
"## Results`n" | Out-File $mdPath -Encoding utf8
# group by variant inferred from param file name (e.g., 20_0)
$grouped = $results | Group-Object { if ($_.paramFile -match "20[_-]0") { '20_0' } elseif ($_.paramFile -match "20[_-]5") { '20_5' } elseif ($_.paramFile -match "20[_-]10") { '20_10' } elseif ($_.paramFile -match "20[_-]20") { '20_20' } else { 'other' } }
foreach ($g in $grouped) {
    "### Variant $($g.Name)`n" | Out-File $mdPath -Append -Encoding utf8
    foreach ($r in $g.Group) {
        "- file: $($r.outputFile)`n- dataset: $($r.dataset)`n- selected station id: $($r.selectedStationId)`n- selected station name: $($r.selectedStationName)`n- stations: $($r.stations)`n- buses: $($r.buses)`n- evidence lines: " | Out-File $mdPath -Append -Encoding utf8
        if ($r.evidence) { ($r.evidence -replace '```','') | Out-File $mdPath -Append -Encoding utf8 }
        "`n" | Out-File $mdPath -Append -Encoding utf8
    }
}
Write-Host "Results written to $mdPath"