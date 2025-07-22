import sentry_sdk

class SentryService:

    def __init__(self):
        sentry_sdk.init(
            dsn="https://3dced3899dece3439a4debe9149150a2@o4509713235378176.ingest.de.sentry.io/4509713236951120",
            send_default_pii=True,
        )