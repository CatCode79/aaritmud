# -*- coding: utf-8 -*-

#= IMPORT ======================================================================

from src.color        import color_first_upper, get_first_color
from src.enums        import PART, PARTFLAG, TO, TRUST
from src.grammar      import grammar_gender
from src.interpret    import translate_input
from src.gamescript   import check_trigger
from src.log          import log
from src.part         import get_part_descriptions
from src.utility      import get_weight_descr
from src.web_resource import create_demi_line


#= FUNZIONI ====================================================================

def command_equipment(entity, argument="", behavioured=False):
    """
    Permette di visualizzare il proprio equipaggiamento.
    """
    # Normale se questo comando è stato deferrato
    if not entity:
        return False

    entity = entity.split_entity(1)

    if not argument:
        target = entity
    else:
        target = entity.find_entity_extensively(argument)
        if not target:
            entity.act("Non vedi nessun [white]%s[close] qui attorno." % argument, TO.ENTITY)
            entity.act("$n cerca qualcuno qui attorno.", TO.OTHERS)
            return False

    force_return = check_trigger(entity, "before_equipment", entity, None if entity == target else target, behavioured)
    if force_return:
        return True

    entity.send_output(get_formatted_equipment_list(entity, target))

    force_return = check_trigger(entity, "after_equipment", entity, None if entity == target else target, behavioured)
    if force_return:
        return True

    return True
#- Fine Funzione -


def get_formatted_equipment_list(entity, target, show_header=True, show_footer=True):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    if not target:
        log.bug("target non è un parametro valido: %r" % target)
        return ""

    # -------------------------------------------------------------------------

    output = get_equipment_list(entity, target)

    if show_header:
        if target == entity:
            if output:
                output = ["[red]Stai utilizzando[close]:\n"] + output
            else:
                output.append("Non stai utilizzando nulla, sei %s!\n" % entity.skin_colorize("nud$o"))
        else:
            if output:
                output = ["%s [red]sta utilizzando[close]:\n" % color_first_upper(target.get_name(entity))] + output
            else:
                output.append("%s non sta utilizzando nulla, è %s!\n" % (
                    color_first_upper(target.get_name(looker=entity)),
                    target.skin_colorize("nud%s" % grammar_gender(target))))

    if show_footer:
        carry_equip_descr = get_weight_descr(target.get_equipped_weight())
        output.append(create_demi_line(entity))
        output.append("Stai indossando un peso totale di %s." % carry_equip_descr)

    return "".join(output)
#- Fine Funzione -


def get_equipment_list(entity, target):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    if not target:
        log.bug("target non è un parametro valido: %r" % target)
        return False

    # -------------------------------------------------------------------------

    look_translation = translate_input(entity, "look", "en")
    if not look_translation:
        log.bug("look_translation non è valida: %r" % look_translation)
        look_translation = "guarda"

    location = None
    if entity != target:
        location = target

    output = []
    # Questo serve ad evitare di visualizzare tot volte la stessa entità se
    # questa copre più parti del corpo
    already_founds = []
    # (TD) NO non va bene, bisogna farlo ordinato a seconda delle dichiarazioni
    # fatte nei vari bodies files, devo aggiungere un numero alla classe Part
    # e fare un ordinamento come ho fatto con gli EnumElement
    body_parts = target.get_body_parts()
    for part in PART.elements:
        # Evita di visualizzare parti estranee (check che in realtà non dovrebbe
        # servire essendo controllato nel wear) o organi interni
        if part not in body_parts:
            continue
        # Gli admin vedono anche gli organi interni, se eventualmente vestiti
        if PARTFLAG.INTERNAL in body_parts[part].flags and entity.trust == TRUST.PLAYER:
            continue
        if PARTFLAG.NO_EQUIP_LIST in body_parts[part].flags:
            continue

        under_weareds = []
        for weared_entity in target.iter_contains():
            if weared_entity.under_weared and weared_entity.under_weared():
                under_weareds.append(weared_entity.under_weared())

        for weared_entity in target.iter_contains():
            if weared_entity in already_founds:
                continue
            if weared_entity in under_weareds:
                continue
            if len(weared_entity.wear_mode) > 0:
                part_descriptions = get_part_descriptions(weared_entity, "equip", target, entity)
                if entity == target:
                    part_descr = part_descriptions[TO.ENTITY]
                else:
                    part_descr = part_descriptions[TO.OTHERS]
                if part in weared_entity.wear_mode:
                    output.append('''%s %s\n''' % (
                        weared_entity.get_formatted_name(looker=entity, location=location, look_translation=look_translation),
                        part_descr))
                    already_founds.append(weared_entity)

    holded = target.get_holded_entity()
    wielded = target.get_wielded_entity()
    if holded or wielded:
        look_translation = translate_input(entity, "look", "en")
        if not look_translation:
            log.bug("look_translation non è valida: %r" % look_translation)
            look_translation = "guarda"
        if holded:
            if holded.weapon_type:
                holded_verb = "impugnat%s" % grammar_gender(holded)
            else:
                holded_verb = "tenut%s" % grammar_gender(holded)
            holded_name = holded.get_formatted_name(looker=entity, location=location, look_translation=look_translation)
        if wielded:
            if wielded.weapon_type:
                wielded_verb = "impugnat%s" % grammar_gender(wielded)
            else:
                wielded_verb = "tenut%s" % grammar_gender(wielded)
            wielded_name = wielded.get_formatted_name(looker=entity, location=location, look_translation=look_translation)

    equipment_line_hold = ""
    equipment_line_wield = ""
    if target == entity:
        if holded and holded == wielded:
            equipment_line_hold = "%s %s con tutte e due le $hands\n" % (holded_name, holded_verb)
        else:
            if holded:
                equipment_line_hold = "%s %s nella $hand2\n" % (holded_name, holded_verb)
            if wielded:
                equipment_line_wield = "%s %s nella $hand1\n" % (wielded_name, wielded_verb)
    else:
        if holded and holded == wielded:
            equipment_line_hold = "%s %s con tutte e due le $HANDS\n" % (holded_name, holded_verb)
        else:
            if holded:
                equipment_line_hold = "%s %s nella $HAND2\n" % (holded_name, holded_verb)
            if wielded:
                equipment_line_wield = "%s %s nella $HAND1\n" % (wielded_name, wielded_verb)
    if equipment_line_hold:
        output.append(entity.replace_act_tags(equipment_line_hold, target=target))
    if equipment_line_wield:
        output.append(entity.replace_act_tags(equipment_line_wield, target=target))

    return output
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    return "equipment\n"
#- Fine Funzione -
