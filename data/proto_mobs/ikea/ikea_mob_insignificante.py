# -*- coding: utf-8 -*-

#= IMPORT ======================================================================

from src.defer import defer

from src.commands.command_say import command_say


#= FUNZIONI ====================================================================

def before_listen_say(listener, speaker, target, phrasei, ask, exclaim, behavioured):
    if not target:
        return
    if target.can_see(speaker):
        to_say = "a %s *adirato* [red]prima[close] che mi arrabbi vattene!" % speaker.code
    else:
        to_say = "*spaventato* Chi sei? Cosa vuoi da me? Lasciami in pace, vai via [red]prima[close] che mi arrabbi!"
    #command_say(target, to_say)
    defer(1, command_say, target, to_say)
#- Fine Funzione -


def after_listen_say(listener, speaker, target, phrase, ask, exclaim, behavioured):
    if not target:
        return
    if target.can_see(speaker):
        to_say = "a %s *adirato* è [red]tardi[close] mi hai indisposto!" % speaker.code
    else:
        to_say = "*spaventato* Chi sei? Cosa vuoi da me? Lasciami in pace, vai via [red]ora[close] che mi hai adirato!"
    command_say(target, to_say)

    if "vagytur" in target.specials:
        to_say = "Vagytur nelle special!"
    else:
        to_say = "Vagytur non è nelle special"
    defer(2, command_say, target, to_say)
#- Fine Funzione -

