# -*- coding: utf-8 -*-

"""
Modulo per la visualizzazione del contenuto del file di log.
"""


#= IMPORT ======================================================================

from twisted.web.server import NOT_DONE_YET

from src.color        import convert_colors
from src.defer        import defer
from src.enums        import TRUST
from src.utility      import html_escape, iter_filenames
from src.web_resource import WebResource


#= CLASSI ======================================================================

class ShowLogsPage(WebResource):
    """
    Visualizza il contenuto dei file di log.
    """
    TITLE = "Show Logs"

    ACCOUNT_MUST_EXIST_IN_GET  = True
    ACCOUNT_MUST_EXIST_IN_POST = True

    MINIMUM_TRUST_ON_GET  = TRUST.MASTER
    MINIMUM_TRUST_ON_POST = TRUST.MASTER

    def render_GET(self, request, conn):
        if "file" not in request.args:
            page = ['''<h3>Lista dei File di Log consultabili:</h3>''']
            for root, filename in iter_filenames("log"):
                page.append('''<a href="show_logs.html?file=%s">%s</a><br>''' % (filename, filename))
            return "".join(page)

        # Stampa il contenuto del file scelto
        filepath = "log/" + request.args["file"][0]
        try:
            file = open(filepath, "r")
        except:
            return "Impossibile aprire il file %s in lettura." % filepath

        # Per evitare che attenda la scrittura del contenuto completo crea
        # una "deferred fasulla" per scrivere la pagina piano piano
        d = defer(0, self.send_log_content, request, conn, file)
        d.addErrback(self.error_on_sending_log)

        return NOT_DONE_YET
    #- Fine Metodo -

    def send_log_content(self, request, conn, file):
        # Scrive poco a poco il file di log che può raggiungere
        # dimensioni ragguardevoli
        for line in file:
            request.write(convert_colors(html_escape(line)) + "<br>")
        request.finish()
    #- Fine Metodo -

    def error_on_sending_log(self):
        log.bug("Errore nell'invio del file di log alla pagina di consultazione dei file di log.")
    #- Fine Metodo -
