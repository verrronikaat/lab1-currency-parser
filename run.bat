@echo off
chcp 65001 > nul
echo ========================================
echo    ПАРСЕР КУРСОВ ВАЛЮТ ЦБ РФ
echo    Вариант 11 - Японская йена
echo ========================================
echo.

if not exist "venv\" (
    echo [1/4] Создание виртуального окружения...
    python -m venv venv
)

echo [2/4] Активация окружения...
call venv\Scripts\activate

echo [3/4] Установка зависимостей...
pip install -r requirements.txt

echo [4/4] Запуск парсера...
python src/cbr_parser.py

echo.
echo ========================================
echo    РАБОТА ЗАВЕРШЕНА
echo ========================================
pause