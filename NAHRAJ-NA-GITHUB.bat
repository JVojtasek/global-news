@echo off
chcp 65001 >nul
title The Deeper Story - nahrani na GitHub
echo.
echo ==========================================================
echo   NAHRANI PROJEKTU NA GITHUB
echo ==========================================================
echo.
echo Nez budes pokracovat, musis mit hotove tohle:
echo.
echo   1. Na https://github.com/new zaloz novy repozitar
echo      - Repository name:  global-news   (nebo jak chces)
echo      - Public
echo      - NEZASKRTAVEJ "Add a README file"
echo.
echo   2. Mit nainstalovany Git ( https://git-scm.com/download/win )
echo.
echo ==========================================================
echo.

where git >nul 2>nul
if errorlevel 1 (
  echo [CHYBA] Git neni nainstalovany.
  echo Stahni ho z https://git-scm.com/download/win a spust tenhle soubor znovu.
  echo.
  pause
  exit /b 1
)

set /p USERNAME=Tvoje uzivatelske jmeno na GitHubu: 
set /p REPONAME=Nazev repozitare (napr. global-news): 

if "%USERNAME%"=="" goto :chybi
if "%REPONAME%"=="" goto :chybi

echo.
echo Pripravuji...
cd /d "%~dp0"

if not exist ".git" (
  git init -q
  git branch -M main
)

git add -A
git -c user.email="%USERNAME%@users.noreply.github.com" -c user.name="%USERNAME%" commit -qm "The Deeper Story - prvni nahrani" 2>nul

git remote remove origin 2>nul
git remote add origin https://github.com/%USERNAME%/%REPONAME%.git

echo.
echo Nahravam na GitHub. Otevre se prihlaseni do GitHubu - potvrd ho.
echo.
git push -u origin main

if errorlevel 1 (
  echo.
  echo [CHYBA] Nahrani se nepovedlo.
  echo Nejcastejsi duvody:
  echo   - repozitar na GitHubu jeste neexistuje
  echo   - preklep v uzivatelskem jmenu nebo nazvu
  echo   - repozitar neni prazdny (mel jsi zaskrtnute "Add a README")
  echo.
  pause
  exit /b 1
)

echo.
echo ==========================================================
echo   HOTOVO
echo ==========================================================
echo.
echo Projekt je na adrese:
echo   https://github.com/%USERNAME%/%REPONAME%
echo.
echo DALSI KROKY (v teto poradi):
echo   1. Settings - Pages - Source: nastav na "GitHub Actions"
echo   2. Actions - potvrd zelene tlacitko, aby se workflow povolily
echo   3. Actions - "1 - Sber zprav" - Run workflow
echo.
echo Pak otevri NAVOD.md a pokracuj krokem 4.
echo.
pause
exit /b 0

:chybi
echo.
echo [CHYBA] Musis vyplnit obe udaje.
pause
exit /b 1
