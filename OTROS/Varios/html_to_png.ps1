param(
    [Parameter(Mandatory=$true)]
    [string]$InputHtml,

    [Parameter(Mandatory=$true)]
    [string]$OutputPng
)

# Ruta a Chrome
$chrome = "C:\Program Files\Google\Chrome\Application\chrome.exe"

# Comando para sacar screenshot de TODO el documento automáticamente
# --full-page ES LA CLAVE
$cmd = @(
    "--headless=new",
    "--disable-gpu",
    "--hide-scrollbars",
    "--full-page",                 # <---- ESTA LÍNEA ES EL ORO
    "--screenshot=""$OutputPng""",
    """$InputHtml"""
) -join " "

Write-Host "Ejecutando Chrome headless..."
& $chrome $cmd

if (Test-Path $OutputPng) {
    Write-Host "👍 LISTO: $OutputPng"
} else {
    Write-Host "❌ ERROR: No se generó el PNG"
}
