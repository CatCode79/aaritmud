# -*- coding: utf-8 -*-

"""
Comando che serve a ripristinare completamente i vari punteggi.
"""


#= IMPORT ======================================================================

from src.command import get_command_syntax
from src.enums   import TO, TRUST
from src.log     import log


#= FUNZIONI ====================================================================

def command_restore(entity, argument=""):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    if not argument:
        if entity.life >= entity.max_life:
            syntax = get_command_syntax(entity, "command_restore")
            entity.send_output(syntax, break_line=False)
            return False
        else:
            argument = entity.code

    target = entity.find_entity_extensively(argument)
    if not target:
        entity.send_output("Nessuna entità trovata con argomento [white]%s[close]." % argument)
        return False

    if target.IS_PLAYER and entity.trust < TRUST.IMPLEMENTOR:
        entity.send_output("Non ti è possibile ripristinare i punti dei personaggi.")
        return False

    # Ripristino prima di inviare il messaggio cosicché il prompt visualizza
    # correttamente il tutto
    target.life = target.max_life
    target.mana = target.max_mana
    target.vigour = target.max_vigour
    if target.IS_ACTOR:
        target.thirst      = 0
        target.hunger      = 0
        target.sleep       = 0
        target.drunkness   = 0
        target.adrenaline  = 0
        target.mind        = 0
        target.emotion     = 0
        target.bloodthirst = 0

    if entity == target:
        entity.act("Ti invii un flusso d'energia per ripristinarti!", TO.ENTITY, target)
        entity.act("$n si invia un flusso d'energia per ripristinarsi!", TO.OTHERS, target)
    else:
        entity.act("Invii un flusso d'energia su di $N che lo ripristina!", TO.ENTITY, target)
        entity.act("$n invia un flusso d'energia su di $N che lo ripristina!", TO.OTHERS, target)
        target.act("$n ti invia un flusso d'energia su di te che ti ripristina!", TO.TARGET, target)

    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""

    syntax += "restore\n"
    syntax += "restore <vittima>\n"

    return syntax
#- Fine Funzione -
