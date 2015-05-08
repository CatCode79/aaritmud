# -*- coding: utf-8 -*-

"""
Modulo per la gestione del comando afk.
"""


#= IMPORT ======================================================================

from src.enums import FLAG, TO
from src.log   import log


#= FUNZIONI ====================================================================

def command_afk(entity, argument=""):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    if not entity.IS_PLAYER:
        return False

    if FLAG.AFK in entity.flags:
        entity.flags -= FLAG.AFK
        entity.send_output("Avverti i giocatori attorno a te che non sei più lontano dalla tastiera.")
        entity.act("$n sembra essere [cyan]tornato in sé[close].", TO.OTHERS)
    else:
        entity.flags += FLAG.AFK
        entity.send_output("Ora tutti i giocatori che verranno in contattato con te sapranno che sei lontano dalla tastiera.")
        entity.act("$n [cyan]sembra essere assente[close] con lo %s e con la mente..." % entity.eye_colorize("sguardo"), TO.OTHERS)

    return True
#- Fine Funzione -
