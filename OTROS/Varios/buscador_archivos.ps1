# buscador_archivos.ps1

function Obtener-Extensiones {
    param(
        [string]$rutaBase,
        [switch]$Recursivo,
        [string]$FiltroFecha,
        [datetime]$FechaExacta = [datetime]::MinValue
    )

    if ($Recursivo) {
        $items = Get-ChildItem -Path $rutaBase -Recurse -File -ErrorAction SilentlyContinue
    } else {
        $items = Get-ChildItem -Path $rutaBase -File -ErrorAction SilentlyContinue
    }

    if (-not $items) { return @() }

    $hoy = Get-Date
    $from = $null
    $to   = $null

    switch ($FiltroFecha) {
        "HOY" {
            $from = $hoy.Date
            $to   = $from.AddDays(1)
        }
        "AYER" {
            $from = $hoy.Date.AddDays(-1)
            $to   = $hoy.Date
        }
        "SEMANA" {
            $dow = [int]$hoy.DayOfWeek
            $offset = $dow - 1
            if ($offset -lt 0) { $offset = 6 }
            $from = $hoy.Date.AddDays(-$offset)
            $to   = $from.AddDays(7)
        }
        "MES" {
            $from = Get-Date -Year $hoy.Year -Month $hoy.Month -Day 1
            $to   = $from.AddMonths(1)
        }
        "FECHA" {
            if ($FechaExacta -ne [datetime]::MinValue) {
                $from = $FechaExacta.Date
                $to   = $from.AddDays(1)
            }
        }
    }

    if ($from -ne $null -and $to -ne $null) {
        $items = $items | Where-Object { $_.LastWriteTime -ge $from -and $_.LastWriteTime -lt $to }
    }

    $exts = $items | Where-Object { $_.Extension -ne $null -and $_.Extension -ne "" } |
            Select-Object -ExpandProperty Extension -Unique |
            Sort-Object

    return $exts
}

function Pedir-Extension {
    param(
        [string]$rutaBase,
        [switch]$Recursivo,
        [string]$FiltroFecha,
        [datetime]$FechaExacta = [datetime]::MinValue
    )

    $exts = Obtener-Extensiones -rutaBase $rutaBase -Recursivo:$Recursivo -FiltroFecha $FiltroFecha -FechaExacta $FechaExacta

    if (-not $exts -or $exts.Count -eq 0) {
        Write-Host ""
        Write-Host "NO SE DETECTAN ARCHIVOS CON ESE FILTRO." -ForegroundColor Yellow
        return $null
    }

    Write-Host ""
    Write-Host "Extensiones detectadas en: $rutaBase" -ForegroundColor Cyan
    for ($i = 0; $i -lt $exts.Count; $i++) {
        Write-Host "$($i+1)) $($exts[$i])"
    }
    Write-Host "0) Escribir otra extension manualmente"

    $eleccion = Read-Host "Elige una opcion"

    if ($eleccion -eq "0") {
        $extManual = Read-Host "Escribe la extension (ej: hptx, txt, json): "
        if ($extManual.StartsWith(".")) { return $extManual } else { return ".$extManual" }
    }

    if ($eleccion -match '^\d+$') {
        $idx = [int]$eleccion
        if ($idx -ge 1 -and $idx -le $exts.Count) {
            return $exts[$idx - 1]
        }
    }

    Write-Host "Entrada no valida." -ForegroundColor Red
    return $null
}

function Pedir-Ruta {
    param(
        [string]$mensaje = "Ruta de carpeta (Enter = carpeta actual): "
    )
    $ruta = Read-Host $mensaje
    if ([string]::IsNullOrWhiteSpace($ruta)) {
        return (Get-Location).Path
    } else {
        return $ruta
    }
}

function Pedir-Recursivo {
    $r = Read-Host "Buscar tambien en subcarpetas? (S/N, Enter = N)"
    return ($r -match '^[sS]')
}

function Pedir-Fecha-Exacta {
    while ($true) {
        $texto = Read-Host "Fecha exacta (dd/mm/aaaa): "
        if ([string]::IsNullOrWhiteSpace($texto)) {
            Write-Host "Debes introducir una fecha." -ForegroundColor Yellow
            continue
        }
        try {
            return [datetime]::ParseExact($texto, 'dd/MM/yyyy', $null)
        } catch {
            Write-Host "Formato invalido. Usa dd/mm/aaaa (ej: 09/11/2025)." -ForegroundColor Red
        }
    }
}

