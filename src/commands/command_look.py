# -*- coding: utf-8 -*-

"""
Comando per guardarsi intorno o qualcuno o qualche cosa, pure il cielo!
"""


#= IMPORT ======================================================================

from src.affect       import is_affected
from src.calendar     import calendar
from src.color        import color_first_upper, close_color
from src.config       import config
from src.database     import database
from src.exit         import get_direction
from src.engine       import engine
from src.enums        import (AFFECT, AREA, CONTAINER, DIR, DOOR, ENTITYPE, EXIT,
                              EXTRA, FLAG, GRAMMAR, OPTION, POSITION, ROOM, TO, TRUST)
from src.interpret    import translate_input
from src.grammar      import grammar_gender, depends_on_vowel, add_article
from src.gamescript   import check_trigger, create_tooltip_gamescripts, create_tooltip_specials
from src.log          import log
from src.utility      import (is_same, is_prefix, one_argument, put_final_dot,
                              get_weight_descr, format_for_admin, to_capitalized_words)
from src.web_resource import create_tooltip, create_demi_line, create_icon
from src.wild         import create_wild_to_show, get_wild_exit_descr, create_visual_map

if config.reload_commands:
    reload(__import__("src.commands.command_inventory", globals(), locals(), [""]))
    reload(__import__("src.commands.command_equipment", globals(), locals(), [""]))
from src.commands.command_inventory import get_formatted_inventory_list, get_inventory_list
from src.commands.command_equipment import get_formatted_equipment_list


#= COSTANTI ====================================================================

MESSAGES = {}

# Il look, a differenza degli altri sensi, ha solo i messaggi generici
# verso una direzione
MESSAGES["direction_entity"]        = "Non vedi nulla di interessante %s."
MESSAGES["direction_others"]        = "$n guarda %s."
MESSAGES["direction_wall_others"]   = "$n guarda il muro %s."
MESSAGES["direction_exit_others"]   = "$n guarda l'uscita %s."
MESSAGES["direction_target_others"] = "$n guarda $N %s"


#= FUNZIONI ====================================================================

# (TD) il comando è sempre più simile a quello generico dei sensi, magari accorpare
def command_look(entity, argument="", behavioured=False, use_examine=False):
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    entity = entity.split_entity(1)

    if entity.IS_ACTOR:
        if entity.position < POSITION.SLEEP:
            entity.send_output("Ora come ora puoi solo vedere le [yellow]stelle[close]!")
            return False
        if entity.position == POSITION.SLEEP:
            entity.send_output("Ora come ora puoi solo vedere i tuoi [cyan]sogni[close].")
            return False
        if not entity.has_sight_sense():
            entity.send_output("Non riesci a vedere [darkgray]nulla[close]!")
            return False

    # -------------------------------------------------------------------------

    # Il caso più comune è guardare la stanza muovendosi
    if not argument:
        if entity.location.IS_ROOM:
            return look_a_room(entity, entity.location, behavioured=behavioured, use_examine=use_examine)
        else:
            return look_an_inventory(entity, entity.location)

    # Se invece è stato passato un argomento allora cerca un'eventuale entità
    # prima nel proprio inventario e poi nella stanza
    original_argument = argument
    arg1, argument = one_argument(argument)

    target, target_argument, extra_argument = entity.find_entity_from_args(arg1, argument)
    if target:
        if not target.is_secret_door() or (target.is_secret_door() and len(target_argument) >= config.min_secret_arg_len):
            return look_an_entity(entity, target, extra_argument, behavioured=behavioured, use_examine=use_examine)
    else:
        arg2, argument = one_argument(argument)
        # Controlla solo se arg1 è abbastanza lungo giusto per non confondere
        # l'argomento con possibili direzioni
        if arg2 and len(arg1) > 2:
            # (TD) Altrimenti prova a guardare sotto, dentro o dietro un'entità
            # dovrò aggiungere dei parametri alla find_entity
            if is_prefix(arg1, "sopra") or is_prefix(arg1, "over"):
                target, target_argument, extra_argument = entity.find_entity_from_args(arg2, argument, location=entity.location)
                if target and (target.is_secret_door() and len(argument) >= config.min_secret_arg_len):
                    return look_an_entity(entity, target, extra_argument, behavioured=behavioured, use_examine=use_examine)
            elif is_prefix(arg1, "sotto") or is_prefix(arg1, "under"):
                target, target_argument, extra_argument = entity.find_entity_from_args(arg2, argument, location=entity.location)
                if target and (target.is_secret_door() and len(argument) >= config.min_secret_arg_len):
                    return look_an_entity(entity, target, extra_argument, behavioured=behavioured, use_examine=use_examine)
            elif is_prefix(arg1, "dentro") or is_prefix(arg1, "in"):
                target, target_argument, extra_argument = entity.find_entity_from_args(arg2, argument, location=entity.location)
                if target and (target.is_secret_door() and len(argument) >= config.min_secret_arg_len):
                    # Quando si guarda dentro un'entità si forza l'use_examine a vero
                    return look_an_entity(entity, target, extra_argument, behavioured=behavioured, use_examine=True)
            elif is_prefix(arg1, "dietro") or is_prefix(arg1, "behind"):
                target, target_argument, extra_argument = entity.find_entity_from_args(arg2, argument, location=entity.location)
                if target and (target.is_secret_door() and len(argument) >= config.min_secret_arg_len):
                    return look_an_entity(entity, target, extra_argument, behavioured=behavioured, use_examine=use_examine)
        argument = ("%s %s" % (arg2, argument)).strip()

    # -------------------------------------------------------------------------

    # Cerca un'eventuale extra nella locazione, prima in maniera esatta
    extra = entity.location.extras.get_extra(original_argument, exact=True)
    if extra:
        descr = extra.get_descr("", looker=entity, parent=entity)
        if descr and "no_send" not in descr:
            force_return = check_trigger(entity, "before_look", entity, entity.location, descr, extra, use_examine, behavioured)
            if force_return:
                return True
            force_return = check_trigger(entity.location, "before_looked", entity, entity.location, descr, extra, use_examine, behavioured)
            if force_return:
                return True
            # (bb) Per qualche motivo le extra del solo look hanno un a capo in
            # più, che qui (e anche nelle altre occorrenze) viene strippato
            # come pezza al baco, ma la cosa si dovrebbe correggere in altro modo...
            entity.send_output('''<div style="width:66%%">%s</div>''' % descr.rstrip(), break_line=False)
            if EXTRA.NO_LOOK_ACT not in extra.flags:
                entity.act("$n guarda %s." % add_article(extra.keywords.split()[0], GRAMMAR.INDETERMINATE), TO.OTHERS)
            force_return = check_trigger(entity, "after_look", entity, entity.location, descr, extra, use_examine, behavioured)
            if force_return:
                return True
            force_return = check_trigger(entity.location, "after_looked", entity, entity.location, descr, extra, use_examine, behavioured)
            if force_return:
                return True
            return True

    # Gestisce il look in una direzione, prima in maniera esatta
    if target_argument:
        direction = get_direction(target_argument, True)
        if direction != DIR.NONE:
            return look_at_direction(entity, direction, extra_argument, True, MESSAGES, use_examine, behavioured, "to_dir")

    # Cerca un'eventuale extra nella locazione, ora in maniera prefissa
    extra = entity.location.extras.get_extra(original_argument, exact=False)
    if extra:
        descr = extra.get_descr("", looker=entity, parent=entity)
        if descr and "no_send" not in descr:
            force_return = check_trigger(entity, "before_look", entity, entity.location, descr, extra, use_examine, behavioured)
            if force_return:
                return True
            force_return = check_trigger(entity.location, "before_looked", entity, entity.location, descr, extra, use_examine, behavioured)
            if force_return:
                return True
            entity.send_output('''<div style="width:66%%">%s</div>''' % descr.rstrip(), TO.ENTITY, break_line=False)
            if EXTRA.NO_LOOK_ACT not in extra.flags:
                entity.act("$n guarda %s." % add_article(extra.keywords.split()[0], GRAMMAR.INDETERMINATE), TO.OTHERS)
            force_return = check_trigger(entity, "after_look", entity, entity.location, descr, extra, use_examine, behavioured)
            if force_return:
                return True
            force_return = check_trigger(entity.location, "after_looked", entity, entity.location, descr, extra, use_examine, behavioured)
            if force_return:
                return True
            return True

    # Gestisce il look in una direzione, ora in maniera prefissa
    if target_argument:
        direction = get_direction(target_argument, exact=False)
        if direction != DIR.NONE:
            return look_at_direction(entity, direction, extra_argument, False, MESSAGES, use_examine, behavioured, "to_dir")

    # -------------------------------------------------------------------------

    # Infine controlla se bisogna far visualizzare il cielo
    if (is_prefix(original_argument, "cielo")    or is_prefix(original_argument, "sky")
    or  is_prefix(original_argument, "il cielo") or is_prefix(original_argument, "the sky")):
        return look_the_sky(entity)

    if extra:
        entity.act("Guardi [white]%s[close] ma non vedi nulla di speciale." % original_argument, TO.ENTITY)
    else:
        entity.act("Non vedi nessun [green]%s[close] qui attorno" % original_argument, TO.ENTITY)
    entity.act("$n si guarda attorno alla ricerca di qualcuno o qualcosa che non trova", TO.OTHERS)
    return False
