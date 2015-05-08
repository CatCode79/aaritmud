# -*- coding: utf-8 -*-

"""
Modulo per la gestione del comando per scavare o dissotterrare.
"""


#= IMPORT ======================================================================

import random

from src.color      import color_first_upper
from src.database   import database
from src.enums      import DIR, DOOR, EXIT, FLAG, GRAMMAR, TO
from src.exit       import get_direction
from src.grammar    import add_article
from src.interpret  import ActionInProgress
from src.item       import Item
from src.gamescript import check_trigger
from src.mob        import Mob
from src.utility    import one_argument


#= COSTANTI ====================================================================

VERBS = {"infinitive" : "[sandybrown]scavare[close]",
         "you2"       : "[sandybrown]scavarti[close]",
         "you"        : "[sandybrown]scavi[close]",
         "it"         : "[sandybrown]scava[close]"}

DIG_SECONDS = 2.5
DIG_PROBABILITY = 10


#= FUNZIONI ====================================================================

def command_dig(entity, argument="", verbs=VERBS, behavioured=False):
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    entity = entity.split_entity(1)

    # (TD) resistenza al comando se charmati

    # (TD) non si può scavare se si sta mondando a cavallo o altra posizione strana

    # (TD) fare la skill di scavo basata sulla forza e il wait per poterla riutilizzare

    if not argument:
        return dig_a_location(entity, verbs, behavioured)
    else:
        return dig_an_exit(entity, argument, verbs, behavioured)
#- Fine Funzione -


def dig_an_exit(entity, argument, verbs, behavioured):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return False

    if not verbs:
        log.bug("verbs non è un parametro valido: %r" % verbs)
        return False

    # behavioured ha valore di verità

    # -------------------------------------------------------------------------

    location = entity.location

    arg, argument = one_argument(argument);
    direction = get_direction(arg)
    if direction == DIR.NONE:
        entity.act("Non trovi nessuna direzione [white]%s[close] in cui %s." % (arg, verbs["infinitive"]), TO.ENTITY, location)
        entity.act("$n sembra voler %s in una direzione, ma appare spaesato." % verbs["infinitive"], TO.OTHERS, location)
        entity.act("$n sembra voler %s in una direzione, ma appare spaesato." % verbs["you2"], TO.TARGET, location)
        return False

    if not location.IS_ROOM:
        entity.act("Non trovi in un luogo ove poter %s %s." % (verbs["infinitive"], direction.to_dir), TO.ENTITY, location)
        entity.act("$n sembra voler %s %s nonostante non si trovi in un luogo con delle uscite." % (verbs["infinitive"], direction.to_dir), TO.OTHERS, location)
        entity.act("Non sei un luogo in cui si possa %s %s, eppure $n ci sta provando lo stesso." % (verbs["infinitive"], direction.to_dir), TO.TARGET, location)
        return False

    # (TD) Questo si potrebbe convertire in metodo se dovesse servire nuovamente
    exit = None
    has_secret_door = False
    if direction in location.exits:
        exit = location.exits[direction]
        door = location.get_door(direction)
        if door and door.door_type and DOOR.SECRET in door.door_type.flags and DOOR.CLOSED in door.door_type.flags:
            has_secret_door = True

    if exit and EXIT.DIGGABLE not in exit.flags and not has_secret_door:
        entity.act("Non sapresti proprio come %s %s: c'è già un'uscita!" % (verbs["infinitive"], direction.to_dir), TO.ENTITY, location)
        entity.act("$n sembra voler %s %s: ma c'è già un'uscita!" % (verbs["infinitive"], direction.to_dir), TO.OTHERS, location)
        entity.act("$n sembra voler %s %s: ma li hai già un'uscita!" % (verbs["infinitive"], direction.to_dir), TO.TARGET, location)
        return False

    entity.act("Cominci a %s %s." % (verbs["infinitive"], direction.to_dir), TO.ENTITY, location)
    entity.act("$n comincia a %s %s." % (verbs["infinitive"], direction.to_dir), TO.OTHERS, location)
    entity.act("$n comincia a %s %s." % (verbs["you2"], direction.to_dir), TO.TARGET, location)

    force_return = check_trigger(entity, "before_dig", entity, location, exit, direction, behavioured)
    if force_return:
        return True
    force_return = check_trigger(location, "before_digged", entity, location, exit, direction, behavioured)
    if force_return:
        return True

    # (TD) Togliere un po' di energie nella scavata
    if exit and not has_secret_door:
        defer_later_function = digging_a_diggable_exit_1
    else:
        defer_later_function = digging_an_inexistent_exit_1
    entity.action_in_progress = ActionInProgress(DIG_SECONDS, defer_later_function, stop_digging_on_exit, entity, location, direction, verbs, behavioured)
    return True
