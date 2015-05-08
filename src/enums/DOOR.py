# -*- coding: utf-8 -*-

"""
Enumerazione delle flag relative alle porte.
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = False


#-------------------------------------------------------------------------------

class DoorElement(EnumElement):
    def __init__(self, name, description=""):
        super(DoorElement, self).__init__(name, description)
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE          = DoorElement("None",        "Nessuna")
CLOSABLE      = DoorElement("Closable",    "La porta si può chiudere")
CLOSED        = DoorElement("Closed",      "La porta è chiusa")
LOCKED        = DoorElement("Locked",      "La porta è chiusa a chiave")
EATKEY        = DoorElement("EatKey",      "Una volta che si apre la porta con la chiave quest'ultima viene distrutta")
FORCE_USE_KEY = DoorElement("ForceUseKey", "Forza l'utilizzo dell'argomento &lt;chiave da usare&gt; nel comando unlock e lock per poter aprire e chiudere la porta")
NO_USE_DIR    = DoorElement("NoUseDir",     "Indica che per questa porta non si possono utilizzare, ad esempio, il comando open nord")
SECRET        = DoorElement("Secret",       "La porta è nascosta")  # (TD) spostare la flag tra quelle delle uscite?
BOLTED        = DoorElement("Bolted",       "La porta ha un catenaccio chiuso")
BOLTABLE      = DoorElement("Boltable",     "La porta ha un catenaccio chiudibile e apribile")
NO_PASSDOOR   = DoorElement("NoPassDoor",   "La porta non è passabile tramite incantesimo")
ASYNCHRONOUS  = DoorElement("Asynchronous", "La porta installata su di un uscita di un lato è resa indipendente rispetto a quella installata nel lato apposto, sostanzialmente ciò permette di inserire due porte in una stesso collegamento tra due stanze.")
BASHED        = DoorElement("Bashed",       "La porta è sfondata")
WINDOW        = DoorElement("Transparent",  "Dalla porta vi si può vedere attraverso, come se fosse una finestra")
OPEN_ONE_TIME = DoorElement("OpenOneTime",  "La porta si può aprire solo una volta, dopodiché perderà la sua flag closable")


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
