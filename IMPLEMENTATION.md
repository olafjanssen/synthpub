# Important SynthPub implementation decisions

## Pexels API Integration

SynthPub uses the Pexels API to find relevant images for project and topic thumbnails. The system:

1. Uses project/topic title and description for image search
2. Automatically selects appropriate images related to the content

Make sure you have a valid Pexels API key in your `settings.yaml` file to enable this feature.

## Feed Queue Architecture

SynthPub uses a queue-based architecture for processing content feeds:

1. **Feed Connectors**: Each connector (RSS, YouTube, etc.) is responsible only for fetching content from its specific type of source. When a feed update is requested:
   - The appropriate connector recognizes and handles the feed URL
   - It fetches all items from the aggregate feed
   - Each individual item is placed on a dedicated feed item queue via signals

2. **Feed Item Processing**: Items in the queue are processed independently:
   - Items are taken from the queue one by one
   - Each item is processed based on relevance to the associated topic
   - Relevant content is incorporated into the article
   
This separation of concerns ensures that:
- Feed connectors focus solely on retrieval of content from their specific sources
- Processing logic is centralized and consistent across different feed types
- The system is more scalable and maintainable