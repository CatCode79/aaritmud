# -*- coding: utf-8 -*-

"""
Modulo per la gestione delle novità da visualizza sulla homepage del sito.
"""


#= IMPORT ======================================================================

from src.data     import Data
from src.database import database
from src.enums    import NEW
from src.log      import log


#= CLASSI ======================================================================

class Comment(object):
    PRIMARY_KEY = "code"
    VOLATILES   = []
    MULTILINES  = ["text"]
    SCHEMA      = {}
    REFERENCES  = {}
    WEAKREFS    = {}

    def __init__(self):
        self.author      = ""       # Autore/i
        self.date        = ""       # Quando è stata scritta
        self.text        = ""       # Testo
    #- Fine Inizializzazione -

    def get_error_message(self):
        if not self.author:
            return "author non è valido: %r" % self.author
        elif not self.date:
            return "date non è valido: %r" % self.date
        elif not self.text:
            return "text non è valido: %r" % self.text
        else:
            return ""

        return msg
    #- Fine Metodo -


class New(Comment, Data):
    PRIMARY_KEY = "code"
    VOLATILES   = Comment.VOLATILES + []
    MULTILINES  = Comment.MULTILINES + []
    SCHEMA      = {"comments" : ("src.new", "Comment")}
    SCHEMA.update(Comment.SCHEMA)
    REFERENCES  = {}
    REFERENCES.update(Comment.REFERENCES)
    WEAKREFS    = {}
    WEAKREFS.update(Comment.WEAKREFS)

    def __init__(self, code=""):
        super(New, self).__init__()
        
        self.code        = code     # Codice identificativo
        self.title       = ""       # Titolo
        self.type        = NEW.NONE # Tipologia di novità
        self.thumbs_up   = ""       # Nomi degli account che hanno espresso parere positivo
        self.thumbs_down = ""       # Nomi degli account che hanno espresso parere negativo
        self.comments    = []       # Commenti al commento
    #- Fine Inizializzazione -

    def get_error_message(self):
        msg = super(New, self).get_error_message()

        if msg:
            pass
        elif not self.code:
            msg = "code non è valido: %r" % self.code
        elif not self.title:
            msg = "title non è valido: %r" % self.title
        elif self.type.get_error_message(NEW, "type") != "":
            msg = self.type.get_error_message(NEW, "type")
        elif self.get_error_message_thumbs() != "":
            return self.get_error_message_thumbs()
        elif self.get_error_message_comments() != "":
            return self.get_error_message_comments()
        else:
            msg = ""

        if msg:
            return "[%s] %s" % (self.code, msg)
        else:
            return ""
    #- Fine Metodo -

    def get_error_message_thumbs(self):
        accounts_up   = self.thumbs_up.split()
        accounts_down = self.thumbs_down.split()

        for name in accounts_up:
            if name in accounts_down:
                return "Nome di account %s trovato sia tra i voti positivi che quelli negativi" % name
            if name not in database["accounts"]:
                return "Nome di account %s inesistente tra gli account" % name

        for name in accounts_down:
            if name not in database["accounts"]:
                return "Nome di account %s inesistente tra gli account" % name

        return ""
    #- Fine Metodo -

    def get_error_message_comments(self):
        for comment in self.comments:
            if comment.get_error_message() != "":
                return comment.get_error_message()

        return ""
    #- Fine Metodo -
