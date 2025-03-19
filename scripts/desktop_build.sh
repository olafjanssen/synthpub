#!/bin/bash

Prepare environment
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
echo "Building SynthPub macOS application..."

python -m nuitka --onefile --macos-create-app-bundle --product-name=SynthPub --macos-app-icon=./frontend/img/dpbtse_logo.icns --output-dir=dist ./src/desktop_app.py

# Deactivate environment
deactivate

# Package
echo "Creating distribution zip..."
cd dist
zip -r SynthPub.zip SynthPub.app
cd ..

echo "Build complete! Distribution file available at dist/SynthPub.zip"
