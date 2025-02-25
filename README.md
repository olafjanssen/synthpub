# synthpub

## API Usage Examples

Run the API:

```bash
cd src
python -m api.run
```

You can interact with the Curator API using curl:

```bash
# Create a new topic
curl -X POST http://localhost:8000/topics/ \
    -H "Content-Type: application/json" \
    -d '{"name": "AI Ethics", "description": "The ethical implications of artificial intelligence in modern society"}'

# Get a specific topic
curl http://localhost:8000/topics/AI%20Ethics

# List all topics
curl http://localhost:8000/topics/
```

## Frontend Usage

```bash 
cd frontend
python -m http.server 8080
```

## Desktop Usage

Build the desktop app:

```bash
python build.py
```

