# -*- coding: utf-8 -*-
# orchi troll nani thepa e drow (look e accompagnati fuori)

#= IMPORT ======================================================================

import random

from src.calendar import calendar
from src.defer    import defer, defer_random_time, defer_if_possible
from src.enums    import RACE, TO
from src.log      import log
from src.room     import Destination
from src.social   import get_target_implicetely
from src.utility  import is_same

from src.commands.command_down import command_down
from src.commands.command_say  import command_say
from src.commands.command_up   import command_up


#= COSTANTI ====================================================================

ASTRONOMA_PROTO_CODE = __name__.split(".")[0]

HATED_RACES = (RACE.ORC, RACE.DWARF, RACE.DROW, RACE.THEPA)


#= FUNZIONI ====================================================================

def after_bow(player, target, argument):
    greet_the_astronoma(player, target)
#- Fine Funzione -

def after_wave(player, target, argument):
    greet_the_astronoma(player, target)
#- Fine Funzione -

def after_smile(player, target, argument):
    greet_the_astronoma(player, target)
#- Fine Funzione -

def greet_the_astronoma(player, astronoma):
    # Se astronoma non è valida significa che i social non sono diretti
    # esplicitamente all'astronoma e quindi esce
    if not astronoma:
        return

    if "is_greetable" in astronoma.specials and astronoma.specials["is_greetable"] == False:
        return

    player_code = player.get_numbered_keyword(looker=astronoma)

    if player.race in HATED_RACES:
        to_say = "a %s *astiosamente* Il tuo inchino non è accettato in questo luogo per il sangue innocente sparso, per l'avidità di alcuni..." % player_code
        defer_if_possible(1, 2, astronoma, player, command_say, astronoma, to_say)
        return

    to_say = "a %s *placidamente* Buongiorno a te stranier$o curios$o, sei benvenut$o nella Torre per guardare le Stelle...." % player_code
    defer_if_possible(1, 2, astronoma, player, command_say, astronoma, to_say)

    astronoma.specials["is_greetable"] = False
    defer(60, reset_greetable, astronoma)
#- Fine Funzione -

def reset_greetable(astronoma):
    # Normale che possa accadere visto che è una funzione deferrata
    if not astronoma:
        return
    astronoma.specials["is_greetable"] = True
#- Fine Funzione -


#-------------------------------------------------------------------------------

def before_touched(player, astronoma, descr, detail, behavioured):
    player.act("Fai come per allungare la $hand su $N.", TO.ENTITY, astronoma)
    player.act("$n fa lo sconsiderato gesto di allungare una $hand.", TO.TARGET, astronoma)
    player.act("$n fa come per allungare una mano su $N.", TO.OTHERS, astronoma)
    return teleport(player, astronoma)
#- Fine Funzione -

def before_tasted(player, astronoma, descr, detail, behavioured):
    player.act("Fai come per assaggiare $N, ma...", TO.ENTITY, astronoma)
    player.act("$n fa lo sconsiderato gesto di assaggiarti...", TO.TARGET, astronoma)
    player.act("$n fa come per voler assaggiare $N, ma...", TO.OTHERS, astronoma)
    return teleport(player, astronoma)
#- Fine Funzione -

def teleport(player, astronoma):
    player_code = player.get_numbered_keyword(looker=astronoma)

    if player.race in HATED_RACES:
        to_say = "a %s Gesto sconsiderato straniero. Troppo per rimanere in questo luogo..." % player_code
        command_say(astronoma, to_say)
        return False

    # Ricava la destinazione per il teletrasporto
    destination_room = Destination(3, 4, 0, "citta-raminghe").get_room()
    if not destination_room:
        return False

    player.act("Una [gold]nube [white]bianca[close] ti avvolge non appena $N fa un gesto.\nQuando la nebbia sparisce ti ritrovi altrove.", TO.ENTITY, astronoma)
    player.act("$n sparisce nel nulla quando $N fa un gesto.", TO.OTHERS, astronoma)
    player = player.from_location(1)
    player.to_location(destination_room, use_look=False)
    player.act("$n compare dal nulla.", TO.OTHERS)
    return True
#- Fine Funzione -


#-------------------------------------------------------------------------------

