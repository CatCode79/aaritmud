# -*- coding: utf-8 -*-

"""
Pagina che visualizza tutto il database di Aarit in forma di albero.
"""


#= IMPORT ======================================================================

import pprint
import string

from src.config       import config
from src.database     import database, SUBFOLDER
from src.enums        import TRUST
from src.web_resource import WebResource


#= CLASSI ======================================================================
prova = """\
[
	{
		"text": "1. Pre Lunch (120 min)",
		"expanded": false,
		"classes": "important",
		"children":
		[
			{
				"text": "1.1 The State of the Powerdome (30 min)"
			},
		 	{
				"text": "1.2 The Future of jQuery (30 min)"
			},
		 	{
				"text": "1.2 jQuery UI - A step to richnessy (60 min)"
			}
		]
	},
	{
		"text": "2. Lunch  (60 min)"
	},
	{
		"text": "3. After Lunch  (120+ min)",
		"children":
		[
			{
				"text": "3.1 jQuery Calendar Success Story (20 min)"
			},
		 	{
				"text": "3.2 jQuery and Ruby Web Frameworks (20 min)"
			},
		 	{
				"text": "3.3 Hey, I Can Do That! (20 min)"
			},
		 	{
				"text": "3.4 Taconite and Form (20 min)"
			},
		 	{
				"text": "3.5 Server-side JavaScript with jQuery and AOLserver (20 min)"
			},
		 	{
				"text": "3.6 The Onion: How to add features without adding features (20 min)",
				"id": "36",
				"hasChildren": true
			},
		 	{
				"text": "3.7 Visualizations with JavaScript and Canvas (20 min)"
			},
		 	{
				"text": "3.8 ActiveDOM (20 min)"
			},
		 	{
				"text": "3.8 Growing jQuery (20 min)"
			}
		]
	}
]
"""

class DatatreePage(WebResource):
    TITLE = "DataTree"

    ACCOUNT_MUST_EXIST_IN_GET  = True
    ACCOUNT_MUST_EXIST_IN_POST = True

    MINIMUM_TRUST_ON_GET  = TRUST.BUILDER
    MINIMUM_TRUST_ON_POST = TRUST.BUILDER

    ADDITIONAL_TEMPLATE = string.Template(open("src/views/datatree_additional_header.view").read())
    PAGE_TEMPLATE       = string.Template(open("src/views/datatree.view").read())

    NEW_PAGE = True

    def create_additional_header(self, request, conn):
        mapping = {}
        return self.ADDITIONAL_TEMPLATE.safe_substitute(mapping)
    #- Fine Metodo -

    def render_GET(self, request, conn):
        folders = []

        for table in sorted(database.keys()):
            has_children_class = ''' class="hasChildren"'''
            if database.TABLES[table][SUBFOLDER]:
                has_children_class = ""
            folders.append('''<li id="%s"%s><span class="folder">%s</span>''' % (
                table, has_children_class, table.capitalize()))

            if database.TABLES[table][SUBFOLDER]:
                folders.append('''<ul>''')
                for subtable in database.get_subfolder_names(table):
                    folders.append('''<li id="%s.%s" class="hasChildren"><span class="folder">%s</span>''' % (
                        table, subtable, subtable.capitalize()))
                    if database.iter_subfolder_related_datas(table, subtable):
                        folders.append('''<ul>''')
                        folders.append('''<li><span class="placeholder">&nbsp;</span></li>''')
                        folders.append('''</ul>''')
                folders.append('''</ul>''')
            else:
                if database[table]:
                    folders.append('''<ul>''')
                    folders.append('''<li><span class="placeholder">&nbsp;</span></li>''')
                    folders.append('''</ul>''')

        mapping = {"folders" : "".join(folders)}
        return self.PAGE_TEMPLATE.safe_substitute(mapping)
    #- Fine Metodo -

        #for subfolder_name in subfolder_names:
        #    folders.append('''<li><span class="folder">%s</span>''' % str(subfolder_name).capitalize())
        #    folders.append('''<ul>''')
        #    for data_code, data_value in sorted(database[table].items()):
        #        if import_value == "code":
        #            subfolder_data = getattr(data_value, subfolder_value)
        #            if getattr(subfolder_data, subfolder_data.PRIMARY_KEY) == subfolder_name:
        #                folders.append('''<li><span class="file">%s</span>''' % data_code.capitalize())
        #        elif import_value == "primary-key-piece":
        #            if getattr(data_value, data_value.PRIMARY_KEY).split("_")[1] == subfolder_name:
        #                folders.append('''<li><span class="file">%s</span>''' % data_code.capitalize())
        #        else:
        #            subfolder_data = getattr(data_value, subfolder_value)
        #            #print subfolder_data
        #            if subfolder_data.get_mini_code() == subfolder_name:
        #                folders.append('''<li><span class="file">%s</span>''' % data_code.capitalize())
        #    folders.append('''</ul>''')

    def render_POST(self, request, conn):
        if "root" not in request.args:
            return "[red]Impossibile ricavare i dati per l'alberatura se manca l'argomento di post source[close]"

        results = []
        root = request.args["root"][0]
        original_pieces = pieces = root.split(".")
        table_name = pieces[0]
        subfolder = database.TABLES[pieces[0]][SUBFOLDER]
        if subfolder == "type":
            # (TD) da filtrare
            datas = sorted(database[table_name].items())
            pieces = pieces[1 : ]
        elif len(pieces) > 1 and pieces[1] in database[subfolder + "s"]:
            datas = database.get_subfolder_related_datas(table_name, pieces[1])
            pieces = pieces[2 : ]
        else:
            datas = sorted(database[table_name].items())
            pieces = pieces[1 : ]

        for data_code, data_value in datas:
            data_infos = {}
            data_infos["id"] = "%s.%s" % (".".join(original_pieces), data_code)
            data_infos["classes"] = "file"
            #data_infos["expanded"] = False
            #data_infos["hasChildren"] = True
            #data_infos["children"] = [{"text" : "xxx"}]
            data_infos["text"] = data_code
            results.append(data_infos)

        # (BB) non va bene, ci vuole per forza il json, altriment False != false, versione 2.6
        json = pprint.pformat(results, indent=0)
        if "{'":
            json = json.replace("{'", '{"')
        if "'}":
            json = json.replace("'}", '"}')
        if "':":
            json = json.replace("':", '":')
        if ": '":
            json = json.replace(": '", ': "')
        if "',":
            json = json.replace("',", '",')
        if ", '":
            json = json.replace(", '", ', "')
        if "\n'":
            json = json.replace("\n'", '\n"')
        if " '":
            json = json.replace(" '", ' "')
        if "['":
            json = json.replace("['", '["')
        if "']":
            json = json.replace("']", '"]')
        #json = json.replace("", '')

        return json
    #- Fine Metodo -
