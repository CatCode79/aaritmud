# -*- coding: utf-8 -*-

"""
Modulo per la gestione della pagina web che raccoglie tutti i link alle altre
pagine che hanno come tema la visualizzazione delle statistiche relative al gioco.
"""


#= IMPORT ======================================================================

import string

from src.config       import config
from src.enums        import TRUST
from src.web_resource import WebResource

if config.reload_web_pages:
    reload(__import__("src.controllers.stats_connection", globals(), locals(), [""]))
    reload(__import__("src.controllers.stats_cpu",        globals(), locals(), [""]))
    reload(__import__("src.controllers.stats_browser",    globals(), locals(), [""]))
    reload(__import__("src.controllers.stats_resolution", globals(), locals(), [""]))
    reload(__import__("src.controllers.stats_so",         globals(), locals(), [""]))
from src.controllers.stats_connection import StatsConnectionPage
from src.controllers.stats_cpu        import StatsCpuPage
from src.controllers.stats_browser    import StatsBrowserPage
from src.controllers.stats_resolution import StatsResolutionPage
from src.controllers.stats_so         import StatsSoPage


#= CLASSI ======================================================================

class StatsPage(WebResource):
    """
    Pagina web per tutti i link relativi alle statistiche.
    """
    TITLE = "Statistiche"

    ACCOUNT_MUST_EXIST_IN_GET  = True
    ACCOUNT_MUST_EXIST_IN_POST = True

    MINIMUM_TRUST_ON_GET  = TRUST.MASTER
    MINIMUM_TRUST_ON_POST = TRUST.MASTER

    PAGE_TEMPLATE = string.Template(open("src/views/stats.view").read())

    def render_GET(self, request, conn):
        hide_stats_connection = ""
        if not conn or not conn.account or conn.account.trust < StatsConnectionPage.MINIMUM_TRUST_ON_GET:
            hide_stats_connection = " visibility:hidden;"

        hide_stats_cpu = ""
        if not conn or not conn.account or conn.account.trust < StatsCpuPage.MINIMUM_TRUST_ON_GET:
            hide_stats_cpu = " visibility:hidden;"

        hide_stats_browser = ""
        if not conn or not conn.account or conn.account.trust < StatsBrowserPage.MINIMUM_TRUST_ON_GET:
            hide_stats_browser = " visibility:hidden;"

        hide_stats_resolution = ""
        if not conn or not conn.account or conn.account.trust < StatsResolutionPage.MINIMUM_TRUST_ON_GET:
            hide_stats_resolution = " visibility:hidden;"

        hide_stats_so = ""
        if not conn or not conn.account or conn.account.trust < StatsSoPage.MINIMUM_TRUST_ON_GET:
            hide_stats_so = " visibility:hidden;"

        show_empty_message = ''' class="invisible"'''
        if hide_stats_connection and hide_stats_cpu and hide_stats_browser and hide_stats_resolution and hide_stats_so:
            show_empty_message = ""

        mapping = {"game_name"             : config.game_name,
                   "game_name_upper"       : config.game_name.upper(),
                   "show_empty_message"    : show_empty_message,
                   "trust"                 : str(conn.account.trust),
                   "hide_stats_connection" : hide_stats_connection,
                   "hide_stats_cpu"        : hide_stats_cpu,
                   "hide_stats_browser"    : hide_stats_browser,
                   "hide_stats_resolution" : hide_stats_resolution,
                   "hide_stats_so"         : hide_stats_so}
        return self.PAGE_TEMPLATE.safe_substitute(mapping)
    #- Fine Metodo -
