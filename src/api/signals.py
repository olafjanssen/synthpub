from blinker import signal

# Topic update signals
topic_update_requested = signal('topic-update-requested', doc='Topic update requested')

news_feed_update_requested = signal('news-feed-update-requested', doc='News feed update requested')
news_feed_item_found = signal('news-feed-item-found', doc='News feed item found')
publish_requested = signal('publish-requested', doc='Publish requested')
convert_requested = signal('convert-requested', doc='Convert requested')

