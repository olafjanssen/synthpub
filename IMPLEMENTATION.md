# Important SynthPub implementation decisions

## Feed Cache System

SynthPub implements a file-based cache system for news feed items to improve performance and reduce redundant network requests:

1. **Cache Architecture**:
   - Each feed URL is cached as a separate JSON file in the `_cache` directory
   - Files are named using a human-readable version of the URL with a short hash suffix
     - Example: `https://example.com/feed` → `https_example.com_feed_a1b2c3d4.json`
   - Ensures uniqueness while maintaining readability for debugging
   - No additional metadata stored in the database (simple design)

2. **Cache Management**:
   - Maximum cache size: 500MB
   - Automatic cleanup when cache reaches 90% capacity (450MB)
   - Each connector specifies its own expiration time:
     - Web pages: 1 day (86400 seconds)
     - RSS feeds: 1 hour (3600 seconds)
     - YouTube content: 6 hours (21600 seconds)
     - arXiv papers: 24 hours (86400 seconds)
     - Gmail: 15 minutes (900 seconds)
     - File system: indefinite (-1, cached forever)

3. **Cache Behavior**:
   - `-1`: Cache forever (default, used for static content)
   - `0`: Never cache (used for frequently changing content)
   - Positive value: Cache for specified seconds

4. **Cache Cleanup Strategy**:
   - First removes expired items
   - Then removes oldest non-forever-cached items when size limit exceeded
   - Preserves items with `-1` expiration unless absolutely necessary

5. **Integration with Feed Processing**:
   - Cache is checked before making network requests
   - Both aggregate and content-specific feeds are cached
   - Items with `needs_further_processing=True` still benefit from caching at each level
   - Dramatically reduces redundant network requests for frequently accessed feeds

This system minimizes redundant network requests while ensuring fresh content when needed, significantly improving feed processing performance.

## Pexels API Integration

SynthPub uses the Pexels API to find relevant images for project and topic thumbnails. The system:

1. Uses project/topic title and description for image search
2. Automatically selects appropriate images related to the content

Make sure you have a valid Pexels API key in your `settings.yaml` file to enable this feature.

## Feed Queue Architecture

SynthPub uses a queue-based architecture for processing content feeds:

1. **Feed Items**: Each content item includes a `needs_further_processing` flag that determines its handling:
   - `needs_further_processing=True`: Item contains a URL that needs to be fetched by another connector
   - `needs_further_processing=False`: Item contains final content ready for processing

2. **Processing Flow**:
   - When a feed URL is processed, the appropriate connector fetches all items
   - Results are cached based on the connector's `cache_expiration` setting
   - Items marked for further processing trigger new feed update requests
   - Final content items are sent to the feed item queue for processing

3. **Component Interaction**:
   - `FeedConnector.handle_feed_update()`: Processes URLs and checks cache
   - `handle_feed_item()`: Routes items based on their `needs_further_processing` flag
   - `queue_feed_item()`: Places items in the queue for asynchronous processing
   - `process_update_queue()`: Worker that processes items from both topic and feed queues

This approach provides several advantages:
- Each connector decides per-item whether further processing is needed
- Processing is determined at the item level, not the connector level
- Caching happens at every level, optimizing network requests
- More flexible than categorizing entire connectors as aggregate or non-aggregate
- Allows connectors like YouTube to handle both individual videos and playlists appropriately

### Aggregate Connectors

The system includes several connectors that handle aggregate feeds containing multiple individual items:

1. **RSS Connector**: 
   - Extracts links from RSS feeds and marks them for further processing
   - Web content is then fetched by the appropriate connector when processing each link
   - Cached for 1 hour (3600 seconds)

2. **YouTube Connector**:
   - For channels/playlists: Returns video URLs marked for further processing
   - For individual videos: Returns the complete transcript with no further processing needed
   - Cached for 6 hours (21600 seconds)

3. **File Connector**:
   - For glob patterns (like `file:///path/to/*.txt`): Returns file URLs marked for further processing
   - For individual files: Returns the complete file content with no further processing needed
   - Cached indefinitely (-1)

4. **arXiv Connector**:
   - For search queries: Returns paper URLs marked for further processing
   - When processing individual papers: Downloads and extracts PDF content
   - Cached for 24 hours (86400 seconds)

5. **Gmail Connector**:
   - For the inbox URL (`gmail://`): Returns message IDs marked for further processing
   - When processing individual messages: Fetches the complete email content
   - Cached for 15 minutes (900 seconds)

Each connector follows the same pattern of separating content acquisition from processing, using the `needs_further_processing` flag to make item-by-item decisions.

## Logging System

SynthPub includes a comprehensive logging system that provides:

1. **System Logs** - Internal debug, info, warning, and error messages for developers
2. **User Logs** - Clear, concise messages displayed to end users in the web interface

## Prompt Templates

SynthPub uses customizable prompt templates stored as Markdown files in the `resources/prompts` directory. These templates are used for various LLM operations:

- `article-generation.md`: Template for generating new articles
- `article-refinement.md`: Template for refining existing articles with new context
- `article-relevance-filter.md`: Template for determining if new content is relevant to an existing article

You can modify these templates to customize the behavior of the LLM operations. The templates are loaded automatically when the application starts.

### Structured Output Parsing

For certain operations like relevance filtering, SynthPub uses Pydantic models to enforce structured output from LLMs. This ensures consistent and reliable responses that can be easily processed by the application. The output format instructions are automatically appended to the prompt templates at runtime.

## Curator Chain Architecture

SynthPub implements a modular, composable curator chain architecture for processing and filtering content from feeds. The implementation uses LangChain Expression Language (LCEL) with individual Runnable components:

- Each step in the curator chain is implemented as a separate `Runnable` class
- Components can be combined and reordered easily without changing the underlying code
- Each component focuses on a single responsibility:
  - `InputCreatorStep`: Prepares and normalizes input data for processing
  - `RelevanceFilterStep`: Determines if content is relevant to the topic
  - `ArticleRefinerStep`: Refines the article with new relevant content
  - `ResultProcessorStep`: Transforms chain results into the required output format
