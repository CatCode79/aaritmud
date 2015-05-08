# -*- coding: utf-8 -*-

"""
Modulo per la gestione della pagina web che serve a chiudere il Mud.
"""


#= IMPORT ======================================================================

import string

from src.config       import config
from src.database     import database
from src.engine       import engine
from src.enums        import TRUST
from src.utility      import is_number
from src.web_resource import WebResource


#= CLASSI ======================================================================

class ShutdownPage(WebResource):
    """
    Serve a chiudere il gioco in maniera il più pulita possibile.
    """
    TITLE = "Shutdown"

    ACCOUNT_MUST_EXIST_IN_GET  = True
    ACCOUNT_MUST_EXIST_IN_POST = True

    MINIMUM_TRUST_ON_GET  = TRUST.IMPLEMENTOR
    MINIMUM_TRUST_ON_POST = TRUST.IMPLEMENTOR

    PAGE_TEMPLATE = string.Template(open("src/views/shutdown.view").read())

    NEW_PAGE = True

    def render_GET(self, request, conn):
        if engine.seconds_to_shutdown >= 0:
            return '''<span id="message_of_shutdown">La Shutdown avverrà tra %d secondi.</span><br>''' % engine.seconds_to_shutdown
        else:
            mapping = {"game_name" : config.game_name}
            return self.PAGE_TEMPLATE.safe_substitute(mapping)
    #- Fine Metodo -

    def render_POST(self, request, conn):
        error_message = ""
        if "minutes" not in request.args:
            return '''<br><span style="color:red">La richiesta di shutdown non è valida</span><br>'''

        minutes = request.args["minutes"][0]
        if not is_number(minutes):
            return '''<br><span style="color:red">Il valore relativo ai minuti è risultato errato: %s</span><br>''' % minutes

        database.avoid_backup_on_shutdown = False
        database.avoid_save_on_shutdown = False
        database.only_player_persistence = False
        if "avoid_backup" in request.args and request.args["avoid_backup"][0] == "1":
            database.avoid_backup_on_shutdown = True
        if "avoid_save" in request.args and request.args["avoid_save"][0] == "1":
            database.avoid_save_on_shutdown = True
        if "only_player_persistence" in request.args and request.args["only_player_persistence"][0] == "1":
            database.only_player_persistence = True

        # Il tutto viene poi gestito dal loop principale
        engine.seconds_to_shutdown = int(minutes) * 60
        javascript = '''<script>current_interval = setInterval(refreshSecondsToShut, 1000);</script>'''
        return '''Lo Shutdown di %s avverà tra <span name="seconds_to_shutdown">%d</span> secondi.%s''' % (
            config.game_name, engine.seconds_to_shutdown, javascript)
    #- Fine Metodo -
