# -*- coding: utf-8 -*-

"""
Modulo per la pagina relativa alla visualizzazione di tutti gli account e
i giocatori con trust differente da quella di giocatore.
"""


#= IMPORT ======================================================================

import operator
import string

from src.color        import remove_colors
from src.database     import database
from src.enums        import TRUST
from src.log          import log
from src.web_resource import WebResource


#= CLASSI ======================================================================

class TrustsPage(WebResource):
    TITLE = "Trusts e Permissions"
    ACCOUNT_MUST_EXIST_IN_GET  = True
    ACCOUNT_MUST_EXIST_IN_POST = True

    MINIMUM_TRUST_ON_GET  = TRUST.MASTER
    MINIMUM_TRUST_ON_POST = TRUST.MASTER

    PAGE_TEMPLATE = string.Template(open("src/views/trusts.view").read())

    def render_GET(self, request, conn):
        mapping = {"trusted_accounts" : self.get_account_trusts(),
                   "trusted_players"  : self.get_player_trusts(),
                   "permissions"      : self.get_permissions()}
        return self.PAGE_TEMPLATE.safe_substitute(mapping)

    def get_account_trusts(self):
        rows = []

        for account in sorted(database["accounts"].values()):
            if account.trust != TRUST.PLAYER:
                rows.append('''<tr><td>%s</td><td>%s</td></tr>''' % (account.name, account.trust))

        if rows:
            return "".join(rows)
        else:
            return '''<tr><td colspan="3">Nessuno</td></tr>'''
    #- Fine Metodo -

    def get_player_trusts(self):
        rows = []

        for player in sorted(database["players"].values(), key=lambda player: remove_colors(player.name)):
            if player.trust != TRUST.PLAYER:
                rows.append('''<tr><td>%s</td><td>%s</td><td>%s</td></tr>''' % (player.name, player.trust, player.account.name))

        if rows:
            return "".join(rows)
        else:
            return '''<tr><td colspan="3">Nessuno</td></tr>'''
    #- Fine Metodo -

    def get_permissions(self):
        rows = []

        for player in sorted(database["players"].values(), key=lambda player: remove_colors(player.name)):
            if player.permissions:
                rows.append('''<tr><td>%s</td><td>%s</td><td>%s</td></tr>''' % (player.name, player.permissions, player.account.name))

        if rows:
            return "".join(rows)
        else:
            return '''<tr><td colspan="3">Nessuno</td></tr>'''
    #- Fine Metodo -
