from blinker import signal

# Topic update signals
topic_update_requested = signal('topic-update-requested', doc='Topic update requested')

# Publishing signals
publish_requested = signal('publish-requested', doc='Publish requested')
convert_requested = signal('convert-requested', doc='Convert requested')

