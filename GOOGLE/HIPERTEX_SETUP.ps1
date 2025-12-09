# HIPERTEX_SETUP.ps1 — compatible con Windows PowerShell 5.1 (sin ternario)
$ErrorActionPreference = "Stop"
chcp 65001 | Out-Null

$Root = $PSScriptRoot
if (-not $Root) { $Root = (Get-Location).Path }

Write-Host "`n=== HIPERTEX UNIVERSAL PARSER ===`n" -ForegroundColor Cyan
$fileName = Read-Host "Introduce el nombre del archivo (.hptx / .txt / .docx)"

# Resolver ruta del archivo (absoluta vs relativa)
if ([IO.Path]::IsPathRooted($fileName)) {
    $src = $fileName
} else {
    $src = Join-Path $Root $fileName
}

if (-not (Test-Path $src)) {
    Write-Host "`n❌ No se encontró: $src" -ForegroundColor Red
    Write-Host "Archivos en ${Root}:" -ForegroundColor Yellow
    Get-ChildItem $Root -File -Include *.hptx,*.txt,*.docx | Format-Table Name,Length,LastWriteTime
    pause; exit 1
}

$baseName   = [IO.Path]::GetFileNameWithoutExtension($src)
$outJson    = Join-Path $Root ("{0}.json" -f $baseName)
$parserPath = Join-Path $Root "parser_hipertex.py"

Write-Host "[1/2] Ejecutando parser..." -ForegroundColor Yellow
& py $parserPath $src

# El parser genera *_parsed.json (o *_utf8_parsed.json). Localizar y renombrar.
$parsed = Join-Path $Root ("{0}_utf8_parsed.json" -f $baseName)
if (-not (Test-Path $parsed)) {
    $parsed = Join-Path $Root ("{0}_parsed.json" -f $baseName)
}

if (-not (Test-Path $parsed)) {
    Write-Host "`n❌ No se encontró la salida del parser." -ForegroundColor Red
    pause; exit 2
}

if (Test-Path $outJson) { Remove-Item $outJson -Force }
Move-Item $parsed $outJson

Write-Host "`n✅ [2/2] Generado: $([IO.Path]::GetFileName($outJson))" -ForegroundColor Green
Write-Host "Carpeta: ${Root}`n" -ForegroundColor Cyan
pause
