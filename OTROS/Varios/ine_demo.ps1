<#
  ine_demo.ps1
  ------------------------------------------------------------------
  OBJETIVO:
    - NO llamar al INE.
    - Usar un JSON local (ine_ctx\demo.json).
    - Enviar ese JSON a Gemini CLI (por ej. gemini-3-pro-preview-11-2025)
      y obtener un analisis en texto.

  USO:
    cd C:\Users\rubenurbano\HIPERTEX
    $env:GEMINI_MODEL = "gemini-3-pro-preview-11-2025"
    .\ine_demo.ps1
#>

# 1) MODELO GEMINI -----------------------------------------------------------
$Model = if ($env:GEMINI_MODEL) { $env:GEMINI_MODEL } else { "gemini-1.5-pro-latest" }

# 2) RUTA DEL JSON DEMO ------------------------------------------------------
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$CtxDir    = Join-Path $ScriptDir "ine_ctx"
$JsonFile  = Join-Path $CtxDir "demo.json"
$OutFile   = Join-Path $CtxDir "analisis_demo_gemini.txt"

if (-not (Test-Path $JsonFile -PathType Leaf)) {
    Write-Error "No existe el archivo demo.json en $CtxDir. Crealo antes de ejecutar."
    exit 1
}

# 3) FUNCION PARA COMPROBAR COMANDO GEMINI ----------------------------------
function Test-Command {
    param([string]$Name)
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

if (-not (Test-Command "gemini")) {
    Write-Error "No se encontro el comando 'gemini'. Instala y configura el Gemini CLI antes de usar este script."
    exit 1
}

# 4) PROMPT PARA GEMINI ------------------------------------------------------
$Prompt = @'
Analiza el JSON proporcionado, que contiene pares Fecha/Valor:
1) Indica cual es la ultima fecha disponible y su valor.
2) Calcula la diferencia entre el primer y el ultimo valor.
3) Resume en lenguaje claro que tendencia muestra esta miniserie.
4) Devuelvelo en 4 bullets muy claros y una conclusion final de 2 lineas.
'@

# 5) LLAMAR A GEMINI CLI -----------------------------------------------------
$inputArgs = @("--input-file", $JsonFile)

Write-Host "Ejecutando Gemini con modelo: $Model"
Write-Host ("Archivo de contexto: " + $JsonFile)

try {
    $resultado = gemini --model $Model @inputArgs -i $Prompt
    $resultado | Tee-Object -FilePath $OutFile | Out-Host
    Write-Host "Resultado guardado en: $OutFile"
}
catch {
    Write-Error "Error al llamar a Gemini CLI: $($_.Exception.Message)"
    Write-Host "Revisa los logs JSON en %TEMP% si el CLI los genera."
}
