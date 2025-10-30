@echo off
echo ============================================================
echo       REINICIAR STREAMLIT - LIMPAR CACHE COMPLETO
echo ============================================================
echo.

echo [1/4] Parando processos do Streamlit...
taskkill /F /IM streamlit.exe 2>nul
timeout /t 2 >nul

echo [2/4] Limpando cache Python...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul

echo [3/4] Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo [4/4] Iniciando Streamlit...
echo.
echo ============================================================
echo  STREAMLIT INICIANDO...
echo  Abra: http://localhost:8501
echo  Pressione Ctrl+C para parar
echo ============================================================
echo.

streamlit run app.py


