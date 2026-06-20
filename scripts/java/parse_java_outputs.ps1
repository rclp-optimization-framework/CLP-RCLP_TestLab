# Parse Java output files and produce a consolidated Markdown results file for Cork-1/2/3
$root = Split-Path -Parent $PSScriptRoot
$dataDir = Join-Path $root "external\jits2022\Code\data"

function Get-VariantOrder([string]$name) {
    if ($name -match 'cork1|cork-1') { return 1 }
    if ($name -match 'cork2|cork-2') { return 2 }
    if ($name -match 'cork3|cork-3') { return 3 }
    return 99
}

function Get-InstanceName([string]$fileName) {
    if ($fileName -match 'output_experiment_parameters_(cork[123]_[^_]+(?:_[^_]+)?)_java\.txt$') {
        return $matches[1]
    }
    if ($fileName -match 'output_experiment_parameters_(cork[123])_java\.txt$') {
        return $matches[1]
    }
    if ($fileName -match 'output_cork-(1-line|2-lines|3-lines)_(.+)\.txt$') {
        return "$($matches[1]) $($matches[2])"
    }
    return $fileName
}

function Get-DatasetFolder([string]$fileName) {
    if ($fileName -match 'cork1') { return 'cork-1-line' }
    if ($fileName -match 'cork2') { return 'cork-2-lines' }
    if ($fileName -match 'cork3') { return 'cork-3-lines' }
    if ($fileName -match 'cork-1-line') { return 'cork-1-line' }
    if ($fileName -match 'cork-2-lines') { return 'cork-2-lines' }
    if ($fileName -match 'cork-3-lines') { return 'cork-3-lines' }
    return 'unknown'
}

function Get-StationSelections([string[]]$lines) {
    $selections = @()
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match '^Station\s+(\d+)\s*/\s*(.+)$') {
            $stationId = [int]$matches[1]
            $stationName = $matches[2].Trim()
            # the station block can be long; search well past the station header for the selection flag
            $windowEnd = [Math]::Min($lines.Count - 1, $i + 40)
            for ($j = $i; $j -le $windowEnd; $j++) {
                if ($lines[$j] -match '^\s*x\s*=\s*1(?:\.0+)?\s*$') {
                    $evidenceStart = [Math]::Max(0, $i - 1)
                    $evidenceEnd = [Math]::Min($lines.Count - 1, $j + 1)
                    $evidence = ($lines[$evidenceStart..$evidenceEnd] -join "`n")
                    $selections += [PSCustomObject]@{
                        id = $stationId
                        name = $stationName
                        evidence = $evidence
                        lineIndex = $i
                    }
                    break
                }
            }
        }
    }

    # Keep first occurrence per station id to avoid repeated buses/stops duplicating the same charger location.
    $unique = @{}
    foreach ($sel in $selections) {
        if (-not $unique.ContainsKey($sel.id)) {
            $unique[$sel.id] = $sel
        }
    }

    return $unique.Values | Sort-Object @{ Expression = 'lineIndex'; Ascending = $true }, @{ Expression = 'id'; Ascending = $true }
}

$outputFiles = Get-ChildItem -Path $dataDir -File | Where-Object {
    $_.Name -match '^output_experiment_parameters_cork[123]_20_.*_java\.txt$'
} | Sort-Object {
    $order = Get-VariantOrder $_.Name
    @{ Expression = $order; Ascending = $true }
}, Name

$results = @()
foreach ($f in $outputFiles) {
    $lines = Get-Content $f.FullName
    $dataset = Get-DatasetFolder $f.Name
    $instanceName = Get-InstanceName $f.Name
    $stationSelections = Get-StationSelections $lines

    $stationsCount = "N/A"
    $busesCount = "N/A"
    $datasetPath = Join-Path $dataDir $dataset
    if (Test-Path (Join-Path $datasetPath "stations_input.csv")) {
        $stations = Get-Content (Join-Path $datasetPath "stations_input.csv") | Where-Object { $_.Trim() -ne "" }
        $stationsCount = [Math]::Max(0, $stations.Count - 1)
    }
    if ($dataset -eq 'cork-1-line') { $busesCount = 1 }
    elseif ($dataset -eq 'cork-2-lines') { $busesCount = 2 }
    elseif ($dataset -eq 'cork-3-lines') { $busesCount = 3 }

    $results += [PSCustomObject]@{
        file = $f.FullName
        instanceName = $instanceName
        dataset = $dataset
        order = Get-VariantOrder $f.Name
        stations = $stationsCount
        buses = $busesCount
        selections = $stationSelections
    }
}

$md = Join-Path $root "JAVA_CPLEX_CLP_cork_results.md"
$mdLines = New-Object System.Collections.Generic.List[string]
$mdLines.Add('## Results')
$mdLines.Add('')

foreach ($group in ($results | Group-Object order | Sort-Object Name)) {
    $variantTitle = switch ([int]$group.Name) {
        1 { 'Cork-1' }
        2 { 'Cork-2' }
        3 { 'Cork-3' }
        default { 'Other' }
    }
    $mdLines.Add("### $variantTitle")
    $mdLines.Add('')

    foreach ($r in ($group.Group | Sort-Object file)) {
        $mdLines.Add("- file: $($r.file)")
        $mdLines.Add("- instance: $($r.instanceName)")
        $mdLines.Add("- dataset: $($r.dataset)")
        $mdLines.Add("- stations: $($r.stations)")
        $mdLines.Add("- buses: $($r.buses)")

        if ($r.selections.Count -eq 0) {
            $mdLines.Add("- selected station id: (none)")
            $mdLines.Add("- selected station name: (none)")
            $mdLines.Add("- evidence lines:")
            $mdLines.Add('')
            continue
        }

        foreach ($sel in $r.selections) {
            $mdLines.Add("- selected station id: $($sel.id)")
            $mdLines.Add("- selected station name: $($sel.name)")
            $mdLines.Add("- evidence lines:")
            if ($sel.evidence) {
                foreach ($line in ($sel.evidence -split "`n")) {
                    $mdLines.Add($line)
                }
            }
            $mdLines.Add('')
        }
    }
}

$mdLines | Set-Content $md -Encoding utf8
Write-Host "Parsed outputs and wrote $md"