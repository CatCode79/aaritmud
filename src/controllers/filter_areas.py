# -*- coding: utf-8 -*-

"""
Pagina web che serve a scegliere di quali aree visualizzare i dati.
"""


#= IMPORT ======================================================================

import string

from src.database     import database
from src.enums        import TRUST
from src.web_resource import WebResource


#= CLASSI ======================================================================

class FilterAreasPage(WebResource):
    TITLE = "Filter Areas"

    ACCOUNT_MUST_EXIST_IN_GET  = True
    ACCOUNT_MUST_EXIST_IN_POST = True

    MINIMUM_TRUST_ON_GET  = TRUST.MASTER
    MINIMUM_TRUST_ON_POST = TRUST.MASTER

    PAGE_TEMPLATE = string.Template(open("src/views/filter_areas.view").read())

    def render_GET(self, request, conn):
        area_checkboxs = []
        for area_code in sorted(database["areas"].keys()):
            area_checkboxs.append('''<input type="checkbox" name="area" value="%s" /> %s''' % (area_code, area_code))

        mapping = {"area_checkboxs" : "<br>".join(area_checkboxs)}
        return self.PAGE_TEMPLATE.safe_substitute(mapping)
    # - Fine Metodo -
