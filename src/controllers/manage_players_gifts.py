# -*- coding: utf-8 -*-

"""
Modulo per la gestione dei regali dati ai giocatori.
"""


#= IMPORT ======================================================================

import string
import weakref

from src.config       import config
from src.database     import database
from src.enums        import TRUST
from src.utility      import sort_datas
from src.web_resource import WebResource, create_tooltip


#= CLASSI ======================================================================

class ManagePlayersGiftsPage(WebResource):
    TITLE = "Gestione Regali"

    ACCOUNT_MUST_EXIST_IN_GET  = True
    ACCOUNT_MUST_EXIST_IN_POST = True

    MINIMUM_TRUST_ON_GET  = TRUST.IMPLEMENTOR
    MINIMUM_TRUST_ON_POST = TRUST.IMPLEMENTOR

    PAGE_TEMPLATE = string.Template(open("src/views/manage_players_gifts.view").read())

    NEW_PAGE = True

    def render_GET(self, request, conn):
        mapping = {"player_gifts" : self.create_player_gifts(request, conn)}
        return self.PAGE_TEMPLATE.safe_substitute(mapping)
    #- Fine Metodo -

    def create_player_gifts(self, request, conn):
        output = []

        output.append('''<table>''')
        output.append('''<tr><th>Giocatori:</th><th>Doni:</th></tr>''')
        for player_code, player in sort_datas(database["players"]):
            if not player.gifts:
                continue
            output.append('''<tr><td>%s</td><td>%s</td></tr>''' % (player.name, get_gift_codes(player, conn)))
        output.append('''</table>''')

        return "".join(output)
    #- Fine Metodo -

    def render_POST(self, request, conn):
        gift_counter = 0

        for player in database["players"].itervalues():
            if not player.gifts:
                continue
            for gift in player.gifts:
                if player_has_gift(player, gift):
                    continue
                refounded = gift.CONSTRUCTOR(gift.code)
                if player.game_request:
                    refounded.inject(player)
                else:
                    database[refounded.ACCESS_ATTR][refounded.code] = refounded
                    refounded.area = player.area
                    refounded.previous_location = weakref.ref(player)
                    refounded.owner = weakref.ref(player)
                gift_counter += 1

        return "Sono stati ridonati %d regali." % gift_counter
    #- Fine Metodo -


#= FUNZIONI ====================================================================

def get_gift_codes(player, conn):
    if not player:
        log.bug("player non è un parametro valido: %r" % player)
        return ""

    if not conn:
        log.bug("conn non è un parametro valido: %r" % conn)
        return ""

    # ---------------------------------------------------------------------

    output = ""
    for gift in player.gifts:
        color_open = ""
        color_close = ""
        if player_has_gift(player, gift):
            color_open = "[green]"
            color_close = "[close]"
        output += create_tooltip(conn, gift.get_name(), color_open + gift.code + color_close) + ", "

    return output.strip(", ")
#- Fine Funzione -


def player_has_gift(player, gift):
    if not player:
        log.bug("player non è un parametro valido: %r" % player)
        return False

    if not gift:
        log.bug("gift non è un parametro valido: %r" % gift)
        return False

    # ---------------------------------------------------------------------

    table_name = gift.ACCESS_ATTR.split("_")[1]
    for entity in database[table_name].itervalues():
        if not entity.prototype:
            log.bug("entity senza prototipo valido: %r" % entity)
            continue
        if entity.prototype.code != gift.code:
            continue
        if entity.owner and entity.owner() and entity.owner() == player:
            return True

    return False
#- Fine Funzione -
