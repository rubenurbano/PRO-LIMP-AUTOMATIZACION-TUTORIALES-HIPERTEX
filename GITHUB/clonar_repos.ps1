# ================================
#  CLONAR LISTA DE REPOS DE GITHUB
#  Archivo: clonar_repos.ps1
# ================================

# 1. Ruta del archivo que contiene la lista de URLs (una por línea)
$lista = "repos.txt"

# 2. Carpeta donde se van a clonar los repos
$destino = "C:\ReposClonados"

# 3. Crear carpeta destino si no existe
if (!(Test-Path $destino)) {
    New-Item -ItemType Directory -Path $destino | Out-Null
}

# 4. Leer todas las líneas del archivo
$repos = Get-Content $lista

# 5. Recorrer cada URL y clonar
foreach ($url in $repos) {
    Write-Host "Clonando: $url..." -ForegroundColor Cyan
    git clone $url $destino
    Write-Host "--------------------------------------------"
}

Write-Host "PROCESO COMPLETADO" -ForegroundColor Green
