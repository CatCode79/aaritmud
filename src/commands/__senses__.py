# -*- coding: utf-8 -*-

"""
Modulo per la gestione generica di tutti i comandi sensoriali.
"""


#= IMPORT ======================================================================

from src.color      import color_first_upper
from src.config     import config
from src.enums      import CONTAINER, DIR, DOOR, EXIT, EXTRA, GRAMMAR, POSITION, ROOM, TO, TRUST
from src.exit       import get_direction
from src.grammar    import add_article
from src.gamescript import check_trigger
from src.log        import log
from src.utility    import one_argument, put_final_dot, get_weight_descr


#= FUNZIONI ====================================================================

# COMANDO   / SENSO
# look      / sight
# listen    / hearing
# smell     / smell
# touch     / touch
# taste     / taste
# intuition / sixth
def five_senses_handler(entity, argument, behavioured, command_name, gamescript_suffix2, sense_name, has_sense_method_name, messages):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # argument può essere una stringa vuota

    # behavioured ha valore di verità

    if not command_name:
        log.bug("command_name non è un parametro valido: %r" % command_name)
        return False

    if not gamescript_suffix2:
        log.bug("gamescript_suffix2 non è un parametro valido: %r" % gamescript_suffix2)
        return False

    # sense_name può essere una stringa vuota, per il look

    if not has_sense_method_name:
        log.bug("has_sense_method_name non è un parametro valido: %r" % has_sense_method_name)
        return False

    if not messages:
        log.bug("messages non è un parametro valido: %r" % messages)
        return False

    # -------------------------------------------------------------------------

    entity = entity.split_entity(1)

    if entity.IS_ACTOR:
        if entity.position < POSITION.SLEEP:
            entity.act(messages["death_position_entity"], TO.ENTITY)
            entity.act(messages["death_position_others"], TO.OTHERS)
            return False
        if entity.position == POSITION.SLEEP:
            entity.act(messages["sleep_position_entity"], TO.ENTITY)
            entity.act(messages["sleep_position_others"], TO.OTHERS)
            return False
        if not getattr(entity, has_sense_method_name)():
            entity.act(messages["not_has_sense_entity"], TO.ENTITY)
            entity.act(messages["not_has_sense_others"], TO.OTHERS)
            return False

    # Se entity è una razza che non può annusare sott'acqua allora esce
    if (sense_name == "smell" and not entity.race.smell_on_water
    and entity.location.IS_ROOM and ROOM.UNDERWATER in entity.location.flags):
        entity.send_output("Stai per annusare quando ti ricordi che qui richieresti di annegare!")
        return False

    # Se non è stato passato nessun argomento allora procede alla ricerca della
    # descrizione sensoriale nella stanza
    if not argument:
        descr = entity.location.get_descr(sense_name, looker=entity)
        if descr and "no_send" not in descr:
            update_sensed_rooms(entity, entity.location, command_name)

            force_return = check_trigger(entity, "before_" + command_name, entity, entity.location, descr, None, behavioured)
            if force_return:
                return True
            force_return = check_trigger(entity.location, "before_" + gamescript_suffix2, entity, entity.location, descr, None, behavioured)
            if force_return:
                return True

            entity.send_output('''<div style="width:66%%">%s</div>''' % descr, break_line=False)
            entity.act(messages["room_descr_others"], TO.OTHERS)

            force_return = check_trigger(entity, "after_" + command_name, entity, entity.location, descr, None, behavioured)
            if force_return:
                return True
            force_return = check_trigger(entity.location, "after_" + gamescript_suffix2, entity, entity.location, descr, None, behavioured)
            if force_return:
                return True
            return True
        else:
            force_return = check_trigger(entity, "before_" + command_name, entity, entity.location, "", None, behavioured)
            if force_return:
                return False
            force_return = check_trigger(entity.location, "before_" + gamescript_suffix2, entity, entity.location, "", None, behavioured)
            if force_return:
                return False

            entity.act(messages["no_argument_entity"], TO.ENTITY)
            entity.act(messages["no_argument_others"], TO.OTHERS)

            force_return = check_trigger(entity, "after_" + command_name, entity, entity.location, "", None, behavioured)
            if force_return:
                return False
            force_return = check_trigger(entity.location, "after_" + gamescript_suffix2, entity, entity.location, "", None, behavioured)
            if force_return:
                return False
            return False

    # ---------------------------------------------------------------------

    original_argument = argument
    arg1, argument = one_argument(argument)

    target, target_argument, extra_argument = entity.find_entity_from_args(arg1, argument)
    if ((target and not target.is_secret_door())
    or  (target and target.is_secret_door() and len(target_argument) >= config.min_secret_arg_len)):
        return sense_an_entity(entity, target, extra_argument, command_name, gamescript_suffix2, sense_name, messages, behavioured)

    # -------------------------------------------------------------------------

    # Cerca un'eventuale extra nella locazione, prima in maniera esatta
    extra = entity.location.extras.get_extra(original_argument, exact=True)
    if extra:
        descr = extra.get_descr(sense_name, looker=entity, parent=entity)
        if descr and "no_send" not in descr:
            update_sensed_rooms(entity, entity.location, command_name)

            force_return = check_trigger(entity, "before_" + command_name, entity, entity.location, descr, extra, behavioured)
            if force_return:
                return True
            force_return = check_trigger(entity.location, "before_" + gamescript_suffix2, entity, entity.location, descr, extra, behavioured)
            if force_return:
                return True

            entity.send_output('''<div style="width:66%%">%s</div>''' % descr, break_line=False)
            if EXTRA.NO_LOOK_ACT not in extra.flags:
                if "%s" in messages["room_extra_others"]:
                    word = add_article(extra.keywords.split()[0])
                    entity.act(messages["room_extra_others"] % add_article(word, GRAMMAR.INDETERMINATE), TO.OTHERS)
                else:
                    entity.act(messages["room_extra_others"], TO.OTHERS)

            force_return = check_trigger(entity, "after_" + command_name, entity, entity.location, descr, extra, behavioured)
            if force_return:
                return True
            force_return = check_trigger(entity.location, "after_" + gamescript_suffix2, entity, entity.location, descr, extra, behavioured)
            if force_return:
                return True
            return True

    # Gestisce il look in una direzione, prima in maniera esatta
    if target_argument:
        direction = get_direction(target_argument, exact=True)
        if direction != DIR.NONE:
            return sense_at_direction(entity, direction, extra_argument, True, command_name, gamescript_suffix2, sense_name, messages, behavioured, "to_dir")

    # Cerca un'eventuale extra sensoriale nella stanza, ora in maniera prefissa
    extra = entity.location.extras.get_extra(original_argument, exact=False)
    if extra:
        descr = extra.get_descr(sense_name, looker=entity, parent=entity)
        if descr and "no_send" not in descr:
            update_sensed_rooms(entity, entity.location, command_name)

            force_return = check_trigger(entity, "before_" + command_name, entity, entity.location, descr, extra, behavioured)
            if force_return:
                return True
            force_return = check_trigger(entity.location, "before_" + gamescript_suffix2, entity, entity.location, descr, extra, behavioured)
            if force_return:
                return True

            entity.send_output('''<div style="width:66%%">%s</div>''' % descr, break_line=False)
            if EXTRA.NO_LOOK_ACT not in extra.flags:
                if "%s" in messages["room_extra_others"]:
                    word = add_article(extra.keywords.split()[0])
                    entity.act(messages["room_extra_others"] % add_article(word, GRAMMAR.INDETERMINATE), TO.OTHERS)
                else:
                    entity.act(messages["room_extra_others"], TO.OTHERS)

            force_return = check_trigger(entity, "after_" + command_name, entity, entity.location, descr, extra, behavioured)
            if force_return:
                return True
            force_return = check_trigger(entity.location, "after_" + gamescript_suffix2, entity, entity.location, descr, extra, behavioured)
            if force_return:
                return True
            return True

    # Gestisce il look in una direzione, ora in maniera prefissa
    if target_argument:
        direction = get_direction(target_argument, exact=False)
        if direction != DIR.NONE:
            return sense_at_direction(entity, direction, extra_argument, False, command_name, gamescript_suffix2, sense_name, messages, behavioured, "to_dir")

    # -------------------------------------------------------------------------

    force_return = check_trigger(entity, "before_" + command_name, entity, None, "", extra, behavioured)
    if force_return:
        return False

    if extra:
        word = add_article(extra.keywords.split()[0])
        entity.act(messages["no_found_extra_entity_alt"].replace(" di $N", "") % word, TO.ENTITY)
    else:
        if "%s" in messages["no_found_entity"]:
            entity.act(messages["no_found_entity"] % original_argument, TO.ENTITY)
        else:
            entity.act(messages["no_found_entity"], TO.ENTITY)
    entity.act(messages["no_found_others"], TO.OTHERS)

    force_return = check_trigger(entity, "after_" + command_name, entity, None, "", extra, behavioured)
    if force_return:
        return False

    return False
