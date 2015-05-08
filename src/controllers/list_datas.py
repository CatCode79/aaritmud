# -*- coding: utf-8 -*-

"""
Modulo per la pagina web che serve a visualizzare tutti i dati di una
particolare tabella di database.
"""


#= IMPORT ======================================================================

import datetime
import types

from src.command      import Command
from src.database     import database
from src.enums        import TRUST
from src.utility      import is_infix, pretty_date, sort_datas, to_capitalized_words, html_escape
from src.web_resource import WebResource, create_demi_line


#= CLASSI ======================================================================

class ListDatasPage(WebResource):
    TITLE = "List datas"

    ACCOUNT_MUST_EXIST_IN_GET  = True
    ACCOUNT_MUST_EXIST_IN_POST = True

    MINIMUM_TRUST_ON_GET  = TRUST.MASTER
    MINIMUM_TRUST_ON_POST = TRUST.MASTER

    def render_GET(self, request, conn):
        table_name, sorted_by, reverse = self.get_request_args(request)
        return self.create_page(request, conn, table_name, sorted_by, database[table_name], reverse)
    #- Fine Metodo -

    def render_POST(self, request, conn):
        table_name, sorted_by, reverse = self.get_request_args(request)
        attributes = self.get_attributes(table_name)
        # Per ogni attributo controlla cosa deve cercare nel database ed effettua
        # un filtering progressivo sui dati del database copiato
        searched_datas = {}
        at_least_one_search = False
        for attr in attributes:
            search_attr = "search_%s" % attr
            if search_attr not in request.args:
                continue
            search_for = request.args[search_attr][0]
            if not search_for:
                continue
            at_least_one_search = True
            for code, data in database[table_name].iteritems():
                data_attr = str(getattr(data, attr))
                if not data_attr:
                    continue
                if is_infix(search_for, data_attr):
                    searched_datas[code] = data
        if at_least_one_search:
            return self.create_page(request, conn, table_name, sorted_by, searched_datas, reverse)
        else:
            return self.create_page(request, conn, table_name, sorted_by, database[table_name], reverse)
    #- Fine Metodo -

    def create_page(self, request, conn, table_name, sorted_by, searched_datas, reverse):
        page = '''<h3>Lista del database %s:</h3>''' % table_name.capitalize()
        # Se ci sono degli errori di richiesta o di account ritorna il messaggio adatto
        if not searched_datas:
            page += '''Non è stato trovato nessun dato.<br>'''
            return page

        # Altrimenti crea la pagina con la lista dei dati nell'ordine voluto
        attributes = self.get_attributes(table_name)
        if not sorted_by in attributes:
            sorted_by = "primary_key"

        # Se serve esegue il filtering delle aree
        areas = []
        if "areas" in request.args:
            areas = request.args["areas"][0].split(",")
        areas_arg = ""
        if areas:
            areas_arg = "&areas=%s" % ",".join(areas)

        page += '''<form id="form_list_datas" name="form_list_datas" action="list_datas.html?table_name=%s&sorted_by=%s%s" method="post"><fieldset>''' % (
            table_name, sorted_by, areas_arg)
        page += '''<table border="1"><tr>'''

        header_cells = []
        for attr in attributes:
            if attr == "primary_key":
                header_cells.append('''<th nowrap='nowrap'><input type="submit" value="Filter ->" onclick="document.getElementById('form_list_datas').submit();" /><br>%s''' % create_demi_line(conn))
            else:
                checked = ""
                if "column" in request.args:
                    if attr in request.args["column"]:
                        checked = '''checked="checked" '''
                    else:
                        continue
                header_cells.append('''<th nowrap='nowrap'><input type="checkbox" name="column" value="%s" %s/><br>''' % (attr, checked))

            arrow = ""
            reverse_arg = ""
            if attr == sorted_by:
                if reverse:
                    arrow = ''' <img src="graphics/ascend.gif" width="10" height="5">'''
                else:
                    arrow = ''' <img src="graphics/descend.gif" width="10" height="5">'''
                    reverse_arg = "&reverse=true"

            header_cells.append('''<a href="list_datas.html?table_name=%s&sorted_by=%s%s%s">%s:</a>%s<br>%s''' % (
                table_name, attr, reverse_arg, areas_arg, to_capitalized_words(attr), arrow, create_demi_line(conn)))
            if attr == "primary_key":
                header_cells.append('''<input type="submit" value="Cerca -&gt;" onclick="document.getElementById('form_list_datas').submit();" /></th>''')
            else:
                value = ""
                if "search_" + attr in request.args:
                    value = request.args["search_" + attr][0]
                header_cells.append('''<input type="text" name="search_%s" maxlength="256" value="%s" /></th>''' % (attr, value))
        page += "".join(header_cells) + '''</tr>'''

        cells = []
        for code, data in sort_datas(searched_datas, sorted_by, reverse):
            if areas and code.split("_")[0] not in areas:
                continue
            cells.append('''<tr align="center">''')
            for attr in attributes:
                if attr == "primary_key":
                    cells.append('''<td><a href="edit_%s.html?code=%s">%s</a> (id: %d)</td>''' % (
                        table_name[0 : -1], code, code, id(data)))
                else:
                    if "column" in request.args and attr not in request.args["column"]:
                        continue

                    if attr == "password":
                        attr_value = "****"
                    else:
                        attr_value = getattr(data, attr)

                    if type(attr_value) == datetime.datetime or type(attr_value) == datetime.date:
                        cells.append('''<td>%s</td>''' % pretty_date(past=attr_value))
                    elif type(data) == Command and attr == "timer":
                        total_use_count = data.get_total_use_count()
                        if total_use_count == 0:
                            cells.append('''<td>0</td>''')
                        else:
                            cells.append('''<td>%s</td>''' % (attr_value / total_use_count))
                    elif hasattr(attr_value, "PRIMARY_KEY") and attr_value.PRIMARY_KEY:
                        cells.append('''<td>%s</td>''' % getattr(attr_value, attr_value.PRIMARY_KEY))
                    elif attr_value and str(attr_value):
                        cells.append('''<td>%s</td>''' % html_escape(str(attr_value)))
                    else:
                        cells.append('''<td>%r</td>''' % attr_value)
            cells.append('''</tr>''')
        page += "".join(cells) + '''</table></fieldset></form>'''

        return page
    #- Fine Metodo -

    def get_request_args(self, request):
        table_name = database.TABLES.keys()[0]
        if "table_name" in request.args:
            table_name = request.args["table_name"][0].lower()
            if table_name not in database.TABLES.keys():
                table_name = database.TABLES.keys()[0]

        sorted_by = "primary_key"
        if "sorted_by" in request.args:
            sorted_by = request.args["sorted_by"][0].lower()
            values = database[table_name].values()
            if values and sorted_by not in values[0].__dict__:
                sorted_by = "primary_key"

        reverse = False
        if "reverse" in request.args:
            reverse = bool(request.args["reverse"][0].capitalize())

        return table_name, sorted_by, reverse
    #- Fine Metodo -

    def get_attributes(self, table_name):
        """
        Prepara la lista degli attributi da visualizzare nella pagina
        nell'ordine voluto.
        """
        # Ricava gli attributi di un dato, come l'inizio della funzione fread
        module_name = database.TABLES[table_name][0]
        class_name  = database.TABLES[table_name][1]
        module = __import__(module_name, globals(), locals(), [""])
        data = getattr(module, class_name)()
        data_attributes = sorted(data.__dict__.keys())

        return ["primary_key"] + data_attributes
    #- Fine Metodo -
