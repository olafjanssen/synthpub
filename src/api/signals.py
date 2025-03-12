from blinker import signal

# Topic update signals
topic_update_requested = signal('topic-update-requested', doc='Topic update requested')

# Feed processing signals
news_feed_item_found = signal('news-feed-item-found', doc='News feed item found')

# Publishing signals
publish_requested = signal('publish-requested', doc='Publish requested')
convert_requested = signal('convert-requested', doc='Convert requested')