#- Fine Funzione -


def dig_a_location(entity, verbs, behavioured):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    if not verbs:
        log.bug("verbs non è un parametro valido: %r" % verbs)
        return False

    # behavioured ha valore di verità

    # -------------------------------------------------------------------------

    location = entity.location

    if location.IS_ROOM:
        sector = add_article(str(location.sector), location.sector.genre, location.sector.number, GRAMMAR.PREPOSITION_IN)
        if location.sector.dig_difficulty >= 100:
            entity.act("Ti è impossibile poter %s %s." % (verbs["infinitive"], sector), TO.ENTITY, location)
            entity.act("$n cerca di %s %s ma gli è impossibile." % (verbs["infinitive"], sector), TO.OTHERS, location)
            entity.act("$n cerca di %s ma gli è impossibile." % verbs["you2"], TO.TARGET, location)
            return False
        elif location.sector.dig_difficulty >= 80:
            entity.act("Cominci a %s con molta difficoltà %s." % (verbs["infinitive"], sector), TO.ENTITY, location)
            entity.act("$n comincia a %s con molta difficoltà %s." % (verbs["infinitive"], sector), TO.OTHERS, location)
            entity.act("$n comincia a %s con molta difficoltà." % verbs["you"], TO.TARGET, location)
            seconds = DIG_SECONDS + 2
        elif location.sector.dig_difficulty >= 60:
            entity.act("Cominci a %s con difficoltà %s." % (verbs["infinitive"], sector), TO.ENTITY, location)
            entity.act("$n comincia a %s con difficoltà %s." % (verbs["infinitive"], sector), TO.OTHERS, location)
            entity.act("$n comincia a %s con difficoltà." % verbs["you"], TO.TARGET, location)
            seconds = DIG_SECONDS + 1
        elif location.sector.dig_difficulty >= 40:
            entity.act("Cominci a %s con fatica %s." % (verbs["infinitive"], sector), TO.ENTITY, location)
            entity.act("$n comincia a %s con fatica %s." % (verbs["infinitive"], sector), TO.OTHERS, location)
            entity.act("$n comincia a %s con fatica." % verbs["you"], TO.TARGET, location)
            seconds = DIG_SECONDS + 0.5
        elif location.sector.dig_difficulty >= 20:
            entity.act("Cominci a %s %s." % (verbs["infinitive"], sector), TO.ENTITY, location)
            entity.act("$n comincia a %s %s." % (verbs["infinitive"], sector), TO.OTHERS, location)
            entity.act("$n comincia a %s." % verbs["you"], TO.TARGET, location)
            seconds = DIG_SECONDS
        else:
            entity.act("Cominci a %s facilmente %s." % (verbs["infinitive"], sector), TO.ENTITY, location)
            entity.act("$n comincia a %s facilmente %s." % (verbs["infinitive"], sector), TO.OTHERS, location)
            entity.act("$n comincia a %s facilmente." % verbs["you"], TO.TARGET, location)
            seconds = DIG_SECONDS - 0.5
    else:
        entity.act("Cominci a %s qui." % verbs["infinitive"], TO.ENTITY, location)
        entity.act("$n comincia a %s qui." % verbs["infinitive"], TO.OTHERS, location)
        entity.act("$n comincia a %s." % verbs["you"], TO.TARGET, location)
        seconds = DIG_SECONDS

    force_return = check_trigger(entity, "before_dig", entity, location, location, DIR.NONE, behavioured)
    if force_return:
        return True
    force_return = check_trigger(location, "before_digged", entity, location, location, DIR.NONE, behavioured)
    if force_return:
        return True

    entity.action_in_progress = ActionInProgress(seconds, digging_a_location_1, stop_digging_on_location, entity, location, verbs, behavioured)
    return True
