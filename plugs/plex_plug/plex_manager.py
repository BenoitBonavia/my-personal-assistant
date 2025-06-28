import json
import os

from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer

from plugs.parent_manager import ParentManager

class PlexManager(ParentManager):
    """
    This class is used to manage the plex media server and the tv plex client
    """

    def __init__(self, config_file='plugs/plex_plug/plex_configuration.json'):
        super().__init__()
        self.manager_name = 'plex'
        with open(config_file) as config_file:
            self.config = json.load(config_file)
            self.base_url = self.config['base_url']
            self.token = os.environ['X_PLEX_TOKEN']
            self.server = PlexServer(self.base_url, self.token)
            self.plex_account = MyPlexAccount(token=self.token)

    def print_known_clients(self):
        """Print all the clients known to the Plex account."""
        clients = []
        for resource in self.plex_account.resources():
            if "player" in resource.provides:
                print(resource.name)
                clients.append(resource.name)
        return clients
