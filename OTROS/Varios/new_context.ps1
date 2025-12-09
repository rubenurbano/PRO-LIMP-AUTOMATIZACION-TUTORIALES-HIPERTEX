$fecha = Get-Date -Format yyyy-MM-dd
$dir = ".\docs"
$archivo = Join-Path $dir ($fecha + ".md")

if (!(Test-Path $dir)) {
    New-Item -ItemType Directory -Path $dir | Out-Null
}

if (Test-Path $archivo) {
    Write-Host "Ya existe: $archivo"
    exit
}

# Cargar plantilla
$plantilla = Get-Content -Path .\_plantilla_contexto.md -Raw

# Reemplazar fecha
$plantilla = $plantilla.Replace("{{FECHA}}", $fecha)

# Guardar archivo final
Set-Content -Path $archivo -Value $plantilla -Encoding utf8

Write-Host "Archivo creado: $archivo"