#- Fine Funzione -


def sense_an_entity(entity, target, extra_argument, command_name, gamescript_suffix2, sense_name, messages, behavioured):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    if not target:
        log.bug("target non è un parametro valido: %r" % target)
        return False

    # extra_argument può essere una stringa vuota

    if not command_name:
        log.bug("command_name non è un parametro valido: %r" % command_name)
        return False

    if not gamescript_suffix2:
        log.bug("gamescript_suffix2 non è un parametro valido: %r" % gamescript_suffix2)
        return False

    # sense_name può essere una stringa vuota, per il look

    # -------------------------------------------------------------------------

    if extra_argument:
        # Cerca una extra sensoriale, prima in maniera esatta e poi prefissa
        extra = target.extras.get_extra(extra_argument, exact=True)
        if extra:
            descr = extra.get_descr(sense_name, looker=entity, parent=entity)
            if descr and "no_send" not in descr:
                update_sensed_entities(entity, target, command_name)

                force_return = check_trigger(entity, "before_" + command_name, entity, target, descr, extra, behavioured)
                if force_return:
                    return True
                force_return = check_trigger(target, "before_" + gamescript_suffix2, entity, target, descr, extra, behavioured)
                if force_return:
                    return True

                entity.send_output('''<div style="width:66%%">%s</div>''' % descr, break_line=False)
                word = add_article(extra.keywords.split()[0], GRAMMAR.INDETERMINATE)
                sense_messages_to_others(entity, target, messages, behavioured, "entity_extra", word, extra)

                force_return = check_trigger(entity, "after_" + command_name, entity, target, descr, extra, behavioured)
                if force_return:
                    return True
                force_return = check_trigger(target, "after_" + gamescript_suffix2, entity, target, descr, extra, behavioured)
                if force_return:
                    return True
                return True

        extra = target.extras.get_extra(extra_argument, exact=False)
        if extra:
            descr = extra.get_descr(sense_name, looker=entity, parent=entity)
            if descr and "no_send" not in descr:
                update_sensed_entities(entity, target, command_name)

                force_return = check_trigger(entity, "before_" + command_name, entity, target, descr, extra, behavioured)
                if force_return:
                    return True
                force_return = check_trigger(target, "before_" + gamescript_suffix2, entity, target, descr, extra, behavioured)
                if force_return:
                    return True

                entity.send_output('''<div style="width:66%%">%s</div>''' % descr, break_line=False)
                word = add_article(extra.keywords.split()[0], GRAMMAR.INDETERMINATE)
                sense_messages_to_others(entity, target, messages, behavioured, "entity_extra", word, extra)
                force_return = check_trigger(entity, "after_" + command_name, entity, target, descr, extra, behavioured)

                if force_return:
                    return True
                force_return = check_trigger(target, "after_" + gamescript_suffix2, entity, target, descr, extra, behavioured)
                if force_return:
                    return True
                return True

        avoid_inventory = True
        if target.is_sensable_inside(sense_name):
            avoid_inventory = False

        # Oltre alle extra cerca anche tra gli oggetti equipaggiati di target
        equipped_target = entity.find_entity(extra_argument, location=target, avoid_inventory=avoid_inventory, avoid_equipment=False)
        if equipped_target:
            descr = equipped_target.get_descr(sense_name, looker=entity)
            if descr and "no_send" not in descr:
                update_sensed_entities(entity, equipped_target, command_name)

                force_return = check_trigger(entity, "before_" + command_name, entity, equipped_target, descr, extra, behavioured)
                if force_return:
                    return True
                force_return = check_trigger(equipped_target, "before_" + gamescript_suffix2, entity, equipped_target, descr, extra, behavioured)
                if force_return:
                    return True

                entity.send_output('''<div style="width:66%%">%s</div>''' % descr, break_line=False)
                sense_messages_to_others_equipped(entity, equipped_target, messages, "entity_equip", target)

                force_return = check_trigger(entity, "after_" + command_name, entity, equipped_target, descr, extra, behavioured)
                if force_return:
                    return True
                force_return = check_trigger(equipped_target, "after_" + gamescript_suffix2, entity, equipped_target, descr, extra, behavioured)
                if force_return:
                    return True
                return True
            else:
                force_return = check_trigger(entity, "before_" + command_name, entity, equipped_target, target, "", behavioured)
                if force_return:
                    return False
                force_return = check_trigger(equipped_target, "before_" + gamescript_suffix2, entity, equipped_target, "", target, behavioured)
                if force_return:
                    return False

                sense_messages_to_others_equipped(entity, equipped_target, messages, "entity_equip", target)
                entity.act(messages["entity_equip_auto"], TO.ENTITY, target, equipped_target)

                force_return = check_trigger(entity, "after_" + command_name, entity, equipped_target, "", target, behavioured)
                if force_return:
                    return False
                force_return = check_trigger(equipped_target, "after_" + gamescript_suffix2, entity, equipped_target, "", target, behavioured)
                if force_return:
                    return False
                return False

        # (TD) Qui inoltre dovrò cercare tra le parti del corpo

        # Se la keyword si trova però in un'altro senso allora invia un
        # messaggio leggermente differente, coma a dare per scontato che
        # vi sia effettivamente un'altra keywords
        force_return = check_trigger(entity, "before_" + command_name, entity, target, "", extra, behavioured)
        if force_return:
            return False
        force_return = check_trigger(target, "before_" + gamescript_suffix2, entity, target, "", extra, behavioured)
        if force_return:
            return False

        if extra:
            if entity == target:
                if "%s" in messages["no_found_extra_entity_alt_auto"]:
                    entity.act(messages["no_found_extra_entity_alt_auto"] % extra_argument, TO.ENTITY)
                else:
                    entity.act(messages["no_found_extra_entity_alt_auto"], TO.ENTITY)
            else:
                if "%s" in messages["no_found_extra_entity_alt"]:
                    entity.act(messages["no_found_extra_entity_alt"] % extra_argument, TO.ENTITY, target)
                else:
                    entity.act(messages["no_found_extra_entity_alt"], TO.ENTITY, target)
        else:
            if entity == target:
                if "%s" in messages["no_found_extra_entity_auto"]:
                    entity.act(messages["no_found_extra_entity_auto"] % extra_argument, TO.ENTITY)
                else:
                    entity.act(messages["no_found_extra_entity_auto"], TO.ENTITY)
            else:
                if "%s" in messages["no_found_extra_entity"]:
                    entity.act(messages["no_found_extra_entity"] % extra_argument, TO.ENTITY, target)
                else:
                    entity.act(messages["no_found_extra_entity"], TO.ENTITY, target)
        if entity == target:
            entity.act(messages["no_found_extra_others_auto"], TO.OTHERS)
        else:
            entity.act(messages["no_found_extra_others"], TO.OTHERS, target)
        if entity != target:
            entity.act(messages["no_found_extra_target"], TO.TARGET, target)

        force_return = check_trigger(entity, "after_" + command_name, entity, target, "", extra, behavioured)
        if force_return:
            return False
        force_return = check_trigger(target, "after_" + gamescript_suffix2, entity, target, "", extra, behavioured)
        if force_return:
            return False
        return False
    else:
        # Se si sta toccando un oggetto ne si può ricavare il peso totale invece
        # della sola tara come avviene invece nel look
        if target.IS_ITEM and sense_name == "touch":
            weight_descr = get_weight_descr(target.get_total_weight())
            if entity == target:
                weight_descr = "Pesi in totale %s" % weight_descr
            else:
                name = target.get_name(entity)
                weight_descr = "%s pesa in totale %s" % (color_first_upper(name), weight_descr)

        descr = target.get_descr(sense_name, looker=entity)
        if descr and "no_send" not in descr:
            update_sensed_entities(entity, target, command_name)

            force_return = check_trigger(entity, "before_" + command_name, entity, target, descr, None, behavioured)
            if force_return:
                return True
            force_return = check_trigger(target, "before_" + gamescript_suffix2, entity, target, descr, None, behavioured)
            if force_return:
                return True

            if target.IS_ITEM and sense_name == "touch":
                entity.send_output('''<div style="width:66%%">%s</div>''' % descr + weight_descr + "\n", break_line=False)
            else:
                entity.send_output('''<div style="width:66%%">%s</div>''' % descr, break_line=False)
            sense_messages_to_others(entity, target, messages, behavioured, "entity_descr", "")
            force_return = check_trigger(entity, "after_" + command_name, entity, target, descr, None, behavioured)
            if force_return:
                return True
            force_return = check_trigger(target, "after_" + gamescript_suffix2, entity, target, descr, None, behavioured)
            if force_return:
                return True
            return True
        else:
            force_return = check_trigger(entity, "before_" + command_name, entity, target, "", None, behavioured)
            if force_return:
                return False
            force_return = check_trigger(target, "before_" + gamescript_suffix2, entity, target, "", None, behavioured)
            if force_return:
                return False

            if entity == target:
                entity.act(messages["no_found_descr_entity_auto"], TO.ENTITY)
            elif target.IS_ITEM and sense_name == "touch":
                entity.act(messages["no_found_descr_entity"] + "\n" + weight_descr, TO.ENTITY, target)
            else:
                entity.act(messages["no_found_descr_entity"], TO.ENTITY, target)
            if entity == target:
                entity.act(messages["no_found_descr_others_auto"], TO.OTHERS)
            else:
                entity.act(messages["no_found_descr_target"], TO.TARGET, target)
                entity.act(messages["no_found_descr_others"], TO.OTHERS, target)

            force_return = check_trigger(entity, "after_" + command_name, entity, target, "", None, behavioured)
            if force_return:
                return False
            force_return = check_trigger(target, "after_" + gamescript_suffix2, entity, target, "", None, behavioured)
            if force_return:
                return False
            return False

    log.bug("Raggiungimento inaspettato del codice")
    return False
