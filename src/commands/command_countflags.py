# -*- coding: utf-8 -*-

#= IMPORT ======================================================================

import operator

from src.command  import get_command_syntax
from src.database import database
from src.element  import get_enum_element
from src.log      import log
from src.utility  import getattr_from_path


#= FUNZIONI ====================================================================

def command_countflags(entity, argument=""):
    """
    Permette di raggiungere il primo oggetto trovato con la flag passata.
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    if not argument:
        syntax = get_command_syntax(entity, "command_countflags")
        entity.send_output(syntax, break_line=False)
        return False

    argument = argument.upper().replace(" ", "_")
    if "." in argument:
        enum_element = get_enum_element(argument, quiet=True)
    else:
        for enum_name in ("FLAG.", "CONTAINER.", "DOOR.", "PORTAL.", "WEAPONFLAG."):
            enum_element = get_enum_element(enum_name + argument, quiet=True)
            if not enum_element:
                continue
            else:
                break

    if not enum_element:
        entity.send_output("Nessun elemento di enumerazione trovato con argomento [green]%s[close]" % argument)
        return False

    if enum_element.enum.name == "FLAG":
        path = "flags"
    elif enum_element.enum.name == "CONTAINER":
        path = "container_type.flags"
    elif enum_element.enum.name == "DOOR":
        path = "door_type.flags"
    elif enum_element.enum.name == "PORTAL":
        path = "portal_type.flags"
    elif enum_element.enum.name == "WEAPONFLAG":
        path = "weapon_type.flags"
    else:
        entity.send_output("L'enumerazione %s non è ancora supportata, se serve basta dirlo al coder." % enum_element.enum.name)
        return False

    output = []
    for table_name, goto_input in (("items", "igoto"), ("mobs", "mgoto"), ("players", "goto")):
        counter = 0
        entities = []
        # Crea prima la lista per poi ordinarla
        for target in database[table_name].itervalues():
            attr = getattr_from_path(target, path)
            if attr and enum_element in attr:
                entities.append(target)

        if entities:
            output.append('''<table class="mud">''')
            output.append('''<tr><th>Code:</th><th>Name:</th><th>Short:</th></tr>''')
            for target in sorted(entities, key=operator.attrgetter("code")):
                javascript = '''javascript:parent.sendInput('%sgoto %s');''' % (
                    goto_input, target.keywords_name.split()[0])
                output.append('''<tr>''')
                output.append('''<td><a href="%s">%s</td><td>%s</td>''' % (
                    javascript, target.code, target.name))
                if target.short_night:
                    tooltip = create_tooltip(entity.get_conn(), "ShortNight: %s" % room.short_night, room.short)
                    output.append('''<td><>%s</td>''' % tooltip)
                else:
                    output.append('''<td>%s</td>''' % target.short)
                output.append('''</tr>''')
                counter += 1
            output.append('''</table>''')
            output.append('''Sono stati trovati %s %s con la flag %s\n\n''' % (counter, table_name, enum_element.code))
        else:
            output.append('''Non è stato trovato nessun %s con la flag %s\n\n''' % (table_name[:-1], enum_element.code))

    entity.send_output("".join(output).rstrip())
    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax  = ""

    syntax += "countflags\n"
    syntax += "countflags <FLAG>\n"

    return syntax
#- Fine Funzione -
