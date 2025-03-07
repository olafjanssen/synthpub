# SynthPub

## Features

- Project and Topic management with automated content generation
- Feed aggregation and processing
- Article generation using LLMs
- Multi-channel publishing
- Image thumbnails from Pexels API

Explanation of important [implementation](IMPLEMENTATION.md) decisions.

## Environment Configuration

The application uses a `settings.yaml` file in the root directory for configuration. Make sure to set up the following:

```yaml
env_vars:
  OPENAI_API_KEY: your_openai_key
  YOUTUBE_API_KEY: your_youtube_key
  PEXELS_API_KEY: your_pexels_key
  # Other API keys...

llm:
  article_generation:
    provider: openai
    model_name: gpt-4
    max_tokens: 800
  # Other LLM settings...

db_path: ../db
```



## API Usage Examples

Run the API with hosted front-edn:

```bash
cd src
python -m api.run
```

You can interact with the Curator API using curl:

```bash
# Create a new topic
curl -X POST http://localhost:8000/api/topics/ \
    -H "Content-Type: application/json" \
    -d '{"name": "AI Ethics", "description": "The ethical implications of artificial intelligence in modern society"}'

# Get a specific topic
curl http://localhost:8000/api/topics/AI%20Ethics

# List all topics
curl http://localhost:8000/api/topics/
```

## Docker Usage

Build and run the application using Docker:

```bash
# Build the Docker image
docker build -t synthpub .

# Run the container
docker run -p 8000:8000 -v $(pwd)/db:/app/db -v $(pwd)/creds:/app/creds synthpub
```

Or use Docker Compose for a simpler setup:

```bash
# Build and start the application
docker-compose up -d

# Stop the application
docker-compose down
```



## Desktop Usage

Build the desktop app:

```bash
python -m nuitka --macos-create-app-bundle --product-name=SynthPub --macos-app-icon=./frontend/img/dpbtse_logo.icns --output-dir=dist ./src/desktop_app.py
```

## Logging System

SynthPub includes a comprehensive logging system that provides:

1. **System Logs** - Internal debug, info, warning, and error messages for developers
2. **User Logs** - Clear, concise messages displayed to end users in the web interface

### Log Levels

The logging system uses [loguru](https://github.com/Delgan/loguru) with standard and custom log levels:

- Standard levels (system-only): DEBUG, INFO, WARNING, ERROR, CRITICAL
- Custom levels (user-facing): USER_INFO, USER_WARNING, USER_ERROR

### Real-time Log Viewing

The system provides real-time log viewing through:

1. Web interface at `/logs.html` with live updates via WebSockets
2. Log files in the `logs` directory:
   - `system.log` - Complete system logs
   - `user.log` - User-facing logs only

### Using Logs in Code

To log messages in your code:

```python
from src.utils.logging import debug, info, warning, error, critical, user_info, user_warning, user_error

# System-only logs (not shown to users)
debug("This is a debug message")
info("Processing started")
warning("Resource usage high")
error("Connection failed")
critical("System failure")

# User-facing logs (shown in web interface)
user_info("Project created successfully")
user_warning("Feed update incomplete - check connection")
user_error("Unable to generate article")
```

System logs include technical details for debugging, while user logs should be clear, concise, and actionable for end users.