# synthpub

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

