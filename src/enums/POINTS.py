# -*- coding: utf-8 -*-

"""
Enumerazione relativa ai punteggi principali.
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = True


#-------------------------------------------------------------------------------

class PointsElement(EnumElement):
    def __init__(self, name, description=""):
        super(PointsElement, self).__init__(name, description)
        self.attr_name = ""  # Nome dell'attributo relativo al punteggio
        self.color_50  = ""  # Nome del colore utilizzato nel prompt quando il punteggio è minore rispetto alla sua metà
        self.color_25  = ""  
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE   = PointsElement("Nessuno")
LIFE   = PointsElement("[red]Vita[close]",         "La vita rappresenta quanto sei 'vivo', se raggiungi lo zero allora muori, ma non permanentemente.")
MANA   = PointsElement("[royalblue]Mana[close]",   "Il mana rappresenta il deposito di magia in te da cui attingere per pronunciare incantesimi.")
VIGOUR = PointsElement("[limegreen]Vigore[close]", "Il vigore man a mano si abbassa se intraprendi azioni stancanti, quando raggiungono lo zero dovrai riposarti, per esempio sedendoti un certo tot di tempo.")

LIFE.attr_name   = "life"
MANA.attr_name   = "mana"
VIGOUR.attr_name = "vigour"

LIFE.color_50   = "[crimson]"
MANA.color_50   = "[darkturquoise]"
VIGOUR.color_50 = "[greenyellow]"

LIFE.color_25   = "[indianred]"
MANA.color_25   = "[deepskyblue]"
VIGOUR.color_25 = "[yellowgreen]"


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
