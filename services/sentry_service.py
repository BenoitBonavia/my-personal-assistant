import sentry_sdk
import logging
from sentry_sdk.integrations.logging import LoggingIntegration

class SentryService:

    def __init__(self):
        sentry_logging = LoggingIntegration(
            level=logging.INFO,
            event_level=logging.ERROR
        )
        sentry_sdk.init(
            dsn="https://3dced3899dece3439a4debe9149150a2@o4509713235378176.ingest.de.sentry.io/4509713236951120",
            send_default_pii=True,
            integrations=[sentry_logging]
        )