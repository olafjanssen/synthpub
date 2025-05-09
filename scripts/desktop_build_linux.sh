#!/bin/bash

# Prepare environment
rm -rf venv-nuitka
python -m venv venv-nuitka
source venv-nuitka/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Lint and test
flake8 src tests --count --select=E9,F63,F7,F82 --show-source --statistics
black --check src tests
isort --check-only --profile black src tests
pytest tests

# Build
echo "Building SynthPub Linux application..."

python -m nuitka \
    --lto=yes \
    --include-data-dir=./frontend=frontend \
    --noinclude-pytest-mode=nofollow \
    --linux-onefile-icon=./frontend/img/dpbtse_logo.png \
    --output-dir=dist \
    --output-filename=SynthPub_linux \
    --onefile \
    ./src/SynthPub.py

# Deactivate environment
deactivate

# Package
echo "Creating distribution archive..."
cd dist
tar -czf SynthPub.tar.gz SynthPub
cd ..

echo "Build complete! Distribution file available at dist/SynthPub.tar.gz" 