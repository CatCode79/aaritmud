# -*- coding: utf-8 -*-

"""
Modulo per la gestione dei libri, racconti e altri scritti inseribili anche
durante il gioco dai personaggi giocanti.
"""

# (TD) supportare i bordi css3 con le immagini

#= IMPORT ======================================================================

import math

from src.element   import Element, Flags
from src.enums     import LANGUAGE, READABLE
from src.interpret import translate_input
from src.log       import log
from src.miml      import MIML_SEPARATOR
from src.utility   import copy_existing_attributes, multiple_arguments


#= CLASSI ======================================================================

class Readable(object):
    PRIMARY_KEY = ""
    VOLATILES   = []
    MULTILINES  = ["comment", "pages", "summary"]
    SCHEMA      = {"visual_width"  : ("", "css_measure"),
                   "visual_height" : ("", "css_measure"),
                   "padding"       : ("", "css_measure"),
                   "border_top"    : ("", "css_border"),
                   "border_right"  : ("", "css_border"),
                   "border_bottom" : ("", "css_border"),
                   "border_left"   : ("", "css_border"),
                   "border_inside" : ("", "css_border"),
                   "pages"         : ("", "str")}
    REFERENCES  = {}
    WEAKREFS    = {}

    def __init__(self):
        self.comment       = ""  # Commento per gli area builder relativo all'entità leggibile
        self.title         = ""  # Titolo del libro
        self.author        = ""  # Autore o gli autori di questo libro
        self.summary       = ""  # Riassunto del libro che il giocatore carpisce esaminandolo
        self.language      = Element(LANGUAGE.COMMON) # (TD) Lingua di questo libro
        self.flags         = Flags(READABLE.NONE)  # Flag relative alle entità leggibili
        self.visual_width  = ""  # Larghezza in pixel del libro sullo schermo
        self.visual_height = ""  # Larghezza in pixel del libro sullo schermo
        self.padding       = ""  # Larghezza in pixel del padding della cornice del libro
        self.border_top    = ""  # Bordo css decorante il libro in alto
        self.border_right  = ""  # Bordo css decorante il libro a destra
        self.border_bottom = ""  # Bordo css decorante il libro in basso
        self.border_left   = ""  # Bordo css decorante il libro a sinistra
        self.border_inside = ""  # Bordo css decorante il libro tra le due pagine
        self.number_decoration_left  = ""  # Decorazione della pagina sinistra per i numeri di pagina
        self.number_decoration_right = ""  # Decorazione della pagina sinistra per i numeri di pagina
        self.pages         = []  # Lista delle pagine e relativo contenuto
    #- Fine Inizializzazione -

    def get_error_message(self, entity):
        if not self.title:
            return "title è una stringa non valida: %r" % self.title
        elif not self.author:
            return "author è una stringa non valida: %r" % self.author
        elif not self.summary:
            return "summary è una stringa non valida: %r" % self.summary
        elif self.language.get_error_message(LANGUAGE, "language") != "":
            return self.language.get_error_message(LANGUAGE, "language")
        elif self.flags.get_error_message(READABLE, "flags") != "":
            return self.flags.get_error_message(READABLE, "flags")
        elif READABLE.CENTER in self.flags and READABLE.RIGHT in self.flags:
            return "Non possono convivere le flag READABLE.CENTER e READABLE.RIGHT assieme."
        elif (self.number_decoration_left or self.number_decoration_right) and READABLE.NUMBERS not  in self.flags:
            return "Nonostante sia stata definita una decorazione per i numeri non esiste la flag READABLE.NUMBERS che la mostrerebbe."
        elif not self.visual_width:
            return "visual_width è una stringa non valida: %r" % self.visual_width
        elif not self.visual_height:
            return "visual_height è una stringa non valida: %r" % self.visual_height
        elif not self.pages:
            return "dev'esservi almeno una pagina: %r" % self.pages

        return ""
    #- Fine Metodo -

    def copy(self, to_obj=None, avoid_volatiles=False):
        if not to_obj:
            to_obj = Readable()
        copy_existing_attributes(self, to_obj, avoid_volatiles=avoid_volatiles)
        return to_obj
    #- Fine Metodo -

    def equals(self, readable2):
        if not readable2:
            return False

        if self.comment != readable2.comment:
            return False
        if self.title != readable2.title:
            return False
        if self.author != readable2.author:
            return False
        if self.summary != readable2.summary:
            return False
        if self.language != readable2.language:
            return False
        if self.flags != readable2.flags:
            return False
        if self.visual_width != readable2.visual_width:
            return False
        if self.visual_height != readable2.visual_height:
            return False
        if self.padding != readable2.padding:
            return False
        if self.border_top != readable2.border_top:
            return False
        if self.border_right != readable2.border_right:
            return False
        if self.border_bottom != readable2.border_bottom:
            return False
        if self.border_left != readable2.border_left:
            return False
        if self.border_inside != readable2.border_inside:
            return False
        if self.number_decoration_left != readable2.number_decoration_left:
            return False
        if self.number_decoration_right != readable2.number_decoration_right:
            return False

        if len(self.pages) != len(readable2.pages):
            return False
        for page in self.pages:
            for page2 in readable2.pages:
                if page == page2:
                    break
            else:
                return False

        return True
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    # (TD) entity e target serviranno in futuro per scramblerare la lingua del
    # libro se sconosciuta
    def get_pages(self, entity, target, page_number, from_location=None):
        if not entity:
            log.bug("entity non è un parametro valido: %r" % entity)
            return ""

        if not target:
            log.bug("target non è un parametro valido: %r" % target)
            return ""

        if page_number < 0 or page_number >= len(self.pages):
            log.bug("page_number non è un parametro valido: %r" % page_number)
            return ""

        # ---------------------------------------------------------------------

        # Prepara i bordi
        border_top    = ""
        border_right  = ""
        border_bottom = ""
        border_left   = ""
        border_inside = ""
        if self.border_top:
            border_top    = "border-top:%s;"    % self.border_top
        if self.border_right:
            border_right  = "border-right:%s;"  % self.border_right
        if self.border_bottom:
            border_bottom = "border-bottom:%s;" % self.border_bottom
        if self.border_left:
            border_left   = "border-left:%s;"   % self.border_left
        if self.border_inside:
            border_inside  = "border-right:%s;" % self.border_inside

        # Prepara il padding se esistente
        padding_style = ""
        if self.padding:
            padding_style = "padding:%s;" % self.padding

        # Prepara lo style css per l'output scritto della pagina
        alignment = ""
        if READABLE.CENTER in self.flags:
            alignment = '''text-align:center;'''
        if READABLE.RIGHT in self.flags:
            alignment = '''text-align:right;'''
        visual_style = ''' style="min-width:%s; max-width:%s; min-height:%s; max-height:%s; %s %s"''' % (
            self.visual_width, self.visual_width, self.visual_height, self.visual_height, padding_style, alignment)

        # Ricava informazioni che servono a sfogliare il libro tramite click
        translated_input = translate_input(entity, "read", "en")
        if not translated_input:
            log.bug("Non è stato possibile tradurre l'input read per %s: %r" % (target.code, translated_input))
            return False
        numbered_keyword = target.get_numbered_keyword(looker=entity)
        if page_number % 2 == 0 and page_number != len(self.pages)-1:
            minimum_page = max([0, page_number-2])
            maximum_page = min([len(self.pages)-1, page_number+1])
        else:
            minimum_page = max([0, page_number-1])
            maximum_page = min([len(self.pages)-1, page_number+2])
        if from_location:
            js_minimum_arguments = "%s %s %s %d" % (translated_input, numbered_keyword, from_location.get_numbered_keyword(looker=entity), minimum_page)
            js_maximum_arguments = "%s %s %s %d" % (translated_input, numbered_keyword, from_location.get_numbered_keyword(looker=entity), maximum_page)
        else:
            js_minimum_arguments = "%s %s %d" % (translated_input, numbered_keyword, minimum_page)
            js_maximum_arguments = "%s %s %d" % (translated_input, numbered_keyword, maximum_page)
        browse_to_left  = '''<div style="float:left"><a href="javascript:sendInput('%s')" style="font-size:larger">&lt;</a> </div>''' % js_minimum_arguments
        browse_to_right = '''<div style="float:left"> <a href="javascript:sendInput('%s')" style="font-size:larger">&gt;</a></div>''' % js_maximum_arguments

        # Gestisce la copertina e la retrocopertina o altre tipologie di entità
        # leggibili differenti da dei libri, ovvero con al massimo il fronte
        # e il retro
        if page_number == 0 or page_number == len(self.pages) - 1:
            style = ""
            if border_top or border_right or border_bottom or border_left:
                style = ''' style="float:left; %s%s%s%s"''' % (border_top, border_right, border_bottom, border_left)
            output = ""
            if page_number == len(self.pages) - 1:
                output += browse_to_left
            output += '''<div%s><div%s>%s</div></div>''' % (style, visual_style, self.pages[page_number])
            if page_number == 0:
                output += browse_to_right
            output += '''<div style="clear:both;" />'''
            return output

        # A seconda che si voglia visualizzare una pagina a destra o a sinistra
        # sceglie il numero corretto di pagina da far visualizzare nell'altra
        if page_number % 2 == 0:
            left_page_number  = page_number - 1
            right_page_number = page_number
        else:
            left_page_number  = page_number
            right_page_number = page_number + 1

        # Prepara lo stile dei bordi preparati in precedenza, se ve n'erano
        left_style  = '''style="float:left;%s%s%s%s"''' % (border_top, border_inside, border_bottom, border_left)
        right_style = '''style="float:left;%s%s%s"'''   % (border_top, border_right,  border_bottom)

        # Prepara il contenuto scritto delle pagine aggiungendo una pagina
        # vuota prima della retrocopertina se necessario
        left_output  = self.pages[left_page_number]
        if len(self.pages) % 2 == 0 and page_number == len(self.pages) - 1:
            right_output = ""
        elif len(self.pages) % 2 == 1 and page_number == len(self.pages) - 2:
            right_output = ""
        else:
            right_output = self.pages[right_page_number]
        if MIML_SEPARATOR in left_output:
            left_output = target.parse_miml(left_output, looker=entity)
        if MIML_SEPARATOR in right_output:
            right_output = target.parse_miml(right_output, looker=entity)

        # Prepara l'output per i numeri di pagina
        left_page_number_output  = ""
        right_page_number_output = ""
        if READABLE.NUMBERS in self.flags:
            if len(self.number_decoration_left) == 0:
                left_page_number_output  = '''<center>%d</center>''' % left_page_number
            elif len(self.number_decoration_left) == 1:
                left_page_number_output  = '''<center>%s%d</center>''' % (self.number_decoration_left, left_page_number)
            else:
                middle = int(math.ceil(len(self.number_decoration_left) / 2.0))
                left_page_number_output  = '''<center>%s%d%s</center>''' % (self.number_decoration_left[ : middle],  left_page_number,  self.number_decoration_left[middle : ])
            if len(self.number_decoration_right) == 0:
                right_page_number_output  = '''<center>%d</center>''' % right_page_number
            elif len(self.number_decoration_right) == 1:
                right_page_number_output = '''<center>%d%s</center>''' % (right_page_number, self.number_decoration_right)
            else:
                middle = int(math.floor(len(self.number_decoration_left) / 2.0))
                right_page_number_output = '''<center>%s%d%s</center>''' % (self.number_decoration_right[ : middle], right_page_number, self.number_decoration_right[middle : ])

        # Ecco l'output del libro in tutto il suo splendore
        output  = browse_to_left
        output += '''<div %s><div%s>%s</div>%s</div>''' % (left_style,  visual_style, left_output,  left_page_number_output)
        output += '''<div %s><div%s>%s</div>%s</div>''' % (right_style, visual_style, right_output, right_page_number_output)
        output += browse_to_right
        output += '''<div style="clear:both;" />'''

        return output
    #- Fine Metodo -
