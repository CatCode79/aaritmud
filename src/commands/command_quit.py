# -*- coding: utf-8 -*-

#= IMPORT ======================================================================

from src.config       import config
from src.enums        import FLAG, OPTION, TO
from src.grammar      import grammar_gender
from src.log          import log
from src.room         import Destination
from src.web_resource import send_audio


#= FUNZIONI ====================================================================

def command_quit(entity, argument=""):
    """
    Permette di uscire dal gioco.
    """
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    # (TD) eventuale utilizzo di argument, come emote del messaggio di uscita

    if not entity.game_request:
        entity.send_output("Non ti è possibile fuggire dalla realtà...")
        return False

    send_audio(entity.get_conn(), "quit.mid")
    entity.send_output("Chiudi gli %s come per addormentarti e ti senti portat%s via poco a poco..." % (
        entity.eye_colorize("occhi"), grammar_gender(entity)))
    entity.send_output("=============================================================================")
    entity.send_output("</body>", break_line=False)
    entity.send_output("</html>", break_line=False)

    if entity.account and OPTION.COMET in entity.account.options:
        entity.game_request.finish()
    else:
        # Utilizza questo attributo come indicatore che al prossimo invio del
        # buffer al giocatore viene chiusa la connessione, inoltre gli evita
        # di ricevere altro buffer
        entity.get_conn().stop_buffering = True

    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    return "quit\n"
#- Fine Funzione -
