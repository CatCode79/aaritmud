# -*- coding: utf-8 -*-

"""
Comando che permette di rimuovere un'uscita nella direzione desiderata.
"""

#= IMPORT ======================================================================

from src.command  import get_command_syntax
from src.database import database
from src.element  import EnumElementDict
from src.enums    import RACE
from src.log      import log
from src.utility  import one_argument, is_same


#= FUNZIONI ====================================================================

def command_countraces(entity, argument=""):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    only_items = False

    if not argument:
        syntax = get_command_syntax(entity, "command_countraces")
        entity.send_output(syntax, break_line=False)
    else:
        arg, argument = one_argument(argument)
        if is_same(arg, "items") or (argument and is_same(argument, "items")):
            only_items = True

    if only_items:
        attr_suffix = "items"
    else:
        attr_suffix = "mobs"

    counter = {}
    counter["totale"] = EnumElementDict()
    for area in database["areas"].itervalues():
        counter[area] = EnumElementDict()
        targets = getattr(area, attr_suffix)
        for target in targets:
            if target.race == RACE.NONE:
                continue
            if target.race not in counter[area]:
                counter[area][target.race] = 0
            counter[area][target.race] += 1
            if target.race not in counter["totale"]:
                counter["totale"][target.race] = 0
            counter["totale"][target.race] += 1

    if only_items:
        entity.send_output("\nLista del numero di razze degli oggetti suddivisi per area.", break_line=False)
    else:
        entity.send_output("\nLista del numero di razze dei mob suddivisi per area.", break_line=False)

    output = []
    for area in counter:
        if not counter[area] or area == "totale":
            continue
        output.append('''<br>[%s]%s[close] (%s):''' % (area.color.web_name, area.name, area.code))
        output.append('''<table class="mud" style="width:75%">''')
        for race_element in RACE.elements:
            if race_element not in counter[area]:
                continue
            output.append('''<tr><td style="width:33%%">%s</td><td style="width:33%%">%s</td><td>%d</td></tr>''' % (
                race_element.code, race_element, counter[area][race_element]))
        output.append('''</table>''')

    if output:
        output.append('''<br>[white]Gran Totale[close]:''')
        output.append('''<table class="mud" style="width:75%">''')
        for race_element in RACE.elements:
            if race_element not in counter["totale"]:
                continue
            output.append('''<tr><td style="width:33%%">%s</td><td style="width:33%%">%s</td><td>%d</td></tr>''' % (
                race_element.code, race_element, counter["totale"][race_element]))
        output.append('''</table>''')
        entity.send_output("".join(output))
    else:
        entity.send_output('''<br>Nessuna!''')

    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""

    syntax += "countraces\n"
    syntax += "countraces items\n"

    return syntax
#- Fine Funzione -
