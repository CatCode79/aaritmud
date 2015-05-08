# -*- coding: utf-8 -*-

"""
Comando che permette di invocare un'istanza esistente di player.
"""

#= IMPORT ======================================================================

from src.command import get_command_syntax
from src.config  import config
from src.enums   import TO
from src.log     import log
from src.player  import search_online_player
from src.utility import is_same, is_prefix


#= FUNZIONI ====================================================================

def command_invoke(entity, argument=""):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    return invoke_handler(entity, argument, "command_invoke", "players")
#- Fine Funzione -


def invoke_handler(entity, argument, command_name, table_name):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    if not command_name:
        log.bug("command_name non è un parametro valido: %r" % command_name)
        return False

    if not table_name:
        log.bug("table_name non è un parametro valido: %r" % table_name)
        return False

    # -------------------------------------------------------------------------

    if not argument:
        syntax = get_command_syntax(entity, command_name)
        entity.send_output(syntax, break_line=False)
        return False

    if table_name == "players":
        # Esegue l'invoke solo tra i giocatori online
        target = search_online_player(argument, only_exact=True)
        if not target:
            target = entity.find_entity(argument, entity_tables=[table_name], avoid_equipment=False)
            if not target:
                entity.send_output("Non è stato trovato nessun player con argomento [green]%s[close]." % argument)
            elif not target.game_request:
                entity.send_output("%s non è un player attualmente online." % target.name)
            else:
                entity.send_output("Devi digitare il nome per intero se intendevi il player %s altrimenti digitane un'altro sempre per intero." % target.name)
            return False
    else:
        target = entity.find_entity(argument, entity_tables=[table_name], avoid_equipment=False)
        if not target:
            entity.send_output("Non è stato trovato nessun %s con argomento [green]%s[close]." % (table_name, argument))
            return False

    if entity == target:
        entity.send_output("Non è saggio invocare sé stessi!")
        return False

    entity.act("Apri un [royalblue]misterioso portale[close] con cui risucchiare $N.", TO.ENTITY, target)
    entity.act("$n apre un [royalblue]misterioso portale[close] con cui risucchiare $N.", TO.OTHERS, target)

    if entity.location == target.location:
        entity.act("Vieni risucchiato in un [royalblue]misterioso portale[close] aperto da $n!", TO.TARGET, target)
    else:
        entity.act("$N viene risucchiato in un [royalblue]misterioso portale[close].", TO.OTHERS, target, send_to_location=target.location)
        entity.act("Vieni risucchiato in un [royalblue]misterioso portale[close]!", TO.TARGET, target, send_to_location=target.location)

    target = target.from_location(1, use_repop=True)
    target.to_location(entity.location, use_look=True if target.IS_ACTOR else False)

    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""
    syntax += "invoke\n"
    syntax += "invoke <codice giocatore per intero>\n"
    syntax += "invoke <nome giocatore per intero>\n"

    return syntax
#- Fine Funzione -