#- Fine Funzione -


#-------------------------------------------------------------------------------

def look_a_room(entity, room, behavioured=False, use_examine=False):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    if not room:
        log.bug("room non è un parametro valido: %r" % room)
        return False

    # use_examine ha valore di verità

    # -------------------------------------------------------------------------

    # Se è buio fa vedere ben poco della stanza
    if room.is_dark() and is_affected(entity, "truesight"):
        result = "È [darkslategray]buio pesto[close] qui..."
        # (BB) quel get_list_of_entities così selvaggio mi sa di baco, lo
        # scopriremo presto appena implementerò le room buie
        entity.send_output(result + room.get_list_of_entities(entity, admin_descrs=True))
        if entity.IS_MOB or entity.IS_ITEM:
            entity.act("$n scruta nel buio.", TO.OTHERS)
        return True

    # Visualizza il nome della stanza e altre informazioni per amministratori
    room_name = room.get_name(entity)
    if "[" not in room_name:
        room_name = "[red]%s[close]" % room_name
    if ROOM.INSIDE not in room.flags:
        if calendar.is_day():
            room_name += ''' <img src="graphics/day.gif" height="16px" width="16px" class="icon" />'''
        else:
            room_name += ''' <img src="graphics/night.gif" height="16px" width="16px" class="icon" />'''

    icon = ""
    if calendar.is_night():
        icon = room.icon_night
    if not icon:
        icon = room.icon
    if icon:
        icon = create_icon(icon)

    if icon:
        result = "%s <b>%s</b>" % (icon, color_first_upper(room_name))
    else:
        result = "<b>%s</b>" % color_first_upper(room_name)

    if entity.trust >= TRUST.MASTER:
        tooltip_id  = "[royalblue]Identificativi[close]\n"
        tooltip_id += "[limegreen]Id[close]: %s\n" % id(room)
        tooltip_id += "[limegreen]Codice[close]: %s\n" % room.code
        tooltip_id += "[limegreen]Destinazione[close]: %d %d %d %s\n" % (room.x, room.y, room.z, room.area.code)
        tooltip_id = create_tooltip(entity.get_conn(), tooltip_id, "{I}")

        tooltip_measures  = "[royalblue]Misure[close]\n"
        tooltip_measures += "[limegreen]Larghezza[close]: %s\n" % room.width
        tooltip_measures += "[limegreen]Profondità[close]: %s\n" % room.depth
        tooltip_measures += "[limegreen]Altezza[close]: %s\n" % room.height
        tooltip_measures = create_tooltip(entity.get_conn(), tooltip_measures, "{M}")

        tooltip_descr = create_tooltip_room_descrs(entity.get_conn(), room)

        tooltip_references = create_tooltip_room_references(entity.get_conn(), room)

        tooltip_extras = create_tooltip_extras(entity.get_conn(), room.extras)
        if tooltip_extras:
            tooltip_extras = " " + tooltip_extras

        tooltip_comment = ""
        if room.comment:
            tooltip_comment = "[royalblue]Commento[close]\n%s" % room.comment
            tooltip_comment = " %s" % create_tooltip(entity.get_conn(), tooltip_comment, "{C}")

        from src.behaviour import create_tooltip_behaviour
        if room.item_behaviour:
            tooltip_behaviour = " " + create_tooltip_behaviour(entity.get_conn(), room.item_behaviour, "Item Behaviour", "{IB}")
        if room.mob_behaviour:
            tooltip_behaviour = " " + create_tooltip_behaviour(entity.get_conn(), room.mob_behaviour, "Mob Behaviour", "{MB}")
        if room.room_behaviour:
            tooltip_behaviour = " " + create_tooltip_behaviour(entity.get_conn(), room.room_behaviour, "Room Behaviour", "{RB}")

        tooltip_gamescripts = create_tooltip_gamescripts(entity.get_conn(), room)
        if tooltip_gamescripts:
            tooltip_gamescripts = " " + tooltip_gamescripts

        tooltip_specials = create_tooltip_specials(entity.get_conn(), room)
        if tooltip_specials:
            tooltip_specials = " " + tooltip_specials

        result += " " + format_for_admin('''settore: %s''' % room.sector)
        result += format_for_admin(" %s %s %s %s%s%s%s%s" % (
            tooltip_id,
            tooltip_measures,
            tooltip_descr,
            tooltip_references,
            tooltip_extras,
            tooltip_comment,
            tooltip_gamescripts,
            tooltip_specials), open_symbol="", close_symbol="")

    # -------------------------------------------------------------------------

    look_descr = ""

    result += "<br>"
    # Visualizza wild e descrizione
    if not room:
        result += "Galleggi nel bel mezzo del [darkslategray]vuoto[close]..."
    elif room.area.wild:
        result += create_wild_to_show(entity)
    elif entity.IS_PLAYER and OPTION.MAP in entity.account.options:
        look_descr = room.get_descr("", looker=entity)
        if look_descr.strip().lower() == "no_send":
            result += '''<div style="float:left; margin-right:5px">%s</div>''' % create_visual_map(entity)
        else:
            result += '''<div style="float:left; margin-right:5px">%s</div><div style="width:66%%">%s</div><div style="clear:both"></div>''' % (create_visual_map(entity), look_descr)
    else:
        look_descr = room.get_descr("", looker=entity)
        if look_descr.strip().lower() == "no_send":
            result += '''Ti guardi intorno.'''
        else:
            result += '''<div style="width:66%%">%s</div>''' % look_descr

    # -------------------------------------------------------------------------

    # Visualizza la lista degli oggetti e degli actor nella stanza
    # (TD) i player e i mob verranno visualizzati da quelli con carisma
    # maggiore a quelli con carisma minore, gli oggetti dal più grande al più
    # piccolo
    result += create_demi_line(entity)
    result_entitites = get_formatted_list_of_entities(entity.location, entity)
    if result_entitites:
        # Viene splittato il contenuto su più righe altrimenti capita il baco
        # dell'output spezzato
        lines = result_entitites.split("\n")
        # (TD) qui per ora l'ultimo elemento è una linea vuota, attenzione non
        # è detto che in futuro sarà così!
        for line in lines[ : -1]:
            if line:
                result += "%s<br>" % line
            else:
                result += "<br>"
        result += create_demi_line(entity)

    # -------------------------------------------------------------------------

    look_translation = translate_input(entity, "look", "en")
    if not look_translation:
        log.bug("look_translation non è valida: %r" % look_translation)
        look_translation = "guarda"

    # Visualizza la lista delle uscite
    # (TD) c'è molto altro da fare, link automatici e porte segrete
    discovered = False
    for direction in DIR.elements:
        if direction not in room.exits:
            continue
        destination_room = room.get_destination_room(direction)
        if not destination_room and not room.area.wild:
            #log.bug("Destinazione o stanza non trovata alla room %d %d %d %s in direzione %s" % (
            #    room.x, room.y, room.z, room.area.code, direction))
            continue

        exit = room.exits[direction]
        flags_info = ""
        if EXIT.NO_LOOK_LIST in exit.flags or EXIT.DIGGABLE in exit.flags:
            if entity.trust <= TRUST.PLAYER:
                continue
            if EXIT.NO_LOOK_LIST in exit.flags:
                flags_info += str(EXIT.NO_LOOK_LIST)
            if EXIT.DIGGABLE in exit.flags:
                flags_info += " " if flags_info else "" + str(EXIT.DIGGABLE)
            flags_info = " " + format_for_admin(flags_info)

        dir_translation = translate_input(entity, exit.direction.english_nocolor, "en")
        if not dir_translation:
            log.bug("dir_translation non è valida: %r" % dir_translation)
            dir_translation = exit.direction.name_nocolor

        # (TD) forse farlo solo l'uscita guardabile e il movimento lo si lascia
        # alle macro
        javascript_code = '''javascript:parent.sendInput('%s %s');''' % (
            look_translation, dir_translation.lower())

        door         = room.get_door(direction, reverse_search=False)
        reverse_door = room.get_door(direction, direct_search=False)

        exit_descr = exit.get_descr("", looker=entity)
        if exit_descr.strip().lower() == "no_send":
            continue
        # In realtà ho scoperto poi che la descr delle exit l'avevo resa
        # obbligatoria e quindi ciò non serve a molto, ma lo tengo lo stesso
        if not exit_descr:
            if room.area.wild:
                exit_descr = get_wild_exit_descr(entity, direction)
            else:
                exit_descr = destination_room.get_name(entity)

        if door and door.door_type:
            if DOOR.CLOSED in door.door_type.flags:
                if DOOR.SECRET in door.door_type.flags and entity.trust == TRUST.PLAYER:
                    continue
                exit_descr = door.get_name(entity) + door.door_type.get_status(door.sex, entity)  # A
            else:
                if reverse_door and reverse_door.door_type:
                    if DOOR.CLOSED in reverse_door.door_type.flags:
                        if DOOR.SECRET in door.door_type.flags and entity.trust == TRUST.PLAYER:
                            exit_descr = "%s%s verso un vicolo cieco."% (door.get_name(entity), door.door_type.get_status(door.sex))
                        else:
                            exit_descr = "%s%s verso %s%s" % (door.get_name(entity), door.door_type.get_status(door.sex, entity), reverse_door.get_name(entity), reverse_door.door_type.get_status(reverse_door.sex, entity))  # A
                    else:
                        exit_descr = "%s%s verso %s" % (door.get_name(entity), door.door_type.get_status(door.sex), exit_descr)  # (B)
                else:
                    exit_descr = "%s%s verso %s" % (door.get_name(entity), door.door_type.get_status(door.sex), exit_descr)  # B
        elif reverse_door and reverse_door.door_type:
            if DOOR.CLOSED in reverse_door.door_type.flags:
                if DOOR.SECRET in reverse_door.door_type.flags and entity.trust == TRUST.PLAYER:
                    continue
                exit_descr = "%s%s" % (color_first_upper(reverse_door.get_name(entity)), reverse_door.door_type.get_status(reverse_door.sex, entity))
            else:
                exit_descr = "%s%s verso %s" % (color_first_upper(reverse_door.get_name(entity)), reverse_door.door_type.get_status(reverse_door.sex), exit_descr)

        tooltips = ""
        if entity.trust >= TRUST.MASTER:
            tooltip_exit = create_tooltip_exit_descrs(entity.get_conn(), exit)

            tooltip_comment = ""
            if (exit.door and exit.door.door_type and exit.door.door_type.comment
            and DOOR.CLOSED in exit.door.door_type.flags):
                tooltip_comment = "[royalblue]Commento Porta[close]\n%s" % exit.door.door_type.comment
                tooltip_comment = " " + create_tooltip(entity.get_conn(), tooltip_comment, "{C}")
            elif exit.comment:
                tooltip_comment = "[royalblue]Commento Uscita[close]\n%s" % exit.comment
                tooltip_comment = " " + create_tooltip(entity.get_conn(), tooltip_comment, "{C}")

            if tooltip_exit or tooltip_comment:
                tooltips = " " + format_for_admin(tooltip_exit + tooltip_comment, open_symbol="", close_symbol="")

        if not discovered:
            discovered = True
            result += "[yellow]Puoi andare verso[close]:"
            result += '''<table class="mud">'''

        if entity.IS_PLAYER and entity.account and OPTION.ITALIAN in entity.account.options:
            direction_string = exit.direction.name_for_look
        else:
            direction_string = exit.direction.english_for_look

        result += '''<tr><td>%s<a href="%s">%s</a></td><td>&nbsp;%s%s%s</td></tr>''' % (
            create_icon(exit.get_icon(room=room)),
            javascript_code,
            direction_string,
            color_first_upper(exit_descr),
            flags_info,
            tooltips)

    if discovered:
        result += '''</table>'''
    else:
        result += "[gray]Nessuna uscita[close].<br>"

    force_return = check_trigger(entity, "before_look", entity, room, look_descr, None, use_examine, behavioured)
    if force_return:
        return True
    force_return = check_trigger(room, "before_looked", entity, room, look_descr, None, use_examine, behavioured)
    if force_return:
        return True

    entity.send_output(result, break_line=False)
    if entity.IS_MOB or entity.IS_ITEM:
        entity.act("$n si guarda attorno.", TO.OTHERS)

    force_return = check_trigger(entity, "after_look", entity, room, look_descr, None, use_examine, behavioured)
    if force_return:
        return True
    force_return = check_trigger(room, "after_looked", entity, room, look_descr, None, use_examine, behavioured)
    if force_return:
        return True

    return True
