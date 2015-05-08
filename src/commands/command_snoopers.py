# -*- coding: utf-8 -*-

#= IMPORT ======================================================================

from src.command  import get_command_syntax
from src.database import database
from src.enums    import TRUST
from src.log      import log


#= FUNZIONI ====================================================================

def command_snoopers(entity, argument=""):
    """
    Permette di visualizzare tutto l'output di uno o più entità.
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    target = None
    if argument:
        target = entity.find_entity(argument, entity_tables=["players"], avoid_equipment=False)
        if not target:
            entity.send_output("Non trovi nessun amministratore con argomento [white]%s[close]" % argument)
            return False
        if target.trust < TRUST.MASTER:
            entity.send_output("Il giocatore %s non è un amministratore." % target.name)
            return False
        syntax = get_command_syntax(entity, "command_snoopers")
        entity.send_output(syntax, break_line=False)
        return False

    snooped_by = {}
    players_founded = False
    players = database["players"].values()
    for admin in players:
        if admin.trust < TRUST.MASTER or admin.trust > entity.trust:
            continue
        if target and admin != target:
            continue
        snooped_by[admin] = []
        for player in players + database["mobs"].values() + database["items"].values():
            if admin in player.snoopers:
                snooped_by[admin].append(player)
                players_founded = True

    lines = []
    for admin, snooped_players in snooped_by.iteritems():
        if not snooped_players:
            continue
        lines.append("Entità snoopate da %s:" % admin.name)
        for snooped_player in snooped_players:
            lines.append(snooped_player.name)

    if players_founded:
        entity.send_output("\n".join(lines))
    else:
        entity.send_output("Nessun giocatore snoopato dagli amministratori.")

    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""
    syntax += "snoopers\n"
    syntax += "snoopers <nome admin>\n"

    return syntax
#- Fine Funzione -
