"""Build script for creating the macOS application."""
import os
import subprocess
import shutil
import time
import glob

def clean_build():
    """Clean previous build artifacts thoroughly."""
    # Directories to clean
    dirs_to_clean = [
        'build',
        'dist',
        '__pycache__',
        '.eggs',
    ]
    
    # Clean main directories
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Removing {dir_name}...")
            shutil.rmtree(dir_name)
    
    # Clean all __pycache__ directories recursively
    for root, dirs, files in os.walk('.'):
        for d in dirs:
            if d == '__pycache__' or d.endswith('.egg-info'):
                path = os.path.join(root, d)
                print(f"Removing {path}...")
                shutil.rmtree(path)
    
    # Remove .pyc files
    for pyc_file in glob.glob('**/*.pyc', recursive=True):
        print(f"Removing {pyc_file}...")
        os.remove(pyc_file)
    
    # Remove dist-info directories in specific build location
    build_collect_path = 'build/bdist.macosx-14.0-x86_64/python3.12-standalone/app/collect'
    if os.path.exists(build_collect_path):
        for item in os.listdir(build_collect_path):
            if item.endswith('.dist-info'):
                path = os.path.join(build_collect_path, item)
                print(f"Removing {path}...")
                shutil.rmtree(path)

def build_app():
    """Build the macOS application."""
    try:
        # Clean previous builds
        print("Cleaning previous builds...")
        clean_build()
        
        # First try building in alias mode (development)
        print("\nBuilding in development mode...")
        subprocess.run(['python', 'setup.py', 'py2app', '-A'], check=True)
        
        # Test the development build
        print("Development build successful!")
        
        # Ask user if they want to proceed with production build
        response = input("\nDevelopment build succeeded. Proceed with production build? (y/n): ")
        
        if response.lower() == 'y':
            print("\nBuilding production version...")
            clean_build()
            
            # Try production build with increased verbosity
            env = os.environ.copy()
            
            subprocess.run(
                ['python', 'setup.py', 'py2app'],
                env=env,
                check=True
            )
            
            print("\nProduction build completed successfully!")
            print("The application can be found in the 'dist' directory.")
        else:
            print("\nSkipping production build. Development version is available in 'dist' directory.")
            
    except subprocess.CalledProcessError as e:
        print(f"\nError during build: {e}")
        print("\nBuild failed. You can:")
        print("1. Try running in development mode only:")
        print("   python setup.py py2app -A")
        print("2. Check the error messages above for more details")
        print("3. Make sure all required dependencies are installed:")
        print("   pip install -r requirements.txt")

if __name__ == '__main__':
    build_app() 