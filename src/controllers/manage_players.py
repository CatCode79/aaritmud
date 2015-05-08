# -*- coding: utf-8 -*-

"""
Modulo per la gestione della pagina web con tutti i link per la gestione
amministrativa dei giocatori.
"""


#= IMPORT ======================================================================

import string

from src.config       import config
from src.enums        import TRUST
from src.web_resource import WebResource

if config.reload_web_pages:
    reload(__import__("src.controllers.manage_players_bans",  globals(), locals(), [""]))
    reload(__import__("src.controllers.manage_players_gifts", globals(), locals(), [""]))
from src.controllers.manage_players_bans  import ManagePlayersBansPage
from src.controllers.manage_players_gifts import ManagePlayersGiftsPage


#= CLASSI ======================================================================

class ManagePlayersPage(WebResource):
    TITLE = "Gestione Giocatori"

    ACCOUNT_MUST_EXIST_IN_GET  = True
    ACCOUNT_MUST_EXIST_IN_POST = True

    MINIMUM_TRUST_ON_GET  = TRUST.MASTER
    MINIMUM_TRUST_ON_POST = TRUST.MASTER

    PAGE_TEMPLATE = string.Template(open("src/views/manage_players.view").read())

    NEW_PAGE = True

    def render_GET(self, request, conn):
        hide_manage_players_bans = ""
        if not conn or not conn.account or conn.account.trust < ManagePlayersBansPage.MINIMUM_TRUST_ON_GET:
            hide_manage_players_bans = " visibility:hidden;"

        hide_manage_players_gifts = ""
        if not conn or not conn.account or conn.account.trust < ManagePlayersGiftsPage.MINIMUM_TRUST_ON_GET:
            hide_manage_players_gifts = " visibility:hidden;"

        show_empty_message = ''' class="invisible"'''
        if hide_manage_players_bans and hide_manage_players_gifts:
            show_empty_message = ""

        mapping = {"show_empty_message"        : show_empty_message,
                   "trust"                     : str(conn.account.trust),
                   "hide_manage_players_bans"  : hide_manage_players_bans,
                   "hide_manage_players_gifts" : hide_manage_players_gifts}
        return self.PAGE_TEMPLATE.safe_substitute(mapping)
    #- Fine Metodo -
