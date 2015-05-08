# -*- coding: utf-8 -*-

#= IMPORT ======================================================================

from src.command      import get_command_syntax
from src.database     import database
from src.log          import log
from src.utility      import is_same, is_prefix, one_argument, nifty_value_search
from src.web_resource import create_tooltip


#= FUNZIONI ====================================================================

def command_coords(entity, argument=""):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    results = []

    if argument:
        area = nifty_value_search(database["areas"], argument)
        if not area:
            entity.send_output("Codice d'area simile a [green]%s[close] inesistente." % argument)
            return False
    else:
        results.append(get_command_syntax(entity, "command_coords") + "\n")
        area = entity.area
        if not area:
            results.append("\nNon ti trovi in un'area valida.")
            entity.send_output("".join(results))
            return False

    results.append('''<table class="mud" rules="rows" frame="below">''')
    results.append('''<tr>''')
    results.append('''<th class="nowrap" align="left">X Y Z</th>''')
    results.append('''<th align="left">Code</th>''')
    results.append('''<th align="left">Name</th>''')
    results.append('''<th align="left">Short</th>''')
    results.append('''</tr>''')
    for coord in sorted(area.rooms):
        room = area.rooms[coord]
        short_tooltip = ""
        if room.short_night:
            short_tooltip = create_tooltip(entity.get_conn(), "ShortNight: %s" % room.short_night, room.short)
        else:
            short_tooltip = room.short
        javascript_code = '''javascript:parent.sendInput('rgoto %s');''' % room.get_destination()
        results.append('''<tr>''')
        results.append('''<td class="nowrap">%s</td><td><a href="%s">%s</a></td><td>%s</td><td>%s</td>''' % (
            coord, javascript_code, room.code, room.name, short_tooltip))
        results.append('''</tr>''')
    results.append('''</table>''')

    entity.send_output("".join(results), break_line=False)
    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""
    syntax += "coords\n"
    syntax += "coords <codice area>\n"

    return syntax
#- Fine Funzione -
