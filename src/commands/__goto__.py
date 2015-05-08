# -*- coding: utf-8 -*-

"""
Modulo per la gestione generica dei comandi di goto.
"""

#= IMPORT ======================================================================

from src.enums      import FLAG, TO
from src.grammar    import grammar_gender
from src.log        import log
from src.utility    import get_weight_descr


#= FUNZIONI ====================================================================

def goto_entity_handler(entity, argument, table_name):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return None, None, ""

    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return None, None, ""

    if not table_name:
        log.bug("table_name non è un parametro valido: %r" % table_name)
        return None, None, ""

    # -------------------------------------------------------------------------

    # Se si vuole cercare tra i giocatori allora cerca prima tra quelli online
    if table_name == "players":
        from src.player import search_online_player
        player = search_online_player(argument)
        if player == entity:
            entity.send_output("L'obiettivo del goto sei [white]tu[close]!")
            return None, None, ""
        if player:
            return player, player.get_in_room(), "\nL'obiettivo del goto era %s" % player.get_name(entity)

    target = entity.find_entity(argument, entity_tables=[table_name], avoid_equipment=False, avoid_doors=False)
    if not target:
        entity.send_output("Nessun %s trovato con argomento [green]%s[close]." % (
            table_name[ : -1], argument))
        return None, None, ""

    if target.IS_PLAYER and not target.game_request:
        room = target.get_in_room()
        if not room:
            entity.send_output("Il giocatore offline %s non ha una stanza valida: %r" % (target.name, room))
            return None, None, ""
        if not room.IS_ROOM:
            entity.send_output("Il giocatore offline %s non si trova in una stanza: %s (normale se il giocatore non si è mai collegato o se sono state rimosse le persistenze)" % (
                target.name, room))
            return None, None, ""
        return target, room, "Il giocatore %s ha quittato in questa stanza." % target.name

    if not target.location:
        entity.send_output("%s %s esiste ma non è raggiungibile perché non ha location valida: %r" % (
            target.__class__.__name__, target.code, target.location))
        return None, None, ""

    if target.location == entity:
        if len(target.wear_mode) > 0:
            where_is = "equipaggiamento"
        elif FLAG.INGESTED in target.flags:
            where_is = "stomaco"
        else:
            where_is = "inventario"
        entity.send_output("L'entità %s si trova nel tuo %s." % (target.get_name(), where_is))
        return None, None, ""

    room = target.get_in_room()
    if not room:
        entity.send_output("Per qualche strano motivo bacoso l'entità %s (contenuta o meno) non si trova in una stanza." % target.get_name())
        return None, None, ""

    if target == entity:
        entity.send_output("L'obiettivo del goto sei [white]tu[close]!")
        return None, None, ""

    last_message = "\nL'obiettivo del goto era %s" % target.get_name()
    player_carrier = target.get_player_previous_carrier()
    if player_carrier and not player_carrier.game_request:
        last_message += " contenuto da %s che ha quittato in questa stanza." % target.location.get_name()
    elif target.location:
        # (TT) qui forse dovrei utilizzare la get_in_room
        last_message += " contenuto da %s, sei stat$o spostat$o nel luogo in cui si trova quest'ultim%s." % (
            target.location.get_name(), grammar_gender(target))

    return target, room, last_message
# - Fine Funzione -


def goto_message(entity, room, command_name):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return

    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return

    if not command_name:
        log.bug("command_name non è un parametro valido: %r" % command_name)
        return

    # -------------------------------------------------------------------------

    room_destination = room.get_destination()
    if not room_destination:
        log.bug("room_destination non è valida: %r" % destination)
        return

    javascript_code = '''javascript:parent.sendInput('rgoto %s');''' % room_destination
    html_link = '''<a href="%s">%s</a>''' % (javascript_code, room_destination)
    entity.act("$n esegue un %s verso %s" % (command_name, html_link), TO.ADMINS)
# - Fine Funzione -
