@echo off
setlocal

:: Cambia al directorio donde está el BAT (en caso de que se ejecute desde otro lado)
cd /d "%~dp0%"

:: Verifica si Python existe
if not exist "python\pythonw.exe" (
    echo Error: No se encontró pythonw.exe en la carpeta 'python'.
    echo Asegúrate de que la ruta es correcta.
    timeout /t 3 >nul
    exit /b 1
)

:: Ejecuta el script con el flag de inicio desde el BAT
start "" "python\pythonw.exe" ".\win.py" --from-bat

exit /b 0
