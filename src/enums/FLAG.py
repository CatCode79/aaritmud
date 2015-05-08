# -*- coding: utf-8 -*-

"""
Enumerazione delle flag di entità.
"""
# (TD) queste convertirle in variabili di descrizione caratteriale -100 / 100
#COURAGEOUS        = FlagElement("Coraggioso", "L'entità non si farà abbattere dalle situazioni che incutono timore")
#COWARD            = FlagElement("Fifone",     "L'entità si farà abbattere da situazioni che incutono timore, e potenzialmente fuggirà da esse")
#TRUSTFUL          = FlagElement("Fiducioso",  "L'entità si fiderà maggiormente delle persone")
#DISTRUSTFUL       = FlagElement("Diffidente", "L'entità è maggiormente diffidente nei confronti delle persone")

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = False


#-------------------------------------------------------------------------------

class FlagElement(EnumElement):
    def __init__(self, name, description=""):
        super(FlagElement, self).__init__(name, description)
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE                      = FlagElement("Nessuna")

NO_GET                    = FlagElement("NoGet",           "L'entità non è raccoglibile (anche se leggera)")
NO_DROP                   = FlagElement("NoDrop",          "L'entità non è posabile")
NO_GIVE                   = FlagElement("NoGive",          "L'entità non può essere data ad altre entità (solitamente se vuoi questa flag vuoi anche inserire NO_PUT)")
NO_PUT                    = FlagElement("NoPut",           "L'entità non può essere messa ad altre entità (solitamente se vuoi questa flag vuoi anche inserire NO_GIVE)")
NO_HOLD                   = FlagElement("NoHold",          "L'entità non può essere essere afferrata in mano")
NO_REMOVE                 = FlagElement("NoRemove",        "L'entità non può essere rimossa una volta indossata")
NO_LOOK_LIST              = FlagElement("NoLookList",      "L'entità non è visualizzabile nelle liste create dal comando look, ma sono comunque interagibili e lookabili con il comando")
SPIRIT                    = FlagElement("Spirit",          "L'entità è appena morta")  # sì, anche gli oggetti quando vengono distrutti hanno una loro anima
AGGRESSIVE                = FlagElement("Aggressive",      "L'entità attaccherà, prima o poi, il personaggio o un altra entità")
SENTINEL                  = FlagElement("Sentinel",        "L'entità rimane nella stanza e non insegue altre entità ostili")
AMBIDEXTROUS              = FlagElement("Ambidextrous",    "L'entità è ambidestra")
CONVERSING                = FlagElement("Conversing",      "L'entità sta dialogando con un'altra entità")
BEATEN                    = FlagElement("Beaten",          "L'entità è stata sconfitta in combattimento e attende il comando kill o spare")
RANDOMIZABLE              = FlagElement("Randomizable",    "L'entità è considerata come utilizzabile in sistema di creazione casuale: per gli oggetti nei tesori casuali, reset per i mob nella wild oppure ancora per oggetti trovati casualmente scavando")
NO_ROOM_BEHAVIOUR         = FlagElement("NoRoomBehaviour", "L'entità non utilizza i behaviour della stanza, sia che ne abbia di propri che non")
UNCLEANABLE               = FlagElement("Uncleanable",     "L'entità non viene rimossa dalla procedura di cleaning delle istanza in eccesso")
VALUE_IS_ONLY_COST        = FlagElement("ValueIsOnlyCost", "L'etichetta Value dell'entità non indica quanta moneta possiede con sé ma solo quanto costa nella lista di un negoziante, diversamente Value viene utilizzata per tutte e due le cose")
NO_REMAINS                = FlagElement("NoCorpse",        "L'entità quando muore non produce cadavere")
STAY_ON_DEATH             = FlagElement("StayOnDeath",     "L'entità rimarrà nell'inventario del personaggio anche se questi è morto e teletrasportato altrove, la flag ha senso solo per le entità trasportate da un giocatore.")
EXTRACT_ON_QUIT           = FlagElement("ExtractOnQuit",   "Le entità con tale flag trasportate dai giocatori verranno estratte quando questi ultimi eseguiranno il quit.")
CAN_DAMAGING              = FlagElement("CanDamaging",     "Le entità con tale flag potranno utilizzare il comando destroy, kill e sinonimi. È pensata per oggetti animati.")

