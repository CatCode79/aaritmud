# -*- coding: utf-8 -*-

"""
Modulo per la gestione della pagina che serve ad inviare delle note agli admin.
"""


#= IMPORT ======================================================================

import pprint
import string
import urllib

from src.config       import config
from src.log          import log
from src.mail         import mail
from src.utility      import email_encoder
from src.web_resource import WebResource, create_tooltip


#= CLASSI ======================================================================

class ContactUsPage(WebResource):
    """
    Pagina utilizzata per inviare note allo staff del Mud.
    """
    TITLE = "Contattaci"

    PAGE_TEMPLATE = string.Template(open("src/views/contact_us.view").read())

    NEW_PAGE = True

    MAX_SUBJECT_LENGTH = 100
    MAX_MESSAGE_LENGTH = 1000
    MAX_EMAIL_LENGTH   = 50

    EMPTY_SUBJECT_ERROR = "Il soggetto è vuoto"
    EMPTY_MESSAGE_ERROR = "Il messaggio è vuoto"

    TOO_LONG_SUBJECT_ERROR = "Il soggetto è troppo lungo"
    TOO_LONG_MESSAGE_ERROR = "Il messaggio è troppo lungo"
    TOO_LONG_EMAIL_ERROR   = "La tua email è troppo lunga"

    EMAIL_TOOLTIP_TEXT = "L'email è facoltativa, permetterà un'eventuale risposta al messaggio."

    def render_GET(self, request, conn):
        mapping = {"MAX_SUBJECT_LENGTH"     : self.MAX_SUBJECT_LENGTH,
                   "MAX_MESSAGE_LENGTH"     : self.MAX_MESSAGE_LENGTH,
                   "MAX_EMAIL_LENGTH"       : self.MAX_EMAIL_LENGTH,
                   "EMPTY_SUBJECT_ERROR"    : self.EMPTY_SUBJECT_ERROR,
                   "EMPTY_MESSAGE_ERROR"    : self.EMPTY_MESSAGE_ERROR,
                   "TOO_LONG_SUBJECT_ERROR" : self.TOO_LONG_SUBJECT_ERROR,
                   "TOO_LONG_MESSAGE_ERROR" : self.TOO_LONG_MESSAGE_ERROR,
                   "TOO_LONG_EMAIL_ERROR"   : self.TOO_LONG_EMAIL_ERROR,
                   "email"                  : email_encoder(config.email),
                   "email_tooltip"          : create_tooltip(conn, self.EMAIL_TOOLTIP_TEXT)}
        return self.PAGE_TEMPLATE.safe_substitute(mapping)
    #- Fine Metodo -

    def render_POST(self, request, conn):
        subject = ""
        if "subject" in request.args:
            subject = urllib.unquote(request.args["subject"][0])
        message = ""
        if "message" in request.args:
            message = urllib.unquote(request.args["message"][0])
        email = ""
        if "email" in request.args:
            email = urllib.unquote(request.args["email"][0])

        errors = {}
        if not subject:
            errors["subject_error"] = self.EMPTY_SUBJECT_ERROR
        elif len(subject) > self.MAX_SUBJECT_LENGTH:
            errors["subject_error"] = self.TOO_LONG_SUBJECT_ERROR
        if not message:
            errors["message_error"] = self.EMPTY_MESSAGE_ERROR
        elif len(message) > self.MAX_MESSAGE_LENGTH:
            errors["message_error"] = self.TOO_LONG_MESSAGE_ERROR
        # L'email è facoltativa
        if len(email) > self.MAX_EMAIL_LENGTH:
            errors["email_error"] = self.TOO_LONG_EMAIL_ERROR

        if errors:
            return pprint.pformat(errors, indent=0)

        # Altrimenti invia il messaggio all'email ufficiale del Mud
        message += "\n\nID di chi ha postato: %s\n" % conn.get_id()
        if email:
            message += "La sua mail per un'eventuale risposta: %s" % email
        else:
            message += "Non e' stata inserita nessuna mail per un'eventuale risposta."
        mail.send(config.email, subject, message)
        return "OK"
    #- Fine Metodo -
