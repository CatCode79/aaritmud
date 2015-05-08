# -*- coding: utf-8 -*-

#= IMPORT ======================================================================

from src.command    import get_command_syntax
from src.enums      import OPTION, PORTAL, ROOM, TO
from src.gamescript import check_trigger
from src.log        import log


#= COSTANTI ====================================================================

VERBS = {}
VERBS["you"]          = "[royalblue]Entri[close]"
VERBS["it"]           = "[royalblue]entra[close]"
VERBS["infinitive"]   = "[royalblue]entrare[close]"
VERBS["you2"]         = "[royalblue]Arrivi[close]"
VERBS["it2"]          = "[royalblue]arriva[close]"
VERBS["destination2"] = "[royalblue]viene mandato[close]"


#= FUNZIONI ====================================================================

# Visto con malizia questo comando è tutto un po' strano...
def command_enter(entity, argument="", verbs=VERBS, behavioured=False, following=False, fleeing=False):
    if not verbs:
        log.bug("verbs non è un parametro valido: %r" % verbs)
        return False

    # -------------------------------------------------------------------------

    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    entity = entity.split_entity(1)

    if not argument:
        entity.send_output("Dove vorresti %s?" % verbs["infinitive"])
        if entity.IS_PLAYER and OPTION.NEWBIE in entity.account.options:
            syntax = get_command_syntax(entity, "command_enter")
            entity.send_output(syntax, break_line=False)
        return False

    target = entity.find_entity_extensively(argument)
    if not target:
        entity.act("Cerchi di %s dentro [white]%s[close] che però non riesci a trovare." % (verbs["infinitive"], argument), TO.ENTITY)
        entity.act("$n cerca qualcosa che non sembra riuscire a trovare." % verbs["infinitive"], TO.OTHERS)
        return False

    if not target.portal_type:
        if entity == target:
            entity.act("Cerchi di %s in te stess$o." % verbs["infinitive"], TO.ENTITY)
            entity.act("$n cerca di %s in sé stess$o." % verbs["infinitive"], TO.OTHERS)
        else:
            entity.act("Cerchi di %s dentro $N, ma non ci riesci." % verbs["infinitive"], TO.ENTITY, target)
            entity.act("$n cerca di %s dentro $N, ma non ci riesce." % verbs["infinitive"], TO.OTHERS, target)
            entity.act("$n cerca di %s dentro di te, ma non ci riesce." % verbs["infinitive"], TO.TARGET, target)
        return False

    destination_room = target.portal_type.get_destination_room(target)
    if not destination_room:
        # Possibile quando è stata impostata sia destination che target_code e
        # le stanze di destinazione ricavate non coincidono
        target.portal_type.send_no_room_messages(entity, target, verbs)
        return False

    if (not following and entity.IS_MOB    and PORTAL.NO_MOB    in target.portal_type.flags
    or  not following and entity.IS_ITEM   and PORTAL.NO_ITEM   in target.portal_type.flags
    or  not following and entity.IS_ROOM   and PORTAL.NO_ROOM   in target.portal_type.flags
    or                    entity.IS_PLAYER and PORTAL.NO_PLAYER in target.portal_type.flags):
        entity.act("Ti è proibito %s dentro $N." % verbs["infinitive"], TO.ENTITY, target)
        entity.act("$n cerca di %s dentro $N ma gli è proibito." % verbs["infinitive"], TO.OTHERS, target)
        return False

    if (not following and entity.IS_MOB    and ROOM.NO_MOB    in destination_room.flags
    or  not following and entity.IS_ITEM   and ROOM.NO_ITEM   in destination_room.flags
    or  not following and entity.IS_ROOM   and ROOM.NO_ROOM   in destination_room.flags
    or                    entity.IS_PLAYER and ROOM.NO_PLAYER in destination_room.flags):
        if target.entitype == ENTITYPE.PORTAL:
            entity.act("Ti è proibito raggiungere $N.", TO.ENTITY, destination_room)
            entity.act("$n cerca di raggiungere $N ma gli è proibito.", TO.OTHERS, destination_room)
        else:
            entity.act("Ti è proibito raggiungere la destinazione di $N.", TO.ENTITY, target)
            entity.act("$n cerca di raggiungere la destinazione di $N ma gli è proibito.", TO.OTHERS, target)
        return False

    starting_location = entity.location
    force_return = check_trigger(entity, "before_enter", entity, target, starting_location, destination_room, behavioured)
    if force_return:
        return True
    force_return = check_trigger(target, "before_entered", entity, target, starting_location, destination_room, behavioured)
    if force_return:
        return True

    target.portal_type.send_enter_messages(entity, target, verbs, fleeing)

    location = entity.location
    entity = entity.from_location(1, use_repop=True)
    entity.to_location(destination_room, use_look=True)
    # L'entità si porta dietro anche coloro che lo stanno seguendo
    # (TD) ma cosa succede se can_see è False?
    # Viene iterato utilizzando il reversed per evitare che eventuali trigger
    # nel comando enter rimuovano follower dalla locazione falsando quindi
    # l'iterazione
    for follower in location.iter_contains(use_reversed=True):
        if follower.guide == entity:
            command_enter(follower, argument, following=True)

    target.portal_type.show_exit_messages(entity, target, verbs, fleeing)

    # Dona un po' di esperienza ai giocatori che sono entrati per la prima
    # volta nell'entità
    if entity.IS_PLAYER:
        if target.prototype.code in entity.entered_entities:
            entity.entered_entities[target.prototype.code] += 1
        else:
            entity.entered_entities[target.prototype.code] = 1
            reason = "per essere entrato per la prima volta in %s" % target.get_name(looker=entity)
            entity.give_experience(target.level*100, reason=reason)

    force_return = check_trigger(entity, "after_enter", entity, target, starting_location, destination_room, behavioured)
    if force_return:
        return True
    force_return = check_trigger(target, "after_entered", entity, target, starting_location, destination_room, behavioured)
    if force_return:
        return True

    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    return "enter <entità in cui entrare>\n"
#- Fine Funzione -
