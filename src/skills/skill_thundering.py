# -*- coding: utf-8 -*-


#= IMPORT ======================================================================

from src.channel import rpg_channel
from src.config  import config
from src.enums   import CHANNEL, SKILL
from src.fight   import start_fight
from src.log     import log
from src.skill   import check_skill
from src.utility import is_same, one_argument


#= COSTANTI ====================================================================


#= FUNZIONI ====================================================================

# (TD) l'hissing e il thundering come attacco possono essere effettuate solo ad inizio combattimento
def skill_thundering(entity, argument="", silent=False):
    """
    Skill voce tonante, prende di sorpresa il nemico urlandogli contro
    qualcosa in maniera 'tonante'.
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    execution_success = rpg_channel(entity, argument, CHANNEL.THUNDERING)
    if not execution_success:
        return False

    # (TD) rimane così fino al rifacimento delle skill
    return True

    # La gestione dell'argomento vuoto viene effettuata dalla rpg_channel.
    # Anche se la parte skillosa del comando non viene effettuata il comando
    # è considerato eseguito
    if not argument:
        return True

    arg, argument = one_argument(argument)
    # Qui effettua una ricerca della particella in minuscolo, ci sono più
    # probabilità che non conflitti con la ricerca del nome di un'entità
    if argument and arg[0 : 2] == "a ":
        arg, argument = one_argument(argument)

    # Se il target non si trova allora esce, non eseguendo la parte della skill
    # e considerando il thundering come un comando di canale rpg
    target = entity.find_entity_extensively(arg)
    if not target:
        return True

    percent = check_skill(entity, target, "thundering")
    # (TD) farla utilizzare anche in combattimento, ma ad inizio combattimento
    # ci sono più chance di sorpresa
    if percent < config.clumsy_value:
        if not silent:
            entity.act("\nCerchi di prendere di [yellow]sorpresa[close] $N con la tua [red]voce tonante[close] ma tutto quello che ti esce è una [pink]vocina stridula[close]...", TO.ENTITY, target)
            entity.act("$lui cerca di prendere di [yellow]sorpresa[close] $N con la sua [red]voce tonante[close] ma tutto quello che gli esce è una [pink]vocina stridula[close]...", TO.OTHERS, target)
            entity.act("$lui cerca ti prenderti di [yellow]sorpresa[close] con la sua [red]voce tonante[close] ma tutto quello che gli esce è una [pink]vocina stridula[close]...", TO.TARGET, target)
        return "clumsy"
    elif percent < config.failure_value:
        if not silent:
            entity.act("\nCerchi di prendere di [yellow]sorpresa[close] $N con la tua [red]voce tonante[close] ma [dimgray]fallisci[close]...", TO.ENTITY, target)
            entity.act("$lui cerca ti prenderti di [yellow]sorpresa[close] con la sua [red]voce tonante[close] ma [dimgray]fallisce[close]...", TO.OTHERS, target)
            entity.act("$lui cerca di prendere di [yellow]sorpresa[close] $N con la sua [red]voce tonante[close] ma [dimgray]fallisce[close]..", TO.TARGET, target)
        return "failure"
    elif percent < config.success_value:
        if not silent:
            entity.act("\n[white]Riesci[close] a prendere di [yellow]sorpresa[close] $N con la tua [red]voce tonante[close]!", TO.ENTITY, target)
            entity.act("$lui [white]riesce[close] a prendere di [yellow]sorpresa[close] $N con la sua [red]voce tonante[close]!", TO.OTHERS, target)
            entity.act("$lui ti [white]riesce[close] a prendere di [yellow]sorpresa[close] con la sua [red]voce tonante[close]!", TO.TARGET, target)
        return "success"
    else:
        if not silent:
            entity.act("\n$N [cyan]salta per aria[close] dalla [yellow]sorpresa[close] e rimane [yellow]spaesato[close] dalla tua [red]voce tonante[close]!", TO.ENTITY, target)
            entity.act("$N [cyan]salta per aria[close] dalla [yellow]sorpresa[close] e rimane [yellow]spaesato[close] dalla [red]voce tonante[close] di $lui!", TO.OTHERS, target)
            entity.act("[cyan]Salti per aria[close] dalla [yellow]sorpresa[close] e rimani [yellow]spaesato[close] dalla [red]voce tonante[close] di $lui!", TO.TARGET, target)
        # (TD) Penalità in attesa nell'iniziare il combattimento o del turno
        return "masterly"

    # (TD) se però non è già iniziato non ne ha bisogno (??) cusa l'è che intendevo?
    #start_fight(entity, target)
    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    return "thunder <nome bersaglio> <messaggio da tuonare al bersaglio>\n"
#- Fine Funzione -
