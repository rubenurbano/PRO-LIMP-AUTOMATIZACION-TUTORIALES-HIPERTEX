<#
  gemini_chat.ps1
  ---------------------------------------------------------
  Usa Gemini desde PowerShell con esta lógica:

  1) Intenta usar:  gemini-3-pro-preview-11-2025
  2) Si ese modelo no existe (404 / NOT_FOUND / error),
     cae a: gemini-1.5-pro-latest

  USO:
    .\gemini_chat.ps1 "Tu pregunta aquí"

  Si no pasas texto, te lo pedirá con Read-Host.
#>

param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$PromptParts
)

# 1) Construir el prompt final
if ($PromptParts -and $PromptParts.Count -gt 0) {
    $prompt = $PromptParts -join " "
} else {
    $prompt = Read-Host "Escribe tu prompt para Gemini"
}

if (-not $prompt -or $prompt.Trim() -eq "") {
    Write-Host "No se proporcionó prompt. Saliendo."
    exit 0
}

# 2) Modelos
$preferredModel = "gemini-3-pro-preview-11-2025"
$fallbackModel  = "gemini-1.5-pro-latest"
$modelToUse     = $preferredModel

# 3) Comprobar que el comando 'gemini' existe
function Test-Command {
    param([string]$Name)
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

if (-not (Test-Command "gemini")) {
    Write-Error "No se encontró el comando 'gemini'. Asegúrate de tener instalado el Gemini CLI y que esté en el PATH."
    exit 1
}

# 4) Probar si el modelo 3-pro-preview existe realmente
Write-Host "Probando modelo preferido: $preferredModel ..."

# IMPORTANTE: aquí NO usamos -i, solo el prompt como argumento
$testOutput = & gemini --model $preferredModel --output-format json "ping" 2>&1
$exitCode = $LASTEXITCODE
$testText = ($testOutput -join "`n")

if ($exitCode -ne 0 -or $testText -match "NOT_FOUND|404|model not found|Requested entity was not found") {
    Write-Host "El modelo $preferredModel no está disponible. Usando modelo de respaldo: $fallbackModel"
    $modelToUse = $fallbackModel
} else {
    Write-Host "Modelo $preferredModel disponible. Usándolo."
}

Write-Host ""
Write-Host ">>> Enviando prompt a: $modelToUse"
Write-Host "------------------------------------------------------"

# 5) Llamar a Gemini con el modelo elegido (sin -i)
& gemini --model $modelToUse --output-format text $prompt
