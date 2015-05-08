# -*- coding: utf-8 -*-


#= IMPORT ======================================================================

from src.command    import get_command_syntax
from src.enums      import CONTAINER, DIR, DOOR, OPTION, TO
from src.exit       import get_destination_room_from_door
from src.gamescript import check_trigger
from src.log        import log


#= COSTANTI ====================================================================

VERBS = {"infinitive" : "[saddlebrown]chiudere[close]",
         "you2"       : "[saddlebrown]chiuderti[close]",
         "you"        : "[saddlebrown]Chiudi[close]",
         "it"         : "[saddlebrown]chiude[close]"}


#= FUNZIONI ====================================================================

def command_close(entity, argument="", verbs=VERBS, behavioured=False, container_only=False):
    if not verbs:
        log.bug("verbs non è un parametro valido: %r" % verbs)
        return False

    # -------------------------------------------------------------------------

    entity = entity.split_entity(1)

    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    if not argument:
        entity.send_output("Che cosa vorresti %s?" % verbs["infinitive"])
        if entity.IS_PLAYER and OPTION.NEWBIE in entity.account.options:
            syntax = get_command_syntax(entity, "command_close")
            entity.send_output(syntax, break_line=False)
        return False

    target = entity.find_entity_extensively(argument, inventory_pos="last")
    if not target:
        entity.act("Cerchi di %s %s che però non riesci a trovare." % (verbs["infinitive"], argument), TO.ENTITY)
        entity.act("$n cerca qualcosa che non sembra riuscire a trovare.", TO.OTHERS)
        return False

    # Nel caso che la porta, nel lato della stanza in cui entity si trova, sia
    # già chiusa NON prova a controllare l'eventuale porta dall'altro lato, come
    # invece succede col comando open, perché sarebbe impossibile da raggiungere

    if not target.door_type and not target.container_type:
        if entity == target:
            entity.act("Cerchi di %s te stess$o, senza molto successo..." % verbs["infinitive"], TO.ENTITY)
            entity.act("$n cerca di %s sé stess$o, senza molto successo..." % verbs["infinitive"], TO.OTHERS)
        else:
            entity.act("Cerchi di %s $N, ma non trovi modo di farlo." % verbs["infinitive"], TO.ENTITY, target)
            entity.act("$n cerca di %s $N, ma non sembra trovare modo di farlo." % verbs["infinitive"], TO.OTHERS, target)
            entity.act("$n cerca di %s, ma non sembra trovare modo di farlo." % verbs["you2"], TO.TARGET, target)
        return False

    if container_only and not target.container_type and target.door_type:
        entity.act("Cerchi di %s $N, ma non sembra essere un contenitore." % verbs["infinitive"], TO.ENTITY, target)
        entity.act("$n cerca di %s $N, ma non sembra essere un contenitore." % verbs["infinitive"], TO.OTHERS, target)
        entity.act("$n cerca di %s, ma non sembra essere un contenitore." % verbs["you2"], TO.TARGET, target)
        return False

    if container_only:
        entitype_priority = "container"
    else:
        entitype_priority = target.get_open_close_priority()
    if entitype_priority != "door" and entitype_priority != "container":
        log.bug("entitype_priority è un valore errato: %s" % entitype_priority)
        return False

    reverse_target = None
    if entitype_priority == "door":
        if not target.is_hinged():
            entity.act("Come puoi %s $N se si trova fuori dai cardini?" % verbs["infinitive"], TO.ENTITY, target)
            entity.act("$n cerca di %s $N, sarà un po' dura visto che non si trova sui cardini." % verbs["infinitive"], TO.OTHERS, target)
            entity.act("$n cerca di %s, sarà un po' dura visto che non ti trovi sui cardini..." % verbs["you2"], TO.TARGET, target)
            return False

        if DOOR.BASHED in target.door_type.flags:
            entity.act("Cerchi di %s $N, ma l$O trovi sfondat$O." % verbs["infinitive"], TO.ENTITY, target)
            entity.act("$n cerca di %s $N, ma l$O trova sfondat$O." % verbs["infinitive"], TO.OTHERS, target)
            entity.act("$n cerca di %s, ma ti trova sfondat$O." % verbs["you2"], TO.TARGET, target)
            return False

        entitype      = target.door_type
        bolted_flag   = DOOR.BOLTED
        locked_flag   = DOOR.LOCKED
        closed_flag   = DOOR.CLOSED
        closable_flag = DOOR.CLOSABLE

        destination_room, direction = get_destination_room_from_door(entity, target)
        # Se c'è una stanza di destinazione al di là della porta allora
        # controlla che da quella stanza sia possibile arrivare a questa,
        # altrimenti non fa visualizzare i messaggi remoti
        if destination_room:
            reverse_destination = destination_room.get_destination(direction.reverse_dir)
            if reverse_destination:
                reverse_destination_room = reverse_destination.get_room()
                if entity.location == reverse_destination_room:
                    # Ricava la porta che si vede dall'altra parte
                    reverse_target = destination_room.get_door(direction.reverse_dir, reverse_search=False)
                else:
                    destination_room = None
                    direction = DIR.NONE
    else:
        entitype         = target.container_type
        # (TD) tutte queste flag sarebbero da spostare nelle strutture container_type e door_type apposite, questo anche nel comando lock e simili
        bolted_flag      = CONTAINER.BOLTED
        locked_flag      = CONTAINER.LOCKED
        closed_flag      = CONTAINER.CLOSED
        closable_flag    = CONTAINER.CLOSABLE
        destination_room = None  # (TD) supportarlo
        direction        = None

    if closed_flag in entitype.flags:
        entity.act("Cerchi di %s $N, ma l$O trovi già chius$O." % verbs["infinitive"], TO.ENTITY, target)
        entity.act("$n cerca di %s $N, ma l$O trova già chius$O." % verbs["infinitive"], TO.OTHERS, target)
        entity.act("$n cerca di %s, ma ti trova già chius$O." % verbs["you2"], TO.TARGET, target)
        if destination_room:
            entity.act("Qualcuno, dall'altra parte, cerca di %s $N %s, ma l$O trova già chius$O." % (
                verbs["infinitive"], direction.reverse_dir.to_dir2), TO.OTHERS, reverse_target, send_to_location=destination_room)
        return False

    # (TD) forse qui è come il test del locked sotto, oppure devo aggiungere
    # una flag che mi indichi se il bolt permetta o meno di chiudere la porta
    if bolted_flag in entitype.flags:
        entity.act("Cerchi di %s $N, scopri che è già chius$O con $a." % verbs["infinitive"], TO.ENTITY, target, entitype.bolt)
        entity.act("$n cerca di %s $N, scoprendo che è già chius$O con $a." % verbs["infinitive"], TO.OTHERS, target, entitype.bolt)
        entity.act("$n cerca di %s, scoprendo che sei già chius$O con $a." % verbs["you2"], TO.TARGET, target, entitype.bolt)
        if destination_room:
            entity.act("Qualcuno, dall'altra parte, cerca di %s $N %s, scoprendo che è già chius$O con $a." % (
                verbs["infinitive"], direction.reverse_dir.to_dir2), TO.OTHERS, reverse_target, send_to_location=destination_room)
        return False

    # (TD) Questa sarà una feature maggiormente utile nel bolt
    #if locked_flag in entitype.flags:
    #    entity.act("Cerchi di %s $N, ma non vi riesci perché è stat$O bloccat$O con la chiave." % verbs["infinitive"], TO.ENTITY, target)
    #    entity.act("$n cerca di %s $N, ma per qualche motivo non ci riesce." % verbs["infinitive"], TO.OTHERS, target)
    #    entity.act("$n cerca di %s, ma non vi riesce perché sei stat$O bloccat$O con la chiave." % verbs["you2"], TO.TARGET, target)
    #    if destination_room:
    #        entity.act("Qualcuno, dall'altra parte, non riesce a %s $N %s perché è stat$O bloccat$O con la chiave." % (
    #            verbs["infinitive"], direction.reverse_dir.to_dir2), TO.OTHERS, reverse_target, send_to_location=destination_room)
    #    return False

    if closable_flag not in entitype.flags:
        entity.act("Non ti è possibile %s $N." % verbs["infinitive"], TO.ENTITY, target)
        entity.act("$n fa gesto di voler %s $N, ma gli è impossibile." % verbs["infinitive"], TO.OTHERS, target)
        if destination_room:
            entity.act("Qualcuno, dall'altra parte, cerca di %s $N, scoprendo che gli è impossibile." % (
                verbs["infinitive"]), TO.OTHERS, reverse_target, send_to_location=destination_room)
        entity.act("$n fa gesto di volerti %s, ma gli è impossibile." % verbs["infinitive"], TO.TARGET, target)
        return False

    force_return = check_trigger(entity, "before_close", entity, target, reverse_target, container_only, behavioured)
    if force_return:
        return True
    force_return = check_trigger(target, "before_closeed", entity, target, reverse_target, container_only, behavioured)
    if force_return:
        return True

    entitype.send_close_messages(entity, target, verbs, direction, destination_room, reverse_target)
    entitype.flags += closed_flag
    if reverse_target and reverse_target.door_type and DOOR.ASYNCHRONOUS not in target.door_type.flags:
        reverse_target.door_type.flags += closed_flag

    # Serve a cambiare lo status della porta o del contenitore tramite il
    # meccanismo di repop allo stato originario
    if target.repop_later:
        target.deferred_repop = target.repop_later.defer_check_status()
    if reverse_target and reverse_target.repop_later:
        reverse_target.deferred_repop = reverse_target.repop_later.defer_check_status()

    force_return = check_trigger(entity, "after_close", entity, target, reverse_target, container_only, behavioured)
    if force_return:
        return True
    force_return = check_trigger(target, "after_closed", entity, target, reverse_target, container_only, behavioured)
    if force_return:
        return True

    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    return "close <porta o contenitore da chiudere>\n"
#- Fine Funzione -