def after_listened(player, astronoma, descr, detail, behavioured):
    if "expecting_answer" in astronoma.specials and astronoma.specials["expecting_answer"] == True:
        return

    player_code = player.get_numbered_keyword(looker=astronoma)

    if player.race in HATED_RACES:
        to_say = "a %s *astiosamente* Ti hanno condotto sin qui propositi di distruzione? La tua razza non è qui ben accetta." % player_code
        defer_if_possible(1, 2, astronoma, player, command_say, astronoma, to_say)
        return

    to_say = "a %s *placidamente* Sei giunt$o sin qui stranier$o perché ti ha spinto il desiderio d'osservar il cielo e perderti negli infiniti spazi stellari?" % player_code
    defer_if_possible(1, 2, astronoma, player, command_say, astronoma, to_say)

    astronoma.specials["expecting_answer"] = True
    defer(15, reset_expecting_answer, player, astronoma)
#- Fine Funzione -

def after_nod(player, target, argument):
    astronoma = get_target_implicetely(player, target, ASTRONOMA_PROTO_CODE)
    if not astronoma or "expecting_answer" not in astronoma.specials:
        return
    if not astronoma.specials["expecting_answer"]:
        return

    player_code = player.get_numbered_keyword(looker=astronoma)

    if astronoma.area.code != "citta-raminghe":
        to_say = "a %s *mestamente* Se solo mi trovassi nella mia città..." % player_code
        defer_if_possible(1, 2, astronoma, player, command_say, astronoma, to_say)
        return

    if astronoma.location.prototype.code != "citta-raminghe_room_osservatorio-02":
        to_say = "a %s *mestamente* Se solo mi trovassi nel luogo in cui lavoro..." % player_code
        defer_if_possible(1, 2, astronoma, player, command_say, astronoma, to_say)
        return

    defer_if_possible(1, 2, astronoma, player, incites_to_follow, player, astronoma)
    astronoma.specials["expecting_answer"] = False
#- Fine Funzione -

def after_shake(player, target, argument):
    astronoma = get_target_implicetely(player, target, ASTRONOMA_PROTO_CODE)
    if not astronoma or "expecting_answer" not in astronoma.specials:
        return
    astronoma.specials["expecting_answer"] = False

    player_code = player.get_numbered_keyword(looker=astronoma)

    to_say = "a %s *indispettita* Oh..." % player_code
    defer_if_possible(1, 2, astronoma, player, command_say, astronoma, to_say)
    astronoma.specials["expecting_answer"] = False
#- Fine Funzione -

def after_listen_rpg_channel(astronoma, player, target, phrase, ask, exclaim, behavioured):
    if target and target != astronoma:
        return

    if is_same(phrase, "si"):
        after_nod(player,astronoma, phrase)
    elif is_same(phrase, "no"):
        after_shake(player, astronoma, phrase)
#- Fine Funzione -

def reset_expecting_answer(player, astronoma):
    # Possibile visto che questa funzione è deferrata
    if not player or not astronoma:
        return

    if "expecting_answer" in astronoma.specials and astronoma.specials["expecting_answer"]:
        astronoma.specials["expecting_answer"] = False
        if player.location == astronoma.location:
            astronoma.act("Smette di attendere una risposta da $N.", TO.OTHERS, player)
            astronoma.act("$n smette di attendere una risposta da te.", TO.TARGET, player)
#- Fine Funzione -

def incites_to_follow(player, astronoma):
    # Possibile visto che questa funzione è deferrata
    if not player or not astronoma:
        return

    player_code = player.get_numbered_keyword(looker=astronoma)

    if calendar.is_day():
        to_say = "a %s *sorridendo* Allora torna da me quando è notte." % player_code
        command_say(astronoma, to_say)
        return

    to_say = "a %s *sorridendo* Seguimi allora stranier$o curios$o!" % player_code
    command_say(astronoma, to_say)
    defer_random_time(1, 2, command_up, astronoma)

    # Invia tra quasi due minuti un messaggio al pg se è ancora lì e poi poco dopo torna giù
    to_say = "a %s *sorridendo* Torno giù a seguire le mie occupazioni..." % player_code
    defer_if_possible(115, 118, astronoma, player, command_say, astronoma, to_say)
    defer(120, command_down, astronoma)
#- Fine Funzione -
