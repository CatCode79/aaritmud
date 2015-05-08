# -*- coding: utf-8 -*-

"""
Modulo per la pagina web relativa alla visualizzazione della lista dei database
e del numero dei suoi dati.
"""


#= IMPORT ======================================================================

import string

from src.asizeof      import asizeof
from src.database     import database
from src.enums        import TRUST
from src.utility      import commafy
from src.web_resource import WebResource


#= CLASSI ======================================================================

class DatabasePage(WebResource):
    """
    Visualizza il menù di accesso per la visualizzazione dei dati o per il loro
    building.
    """
    TITLE = "Database"

    ACCOUNT_MUST_EXIST_IN_GET  = True
    ACCOUNT_MUST_EXIST_IN_POST = True

    MINIMUM_TRUST_ON_GET  = TRUST.MASTER
    MINIMUM_TRUST_ON_POST = TRUST.MASTER

    PAGE_TEMPLATE = string.Template(open("src/views/database.view").read())

    def render_GET(self, request, conn):
        database_rows = []

        compute = False
        if "compute" in request.args and request.args["compute"][0] == "True":
            compute = True
            database_rows.append('''I valori sono approsimati e pertanto non esatti, ma dovrebbero comunque dare una buona idea.<br><br>''')

        total_of_datas = 0
        total_dimension = 0
        first_compute_button = False
        for table_name in sorted(database.TABLES.keys()):
            if table_name in ("proto_rooms", "proto_items", "proto_mobs", "rooms", "items", "mobs"):
                url = "filter_areas.html"
            else:
                url = "list_datas.html"
            database_rows.append('''<tr align="center">''')
            database_rows.append('''<td><a href="%s?table_name=%s&sorted_by=primary_key">%s</a></td>''' % (
                url, table_name, table_name))
            number_of_datas = len(database[table_name])
            total_of_datas += number_of_datas
            database_rows.append('''<td>%d</td>''' % number_of_datas)
            if compute:
                table_dimension = asizeof(table_name, database[table_name])
                total_dimension += table_dimension
                database_rows.append('''<td>%s</td>''' % commafy(table_dimension))
            else:
                if not first_compute_button:
                    database_rows.append('''<td database_rowspan="%d"><input type="submit" value="Calcola" onclick="compute();" /></td>''' % len(database))
                    first_compute_button = True
                else:
                    database_rows.append('''<td> </td>''')
            database_rows.append('''<td><a href="edit_%s.html" target="_blank">Crea dato</a></td>''' % table_name[0 : -1])
            database_rows.append('''</tr>''')

        area_rows = []
        if compute:
            total_areas_rooms_qty = 0
            total_areas_items_qty = 0
            total_areas_mobs_qty = 0
            total_areas_players_qty = 0
            total_areas_rooms_dimension = 0
            total_areas_items_dimension = 0
            total_areas_mobs_dimension = 0
            total_areas_players_dimension = 0
            for area in database["areas"].itervalues():
                area_rooms_qty = len(area.rooms)
                area_items_qty = len(area.items)
                area_mobs_qty = len(area.mobs)
                area_players_qty = len(area.players)
                total_areas_rooms_qty += area_rooms_qty
                total_areas_items_qty += area_items_qty
                total_areas_mobs_qty += area_mobs_qty
                total_areas_players_qty += area_players_qty

                area_rooms_dimension = asizeof("rooms", area.rooms)
                area_items_dimension = asizeof("items", area.items)
                area_mobs_dimension = asizeof("mobs", area.mobs)
                area_players_dimension = asizeof("players", area.players)
                total_areas_rooms_dimension += area_rooms_dimension
                total_areas_items_dimension += area_items_dimension
                total_areas_mobs_dimension += area_mobs_dimension
                total_areas_players_dimension += area_players_dimension

                area_rows.append('''<tr><td rowspan="4">%s</td><td>Rooms</td><td>%d</td><td>%s</td></tr>''' % (area.code, area_rooms_qty, commafy(area_rooms_dimension)))
                area_rows.append('''<tr><td>Items</td><td>%d</td><td>%s</td></tr>''' % (area_items_qty, commafy(area_items_dimension)))
                area_rows.append('''<tr><td>Mobs</td><td>%d</td><td>%s</td></tr>''' % (area_mobs_qty, commafy(area_mobs_dimension)))
                area_rows.append('''<tr><td>Players</td><td>%d</td><td>%s</td></tr>''' % (area_players_qty, commafy(area_players_dimension)))

            area_rows.append('''<tr><td rowspan="4">Totale</td><td>Rooms</td><td>%d</td><td>%s</td></tr>''' % (total_areas_rooms_qty, commafy(total_areas_rooms_dimension)))
            area_rows.append('''<tr><td>Items</td><td>%d</td><td>%s</td></tr>''' % (total_areas_items_qty, commafy(total_areas_items_dimension)))
            area_rows.append('''<tr><td>Mobs</td><td>%d</td><td>%s</td></tr>''' % (total_areas_mobs_qty, commafy(total_areas_mobs_dimension)))
            area_rows.append('''<tr><td>Players</td><td>%d</td><td>%s</td></tr>''' % (total_areas_players_qty, commafy(total_areas_players_dimension)))

        mapping = {"database_rows"    : "".join(database_rows),
                   "number_of_tables" : len(database),
                   "total_of_datas"   : commafy(total_of_datas),
                   "total_dimension"  : commafy(total_dimension),
                   "areas_rows"       : "".join(area_rows)}
        return self.PAGE_TEMPLATE.safe_substitute(mapping)
    #- Fine Metodo -
