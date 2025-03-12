# Curator Chain Examples

This directory contains example scripts that demonstrate how to use the curator chain components.

## Test Curator Chain

The `test_curator_chain.py` script demonstrates how to:

1. Create a test Topic
2. Generate an initial article for the topic
3. Process a new feed item to update the article if the content is relevant

### Running the Example

To run the example:

```bash
# From the project root directory
python src/examples/test_curator_chain.py
```

### What the Example Does

The example performs these steps:

1. Creates a test Topic about "Climate Change"
2. Runs the curator chain to generate an initial article for the topic
3. Creates a test feed item with sample content about climate research
4. Runs the curator chain again to process the feed item
5. If the content is relevant, updates the article and adds the feed item to the topic's processed feeds

### Expected Output

The example will log its progress using the application's logging system. You should see output indicating:

- Topic creation
- Article generation
- Content relevance assessment
- Article refinement (if the content is relevant)

If everything works correctly, you'll see a message indicating the chain completed successfully.

## Troubleshooting

If you encounter errors:

1. Make sure all dependencies are installed
2. Check that the database connections are properly configured
3. Verify that the LLM service is available and properly configured
4. Look for specific error messages in the logs

## Extending the Example

You can modify the example to test different scenarios:

- Change the topic to test different domains
- Modify the feed content to test different relevance scenarios
- Add more feed items to test sequential updates 