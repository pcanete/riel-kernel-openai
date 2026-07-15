param(
    [Parameter(Mandatory=$false)]
    [string]$Target = "."
)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
py -3 "$ScriptDir\installer.py" --target $Target
exit $LASTEXITCODE