#- Fine Funzione -


def sense_messages_to_others(entity, target, messages, behavioured, message_key, arg="", extra=None):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return

    if not target:
        log.bug("target non è un parametro valido: %r" % target)
        return

    if not messages:
        log.bug("messages non è un parametro valido: %r" % messages)
        return

    if not message_key:
        log.bug("message_key non è un parametro valido: %r" % message_key)
        return

    # -------------------------------------------------------------------------

    if target == entity:
        if not extra or EXTRA.NO_LOOK_ACT not in extra.flags:
            message = messages[message_key + "_auto"]
            if arg and "%" in message:
                message = message % arg
            entity.act(message, TO.OTHERS)
    else:
        if not extra or EXTRA.NO_LOOK_ACT not in extra.flags:
            message = messages[message_key + "_others"]
            if arg and "%" in message:
                message = message % arg
            entity.act(message, TO.OTHERS, target)
        message = messages[message_key + "_target"]
        if arg and "%" in message:
            message = message % arg
        entity.act(message, TO.TARGET, target)
#- Fine Funzione -


def sense_messages_to_others_equipped(entity, target, messages, message_key, equipped_target):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return

    if not target:
        log.bug("target non è un parametro valido: %r" % target)
        return

    if not messages:
        log.bug("messages non è un parametro valido: %r" % messages)
        return

    if not message_key:
        log.bug("message_key non è un parametro valido: %r" % message_key)
        return

    if not equipped_target:
        log.bug("equipped_target non è un parametro valido: %r" % equipped_target)
        return

    # -------------------------------------------------------------------------

    if target == entity:
        entity.act(messages[message_key + "_self"], TO.OTHERS)
    else:
        entity.act(messages[message_key + "_others"], TO.OTHERS, target)
        entity.act(messages[message_key + "_target"], TO.TARGET, target)