#- Fine Funzione -


#-------------------------------------------------------------------------------

def stop_digging_on_exit(entity, location, direction, verbs, behavioured):
    """
    Funzione chiamata nel qual caso le deferLater vengano interrotte da un'altra
    azione interattiva dell'entità.
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return

    if not location:
        log.bug("location non è un parametro valido: %r" % location)
        return

    if not direction or direction == DIR.NONE:
        log.bug("direction non è un paramtro valido: %r" % direction)
        return

    if not verbs:
        log.bug("verbs non è un parametro valido: %r" % verbs)
        return

    # -------------------------------------------------------------------------

    entity.act("Smetti di %s %s." % (verbs["infinitive"], direction.to_dir), TO.ENTITY, location)
    entity.act("$n smette di %s %s." % (verbs["infinitive"], direction.to_dir), TO.OTHERS, location)
    entity.act("$n smette di %s %s." % (verbs["you2"], direction.to_dir), TO.TARGET, location)
#- Fine Funzione -


def stop_digging_on_location(entity, location, verbs, behavioured):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return

    if not location:
        log.bug("location non è un parametro valido: %r" % location)
        return

    if not verbs:
        log.bug("verbs non è un parametro valido: %r" % verbs)
        return

    # -------------------------------------------------------------------------

    if location.IS_ROOM:
        entity.act("Smetti di %s in $N." % verbs["infinitive"], TO.ENTITY, location)
        entity.act("$n smette di %s in $N." % verbs["infinitive"], TO.OTHERS, location)
        entity.act("$n smette di %s." % verbs["you2"], TO.TARGET, location)
    else:
        entity.act("Smetti di %s qui." % verbs["infinitive"], TO.ENTITY, location)
        entity.act("$n smette di %s qui." % verbs["infinitive"], TO.OTHERS, location)
        entity.act("$n smette di %s." % verbs["you2"], TO.TARGET, location)
#- Fine Funzione -


#-------------------------------------------------------------------------------

def digging_an_inexistent_exit_1(entity, location, direction, verbs, behavioured):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return


    if not location:
        log.bug("location non è un parametro valido: %r" % location)
        return

    if not direction or direction == DIR.NONE:
        log.bug("direction non è un paramtro valido: %r" % direction)
        return

    if not verbs:
        log.bug("verbs non è un parametro valido: %r" % verbs)
        return

    # -------------------------------------------------------------------------

    entity.act("\nContinui a %s %s." % (verbs["infinitive"], direction.to_dir), TO.ENTITY, location)
    entity.act("$n continua a %s %s." % (verbs["infinitive"], direction.to_dir), TO.OTHERS, location)
    entity.act("$n continua a %s %s." % (verbs["you2"], direction.to_dir), TO.TARGET, location)
    entity.send_prompt()

    entity.action_in_progress = ActionInProgress(DIG_SECONDS+1, digging_an_inexistent_exit_2, stop_digging_on_exit, entity, location, direction, verbs, behavioured)
#- Fine Funzione -


def digging_an_inexistent_exit_2(entity, location, direction, verbs, behavioured):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return

    if not location:
        log.bug("location non è un parametro valido: %r" % location)
        return

    if not direction or direction == DIR.NONE:
        log.bug("direction non è un paramtro valido: %r" % direction)
        return

    if not verbs:
        log.bug("verbs non è un parametro valido: %r" % verbs)
        return

    # -------------------------------------------------------------------------

    entity.action_in_progress = None

    entity.act("\nSmetti di %s %s, non hai trovato niente. Tanta fatica per nulla!" % (verbs["infinitive"], direction.to_dir), TO.ENTITY, location)
    entity.act("$n smette di %s, sembra non aver trovato niente %s." % (verbs["infinitive"], direction.to_dir), TO.OTHERS, location)
    entity.act("$n smette di %s, sembra non aver trovato niente %s." % (verbs["you2"], direction.to_dir), TO.TARGET, location)
    entity.send_prompt()

    # (TD) imparare un po' la skill scava, ma poco

    force_return = check_trigger(entity, "after_dig", entity, location, None, direction, behavioured)
    if force_return:
        return True
    force_return = check_trigger(location, "after_digged", entity, location, None, direction, behavioured)
    if force_return:
        return True
#- Fine Funzione -


#-------------------------------------------------------------------------------

def digging_a_diggable_exit_1(entity, location, direction, verbs, behavioured):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return

    if not location:
        log.bug("location non è un parametro valido: %r" % location)
        return

    if not direction or direction == DIR.NONE:
        log.bug("direction non è un paramtro valido: %r" % direction)
        return

    if not verbs:
        log.bug("verbs non è un parametro valido: %r" % verbs)
        return

    # -------------------------------------------------------------------------

    entity.act("\nContinui a %s %s." % (verbs["infinitive"], direction.to_dir), TO.ENTITY, location)
    entity.act("$n continua a %s %s." % (verbs["infinitive"], direction.to_dir), TO.OTHERS, location)
    entity.act("$n continua a %s %s." % (verbs["you2"], direction.to_dir), TO.TARGET, location)
    entity.send_prompt()

    entity.action_in_progress = ActionInProgress(DIG_SECONDS+1, digging_a_diggable_exit_2, stop_digging_on_exit, entity, location, direction, verbs, behavioured)
#- Fine Funzione -


def digging_a_diggable_exit_2(entity, location, direction, verbs, behavioured):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return

    if not location:
        log.bug("location non è un parametro valido: %r" % location)
        return

    if not direction or direction == DIR.NONE:
        log.bug("direction non è un paramtro valido: %r" % direction)
        return

    if not verbs:
        log.bug("verbs non è un parametro valido: %r" % verbs)
        return

    # -------------------------------------------------------------------------

    # (TD) Bisognerà fare i check se l'uscita esista ancora

    entity.action_in_progress = None

    entity.act("\nSmetti di %s quando i tuoi sforzi rivelano l'esistenza di un passaggio %s!" % (verbs["infinitive"], direction.to_dir), TO.ENTITY, location)
    entity.act("$n smette di %s quando scopre un passaggio %s." % (verbs["infinitive"], direction.to_dir), TO.OTHERS, location)
    entity.act("$n smette di %s quando scopre un passaggio %s." % (verbs["you2"], direction.to_dir), TO.TARGET, location)
    entity.send_prompt()

    location.exits[direction].flags -= EXIT.DIGGABLE
    reverse_exit = location.get_reverse_exit(direction)
    if reverse_exit:
        reverse_exit.flags -= EXIT.DIGGABLE

    # Rimuove l'eventuale flag di secret alle eventuali due porte ai lati
    normal_door = location.get_door(direction, reverse_search=False)
    if normal_door and normal_door.door_type and DOOR.SECRET in normal_door.door_type.flags:
        normal_door.door_type.flags -= DOOR.SECRET
    reverse_door = location.get_door(direction, direct_search=True)
    if reverse_door and reverse_door.door_type and DOOR.SECRET in reverse_door.door_type.flags:
        reverse_door.door_type.flags -= DOOR.SECRET

    # (TD) imparare un po' la skill scava dai propri successi

    force_return = check_trigger(entity, "after_dig", entity, location, None, direction, behavioured)
    if force_return:
        return True
    force_return = check_trigger(location, "after_digged", entity, location, None, direction, behavioured)
    if force_return:
        return True
#- Fine Funzione -


#-------------------------------------------------------------------------------

def digging_a_location_1(entity, location, verbs, behavioured):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return

    if not location:
        log.bug("location non è un parametro valido: %r" % location)
        return

    if not verbs:
        log.bug("verbs non è un parametro valido: %r" % verbs)
        return

    # -------------------------------------------------------------------------

    sector = add_article(str(location.sector), location.sector.genre, location.sector.number, GRAMMAR.PREPOSITION_IN)

    entity.act("\nContinui a %s %s." % (verbs["infinitive"], sector), TO.ENTITY, location)
    entity.act("$n continua a %s %s." % (verbs["infinitive"], sector), TO.OTHERS, location)
    entity.act("$n continua a %s %s." % (verbs["you2"], sector), TO.TARGET, location)
    entity.send_prompt()

    entity.action_in_progress = ActionInProgress(DIG_SECONDS+1, digging_a_location_2, stop_digging_on_location, entity, location, verbs, behavioured)
#- Fine Funzione -


def digging_a_location_2(entity, location, verbs, behavioured):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return

    if not location:
        log.bug("location non è un parametro valido: %r" % location)
        return

    if not verbs:
        log.bug("verbs non è un parametro valido: %r" % verbs)
        return

    # -------------------------------------------------------------------------

    targets = []
    for target in location.iter_contains():
        if FLAG.BURIED in target.flags:
            targets.append(target)

    # C'è una possibilità su cento che venga trovato qualcosa di interessante
    # (TD) magari la probabilità aumentarla facendola sulla base della skill scava
    # (TD) magari aggiungere un affect per invalidare tentativi robotizzati di scavaggio continuo
    if not targets and random.randint(1, 100) < DIG_PROBABILITY:
        codes = database["areas"]["rip"].proto_items.keys()
        codes += database.randomizable_codes
        codes += database.race_money_codes
        codes += database.seed_codes

        code = random.choice(codes)
        if code.split("_")[1] == "item":
            targets = [Item(code)]
        else:
            targets = [Mob(code)]

        # Per le monete viene impostata anche una quantità casuale.
        # Qui in sostanza viene detto che si possono trovare da 1 a 1000 monete
        # di rame e al massimo solo 1 moneta di mithril, valori intermedi sono
        # inversamente proporzionali al valore della moneta stessa
        if targets[0].money_type:
            copper_value = min(targets[0].money_type.copper_value, 1000)
            targets[0].quantity = random.randint(1, int(1000 / copper_value))

        # (TD) Bisognerebbe inserire un affect nella locazione che impedisca di
        # scavare ancora lì per tot tempo
        targets[0].inject(location)

    # L'esperienza per aver scavato la prima volta nella stanza viene data
    # a prescindere che sia stato trovata un'entità o meno
    if entity.IS_PLAYER and location.IS_ROOM:
        if location.prototype.code in entity.digged_rooms:
            entity.digged_rooms[location.prototype.code] += 1
        else:
            entity.digged_rooms[location.prototype.code] = 1
            reason = "per aver scavato %s" % location.get_name(looker=entity)
            entity.give_experience(location.area.level, reason=reason)

    if not targets:
        entity.act("\n%s ma non trovi proprio nulla di interessante." % color_first_upper(verbs["you"]), TO.ENTITY, location)
        entity.act("$n %s una buca in $N senza trovare nulla di interessante." % verbs["it"], TO.OTHERS, location)
        entity.act("$n ti %s una buca senza trovare nulla di interessante." % verbs["it"], TO.TARGET, location)
        entity.send_prompt()
        entity.action_in_progress = None
        return

    target = random.choice(targets)
    target = target.split_entity(random.randint(1, target.quantity))

    entity.action_in_progress = None

    entity.act("\nFinisci di %s scoprendo $N!" % verbs["infinitive"], TO.ENTITY, target)
    entity.act("$n termina di %s dopo che ha scoperto qualcosa." % verbs["infinitive"], TO.OTHERS, target)
    entity.act("$n termina di %s dopo che ti ha scoperto nel terreno." % verbs["infinitive"], TO.TARGET, target)
    entity.act("$n termina di %s dopo che ha scoperto $a dentro di te." % verbs["infinitive"], TO.TARGET, location, target)
    entity.send_prompt()

    target.flags -= FLAG.BURIED
    # Se era un seme o una pianta allora ne ferma la crescita 
    if target.seed_type:
        target.seed_type.stop_growth()
    if target.plant_type:
        target.plant_type.stop_growth()

    # (TD) imparare un po' la skill scava dai propri successi

    force_return = check_trigger(entity, "after_dig", entity, location, target, DIR.NONE, behavioured)
    if force_return:
        return True
    force_return = check_trigger(location, "after_digged", entity, location, target, DIR.NONE, behavioured)
    if force_return:
        return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""
    syntax += "dig\n"
    syntax += "dig <direzione>\n"

    return syntax
#- Fine Funzione -
