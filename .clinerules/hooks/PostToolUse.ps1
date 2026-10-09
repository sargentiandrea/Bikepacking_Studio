# Hook Cline PowerShell: avvio del motore comune di continuità.
$ErrorActionPreference = 'Stop'
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = $OutputEncoding
[Console]::InputEncoding = $OutputEncoding
$repoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$hookEvent = [System.IO.Path]::GetFileNameWithoutExtension($PSCommandPath)
$rawEvent = [Console]::In.ReadToEnd()
$rawEvent | & node (Join-Path $repoRoot 'scripts/continuita-hook.cjs') cline $hookEvent
exit $LASTEXITCODE