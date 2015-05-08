# -*- coding: utf-8 -*-

"""
Modulo per la gestione del comando put.
"""

#= IMPORT ======================================================================

from src.color      import color_first_upper
from src.command    import get_command_syntax
from src.enums      import CONTAINER, DIR, FLAG, OPTION, TO, ROOM, TRUST
from src.exit       import get_direction
from src.grammar    import grammar_gender
from src.gamescript import check_trigger
from src.log        import log
from src.utility    import one_argument, quantity_argument


#= FUNZIONI ====================================================================

def give_or_put(entity, argument, verbs, behavioured, entity_tables, noflag, noroom, gamescript_suffix1, gamescript_suffix2, gamescript_suffix3, preposition):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # argument può essere una stringa vuota

    if not verbs:
        log.bug("verbs non è un parametro valido: %r" % verbs)
        return False

    if not entity_tables:
        log.bug("entity_tables non è un parametro valido: %r" % entity_tables)
        return False

    if noflag not in (FLAG.NO_PUT, FLAG.NO_GIVE):
        log.bug("noflag non è un parametro valido: %r" % noflag)
        return False

    if noroom not in (ROOM.NO_PUT, ROOM.NO_GIVE):
        log.bug("noroom non è un parametro valido: %r" % noroom)
        return False

    if gamescript_suffix1 not in ("put", "give"):
        log.bug("gamescript_suffix1 non è un parametro valido: %r" % gamescript_suffix1)
        return False

    if gamescript_suffix2 not in ("putted", "gave"):
        log.bug("gamescript_suffix2 non è un parametro valido: %r" % gamescript_suffix2)
        return False

    if gamescript_suffix3 not in ("putting", "giving"):
        log.bug("gamescript_suffix3 non è un parametro valido: %r" % gamescript_suffix3)
        return False

    if preposition not in ("in", "a"):
        log.bug("gamescript_suffix non è un parametro valido: %r" % gamescript_suffix)
        return False

    # -------------------------------------------------------------------------

    entity = entity.split_entity(1)

    if not argument:
        entity.send_output("Che [white]cosa[close] vorresti %s %s [white]%s[close]?" % (verbs["infinitive"], preposition, "qualcuno" if preposition == "a" else "qualcosa"))
        if entity.IS_PLAYER and OPTION.NEWBIE in entity.account.options:
            syntax = get_command_syntax(entity, "command_put")
            entity.send_output(syntax)
        return False

    # Ricava l'eventuale quantità d'oggetti da posare
    quantity, argument = quantity_argument(argument)
    arg1, argument = one_argument(argument)

    # (TD) Controllo del mental state deviato

    # Ricerca nell'inventario dell'entità quella da dare o mettere
    target = entity.find_entity(arg1, quantity=quantity, location=entity)

    arg2 = ""
    receiver = None
    if argument:
        arg2, argument = one_argument(argument)
        # Rimuove eventuali argomenti facoltativi
        if argument and arg2 == "a":
            arg2, argument = one_argument(argument)
        # Ricerca dell'entità bersaglio a cui dare l'entità target
        receiver = entity.find_entity_extensively(arg2, entity_tables=entity_tables)

        # Controlla se si vuole inserire una porta sui cardini di un'uscita
        direction = get_direction(arg2)
        if target and not receiver and direction != DIR.NONE:
            if not entity.location.IS_ROOM:
                entity.act("Vorresti %s $N sui cardini di un'eventuale uscita %s, ma non ti trovi in una stanza." % (verbs["infinitive"], direction.to_dir), TO.ENTITY, target)
                entity.act("$n vorrebbe %s $N sui cardini di un'eventuale uscita %s, ma non vi trovate in una stanza." % (verbs["infinitive"], direction.to_dir), TO.OTHERS, target)
                entity.act("$n ti vorrebbe %s sui cardini di un'eventuale uscita %s, ma non vi trovate in una stanza." % (verbs["infinitive"], direction.to_dir), TO.TARGET, target)
                return False
            if not direction in entity.location.exits:
                entity.act("Vorresti %s $N sui cardini di un'eventuale uscita %s, ma questa non esiste." % (verbs["infinitive"], direction.to_dir), TO.ENTITY, target)
                entity.act("$n vorrebbe %s $N sui cardini di un'eventuale uscita %s, ma questa non esiste." % (verbs["infinitive"], direction.to_dir), TO.OTHERS, target)
                entity.act("$n ti vorrebbe %s sui cardini di un'eventuale uscita %s, ma questa non esiste." % (verbs["infinitive"], direction.to_dir), TO.TARGET, target)
                return False
            exit_door = entity.location.exits[direction].door
            if exit_door:
                entity.act("Vorresti %s $N sui cardini dell'uscita %s, ma questa possiede già $a." % (verbs["infinitive"], direction.to_dir), TO.ENTITY, target, exit_door)
                entity.act("$n vorrebbe %s $N sui cardini dell'uscita %s, ma questa possiede già $a." % (verbs["infinitive"], direction.to_dir), TO.OTHERS, target, exit_door)
                entity.act("$n ti vorrebbe %s sui cardini dell'uscita %s, ma questa possiede già $a." % (verbs["infinitive"], direction.to_dir), TO.TARGET, target, exit_door)
                return False
            if not target.door_type:
                entity.act("Vorresti %s sui cardini dell'uscita %s $N, ma quest'ultim$O non è una porta." % (verbs["infinitive"], direction.to_dir), TO.ENTITY, target, exit_door)
                entity.act("$n vorrebbe %s sui cardini dell'uscita %s $N, ma quest'ultim$O non è una porta." % (verbs["infinitive"], direction.to_dir), TO.OTHERS, target, exit_door)
                entity.act("$n ti vorrebbe %s sui cardini dell'uscita %s, ma non sei una porta." % (verbs["infinitive"], direction.to_dir), TO.TARGET, target, exit_door)
                return False
            if quantity > 1:
                entity.act("Vorresti %s sui cardini dell'uscita %s $N, ma è possibile inserirne solo un$O." % (verbs["infinitive"], direction.to_dir), TO.ENTITY, target, exit_door)
                entity.act("$n vorrebbe %s sui cardini dell'uscita %s $N, ma è possibile inserirne solo un$O" % (verbs["infinitive"], direction.to_dir), TO.OTHERS, target, exit_door)
                entity.act("$n ti vorrebbe %s sui cardini dell'uscita %s, ma è possibile inserirti solo in un'unità." % (verbs["infinitive"], direction.to_dir), TO.TARGET, target, exit_door)
                return False

            force_return = check_trigger(entity, "before_" + gamescript_suffix1, entity, target, None, direction, behavioured)
            if force_return:
                return True
            force_return = check_trigger(target, "before_" + gamescript_suffix2, entity, target, None, direction, behavioured)
            if force_return:
                return True
            force_return = check_trigger(receiver, "before_" + gamescript_suffix3, entity, target, None, direction, behavioured)
            if force_return:
                return True

            entity.act("%s $N sui cardini dell'uscita %s." % (verbs["you"], direction.to_dir), TO.ENTITY, target)
            entity.act("$n %s $N sui cardini dell'uscita %s." % (verbs["it"], direction.to_dir), TO.OTHERS, target)
            entity.act("$n ti %s sui cardini dell'uscita %s." % (verbs["it"], direction.to_dir), TO.TARGET, target)
            target = target.from_location(1)
            target.to_location(entity.location)
            entity.location.exits[direction].door = target

            force_return = check_trigger(entity, "after_" + gamescript_suffix1, entity, target, None, direction, behavioured)
            if force_return:
                return True
            force_return = check_trigger(target, "after_" + gamescript_suffix2, entity, target, None, direction, behavioured)
            if force_return:
                return True
            force_return = check_trigger(receiver, "after_" + gamescript_suffix3, entity, target, None, direction, behavioured)
            if force_return:
                return True

            return True

    # -------------------------------------------------------------------------

    if not arg2:
        arg2 = "qualcuno" if preposition == "a" else "qualcosa"

    # Se l'entità a cui dare si trova nell'inventario allora lo indica
    on_message_you = ""
    on_message_it = ""
    if receiver and receiver.location and receiver.location == entity:
        if receiver and len(receiver.wear_mode) > 0:
            on_message_you = " che stai [khaki]indossando[close]"
            on_message_it  = " che sta [khaki]indossando[close]"
        else:
            on_message_you = " nel tuo [yellow]inventario[close]"
            on_message_it  = " nel suo [yellow]inventario[close]"

    # Gestisce le varie combinazioni di entità non trovate e/o uguali
    # all'entità che ha digitato il comando
    if target:
        if not receiver:
            entity.act("Cerchi di %s $N %s [white]%s[close] che non trovi da nessuna parte." % (verbs["infinitive"], preposition, arg2), TO.ENTITY, target)
            entity.act("$n cerca di %s $N %s [white]%s[close] che non sembra trovare da nessuna parte." % (verbs["infinitive"], preposition, arg2), TO.OTHERS, target)
            entity.act("$n cerca di %s %s [white]%s[close] che non sembra trovare da nessuna parte." % (verbs["you2"], preposition, arg2), TO.TARGET, target)
            return False
        elif receiver == entity:
            entity.act("Cerchi di %s $N %s te stess$o, ma è già tu$O!" % (verbs["infinitive"], preposition), TO.ENTITY, target)
            entity.act("$n cerca di %s $N %s se stess$o, ma è già su$O." % (verbs["infinitive"], preposition), TO.OTHERS, target)
            entity.act("$n cerca di %s $N %s se stess$o, ma è già su$O." % (verbs["infinitive"], preposition), TO.TARGET, target)
            return False
        elif receiver == target:
            entity.act("Cerchi di %s $N %s se stess$o, ma ciò è impossibile!" % (verbs["infinitive"], preposition), TO.ENTITY, target)
            entity.act("$n cerca di %s $N %s se stess$o, ma ciò è impossibile." % (verbs["infinitive"], preposition), TO.OTHERS, target)
            entity.act("$n cerca di %s $N %s te stess$o, ciò è impossibile." % (verbs["infinitive"], preposition), TO.TARGET, target)
            return False
    elif not target:
        if not receiver:
            entity.act("Cerchi di %s [white]%s[close] %s [white]%s[close], ma non trovi nulla e nessuno nel tuo inventario." % (verbs["infinitive"], arg1, preposition, arg2), TO.ENTITY)
            entity.act("$n cerca di %s [white]qualcosa[close] %s [white]quacuno[close], ma senza molti risultati nel suo inventario." % (verbs["infinitive"], preposition), TO.OTHERS)
            return False
        elif receiver == entity:
            if entity.IS_ITEM:
                entity.act("Cerchi di [orange]passarti [white]%s[close], ma non trovi [gray]nulla del genere[close] nel tuo [yellow]inventario[close]." % arg1, TO.ENTITY, receiver)
                entity.act("$n cerca di [orange]passarsi [white]qualcosa[close] che [gray]non sembra trovare[close] nel suo [yellow]inventario[close].", TO.OTHERS, receiver)
            else:
                entity.act("Cerchi di [orange]passarti[close] da una $hand all'altra [white]%s[close], ma non trovi [gray]nulla del genere[close] nel tuo [yellow]inventario[close]." % arg1, TO.ENTITY, receiver)
                entity.act("$n cerca di [orange]passarsi[close] da una $hand all'altra [white]qualcosa[close] che [gray]non sembra trovare[close] nel suo [yellow]inventario[close].", TO.OTHERS, receiver)
            return False
        else:
            if on_message_you and on_message_it:
                entity.act("Cerchi di %s un [white]%s[close] %s $N%s, ma non trovi [gray]nulla del genere[close]." % (verbs["infinitive"], arg1, preposition, on_message_you), TO.ENTITY, receiver)
                entity.act("$n cerca di %s [white]qualcosa[close] %s $N%s, ma non sembra trovare [gray]nulla del genere[close]." % (verbs["infinitive"], preposition, on_message_it), TO.OTHERS, receiver)
                entity.act("$n cerca di %s [white]qualcosa[close], ma non sembra trovare [gray]nulla del genere[close]." % (verbs["infinitive"]), TO.TARGET, receiver)
            else:
                entity.act("Cerchi di %s un [white]%s[close] %s $N, ma non trovi [gray]nulla del genere[close] nel tuo [yellow]inventario[close]." % (verbs["infinitive"], arg1, preposition), TO.ENTITY, receiver)
                entity.act("$n cerca di %s [white]qualcosa[close] %s $N, ma non sembra trovare [gray]nulla del genere[close] nel suo [yellow]inventario[close]." % (verbs["infinitive"], preposition[2 : ]), TO.OTHERS, receiver)
                entity.act("$n cerca di %s [white]qualcosa[close], ma non sembra trovare [gray]nulla del genere[close] nel suo [yellow]inventario[close]." % (verbs["infinitive"]), TO.TARGET, receiver)
            return False

    if quantity == 0:
        quantity = target.quantity
    elif target.quantity < quantity:
        entity.act("Non puoi %s $N perché ne possiedi solo %d e non %d." % (verbs["infinitive"], target.quantity, quantity), TO.ENTITY, target)
        entity.act("$n sta cercando di ammucchiare un quantitativo voluto di $N per poterlo %s" % verbs["infinitive"], TO.OTHERS, target)
        entity.act("$n sta cercando di ammucchiarti per un quantitativo voluto per poterti %s" % verbs["infinitive"], TO.TARGET, target)
        return False

    if receiver.container_type and CONTAINER.CLOSED in receiver.container_type.flags:
        entity.act("Cerchi di %s $a %s $N ma l$O trovi chius$O." % (verbs["infinitive"], preposition), TO.ENTITY, receiver, target)
        entity.act("$n cerca di %s $a %s $N ma l$O trova chius$O." % (verbs["infinitive"], preposition), TO.OTHERS, receiver, target)
        return False

    # Se l'obiettivo a cui dare l'entità è un oggetto e non è un contenitore
    # allora solo gli admin possono eseguire l'azione
    if receiver.IS_ITEM and not receiver.container_type:
        if entity.trust > TRUST.PLAYER:
            entity.send_to_admin("Il ricevitore non è un contenitore ma tu puoi eseguire comunque l'azione")
        else:
            entity.act("Cerchi di %s $N %s $a, ma quest'ultimo non ti sembra un contenitore." % (verbs["infinitive"], preposition), TO.ENTITY, target, receiver)
            entity.act("$n cerca di %s $N %s $a, ma non riesce a trovare modo per farlo non essendo un contenitore." % (verbs["infinitive"], preposition), TO.OTHERS, target, receiver)
            entity.act("$n cerca di %s %s $a, ma non sembra riuscirvi visto che quest'ultimo non è un contenitore." % (verbs["you2"], preposition), TO.TARGET, target, receiver)
            entity.act("$n cerca di %s $a, ma avrà ben poca fortuna visto che non sei un contenitore." % verbs["you"], TO.TARGET, receiver, target)
            return False
    
    # Se l'entità che ha inviato il comando ha la noflag viene evitata
    # l'azione
    if noflag in entity.flags:
        if entity.trust > TRUST.PLAYER:
            entity.send_to_admin("Tu avresti in realtà la flag NO_GIVE")
        else:
            entity.act("Cerchi di %s $N %s $a, ma qualche [blueroyal]forza misteriosa[close] ti blocca l'azione." % (verbs["infinitive"], preposition), TO.ENTITY, target, receiver)
            entity.act("$n cerca di %s $N %s $a, ma sembra essere bloccat$n da una [royalblue]forza misteriosa[close]." % (verbs["infinitive"], preposition), TO.OTHERS, target, receiver)
            entity.act("$n cerca di %s %s $a, ma sembra essere essere bloccat$o da una [royalblue]forza misteriosa[close]." % (verbs["you2"], preposition), TO.TARGET, target, receiver)
            entity.act("$n cerca di %s $a, ma sembre essere bloccat$o da una [royalblue]forza misteriosa[close]." % verbs["you"], TO.TARGET, receiver, target)
            return False

    # Se l'oggetto da dare ha la flag NO_GIVE allora evita di farsi
    if noflag in target.flags:
        if entity.trust > TRUST.PLAYER:
            entity.send_to_admin("L'entità da dare avrebbe in realtà la flag NO_GIVE")
        else:
            if entity.IS_ITEM:
                entity.act("Appena cerchi di %s $N %s $a te lo ritrovi, con un [cyan]balzo[close] addosso." % (verbs["infinitive"], preposition), TO.ENTITY, target, receiver)
                entity.act("Appena $n cerca di %s $N %s $a se lo ritrova, con un [cyan]balzo[close] addosso." % (verbs["infinitive"], preposition), TO.OTHERS, target, receiver)
                entity.act("Appena $n cerca di %s %s $a gli [cyan]rimbalzi[close] addosso." % (verbs["you2"], preposition), TO.TARGET, target, receiver)
                entity.act("Appena $n cerca di %s $a se lo ritrova, con un [cyan]balzo[close] addosso." % verbs["you2"], TO.TARGET, receiver, target)
            else:
                entity.act("Appena cerchi di %s $N %s $a te lo ritrovi, con un [cyan]balzo[close], in $hand." % (verbs["infinitive"], preposition), TO.ENTITY, target, receiver)
                entity.act("Appena $n cerca di %s $N %s $a se lo ritrova, con un [cyan]balzo[close], in $hand." % (verbs["infinitive"], preposition), TO.OTHERS, target, receiver)
                entity.act("Appena $n cerca di %s %s $a gli [cyan]rimbalzi[close] in $hand." % (verbs["you2"], preposition), TO.TARGET, target, receiver)
                entity.act("Appena $n cerca di %s $a se lo ritrova, con un [cyan]balzo[close], in $hand." % verbs["you2"], TO.TARGET, receiver, target)
            return False

    # Se l'entità a cui dare l'oggetto ha la flag NO_GIVE allora non lo accetta
    if noflag in receiver.flags:
        if entity.trust > TRUST.PLAYER:
            entity.send_to_admin("L'entità a cui dare avrebbe in realtà la flag NO_GIVE")
        else:
            if entity.IS_ITEM:
                entity.act("Cerchi di %s $N %s $a, ma questi te l$O ridà." % (verbs["infinitive"], preposition), TO.ENTITY, target, receiver)
                entity.act("$n cerca di %s $N %s $a, ma questi gliel$O ridà." % (verbs["infinitive"], preposition), TO.OTHERS, target, receiver)
                entity.act("$n cerca di %s %s $a, ma questi gliel$O ridà." % (verbs["you2"], preposition), TO.TARGET, target, receiver)
                entity.act("$n cerca di %s $a, ma gliel%s ridai." % (verbs["you2"], grammar_gender(target)), TO.TARGET, receiver, target)
            else:
                entity.act("Cerchi di %s $N %s $a, ma questi te l$O ridà in $hand." % (verbs["infinitive"], preposition), TO.ENTITY, target, receiver)
                entity.act("$n cerca di %s $N %s $a, ma questi gliel$O ridà in $hand." % (verbs["infinitive"], preposition), TO.OTHERS, target, receiver)
                entity.act("$n cerca di %s %s $a, ma questi gliel$O ridà in $hand." % (verbs["you2"], preposition), TO.TARGET, target, receiver)
                entity.act("$n cerca di %s $a, ma gliel%s ridai in $hand." % (verbs["you2"], grammar_gender(target)), TO.TARGET, receiver, target)
            return False

    # Se la stanza ha la flag NO_GIVE non permette di dare oggetti
    if entity.location.IS_ROOM and noroom in entity.location.flags:
        if entity.trust > TRUST.PLAYER:
            entity.send_to_admin("Questa stanza avrebbe in realtà la flag di NO_GIVE")
        else:
            if entity.IS_ITEM:
                entity.act("Appena cerchi di %s $N %s $a%s te l$O ritrovi addosso come se una [royalblue]forza misteriosa[close] nel luogo ti impedisse quest'azione!" % (
                    verbs["infinitive"], preposition, on_message_you), TO.ENTITY, target, receiver)
                entity.act("Appena $n cerca di %s %s $a%s $N se l$O ritrova addosso come se vi fosse una [royalblue]forza misteriosa[close] nel luogo!" % (
                    verbs["infinitive"], preposition, on_message_it), TO.OTHERS, target, receiver)
                entity.act("Appena $n cerca di %s %s $a%s gli ritorni addosso grazie ad una [royalblue]forza misteriosa[close] del luogo!" % (
                    verbs["you2"], preposition, on_message_it), TO.TARGET, target, receiver)
                entity.act("Appena $n cerca di %s $a gli ritorna addosso grazie ad una [royalblue]forza misteriosa[close] del luogo!" % (
                    verbs["you2"]), TO.TARGET, receiver, target)
            else:
                entity.act("Appena cerchi di %s $N %s $a%s te l$O ritrovi in $hand come se una [royalblue]forza misteriosa[close] nel luogo ti impedisse quest'azione!" % (
                    verbs["infinitive"], preposition, on_message_you), TO.ENTITY, target, receiver)
                entity.act("Appena $n cerca di %s %s $a%s $N se l$O ritrova in $hand come se vi fosse una [royalblue]forza misteriosa[close] nel luogo!" % (
                    verbs["infinitive"], preposition, on_message_it), TO.OTHERS, target, receiver)
                entity.act("Appena $n cerca di %s %s $a%s gli ritorni in $hand grazie ad una [royalblue]forza misteriosa[close] del luogo!" % (
                    verbs["you2"], preposition, on_message_it), TO.TARGET, target, receiver)
                entity.act("Appena $n cerca di %s $a gli ritorna in $hand grazie ad una [royalblue]forza misteriosa[close] del luogo!" % (
                    verbs["you2"]), TO.TARGET, receiver, target)
            return False

    # (TD) dare monete

    # (TD) gestione dell'argomento all, ultima cosa da supportare

    # Se il peso dell'entità da dare supera quello sopportabile dall'obiettivo
    # a cui darlo allora avverte e evita l'azione
    # (TD) size e carry_number come il get?
    if not receiver.can_carry_target(target, quantity=quantity):
        if receiver.trust > TRUST.PLAYER:
            receiver.send_to_admin("Riesci comunque a %s %s anche se è troppo pesante per te." % (
                verbs["infinitive"], target.get_name(entity)))
        elif entity.trust > TRUST.PLAYER and not receiver.IS_PLAYER:
            entity.send_to_admin("Riesci comunque a %s %s anche se è troppo pesante per %s." % (
                verbs["infinitive"], target.get_name(entity), receiver.get_name(entity)))
        else:
            entity.act("Non riesci %s %s $N a $a, non può portare con sé tutto quel peso." % (verbs["infinitive"], preposition), TO.ENTITY, target, receiver)
            entity.act("$n non riesce a %s $N %s $a, non può portare con sé tutto quel peso." % (verbs["infinitive"], preposition), TO.OTHERS, target, receiver)
            entity.act("$n non riesce a %s %s $a, non può portare con sé tutto il tuo peso." % (verbs["you2"], preposition), TO.TARGET, target, receiver)
            entity.act("$n non riesce a %s $a, non puoi portare con te tutto quel peso." % verbs["you2"], TO.TARGET, receiver, target)
            return False

    force_return = check_trigger(entity, "before_" + gamescript_suffix1, entity, target, receiver, DIR.NONE, behavioured)
    if force_return:
        return True
    force_return = check_trigger(target, "before_" + gamescript_suffix2, entity, target, receiver, DIR.NONE, behavioured)
    if force_return:
        return True
    force_return = check_trigger(receiver, "before_" + gamescript_suffix3, entity, target, receiver, DIR.NONE, behavioured)
    if force_return:
        return True

    if on_message_you and on_message_it:
        entity.act("%s $N %s $a%s." % (color_first_upper(verbs["you"]), preposition, on_message_you), TO.ENTITY, target, receiver)
        entity.act("$n %s $N %s $a%s." % (verbs["it"], preposition, on_message_it), TO.OTHERS, target, receiver)
        entity.act("$n ti %s %s $a%s." % (verbs["it"], preposition, on_message_it), TO.TARGET, target, receiver)
        entity.act("$n ti %s $a." % verbs["it"], TO.TARGET, receiver, target)
    else:
        entity.act("%s $N %s $a." % (color_first_upper(verbs["you"]), preposition), TO.ENTITY, target, receiver)
        entity.act("$n %s $N %s $a." % (verbs["it"], preposition), TO.OTHERS, target, receiver)
        entity.act("$n ti %s %s $a." % (verbs["it"], preposition), TO.TARGET, target, receiver)
        entity.act("$n ti %s $a." % verbs["it"], TO.TARGET, receiver, target)

    target = target.from_location(quantity, use_repop=True)
    target.to_location(receiver)

    force_return = check_trigger(entity, "after_" + gamescript_suffix1, entity, target, receiver, DIR.NONE, behavioured)
    if force_return:
        return True
    force_return = check_trigger(target, "after_" + gamescript_suffix2, entity, target, receiver, DIR.NONE, behavioured)
    if force_return:
        return True
    force_return = check_trigger(receiver, "after_" + gamescript_suffix3, entity, target, receiver, DIR.NONE, behavioured)
    if force_return:
        return True

    return True
#- Fine Funzione -
