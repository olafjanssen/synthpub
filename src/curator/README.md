# Curator Module

The Curator module is responsible for processing and refining content for topics. It handles the fetching, filtering, generation, and refinement of articles based on topic definitions.

## Overview

The core of the curator is a LangGraph-based workflow that processes content through a series of steps:

1. **Input Creation**: Loads the topic and any existing article
2. **Article Generation**: Creates a new article if one doesn't exist
3. **News Relevance**: Determines if new content is relevant to the topic
4. **Article Refinement**: Updates the article with relevant new content

## Architecture

### LangGraph Workflow

The curator uses a LangGraph workflow to process content. This provides several advantages:

- Explicit state management through the entire process
- Conditional branching based on clear decision points
- Better error handling and recovery
- Visualization for debugging the workflow

The workflow is defined in `graph_workflow.py` and follows this flow:

```
create_input -> should_generate? 
                YES -> generate_article -> news_relevance 
                NO  -> news_relevance
                      is_relevant? 
                      YES -> refine_article -> end
                      NO  -> end
```

### State Management

The workflow maintains state throughout the process. The state includes:

- Input parameters (topic_id, feed_content, feed_item)
- Loaded entities (topic, existing_article)
- Generated entities (refined_article, generated_article)
- Extracted substance (new_information, enforcing_information, contradicting_information)
- Status flags (has_error, error_message, error_step)

The state is designed to be minimal, with information stored in the appropriate models where possible. For example:

- Relevance information is stored directly in the `feed_item` object rather than duplicated in the state
- Substance extraction results are stored in both the state and the `feed_item` object for persistence
- The resulting article ID is stored in the `feed_item` object to track which articles were created or updated based on each feed item

### Steps

Each step in the workflow is implemented as a function in the `steps` directory:

- `input_creator.py`: Functions for loading the topic and existing article
- `article_generator.py`: Functions for creating a new article if needed and determining if article generation is needed
- `news_relevance.py`: Functions for determining if content is relevant and making relevance decisions
- `article_refiner.py`: Functions for updating the article with new content

Each step module follows a consistent pattern:

- Process functions that take and return state
- Conditional routing functions that determine workflow paths
- Helper functions that implement the core logic

### Conditional Routing

The workflow uses function factories from the step modules to create conditional routing functions:

- `should_generate`: From `article_generator.py`, creates a router function that decides if a new article needs to be generated
- `is_relevant`: From `news_relevance.py`, creates a router function that determines if the content is relevant enough for refinement

Each function factory takes node parameters and returns a function that evaluates the state:

```python
# Example usage in graph_workflow.py
graph.add_conditional_edges(
    "create_input",
    should_generate("generate_article", "news_relevance", "end")
)
```

This approach eliminates lambda functions and makes the workflow entirely self-documenting, as the flow is explicit in the graph definition.

## Using the Curator

### Processing Feed Items

To process a feed item through the curator:

```python
from curator.graph_workflow import process_feed_item

# Process a feed item
result = process_feed_item(
    topic_id="my-topic-id",
    feed_content="New content to process",
    feed_item=feed_item
)

# Check the result
if result.get("has_error"):
    print(f"Error: {result['error_message']}")
elif result.get("refined_article"):
    print("Article refined successfully")
elif result.get("generated_article"):
    print("Article generated successfully")
elif result.get("feed_item") and not result.get("feed_item").is_relevant:
    print("Content not relevant")
```

### Queueing Topic Updates

The topic updater provides a queue-based interface for processing feed items:

```python
from curator.topic_updater import queue_topic_update

# Queue all feeds for a topic
queue_topic_update("my-topic-id")
```

## Visualizing the Workflow

To visualize the LangGraph workflow, you can use the CLI:

```bash
python -m curator.cli visualize --output workflow.png
```

Or programmatically:

```python
from curator.graph_workflow import visualize_curator_workflow

# Create visualization
visualize_curator_workflow("curator_workflow.png")
```

## Extending the Workflow

To add a new step to the workflow:

1. Create a new step module in the `steps` directory with process functions and conditional routing factories
2. Import the functions in `graph_workflow.py`
3. Add the step to the workflow graph
4. Update the conditional routing as needed

## Implementation Details

The workflow is implemented as a directed graph with:
- Processing nodes that transform the state (e.g., `process_input`, `generate_article`)
- Conditional routing functions created by factory functions with explicit node targets
- Clear, unidirectional transitions between nodes

This separation of concerns makes the workflow easier to understand, debug, and extend.

## Error Handling

Errors are handled at two levels:

1. **Step Level**: Each step handles errors specific to its operation
2. **Graph Level**: Conditional routing functions direct errors to the end of the workflow

This approach ensures that errors are handled gracefully and that the workflow terminates in a clean state. 