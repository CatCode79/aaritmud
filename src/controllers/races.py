# -*- coding: utf-8 -*-

"""
Modulo per la gestione della pagina sulle razze.
"""


#= IMPORT ======================================================================

from src.config       import config
from src.enums        import RACE
from src.web_resource import WebResource


#= CLASSI ======================================================================

# (TD) inserire delle immaginette ad inizio di ogni link, le stesse che
# visualizzerà il look alla TG
class RacesPage(WebResource):
    """
    Pagina web riguardante la biblioteca sulle razze.
    """
    TITLE = "Races"

    def render_GET(self, request, conn):
        return self.create_page(request, conn)
    #- Fine Metodo -

    def create_page(self, request, conn):
        output = []

        output.append('''<h3 align="center">LISTA DELLE RAZZE GIOCABILI DI %s:</H3>''' % (config.game_name.upper()))
        output.append('''<p><table>''')
        for race in RACE.elements:
            if not race.playable:
                continue
            output.append('''<tr><td><a href="race_%s.html">%s:</a></td><td>%s</td></tr>''' % (
                race.code[len("RACE.") : ].lower(), race, race.description))
        output.append('''</table></p>''')

        #output.append('''<h3 align="center">"LISTA DELLE RAZZE DEI MOB DI %s":</H3>''' % (config.game_name.upper()))
        #output.append('''<p><table>''')
        #output.append('''<tr><td><a href="race_%s.html">%s</a></td><td>%s</td></tr>''' % (
        #    RACE.MIMIC.code[len("RACE.") : ].lower(), RACE.MIMIC, RACE.MIMIC.description))
        #output.append('''<p><table>''')
        #output.append('''<tr><th>Razza:</th><th>Descrizione:</th></tr>''')
        #for race in RACE.elements:
        #    if race.playable:
        #        continue
        #    output.append('''<tr><td><a href="race_%s.html">%s</a></td><td>%s</td></tr>''' % (
        #        race.code[len("RACE.") : ].lower(), race, race.description))
        #output.append('''</table></p>''')

        return "".join(output)
    #- Fine Metodo -
