# -*- coding: utf-8 -*-

#= IMPORT ======================================================================

import random

from src.defer import defer

from src.commands.command_say import command_say


#= FUNZIONI ====================================================================

def after_look(player, spiritello, descr, detail, use_examine, behavioured):
    if random.randint(0, 1):  
        to_say = "a %s *piagnucoloso* Il luccichino! Il mio luccichino, malvagio ragno avido e scontroso!" % player.code
    else:
        to_say = "a self *piagnucoloso* Il luccichino! Il mio luccichino, malvagio ragno... malvagio..."

    command_say(spiritello, to_say)
#- Fine Funzione -


def after_listen_say(listener, speaker, target, phrase, behavioured):
    if not speaker.IS_PLAYER:
        return

    if not target:
        return

    if not target.IS_ROOM:
        return

    if target.can_see(speaker):
        to_say = "a %s *adirato* Odioso malnato sputaveleno! Fuggito in quell'impossibile intrico di gallerie" % speaker.code
    else:
        to_say = "*spaventato* Chi sei? Cosa vuoi da me? Lasciami in pace, vai via!"
    command_say(target, to_say)
    #defer(1, command_say, target, to_say)
#- Fine Funzione -
