import os
from androidtv import AndroidTVSync

class AndroidTvManager:
    """
    This class is used to manager the TV in the house through the Android TV API
    """

    def __init__(self):
        self.androidtv = AndroidTVSync(host=os.getenv('ANDROIDTV_HOST'))
        self.androidtv.adb_connect()
