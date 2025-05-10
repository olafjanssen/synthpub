@echo off
setlocal enabledelayedexpansion

:: Prepare environment
echo Preparing environment...
if exist venv-nuitka rmdir /s /q venv-nuitka
python -m venv venv-nuitka
call venv-nuitka\Scripts\activate.bat

:: Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

:: Lint and test
echo Running linting and tests...
flake8 src tests --count --select=E9,F63,F7,F82 --show-source --statistics
black --check src tests
isort --check-only --profile black src tests
pytest tests

:: Build
echo Building SynthPub Windows application...
python -m nuitka ^
    --lto=yes ^
    --include-data-dir=./frontend=frontend ^
    --noinclude-pytest-mode=nofollow ^
    --windows-icon-from-ico=./frontend/img/dpbtse_logo.ico ^
    --output-dir=dist ^
    --output-filename=SynthPub.exe ^
    ./src/SynthPub.py

:: Deactivate environment
call deactivate

:: Package
echo Creating distribution zip...
cd dist
powershell Compress-Archive -Path SynthPub.exe -DestinationPath SynthPub.zip -Force
cd ..

echo Build complete! Distribution file available at dist\SynthPub.zip 