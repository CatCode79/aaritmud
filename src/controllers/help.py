# -*- coding: utf-8 -*-

"""
Modulo per la visualizzazione di tutti i topic di help.
"""


#= IMPORT ======================================================================

import string

from src.color        import remove_colors
from src.config       import config
from src.enums        import HELP, TRUST
from src.web_resource import WebResource


#= CLASSI ======================================================================

class HelpPage(WebResource):
    """
    Pagina web utilizzata per visualizzare i topic relativi agli help.
    """
    TITLE = "Help"

    PAGE_TEMPLATE = string.Template(open("src/views/help.view").read())

    def render_GET(self, request, conn):
        max_help_types = len(HELP.elements)
        for help_element in HELP.elements:
            if (conn.player and help_element.trust > conn.player.trust
            or  conn.account and help_element.trust > conn.account.trust
            or  not conn.account and not conn.player and help_element.trust > TRUST.PLAYER):
                max_help_types -= 1
        half_help_types = max_help_types / 2 + max_help_types % 2

        help_types = []
        help_types.append('''<table class="mud" align="center" width="100%"><tr>''')
        help_types.append('''<td valign="top"><ul>''')
        help_types += self._render_help_types_list(0, half_help_types)
        help_types.append('''</ul></td>''')
        help_types.append('''<td valign="top"><ul>''')
        help_types += self._render_help_types_list(half_help_types, max_help_types)
        help_types.append('''</ul></td>''')
        help_types.append('''</tr></table>''')

        mapping = {"game_name"          : config.game_name,
                   "game_name_nocolor"  : remove_colors(config.game_name),
                   "help_types"        : "".join(help_types)}
        return self.PAGE_TEMPLATE.safe_substitute(mapping)
    #- Fine Metodo -

    def _render_help_types_list(self, starts_at, ends_at):
        help_types = []

        counter = starts_at
        while counter < ends_at:
            
            help_types.append('''<li> <a href="show_helps?helptype=%s">%s</a>''' % (
                HELP.elements[counter].code, HELP.elements[counter]))
            counter += 1

        return help_types
    #- Fine Metodo -

    def render_POST(self, request, conn):
        # Ricava gli argomenti del form dalla richiesta
        pass

        # Controlla la validità degli argomenti inseriti nel form
        pass

        return self.create_page(request, conn)
    #- Fine Metodo -
