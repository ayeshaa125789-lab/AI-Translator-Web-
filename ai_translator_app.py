@echo off
echo ========================================
echo    AI Translator Pro - Installation
echo ========================================
echo.

echo Step 1: Installing Python packages...
pip install -r requirements.txt

echo.
echo Step 2: Updating translation packages...
argospm update

echo.
echo Step 3: Installing language models...
echo Installing English to Spanish...
argospm install translate-en-es

echo Installing English to French...
argospm install translate-en-fr

echo Installing English to German...
argospm install translate-en-de

echo Installing English to Chinese...
argospm install translate-en-zh

echo Installing English to Arabic...
argospm install translate-en-ar

echo Installing English to Japanese...
argospm install translate-en-ja

echo.
echo ========================================
echo    Installation Complete!
echo ========================================
echo.
echo To run the application, use:
echo streamlit run app.py
echo.
pause
