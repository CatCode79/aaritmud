# -*- coding: utf-8 -*-

"""
Modulo di gestione della manutenzione del Mud sul lungo tempo: log di
informazioni varie e pulizia delle persistenze.
"""


#= IMPORT ======================================================================

import datetime

from src.config   import config
from src.database import database
from src.enums    import DOOR, FLAG
from src.log      import log
from src.loop     import UnstoppableLoop


#= CLASSI ======================================================================

class MaintenanceLoop(UnstoppableLoop):
    def __init__(self):
        super(MaintenanceLoop, self).__init__()
        self.paused = False
    #- Fine Inizializzazione -

    def start(self, seconds=0):
        if seconds == 0:
            seconds = config.maintenance_loop_seconds
        super(MaintenanceLoop, self).start(seconds)
    #- Fine Metodo -

    def stop(self):
        if self.running:
            super(MaintenanceLoop, self).stop()
        else:
            log.bug("Il MaintenanceLoop non è stato trovato attivo.")
    #- Fine Metodo -

    def cycle(self):
        if self.paused:
            return

        self.check_idle_players()

        now = datetime.datetime.now()
        if now.minute == 0:
            log.cpu_time()

        if now.hour == 4 and now.minute == 0:
            database.backup("automatic_daily_backup")
    #- Fine Metodo -

    def check_idle_players(self):
        for player in database["players"].itervalues():
            if not player.game_request:
                continue
            if player.get_conn():
                continue
            player.idle_seconds += 1
            if player.idle_seconds > config.max_idle_seconds:
                # Chiude le connessioni dei giocatori che sono rimasti troppo
                # tempo in idle connection
                player.game_request.finish()
    #- Fine Metodo -


#= SINGLETON ===================================================================

maintenance_loop = MaintenanceLoop()
