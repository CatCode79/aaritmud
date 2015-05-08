# -*- coding: utf-8 -*-

"""
Enumerazione dele vie (praticamente le solite classi, non ho potuto chiamarle
class perché il termine fa conflitto con la keyword del linguaggio python).
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = True


#-------------------------------------------------------------------------------

class WayElement(EnumElement):
    def __init__(self, name, description=""):
        super(WayElement, self).__init__(name, description)
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE      = WayElement("Nessuno")
GLADIATOR = WayElement("[red]Gladiatore[close]",      "È la via della guerra: perfezionare ed imparare sempre più nuove tecniche di combattimento e migliorare quelle antiche.")
RUNIC     = WayElement("[royalblue]Runico[close]",    "È la via della magia: grazie al segreto delle rune e al Mana si possono rendere concrete cose altrimenti difficilmente realizzabili.")
WANDERING = WayElement("[green]Ramingo[close]",       "È la via della sopravvivenza: eplorazione, caccia, conoscenza dei luoghi selvaggi e rispetto per gli animali sono i tratti più conosciuti di questa vita.")
SHADOW    = WayElement("[darkslategray]Ombra[close]", "È la via del sotterfugio: nascondersi nell'ombra, rubare senza essere visti, fuggire dalle guardie, tendere un'agguato alla propria vittima... C'è chi lo fa per denaro, chi per divertimento.")
#DRUID     = WayElement("Druido", )
#MUTAFORMA = WayElement("Mutaforma", )
#PSICOITEM = WayElement("PsicoItem", )


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
