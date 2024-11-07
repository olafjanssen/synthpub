import os
from api import create_app
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Flask application instance
app = create_app()

if __name__ == '__main__':
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    # Get debug mode from environment variable or default to True for development
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"Starting server on port {port}")
    print(f"Debug mode: {'on' if debug else 'off'}")
    print("\nAvailable routes:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule.rule} [{', '.join(rule.methods)}]")
    
    # Run the application
    app.run(host='0.0.0.0', port=port, debug=debug) 