"""
Desktop application wrapper for SynthPub using PyWebView.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import threading
import time

import requests
import uvicorn
import webview
import yaml

from api.app import app
from utils.logging import debug, error


def load_environment():
    """Load environment variables from settings.yaml"""
    if os.path.exists("settings.yaml"):
        with open("settings.yaml", 'r') as f:
            settings = yaml.safe_load(f)
            env_vars = settings.get("env_vars", {})
            for key, value in env_vars.items():
                os.environ[key] = value

# Load environment variables before starting the app
load_environment()

class SynthPubApp:
    def __init__(self):
        self.window = None
        self.server_thread = None
        self.server_started = False

    def start_server(self):
        """Start the FastAPI server."""
        config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="info")
        server = uvicorn.Server(config)
        self.server_thread = threading.Thread(target=server.run)
        self.server_thread.daemon = True
        self.server_thread.start()

    def wait_for_server(self, timeout=10):
        """Wait for the server to start."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get('http://127.0.0.1:8000/api/health', timeout=2)
                if response.status_code == 200:
                    self.server_started = True
                    return True
            except requests.exceptions.ConnectionError:
                time.sleep(0.1)
        return False

    def create_window(self):
        """Create the application window."""
        # Start server if not already running
        if not self.server_thread:
            self.start_server()
        
        # Wait for server to start
        if not self.wait_for_server():
            raise Exception("Server failed to start within timeout")

        # Create window only after server is confirmed running
        self.window = webview.create_window(
            'SynthPub',
            'http://127.0.0.1:8000',
            width=1200,
            height=800,
            min_size=(800, 600),
            zoomable=True
        )

    def run(self):
        """Run the application."""
        try:
            # Set resource paths
            frontend_path = os.path.join(os.path.dirname(__file__), 'frontend')
            db_path = os.path.join(os.path.dirname(__file__), 'db')
            
            # Set environment variables
            os.environ['FRONTEND_PATH'] = frontend_path
            os.environ['DB_PATH'] = db_path

            debug("APP", "Environment setup", f"DB_PATH: {db_path}")
            
            # Create and show the window
            self.create_window()
            
            # Start the application
            webview.start(debug=True)
            
        except Exception as e:
            error("APP", "Startup failed", f"Error starting application: {e}")
            sys.exit(1)

def main():
    """Entry point for the application."""
    app = SynthPubApp()
    app.run()

if __name__ == '__main__':
    main() 