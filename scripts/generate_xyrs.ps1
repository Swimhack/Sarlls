# Requires: PowerShell 5+
param(
    [Parameter(Mandatory=$true)] [string]$BomCsv,
    [Parameter(Mandatory=$true)] [string]$CplCsv,
    [Parameter(Mandatory=$true)] [string]$OutFile
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function ConvertTo-Mils([double]$mm) {
    return [math]::Round($mm * 39.3701, 2)
}

function Get-MountType([string]$package) {
    if ([string]::IsNullOrWhiteSpace($package)) { return 1 }
    $pkg = $package.ToLowerInvariant()
    if ($pkg -match '0603|0402|0805|1206|smd|smt|qfn|qfp|tqfp|soic|sop|dfn|bga|wroom') {
        return 1 # SMD
    }
    if ($pkg -match 'tht|pth|to-\d+|do-\d+|dip|t\s?h\s?t') { return 2 } # PTH
    return 1
}

# Load BOM
$bom = Import-Csv -Path $BomCsv
# Build map: designator -> { Value, Footprint, MPN }
$bomByDesignator = @{}
foreach ($row in $bom) {
    $d = ($row.Designator).Trim()
    if (-not [string]::IsNullOrWhiteSpace($d)) {
        $bomByDesignator[$d] = [pscustomobject]@{
            Value = $row.Value
            Footprint = $row.Package
            MPN = $row.MPN
        }
    }
}

# Load CPL
$cpl = Import-Csv -Path $CplCsv

# Prepare XYRS output (tab-delimited)
$out = New-Object System.Collections.Generic.List[object]
# Header
$out.Add("Designator`tX-Loc`tY-Loc`tRotation`tSide`tType`tX-Size`tY-Size`tValue`tFootprint`tPopulate`tMPN")

foreach ($p in $cpl) {
    $d = ($p.Designator).Trim()
    if ([string]::IsNullOrWhiteSpace($d)) { continue }

    $bomInfo = $null
    if ($bomByDesignator.ContainsKey($d)) { $bomInfo = $bomByDesignator[$d] }

    # Coordinates from KiCad-style CPL likely in mm
    $xMils = ConvertTo-Mils([double]$p.'Mid X')
    $yMils = ConvertTo-Mils([double]$p.'Mid Y')

    # Layer to Side
    $layer = ($p.Layer).ToString().ToLowerInvariant()
    $side = if ($layer -eq 'top') { '1' } elseif ($layer -eq 'bottom') { '2' } else { '1' }

    # Rotation in degrees as-is
    $rotation = [string]$p.Rotation

    # Type: infer from footprint/package
    $footprint = if ($bomInfo) { [string]$bomInfo.Footprint } else { '' }
    $type = Get-MountType($footprint)

    # Sizes unknown; leave blank
    $xSize = ''
    $ySize = ''

    $value = if ($bomInfo) { [string]$bomInfo.Value } else { '' }
    $mpn = if ($bomInfo) { [string]$bomInfo.MPN } else { '' }

    $populate = '1'

    $line = @(
        $d,
        ('{0:F2}' -f $xMils),
        ('{0:F2}' -f $yMils),
        $rotation,
        $side,
        $type,
        $xSize,
        $ySize,
        $value,
        $footprint,
        $populate,
        $mpn
    ) -join "`t"

    $out.Add($line) | Out-Null
}

[IO.File]::WriteAllLines($OutFile, $out)
Write-Host "Wrote XYRS to $OutFile" -ForegroundColor Green




