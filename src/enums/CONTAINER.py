# -*- coding: utf-8 -*-

"""
Enumerazione delle flag relative ai contenitori.
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = False


#-------------------------------------------------------------------------------

class ContainerElement(EnumElement):
    def __init__(self, name, description=""):
        super(ContainerElement, self).__init__(name, description)
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE          = ContainerElement("None",        "Nessuno")
CLOSED        = ContainerElement("Closed",      "Il contenitore è chiusa")
LOCKED        = ContainerElement("Locked",      "Il contenitore è chiusa a chiave")
EATKEY        = ContainerElement("EatKey",      "Una volta che si apre il contenitore con la chiave quest'ultima viene distrutta")
FORCE_KEY_ARG = ContainerElement("ForceUsearg", "Forza l'utilizzo dell'argomento chiave nel comando unlock e lock per poter aprire e chiudere la porta")
BOLTED        = ContainerElement("Bolted",      "Il contenitore ha un catenaccio chiuso")
BOLTABLE      = ContainerElement("Boltable",    "Il contenitore ha un catenaccio azionabile")
CLOSABLE      = ContainerElement("Closable",    "Il contenitore si può aprire chiudere")
SECRET        = ContainerElement("Secret",      "Non si capisce che è un contenitore fino a che non sia già stato aperto")
OPEN_ONE_TIME = ContainerElement("OpenOneTime", "Il contenitore è apribile solo una volta, dopodiché perderà la sua flag closable")

#(TD) mancano i NO_MOB, NO_ITEM etc una volta che i contenitori saranno enterabili


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
