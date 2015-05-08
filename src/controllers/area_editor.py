# -*- coding: utf-8 -*-

"""
Modulo per la modifica di un'area.
Preferisco non dare possibilità di creare una nuova area da zero per dare
maggiore peso al miglioramento di quelle già esistenti.
"""


#= IMPORT ======================================================================

import math
import string

from src.area         import Area, get_area_from_argument
from src.config       import config
from src.database     import database
from src.enums        import SECTOR, TRUST
from src.log          import log
from src.utility      import is_number, to_capitalized_words
from src.web_resource import WebResource, create_checklist_of_flags, create_listdrop_of_elements


#= CLASSI ======================================================================

class AreaEditorPage(WebResource):
    TITLE = "Area Builder"

    ACCOUNT_MUST_EXIST_IN_GET  = True
    ACCOUNT_MUST_EXIST_IN_POST = True

    MINIMUM_TRUST_ON_GET  = TRUST.BUILDER
    MINIMUM_TRUST_ON_POST = TRUST.BUILDER

    ADDITIONAL_TEMPLATE = string.Template(open("src/views/area_editor_additional_header.view").read())
    PAGE_TEMPLATE       = string.Template(open("src/views/area_editor.view").read())

    def create_additional_header(self, request, conn):
        mapping = {}
        return self.ADDITIONAL_TEMPLATE.safe_substitute(mapping)
    #- Fine Metodo -

    def create_menu(self, request, conn):
        return ""
    #- Fine Metodo -

    def create_square(self, request, conn):
        return ""
    #- Fine Metodo -

    def render_GET(self, request, conn):
        error_message = ""
        area_code = ""
        coord_z = 0

        if "area_code" in request.args:
            area_code = request.args["area_code"][0]
        if not area_code:
            area_code = sorted(database["areas"].keys())[0]

        area = get_area_from_argument(area_code)
        if area:
            if "coord_z" in request.args:
                coord_z = request.args["coord_z"][0]
                if not coord_z:
                    error_message = "La coordinata Z non è un valore valido: %r" % coord_z
                    coord_z = 0
                if not is_number(coord_z):
                    error_message = "La coordinata Z non è un valore numerico valido: %s" % coord_z
                    coord_z = 0
                coord_z = int(coord_z)
        else:
            error_message = "Non esiste nessun'area con il codice %s" % area_code

        mapping = {"area_select_options" : self.create_area_select_options(area_code),
                   "error_message"       : error_message,
                   "area_code"           : area.code if area else "",
                   "min_coord_z"         : area.get_min_coord("z") if area else 0,
                   "coord_z"             : coord_z,
                   "max_coord_z"         : area.get_max_coord("z") if area else 0,
                   "proto_rooms"         : self.create_proto_datas("proto_rooms", area) if area else "",
                   "proto_items"         : self.create_proto_datas("proto_items", area) if area else "",
                   "proto_mobs"          : self.create_proto_datas("proto_mobs", area) if area else "",
                   "cells"               : self.create_cells(area, coord_z) if area else "",
                   "legend_icons"        : self.create_legend_icons(),
                   "area_labels"         : self.create_area_labels(area) if area else ""}
        return self.PAGE_TEMPLATE.safe_substitute(mapping)
    # - Fine Metodo -

    def create_area_select_options(self, selected_area_code):
        options = []

        for area_code in sorted(database["areas"]):
            selected = ""
            if area_code == selected_area_code:
                selected = '''selected="selected"'''
            options.append('''<option value="%s"%s>%s</option>''' % (area_code, selected, area_code))

        return "".join(options)
    # - Fine Metodo -

    def create_proto_datas(self, table_name, area):
        protos = []

        max = 0
        for code in sorted(database[table_name].keys()):
            if code.startswith(area.code + "_"):
                max += 1

        protos.append('''<table>''')
        n = 0
        for code in sorted(database[table_name].keys()):
            if code.startswith(area.code + "_"):
                if n == 0:
                    protos.append('''<tr>''')
                elif n % 3 == 0 and n != max:
                    protos.append('''</tr><tr>''')
                protos.append('''<td style="padding-left:1em;padding-right:1em"><a href="edit_proto_room.html?code=%s">%s</a></td>''' % (code, code))
                n += 1
        protos.append('''</tr>''')
        protos.append('''</table>''')

        return "".join(protos)
    # - Fine Metodo -

    def create_cells(self, area, z):
        cells = []

        min_y = area.get_min_coord("y")
        max_y = area.get_max_coord("y")
        min_x = area.get_min_coord("x")
        max_x = area.get_max_coord("x")

        for y in reversed(xrange(min_y-2, max_y+3)):
            cells += '''<tr>'''
            for x in xrange(min_x-2, max_x+3):
                room_reset = area.get_room_reset(x, y, z)
                upper_style = ""
                upper_room_reset = area.get_room_reset(x, y, z+1)
                if upper_room_reset:
                    upper_style = '''border-top:1px dotted grey; border-left:1px dotted grey;'''
                lower_style = ""
                lower_room_reset = area.get_room_reset(x, y, z-1)
                if lower_room_reset:
                    lower_style = '''border-bottom:1px dotted darkslategray; border-right:1px dotted darkslategray;'''
                if room_reset:
                    cells += '''<td id="%d %d %d" style="%s%s" onclick="location.href='room_resets_edit.html?x=%d&y=%d&z=%d&area_code=%s'" onmouseover="this.style.backgroundColor='gold'" align="center" onmouseout="this.style.backgroundColor='black'"><img src="sector/%s.png" width="32" height="32" title="%d %d %d: %s" /></td>''' % (
                        x, y, z, upper_style, lower_style, x, y, z, area.code, room_reset.proto_room.sector.get_mini_code(), x, y, z, room_reset.proto_room.code)
                else:
                    if y == min_y - 2 or y == max_y + 2 or x == min_x - 2 or x == max_x + 2:
                        if y == min_y - 2 and (x == min_x - 2 or x == max_x + 2):
                            content = ""
                        elif y == max_y + 2 and (x == min_x - 2 or x == max_x + 2):
                            content = ""
                        elif y == min_y - 2 or y == max_y + 2:
                            content = str(x)
                        else:
                            content = str(y)
                        cells += '''<td id="%d %d %d" style="%s%s"><div style="height:32px; width:32px;">%s</div></td>''' % (
                            x, y, z, upper_style, lower_style, content)
                    else:
                        cells += '''<td id="%d %d %d" style="%s%s" align="center" onclick="location.href='room_resets_edit.html?x=%d&y=%d&z=%d&area_code=%s'" onmouseover="this.style.backgroundColor='gold'" align="center" onmouseout="this.style.backgroundColor='black'"><img src="sector/__blank__.png" width="32" height="32" title="%d %d %d" /></td>''' % (
                            x, y, z, upper_style, lower_style, x, y, z, area.code, x, y, z)
            cells += '''</tr>'''

        return "".join(cells)
    # - Fine Metodo -

    def create_legend_icons(self):
        legend_icons = []

        legend_icons += '''<table widht="100%%">'''
        line_numbers = len(SECTOR.elements) / 4 + (1 if len(SECTOR.elements) % 4 != 0 else 0)
        for line_number in xrange(line_numbers):
            legend_icons += '''<tr>'''
            legend_icons += self.create_icon(line_number, 0)
            legend_icons += self.create_icon(line_number, 1)
            legend_icons += self.create_icon(line_number, 2)
            legend_icons += self.create_icon(line_number, 3)
            legend_icons += '''</tr>'''
        legend_icons += '''</table>'''

        return "".join(legend_icons)
    # - Fine Metodo -

    def create_icon(self, line_number, shift):
        try:
            sector_element = SECTOR.elements[4*line_number + shift]
            return '''<td><img src="sector/%s.png" width="32" height="32" /></td><td width="25%%">%s</td>''' % (sector_element.get_mini_code(), sector_element)
        except IndexError:
            return '''<td> </td><td> </td>'''
    # - Fine Metodo -

    def create_area_labels(self, area):
        area_labels = []

        area_labels += '''<table>'''
        for attr_name in sorted(area.__dict__.keys()):
            if attr_name in area.VOLATILES or attr_name in ["room_resets"]:
                continue
            area_labels += '''<tr>'''
            area_labels += '''<td valign="top"><span style="color:white;">%s</span>: </td>''' % to_capitalized_words(attr_name)
            attr = getattr(area, attr_name)
            if isinstance(attr, basestring):
                widget = '''<input type="text" id="%s" value="%s" />''' % (attr_name, attr)
            else:
                widget = str(attr)
            area_labels += '''<td>%s</td>''' % widget
            area_labels += '''</tr>'''
        area_labels += '''</table>'''

        return "".join(area_labels)
    # - Fine Metodo -

# (TD) questo da aggiungere nel POST una volta che si farà:
#            new_area.creators = conn.account.code
#            database["areas"][new_code] = new_area
