# -*- coding: utf-8 -*-


#= IMPORT ======================================================================

from src.command  import get_command_syntax
from src.database import database
from src.log      import log
from src.utility  import is_same, is_prefix, one_argument, nifty_value_search


#= FUNZIONI ====================================================================

def command_links(entity, argument="", behavioured=False):
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
        areas = [area, ]
    else:
        results.append(get_command_syntax(entity, "command_links") + "\n")
        areas = sorted(database["areas"].values())

    results.append('''<table class="mud" rules="rows" frame="below" width="100%">''')
    results.append('''<tr>''')
    results.append('''<th class="nowrap" align="left">From Room</th>''')
    results.append('''<th class="nowrap" align="left">To Area</th>''')
    results.append('''<th class="nowrap" align="left">To Coords</th>''')
    results.append('''<th class="nowrap" align="left">Current Room At Coords</th>''')
    results.append('''</tr>''')
    for area in areas:
        for proto_room in area.proto_rooms.itervalues():
            for exit in proto_room.exits.itervalues():
                if not exit.destination:
                    continue
                if exit.destination.area != area:
                    results.append('''<tr>''')
                    results.append('''<td>%s</td><td>%s</td><td class="nowrap">%d %d %d</td>''' % (
                        proto_room.code,
                        exit.destination.area.code,
                        exit.destination.x, exit.destination.y, exit.destination.z))
                    destination_room = exit.destination.get_room()
                    if destination_room:
                        results.append('''<td>%s</td>''' % destination_room.prototype.code)
                    else:
                        results.append('''<td>Nessuna resettata al momento</td>''')
                    results.append('''</tr>''')
    results.append('''</table>''')

    entity.send_output("".join(results).rstrip("\n"), break_line=False)
    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax  = ""
    syntax += "links\n"
    syntax += "links <codice di un'area>\n"

    return syntax
#- Fine Funzione -