#- Fine Funzione -


def sense_at_direction(entity, direction, argument, exact, command_name, gamescript_suffix2, sense_name, messages, behavioured, from_or_to, readable=False):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    if not direction:
        log.bug("direction non è un parametro valido: %r" % direction)
        return False

    # argument può essere una stringa vuota

    # exact ha valore di verità

    if not command_name:
        log.bug("command_name non è un parametro valido: %r" % command_name)
        return False

    if not gamescript_suffix2:
        log.bug("gamescript_suffix2 non è un parametro valido: %r" % gamescript_suffix2)
        return False

    if not sense_name and sense_name != "":
        log.bug("sense_name non è un parametro valido: %r" % sense_name)
        return False

    if not messages:
        log.bug("messages non è un parametro valido: %r" % messages)
        return False

    if from_or_to not in ("from_dir", "to_dir"):
        log.bug("from_or_to non è un parametro valido: %r" % from_or_to)
        return False

    # readable ha valore di verità

    # -------------------------------------------------------------------------

    if not readable:
        if not entity.location.IS_ROOM:
            force_return = check_trigger(entity, "before_" + sense_name, entity, entity.location, "", None, behavioured)
            if force_return:
                return False
            force_return = check_trigger(entity.location, "before_" + gamescript_suffix2, entity, entity.location, "", None, behavioured)
            if force_return:
                return False

            if "%s" in messages["direction_entity"]:
                entity.act(messages["direction_entity"] % getattr(direction, from_or_to), TO.ENTITY)
            else:
                entity.act(messages["direction_entity"], TO.ENTITY)
            if "%s" in messages["direction_others"]:
                entity.act(messages["direction_others"] % direction.to_dir, TO.OTHERS)
            else:
                entity.act(messages["direction_others"], TO.OTHERS)

            force_return = check_trigger(entity, "after_" + sense_name, entity, entity.location, "", None, behavioured)
            if force_return:
                return False
            force_return = check_trigger(entity.location, "after_" + gamescript_suffix2, entity, entity.location, "", None, behavioured)
            if force_return:
                return False
            return False

    # (TD) dovrebbe far vedere anche altre cose, a seconda della tipologia
    # dell'uscita (segreta e non) e se l'eventuale porta è stata sfondata

    # (TD) Se la stanza di arrivo è buia le cose cambiano, da pensare, anche
    # relativamente alla descr_night

    # -------------------------------------------------------------------------

    if direction in entity.location.walls:
        wall = entity.location.walls[direction]
        # (TD) pensare se accorpare tutti questi pezzetti di codice simile sotto
        show_to_others = True
        if argument:
            descr = ""
            extra = wall.extras.get_extra(argument, entity, parent=entity)
            if readable and EXTRA.READABLE not in extra.flags:
                extra = None
            if extra:
                descr = extra.get_descr(sense_name, looker=entity, parent=entity)
                if EXTRA.NO_LOOK_ACT in extra.flags:
                    show_to_others = False
        elif not readable:
            descr = wall.get_descr(sense_name, looker=entity)
            
        if descr and "no_send" not in descr:
            update_sensed_rooms(entity, entity.location, command_name)

            force_return = check_trigger(entity, "before_" + "read" if readable else sense_name, entity, entity.location, descr, wall, behavioured)
            if force_return:
                return True
            force_return = check_trigger(entity.location, "before_" + "readed" if readable else sense_name, entity, entity.location, descr, wall, behavioured)
            if force_return:
                return True

            entity.send_output('''<div style="width:66%%">%s</div>''' % descr, break_line=False)
            if "%s" in messages["direction_wall_others"]:
                entity.act(messages["direction_wall_others"] % direction.to_dir, TO.OTHERS)
            else:
                entity.act(messages["direction_wall_others"], TO.OTHERS)
            force_return = check_trigger(entity, "after_" + "read" if readable else sense_name, entity, entity.location, descr, wall, behavioured)
            if force_return:
                return True
            force_return = check_trigger(entity.location, "after_" + "readed" if readable else sense_name, entity, entity.location, descr, wall, behavioured)
            if force_return:
                return True
            return True

    # -------------------------------------------------------------------------

    door = entity.location.get_door(direction)
    if door and DOOR.CLOSED in door.door_type.flags:
        if DOOR.SECRET in door.door_type.flags:
            if "%s" in messages["direction_entity"]:
                entity.act(messages["direction_entity"] % getattr(direction, from_or_to), TO.ENTITY)
            else:
                entity.act(messages["direction_entity"], TO.ENTITY)
            if "%s" in messages["direction_others"]:
                entity.act(messages["direction_others"] % direction.to_dir, TO.OTHERS)
            else:
                entity.act(messages["direction_others"], TO.OTHERS)
            return False
        else:
            show_to_others = True
            if argument:
                descr = ""
                extra = door.extras.get_extra(argument, exact=exact)
                if readable and EXTRA.READABLE not in extra.flags:
                    extra = None
                if extra:
                    descr = extra.get_descr(sense_name, looker=entity, parent=entity)
                    if EXTRA.NO_LOOK_ACT in extra.flags:
                        show_to_others = False
            elif not readable:
                descr = door.get_descr(sense_name, looker=entity)
            if descr and "no_send" not in descr:
                update_sensed_entities(entity, door, command_name)

                force_return = check_trigger(entity, "before_" + command_name, entity, door, descr, None, behavioured)
                if force_return:
                    return True
                force_return = check_trigger(entity.location, "before_" + gamescript_suffix2, entity, door, descr, None, behavioured)
                if force_return:
                    return True

                entity.send_output('''<div style="width:66%%">%s</div>''' % descr, break_line=False)
                if "%s" in messages["direction_target_others"]:
                    entity.act(messages["direction_target_others"] % direction.to_dir, TO.OTHERS, door)
                else:
                    entity.act(messages["direction_target_others"], TO.OTHERS, door)
                force_return = check_trigger(entity, "after_" + command_name, entity, door, descr, None, behavioured)
                if force_return:
                    return True
                force_return = check_trigger(entity.location, "after_" + gamescript_suffix2, entity, door, descr, None, behavioured)
                if force_return:
                    return True
                return True

    # -------------------------------------------------------------------------

    exit = None
    if direction in entity.location.exits:
        exit = entity.location.exits[direction]

    if exit and EXIT.DIGGABLE not in exit.flags:
        show_to_others = True
        if argument:
            descr = ""
            extra = exit.extras.get_extra(argument, exact=exact)
            if readable and EXTRA.READABLE not in extra.flags:
                extra = None
            if extra:
                descr = extra.get_descr(sense_name, looker=entity, parent=entity)
                if EXTRA.NO_LOOK_ACT in extra.flags:
                    show_to_others = False
        elif not readable:
            descr = exit.get_descr(sense_name, looker=entity)
        if descr and "no_send" not in descr:
            update_sensed_rooms(entity, entity.location, command_name)

            force_return = check_trigger(entity, "before_" + command_name, entity, entity.location, descr, exit, behavioured)
            if force_return:
                return True
            force_return = check_trigger(entity.location, "before_" + gamescript_suffix2, entity, entity.location, descr, exit, behavioured)
            if force_return:
                return True

            entity.send_output('''<div style="width:66%%">%s</div>''' % descr, break_line=False)
            if "%s" in messages["direction_exit_others"]:
                entity.act(messages["direction_exit_others"] % direction.to_dir, TO.OTHERS)
            else:
                entity.act(messages["direction_exit_others"], TO.OTHERS)
            force_return = check_trigger(entity, "after_" + command_name, entity, entity.location, descr, exit, behavioured)
            if force_return:
                return True
            force_return = check_trigger(entity.location, "after_" + gamescript_suffix2, entity, entity.location, descr, exit, behavioured)
            if force_return:
                return True
            return True
    else:
        if "%s" in messages["direction_entity"]:
            entity.act(messages["direction_entity"] % getattr(direction, from_or_to), TO.ENTITY)
        else:
            entity.act(messages["direction_entity"], TO.ENTITY)
        if "%s" in messages["direction_others"]:
            entity.act(messages["direction_others"] % direction.to_dir, TO.OTHERS)
        else:
            entity.act(messages["direction_others"], TO.OTHERS)
        return False

    # -------------------------------------------------------------------------

    # Se c'era una extra da guardare e non ha trovato nulla nell'uscita o nel
    # wall allora prova a guardare tra le extra dell'eventuale porta aperta
    if argument and door and DOOR.CLOSED not in door.door_type.flags:
        # Qui poiché la porta è aperta non è più da considerarsi segreta
        extra = door.extras.get_extra(argument, exact=exact)
        if readable and EXTRA.READABLE not in extra.flags:
            extra = None
        if extra:
            descr = extra.get_descr(sense_name, looker=entity, parent=entity)
            if descr and "no_send" not in descr:
                update_sensed_entities(entity, door, command_name)

                force_return = check_trigger(entity, "before_" + command_name, entity, door, descr, None, behavioured)
                if force_return:
                    return True
                force_return = check_trigger(entity.location, "before_" + gamescript_suffix2, entity, door, descr, None, behavioured)
                if force_return:
                    return True

                entity.send_output('''<div style="width:66%%">%s</div>''' % descr, break_line=False)
                if "%s" in messages["direction_target_others"]:
                    entity.act(messages["direction_target_others"] % direction.to_dir, TO.OTHERS, door)
                else:
                    entity.act(messages["direction_target_others"], TO.OTHERS, door)
                force_return = check_trigger(entity, "after_" + command_name, entity, door, descr, None, behavioured)
                if force_return:
                    return True
                force_return = check_trigger(entity.location, "after_" + gamescript_suffix2, entity, door, descr, None, behavioured)
                if force_return:
                    return True
                return True

    if readable:
        return False
    else:
        destination_room = entity.location.get_destination_room(direction)
        if not destination_room:
            force_return = check_trigger(entity, "before_" + command_name, entity, entity.location, "", str(direction), behavioured)
            if force_return:
                return False
            force_return = check_trigger(entity.location, "before_" + gamescript_suffix2, entity, entity.location, "", str(direction), behavioured)
            if force_return:
                return False

            if "%s" in messages["direction_entity"]:
                entity.act(messages["direction_entity"] % getattr(direction, from_or_to), TO.ENTITY)
            else:
                entity.act(messages["direction_entity"] % getattr(direction, from_or_to), TO.ENTITY)
            if "%s" in messages["direction_others"]:
                entity.act(messages["direction_others"] % direction.to_dir, TO.OTHERS)
            else:
                entity.act(messages["direction_others"], TO.OTHERS)
            force_return = check_trigger(entity, "after_" + command_name, entity, entity.location, "", str(direction), behavioured)
            if force_return:
                return False
            force_return = check_trigger(entity.location, "after_" + gamescript_suffix2, entity, entity.location, "", str(direction), behavioured)
            if force_return:
                return False
            return False

        # Fa visualizzare il nome della stanza
        # (TD) non farlo vedere se la stanza non è visibile, buia o che
        # sarà bene unire questa ricerca del nome della stanza con la stessa
        # che viene visualizza nell'elenco delle uscite della stanza
        descr = color_first_upper(put_final_dot(destination_room.get_name(entity)))

        force_return = check_trigger(entity, "before_" + command_name, entity, entity.location, descr, destination_room, behavioured)
        if force_return:
            return True
        force_return = check_trigger(entity.location, "before_" + gamescript_suffix2, entity, entity.location, descr, destination_room, behavioured)
        if force_return:
            return True

        entity.send_output('''<div style="width:66%%">%s</div>''' % descr, break_line=False)
        if "%s" in messages["direction_others"]:
            entity.act(messages["direction_others"] % direction.to_dir, TO.OTHERS)
        else:
            entity.act(messages["direction_others"], TO.OTHERS)

        force_return = check_trigger(entity, "after_" + command_name, entity, entity.location, descr, destination_room, behavioured)
        if force_return:
            return True
        force_return = check_trigger(entity.location, "after_" + gamescript_suffix2, entity, entity.location, descr, destination_room, behavioured)
        if force_return:
            return True
        return True
