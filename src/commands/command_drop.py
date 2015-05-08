# -*- coding: utf-8 -*-

# (TD) il drop all deve far cascare tutti gli oggetti no look list, per far evitare che i pg si riempiano

#= IMPORT ======================================================================

from src.color      import color_first_upper
from src.command    import get_command_syntax
from src.enums      import FLAG, OPTION, ROOM, TO, TRUST
from src.gamescript import check_trigger
from src.log        import log
from src.utility    import is_prefix, one_argument, quantity_argument


#= COSTANTI ====================================================================

VERBS = {}
VERBS["infinitive"] = "[orange]posare[close]"
VERBS["noun"]       = "[orange]posarlo[close]"
VERBS["you"]        = "[orange]posi[close]"
VERBS["you2"]       = "[orange]posarti[close]"
VERBS["it"]         = "[orange]posa[close]"

VERBS2 = {}
VERBS2["infinitive"] = "[brown]abbandonare[close]"
VERBS2["noun"]       = "[brown]abbandonarlo[close]"
VERBS2["you"]        = "[brown]abbandoni[close]"
VERBS2["you2"]       = "[brown]abbandonarti[close]"
VERBS2["it"]         = "[brown]abbandona[close]"


#= FUNZIONI ====================================================================

def command_drop(entity, argument="", verbs=VERBS, behavioured=False):
    """
    Permette di abbandonare oggetti per terra oppure posarli in un luogo preciso.
    """
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    entity = entity.split_entity(1)

    if entity.sended_inputs and is_prefix("abbandon", entity.sended_inputs[-1]):
        verbs = VERBS2

    if not argument:
        entity.send_output("Che cosa vorresti %s." % verbs["infinitive"])
        if entity.IS_PLAYER and OPTION.NEWBIE in entity.account.options:
            syntax = get_command_syntax(entity, "command_drop")
            entity.send_output(syntax, break_line=False)
        return False

    # Ricava l'eventuale quantità d'oggetti da posare
    quantity, argument = quantity_argument(argument)

    # (TD) Controllo del mental state deviato

    # Ricerca dell'oggetto nell'inventario, non viene utilizzata la extended
    target = entity.find_entity(argument, quantity=quantity, location=entity)
    if not target:
        entity.act("Non riesci a trovare nessun [white]%s[close] da poter %s." % (argument, verbs["infinitive"]), TO.ENTITY)
        entity.act("$n sembra cercare qualcosa ma senza risultato.", TO.OTHERS)
        return False

    if quantity == 0:
        quantity = target.quantity
    elif target.quantity < quantity:
        entity.act("Non puoi %s $N perché ne hai solo %d e non %d." % (verbs["infinitive"], target.quantity, quantity), TO.ENTITY, target)
        entity.act("$n sta cercando di ammucchiare un quantitativo voluto di $N per poterlo %s" % verbs["infinitive"], TO.OTHERS, target)
        entity.act("$n sta cercando di ammucchiarti per un quantitativo voluto per poterti %s" % verbs["infinitive"], TO.TARGET, target)
        return False

    if FLAG.NO_DROP in target.flags:
        if entity.trust > TRUST.MASTER:
            entity.send_to_admin("Questa sarebbe in realtà un'entità NO_DROP e non potresti lasciarla")
        else:
            entity.act("Appena cerchi di %s $N te lo ritrovi, con un balzo, in $hand." % verbs["infinitive"], TO.ENTITY, target)
            entity.act("Appena $n cerca di %s $N se lo ritrova, con un balzo, in $hand." % verbs["infinitive"], TO.OTHERS, target)
            entity.act("\nAppena $n cerca di %s gli ritorni in $hand con un balzo." % verbs["you2"], TO.TARGET, target)
            return False

    # Non permette di droppare oggetti nelle stanze con flag di NO_DROP
    if entity.location.IS_ROOM and ROOM.NO_DROP in entity.location.flags:
        if entity.trust > TRUST.MASTER:
            entity.send_to_admin("Questa sarebbe in realtà una stanza NO_DROP in cui non poter lasciar entità")
        else:
            entity.act("Appena %s $N te lo ritrovi in %hand come se una [royalblue]forza misteriosa[close] nel luogo ti impedisse quest'azione!" % verbs["you"], TO.ENTITY, target)
            entity.act("Appena $n lascia andare $N, con l'intenzione di %s, se lo ritrova in $hand come se vi fosse una [royalblue]forza misteriosa[close] nel luogo!" % verbs["noun"], TO.OTHERS, target)
            entity.act("\nAppena $n ti %s ritorni nella sua $hand grazie ad una [royalblue]forza misteriosa[close] del luogo!" % verbs["it"], TO.TARGET, target)
            return False

    # (TD) posare monete

    # (TD) argomento all, ultima cosa da supportare

    # Ricava la locazione in cui posare l'oggetto
    # (TD)
    location = entity.location

    force_return = check_trigger(entity, "before_drop", entity, target, location, behavioured)
    if force_return:
        return True
    force_return = check_trigger(target, "before_dropped", entity, target, location, behavioured)
    if force_return:
        return True
    force_return = check_trigger(location, "before_drop_from_location", entity, target, location, behavioured)
    if force_return:
        return True

    entity.act("%s $N in $l." % color_first_upper(verbs["you"]), TO.ENTITY, target)
    entity.act("$n %s $N in $l." % verbs["it"], TO.OTHERS, target)
    entity.act("$n ti %s in $l." % verbs["it"], TO.TARGET, target)
    if not location.IS_ROOM:
        entity.act("$n ti %s qualcosa." % verbs["it"], TO.TARGET, location)

    if FLAG.INGESTED in target.flags:
        if entity.trust >= TRUST.MASTER:
            entity.send_to_admin("%s %s anche se lo stai digerendo." % (verbs["you"], target.get_name(entity)))
        else:
            log.bug("I giocatori non dovrebbero poter manipolare oggetti ingeriti")
            entity.send_output("[cyan]Errore di digestione nel comando, gli amministratori sono stati avvertiti del problema.[close]")
            return False
        target.stop_digestion()

    target = target.from_location(quantity, use_repop=True)
    target.to_location(location)

    force_return = check_trigger(entity, "after_drop", entity, target, location, behavioured)
    if force_return:
        return True
    force_return = check_trigger(target, "after_dropped", entity, target, location, behavioured)
    if force_return:
        return True
    force_return = check_trigger(location, "after_drop_from_location", entity, target, location, behavioured)
    if force_return:
        return True

    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""
    syntax += "drop <nome oggetto o creatura>\n"
    syntax += "drop <nome oggetto o creatura> <luogo in cui posarla>\n"

    return syntax
#- Fine Funzione -
