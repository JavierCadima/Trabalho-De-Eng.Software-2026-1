@echo off
REM Constrói o executável do aplicativo usando PyInstaller.
REM Execute este script na raiz do projeto.

py -m PyInstaller --noconfirm --onefile --windowed --name AutoMecanicaBaterias main.py
if errorlevel 1 (
    echo ERRO: falha ao gerar o executável com PyInstaller.
    pause
    exit /b 1
)

echo Executável criado em dist\AutoMecanicaBaterias.exe
echo Agora execute o instalador NSIS com: makensis AutoMecanicaBateriasInstaller.nsi
pause
