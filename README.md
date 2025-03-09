# SynthPub

## Features

- Project and Topic management with automated content generation
- Feed aggregation and processing
- Article generation using LLMs
- Multi-channel publishing
- Image thumbnails from Pexels API
- Text-to-speech conversion using OpenAI TTS or local Piper TTS

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

## Text-to-Speech Conversion

SynthPub supports two text-to-speech conversion methods:

### OpenAI TTS

Uses OpenAI's cloud-based TTS service. Requires an OpenAI API key.

```bash
# Convert a topic's text to speech using OpenAI TTS
curl -X POST http://localhost:8000/api/topics/AI%20Ethics/convert \
    -H "Content-Type: application/json" \
    -d '{"type": "openai-tts"}'
```

### Piper TTS (Local)

Uses the Piper TTS library for local, offline text-to-speech conversion. Voice models are automatically downloaded from Hugging Face when needed.

1. Install the Piper Python library:
   ```bash
   pip install piper-tts requests
   ```

2. Convert a topic's text to speech:
   ```bash
   # Convert a topic's text to speech using Piper TTS
   curl -X POST http://localhost:8000/api/topics/AI%20Ethics/convert \
       -H "Content-Type: application/json" \
       -d '{"type": "piper-tts"}'
   ```

3. Specify a voice (optional):
   ```bash
   # Convert a topic's text to speech using a specific voice
   curl -X POST http://localhost:8000/api/topics/AI%20Ethics/convert \
       -H "Content-Type: application/json" \
       -d '{"type": "piper-tts", "metadata": {"voice": "en_US-lessac-medium"}}'
   ```

The first time you use a voice, it will be automatically downloaded from Hugging Face and cached locally. Subsequent uses of the same voice will use the cached version.

See the `examples/piper_tts_example.py` script for a demonstration of how to use the PiperTTS module programmatically, including how to list available voices.

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

```