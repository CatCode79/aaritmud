# -*- coding: utf-8 -*-

"""
Comando che permette di modificare la razza di un'entità.
"""


#= IMPORT ======================================================================

from src.command import get_command_syntax
from src.element import get_element_from_name, get_enum_element
from src.enums   import RACE
from src.log     import log
from src.utility import one_argument


#= FUNZIONI ====================================================================

def command_setrace(entity, argument=""):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    if not argument:
        syntax = get_command_syntax(entity, "command_setrace")
        entity.send_output(syntax, break_line=False)
        return False

    arg, argument = one_argument(argument)
    target = entity.find_entity_extensively(arg)
    if not target:
        entity.send_output("Nessuna entità trovata con argomento [white]%s[close]" % arg)
        return False

    if not argument:
        entity.send_output("Che razza vuoi impostare a [white]%s[close]?" % target.get_name(entity))
        return False

    new_race = get_element_from_name(RACE, argument)
    if not new_race:
        new_race = get_enum_element(argument, quiet=True)
        if not new_race:
            new_race = get_enum_element("RACE." + argument.upper(), quiet=True)
            if not new_race:
                entity.send_output("Nessuna razza trovata con argomento [white]%s[close]" % argument)
                return False

    if target.race == new_race:
        if target == entity:
            entity.send_output("La tua razza è già %s" % new_race)
        else:
            entity.send_output("La razza di %s è già %s" % (target.get_name(looker), new_race))
        return False

    if target == entity:
        entity.send_output("Cambi la tua razza da %s in %s." % (target.race, new_race))
    else:
        entity.send_output("Cambi la razza dell'entità %s da %s in %s." %(target.get_name(entity), target.race, new_race))
    target.race = new_race
    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""

    syntax += "setrace\n"
    syntax += "setrace <nome o codice entità> <razza>\n"

    return syntax
#- Fine Funzione -