#- Fine Funzione -


def update_sensed_rooms(entity, room, command_name):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return

    if not room:
        log.bug("room non è un parametro valido: %r" % room)
        return

    if not command_name:
        log.bug("command_name non è un parametro valido: %r" % command_name)
        return

    # -------------------------------------------------------------------------

    if not entity.IS_PLAYER:
        return

    if not room.IS_ROOM:
        return

    if command_name == "look":
        return

    if room.prototype.code in entity.sensed_rooms:
        entity.sensed_rooms[room.prototype.code] += 1
    else:
        entity.sensed_rooms[room.prototype.code] = 1
        if   command_name == "listen":    verb = "ascoltato"
        elif command_name == "smell":     verb = "annusato"
        elif command_name == "touch":     verb = "toccato"
        elif command_name == "taste":     verb = "assaggiato"
        elif command_name == "intuition": verb = "intuito"
        else:                             verb = "<errore comando sensoriale>"
        reason = "per aver %s per la prima volta %s" % (verb, room.get_name(looker=entity))
        entity.give_experience(room.area.level, reason=reason)
#- Fine Funzione -


def update_sensed_entities(entity, target, command_name):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return

    if not target:
        log.bug("target non è un parametro valido: %r" % target)
        return

    if not command_name:
        log.bug("command_name non è un parametro valido: %r" % command_name)
        return

    # -------------------------------------------------------------------------

    if not entity.IS_PLAYER:
        return

    if target.IS_ROOM:
        return

    if command_name == "look":
        return

    if target.prototype.code in entity.sensed_entities:
        entity.sensed_entities[target.prototype.code] += 1
    else:
        entity.sensed_entities[target.prototype.code] = 1
        if   command_name == "listen":    verb = "ascoltato"
        elif command_name == "smell":     verb = "annusato"
        elif command_name == "touch":     verb = "toccato"
        elif command_name == "taste":     verb = "assaggiato"
        elif command_name == "intuition": verb = "intuito"
        else:                             verb = "<errore comando sensoriale>"
        reason = "per aver %s per la prima volta %s" % (verb, target.get_name(looker=entity))
        entity.give_experience(target.level, reason=reason)
#- Fine Funzione -
