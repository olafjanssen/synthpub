# SynthPub - An AI Curated Digital Garden

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/09786f5f3e3d4890a9afc8ebcd9a04cc)](https://app.codacy.com/gh/olafjanssen/synthpub?utm_source=github.com&utm_medium=referral&utm_content=olafjanssen/synthpub&utm_campaign=Badge_Grade)

## Overview

SynthPub reimagines automated content publishing by treating information as a carefully tended digital garden rather than an endless stream of new content. In an age of information overload, this platform takes a thoughtful approach to content synthesis and curation, focusing on quality over quantity.

Unlike traditional automated publishing systems that continuously generate new content, SynthPub intelligently aggregates, refines, and evolves existing content. It acts as a dynamic knowledge base that:

- Synthesizes information from diverse sources (RSS feeds, blogs, news sites)
- Refines existing content with new relevant information instead of creating redundant posts
- Prunes outdated or less relevant information to maintain a focused knowledge base
- Ensures content quality through AI-powered curation and synthesis

The platform represents a strategic experiment in using artificial intelligence to address information overload while maintaining editorial quality and fostering meaningful knowledge sharing.

## Features

- Project and Topic management with automated content generation
- Feed aggregation and processing from multiple sources
- Intelligent article generation and refinement using LLMs
- Multi-channel publishing capabilities
- Automatic image thumbnails via Pexels API
- Text-to-speech conversion using OpenAI TTS or local Piper TTS
- Content pruning and quality assessment

See the [implementation documentation](docs/IMPLEMENTATION.md) for important architectural decisions.

## Getting Started

### Prerequisites

- Python 3.8+
- pip package manager
- API keys for external services (OpenAI, YouTube, Pexels)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/olafjanssen/synthpub.git
   cd synthpub
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your environment (see Environment Configuration section)

4. Run the application:
   ```bash
   cd src
   python -m api.run
   ```

## Environment Configuration

The application uses a `settings.yaml` file in the root directory for configuration. Create this file with the following structure:

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
## Prompt Templates

SynthPub uses customizable prompt templates stored as Markdown files in the `resources/prompts` directory. These templates are used for various LLM operations:

- `article-generation.md`: Template for generating new articles
- `article-refinement.md`: Template for refining existing articles with new context
- `article-relevance-filter.md`: Template for determining if new content is relevant to an existing article

You can modify these templates to customize the behavior of the LLM operations. The templates are loaded automatically when the application starts.

## Usage

### API Examples

The SynthPub API allows you to manage topics, articles, and content generation programmatically:

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



### Deployment using Docker Compose

```bash
# Build and start the application
docker-compose up -d

# Stop the application
docker-compose down
```

## Desktop Application

Build the desktop app:

```bash
./scripts/desktop_build.sh
```

## Project Structure

```
synthpub/
├── src/              # Source code for the application
├── tests/            # Test files
├── docs/             # Documentation
├── frontend/         # Frontend resources
├── resources/        # General resources
└── scripts/          # Utility scripts
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenAI for providing the LLM capabilities
- Pexels for the image API
- Piper TTS for local text-to-speech conversion

## Disclaimers

### AI Development and Documentation

![AI-Human Collaboration](resources/images/cyborg-black.svg)

This project is developed using Cursor AI for code generation, documentation, and development assistance. While human developers review and validate the code, a significant portion of the implementation, documentation, and architectural decisions are generated or assisted by AI tools. 

The project represents a true AI-human collaboration where AI tools are not just assistants but active participants in the development process. While human developers maintain final control and make critical decisions, the majority of the codebase and documentation is AI-generated and then refined through human review and modification.