# (TD) ancora da implementare, andrà a "sorpassare" il check sulla hardness del materiale
UNBREAKABLE               = FlagElement("Unbreakable",     "Le entità con tale flag non possono essere distrutte normalmente.")

# (TD) farle come affect-malattia
VAMPIRISM                 = FlagElement("Vampirism",       "L'entità è sotto effetto del vamprismo")
LICANTHROPY               = FlagElement("Licantropia",     "L'entità è sotto effetto della licantropia")

# (TD) per queste fare una lista di crimini con tutti i dettagli del caso da
# utilizzare in un sistema esteso di legistlatura
THIEF                     = FlagElement("Thief",           "L'entità è un ladro")
ATTACKER                  = FlagElement("Attacker",        "L'entità è un aggressore")
KILLER                    = FlagElement("Killer",          "L'entità è un pkiller")
HEADHUNTER                = FlagElement("Headhunter",      "L'entità è un cacciatore di taglie")
OUTCAST                   = FlagElement("Outcast",         "L'entità è reietto da un clan")

# (TD) spostarle come enumerazioni dello stato di una connessione
AFK                       = FlagElement("Afk",             "Il giocatore è lontano dalla tastiera")
IDLE                      = FlagElement("Idle",            "Il giocatore è in idle")
LINKDEATH                 = FlagElement("Linkdeath",       "Il giocatore è in link-death")
EXTRACTED                 = FlagElement("Extracted",       "L'entità è stata rimossa dal gioco tramite il metodo extract, serve per debug sui riferimenti")
WEAKLY_EXTRACTED          = FlagElement("WeaklyExtracted", "L'entità è stata rimossa dal gioco perchè raghgruppata fisicamente con un'altra entità simile")

# Flag particolari relativi al comando eat, dig e seed
HERBIVORE                 = FlagElement("Erbivoro",        "L'entità si ciba prevalentemente di vegetali")
CARNIVOROUS               = FlagElement("Carnivoro",       "L'entità si ciba prevalentemente di carne")
INGESTED                  = FlagElement("Ingerito",        "L'entità si trova nello stomaco di qualcuno")
BURIED                    = FlagElement("Sepolto",         "L'entità è stata sepolta, interrata o seminata nel terreno o da qualche altra parte")
GROWING                   = FlagElement("Piantando",       "L'entità sta attivamente crescendo (gli stati di SeedType o PlantType verranno eseguiti)")
INTERACTABLE_FROM_OUTSIDE = FlagElement("Interagibile dall'esterno", "L'entità anche se si trova in un contenitore, è interagibile all'esterno, deve essere di norma utilizzato per entità che effettivamente 'sporgono' dalla locazione in cui si trovano (serve soprattutto per le piante cresciute nei loro vasi)")

# (TD) Forse queste flag direpop devono essere inserite come flag di reset
NO_REPOP                  = FlagElement("NoRepop",              "L'entità non viene repoppata se rimossa da dove è stata resettata")
NO_CHECK_STATUS           = FlagElement("NoCheckStatus",        "All'entità non vengono controllate le flag di door e di container (e di wear) quando viene resettato o controllato tramite un repop")
REPOP_ONLY_ON_EXTRACT     = FlagElement("RepopOnlyOnExtract",   "Repoppa non quando si sposta dalla locazione di reset originaria, ma quando viene rimossa dal gioco")
REPOP_ON_COORDS_AND_CODE  = FlagElement("RepopOnCoordsAndCode", "Repoppa non solo se le coordinate della room_reset sono quelle corrette ma anche se il codice della proto_room è identico")


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
