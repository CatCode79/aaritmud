# -*- coding: utf-8 -*-

"""
Modulo per la pagina web che elenca i valori di CurrentGlobalQuantity
e MaxGlobalQuantity.
"""


#= IMPORT ======================================================================

import string

from src.color        import remove_colors
from src.config       import config
from src.enums        import TRUST
from src.database     import database
from src.log          import log
from src.web_resource import WebResource


#= CLASSI ======================================================================

class GlobalQuantityPage(WebResource):
    TITLE = "Global Quantity"

    ACCOUNT_MUST_EXIST_IN_GET  = False
    ACCOUNT_MUST_EXIST_IN_POST = False

    MINIMUM_TRUST_ON_GET  = TRUST.BUILDER
    MINIMUM_TRUST_ON_POST = TRUST.BUILDER

    PAGE_TEMPLATE = string.Template(open("src/views/global_quantity.view").read())

    def render_GET(self, request, conn):
        if "proto_code" in request.args:
            proto_code = request.args["proto_code"][0]
            if not proto_code:
                return "Codice passato non valido: %r" % proto_code
            quantities = self.create_instances_list(proto_code)
        else:
            quantities = self.create_quantities_list()

        mapping = {"quantities" : "".join(quantities)}
        return self.PAGE_TEMPLATE.safe_substitute(mapping)
    #- Fine Metodo -

    def create_quantities_list(self):
        quantities = []

        for table_name in ("proto_mobs", "proto_items"):
            quantities.append('''<table class="mud">''')
            for proto_code, prototype in database[table_name].iteritems():
                if prototype.max_global_quantity <= 0:
                    continue
                quantities.append('''<tr><td>''')
                quantities.append('''<a href="global_quantity.html?proto_code=%s" title="%s">%s</a>''' % (proto_code, remove_colors(prototype.name), proto_code))
                quantities.append('''</td><td>''')
                quantities.append('''<span style="color:%s">%d su %d</span>''' % (
                    "red" if prototype.current_global_quantity >= prototype.max_global_quantity else "", prototype.current_global_quantity, prototype.max_global_quantity))
                quantities.append('''</tr></td>''')
            quantities.append('''</table><br>''')

        return quantities
    #- Fine Metodo -

    def create_instances_list(self, proto_code):
        instances = []

        instances.append('''Istanze di entità con codice di prototipo %s e relativa destinatione:<br><br>''' % proto_code)
        instances.append('''<table class="mud">''')
        table_name = proto_code.split("_")[1] + "s"
        for code, instance in database[table_name].iteritems():
            if instance.prototype.code != proto_code:
                continue
            in_room = instance.get_in_room()
            instances.append('''<tr><td>''')
            instances.append('''%s''' % instance.name)
            instances.append('''</td><td>''')
            instances.append('''%d %d %d %s''' % (in_room.x, in_room.y, in_room.z, in_room.area.code))
            instances.append('''</tr></td>''')
        instances.append('''</table>''')

        if not instances:
            instances.append('''Se ti attendevi dei risultati probabilmente tra la visualizzazione della pagina precedente e l'arrivo su questa l'istanza precedentemente contata è stata estratta.''')

        return instances
    #- Fine Metodo -
