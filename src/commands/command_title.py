# -*- coding: utf-8 -*-


#= IMPORT ======================================================================

from src.color   import count_colors, close_color
from src.command import get_command_syntax
from src.enums   import TRUST
from src.grammar import grammar_gender
from src.log     import log
from src.utility import is_same


#= FUNZIONI ====================================================================

def command_title(entity, argument=""):
    """
    Permette al giocatore d'inserire un proprio title al personaggio.
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    if not argument:
        syntax = get_command_syntax(entity, "command_title")
        entity.send_output(syntax, break_line=False)
        return False

    if not entity.IS_PLAYER:
        entity.send_output("Non ti è possibile impostare un titolo.")
        return

    if is_same(argument, "cancella") or is_same(argument, "delete"):
        entity.title = ""
        entity.send_output("Il tuo titolo è stato cancellato.")
        return True

    color_qty = count_colors(argument)
    # (TD) In futuro non farlo dipendente dal livello ma da qualche achievement o quest
    if color_qty > entity.level / 2:
        entity.send_output("Devi crescere di livello se vuoi colorare maggiormente il tuo titolo.")
        return False

    entity.title = close_color(argument)
    entity.send_output("Il tuo titolo è stato modificato in: '%s'" % entity.title)
    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""
    syntax += "title <titolo con cui vuoi essere conosciut%s>\n" % grammar_gender(entity)
    syntax += "title cancella"

    return syntax
#- Fine Funzione -
