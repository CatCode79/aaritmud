# -*- coding: utf-8 -*-

"""
Modulo per la gestione del comando per seminare o piantare un'entità.
"""

#= IMPORT ======================================================================

import random

from src.color      import color_first_upper
from src.command    import get_command_syntax
from src.config     import config
from src.enums      import ENTITYPE, FLAG, OPTION, TO
from src.gamescript import check_trigger
from src.log        import log
from src.utility    import one_argument

from src.entitypes.container import Container


#= FUNZIONI ====================================================================

# Questo comando è concettualmente uguale ai comandi di give e put, quindi
# per ogni fix che avviene nel primo bisognerebbe passare anche qui a dare
# una controllatina.
def seed_or_plant(entity, argument, verbs, behavioured, command_name):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    if not verbs:
        log.bug("verbs non è un parametro valido: %r" % verbs)
        return False

    if command_name not in ("command_seed", "command_plant"):
        log.bug("command_name non è un parametro valido: %r" % command_name)
        return False

    # -------------------------------------------------------------------------

    entity = entity.split_entity(1)

    gamescript_suffix = command_name.split("_")[1]
    type_attr_name = gamescript_suffix + "_type"

    if not argument:
        entity.act("Che cosa vorresti %s?" % verbs["infinitive"], TO.ENTITY)
        if entity.IS_PLAYER and OPTION.NEWBIE in entity.account.options:
            syntax = get_command_syntax(entity, command_name)
            entity.send_output(syntax, break_line=False)
        return False

    # (TD) Controllo del mental state deviato

    # Ricerca le entità da seminare o piantare nell'inventario
    arg1, argument = one_argument(argument)
    target = entity.find_entity(arg1, location=entity)
    if not target:
        entity.act("Non hai nessun [white]%s[close] da %s." % (arg1, verbs["infinitive"]), TO.ENTITY)
        entity.act("$n sta cercando inutilmente qualcosa.", TO.OTHERS)
        return False

    arg2 = ""
    location = entity.location
    if argument:
        arg2, argument = one_argument(argument)
        # Rimuove eventuali argomenti facoltativi
        if argument and arg == "in":
            arg2, argument = one_argument(argument)
        # Ricerca dell'entità bersaglio a cui dare l'entità target
        location = entity.find_entity_extensively(arg2)
        if not location:
            entity.act("Non hai trovato nessun [white]%s[close] ove %s $N." % (arg2, verbs["infinitive"]), TO.ENTITY, target)
            entity.act("$n non ha trovato nulla ove %s $N." % (verbs["infinitive"]), TO.OTHERS, target)
            entity.act("$n non ha trovato nulla ove %s." % (verbs["you2"]), TO.TARGET, target)
            return False

    if not arg2:
        arg2 = "da qualche parte"

    # Se l'entità a cui dare si trova nell'inventario allora lo indica
    inventory_message_you = ""
    inventory_message_it = ""
    if location and not location.IS_ROOM and location.location and location.location == entity:
        inventory_message_you = ", nel tuo [yellow]inventario[close],"
        inventory_message_it  = ", nel suo [yellow]inventario[close],"

    # Qui vengono gestite i due casi particolari in cui una delle due entità
    # è stata trovata mentre l'altra no, e quella trovata corrisponde all'entità
    # che ha inviato il comando
    if target and not location and target == entity:
        entity.act("Cerchi di %s [white]te stess$o[close] a [white]%s[close] che non trovi da [gray]nessuna parte[close]." % (verbs["infinitive"], arg2), TO.ENTITY, target)
        entity.act("$n cerca di %s [white]sé stess$o[close] a [white]qualcuno[close] che non sembra trovare da [gray]nessuna parte[close]." % verbs["infinitive"], TO.OTHERS, target)
        return False
    elif not target and location and location == entity:
        entity.act("Cerchi di [orange]passarti[close] da una $hand all'altra [white]%s[close], ma non trovi [gray]nulla del genere[close]." % arg1, TO.ENTITY, location)
        entity.act("$n cerca di [orange]passarsi[close] da una $hand all'altra [white]qualcosa[close] che [gray]non sembra trovare[close].", TO.OTHERS, location)
        return False

    # Gestisce le tre combinazioni di entità non trovate
    if target:
        if not location:
            entity.act("Cerchi di %s $N a [white]%s[close] che non trovi da [gray]nessuna parte[close]." % (verbs["infinitive"], arg2), TO.ENTITY, target)
            entity.act("$n cerca di %s $N a [white]quacuno[close] che non sembra trovare da [gray]nessuna parte[close]." % verbs["infinitive"], TO.OTHERS, target)
            entity.act("$n cerca di %s a [white]qualcuno[close] che non sembra trovare da [gray]nessuna parte[close]." % verbs["you2"], TO.TARGET, target)
            return False
    else:
        if location:
            entity.act("Cerchi di %s a $N%s un [white]%s[close], ma non trovi [gray]nulla del genere[close]." % (verbs["infinitive"], inventory_message_you, arg1), TO.ENTITY, location)
            entity.act("$n cerca di %s a $N%s [white]qualcosa[close], ma non sembra trovare [gray]nulla del genere[close]." % (verbs["infinitive"], inventory_message_it), TO.OTHERS, location)
            entity.act("$n cerca di %s [white]qualcosa[close], ma non sembra trovare [gray]nulla del genere[close]." % verbs["infinitive"], TO.TARGET, location)
        else:
            entity.act("Cerchi di %s [white]%s[close] a [white]%s[close], ma non trovi [gray]nulla e nessuno[close]." % (verbs["infinitive"], arg1, arg2), TO.ENTITY)
            entity.act("$n cerca di %s [white]qualcosa[close] a [white]quacuno[close], ma [gray]senza molti risultati[close]." % verbs["infinitive"], TO.OTHERS)
        return False

    # Gestisce i tre casi in cui le entità trovate siano uguali a quella che ha
    # inviato il comando
    if target == entity:
        if location == entity:
            entity.act("Cerchi di %s tutt$o [white]te stess$o[close] a... te stess$o!" % verbs["infinitive"], TO.ENTITY)
            entity.act("$n cerca di %s tutt$o [white]sé stess$o[close] a... sé stess$o!" % verbs["infinitive"], TO.OTHERS)
        else:
            entity.act("Cerchi di %s tutt$o [white]te stess$o[close] a $N..." % verbs["infinitive"], TO.ENTITY, location)
            entity.act("$n cerca di %s tutt$o [white]sé stess$o[close] a $N..." % verbs["infinitive"], TO.OTHERS, location)
            entity.act("$n cerca di %s tutt$o [white]sé stess$o[close] a te..." % verbs["infinitive"], TO.TARGET, location)
        return False
    else:
        if location == entity:
            entity.act("Ti [orange]passi[close] $N da una $hand all'altra.", TO.ENTITY, target)
            entity.act("$n si [orange]passa[close] $N da una $hand all'altra.", TO.OTHERS, target)
            entity.act("$n ti [orange]passa[close] da una $hand all'altra.", TO.TARGET, target)
            return False

    # Non si può seminare l'entità in sé stessa
    if target == location:
        entity.act("Cerchi di %s $N a [white]$LUI stess$O[close] senza molti risultati..." % verbs["infinitive"], TO.ENTITY, target)
        entity.act("$n cerca di %s $N a [white]$LUI stess$O[close] senza molti risultati..." % verbs["infinitive"], TO.OTHERS, target)
        entity.act("$n cerca di %s a [white]te stess$O[close] senza molti risultati..." % verbs["you2"], TO.TARGET, target)
        return False

    target_entitype = getattr(target, type_attr_name)

    # Se l'entità è una pianta avvisa che è il caso di utilizzare il comando apposito
    if command_name == "command_seed" and target.plant_type:
        from src.commands.command_plant import VERBS as PLANT_VERBS
        entity.act("Cerchi di %s $N ma faresti prima a %s." % (verbs["infinitive"], PLANT_VERBS["it2"]), TO.ENTITY, target)
        entity.act("$n cerca di %s $N ma farebbe prima a %s." % (verbs["infinitive"], PLANT_VERBS["it2"]), TO.OTHERS, target)
        entity.act("$n cerca di %s ma farebbe prima a %s." % (verbs["you2"], PLANT_VERBS["you2"]), TO.TARGET, target)
        return False

    # Come si può denotare invece è possibile seminare anche se l'entitype
    # non è valido interrando successivamente così l'entità
    if command_name == "command_plant" and not target_entitype:
        entity.act("Cerchi di %s $N che però non sembra essera affatto una pianta." % verbs["infinitive"], TO.ENTITY, target)
        entity.act("$n cerca di %s $N che però non sembra affatto essere una pianta." % verbs["infinitive"], TO.OTHERS, target)
        entity.act("$n cerca di %s, ma tu sai di non essere una pianta." % verbs["you2"], TO.TARGET, target)
        return False

    ground = None
    if location.IS_ROOM:
        if (target_entitype and (target_entitype.sectors and location.sector not in target_entitype.sectors
                                 or not target_entitype.sectors and not location.sector.fertile)):
            entity.act("Cerchi di %s $N tuttavia il terreno non sembra essere adatto." % verbs["infinitive"], TO.ENTITY, target)
            entity.act("$n cerca di %s $N tuttavia il terreno non sembra essere adatto." % verbs["infinitive"], TO.OTHERS, target)
            entity.act("$n cerca di %s, tuttavia il terreno non sembra essere addato." % verbs["you2"], TO.TARGET, target)
            return False
    elif location.container_type:
        for contains in location.iter_contains():
            if contains.entitype == ENTITYPE.GROUND:
                ground = contains
                break
        else:
            entity.act("Cerchi di %s $N tuttavia non trovi del terreno adatto." % verbs["infinitive"], TO.ENTITY, target)
            entity.act("$n cerca di %s $N tuttavia non trova del terreno terreno adatto." % verbs["infinitive"], TO.OTHERS, target)
            entity.act("$n cerca di %s, tuttavia non trova del terreno addato." % verbs["you2"], TO.TARGET, target)
            return False
    elif location.entitype == ENTITYPE.GROUND:
        ground = location
    else:
        entity.act("Cerchi di %s $N tuttavia non trovi del terreno adatto." % verbs["infinitive"], TO.ENTITY, target)
        entity.act("$n cerca di %s $N tuttavia non trova del terreno terreno adatto." % verbs["infinitive"], TO.OTHERS, target)
        entity.act("$n cerca di %s, tuttavia non trova del terreno addato." % verbs["you2"], TO.TARGET, target)
        return False

    if ground:
        # Evita di far attecchire piante in un  terreno se questo ha già un seme
        # o una pianta in crescita
        for contains in ground.iter_contains():
            # E' voluto che vi siano potenzialmente più plant_type in uno
            # stesso terreno, ma non più ENTITYPE.PLANT; stesso discorso
            # con l'ENTITYPE.SEED
            if contains.entitype == ENTITYPE.PLANT:
                entity.act("Cerchi di %s $N tuttavia vi è già $a e non riuscirebbe ad attecchire in $A." % verbs["infinitive"], TO.ENTITY, target, contains, ground)
                entity.act("$n cerca di %s $N tuttavia vi è già $a e non riuscirebbe ad attecchire in $A." % verbs["infinitive"], TO.OTHERS, target, contains, ground)
                entity.act("$n cerca di %s, tuttavia vi è già $a e non riuscirebbe ad attecchire in $A." % verbs["you2"], TO.TARGET, target, contains, ground)
                return False
            elif contains.entitype == ENTITYPE.SEED:
                entity.act("Cerchi di %s $N tuttavia noti che qui è già stato %s qualcosa." % (verbs["infinitive"], verbs["infinitive"]), TO.ENTITY, target)
                entity.act("$n cerca di %s $N tuttavia nota che qui è già stato %s qualcosa." % (verbs["infinitive"], verbs["infinitive"]), TO.OTHERS, target)
                entity.act("$n cerca di %s, tuttavia nota che qui è già stato %s qualcosa." % (verbs["you2"], verbs["infinitive"]), TO.TARGET, target)
                return False
    else:
        # Per le staze invece il massimo piantabile è il numero i metri quadri
        # della stanza meno il numero di oggetti già contenuti (visivamente,
        # quindi mucchi di più oggetti valgono uno)
        measured_area = (location.width * location.depth) / 100
        if len(location.get_list_of_entities(entity)) >= measured_area:
            entity.act("Cerchi di %s $N ma non hai spazio ove metterla." % verbs["infinitive"], TO.ENTITY, target)
            entity.act("$n cerca di %s $N ma non hai spazio ove metterla." % verbs["infinitive"], TO.OTHERS, target)
            entity.act("$n cerca di %s, ma non hai spazio ove metterla." % verbs["you2"], TO.TARGET, target)
            return False

    force_return = check_trigger(entity, "before_" + gamescript_suffix, entity, target, location, ground, behavioured)
    if force_return:
        return True
    force_return = check_trigger(target, "before_" + gamescript_suffix + "ed", entity, target, location, ground, behavioured)
    if force_return:
        return True
    force_return = check_trigger(location, "before_" + gamescript_suffix + "ing_in_location", entity, target, location, ground, behavioured)
    if force_return:
        return True

    if inventory_message_you and inventory_message_it:
        entity.act("%s $N in $a%s." % (color_first_upper(verbs["you"]), inventory_message_you[ : -1]), TO.ENTITY, target, location)
        entity.act("$n %s $N in $a%s." % (verbs["it"], inventory_message_it[ : -1]), TO.OTHERS, target, location)
        entity.act("$n ti %s in $a%s." % (verbs["it"], inventory_message_it[ : -1]), TO.TARGET, target, location)
        entity.act("$n ti %s $a." % verbs["it"], TO.TARGET, location, target)
    else:
        entity.act("%s $N in $a." % color_first_upper(verbs["you"]), TO.ENTITY, target, location)
        entity.act("$n %s $N in $a." % verbs["it"], TO.OTHERS, target, location)
        entity.act("$n ti %s in $a." % verbs["it"], TO.TARGET, target, location)
        entity.act("$n ti %s $a." % verbs["it"], TO.TARGET, location, target)

    target = target.from_location(1, use_repop=True)
    if ground:
        # Se esiste del ground per la pianta questa attecchisce in esso
        if not ground.container_type:
            # (TD) scelta tecnica di dubbia qualità, da ripensare forse, è certo
            # che se viene cambiata è da rivedere il check nell'iter_variant
            container = Container()
            container.max_weight = target.get_total_weight() * 2
            ground.container_type = container
        target.to_location(ground)
    else:
        target.to_location(location)
    target.flags += FLAG.BURIED
    if target_entitype:
        target.flags += FLAG.GROWING
        target_entitype.start_growth(target, type_attr_name)

    # Dona un po' di esperienza ai giocatori che hanno piantato o seminato
    # la prima volta l'entità
    if entity.IS_PLAYER:
        if target.prototype.code in entity.interred_entities:
            entity.interred_entities[target.prototype.code] += 1
        else:
            entity.interred_entities[target.prototype.code] = 1
            reason = "per aver interrato per la prima volta %s" % target.get_name(looker=entity)
            entity.give_experience(target.level*10, reason=reason)

    force_return = check_trigger(entity, "after_" + gamescript_suffix, entity, target, location, ground, behavioured)
    if force_return:
        return True
    force_return = check_trigger(target, "after_" + gamescript_suffix + "ed", entity, target, location, ground, behavioured)
    if force_return:
        return True
    force_return = check_trigger(location, "after_" + gamescript_suffix + "ing_in_location", entity, target, location, ground, behavioured)
    if force_return:
        return True

    return True
#- Fine Funzione -
