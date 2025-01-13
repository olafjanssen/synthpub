from blinker import signal

# Topic update signals
topic_update_requested = signal('topic-update-requested', doc='Topic update requested')
topic_updated = signal('topic-updated', doc='Topic description updated')
topic_saved = signal('topic-saved', doc='Topic saved')
topic_published = signal('topic-published', doc='Topic published')

article_updated = signal('article-updated', doc='Article updated')

news_feed_update_requested = signal('news-feed-update-requested', doc='News feed update requested')
news_feed_item_found = signal('news-feed-item-found', doc='News feed item found')
publish_requested = signal('publish-requested', doc='Publish requested')

