from blinker import signal

# Publishing signals
publish_requested = signal("publish-requested", doc="Publish requested")
convert_requested = signal("convert-requested", doc="Convert requested")
