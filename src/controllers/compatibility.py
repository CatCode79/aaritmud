# -*- coding: utf-8 -*-

"""
Modulo per la visualizzazione di tutti i topic di help.
"""


#= IMPORT ======================================================================

import datetime
import string
import urllib

from src.config       import config
from src.web_resource import WebResource


#= CLASSI ======================================================================

class CompatibilityPage(WebResource):
    """
    Pagina web utilizzata per visualizzare i topic relativi agli help.
    """
    TITLE = "Compatibility"

    ACCOUNT_MUST_EXIST_IN_GET  = False
    ACCOUNT_MUST_EXIST_IN_POST = True

    PAGE_TEMPLATE = string.Template(open("src/views/compatibility.view").read())

    def render_GET(self, request, conn):
        mapping = {"max_feedback_len" : config.max_feedback_len,
                   "game_name"          : config.game_name,
                   "browser_code"       : conn.get_browser(),
                   "login_message"      : "." if conn.account else ", connettendoti al sito <a href='login.html'>da qui</a>.",
                   "disabled_color"     : "" if conn.account else "style='color:grey'",
                   "disabled_attribute" : "" if conn.account else "disabled='disabled'",
                   "disabled_message"   : "" if conn.account else "Connettiti al sito per poter inviare un messaggio qui"}
        return self.PAGE_TEMPLATE.safe_substitute(mapping)
    #- Fine Metodo -

    def render_POST(self, request, conn):
        if not conn:
            return "La connessione non è valida"

        if not conn.account:
            return "Per poter inviare messaggi devi eseguire il login al sito"

        msg = ""
        if "msg" in request.args:
            msg = request.args["msg"][0]
        if not msg:
            log.bug("messagge non valido: %r" % msg)
            return "Il messaggio è vuoto"

        msg = urllib.unquote(msg)
        if len(msg) > config.max_feedback_len:
            return "Il messaggio è troppo lungo, massimo %d" % config.max_feedback_len

        compatibility_path = "persistence/compatibility.feedbacks"
        try:
            compatibility_file = open(compatibility_path, "a")
        except IOError:
            log.bug("Impossibile aprire il file %s in append: %r" % compatibility_path)
            return "Errore nell'apertura del database dei messaggi"

        feedback = "%s\%s\n%s\n%s\n\n" % (datetime.datetime.now(), conn.account.name, request.received_headers["user-agent"], msg)
        compatibility_file.write(feedback)
        compatibility_file.close()

        return ""
    #- Fine Metodo -
