# -*- coding: utf-8 -*-

"""
Modulo per la modifica delle descrizioni dei personaggi.
"""


#= IMPORT ======================================================================

import pprint
import string
import urllib

from src.config       import config
from src.interpret    import translate_input
from src.utility      import sort_datas
from src.web_resource import WebResource


#= CLASSI ======================================================================

class DescriptionsPage(WebResource):
    """
    Pagina utilizzata per gestire le descrizioni dei vari personaggi.
    """
    TITLE = "Descrizioni"

    ACCOUNT_MUST_EXIST_IN_GET  = True
    ACCOUNT_MUST_EXIST_IN_POST = True

    PAGE_TEMPLATE = string.Template(open("src/views/descriptions.view").read())

    DESCR_ATTRS = ["descr",         "descr_night",
                   "descr_hearing", "descr_hearing_night",
                   "descr_smell",   "descr_smell_night",
                   "descr_touch",   "descr_touch_night",
                   "descr_taste",   "descr_taste_night",
                   "descr_sixth",   "descr_sixth_night"]

    NEW_PAGE = True

    def render_GET(self, request, conn):
        mapping = {"players"   : self.create_player_options(request, conn),
                   "look"      : translate_input(conn, "look", "en", colorize=True),
                   "listen"    : translate_input(conn, "listen", "en", colorize=True),
                   "smell"     : translate_input(conn, "smell", "en", colorize=True),
                   "touch"     : translate_input(conn, "touch", "en", colorize=True),
                   "taste"     : translate_input(conn, "taste", "en", colorize=True),
                   "intuition" : translate_input(conn, "intuition", "en", colorize=True)}
        return self.PAGE_TEMPLATE.safe_substitute(mapping)
    #- Fine Metodo -

    def create_player_options(self, request, conn):
        options = ""
        for player_code, player in sort_datas(conn.account.players):
            options += '''\t<option>%s</option>\n''' % player_code
        return options
    #- Fine Metodo -

    def render_POST(self, request, conn):
        choised_player = None
        if "player_code" in request.args:
            player_code = request.args["player_code"][0]
            if player_code in conn.account.players:
                choised_player = conn.account.players[player_code]
        else:
            return "Codice di giocatore non trovato."

        if not choised_player:
            return "Giocatore non trovato."

        if "refresh_descrs" in request.args:
            return self.refresh_descrs(request, conn, choised_player)
        else:
            return self.save_descrs(request, conn, choised_player)
    #- Fine Metodo -

    def refresh_descrs(self, request, conn, choised_player):
        """
        Aggiorna le descrizioni del personaggio inviando le informazioni tramite
        sintassi json (che è identica a quella di un dizionario python).
        """
        descriptions = {}
        for descr_attr in self.DESCR_ATTRS:
            if getattr(choised_player, descr_attr):
                descriptions[descr_attr] = urllib.quote(getattr(choised_player, descr_attr))

        return pprint.pformat(descriptions, indent=0)
    #- Fine Metodo -

    def save_descrs(self, request, conn, choised_player):
        for descr_attr in self.DESCR_ATTRS:
            if descr_attr in request.args:
                text_to_save = urllib.unquote(request.args[descr_attr][0])
                setattr(choised_player, descr_attr, text_to_save)
            else:
                setattr(choised_player, descr_attr, "")
        return ""
    #- Fine Metodo -
