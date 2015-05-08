# -*- coding: utf-8 -*-

"""
Controller della pagina web per la gestione delle opzioni di admin.
"""


#= IMPORT ======================================================================

import string

from src.element      import Flags
from src.enums        import LOG, TRUST
from src.web_resource import (WebResource, create_form_row, create_form,
                              create_checklist_of_flags, set_checked_flags)


#= CLASSI ======================================================================

class AdminAccountPage(WebResource):
    TITLE = "Admin Account"

    ACCOUNT_MUST_EXIST_IN_GET  = True
    ACCOUNT_MUST_EXIST_IN_POST = True

    MINIMUM_TRUST_ON_GET          = TRUST.MASTER
    MINIMUM_TRUST_ON_POST         = TRUST.MASTER

    def render_GET(self, request, conn):
        return self.create_page(request, conn)
    #- Fine Metodo -

    def render_POST(self, request, conn):
        if "show_logs" in request.args:
            set_checked_flags(request, "show_logs", conn.account.show_logs)
            return self.create_page(request, conn)
        else:
            # Capita quando vengono disabilitate tutte le checkbox
            conn.account.show_logs = Flags(LOG.NONE)
            return self.create_page(request, conn)
    #- Fine Metodo -

    def create_page(self, request, conn):
        # Prepara il form delle opzioni
        form_show_logs = []
        row = create_form_row(form_show_logs)
        row.label = "Log Visualizzati"
        row.field = self.create_checklist_of_logs(conn)
        row = create_form_row(form_show_logs)
        row.label = '''<input type="submit" value="Salva" onclick="document.getElementById('form_show_logs').submit();" />'''
        if request.method == "POST" and "show_logs" in request.args:
            row.label += ''' <span style="color:green">Opzioni salvate.</span>'''

        page  = "<br>"
        page += create_form(form_show_logs, "form_show_logs", "admin_account.html", "Scegli i log da visualizzare", show_label=False)
        page += "<br>"

        return page
    #- Fine Metodo -

    def create_checklist_of_logs(self, conn):
        """
        Concettualmente questa è un override della funzione create_checklist_of_flags
        in web.py.
        """
        page = '''<table>'''
        for log_element in LOG.elements:
            if not log_element.is_checkable:
                continue
            if conn.account.trust < log_element.trust:
                continue
            checked = ""
            if log_element in conn.account.show_logs:
                checked = ''' checked="checked"'''
            page += '''  <tr><td nowrap><input type="checkbox" name="%s" value="%s"%s /> %s</td><td>%s</td></tr>''' % (
                "show_logs", log_element.code, checked, log_element, log_element.description)
        page += '''</table>'''

        return page
    #- Fine Metodo -
