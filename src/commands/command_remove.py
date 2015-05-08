# -*- coding: utf-8 -*-


#= IMPORT ======================================================================

from src.color      import color_first_upper
from src.command    import get_command_syntax
from src.config     import config
from src.enums      import FLAG, OPTION, PART, TO, TRUST
from src.gamescript import check_trigger
from src.grammar    import is_masculine
from src.interpret  import translate_input
from src.log        import log
from src.part       import get_part_descriptions
from src.utility    import is_same, one_argument

from src.entitypes.wear import send_remove_messages


#= COSTANTI ====================================================================

VERBS = {"infinitive" : "[feldspar]togliere[close]",
         "you2"       : "[feldspar]toglierti[close]",
         "you"        : "[feldspar]togli[close]",
         "it"         : "[feldspar]toglie[close]",
         "self"       : "[feldspar]togliersi[close]",
         "participle" : "[feldspar]tolto[close]"}


#= FUNZIONI ====================================================================

def command_remove(entity, argument="", verbs=VERBS, behavioured=False):
    """
    Permette di vestirsi di entità nelle varie parti del corpo.
    """
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    entity = entity.split_entity(1)

    if not argument:
        entity.send_output("Che cosa vorresti %s di dosso?" % verbs["you2"])
        if entity.IS_PLAYER and OPTION.NEWBIE in entity.account.options:
            syntax = get_command_syntax(entity, "command_remove")
            entity.send_output(syntax)
        return False

    # (TD) Controllo del mental state deviato
    pass

    # (TD) gestione di all (ti vesti di tutto punto: elenco delle cose indossate)
    pass

    location = None
    arg, argument = one_argument(argument)
    if argument:
        location = entity.find_entity(argument)
        if not location:
            entity.send_output("Non è stato trovato nessun %s da cui %s %s." % (argument, verbs["infinitive"], arg))
            return False
        target = entity.find_equipped_entity(arg, location)
    else:
        target = entity.find_equipped_entity(arg, entity)

    if not target:
        if is_masculine(arg):
            descr = "indossato"
        else:
            descr = "indossata"
        entity.act("Non hai nessun [white]%s[close] %s." % (arg, descr), TO.ENTITY)
        entity.act("$n sembra cercare qualche cosa che ha addosso.", TO.OTHERS)
        return False

    if target == entity:
        entity.act("Cerchi di %s di dosso ma... sei sicur$o di quello che stai facendo?" % verbs["you2"], TO.ENTITY)
        entity.act("$n sembra volersi %s di dosso... Ma che sta facendo?" % verbs["infinitive"], TO.OTHERS)
        return False

    if location and location != entity and location.IS_ACTOR:
        entity.send_output("Non ti è possibile %s %s da %s." % (verbs["infinitive"], targetget_name(looker=entity), location.get_name(looker=entity)))
        return False

    if FLAG.NO_REMOVE in target.flags:
        if entity.trust > TRUST.MASTER:
            entity.send_output("{Questa sarebbe in realtà un'entità NO_REMOVE}")
        else:
            entity.act("Appena cerchi di %s $N ti accorgi di non poterlo fare." % verbs["infinitive"], TO.ENTITY, target)
            entity.act("Appena $n cerca di %s $N si accorge di non poterlo fare." % verbs["infinitive"], TO.OTHERS, target)
            entity.act("\nAppena $n cerca di %s si accorge di non riuscirci." % verbs["you2"], TO.TARGET, target)
            return False

        # (TT) nel caso si sviluppino stanze no remove qui ci va il chk opportuno

    if target.wear_type:
        upper_weared = target.wear_type.get_upper_weared(target)
        if upper_weared:
            entity.act("Devi %s prima $a di $N." % verbs["you2"], TO.ENTITY, target, upper_weared)
            entity.act("$n cerca di %s $N senza prima essersi %s $a." % (verbs["self"], verbs["participle"]), TO.OTHERS, target, upper_weared)
            entity.act("$n cerca di %s senza prima essersi %s $a." % (verbs["you2"], verbs["participle"]), TO.TARGET, target, upper_weared)
            entity.act("$n cerca di %s $N senza prima %s." % (verbs["self"], verbs["you2"]), TO.TARGET, target, upper_weared)
            return False

    chosen_part = None
    if argument:
        # (TD) rimuovere un'entità da una parte del corpo precisa
        #chosen_part = search_part(argument)
        pass

    if config.reload_commands:
        reload(__import__("src.commands.command_hold", globals(), locals(), [""]))
        reload(__import__("src.commands.command_wield", globals(), locals(), [""]))
        reload(__import__("src.commands.command_wear", globals(), locals(), [""]))
    from src.commands.command_hold  import VERBS as hold_verbs
    from src.commands.command_wield import VERBS as wield_verbs
    from src.commands.command_wear  import VERBS as wear_verbs

    force_return = check_trigger(entity, "before_remove", entity, target, location, chosen_part, behavioured)
    if force_return:
        return True
    force_return = check_trigger(target, "before_removed", entity, target, location, chosen_part, behavioured)
    if force_return:
        return True

    # Fare il sistema messaggistica proprio di tutti gli entitype
    # (TD) estendere il sistema di verb dall'inizio del comando
    part_descriptions = get_part_descriptions(target, "remove", entity, entity)
    if PART.HOLD in target.wear_mode or PART.WIELD in target.wear_mode:
        if target.weapon_type:
            if entity == target.location:
                part_descriptions[TO.ENTITY].replace(wield_verbs["participle"] + " ", "")
                part_descriptions[TO.OTHERS].replace(wield_verbs["participle"] + " ", "")
                part_descriptions[TO.TARGET].replace(wield_verbs["participle"] + " ", "")
                send_remove_messages(entity, target, "Smetti d'" + wield_verbs["infinitive_min"], "smette d'" + wield_verbs["infinitive_min"], part_descriptions, True)
            else:
                part_descriptions[TO.ENTITY] = "da $L"
                part_descriptions[TO.OTHERS] = "da $L"
                part_descriptions[TO.TARGET] = "da $L"
                send_remove_messages(entity, target, color_first_upper(verbs["you_min"]), verbs["it_min"], part_descriptions, True)
        else:
            if entity == target.location:
                part_descriptions[TO.ENTITY].replace(hold_verbs["participle"] + " ", "")
                part_descriptions[TO.OTHERS].replace(hold_verbs["participle"] + " ", "")
                part_descriptions[TO.TARGET].replace(hold_verbs["participle"] + " ", "")
                send_remove_messages(entity, target, "Smetti di " + hold_verbs["infinitive_min"], "smette di " + hold_verbs["infinitive_min"], part_descriptions, True)
            else:
                part_descriptions[TO.ENTITY] = "da $L"
                part_descriptions[TO.OTHERS] = "da $L"
                part_descriptions[TO.TARGET] = "da $L"
                send_remove_messages(entity, target, color_first_upper(verbs["you_min"]), verbs["it_min"], part_descriptions, True)
    else:
        if entity == target.location:
            send_remove_messages(entity, target, "Smetti d'" + wear_verbs["infinitive"], "smette d'" + wear_verbs["infinitive"], part_descriptions, False)
        else:
            part_descriptions[TO.ENTITY] = "da $L"
            part_descriptions[TO.OTHERS] = "da $L"
            part_descriptions[TO.TARGET] = "da $L"
            send_remove_messages(entity, target, color_first_upper(verbs["you"]), verbs["it"], part_descriptions, False)
    target.wear_mode.clear()
    target.under_weared = None
    if upper_weared:
        upper_weared.under_weared = None

    # Rimuove tutti gli affect che target stava applicando
    for affect in target.affects:
        affect.remove()

    # Per oggetti rimossi ad altri oggetti li mette per terra, questo perché
    # forza a raccoglierli, facendo scattare eventuali gamescript o altre flag
    if location:
        target = target.from_location(1, use_repop=False)
        target.to_location(location.location)

    # Serve a cambiare il wear mode dell'oggetto allo stato originario
    if target.repop_later:
        target.deferred_repop = target.repop_later.defer_check_status()

    force_return = check_trigger(entity, "after_remove", entity, target, location, chosen_part, behavioured)
    if force_return:
        return True
    force_return = check_trigger(target, "after_removed", entity, target, location, chosen_part, behavioured)
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
    syntax += "remove <nome oggetto o creatura>\n"
    syntax += "remove <nome oggetto o creatura> <da un altro oggetto>\n"
    #syntax += "remove <nome oggetto o creatura> <nome parte da cui rimuoverla>\n"

    return syntax
#- Fine Funzione -
