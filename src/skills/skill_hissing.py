# -*- coding: utf-8 -*-


#= IMPORT ======================================================================

from src.channel import rpg_channel
from src.enums   import CHANNEL, SKILL
from src.log     import log


#= COSTANTI ====================================================================


#= FUNZIONI ====================================================================

# (TD) l'hissing e il thundering come attacco possono essere effettuate solo ad inizio combattimento
def skill_hissing(entity, argument):
    """
    Skill voce sibilante, impaurisce il nemico sibilandogli contro qualcosa.
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    if not argument and argument != "":
        log.bug("argument non è un parametro valido: %r" % argument)
        return False

    # -------------------------------------------------------------------------

    execution_success = rpg_channel(entity, argument, CHANNEL.HISSING)
    if not execution_success:
        return False

    # La gestione dell'argomento vuoto viene effettuata dalla rpg_channel.
    # Anche se la parte skillosa del comando non viene effettuata il comando
    # è considerato eseguito
    if argument == "":
        return True

    # (TD) scopiazzare dalla thunder
    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    return "hissing <nome bersaglio> <messaggio da sibilare al bersaglio>"
#- Fine Funzione -
