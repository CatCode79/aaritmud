# -*- coding: utf-8 -*-

"""
Enumerazione delle flag delle stanze.
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = False


#-------------------------------------------------------------------------------

class RoomElement(EnumElement):
    def __init__(self, name, description=""):
        super(RoomElement, self).__init__(name, description)
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE           = RoomElement("Nessuna")
INSIDE         = RoomElement("Inside",         "Flag utile per le case, caverne o altri luoghi interni, chiusi o abitati")
UNDERWATER     = RoomElement("Underwater",     "Tutte le stanze virtuali sotto al livello dell'acqua hanno questa flag")
NO_MOB         = RoomElement("NoMob",          "La stanza non è praticabile dai mob")
NO_ITEM        = RoomElement("NoItem",         "La stanza non è praticabile dagli oggetti")
NO_ROOM        = RoomElement("NoRoom",         "La stanza non è praticabile dalle stanze")
NO_PLAYER      = RoomElement("NoPlayer",       "La stanza non è praticabile dai giocatori, neppure da quelli che seguono un'altro tipo di entità.")  # (TD) ora come ora se un giocatore segue un altro giocatore questo entra comunque nella stanza
SAFE           = RoomElement("Safe",           "Nella stanza non si può attaccare ed essere attaccati")
NO_MAGIC       = RoomElement("NoMagic",        "Nella stanza non si può castare")
NO_RECALL      = RoomElement("NoRecall",       "Dalla stanza non si può eseguire un recall")
NO_SUMMON      = RoomElement("NoSummon",       "Non si può utilizzare l'incantesimo di summon")
NO_TELEPORT    = RoomElement("NoTeleport",     "Non ci si può teletrasportare")
STOREROOM      = RoomElement("Storeroom",      "La stanza è adebita ad immagazzinare oggetti (vengono salvati anche quelli meno importanti)")
NO_GET         = RoomElement("NoGet",          "Nella stanza non è possibile utilizzare il comando get e neppure il get all")
NO_GETALL      = RoomElement("NoGetAll",       "Nella stanza non è possibile utilizzare il comando get all, mentre il get semplice sì")
NO_DROP        = RoomElement("NoDrop",         "Nella stanza non si possono lasciare entità")
NO_DROPALL     = RoomElement("NoDropAll",      "Nella stanza non si possono lasciare entità tutti in un volta")
NO_PUT         = RoomElement("NoPut",          "Nella stanza non si possono mettere entità ad altre entità")
NO_GIVE        = RoomElement("NoGive",         "Nella stanza non si possono dare entità ad altre entità")
NO_HOLD        = RoomElement("NoHold",         "Nella stanza non si possono afferrare oggetti in mano")
SILENCE        = RoomElement("Silence",        "Nella stanza non si può parlare")
AMPLIFY        = RoomElement("Amplify",        "La stanza amplifica i suoni e il parlato")
ARENA          = RoomElement("Arena",          "La stanza è una arena")
TERRACE        = RoomElement("Terrace",        "La stanza è una gradinata di un'arena")
NO_MISSILE     = RoomElement("NoMissile",      "Dalla (o nella) stanza non si possono utilizzare armi a distanza")
NO_FLYING      = RoomElement("NoFlying",       "Nella stanza non di può volare")
NO_MOUNTFLYING = RoomElement("NoMountFlying",  "Nella stanza non di può volare su di un mezzo o su di una cavalcatura")
NO_LANDING     = RoomElement("NoLanding",      "Nella stanza non si può atterrare con un mezzo o con una cavalcatura")
STICKY         = RoomElement("Sticky",         "C'è una probabilità che i piedi si incollano al pavimento della stanza")
CREAKY         = RoomElement("Creacky",        "C'è una probabilità che camminando il pavimendo scricchioli, avvertendo i nemici della tua presenza")
SPLIPPERY      = RoomElement("Scivolosa",      "C'è una probabilità di scivolare su pavimento andando a sbattere da qualche parte (oltre che col sedere) oppure finire in un'altra stanza")
#MISTY         = RoomElement("Misty")  # (TD) potrebbe non servire se potenzio al meglio il meteo
EXTRACTED      = RoomElement("Extracted",      "La stanza è stata rimossa dal gioco tramite il metodo extract, serve per debug sui riferimenti")
DEATH_TRAP     = RoomElement("DeathTrap",      "Se un'entità entra nella stanza questa muore all'istante, se l'entità è un giocatore il suo cadavere viene teletrasportato con lui al Menhir della Vita più vicino")


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
