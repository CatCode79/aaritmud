# -*- coding: utf-8 -*-

"""
Modulo per la gestione della pagina web che serve a chiudere il Mud.
"""


#= IMPORT ======================================================================

import string

from src.color        import convert_colors
from src.config       import config
from src.database     import database
from src.enums        import TRUST
from src.web_resource import WebResource


#= CLASSI ======================================================================

class BackupDbPage(WebResource):
    """
    Serve a forzare un backup di tutta la cartella data.
    """
    TITLE = "Backup DB"

    ACCOUNT_MUST_EXIST_IN_GET  = True
    ACCOUNT_MUST_EXIST_IN_POST = True

    MINIMUM_TRUST_ON_GET  = TRUST.MASTER
    MINIMUM_TRUST_ON_POST = TRUST.MASTER

    PAGE_TEMPLATE = string.Template(open("src/views/backup_db.view").read())

    NEW_PAGE = True

    def render_GET(self, request, conn):
        mapping = {}
        return self.PAGE_TEMPLATE.safe_substitute(mapping)
    #- Fine Metodo -

    def render_POST(self, request, conn):
        if "backup_db" not in request.args:
            return '''<span style="colore:red">Era atteso il parametro backup_db durante il POST.</span>'''

        database.backup("web_backup_of_%s" % conn.account.name.lower())
        return '''Backup delle cartelle data e persistence di %s eseguito con successo.''' % (
            convert_colors(config.game_name))
    #- Fine Metodo -
