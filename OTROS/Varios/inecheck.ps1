<#
  inecheck.ps1
  ------------------------------------------------------------------
  OBJETIVO:
    - Descargar datos del INE (JSON) via API Tempus.
    - (Opcional) Descargar y convertir una pagina del INE a TXT/PDF.
    - Enviar todo a Gemini CLI y obtener un analisis en texto.

  USO:
    1) Guardar este archivo como: inecheck.ps1
    2) En PowerShell:
          cd C:\Users\rubenurbano\HIPERTEX
          $env:GEMINI_MODEL = "gemini-3-pro-preview-11-2025"   # o dejar por defecto
          .\inecheck.ps1

    3) Cambiar serie o meses:
          .\inecheck.ps1 -SerieId "OTRA_SERIE" -NMeses 24
#>

param(
    [string]$SerieId = "IPC206458",          # Serie del INE (IPC general)
    [int]$NMeses = 12,                       # Numero de ultimos valores
    [string]$PageUrl = "https://www.ine.es/ipc/"  # Pagina del INE como contexto
)

# 1) MODELO GEMINI -----------------------------------------------------------
# Si existe variable de entorno GEMINI_MODEL, la usamos; si no, modelo por defecto.
$Model = if ($env:GEMINI_MODEL) { $env:GEMINI_MODEL } else { "gemini-1.5-pro-latest" }

# 2) CARPETA DE CONTEXTO Y ARCHIVOS -----------------------------------------
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$CtxDir    = Join-Path $ScriptDir "ine_ctx"

if (-not (Test-Path $CtxDir)) {
    New-Item -ItemType Directory -Path $CtxDir | Out-Null
}

$JsonFile = Join-Path $CtxDir ("ine_{0}_{1}m.json" -f $SerieId, $NMeses)
$PdfFile  = Join-Path $CtxDir "ine_page.pdf"
$TxtFile  = Join-Path $CtxDir "ine_page.txt"
$OutFile  = Join-Path $CtxDir "analisis_gemini.txt"

# 3) FUNCION PARA COMPROBAR COMANDOS ----------------------------------------
function Test-Command {
    param([string]$Name)
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

if (-not (Test-Command "gemini")) {
    Write-Error "No se encontro el comando 'gemini'. Instala y configura el Gemini CLI antes de usar este script."
    exit 1
}

if (-not (Test-Command "Invoke-WebRequest")) {
    Write-Error "No se encontro 'Invoke-WebRequest' en esta sesion de PowerShell."
    exit 1
}

# 4) DESCARGAR JSON DEL INE --------------------------------------------------
$ApiUrl = "https://servicios.ine.es/wstempus/json/es/DATOS_SERIE/$SerieId?nult=$NMeses"
Write-Host "Descargando JSON del INE ($SerieId, ultimos $NMeses meses)..."

try {
    Invoke-WebRequest -Uri $ApiUrl -OutFile $JsonFile -UseBasicParsing
    Write-Host "Guardado: $JsonFile"
}
catch {
    Write-Error "Error descargando el JSON del INE: $($_.Exception.Message)"
    exit 1
}

# Vista previa con jq (si existe)
if (Test-Command "jq") {
    Write-Host "Ultimo registro (vista previa con jq):"
    jq ".[-1]" $JsonFile
}

# 5) OPCIONAL: PDF Y TXT DE LA PAGINA DEL INE --------------------------------
# Buscamos algun navegador basado en Chromium con soporte headless
$Chrome = $null
if (Test-Command "chrome")            { $Chrome = "chrome" }
elseif (Test-Command "google-chrome") { $Chrome = "google-chrome" }
elseif (Test-Command "chromium")      { $Chrome = "chromium" }

if ($Chrome) {
    Write-Host "Convirtiendo URL a PDF con $Chrome (headless)..."
    try {
        & $Chrome --headless --disable-gpu --print-to-pdf="$PdfFile" "$PageUrl" | Out-Null
        if (Test-Path $PdfFile -PathType Leaf) {
            Write-Host "PDF generado: $PdfFile"
        } else {
            Write-Warning "No se genero el PDF."
        }
    }
    catch {
        Write-Warning "Error generando PDF: $($_.Exception.Message)"
    }
} else {
    Write-Host "No se encontro Chrome/Chromium; se omite la generacion de PDF."
}

# Texto plano con pandoc (si existe)
if (Test-Command "pandoc") {
    Write-Host "Extrayendo texto legible de la URL con pandoc..."
    try {
        pandoc $PageUrl -t plain -o $TxtFile
        if (Test-Path $TxtFile -PathType Leaf) {
            Write-Host "Texto generado: $TxtFile"
        } else {
            Write-Warning "No se genero el TXT."
        }
    }
    catch {
        Write-Warning "Error generando TXT: $($_.Exception.Message)"
    }
} else {
    Write-Host "No se encontro 'pandoc'; se omite la generacion de TXT."
}

# 6) PROMPT PARA GEMINI ------------------------------------------------------
$Prompt = @'
Analiza la informacion proporcionada (JSON del INE y, si esta, la pagina PDF/TXT):
1) Dame el ULTIMO valor del IPC, su FECHA (ano-mes) y la variacion interanual (YoY).
2) Calcula la variacion acumulada de los ultimos 12 meses con base en la serie JSON.
3) Si hay discrepancias entre JSON y la pagina (PDF/TXT), indicalas y explica el motivo probable (fechas de corte, provisional vs. definitivo, etc.).
4) Devuelvelo en 5 bullets muy claros y una conclusion final de 2 lineas.
'@

# 7) ARCHIVOS DE CONTEXTO PARA GEMINI ----------------------------------------
$inputArgs = @("--input-file", $JsonFile)

if (Test-Path $PdfFile -PathType Leaf) {
    $inputArgs += @("--input-file", $PdfFile)
}
if (Test-Path $TxtFile -PathType Leaf) {
    $inputArgs += @("--input-file", $TxtFile)
}

# 8) LLAMAR A GEMINI CLI -----------------------------------------------------
Write-Host "Ejecutando Gemini con modelo: $Model"
Write-Host ("Archivos de contexto: " + ($inputArgs -join " "))

try {
    $resultado = gemini --model $Model @inputArgs -i $Prompt
    $resultado | Tee-Object -FilePath $OutFile | Out-Host
    Write-Host "Resultado guardado en: $OutFile"
}
catch {
    Write-Error "Error al llamar a Gemini CLI: $($_.Exception.Message)"
    Write-Host "Revisa los logs JSON en %TEMP% si el CLI los genera."
}
