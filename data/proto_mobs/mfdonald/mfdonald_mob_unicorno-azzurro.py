# -*- coding: utf-8 -*-


#= IMPORT ======================================================================

import random

from src.defer   import defer_random_time
from src.log     import log
from src.utility import is_prefix, multiple_arguments, random_marks

from src.commands.command_say import command_say


#= FUNZIONI ====================================================================

def before_listen_rpg_channel(listener, speaker, target, phrase, ask, exclaim, behavioured):
    # Con una probabilità dell'10%
    if random.randint(1, 10) != 1:
        return

    # Continua solo se sta per parlare l'unicorno rosa
    if speaker.prototype.code != "mfdonald_mob_unicorno-rosa":
        return

    # Spezza la frase detta in più parole (o gruppi di parole tra virgolette)
    words = multiple_arguments(phrase)

    # Controlla se vi sia almeno una parola che inizi nella maniera voluta
    # tra quelle dette (occhio che lo script si attiva anche se l'unicorno dice
    # parole come 'ringhia', per evitare questo bisognerebbe utilizzare la
    # funzione is_same sempre dal modulo utility)
    if not is_prefix(("drin", "ring"), words):
        return

    # Aggiungendo casualmente qualche punto esclamativo a quello che viene detto
    to_say = "Ring!%s Ring!%s" % (random_marks(0, 3), random_marks(0, 3))
    command_say(listener, to_say)

    # Avendo anticipato l'unicorno rosa blocca quello che stava per dire
    return True
#- Fine Funzione -


def after_listen_rpg_channel(listener, speaker, target, phrase, ask, exclaim, behavioured):
    words = multiple_arguments(phrase)
    if not is_prefix(("drin", "ring"), words):
        return

    if speaker.prototype.code != "mfdonald_mob_unicorno-rosa":
        return

    # Aggiunge casualmente un prefisso, qualche o finale e punti esclamativi
    # e di domanda finali, risponde all'unicorno rosa
    prefix = ""
    if random.randint(1, 10) == 1:
        prefix = "Ha%s " % ("." * random.randint(2, 4))
    to_say = "a %s %sHall%s?%s" % (speaker.get_numbered_keyword(looker=listener), prefix, "o" * random.randint(1, 3), random_marks(1, 1))
    # Attende qualche secondo.. dopotutto deve raggiungere il telefono!
    # Attenzione ad inserire un numero di secondi troppo alto, altrimenti
    # l'unicorno rosa potrebbe dire più spesso ring ring di quanto l'unicorno
    # azzurro possa rispondere, riempiendo così la ram di callback :P
    # Comunque in questo caso non abbiamo assolutamente questo problema
    defer_random_time(1, 3, command_say, listener, to_say)
#- Fine Funzione -
