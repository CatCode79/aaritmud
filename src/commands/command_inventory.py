# -*- coding: utf-8 -*-


#= IMPORT ======================================================================

from src.color        import color_first_upper, get_first_color
from src.enums        import FLAG, PART, TRUST
from src.interpret    import translate_input
from src.gamescript   import check_trigger
from src.log          import log
from src.utility      import get_weight_descr, format_for_admin
from src.web_resource import create_demi_line


#= FUNZIONI ====================================================================

def command_inventory(entity, argument="", behavioured=False):
    """
    Permette di visualizzare il proprio inventario.
    """
    # Normale se questo comando è stato deferrato
    if not entity:
        return False

    entity = entity.split_entity(1)

    # (TD) I trigger di inventory funzionano cmq con il target perché in futuro
    # ci sarà la skill apposita per visualizzare l'inventario anche se adesso
    # è solo lato admin
    if not argument or entity.trust <= TRUST.PLAYER:
        target = entity
    else:
        target = entity.find_entity_extensively(argument)
        if not target:
            entity.act("Non vedi nessun [white]%s[close] qui attorno." % argument, TO.ENTITY)
            entity.act("$n sembra stia cercando qualcuno qui attorno che però non c'è.", TO.OTHERS)
            return False

    force_return = check_trigger(entity, "before_inventory", entity, None if entity == target else target, behavioured)
    if force_return:
        return True

    entity.send_output(get_formatted_inventory_list(entity, target), break_line=False)

    force_return = check_trigger(entity, "after_inventory", entity, None if entity == target else target, behavioured)
    if force_return:
        return True

    return True
#- Fine Funzione -


def get_formatted_inventory_list(entity, target, show_header=True, show_footer=True):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    if not target:
        log.bug("target non è un parametro valido: %r" % target)
        return ""

    # -------------------------------------------------------------------------

    output = get_inventory_list(entity, target)

    if show_header:
        if target == entity:
            if output:
                output = ["[red]Stai trasportando[close]:\n"] + output
            else:
                output.append("Non stai trasportando nulla.\n")
        else:
            if output:
                output = ["[red]Sta trasportando[close]:\n"] + output
            else:
                output.append("%s non sta trasportando nulla.\n" % target.get_name(entity))

    # Crea la parte con il totale trasportato dal giocatore
    if show_footer:
        carry_weight_descr     = get_weight_descr(entity.get_carried_weight())
        can_carry_weight_descr = get_weight_descr(entity.can_carry_weight())
        output.append(create_demi_line(entity))
        output.append("Stai trasportando e indossando un peso totale di %s.\n" % carry_weight_descr)
        output.append("Con le tue attuali forze il tuo massimo è di %s.\n" % can_carry_weight_descr)

    return "".join(output)
#- Fine Funzione -


def get_inventory_list(looker, target):
    if not looker:
        log.bug("looker non è un parametro valido: %r" % looker)
        return []

    if not target:
        log.bug("target non è un parametro valido: %r" % target)
        return []

    # -------------------------------------------------------------------------

    from src.find_entity import INSTANCE, COUNTER, NO_LOOK_LIST, BURIED, INGESTED, INCOGNITO

    look_translation = translate_input(looker, "look", "en")
    if not look_translation:
        log.bug("look_translation non è valida: %r" % look_translation)
        look_translation = "guarda"

    output = []
    for possession in target.get_list_of_entities(looker, admin_descrs=True):
        if not looker.can_see(possession[INSTANCE]):
            continue
        # Si suppone che se il giocatore ha con sé un oggetto no look list
        # sappia della sua esistenza
        if looker != target and FLAG.NO_LOOK_LIST in possession[INSTANCE].flags:
            continue
        if FLAG.INTERACTABLE_FROM_OUTSIDE in possession[INSTANCE].flags and possession[INSTANCE].location != target:
            continue

        interactable_entities = list(possession[INSTANCE].iter_only_interactable_entities(use_can_see=True))
        if "$i" in possession[INSTANCE].long or "$I" in possession[INSTANCE].long or interactable_entities:
            # (TT) Far vedere la long al posto della short nell'inventario
            # per tutte e quante le entità: da pensare!
            name = possession[INSTANCE].get_long(looker, look_translation)
        else:
            name = possession[INSTANCE].get_formatted_name(looker, location=target, look_translation=look_translation)
        output.append('''%s pesante %s, %s.''' % (
            name,
            get_weight_descr(possession[INSTANCE].get_total_weight()),
            possession[INSTANCE].get_condition()))
        if possession[COUNTER] > 1:
            output.append(" (%s)" % possession[COUNTER])
        if looker.trust > TRUST.PLAYER:
            if looker == target:
                message = "%s%s%s" % (possession[BURIED], possession[INGESTED], possession[INCOGNITO])
            else:
                message = "%s%s%s%s" % (possession[NO_LOOK_LIST], possession[BURIED], possession[INGESTED], possession[INCOGNITO])
            if message:
                output.append(" " + format_for_admin(message.lstrip()))
        output.append("\n")

    # È corretto che possa ritornare output vuoto, viene gestito esternamente
    return output
#- Fine Funzione -


# (TD)
def create_js_menu_inventory(target, entity):
    """
    Crea un menù javascript apribile con il tasto destro sul link dell'entità
    in inventario.
    Permette di guardare o droppare un'entità.
    """
    if not target:
        log.bug("target non è un parametro valido: %r" % target)
        return ""

    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    look_translation = translate_input(entity, "look", "en")
    if not look_translation:
        log.bug("look_translation non è valida: %r" % look_translation)
        look_translation = "guarda"

    drop_translation = translate_input(entity, "drop", "en")
    if not drop_translation:
        log.bug("drop_translation non è valida: %r" % drop_translation)
        drop_translation = "posa"

    keywords = target.get_keywords_attr(entity)
    if not keywords:
        log.bug("keywords non è valida: %r" % keywords)
        return ""

    # (TD)
    return ""
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    return "inventory\n"
#- Fine Funzione -
