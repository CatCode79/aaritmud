# -*- coding: utf-8 -*-

#= IMPORT ======================================================================

import random
import re

from src.defer   import defer, defer_if_possible
from src.enums   import TO
from src.utility import is_same

from src.commands.command_say     import command_say
from src.commands.command_whisper import command_whisper


#= COSTANTI ====================================================================

ALFA_ONLY_PATTERN = re.compile("[^a-zA-Zì ]+")


#= FUNZIONI ====================================================================

def after_looked(player, apprendista, descr, detail, use_examine, behavioured):
    print " >>> SPECIALS <<<", apprendista.specials      
    if not player.IS_PLAYER:
        return

    if apprendista.specials:
        to_say = "a %s *allegro* Benvenuto nella bottega del tagliapietre! Eseguiamo lavorazioni per tutti i gusti e tutte le voglie!" % player.code
        command_say(apprendista, to_say)
        return
 
    if random.randint(1, 2) != 1:
        return

    apprendista.specials["apprendista:player_code"] = player.code
    apprendista.specials["apprendista_situation"] = "look"

    to_say = "a %s Il tuo sguardo indagatore mi dice che ti piacerebbe conoscere qualche segreto riguardo a questo villaggio, mi sbaglio?" % player.code
    command_say(apprendista, to_say)

    defer(60, del_specials_status, apprendista, "look")    
#- Fine Funzione -


def before_listen_say(listener, speaker, apprendista, phrase, ask, exclaim, behavioured):
    if not speaker.IS_PLAYER:
        return
   
    if not apprendista.specials or not "apprendista:player_code" in apprendista.specials or not "apprendista_situation" in apprendista.specials:
        return

    player_code = apprendista.specials["apprendista:player_code"]
    situation = apprendista.specials["apprendista_situation"]

    if situation == "look":
        if speaker.code != player_code:
            to_say = "a %s *allegro* Benvenuto nella bottega del tagliapietre! Eseguiamo lavorazioni per tutti i gusti e tutte le voglie!" % speaker.code
            command_say(apprendista, to_say)
            return

        if is_same(phrase, "no"):
            defer(1, reveal_secret, apprendista, speaker)
            defer(60, del_specials, apprendista)
            return
            
        defer(1, ask_again, apprendista, speaker)
        defer(60, del_specials_status, apprendista, "domanda")    
        return

    if situation == "domanda": 
        if speaker.code != player_code:
            to_say = "a %s *allegro* Benvenuto nella bottega del tagliapietre! Eseguiamo lavorazioni per tutti i gusti e tutte le voglie!" % speaker.code
            command_say(apprendista, to_say)
            return

        phrase = ALFA_ONLY_PATTERN.sub("", phrase)
        if is_same(phrase, "si"):
            defer(1, reveal_secret, apprendista, speaker)
            defer(60, del_specials, apprendista)
            return
        defer(1, no_secret, apprendista, speaker)
        del_specials(apprendista)
        return

    if situation == "segreto_svelato":
        defer(1, no_more_secrets, apprendista, speaker)
        del_specials(apprendista)
#- Fine Funzione -


def reveal_secret(apprendista, speaker):
    # Normale che capiti visto che la funzione viene deferrata
    if not apprendista or not speaker:
        return

    # Qui è concettualmente meglio utilizzare il comando whisper piuttosto che
    # la act per poter giocare in futuro sulle lingue
    print ">>> SEGRETO <<<", speaker, apprendista
    to_whisper = "a %s *all'orecchio* Una delle leggende che i tagliapietre si tramandano di maestro in apprendista narra di una pietra, una pietra dalle proprietà eccezionali." % speaker.code
    command_whisper(apprendista, to_whisper)
    to_whisper = "a %s *all'orecchio* Un altro mito, di un altro tempo, racconta di accadimenti prodigiosi... nel centro del villaggio... nel cuore della foresta." % speaker.code
    defer_if_possible(1, apprendista, speaker, command_whisper, apprendista, to_whisper)

    apprendista.specials["apprendista_situation"] = "segreto_svelato"
#- Fine Funzione -


def ask_again(apprendista, speaker):
    # Normale che capiti visto che la funzione viene deferrata
    if not apprendista or not speaker:
        return

    to_say = "a %s *deluso* Ok, forse non si siamo capiti, è un segreto che nessun'altro sarebbe disposto a svelarti." % speaker.code
    command_say(apprendista, to_say)
    to_say = "a %s Te lo richiedo: vuoi conoscere un segreto riguardo a questo villaggio?" % speaker.code
    defer_if_possible(1, apprendista, speaker, command_say, apprendista, to_say)

    apprendista.specials["apprendista_situation"] = "domanda"
#- Fine Funzione -


def no_secret(apprendista, speaker):
    # Normale che capiti visto che la funzione viene deferrata
    if not apprendista or not speaker:
        return

    to_say = "a %s Oh beh... Peggio per te!" % speaker.code
    command_say(apprendista, to_say)
#- Fine Funzione -


def no_more_secrets(apprendista, speaker):
    # Normale che capiti visto che la funzione viene deferrata
    if not apprendista or not speaker:
        return

    to_say = "a %s Questo è tutto ciò che avevo da dirti, non c'è altro." % speaker.code
    command_say(apprendista, to_say)
#- Fine Funzione -


def del_specials(apprendista):
    # Normale che capiti visto che la funzione viene deferrata
    if not apprendista:
        return

    print ">>> ELIMINAZIONE SPECIALS <<<"
    if "apprendista_situation" in apprendista.specials:
        del(apprendista.specials["apprendista_situation"])
    if "apprendista:player_code" in apprendista.specials:
        del(apprendista.specials["apprendista:player_code"])
#- Fine Funzione -


def del_specials_status(apprendista, status):
    # Normale che capiti visto che la funzione viene deferrata
    if not apprendista:
        return

    if "apprendista_situation" in apprendista.specials and apprendista.specials["apprendista_situation"] == status:
        del_specials(apprendista)
        print ">>> STATUS <<<", status
#- Fine Funzione -