#- Fine Funzione -


def get_formatted_list_of_entities(location, looker):
    """
    Ritorna una stringa con tutte le entità visualizzate in quella locazione.
    """
    output = []

    from src.find_entity import INSTANCE, COUNTER, ICON, LONG, NO_LOOK_LIST, BURIED, INGESTED, INCOGNITO

    for contained in location.get_list_of_entities(looker, admin_descrs=True):
        if not looker.can_see(contained[INSTANCE]):
            continue
        if FLAG.NO_LOOK_LIST in contained[INSTANCE].flags and looker.trust == TRUST.PLAYER:
            continue
        if FLAG.INTERACTABLE_FROM_OUTSIDE in contained[INSTANCE].flags and contained[INSTANCE].location != location:
            continue
        if contained[INSTANCE].is_hinged():
            continue

        output.append(contained[ICON] + contained[LONG])
        if contained[COUNTER] > 1:
            output.append(" (%s)" % contained[COUNTER])
        if looker.trust > TRUST.PLAYER:
            message = "%s%s%s%s" % (contained[NO_LOOK_LIST], contained[BURIED], contained[INGESTED], contained[INCOGNITO])
            if message:
                output.append(" " + format_for_admin(message.lstrip()))
        output.append("\n")

    return "".join(output)
#- Fine Funzione -