function Buscar-Extension {
    param(
        [string]$extension,
        [string]$ruta,
        [switch]$Recursivo,
        [string]$FiltroFecha,
        [datetime]$FechaExacta = [datetime]::MinValue
    )

    if (-not $extension) { return }

    Write-Host ""
    Write-Host "Buscando *$extension en: $ruta" -ForegroundColor Cyan

    $filtro = "*$extension"
    if ($Recursivo) {
        $items = Get-ChildItem -Path $ruta -Recurse -File -Filter $filtro -ErrorAction SilentlyContinue
    } else {
        $items = Get-ChildItem -Path $ruta -File -Filter $filtro -ErrorAction SilentlyContinue
    }

    if (-not $items) {
        Write-Host "No se encontraron archivos con esa extension." -ForegroundColor Yellow
        return
    }

    $hoy = Get-Date
    $from = $null
    $to   = $null

    switch ($FiltroFecha) {
        "HOY" {
            $from = $hoy.Date
            $to   = $from.AddDays(1)
        }
        "AYER" {
            $from = $hoy.Date.AddDays(-1)
            $to   = $hoy.Date
        }
        "SEMANA" {
            $dow = [int]$hoy.DayOfWeek
            $offset = $dow - 1
            if ($offset -lt 0) { $offset = 6 }
            $from = $hoy.Date.AddDays(-$offset)
            $to   = $from.AddDays(7)
        }
        "MES" {
            $from = Get-Date -Year $hoy.Year -Month $hoy.Month -Day 1
            $to   = $from.AddMonths(1)
        }
        "FECHA" {
            if ($FechaExacta -ne [datetime]::MinValue) {
                $from = $FechaExacta.Date
                $to   = $from.AddDays(1)
            }
        }
    }

    if ($from -and $to) {
        $items = $items | Where-Object { $_.LastWriteTime -ge $from -and $_.LastWriteTime -lt $to }
    }

    if (-not $items) {
        Write-Host "NO SE DETECTAN ARCHIVOS CON ESE FILTRO." -ForegroundColor Yellow
        return
    }

    $items | Select-Object FullName, Length, LastWriteTime | Format-Table -AutoSize
    Write-Host ""
    Write-Host "Total archivos: $($items.Count)" -ForegroundColor Green
}

function Mostrar-Menu {
    Clear-Host
    Write-Host "===================================="
    Write-Host "       BUSCADOR DE ARCHIVOS"
    Write-Host "===================================="
    Write-Host "Carpeta actual: $(Get-Location)"
    Write-Host ""
    Write-Host "1) Listar por extension (sin filtro de fecha)"
    Write-Host "2) Modificados HOY"
    Write-Host "3) Modificados AYER"
    Write-Host "4) Modificados ESTA SEMANA"
    Write-Host "5) Modificados ESTE MES"
    Write-Host "6) Modificados en FECHA exacta (dd/mm/aaaa)"
    Write-Host "7) Cambiar carpeta actual"
    Write-Host "0) Salir"
    Write-Host ""
}

do {
    Mostrar-Menu
    $opcion = Read-Host "Elige una opcion"

    switch ($opcion) {
        "1" {
            $ruta = Pedir-Ruta
            $rec = Pedir-Recursivo
            $ext = Pedir-Extension -rutaBase $ruta -Recursivo:$rec -FiltroFecha ""
            Buscar-Extension -extension $ext -ruta $ruta -Recursivo:$rec -FiltroFecha ""
            Pause
        }
        "2" {
            $ruta = Pedir-Ruta
            $rec = Pedir-Recursivo
            $ext = Pedir-Extension -rutaBase $ruta -Recursivo:$rec -FiltroFecha "HOY"
            Buscar-Extension -extension $ext -ruta $ruta -Recursivo:$rec -FiltroFecha "HOY"
            Pause
        }
        "3" {
            $ruta = Pedir-Ruta
            $rec = Pedir-Recursivo
            $ext = Pedir-Extension -rutaBase $ruta -Recursivo:$rec -FiltroFecha "AYER"
            Buscar-Extension -extension $ext -ruta $ruta -Recursivo:$rec -FiltroFecha "AYER"
            Pause
        }
        "4" {
            $ruta = Pedir-Ruta
            $rec = Pedir-Recursivo
            $ext = Pedir-Extension -rutaBase $ruta -Recursivo:$rec -FiltroFecha "SEMANA"
            Buscar-Extension -extension $ext -ruta $ruta -Recursivo:$rec -FiltroFecha "SEMANA"
            Pause
        }
        "5" {
            $ruta = Pedir-Ruta
            $rec = Pedir-Recursivo
            $ext = Pedir-Extension -rutaBase $ruta -Recursivo:$rec -FiltroFecha "MES"
            Buscar-Extension -extension $ext -ruta $ruta -Recursivo:$rec -FiltroFecha "MES"
            Pause
        }
        "6" {
            $ruta = Pedir-Ruta
            $rec = Pedir-Recursivo
            $fecha = Pedir-Fecha-Exacta
            $ext = Pedir-Extension -rutaBase $ruta -Recursivo:$rec -FiltroFecha "FECHA" -FechaExacta $fecha
            Buscar-Extension -extension $ext -ruta $ruta -Recursivo:$rec -FiltroFecha "FECHA" -FechaExacta $fecha
            Pause
        }
        "7" {
            $ruta = Pedir-Ruta "Nueva carpeta (ruta absoluta o relativa): "
            if (Test-Path $ruta) {
                Set-Location $ruta
            } else {
                Write-Host "Ruta no valida." -ForegroundColor Red
                Pause
            }
        }
        "0" {
            Write-Host "Saliendo..." -ForegroundColor Cyan
        }
        Default {
            Write-Host "Opcion no valida." -ForegroundColor Red
            Pause
        }
    }
} while ($opcion -ne "0")
