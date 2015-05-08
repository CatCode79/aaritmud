# -*- coding: utf-8 -*-

"""
Modulo per la gestione della pagina dei punteggi dei personaggi.
"""


#= IMPORT ======================================================================

from src.web_resource import WebResource


#= CLASSI ======================================================================

class RankingsPage(WebResource):
    """
    Pagina web utilizzata per visualizzare le classifiche dei giocatori
    riguardo ore di gioco, livelli e altro.
    """
    TITLE = "Rankings"

    # (TD) basarsi sulla BuildListPage e la funzione sort_datas per fare questa classe.
    def render_GET(self, request, conn):
        return self.create_page(request, conn)
    #- Fine Metodo -

    def render_POST(self, request, conn):
        # Ricava gli argomenti del form dalla richiesta
        # (TD)
        # Controlla la validità degli argomenti inseriti nel form
        # (TD)
        return self.create_page(request, conn)
    #- Fine Metodo -

    def create_page(self, request, conn):
        # Prepara il form con i dati per xxx
#        form = [["" for y in xrange(3)] for x in xrange()]
#        form[0][0]  = ''''''
#        form[0][1]  = ''''''
#        if not correct_:
#            form[0][2]  = ''''''

        # Crea la pagina html
        page = '''<p><h3 align="center">CLASSIFICHE<br></h3></p>'''
        return page
    #- Fine Metodo -