#-------------------------------------------------------------------------------

def look_an_inventory(entity, target):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    if not target:
        log.bug("target non è un parametro valido: %r" % target)
        return False

    # -------------------------------------------------------------------------

    output = get_formatted_inventory_list(entity, target, show_header=False, show_footer=False)
    if output:
        output = "[red]Ti trovi nell'inventario di[close] %s:\n%s" % (target.get_name(entity), output)
    else:
        output = "Non c'è nulla nell'inventario di %s.\n" % target.get_name(entity)

    entity.send_output(output, break_line=False)
    if entity.IS_MOB or entity.IS_ITEM:
        entity.act("$n si guarda attorno.", TO.OTHERS)
    return True
#- Fine Funzione -


#-------------------------------------------------------------------------------

def look_an_entity(entity, target, extra_argument="", behavioured=False, use_examine=False):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    if not target:
        log.bug("target non è un parametro valido: %r" % target)
        return False

    # -------------------------------------------------------------------------

    if not extra_argument:
        return send_entity_descr(entity, target, behavioured=behavioured, use_examine=use_examine)

    extra = target.extras.get_extra(extra_argument, exact=True)
    if extra:
        descr = extra.get_descr("", looker=entity, parent=target)
        if descr and "no_send" not in descr:
            force_return = check_trigger(entity, "before_look", entity, target, descr, extra, use_examine, behavioured)
            if force_return:
                return True
            force_return = check_trigger(target, "before_looked", entity, target, descr, extra, use_examine, behavioured)
            if force_return:
                return True
            output = '''<div style="width:66%%">%s</div>''' % descr.rstrip()
            # Viene utilizzata l'act per un'eventuale conversione dei tag per target
            entity.act(output, TO.ENTITY, target)
            # (TD) grammar is_masculine alle due act sotto
            if EXTRA.NO_LOOK_ACT not in extra.flags:
                if target != entity:
                    entity.act("$n guarda %s di $N." % add_article(extra.keywords.split()[0], GRAMMAR.INDETERMINATE), TO.OTHERS, target)
                else:
                    entity.act("$n guarda %s." % add_article(extra.keywords.split()[0], GRAMMAR.INDETERMINATE, GRAMMAR.POSSESSIVE), TO.OTHERS, target)
            if entity != target:
                entity.act("$n ti guarda %s." % add_article(extra.keywords.split()[0], GRAMMAR.INDETERMINATE), TO.TARGET, target)
            force_return = check_trigger(entity, "after_look", entity, target, descr, extra, use_examine, behavioured)
            if force_return:
                return True
            force_return = check_trigger(target, "after_looked", entity, target, descr, extra, use_examine, behavioured)
            if force_return:
                return True
            return True

    extra = target.extras.get_extra(extra_argument, exact=False)
    if extra:
        descr = extra.get_descr("", looker=entity, parent=target)
        if descr and "no_send" not in descr:
            force_return = check_trigger(entity, "before_look", entity, target, descr, extra, use_examine, behavioured)
            if force_return:
                return True
            force_return = check_trigger(target, "before_looked", entity, target, descr, extra, use_examine, behavioured)
            if force_return:
                return True
            output = '''<div style="width:66%%">%s</div>''' % descr.rstrip()
            # Viene utilizzata l'act per un'eventuale conversione dei tag per target
            entity.act(output, TO.ENTITY, target)
            # (TD) grammar is_masculine alle due act sotto
            if EXTRA.NO_LOOK_ACT not in extra.flags:
                if target != entity:
                    entity.act("$n guarda %s di $N." % add_article(extra.keywords.split()[0], GRAMMAR.INDETERMINATE), TO.OTHERS, target)
                else:
                    entity.act("$n guarda %s." % add_article(extra.keywords.split()[0], GRAMMAR.INDETERMINATE, GRAMMAR.POSSESSIVE), TO.OTHERS, target)
            if entity != target:
                entity.act("$n ti guarda %s." % add_article(extra.keywords.split()[0], GRAMMAR.INDETERMINATE), TO.TARGET, target)
            force_return = check_trigger(entity, "after_look", entity, target, descr, extra, use_examine, behavioured)
            if force_return:
                return True
            force_return = check_trigger(target, "after_looked", entity, target, descr, extra, use_examine, behavioured)
            if force_return:
                return True
            return True

    avoid_inventory = True
    if target.is_sensable_inside("sight", looker=entity, show_message=True):
        avoid_inventory = False

    equipped_target = entity.find_entity(extra_argument, location=target, avoid_inventory=avoid_inventory, avoid_equipment=False)
    if equipped_target:
        return send_entity_descr(entity, equipped_target, target, behavioured=behavioured, use_examine=use_examine)

    # (TD) Qui inoltre dovrò cercare tra le parti del corpo

    if target.IS_ITEM:
        if entity == target:
            if extra:
                entity.act("Ti guardi [white]%s[close] ma non vedi nulla di speciale." % extra_argument, TO.ENTITY, target)
            else:
                entity.act("Cerchi di guardare senza successo il tuo particolare [white]%s[close]" % extra_argument, TO.ENTITY, target)
            entity.act("$n cerca di guardare senza successo un suo particolare", TO.OTHERS, target)
        else:
            if extra:
                entity.act("Guardi il particolare [white]%s[close] di $N ma non vedi nulla di speciale." % extra_argument, TO.ENTITY, target)
            else:
                entity.act("Cerchi di guardare senza successo il particolare [white]%s[close] di $N" % extra_argument, TO.ENTITY, target)
            entity.act("$n cerca di guardare senza successo un particolare di $N", TO.OTHERS, target)
            entity.act("$n cerca di guardare senza successo un tuo particolare", TO.TARGET, target)
    else:
        if entity == target:
            if extra:
                entity.act("Ti guardi [white]%s[close] ma non vedi nulla di speciale." % extra_argument, TO.ENTITY, target)
            else:
                entity.act("Cerchi di guardare senza successo il tuo particolare [white]%s[close]" % extra_argument, TO.ENTITY, target)
            entity.act("$n guarda senza successo un suo particolare", TO.OTHERS, target)
        else:
            if extra:
                entity.act("Osservi il particolare [white]%s[close] di $N ma non vedi nulla di speciale." % extra_argument, TO.ENTITY, target)
            else:
                entity.act("Cerchi di guardare senza successo il particolare [white]%s[close] di $N" % extra_argument, TO.ENTITY, target)
            entity.act("$n guardare senza successo un particolare di $N", TO.OTHERS, target)
            entity.act("$n guarda senza successo un tuo particolare", TO.TARGET, target)

    return False
