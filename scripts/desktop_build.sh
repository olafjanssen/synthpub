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
echo "Building SynthPub macOS application..."

python -m nuitka --macos-create-app-bundle \
    --lto=yes \
    --include-data-dir=./frontend=frontend \
    --noinclude-pytest-mode=nofollow \
    --macos-app-name=SynthPub \
    --product-name=SynthPub \
    --output-filename=SynthPub \
    --macos-app-icon=./frontend/img/dpbtse_logo.icns \
    --output-dir=dist ./src/SynthPub.py


[[ $OSTYPE == 'darwin'* ]] && cp -r ./frontend ./dist/SynthPub.app/Contents/


# Deactivate environment
deactivate

# Package
echo "Creating distribution zip..."
cd dist
zip -r SynthPub.zip SynthPub.app
cd ..

echo "Build complete! Distribution file available at dist/SynthPub.zip"
