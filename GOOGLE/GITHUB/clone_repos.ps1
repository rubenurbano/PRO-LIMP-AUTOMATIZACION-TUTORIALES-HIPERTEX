<#
clone_repos.ps1
Clona una lista de repositorios GitHub secuencialmente.
Uso:
  PowerShell -ExecutionPolicy Bypass -File .\clone_repos.ps1 -ListFile .\repos.txt -DestFolder "C:\Users\rubenurbano\CLONADOS"
Formato de repos.txt:
  https://github.com/usuario/repo.git
  usuario/repo
  https://github.com/otro/repo
Comentarios: líneas que empiecen por # se ignoran
#>

param(
  [Parameter(Mandatory=$true)] [string]$ListFile,
  [Parameter(Mandatory=$true)] [string]$DestFolder
)

# Preparar destino y log
if (-not (Test-Path $DestFolder)) {
  New-Item -ItemType Directory -Path $DestFolder | Out-Null
}
$LogFile = Join-Path $DestFolder "clone_log_$(Get-Date -Format yyyyMMdd_HHmmss).log"

function Write-Log { param($t) $t | Tee-Object -FilePath $LogFile -Append; Write-Host $t }

Write-Log "INICIO de clonación: $(Get-Date)"
Write-Log "Lista: $ListFile"
Write-Log "Destino: $DestFolder"
Write-Log "-----------------------------------------"

# Leer y procesar cada línea
Get-Content $ListFile | ForEach-Object {
  $line = $_.Trim()
  if ([string]::IsNullOrWhiteSpace($line) -or $line.StartsWith("#")) { return }

  try {
    # Normalizar destino local: nombre carpeta = repo (sin .git)
    if ($line -match "github\.com") {
      $url = $line
      $repoName = ([IO.Path]::GetFileNameWithoutExtension($url))
      $cloneCmd = "git clone `"$url`""
    } else {
      # asumimos formato usuario/repo
      $url = "https://github.com/$line.git"
      $repoName = $line.Split("/")[-1]
      $cloneCmd = "gh repo clone $line"
    }

    $targetPath = Join-Path $DestFolder $repoName
    if (Test-Path $targetPath) {
      Write-Log "Ya existe: $repoName — saltando."
      return
    }

    Write-Log "Clonando: $url -> $targetPath"
    Push-Location $DestFolder
    # Intentar con gh (mejor integración). Si falla, usar git clone con HTTPS.
    $ghExit = & gh repo clone $line 2>&1
    if ($LASTEXITCODE -ne 0) {
      Write-Log "gh falló, intentando git clone (mensaje gh):"
      Write-Log $ghExit
      $gitExit = & git clone $url 2>&1
      if ($LASTEXITCODE -ne 0) {
        Write-Log "ERROR clonando con git: $url"
        Write-Log $gitExit
      } else {
        Write-Log "Clonado OK con git: $repoName"
      }
    } else {
      Write-Log "Clonado OK con gh: $repoName"
    }
    Pop-Location
  } catch {
    Write-Log "EXCEPCION al procesar '$line' : $_"
  } finally {
    Write-Log "-----------------------------------------"
  }
}

Write-Log "FIN de clonación: $(Get-Date)"
