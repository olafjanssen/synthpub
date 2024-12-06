"""
Setup configuration for building the macOS app with py2app.
"""
from setuptools import setup
import os
import sys
from pathlib import Path

def collect_data_files():
    """Collect all static files needed for the application."""
    data_files = []
    
    # Add frontend files
    for root, dirs, files in os.walk('frontend'):
        files_paths = [os.path.join(root, file) for file in files]
        data_files.append((root, files_paths))
    
    # Add database files
    for root, dirs, files in os.walk('db'):
        files_paths = [os.path.join(root, file) for file in files]
        data_files.append((root, files_paths))
    
    # Add environment file if it exists
    if os.path.exists('.env'):
        data_files.append(('.', ['.env']))
    
    return data_files

def collect_packages():
    """Collect all local packages."""
    packages = []
    for item in os.listdir('.'):
        if os.path.isdir(item) and os.path.exists(os.path.join(item, '__init__.py')):
            packages.append(item)
    return packages

APP = ['src/desktop_app.py']
DATA_FILES = collect_data_files()
local_packages = collect_packages()

OPTIONS = {
    'argv_emulation': False,
    'packages': [
        # Local packages
        *local_packages,
        
        # Core dependencies
        'fastapi',
        'uvicorn',
        'starlette',
        'pydantic',
        'webview',
        'requests',
        
        # Modern importlib replacements for pkg_resources
        'importlib_resources',
        'importlib_metadata',
        
        # LangChain related
        'langchain',
        'langchain_core',
        'langchain_text_splitters',
        
        # Google API
        'googleapiclient',
        'httplib2',
        
        # Utilities
        'dotenv',
        'certifi',
        'tqdm',
        'chardet'
    ],
    'includes': [
        'webview.platforms.cocoa',
    ],
    'excludes': [
        # Qt related
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
        'PyInstaller',
        
        # Other GUI frameworks
        'tkinter',
        'wx',
        'gi',
        'gtk',
        
        # Heavy dependencies
        'numpy',
        'scipy',
        'pandas',
        'matplotlib',
        'PIL',
        
        # Development tools
        'IPython',
        'pytest',
        'nose',
        
        # Deprecated
        'pkg_resources',
    ],
    'resources': ['frontend', 'db', 'src/api'],
    'iconfile': './frontend/img/dpbtse_logo.icns',
    'plist': {
        'CFBundleName': 'SynthPub',
        'CFBundleDisplayName': 'SynthPub',
        'CFBundleIdentifier': 'com.synthpub.app',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'LSMinimumSystemVersion': '10.12',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
    }
}

setup(
    name='SynthPub',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    packages=local_packages,
    install_requires=[
        'fastapi==0.110.0',
        'uvicorn==0.27.1',
        'pydantic==2.9.2',
        'pywebview',
        'requests',
        'importlib_resources',
        'importlib_metadata',
        'langchain',
        'langchain_core',
        'langchain_text_splitters',
        'google-api-python-client',
        'python-dotenv',
        'certifi',
        'tqdm',
        'chardet',
    ],
) 