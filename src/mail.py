# -*- coding: utf-8 -*-

"""
Modulo generico per la gestione dell'invio delle mail.
"""


#= IMPORT ======================================================================

from email import Charset
#from email.mime.text      import MIMEText
#from email.mime.multipart import MIMEMultipart

from twisted.mail.smtp import sendmail

from src.config   import config
from src.database import database
from src.engine   import engine
from src.enums    import TRUST


#= CLASSES =====================================================================

class Mail(object):
    def send(self, to_address, subject, message):
        if not to_address:
            log.bug("to_address non è un parametro valido: %s" % to_address)
            return

        if not subject:
            log.bug("subject non è un parametro valido: %s" % subject)
            return

        if not message:
            log.bug("message non è un parametro valido: %s" % message)
            return

        # -------------------------------------------------------------------------

        # Evita di inviare mail quando si stanno testando gli input
        if engine.test_inputs_mode:
            return

        # (TD) sarà color.remove_all e un import esterno
        from src.color import remove_colors

        message += "\n\n----------------------------------------------------------------------\n"
        message += "Questa mail e' stata generata automaticamente da %s.\n" % remove_colors(config.game_name)
        message += "Per favore non inviare una risposta a questa mail, non la riceveremmo.\n"
        message += "Se hai bisogno di contattarci puoi inviarci una mail al seguente indirizzo: %s\n" % config.email
        message += "\n%s" % remove_colors(config.staff_name)

        deferred = sendmail(config.smtp_host, config.smtp_email, to_address, "Subject: %s\n\n%s" % (
            subject, message))
        deferred.addCallback(_send_complete)
        deferred.addErrback(_handle_error)
    #- Fine Metodo -

    def send_to_admins(self, subject, message, trust=TRUST.MASTER, show_players=True, avoid_account=None):
        if not subject:
            log.bug("subject non è un parametro valido: %s" % subject)
            return

        if not message:
            log.bug("message non è un parametro valido: %s" % message)
            return

        if not trust or trust == TRUST.NONE:
            log.bug("trust non è un parametro valido: %s" % trust)
            return

        # ---------------------------------------------------------------------

        if show_players:
            footer = ["\n\nGiocatori in gioco:\n"]
            for player in database["players"].itervalues():
                if player.game_request:
                    footer.append(player.code + "\n")
            message += "".join(footer)

        for account in database["accounts"].itervalues():
            if avoid_account and account == avoid_account:
                continue
            if account.email and account.trust >= trust:
                self.send(account.email, subject, message)
    #- Fine Metodo -


#= FUNZIONI ====================================================================

def _send_complete(result):
    return True
#- Fine Funzione -


def _handle_error(error):
    if not error:
        log.bug("error non è un parametro valido: %s" % error)
        return False

    error.printTraceback()
    return False
#- Fine Funzione -


#= SINGLETON ===================================================================

mail = Mail()