#- Fine Funzione -


def send_entity_descr(entity, target, carrier=None, behavioured=False, use_examine=False):
    if not entity:
        log.bug("entity non è un parametro valido: %s" % entity)
        return False

    if not target:
        log.bug("target non è un parametro valido: %s" % target)
        return False

    # -------------------------------------------------------------------------

    if use_examine and target.readable_type:
        look_descr = descr = target.readable_type.summary
    else:
        look_descr = descr = target.get_descr("", looker=entity)
    if not descr or descr.strip().lower() == "no_send":
        if target.level <= 2:
            descr = "Non noti nulla di speciale."
        else:
            descr = "Una personalità tiepida ma con grosse potenzialità."

    name = target.get_name(entity)
    if not name:
        log.bug("name ricavato da target %s e guardato dall'entity %s non è valido: %r" % (target.code, entity.code, name))
        return False

    if use_examine:
        weight_descr = get_weight_descr(target.get_total_weight())
        if entity == target:
            descr += "\nPesi in totale %s" % weight_descr
        else:
            descr += "\n%s pesa in totale %s" % (color_first_upper(name), weight_descr)
    else:
        weight_descr = get_weight_descr(target.get_weight())
        if entity == target:
            descr += "\nPesi %s" % weight_descr
        else:
            descr += "\n%s pesa %s" % (color_first_upper(name), weight_descr)

    if not target.location and target.entitype == ENTITYPE.DOOR and target.door_type:
        if entity == target:
            status = target.door_type.get_status(target.sex)
            if status:
                descr += " e sei%s" % status
        else:
            status = target.door_type.get_status(target.sex)
            if status:
                descr += " ed è%s" % status

    if target.entitype == ENTITYPE.CONTAINER and target.container_type:
        if entity == target:
            status = target.container_type.get_status(target.sex)
            if status:
                descr += " e sei%s" % status
        else:
            status = target.container_type.get_status(target.sex)
            if status:
                descr += " ed è%s" % status

    if use_examine and target.IS_ITEM and target.material_percentages:
        if entity == target:
            if len(target.material_percentages) > 1:
                descr += "\nSei composto da %s" % target.material_percentages.get_descr()
            else:
                descr += "\nSei composto %s" % depends_on_vowel(target.material_percentages.get_descr(), "d'", "di ")
        else:
            if len(target.material_percentages) > 1:
                descr += "\nÈ composto da %s" % target.material_percentages.get_descr()
            else:
                descr += "\nÈ composto %s" % depends_on_vowel(target.material_percentages.get_descr(), "d'", "di ")

    # -------------------------------------------------------------------------

    tooltip_content = ""
    if entity.trust > TRUST.MASTER:
        tooltip_id  = "[royalblue]Identificativi[close]\n"
        tooltip_id += "[limegreen]Id[close]: %s\n" % id(target)
        tooltip_id += "[limegreen]Codice[close]: %s\n" % target.code
        tooltip_id += "[limegreen]Livello[close]: %s\n" % target.level
        tooltip_id += "[limegreen]Entitype[close]: %s\n" % target.entitype
        tooltip_id += "[limegreen]Race[close]: %s\n" % target.race
        tooltip_id = create_tooltip(entity.get_conn(), tooltip_id, "{I}")

        tooltip_descr = create_tooltip_entity_descrs(entity.get_conn(), target)

        tooltip_references = create_tooltip_entity_references(entity.get_conn(), target)

        tooltip_extras = create_tooltip_extras(entity.get_conn(), target.extras)
        if target.extras:
            tooltip_extras = " " + tooltip_extras

        tooltip_comment = ""
        if target.comment:
            tooltip_comment = "[royalblue]Commento[close]\n%s" % target.comment
            tooltip_comment = " " + create_tooltip(entity.get_conn(), tooltip_comment, "{C}")

        tooltip_behaviour = ""
        if hasattr(target, "behaviour") and target.behaviour:
            from src.behaviour import create_tooltip_behaviour
            tooltip_behaviour = " " + create_tooltip_behaviour(entity.get_conn(), target.behaviour, "Behaviour", "{B}")

        tooltip_entitypes = create_entitypes_tooltip(entity.get_conn(), target)

        tooltip_gamescripts = create_tooltip_gamescripts(entity.get_conn(), target)
        if tooltip_gamescripts:
            tooltip_gamescripts = " " + tooltip_gamescripts

        tooltip_specials = create_tooltip_specials(entity.get_conn(), target)
        if tooltip_specials:
            tooltip_specials = " " + tooltip_specials

        if target.IS_ITEM:
            typology = "Type: %s" % target.entitype
        else:
            typology = "Race: %s" % target.race
        tooltip_content = " " + format_for_admin("%s" % typology)
        tooltip_content += format_for_admin(" %s %s %s%s%s%s%s%s%s" % (
            tooltip_id,
            tooltip_descr,
            tooltip_references,
            tooltip_extras,
            tooltip_comment,
            tooltip_behaviour,
            tooltip_entitypes,
            tooltip_gamescripts,
            tooltip_specials), open_symbol="", close_symbol="")

    descr += ".%s" % tooltip_content

    # -------------------------------------------------------------------------

    equipment = get_formatted_equipment_list(entity, target, show_header=False, show_footer=False)
    if equipment:
        descr += '''<br>%s%s''' % (create_demi_line(entity), "".join(equipment))

    # -------------------------------------------------------------------------

    # (TD) Questa parte assomiglia alla funzione get_formatted_inventory_list, magari accorpare?
    results = []
    contains = get_inventory_list(entity, target)

    if target.is_sensable_inside("sight", looker=entity, show_message=True):
        if target == entity:
            if contains:
                if target.entitype == ENTITYPE.PLANT:
                    results.append("\n[red]Tra i tuoi rami vi sono[close]:\n")
                else:
                    results.append("\n[red]Stai trasportando[close]:\n")
                results += contains
            else:
                if target.entitype != ENTITYPE.PLANT:
                    results.append("\nNon stai trasportando nulla.")
        else:
            if contains:
                if target.entitype == ENTITYPE.PLANT:
                    results.append("\n[red]Tra i rami vedi[close]:\n")
                else:
                    results.append("\n[red]Contiene[close]:\n")
                results += contains
            else:
                if target.entitype == ENTITYPE.PLANT:
                    results.append("\nNon vi è nulla tra i rami.")

    # -------------------------------------------------------------------------

    if look_descr:
        force_return = check_trigger(entity, "before_look", entity, target, look_descr, None, use_examine, behavioured)
        if force_return:
            return True
        force_return = check_trigger(target, "before_looked", entity, target, look_descr, None, use_examine, behavioured)
        if force_return:
            return True

    descr += "".join(results)
    entity.act('''<span style="width:66%%">%s</span>''' % descr.rstrip("\n"), TO.ENTITY, target)
    if entity == target:
        if carrier:
            entity.act("$n guarda il suo $N.", TO.OTHERS, target)
        else:
            entity.act("$n si guarda.", TO.OTHERS)
    else:
        if carrier:
            entity.act("$n guarda $N di $a.", TO.OTHERS, target, carrier)
            entity.act("$n ti guarda.", TO.TARGET, target)
        else:
            entity.act("$n guarda $N.", TO.OTHERS, target)
            entity.act("$n ti guarda.", TO.TARGET, target)

    if look_descr:
        force_return = check_trigger(entity, "after_look", entity, target, look_descr, None, use_examine, behavioured)
        if force_return:
            return True
        force_return = check_trigger(target, "after_looked", entity, target, look_descr, None, use_examine, behavioured)
        if force_return:
            return True

    return True
