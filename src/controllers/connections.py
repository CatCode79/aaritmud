# -*- coding: utf-8 -*-

"""
Modulo per la pagina web relativa alla visualizzazione della lista delle
connessioni al Mud.
"""


#= IMPORT ======================================================================

import string

from src.connection   import connections
from src.enums        import TRUST
from src.log          import log
from src.utility      import html_escape
from src.web_resource import WebResource


#= CLASSI ======================================================================

class ConnectionsPage(WebResource):
    """
    Visualizza il menù di accesso per la visualizzazione dei dati o per il loro
    building.
    """
    TITLE = "Connections"

    ACCOUNT_MUST_EXIST_IN_GET  = True
    ACCOUNT_MUST_EXIST_IN_POST = True

    MINIMUM_TRUST_ON_GET  = TRUST.MASTER
    MINIMUM_TRUST_ON_POST = TRUST.MASTER

    PAGE_TEMPLATE = string.Template(open("src/views/connections.view").read())

    def render_GET(self, request, conn):
        mapping = {"connections" : self.get_connections(request, conn)}
        return self.PAGE_TEMPLATE.safe_substitute(mapping)
    #- Fine Metodo -

    def get_connections(self, request, conn):
        rows = []

        for conn in connections.itervalues():
            rows.append('''<tr>''')

            rows.append('''<td>%s</td>''' % conn.get_id(conn))
            rows.append('''<td>%s</td>''' % conn.logged_on)
            if "user-agent" in conn.request.received_headers:
                rows.append('''<td>%s</td>''' % conn.request.received_headers["user-agent"])
            else:
                log.bug("Connessione senza user-agent: %s" % conn.get_id())
                rows.append('''<td>[red]Empty[close]</td>''')
            rows.append('''<td>%s</td>''' % html_escape("%r" % conn.request))
            rows.append('''<td>%d</td>''' % (conn.player.idle_seconds if conn.player else 0))

            rows.append('''</tr>''')

        return "".join(rows)
    #- Fine Metodo -
