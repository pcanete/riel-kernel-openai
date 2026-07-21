param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("session_start.py", "guard.py", "audit.py")]
    [string]$Hook
)

$ErrorActionPreference = "Stop"
$root = (git rev-parse --show-toplevel).Trim()
$script = Join-Path $root ".codex\hooks\$Hook"
$candidates = @()
$linkPath = Join-Path $root ".riel-instance.json"

if (Test-Path -LiteralPath $linkPath) {
    try {
        $link = Get-Content -Raw -LiteralPath $linkPath | ConvertFrom-Json
        $instancePath = Join-Path ([string]$link.state_dir) "instance.json"
        $instance = Get-Content -Raw -LiteralPath $instancePath | ConvertFrom-Json
        if ($instance.python_executable) {
            $candidates += ,@([string]$instance.python_executable)
        }
    }
    catch {
        Write-Error "No se pudo leer el intérprete de la instancia técnica de Riel: $($_.Exception.Message)"
        exit 1
    }
}

$candidates += ,@("py", "-3")
$candidates += ,@("python3")
$candidates += ,@("python")

foreach ($candidate in $candidates) {
    $command = $candidate[0]
    $prefix = @($candidate | Select-Object -Skip 1)
    try {
        & $command @prefix --version *> $null
        if ($LASTEXITCODE -eq 0) {
            & $command @prefix $script
            exit $LASTEXITCODE
        }
    }
    catch {
        continue
    }
}

Write-Error "Riel no encontró un Python funcional. Ejecutá init con Python 3.11+ antes de abrir Codex."
exit 1
