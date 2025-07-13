"""Manager used to control a Plex Media Server and its clients."""

import json
import logging
import os

from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer

from plugs.parent_manager import ParentManager


logger = logging.getLogger(__name__)


class PlexManager(ParentManager):
    """Manage the Plex Media Server and connected clients."""

    def __init__(self, config_file: str = 'plugs/plex_plug/plex_configuration.json'):
        super().__init__()
        self.manager_name = 'plex'
        with open(config_file, encoding='utf-8') as conf_file:
            self.config = json.load(conf_file)
            self.base_url = self.config['base_url']

        self.token = os.environ['X_PLEX_TOKEN']
        self.server = PlexServer(self.base_url, self.token)
        try:
            self.plex_account = MyPlexAccount(token=self.token)
        except Exception:  # pragma: no cover - network access required
            logger.exception("Unable to connect to Plex account")
            self.plex_account = None

    def get_clients(self):
        """Get list of clients connected to the Plex server."""
        clients = self.server.clients()
        logger.info("Clients: %s", clients)
        return clients

    def search_media(self, title: str):
        """Search for a media by title across libraries."""
        results = self.server.search(title)
        logger.info("Search '%s' -> %s", title, results)
        return results

    def play_media(self, client_name: str, media_title: str):
        """Play the specified media on the given client."""
        client = None
        for c in self.server.clients():
            if c.title == client_name:
                client = c
                break

        if client is None:
            logger.error("Client %s not found", client_name)
            return

        results = self.search_media(media_title)
        if not results:
            logger.error("Media %s not found", media_title)
            return

        media = results[0]
        try:
            client.playMedia(media)
            logger.info("Playing %s on %s", media, client_name)
        except Exception:  # pragma: no cover - requires active Plex client
            logger.exception("Unable to play %s on %s", media_title, client_name)
