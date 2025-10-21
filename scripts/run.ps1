param(
    [string]$PyReq = ".\requirements.txt"
)

function Write-Info($msg){ Write-Host "[TasPy] $msg" -ForegroundColor Cyan }
function Write-Err($msg){ Write-Host "[TasPy] $msg" -ForegroundColor Red }

# --- 0) Проверяем, что мы в корне проекта (есть app\ui\main.py)
if (-not (Test-Path ".\app\ui\main.py")) {
    Write-Err "Не вижу .\app\ui\main.py. Запусти скрипт из корня репозитория."
    exit 1
}

# --- 1) Проверяем наличие python 3.12
$py312 = $null
try {
    $v = & py -3.12 -V 2>$null
    if ($LASTEXITCODE -eq 0) { $py312 = "py -3.12" }
} catch {}

if (-not $py312) {
    Write-Info "Python 3.12 не найден. Пытаюсь поставить через winget..."
    try {
        winget install --id Python.Python.3.12 -e --silent
        $v = & py -3.12 -V 2>$null
        if ($LASTEXITCODE -ne 0) { throw "py -3.12 всё ещё не доступен" }
        $py312 = "py -3.12"
    } catch {
        Write-Err "Не удалось автоматически установить Python 3.12. Поставь вручную с https://www.python.org/downloads/windows/ и запусти ещё раз."
        exit 1
    }
}

# --- 2) Создаём/обновляем виртуальное окружение .venv312
$venvPy = ".\.venv312\Scripts\python.exe"
if (-not (Test-Path $venvPy)) {
    Write-Info "Создаю .venv312..."
    & py -3.12 -m venv .venv312
    if ($LASTEXITCODE -ne 0) { Write-Err "Не смог создать .venv312"; exit 1 }
}

# --- 3) Обновляем pip и ставим зависимости
Write-Info "Обновляю pip..."
& $venvPy -m pip install -U pip

if (Test-Path $PyReq -and (Get-Content $PyReq | Where-Object { $_.Trim() -ne "" } | Measure-Object).Count -gt 0) {
    Write-Info "Ставлю зависимости из $PyReq..."
    & $venvPy -m pip install -r $PyReq
} else {
    Write-Info "requirements.txt пуст/отсутствует — ставлю базовый набор..."
    & $venvPy -m pip install PySide6 sqlmodel pydantic pydantic-settings python-dateutil pytest
}

# --- 4) Стартуем приложение
Write-Info "Запускаю TasPy..."
& $venvPy -m app.ui.main
