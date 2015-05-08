# -*- coding: utf-8 -*-

"""
Modulo per la gestione della pagina di login all'account.
"""


#= IMPORT ======================================================================

import pprint
import string

from twisted.web import server

from src.color        import remove_colors
from src.config       import config
from src.database     import database
from src.enums        import LOG
from src.log          import log
from src.web_resource import WebResource


#= CLASSI ======================================================================

class LoginPage(WebResource):
    """
    Pagina web per loggarsi al Mud.
    """
    TITLE = "Login"

    PAGE_TEMPLATE = string.Template(open("src/views/login.view").read())

    NEW_PAGE = True

    def render_GET(self, request, conn):
        if conn.account:
            request.redirect("players.html")
            request.finish()
            return server.NOT_DONE_YET

        mapping = {"game_name" : config.game_name}
        return self.PAGE_TEMPLATE.safe_substitute(mapping)
    #- Fine Metodo -

    def render_POST(self, request, conn):
        # Ricava i dati di login
        name = ""
        if "name" in request.args:
            name = request.args["name"][0].capitalize()

        password = ""
        if "password" in request.args:
            password = request.args["password"][0]

        # Controlla i dati di login
        if name not in database["accounts"]:
            return "Nome account inesistente."
        elif password != database["accounts"][name].password:
            return "Password errata."

        # ---------------------------------------------------------------------

        # Se invece è tutto a posto procede con la pagina di account
        conn.account = database["accounts"][name]

        # Aggiunge l'user agent utilizzato nella connessione
        if request.received_headers and "user-agent" in request.received_headers:
            user_agent = request.received_headers["user-agent"]
            if user_agent:
                if user_agent in conn.account.user_agents:
                    # Lo rimuove per mantenere sempre al posto più recente
                    # il browser utilizzato per ultimo
                    conn.account.user_agents.remove(user_agent)
                conn.account.user_agents.append(user_agent)

        return ""
    #- Fine Metodo -
