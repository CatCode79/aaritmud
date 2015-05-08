# -*- coding: utf-8 -*-


#= IMPORT ======================================================================

import weakref

from src.color      import color_first_upper
from src.config     import config
from src.command    import get_command_syntax
from src.enums      import FLAG, OPTION, PART, TO, WEAR
from src.gamescript import check_trigger
from src.interpret  import translate_input
from src.log        import log
from src.part       import check_if_part_is_already_weared, get_part_descriptions
from src.utility    import is_same, one_argument

from src.entitypes.wear import send_wear_messages

if config.reload_commands:
    reload(__import__("src.commands.command_hold", globals(), locals(), [""]))
    reload(__import__("src.commands.command_wield", globals(), locals(), [""]))
from src.commands.command_hold import command_hold
from src.commands.command_wield import command_wield


#= COSTANTI ====================================================================

VERBS = {"infinitive" : "[khaki]indossare[close]",
         "participle" : "[khaki]indossato[close]",
         "you2"       : "[khaki]indossarti[close]",
         "you"        : "[khaki]indossi[close]",
         "it"         : "[khaki]indossa[close]"}


#= FUNZIONI ====================================================================

def command_wear(entity, argument="", verbs=VERBS, behavioured=False):
    """
    Permette di vestirsi di entità nelle varie parti del corpo.
    """
    if not verbs:
        log.bug("verbs non è un parametro valido: %r" % verbs)
        return False

    # -------------------------------------------------------------------------

    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    entity = entity.split_entity(1)

    if not argument:
        entity.send_output("Che cosa vorresti %s?" % verbs["infinitive"])
        if entity.IS_PLAYER and OPTION.NEWBIE in entity.account.options:
            syntax = get_command_syntax(entity, "command_wear")
            entity.send_output(syntax, break_line=False)
        return False

    # (TD) Controllo del mental state deviato
    pass

    # (TD) gestione di all (ti vesti di tutto punto: elenco delle cose indossate)
    pass

    original_argument = argument
    arg, argument = one_argument(argument)
    target = entity.find_entity(arg, location=entity)
    if not target:
        entity.act("Non hai nessun [white]%s[close] nel tuo inventario." % arg, TO.ENTITY)
        entity.act("$n sembra frugare nel suo inventario cercando inutilmente qualcosa.", TO.OTHERS)
        return False

    if target == entity:
        entity.act("Cerchi di %s da sol$o ma... sei sicur$o di quello che stai facendo?" % verbs["you2"], TO.ENTITY)
        entity.act("$n sembra volersi %s da sol$o... Fa finta di non aver visto nulla!" % verbs["infinitive"], TO.OTHERS)
        return False

    chosen_part = None
    if not argument:
        if not target.wear_type:
            entity.act("Non vedi come poter %s $N." % verbs["infinitive"], TO.ENTITY, target)
            entity.act("$n cerca di %s $N ma senza grossi risultati." % verbs["infinitive"], TO.OTHERS, target)
            return False
    else:
        # (TD) Scelta personalizzata della parte da vestire e/o di chi vestire
        #chosen_part = search_part(argument)
        pass

    # (TD) bisognerà fare il supporto body anche per gli oggetti con le proprie parti
    body_parts = entity.get_body_parts()
    if not body_parts and not entity.IS_ITEM:
        log.bug("body_parts non valido per l'entità %s di razza %s" % (entity.code, entity.race))
        return False

    # Ricava la modalità di wear uscendo dal comando se al corpo dell'entità
    # gli mancano delle parti per poter indossare target oppure se l'entità ha
    # già indossato qualcosa
    chosen_mode = None
    already_used_possession = None
    for cycle in ("free", "layarable"):
        for mode in target.wear_type.modes:
            incompatible_part = None
            already_weared_part = None
            # Scorre tra le parti della modalità di wear per controllare discrepanze
            # tra le parti del corpo della razza e quelle dell'entità da indossare
            for part in mode:
                if body_parts and part not in body_parts:
                    incompatible_part = part
                    break
            if incompatible_part:
                continue

            # Supporto friendly per l'hold e il wield, così si possono impugnare o
            # tenere entità anche tramite il comando wear
            if PART.HOLD in mode:
                return command_hold(entity, original_argument)
            if PART.WIELD in mode:
                return command_wield(entity, original_argument)

            # Qui sotto c'è un altro ciclo uguale a quello sopra per dare
            # maggiore priorità alle differenze razziali rispetto alle parti
            # già indossate
            for part in mode:
                already_weared_part, already_weared_possession = check_if_part_is_already_weared(entity, part)
                if already_weared_part:
                    break
            # Se non ha trovato nessuna parte già indossata allora utilizza
            # questa modalità di wear ed esce dal ciclo delle modalità
            if not already_weared_possession or (cycle == "layarable" and already_weared_possession.is_layerable()):
                chosen_mode = mode
                break
        if chosen_mode:
            break

    if incompatible_part:
        # (TT) è stato deciso per ora di nascondere la parte del corpo per cui
        # non si può indossare il vestito
        #entity.act("Il tuo corpo non è adatto a poter indossare $N, ti manca %s." % incompatible_part, TO.ENTITY, target)
        entity.act("Il tuo corpo non è adatto a poter %s $N." % verbs["infinitive"], TO.ENTITY, target)
        entity.act("Il corpo di $n non è adatto a poter %s $N." % verbs["infinitive"], TO.OTHERS, target)
        return False

    if already_weared_possession and not already_weared_possession.is_layerable():
        entity.act("Cerchi di %s $N %s ma hai già indosso $a." % (verbs["infinitive"], already_weared_part.description), TO.ENTITY, target, already_weared_possession)
        entity.act("$n cerca di %s $N %s ma ha già indosso $a." % (verbs["infinitive"], already_weared_part.description), TO.OTHERS, target, already_weared_possession)
        return False

    # (TD) Aggiungere la flag di NO_WEAR (se la location ha la flag NO_WEAR
    # anche il contenuto non potrà indossare, questo è da fare in vista del
    # sistema generico entità-stanze)
    pass

    force_return = check_trigger(entity, "before_wear", entity, target, chosen_part, chosen_mode, behavioured)
    if force_return:
        return True
    force_return = check_trigger(target, "before_weared", entity, target, chosen_part, chosen_mode, behavioured)
    if force_return:
        return True

    if FLAG.INGESTED in target.flags:
        if entity.trust >= TRUST.MASTER:
            entity.send_to_admin("%s %s anche se lo stai digerendo." % (verbs["you"], target.get_name(entity)))
        else:
            log.bug("I giocatori non dovrebbero poter manipolare oggetti ingeriti")
            entity.send_output("[cyan]Errore di digestione nel comando, gli amministratori sono stati avvertiti del problema.[close]")
            return False
        target.stop_digestion()

    target.wear_mode.clear()
    for part in chosen_mode:
        target.wear_mode += part
    if already_weared_possession:
        target.under_weared = weakref.ref(already_weared_possession)
        # Forza il posizionamento di target prima di already_weared_possession
        # così che nelle manipolazioni venga prima quella sovrastante
        list_of_target = getattr(entity, target.ACCESS_ATTR)
        index = list_of_target.index(already_weared_possession)
        if index != -1:
            list_of_target.remove(target)
            list_of_target.insert(index, target)

    for affect in target.affects:
        affect.apply()

    # Poiché l'entità è stata vestita forse ha un valore nel gioco e non
    # verrà quindi purificata
    if target.deferred_purification:
        target.stop_purification()

    # Serve a cambiare il wear mode dell'oggetto allo stato originario
    if target.repop_later:
        target.deferred_repop = target.repop_later.defer_check_status()

    part_descriptions = get_part_descriptions(target, "wear", entity, entity)
    # (TD) estendere il verb a tutti i verbi degli act da inizio comando
    send_wear_messages(entity, target, color_first_upper(verbs["you"]), verbs["it"], part_descriptions)

    force_return = check_trigger(entity, "after_wear", entity, target, chosen_part, chosen_mode, behavioured)
    if force_return:
        return True
    force_return = check_trigger(target, "after_weared", entity, target, chosen_part, chosen_mode, behavioured)
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
    syntax += "wear <nome oggetto o creatura>\n"
    #syntax += "wear <nome oggetto o creatura> <nome parte in cui indossarla>\n"

    return syntax
#- Fine Funzione -
