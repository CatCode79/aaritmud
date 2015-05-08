# -*- coding: utf-8 -*-

#= IMPORT ======================================================================

from src.command  import get_command_syntax
from src.database import database
from src.grammar  import grammar_gender
from src.enums    import LOG
from src.log      import log
from src.utility  import is_same


#= FUNZIONI ====================================================================

def command_snoop(entity, argument=""):
    """
    Permette di visualizzare tutto l'output di uno o più entità.
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    if not argument:
        syntax = get_command_syntax(entity, "command_snoop")
        entity.send_output(syntax, break_line=False)

        being_watched = []
        for other in database["players"].values() + database["mobs"].values() + database["items"].values():
            if entity in other.snoopers:
                being_watched.append(other)

        if being_watched:
            entity.send_output("Entità che stai snoopando:")
            for other in being_watched:
                if other.IS_ITEM:
                    goto_input = "igoto"
                elif other.IS_ROOM:
                    goto_input = "rgoto"
                elif other.IS_MOB:
                    goto_input = "mgoto"
                else:
                    goto_input = "goto"
                javascript_code = '''javascript:parent.sendInput("%s %s");''' % (goto_input, other.code)
                entity.send_output('''- <a href='%s'>%s</a>''' % (javascript_code, other.get_name(entity)))
        else:
            entity.send_output("Non stai snoopando nessuno.")
        return False

    # -------------------------------------------------------------------------

    if is_same(argument, "stop"):
        counter = remove_and_count_snooped_by(entity)
        if counter > 0:
            entity.send_output("Smetti di snoopare %d entità." % counter)
            log.admin("%s smette di snoopare %d entità" % (entity.name, counter))
        else:
            entity.send_output("Non hai nessuna entità snoopata.")
        return True

    target = entity.find_entity_extensively(argument, inventory_pos="first")
    if not target:
        target = entity.find_entity(argument)
        if not target:
            entity.send_output("Nessuna entità trovata con argomento [green]%s[close]" % argument)
            return False

    if entity == target:
        entity.send_output("Non puoi snoopare te stesso.")
        return False

    if entity in target.snoopers:
        target.snoopers.remove(entity)
        entity.send_output("Smetti di snoopare %s." % target.get_name(entity))
        log.admin("%s smette di snoopare %s" % (entity.name, target.name))
    else:
        snoopers = []
        for snooper in target.snoopers:
            if snooper.trust > entity.trust:
                continue
            snoopers.append(snooper.name)
        if snoopers:
            entity.send_output("%s viene comunque già snoopat%s da: %s" % (
                target, grammar_gender(target), ",".join(snoopers)))

        target.snoopers.append(entity)
        entity.send_output("Incominci a snoopare %s." % target.get_name(entity))
        log.admin("%s incomincia a snoopare %s" % (entity.name, target.name))

    return True
#- Fine Funzione -


def remove_and_count_snooped_by(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    counter = 0
    for other in database["players"].values() + database["mobs"].values() + database["items"].values():
        if entity in other.snoopers:
            other.snoopers.remove(entity)
            counter += 1

    return counter
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""

    syntax += "snoop\n"
    syntax += "snoop <qualcuno o qualcosa>\n"
    syntax += "snoop stop\n"

    return syntax
#- Fine Funzione -
