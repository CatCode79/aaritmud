# -*- coding: utf-8 -*-

"""
Modulo per la gestione di tutte le punizione dei giocatori.
"""


#= IMPORT ======================================================================

import string

from src.ban          import count_bans
from src.config       import config
from src.database     import database
from src.enums        import TRUST
from src.utility      import sort_datas, pretty_date
from src.web_resource import WebResource, create_tooltip


#= CLASSI ======================================================================

class ManagePlayersBansPage(WebResource):
    TITLE = "Gestione Punizioni"

    ACCOUNT_MUST_EXIST_IN_GET  = True
    ACCOUNT_MUST_EXIST_IN_POST = True

    MINIMUM_TRUST_ON_GET  = TRUST.IMPLEMENTOR
    MINIMUM_TRUST_ON_POST = TRUST.IMPLEMENTOR

    PAGE_TEMPLATE = string.Template(open("src/views/manage_players_bans.view").read())

    NEW_PAGE = True

    def render_GET(self, request, conn):
        if count_bans() == 0:
            player_bans = "[green]Nessuna punizione inflitta ai giocatori.[close]"
        else:
            player_bans = self.create_player_bans(conn)

        player_options = []
        for player_code, player in sort_datas(database["players"]):
            if not player.ban:
                player_options.append('''<option>%s</option>''' % player_code)

        day_options = []
        for day in range(1, 31):
            day_options.append('''<option>%d</option>''' % day)

        reason_tooltip = create_tooltip(conn, "Questo testo verrà letto dal giocatore come motivazione della punizione")

        comment_tooltip = create_tooltip(conn, "Questo commento verrà letto solo dagli amministratori, utile per aggiungere delle note per una gestione interna della punizione")

        mapping = {"player_options"  : "".join(player_options),
                   "day_options"     : "".join(day_options),
                   "reason_tooltip"  : reason_tooltip,
                   "comment_tooltip" : comment_tooltip,
                   "player_bans"     : player_bans}
        return self.PAGE_TEMPLATE.safe_substitute(mapping)
    #- Fine Metodo -

    def create_player_bans(self, conn):
        output = []

        output.append('''<table rules="rows">''')
        output.append('''<tr><th>Giocatore:</th><th>Punizione Dal:</th><th>Per:</th><th>Motivo:</th></tr>''')
        for player_code, player in sort_datas(database["players"]):
            if not player.ban:
                continue
            output.append('''<tr><td>%s</td><td>%s</td><td align="center">%d giorn%s</td><td>%s</td></tr>''' % (
                player.name,
                pretty_date(player.ban.starting_from) if player.ban.starting_from else "Deve collegarsi",
                player.ban.days,
                "o" if player.ban.days == 1 else "i",
                create_tooltip(conn, player.ban.comment, player.ban.reason) if player.ban.comment else player.ban.reason))
        output.append('''</table>''')

        return "".join(output)
    #- Fine Metodo -
