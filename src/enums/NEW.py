# -*- coding: utf-8 -*-

"""
Enumerazione delle tipologie di help.
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = True


#-------------------------------------------------------------------------------

class NewElement(EnumElement):
    def __init__(self, name, description=""):
        super(NewElement, self).__init__(name, description)
        self.tag_image = ""  # Immagine rappresentante la tipologia di notizia
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE    = NewElement("Nessuna")
CODE    = NewElement("Codice",   "Notizia relativa al codice del motore di Aarit")
OPENING = NewElement("Apertura", "Aperture temporanee ai giocatori")
CLOSING = NewElement("Chiusura", "Chiusure delle aperture temporanee")
RELEASE = NewElement("Release",  "Lista delle note di rilascio delle nuove versioni")

CODE.tag_image    = "tags/code.png"
OPENING.tag_image = "tags/opening.png"
CLOSING.tag_image = "tags/closing.png"
RELEASE.tag_image = "tags/release.png"


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
