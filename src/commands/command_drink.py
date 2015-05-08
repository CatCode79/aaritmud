# -*- coding: utf-8 -*-

"""
Modulo per la gestione del comando drink.
"""


#= IMPORT ======================================================================

from src.command    import get_command_syntax
from src.enums      import FLAG, OPTION, TRUST, TO
from src.gamescript import check_trigger
from src.interpret  import send_input
from src.log        import log
from src.utility    import is_prefix, multiple_arguments

from src.loops.digestion import digestion_loop


#= COSTANTI ====================================================================

VERBS = {"infinitive" : "bere",
         "you"        : "bevi",
         "you2"       : "berti",
         "it"         : "beve"}


#= FUNZIONI ====================================================================

# (TD) aggiungere il check_trigger
def command_drink(entity, argument="", verbs=VERBS, behavioured=False):
    """
    Comando che serve per mangiare un entità.
    """
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    entity = entity.split_entity(1)

    # (TD) controllo sulle posizioni, possibilità di muovere la bocca come
    # per bere nel sonno

    if not argument:
        entity.send_output("Cosa vorresti %s?" % verbs["infinitive"])
        if entity.IS_PLAYER and OPTION.NEWBIE in entity.account.options:
            syntax = get_command_syntax(entity, "command_eat")
            entity.send_output(syntax, break_line=False)
        return False

    # (TD) futura ricerca allucinogena, se si è pazzi è difficile trovare
    # qualsiasi entità, probabilmente il sistema verrà integrato nel metodo
    # find_entity

    # Cerca l'entità da bere prima nel proprio inventario e poi utilizza
    # il comando get per prendere la bevanda da qualsiasi altra parte
    target = entity.find_entity(argument, location=entity)
    if not target:
        # (TD) Manca la ricerca se il cibo si trova dentro o sopra target, da fare
        # quando ci saranno i contenitori e quando le entità si potranno appoggiare
        entity.act("Non trovi nessun [white]%s[close] da poter %s." % (argument, verbs["infinitive"]), TO.ENTITY)
        entity.act("$n si guarda attorno cercando qualcosa." % verbs["infinitive"], TO.OTHERS)
        return False

    # Ricava il peso di un morso in proporzione al proprio, viene ricavato
    # un peso in grammi. Il pezzo è più grande se si sta divorando
    if devours:
        bite_weight = entity.weight / 50
    else:
        bite_weight = entity.weight / 100
    if target.weight < bite_weight:
        bite_weight = target.weight

    # Ricava il peso di quello che si può ingerire prima di non sentire più fame
    # il doppio di questo valore è il peso massimo che lo stomaco può sopportare
    # In sostanza per ogni 50kg di peso proprio si suppone che prima di non
    # sentire più fame bisogna ingerire 1kg, viene ricavato un peso in grammi
    eatable_weight = entity.weight * 1000 / 50000

    # Ricava il peso delle cose ingerite
    eated_weight = 0
    for something in entity.iter_contains():
        if FLAG.INGESTED in something.flags:
            eated_weight += something.weight

    if eated_weight + bite_weight > eatable_weight * 2:
        if entity.trust >= TRUST.MASTER:
            entity.send_to_admin("Mangi l'entità nonostante tu abbia la pancia piena")
        else:
            entity.act("Hai la pancia troppo piena per riuscire ad ingurgitare $N.", TO.ENTITY, target)
            entity.act("$n cerca di %s $N, ma sembra che abbia la pancia piena." % verbs["infinitive"], TO.OTHERS, target)
            entity.act("$n cerca di %s, ma sembra che abbia la pancia piena." % verbs["you2"], TO.TARGET, target)
            return False

    # Se l'entità non è un cibo allora si comporta in maniera differente a
    # seconda della tipologia della stessa
    if not target.food_type:
        if target == entity:
            input = "nail %s" % target.get_numbered_keyword(looker=entity)
            send_input(entity, input, "en", show_input=False, show_prompt=False)
            return True
        elif target.IS_ACTOR:
            input = "nibble %s" % target.get_numbered_keyword(looker=entity)
            send_input(entity, input, "en", show_input=False, show_prompt=False)
            return True
        else:
            if target.weight > bite_weight:
                if entity.trust == TRUST.PLAYER :
                    entity.act("Cerchi di %s $N ma ti rendi conto che è troppo grande da ingoiare." % verbs["infinitive"], TO.ENTITY, target)
                    entity.act("$n cerca di %s $N ma senza grossi risultati..." % verbs["infinitive"], TO.OTHERS, target)
                    entity.act("$n cerca di %s... Ouch!" % verbs["you2"], TO.TARGET, target)
                    return False
                else:
                    entity.send_to_admin("Ingoi quest'oggetto nonostante sia troppo grande")
            entity.act("%s $N"    % verbs["you"], TO.ENTITY, target)
            entity.act("$n %s $N" % verbs["it"], TO.OTHERS, target)
            entity.act("$n ti %s" % verbs["it"], TO.TARGET, target)
            digestion_loop.add(entity, target)
            return True

    # (TD) Splitting di un oggetto da un gruppo di oggetti

    # (TD) Probabilità che il cibo cada per terra se si sta combattimento

    # Controlla se l'entità segue la dieta necessaria per mangiare target.
    # Se sta divorando non si guarda per il sottile e si mangia un po' di tutto
    if devours:
        acceptability = 50
    else:
        acceptability = 25
    if FLAG.CARNIVOROUS in entity.flags and target.food_type.vegetable >= acceptability:
        entity.act("Non puoi %s $N, è fatto più d'erba che carne!" % verbs["infinitive"], TO.ENTITY, target)
        entity.act("$n guarda perpless$o $N, sembra che non $gli vada a genio...", TO.OTHERS, target)
        entity.act("$n ti guarda perpless$o, sembra che non $gli vai a genio...", TO.TARGET, target)
        return False
    elif FLAG.HERBIVORE in entity.flags and target.food_type.animal >= acceptability:
        entity.act("Non puoi %s $N, è fatto più di sangue che di vegetali!" % verbs["infinitive"], TO.ENTITY, target)
        entity.act("$n guarda perpless$o $N, sembra che non $gli vada a genio...", TO.OTHERS, target)
        entity.act("$n ti guarda perpless$o, sembra che non $gli vai a genio...", TO.TARGET, target)
        return False

    # Diminuisce la fame di una certa percentuale pari al peso mangiato rispetto
    # a quello ingeribile.
    # (TD) Tutto da rifare, la hunger sarà un effetto, verrà presa una
    # percentuale dell'effetto a seconda della grandezza del morso
    # (TD) A seconda delle condizioni e delle ore passate il cibo
    # ha più o meno consistenza o è più o meno mangiabile
    if entity.IS_ACTOR:
        entity.hunger -= (bite_weight * 100 / eatable_weight) * 2
        if entity.hunger < 0:
            entity.hunger = 0

    # I messaggi devono essere visualizzati solo dopo aver diminuito la hunger
    target.food_type.send_messages(entity, target, verbs)

    # Viene visualizza l'eventuale descrizione del gusto, ma solo se non si sta
    # mangiando normalmente
    if not devours:
        # Anche qui l'eat scatena il gamescript before_taste e after_taste
        descr = target.get_descr("taste", looker=entity)
        if descr:
            entity.send_output('''<div style="width:66%%">%s</div>''' % descr)

    # Inserisce l'oggetto nello stomaco e ne inizia la digestione
    # (TD) le cose bevute vanno estratte e non digerite, al limite ne rimane
    # il contenitore, cosa da fare anche per i food
    digestion_loop.add(entity, target)

    # (TD) aggiunta degli effetti del cibo sul giocatore

    # (TD) social vomito e rimozione di alcuni oggetti dallo stomaco
    #if eated_weight + bite_weight == eatable_weight * 2:
        # pass
    if eated_weight + bite_weight > eatable_weight * 1.5:
        entity.act("Il tuo stomaco è scosso da degli spasmi... Sei pien$o!", TO.ENTITY, target)
        entity.act("$n si tiene la pancia con una $hand... Che abbia %sto troppo?" % verbs["it"], TO.OTHERS, target)
        entity.act("Puoi constatare in prima persona che lo stomaco di $n è pieno.", TO.TARGET, target)
    elif not devours and eated_weight + bite_weight > eatable_weight:
        # Se si sta divorando in fretta non si lascia il tempo di capire che sta arrivando la nausea
        entity.act("Comincia a venirti una certa nausea per il cibo... Sei quasi pien$o!", TO.ENTITY, target)
        entity.act("$n si passa una $hand sullo stomaco... Che sia ormai sazi$o?", TO.OTHERS, target)
        entity.act("Puoi constatare in prima persona che lo stomaco di $n è quasi pieno.", TO.TARGET, target)

    if entity.IS_PLAYER:
        if target.prototype.code in entity.drinked_entities:
            entity.drinked_entities[target.prototype.code] += 1
        else:
            entity.drinked_entities[target.prototype.code] = 1
            reason = "per aver bevuto per la prima volta %s" % target.get_name(looker=entity)
            entity.give_experience(target.level, reason=reason)

    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""

    syntax += "eat\n"
    syntax += "eat <qualcuno o qualcosa>\n"

    return syntax
#- Fine Funzione -
