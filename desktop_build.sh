#!/bin/bash

python -m nuitka --macos-create-app-bundle --product-name=SynthPub --macos-app-icon=./frontend/img/dpbtse_logo.icns --output-dir=dist ./src/desktop_app.py