#- Fine Funzione -


def look_at_direction(entity, direction, argument, exact, messages, use_examine, behavioured, from_or_to, readable=False):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    if not direction:
        log.bug("direction non è un parametro valido: %r" % direction)
        return False

    # argument può essere una stringa vuota

    # exact ha valore di verità

    if not messages:
        log.bug("messages non è un parametro valido: %r" % messages)
        return False

    # use_examine ha valore di verità

    # behavioured ha valore di verità

    if from_or_to not in ("from_dir", "to_dir"):
        log.bug("from_or_to non è un parametro valido: %r" % from_or_to)
        return False

    # readable ha valore di verità

    # -------------------------------------------------------------------------

    if not readable:
        if not entity.location.IS_ROOM:
            force_return = check_trigger(entity, "before_look", entity, entity.location, "", None, use_examine, behavioured)
            if force_return:
                return False
            force_return = check_trigger(entity.location, "before_looked", entity, entity.location, "", None, use_examine, behavioured)
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

            force_return = check_trigger(entity, "after_look", entity, entity.location, "", None, use_examine, behavioured)
            if force_return:
                return False
            force_return = check_trigger(entity.location, "after_looked", entity, entity.location, "", None, use_examine, behavioured)
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
                descr = extra.get_descr("", looker=entity, parent=entity)
                if EXTRA.NO_LOOK_ACT in extra.flags:
                    show_to_others = False
        elif not readable:
            descr = wall.get_descr("", looker=entity)
        if descr and "no_send" not in descr:
            force_return = check_trigger(entity, "before_" + "read" if readable else "look", entity, entity.location, descr, wall, use_examine, behavioured)
            if force_return:
                return True
            force_return = check_trigger(entity.location, "before_" + "readed" if readable else "looked", entity, entity.location, descr, wall, use_examine, behavioured)
            if force_return:
                return True

            entity.send_output('''<div style="width:66%%">%s</div>''' % descr, break_line=False)
            if "%s" in messages["direction_wall_others"]:
                entity.act(messages["direction_wall_others"] % direction.to_dir, TO.OTHERS)
            else:
                entity.act(messages["direction_wall_others"], TO.OTHERS)
            force_return = check_trigger(entity, "after_" + "read" if readable else "look", entity, entity.location, descr, wall, use_examine, behavioured)
            if force_return:
                return True
            force_return = check_trigger(entity.location, "after_" + "readed" if readable else "looked", entity, entity.location, descr, wall, use_examine, behavioured)
            if force_return:
                return True
            return True

    # -------------------------------------------------------------------------

    door = entity.location.get_door(direction)
    if door and DOOR.CLOSED in door.door_type.flags:
        if DOOR.SECRET in door.door_type.flags:
            entity.act(messages["direction_entity"] % getattr(direction, from_or_to), TO.ENTITY)
            entity.act(messages["direction_others"] % direction.to_dir, TO.OTHERS)
            return False
        else:
            show_to_others = True
            if argument:
                descr = ""
                extra = door.extras.get_extra(argument, exact=exact)
                if readable and EXTRA.READABLE not in extra.flags:
                    extra = None
                if extra:
                    descr = extra.get_descr("", looker=entity, parent=entity)
                    if EXTRA.NO_LOOK_ACT in extra.flags:
                        show_to_others = False
            elif not readable:
                descr = door.get_descr("", looker=entity)
            if descr and "no_send" not in descr:
                force_return = check_trigger(entity, "before_look", entity, door, descr, None, use_examine, behavioured)
                if force_return:
                    return True
                force_return = check_trigger(entity.location, "before_looked", entity, door, descr, None, use_examine, behavioured)
                if force_return:
                    return True

                entity.send_output('''<div style="width:66%%">%s</div>''' % descr, break_line=False)
                if "%s" in messages["direction_target_others"]:
                    entity.act(messages["direction_target_others"] % direction.to_dir, TO.OTHERS, door)
                else:
                    entity.act(messages["direction_target_others"], TO.OTHERS, door)
                force_return = check_trigger(entity, "after_look", entity, door, descr, None, use_examine, behavioured)
                if force_return:
                    return True
                force_return = check_trigger(entity.location, "after_looked", entity, door, descr, None, use_examine, behavioured)
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
                descr = extra.get_descr("", looker=entity, parent=entity)
                if EXTRA.NO_LOOK_ACT in extra.flags:
                    show_to_others = False
        elif not readable:
            descr = exit.get_descr("", looker=entity)
        if descr and "no_send" not in descr:
            force_return = check_trigger(entity, "before_look", entity, entity.location, descr, exit, use_examine, behavioured)
            if force_return:
                return True
            force_return = check_trigger(entity.location, "before_looked", entity, entity.location, descr, exit, use_examine, behavioured)
            if force_return:
                return True

            entity.send_output('''<div style="width:66%%">%s</div>''' % descr, break_line=False)
            if "%s" in messages["direction_exit_others"]:
                entity.act(messages["direction_exit_others"] % direction.to_dir, TO.OTHERS)
            else:
                entity.act(messages["direction_exit_others"], TO.OTHERS)
            force_return = check_trigger(entity, "after_look", entity, entity.location, descr, exit, use_examine, behavioured)
            if force_return:
                return True
            force_return = check_trigger(entity.location, "after_looked", entity, entity.location, descr, exit, use_examine, behavioured)
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
            descr = extra.get_descr("", looker=entity, parent=entity)
            if descr and "no_send" not in descr:
                force_return = check_trigger(entity, "before_look", entity, door, descr, None, use_examine, behavioured)
                if force_return:
                    return True
                force_return = check_trigger(entity.location, "before_looked", entity, door, descr, None, use_examine, behavioured)
                if force_return:
                    return True

                entity.send_output('''<div style="width:66%%">%s</div>''' % descr, break_line=False)
                if "%s" in messages["direction_target_others"]:
                    entity.act(messages["direction_target_others"] % direction.to_dir, TO.OTHERS, door)
                else:
                    entity.act(messages["direction_target_others"], TO.OTHERS, door)
                force_return = check_trigger(entity, "after_look", entity, door, descr, None, use_examine, behavioured)
                if force_return:
                    return True
                force_return = check_trigger(entity.location, "after_looked", entity, door, descr, None, use_examine, behavioured)
                if force_return:
                    return True
                return True

    if readable:
        return False
    else:
        destination_room = entity.location.get_destination_room(direction)
        if not destination_room:
            force_return = check_trigger(entity, "before_look", entity, entity.location, "", str(direction), use_examine, behavioured)
            if force_return:
                return False
            force_return = check_trigger(entity.location, "before_looked", entity, entity.location, "", str(direction), use_examine, behavioured)
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
            force_return = check_trigger(entity, "after_look", entity, entity.location, "", str(direction), use_examine, behavioured)
            if force_return:
                return False
            force_return = check_trigger(entity.location, "after_looked", entity, entity.location, "", str(direction), use_examine, behavioured)
            if force_return:
                return False
            return False

        # Fa visualizzare il nome della stanza
        # (TD) non farlo vedere se la stanza non è visibile, buia o che
        # sarà bene unire questa ricerca del nome della stanza con la stessa
        # che viene visualizza nell'elenco delle uscite della stanza
        descr = color_first_upper(put_final_dot(destination_room.get_name(entity)))

        force_return = check_trigger(entity, "before_look", entity, entity.location, descr, destination_room, use_examine, behavioured)
        if force_return:
            return True
        force_return = check_trigger(entity.location, "before_looked", entity, entity.location, descr, destination_room, use_examine, behavioured)
        if force_return:
            return True

        entity.send_output('''<div style="width:66%%">%s</div>''' % descr, break_line=False)
        if "%s" in messages["direction_others"]:
            entity.act(messages["direction_others"] % direction.to_dir, TO.OTHERS)
        else:
            entity.act(messages["direction_others"], TO.OTHERS)

        force_return = check_trigger(entity, "after_look", entity, entity.location, descr, destination_room, use_examine, behavioured)
        if force_return:
            return True
        force_return = check_trigger(entity.location, "after_looked", entity, entity.location, descr, destination_room, use_examine, behavioured)
        if force_return:
            return True
        return True
