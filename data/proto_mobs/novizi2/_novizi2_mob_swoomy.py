# -*- coding: utf-8 -*-

#= COMMENT ====================================================================

# mob che pone indovinelli


#= IMPORT =====================================================================

import random
import re

from src.defer   import defer, defer_if_possible
from src.entity  import remove_little_words
from src.utility import is_same

from src.commands.command_say import command_say


#= RIDDLE =====================================================================

RIDDLES = {
    1 : ["Nome dell'impetuosa combattente", "idrusa"],
    2 : ["È più grande degli dei, più cattivo del male stesso. Lo posseggono i poveri ma i ricchi non ne hanno bisgono ma a mangiarne si muore. Che cos'è?", "niente", "nulla"],
    3 : ["Chi la costruisce la vende, chi la compera non la usa, chi la usa non sa chi sono. Di che si tratta?", "bara", "bare", "tomba", "tombe"],
    4 : ["Chi la fa non lo dice, chi la prende non lo sa, chi lo sa non la vuole.", "moneta falsa", "falsa moneta", "moneta contraffatta", "contraffatta moneta", "monete false", "false monete", "monete contraffatte", "contraffatte monete"],
    5 : ["Si bagna quando asciuga. Cos'è?", "asciugamano", "asciugamani", "salvietta", "salviette"],
    6 : ["Un cavallo di ferro con una lunga coda morbida, più veloce va il cavallo e più la coda si accorcia.", "ago filo", "filo ago", "aghi fili", "fili aghi", "ago e filo", "filo e ago"]}


#= COSTANTI ====================================================================

ALFA_ONLY_PATTERN = re.compile("[^a-zA-Zì ]+")
WAITING_TIME = 60  # Secondi di attesa per la risposta


#= FUNZIONI ====================================================================

def after_listen_say(mob, player, target, phrase, behavioured):
    if not player.IS_PLAYER:
        return

    # Verifico che gli si parli con "a"
    if target != mob:
        return

    # Se non sta attendendo una risposta chiede l'indovinello
    if not mob.specials or not mob.specials["wait_for_reply"]:
        riddle_number = random.choice(RIDDLES.keys())
        to_say = "a %s *zugiolone* " % player.code
        to_say += RIDDLES[riddle_number][0]
        defer_if_possible(1, mob, player, command_say, mob, to_say)
        mob.specials["wait_for_reply"] = True
        mob.specials["player"] = player.code
        mob.specials["riddle"] = riddle_number
        message = "*asciutto* tempo scaduto e nessuno ha indovinato..."
        defer(WAITING_TIME, reset_timer, mob, message)
        return

    # Ripulisce la risposta del giocatore da paccottaglie e da articoli e simili
    phrase = ALFA_ONLY_PATTERN.sub("", phrase)
    phrase = remove_little_words(phrase)

    riddle_number = mob.specials["riddle"]
    print riddle_number
    solutions = RIDDLES[riddle_number][1 : ]
    for solution in solutions:
        print "soluzioni: ", solution, " frasi: ",  phrase
        # (TD) qui al posto della is_same ci starebbe bene una futura implementazione di soundex
        if is_same(phrase, solution):
            congratulation(mob, player)
            reset_timer(mob)
            break
#- Fine Funzione -


def congratulation(mob, player):
    if player.code == mob.specials["player"]:
        to_say = "a %s *illuminato* ebbrav$o cannabuscolo, risposta esatta ed eccoti dei px" % player.code
        player.experience += 10
    else:
        to_say = "a %s *zugiolone* bravò!" % player.code
    defer_if_possible(1, 1, command_say, mob, to_say)
#- Fine Funzione -


def reset_timer(mob, message=""):
    # E' normale visto che tale funzione viene deferrata
    if not mob:
        return

    if "wait_for_reply" in mob.specials:
        del(mob.specials["wait_for_reply"])
    if "player" in mob.specials:
        del(mob.specials["player"])
    if "riddle" in mob.specials:
        del(mob.specials["riddle"])

    if message:
        command_say(mob, message)
#- Fine Funzione -


def after_shake(player, mob, bob):
    reset_timer(mob)
#- Fine Funzione -
