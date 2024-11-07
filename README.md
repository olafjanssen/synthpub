# synthpub

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

```bash
# Create a topic
curl -X POST http://localhost:5000/api/topics/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Game Mechanics", "description": "Core game mechanics concepts"}'

# Get all topics
curl http://localhost:5000/api/topics/

# Create an article
curl -X POST http://localhost:5000/api/articles/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Introduction to Game Loops", "content": "Game loops are...", "topic_id": 1}'

# Get all articles
curl http://localhost:5000/api/articles/
```

```bash
# Initialize database
python scripts/db_cli.py init

# Check database status
python scripts/db_cli.py status

# Optimize database
python scripts/db_cli.py optimize

# Drop all tables (with confirmation)
python scripts/db_cli.py drop
```

```bash
# Seed database with initial data
python scripts/seed_data.py
```

```bash
# Process new content
curl -X POST http://localhost:5000/api/curator/process \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Article content here...",
    "topic": "Game Mechanics",
    "topic_id": 1,
    "metadata": {
      "source": "blog",
      "author": "John Doe"
    }
  }'

# Update existing article
curl -X PUT http://localhost:5000/api/curator/update/1 \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Updated content here...",
    "topic": "Game Mechanics"
  }'

# Get curator status
curl http://localhost:5000/api/curator/status
```