#- Fine Funzione -


#-------------------------------------------------------------------------------

STARMAP_WIDTH  = 72
STARMAP_HEIGHT =  8
          #****************** CONSTELLATIONS and STARS *****************************
          #  Cygnus     Mars        Orion      Dragon       Cassiopeia          Venus
          #           Ursa Ninor                           Mercurius     Pluto
          #               Uranus              Leo                Crown       Raptor
          #*************************************************************************
STARMAP = ("                                               C. C.                  g*"
           "    O:       R*        G*    G.  W* W. W.          C. C.    Y* Y. Y.    "
           "  O*.                c.          W.W.     W.            C.       Y..Y.  "
           "O.O. O.              c.  G..G.           W:      B*                   Y."
           "     O.    c.     c.                     W. W.                  r*    Y."
           "     O.c.     c.      G.             P..     W.        p.      Y.   Y:  "
           "        c.                    G*    P.  P.           p.  p:     Y.   Y. "
           "                 b*             P.: P*                 p.p:             ")

SUN = ("\\`|'/"
       "- O -"
       "/.|.\\")

MOON = (" @@@ "
        "@@@@@"
        " @@@ ")

def look_the_sky(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    # (TD)
    entity.act("Il cielo è sereno", TO.ENTITY)
    entity.act("$n guarda il cielo", TO.OTHERS)
    return True

    # (TD) Se in alto è aperto allora fa vedere il cielo
#- Fine Funzione -


#-------------------------------------------------------------------------------

def _create_tooltip_descrs(obj):
    """
    Crea un pezzo di testo per una tooltip che serve a tutti gli oggetti che
    hanno delle descrizioni.
    """
    if not obj:
        log.bug("obj non è un parametro valido %r" % obj)
        return ""

    # -------------------------------------------------------------------------

    tooltip = []

    if obj.descr:               tooltip.append("[limegreen]Descr[close]: lunga %d"             % len(obj.descr))
    if obj.descr_night:         tooltip.append("[limegreen]DescrNight[close]: lunga %d"        % len(obj.descr_night))
    if obj.descr_hearing:       tooltip.append("[limegreen]DescrHearing[close]: lunga %d"      % len(obj.descr_hearing))
    if obj.descr_hearing_night: tooltip.append("[limegreen]DescrHearingNight[close]: lunga %d" % len(obj.descr_hearing_night))
    if obj.descr_smell:         tooltip.append("[limegreen]DescrSmell[close]: lunga %d"        % len(obj.descr_smell))
    if obj.descr_smell_night:   tooltip.append("[limegreen]DescrSmellNight[close]: lunga %d"   % len(obj.descr_smell_night))
    if obj.descr_touch:         tooltip.append("[limegreen]DescrTouch[close]: lunga %d"        % len(obj.descr_touch))
    if obj.descr_touch_night:   tooltip.append("[limegreen]DescrTouchNight[close]: lunga %d"   % len(obj.descr_touch_night))
    if obj.descr_taste:         tooltip.append("[limegreen]DescrTaste[close]: lunga %d"        % len(obj.descr_taste))
    if obj.descr_taste_night:   tooltip.append("[limegreen]DescrTasteNight[close]: lunga %d"   % len(obj.descr_taste_night))
    if obj.descr_sixth:         tooltip.append("[limegreen]DescrSixth[close]: lunga %d"        % len(obj.descr_sixth))
    if obj.descr_sixth_night:   tooltip.append("[limegreen]DescrSixthNight[close]: lunga %d"   % len(obj.descr_sixth_night))

    return tooltip
#- Fine Funzione -


def create_tooltip_room_descrs(conn, room):
    if not conn:
        if not engine.test_inputs_mode:
            log.bug("conn non è un parametro valido %r" % conn)
        return ""

    if not room:
        log.bug("room non è un parametro valido %r" % room)
        return ""

    # -------------------------------------------------------------------------

    tooltip = ["[royalblue]Descrizioni[close]"]

    tooltip.append("[limegreen]Name[close]: %s" % room.name)
    tooltip.append("[limegreen]Short[close]: %s" % room.short)
    if room.short_night:
        tooltip.append("[limegreen]ShortNight[close]: %s" % room.short_night)
    tooltip += _create_tooltip_descrs(room)

    return create_tooltip(conn, "\n".join(tooltip), "{D}")
#- Fine Funzione -


def create_tooltip_exit_descrs(conn, exit):
    if not conn:
        if not engine.test_inputs_mode:
            log.bug("conn non è un parametro valido %r" % conn)
        return ""

    if not exit:
        log.bug("exit non è un parametro valido %r" % exit)
        return ""

    # -------------------------------------------------------------------------

    tooltip = []
    if exit.door and exit.door.door_type and DOOR.CLOSED in exit.door.door_type.flags:
        tooltip.append("[royalblue]Keywords Porta[close]")
        tooltip.append(exit.door.get_keywords_attr())
        tooltip.append("[royalblue]Descrizioni Porta[close]")
        tooltip += _create_tooltip_descrs(exit.door)
        tooltip.append("[royalblue]Flags Porta[close]")
        tooltip.append(repr(exit.door.door_type.flags))
    else:
        tooltip.append("[royalblue]Descrizioni Uscita[close]")
        tooltip += _create_tooltip_descrs(exit)
        tooltip.append("[royalblue]Flags Uscita[close]")
        tooltip.append(repr(exit.flags))

    return create_tooltip(conn, "\n".join(tooltip), "{D}")
#- Fine Funzione -


def create_tooltip_entity_descrs(conn, obj):
    if not conn:
        if not engine.test_inputs_mode:
            log.bug("conn non è un parametro valido %r" % conn)
        return ""

    if not obj:
        log.bug("obj non è un parametro valido %r" % obj)
        return ""

    # -------------------------------------------------------------------------

    tooltip = ["[royalblue]Descrizioni[close]"]

    if hasattr(obj, "keywords_name"):
        tooltip.append("[limegreen]KeywordsName[close]: %s" % obj.keywords_name)
    tooltip.append("[limegreen]Name[close]: %s" % obj.name)

    if hasattr(obj, "keywords_short"):
        tooltip.append("[limegreen]KeywordsShort[close]: %s" % obj.keywords_short)
    tooltip.append("[limegreen]Short[close]: %s" % obj.short)

    if obj.short_night:
        if hasattr(obj, "keywords_short_night"):
            tooltip.append("[limegreen]KeywordsShortNight[close]: %s" % obj.keywords_short_night)
        tooltip.append("[limegreen]ShortNight[close]: %s" % obj.short_night)

    tooltip += _create_tooltip_descrs(obj)

    return create_tooltip(conn, "\n".join(tooltip), "{D}")
#- Fine Funzione -


def create_tooltip_extras(conn, extras):
    """
    Crea il testo relativo alle tooltip, per gli admin, che elencano le extra
    delle varie entità.
    """
    if not conn:
        if not engine.test_inputs_mode:
            log.bug("conn non è un parametro valido %r" % conn)
        return ""

    # -------------------------------------------------------------------------

    if not extras:
        return ""
        
    tooltip = ["[royalblue]Extras[close]"]
    for extra in extras:
        tooltip.append("Keywords: %s" % extra.keywords)

        if EXTRA.DAY_ONLY in extra.flags:
            tooltip.append(" (DAY_ONLY)")
        if EXTRA.NIGHT_ONLY in extra.flags:
            tooltip.append(" (NIGHT_ONLY)")
        tooltip += _create_tooltip_descrs(extra)

    return create_tooltip(conn, "\n".join(tooltip), "{E}")
#- Fine Funzione -


def create_tooltip_room_references(conn, room):
    if not conn:
        if not engine.test_inputs_mode:
            log.bug("conn non è un parametro valido %r" % conn)
        return ""

    if not room:
        log.bug("room non è un parametro valido: %r" % room)
        return ""

    # -------------------------------------------------------------------------

    tooltip = ["[royalblue]Riferimenti[close]"]

    if room.code in database["rooms"]:
        tooltip.append("Database: [green]esistente nel database %s[close]" % room.ACCESS_ATTR)
    else:
        tooltip.append("Database: [red]inesistente nel database %s[close]" % room.ACCESS_ATTR)

    if not room.area:
        tooltip.append("Area: [red]None[close]")
    elif room not in room.area.rooms.values():
        tooltip.append("Area: %s [red]ma nella lista delle room dell'area non c'è[close]" % room.area.code)
    else:
        tooltip.append("Area: [green]%s[close]" % room.area.code)

    return create_tooltip(conn, "\n".join(tooltip), "{R}")
#- Fine Funzione -


def create_tooltip_entity_references(conn, obj):
    if not conn:
        if not engine.test_inputs_mode:
            log.bug("conn non è un parametro valido %r" % conn)
        return ""

    if not obj:
        log.bug("obj non è un parametro valido: %r" % obj)
        return ""

    # -------------------------------------------------------------------------

    tooltip = ["[royalblue]Riferimenti[close]"]

    if obj.code in database[obj.ACCESS_ATTR]:
        tooltip.append("Database: [green]esistente nel database %s[close]" % obj.ACCESS_ATTR)
    else:
        tooltip.append("Database: [red]inesistente nel database %s[close]" % obj.ACCESS_ATTR)

    if not obj.area:
        tooltip.append("Area: [red]None[close]")
    elif obj not in getattr(obj.area, obj.ACCESS_ATTR):
        tooltip.append("Area: %s [red]ma nella lista %s dell'area non c'è[close]" % (
            obj.area.code, obj.ACCESS_ATTR))
    else:
        tooltip.append("Area: [green]%s[close]" % obj.area.code)

    if not obj.location:
        tooltip.append("Location: [red]None[close]")
    elif obj not in getattr(obj.location, obj.ACCESS_ATTR):
        tooltip.append("Location: %s [red]ma nella lista %s del %s non c'è[close]" % (
            obj.location.code, obj.ACCESS_ATTR, obj.location.ACCESS_ATTR[-1]))
    else:
        tooltip.append("Location: [green]%s[close]" % obj.location.code)

    if not obj.previous_location or not obj.previous_location():
        tooltip.append("PreviousLocation: None (spesso non è un errore)")
    else:
        tooltip.append("PreviousLocation: [green]%s[close]" % obj.previous_location().code)

    tooltip.append("Quantità: %d\n" % obj.quantity)

    if FLAG.EXTRACTED in obj.flags:
        tooltip.append("Extracted: [red]Sì[close]")

    if FLAG.WEAKLY_EXTRACTED in obj.flags:
        tooltip.append("WeaklyExtracted: [red]Sì[close]")

    if obj.extract_timeout:
        tooltip.append("ExtractTimeout: [white]%d[close] (valore originale)" % obj.extract_timeout.minutes)

    return create_tooltip(conn, "\n".join(tooltip), "{R}")
#- Fine Funzione -


def create_entitypes_tooltip(conn, entity):
    if not conn:
        if not engine.test_inputs_mode:
            log.bug("conn non è un parametro valido: %r" % conn)
        return ""

    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    tooltips = []
    for entitype_element in ENTITYPE.elements:
        entitype_attr_name = entitype_element.get_mini_code() + "_type"
        if not hasattr(entity, entitype_attr_name):
            continue
        entitype = getattr(entity, entitype_attr_name)
        if entitype:
            title = "%s" % to_capitalized_words(entitype_attr_name)
            symbol = "{%s}" % "".join([c for c in title if c.isupper()])  # Oppure un po' meno veloce ma forse più pulita:  filter(lambda c: c.isupper(), title)
            # Non fa nulla se ci sono delle tooltype con simbolo uguale
            tooltips.append(create_entitype_tooltip(conn, entitype, title, symbol))

    return " ".join(tooltips)
#- Fine Funzione -


def create_entitype_tooltip(conn, entitype, title, symbol):
    if not conn:
        if not engine.test_inputs_mode:
            log.bug("conn non è un parametro valido: %r" % conn)
        return ""

    if not entitype:
        log.bug("entitype non è un parametro valido: %r" % entitype)
        return ""

    if not title:
        log.bug("title non è un parametro valido: %r" % title)
        return ""

    if not symbol:
        log.bug("symbol non è un parametro valido: %r" % symbol)
        return ""

    # -------------------------------------------------------------------------

    lines = []
    lines.append("[royalblue]%s[close]" % title)
    for attr_name in sorted(entitype.__dict__):
        if attr_name[0] == "_":
            continue
        value = getattr(entitype, attr_name)
        if value:
            # (bb) questo check serve ad evitare che la tooltip sballi con
            # contenuto html, attualmente è un mistero che anche la tools-tooltip
            # sballi anche utilizzando il tag di div
            if attr_name in entitype.MULTILINES:
                value = len(value)
            lines.append("[limegreen]%s[close]: %s" % (to_capitalized_words(attr_name), value))

    return " " + create_tooltip(conn, "<br>".join(lines), symbol)
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""

    syntax += "look\n"
    syntax += "look <qualcuno o qualcosa>\n"
    syntax += "look <particolare> <di qualcuno o qualcosa>\n"
    syntax += "look dentro <qualcuno o qualcosa da guardare>\n"
    syntax += "look dietro <qualcuno o qualcosa da guardare>\n"
    syntax += "look sotto <qualcuno o qualcosa da guardare>\n"
    syntax += "look sopra <qualcuno o qualcosa da guardare>\n"
    syntax += "look <in una direzione>\n"
    syntax += "look <particolare> <di una direzione>\n"
    syntax += "look cielo\n"

    return syntax
#- Fine Funzione -
