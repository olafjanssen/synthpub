from blinker import signal

# Define signals
topic_update_requested = signal('topic-update-requested', doc='Topic update requested')
topic_updated = signal('topic-updated', doc='Topic description updated')
topic_saved = signal('topic-saved', doc='Topic saved')