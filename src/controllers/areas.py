# -*- coding: utf-8 -*-

"""
Modulo per la gestione della pagine
"""


#= IMPORT ======================================================================

import operator

from src.behaviour    import create_tooltip_behaviour
from src.database     import database
from src.enums        import AREA, TRUST
from src.web_resource import WebResource, create_tooltip


#= CLASSI ======================================================================

class AreasPage(WebResource):
    """
    Pagina web riguardante le aree.
    """
    TITLE = "Areas"

    def render_GET(self, request, conn):
        return self.create_page(request, conn)
    #- Fine Metodo -

    def create_page(self, request, conn):
        sorted_areas = sorted(database["areas"].values(), key=operator.attrgetter("name"))

        visibile_areas = []
        for area in sorted_areas:
            if AREA.DONT_LIST not in area.flags:
                visibile_areas.append(area)

        dont_list_areas = []
        for area in sorted_areas:
            if AREA.DONT_LIST in area.flags:
                dont_list_areas.append(area)

        html_parts = []
        html_parts.append('''<h3 align="center">AREE DI NAKILEN:</h3>''')
        html_parts += self.create_table_of_areas(request, conn, visibile_areas)
        if conn and conn.account and conn.account.trust >= TRUST.BUILDER:
            html_parts.append('''<h3 align="center">AREE CON FLAG DONT_LIST:</h3>''')
            html_parts += self.create_table_of_areas(request, conn, dont_list_areas)

        return "".join(html_parts)
    #- Fine Metodo -

    def create_table_of_areas(self, request, conn, areas):
        html_parts = []

        for area in areas:
            if " " in area.creators:
                creators = " &nbsp(Autori: %s)" % area.creators
            elif area.creators:
                creators = " &nbsp(Autore: %s)" % area.creators
            else:
                creators = ""
            html_parts.append('''<span style='color:%s; font-size:larger;'>%s</span>.%s''' % (area.color.hex_code, area.name, creators))
            if conn and conn.account and conn.account.trust >= TRUST.BUILDER:
                html_parts.append(''' {Code: %s}''' % area.code)
                html_parts.append(''' {MaxPlayers: %d}''' % area.max_players)
                if area.comment:
                    html_parts.append(''' %s''' % create_tooltip(conn, "[royalblue]Commento[close]:<br>%s" % area.comment, "{C}"))
            html_parts.append('''<div style="padding-left:1.9em;">%s</div><br>''' % area.descr.replace("\n", "<br>"))

        return html_parts
    #- Fine Metodo -
