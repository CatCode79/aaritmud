# -*- coding: utf-8 -*-

"""
Enumerazione dei settori delle stanze.
"""

from src.element import EnumElement, finalize_enumeration
from src.enums   import GRAMMAR


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = True


#-------------------------------------------------------------------------------

class SectorElement(EnumElement):
    SHOW_ATTRS_ON_HTML = ["fertile"]

    def __init__(self, name, description=""):
        super(SectorElement, self).__init__(name, description)
        self.genre          = GRAMMAR.FEMININE  # Indica se il nome del settore è maschile
        self.number         = GRAMMAR.MASCULINE # Indica se il nome del settore è singolare
        self.fertile        = False             # Indica se il settore è fertile e vi si può seminare
        self.dig_difficulty = 0                 # Indica la facilità con cui si scava nel terreno (da 0 a 100, 100 impossibile)
        self.tile           = ""                # Tile grafico relativo alla wild
    # - Fine Inizializzazione -


#-------------------------------------------------------------------------------


NONE = SectorElement("Nessuno")

# Settori che indicano un'altitudine
PLAIN        = SectorElement("[lightgreen]pianura[close]",  "Settore della pianura")
SAVANNA      = SectorElement("[yellow]savana[close]",       "Settore per la savana: ampie distese erbose, più o meno alte, in zone tropicali, dove le temperature sono elevate e le pioggie hanno un andamento stagionale")
HILL         = SectorElement("[green]collina[close]",       "Settore per la collina")
MOUNTAIN     = SectorElement("[lightgray]montagna[close]",  "Settore per la montagna")
PLATEAU      = SectorElement("altopiano",                   "Settore per gli altopiani")
HIGHMOUNTAIN = SectorElement("[gray]alta montagna[close]",  "Settore per l'alta montagna")
PEAK         = SectorElement("[darkgray]picco[close]",      "Settore per i picchi, alte montagne con pareti sempre verticali e corpo della montagna stretto")

# Settori che indicano un certo tipo di vegetazione o di densità di vegetazione:
SHRUB  = SectorElement("[darkgreen]macchia[close]",    "Settore per la macchia")
WOOD   = SectorElement("[green]bosco[close]",          "Settore per il bosco")
FOREST = SectorElement("[forestgreen]foresta[close]",  "Settore per la foresta")
JUNGLE = SectorElement("[green]giungla[close]",        "Settore per la giungla")

# Altri:
DESERT      = SectorElement("[darkgoldenrod]deserto[close]",       "Settore per i deserti")
DUNNO       = SectorElement("[darkgoldenrod]duna[close]",          "Settore per le colline nei deserti")
QUICKSAND   = SectorElement("[darkgoldenrod]sabbie mobili[close]", "Settore in cui la probabilità di trovarsi invischiati in questa trappola è alta")
CAVERN      = SectorElement("[gray]caverna[close]",                "Settore per caverne piene di stallatiti e stalagmiti")
UNDERGROUND = SectorElement("[darkgray]sottoterra[close]",         "Settore per tutte le zone sottoterra non simili a caverne o a dungeon")
VOLCANO     = SectorElement("[red]vulcano[close]",                 "Settore per i vulcani")
LAVA        = SectorElement("[red]lava[close]",                    "Settore per la lava vulcanica")
HEATH       = SectorElement("[darkgreen]brughiera[close]",         "Settore per la brughiera: temperature mediamente più basse e maggiore umidità che porta anche alla formazione di stagni, paludi e torbiere.")
SWAMP       = SectorElement("palude",                              "Settore per le paludi e fanghiglia simile")
TAIGA       = SectorElement("taiga",                               "Settore per la Taiga: La vegetazione è formata da abeti, larici e pini, con foglie aghiformi presenti tutto l'anno, possono raggiungere 40-50 metri di altezza, tuttavia con il calare della temperatura anche l'altezza degli alberi diminuisce; è spesso presente anche la betulla. Nella taiga si alternano alla foresta zone umide che formano acquitrini, paludi e torbiere.")
TUNDRA      = SectorElement("tundra",                              "Settore per le tundre: dove la crescita degli alberi è ostacolata dalle basse temperature e dalla breve stagione estiva. Vegetazione tipica: muschi e licheni e pochi arbusti. A volte arbusti nani sempreverdi.")
SNOW        = SectorElement("[white]neve[close]",                  "Settore per luoghi innevati")
ICE         = SectorElement("[white]ghiaccio[close]",              "Settore per ghiacciai, laghi ghiacciati e simili")
STEPPE      = SectorElement("steppa",                              "Settore per la steppa: La steppa è un paesaggio naturale, caratterizzato dalla pressoché totale assenza di alberi. La vegetazione è costituita unicamente da erba. Estati calde ed inverni freddi.")
ROCKY       = SectorElement("[gray]terreno roccioso[close]",       "Settore pieno di pietre, può essere una pianura pietrosa come un deserto..")

# Settori relativi all'acqua
RIVER      = SectorElement("[cyan]fiume[close]",              "Settore per i fiumi")
RAPIDS     = SectorElement("[cyan]rapide[close]",             "Settore per le rapide")
WATERFALL  = SectorElement("[cyan]cascata[close]",            "Settore per una cascata")
LAKE       = SectorElement("[darkcyan]lago[close]",           "Settore per i laghi")
SEA        = SectorElement("[lightblue]mare[close]",          "Settore del mare o dell'oceano")
OCEANFLOOR = SectorElement("[darkslategray]fondale[close]",   "Il settore più in basso di una serie di stanze con settori underwater")
REEF       = SectorElement("[darkslategray]scogliera[close]", "Settore per scogliere")
SHORE      = SectorElement("[orange]spiaggia[close]",         "Settore per le spiagge")

# Settori relativi ad opere non naturali
HOUSE      = SectorElement("casa",                            "Settore per le case")
SHOP       = SectorElement("negozio",                         "Settore per i negozi")
BLACKSMITH = SectorElement("fabbro",                          "Settore per i fabbri e gli armaioli")
TAVERN     = SectorElement("taverna",                         "Settore per le taverne, ristoranti e alberghi")
VILLA      = SectorElement("villa",                           "Settore per le ville")
ESTATE     = SectorElement("proprietà",                       "Settore per le grosse case o ville signorili")
CASTLE     = SectorElement("castello",                        "Settore per i castelli")
VILLAGE    = SectorElement("villaggio",                       "Settore per i villaggi")
CITY       = SectorElement("città",                           "Settore per le aree di città")
WALL       = SectorElement("muro",                            "Mura difensive di una città o di un villaggio su cui camminare")
BRIDGE     = SectorElement("ponte",                           "Settore per un qualsiasi tipo di ponte")
TERRACE    = SectorElement("gradinata",                       "Settore per le gradinate degli spalti dell'arena")
PATH       = SectorElement("sentiero",                        "Settore per i sentiero")
ROAD       = SectorElement("strada",                          "Settore per le strade")
FARMLAND   = SectorElement("[green]terreno coltivato[close]", "Settore che indica dei campi coltivati")
PORT       = SectorElement("porto",                           "Settore per i porti")
DOCK       = SectorElement("attracco",                        "Settore che indica dove le barche possono attraccare senza pericolo")
PASTURE    = SectorElement("[green]pascolo[close]",           "Settore in cui gli animali erbivori vengono attirati")
RUIN       = SectorElement("[darkgray]rovine[close]",         "Rovine di qualsiasi tipo, di una casa, di una città..")

# Settori che non hanno una consistenza fisica
AIR  = SectorElement("[lightcyan]Aria[close]", "Tutte le stanze virtualmente create su quelle dove ci si mette i piedi sono nell'aria")
VOID = SectorElement("Vuoto",                  "Settore per il vuoto totale, spaziale o magico")


# Supporto per la manipolazione grammaticale
PLAIN.genre, PLAIN.number               = GRAMMAR.FEMININE,  GRAMMAR.SINGULAR
SAVANNA.genre, SAVANNA.number           = GRAMMAR.FEMININE,  GRAMMAR.SINGULAR
HILL.genre, HILL.number                 = GRAMMAR.FEMININE,  GRAMMAR.SINGULAR
MOUNTAIN.genre, MOUNTAIN.number         = GRAMMAR.FEMININE,  GRAMMAR.SINGULAR
PLATEAU.genre, PLATEAU.number           = GRAMMAR.MASCULINE, GRAMMAR.SINGULAR
HIGHMOUNTAIN.genre, HIGHMOUNTAIN.number = GRAMMAR.FEMININE,  GRAMMAR.SINGULAR
PEAK.genre, PEAK.number                 = GRAMMAR.MASCULINE, GRAMMAR.SINGULAR
SHRUB.genre, SHRUB.number               = GRAMMAR.FEMININE,  GRAMMAR.SINGULAR
WOOD.genre, WOOD.number                 = GRAMMAR.MASCULINE, GRAMMAR.SINGULAR
FOREST.genre, FOREST.number             = GRAMMAR.FEMININE,  GRAMMAR.SINGULAR
JUNGLE.genre, JUNGLE.number             = GRAMMAR.FEMININE,  GRAMMAR.SINGULAR
DESERT.genre, DESERT.number             = GRAMMAR.MASCULINE, GRAMMAR.SINGULAR
DUNNO.genre, DUNNO.number               = GRAMMAR.FEMININE,  GRAMMAR.SINGULAR
QUICKSAND.genre, QUICKSAND.number       = GRAMMAR.FEMININE,  GRAMMAR.PLURAL
CAVERN.genre, CAVERN.number             = GRAMMAR.FEMININE,  GRAMMAR.SINGULAR
UNDERGROUND.genre, UNDERGROUND.number   = GRAMMAR.MASCULINE, GRAMMAR.SINGULAR
VOLCANO.genre, VOLCANO.number           = GRAMMAR.MASCULINE, GRAMMAR.SINGULAR
LAVA.genre, LAVA.number                 = GRAMMAR.FEMININE,  GRAMMAR.SINGULAR
HEATH.genre, HEATH.number               = GRAMMAR.FEMININE,  GRAMMAR.SINGULAR
SWAMP.genre, SWAMP.number               = GRAMMAR.FEMININE,  GRAMMAR.SINGULAR
TAIGA.genre, TAIGA.number               = GRAMMAR.FEMININE,  GRAMMAR.SINGULAR
TUNDRA.genre, TUNDRA.number             = GRAMMAR.FEMININE,  GRAMMAR.SINGULAR
ICE.genre, ICE.number                   = GRAMMAR.MASCULINE, GRAMMAR.SINGULAR
STEPPE.genre, STEPPE.number             = GRAMMAR.FEMININE,  GRAMMAR.SINGULAR
ROCKY.genre, ROCKY.number               = GRAMMAR.MASCULINE, GRAMMAR.SINGULAR
RIVER.genre, RIVER.number               = GRAMMAR.MASCULINE, GRAMMAR.SINGULAR
RAPIDS.genre, RAPIDS.number             = GRAMMAR.FEMININE,  GRAMMAR.PLURAL
WATERFALL.genre, WATERFALL.number       = GRAMMAR.FEMININE,  GRAMMAR.SINGULAR
LAKE.genre, LAKE.number                 = GRAMMAR.MASCULINE, GRAMMAR.SINGULAR
SEA.genre, SEA.number                   = GRAMMAR.MASCULINE, GRAMMAR.SINGULAR
OCEANFLOOR.genre, OCEANFLOOR.number     = GRAMMAR.MASCULINE, GRAMMAR.SINGULAR
REEF.genre, REEF.number                 = GRAMMAR.FEMININE,  GRAMMAR.SINGULAR
SHORE.genre, SHORE.number               = GRAMMAR.FEMININE,  GRAMMAR.SINGULAR
HOUSE.genre, HOUSE.number               = GRAMMAR.FEMININE,  GRAMMAR.SINGULAR
SHOP.genre, SHOP.number                 = GRAMMAR.MASCULINE, GRAMMAR.SINGULAR
BLACKSMITH.genre, BLACKSMITH.number     = GRAMMAR.MASCULINE, GRAMMAR.SINGULAR
TAVERN.genre, TAVERN.number             = GRAMMAR.FEMININE,  GRAMMAR.SINGULAR
VILLA.genre, VILLA.number               = GRAMMAR.FEMININE,  GRAMMAR.SINGULAR
ESTATE.genre, ESTATE.number             = GRAMMAR.FEMININE,  GRAMMAR.SINGULAR
CASTLE.genre, CASTLE.number             = GRAMMAR.MASCULINE, GRAMMAR.SINGULAR
VILLAGE.genre, VILLAGE.number           = GRAMMAR.MASCULINE, GRAMMAR.SINGULAR
CITY.genre, CITY.number                 = GRAMMAR.FEMININE,  GRAMMAR.SINGULAR
WALL.genre, WALL.number                 = GRAMMAR.MASCULINE, GRAMMAR.SINGULAR
BRIDGE.genre, BRIDGE.number             = GRAMMAR.FEMININE,  GRAMMAR.SINGULAR
TERRACE.genre, TERRACE.number           = GRAMMAR.FEMININE,  GRAMMAR.SINGULAR
PATH.genre, PATH.number                 = GRAMMAR.MASCULINE, GRAMMAR.SINGULAR
ROAD.genre, ROAD.number                 = GRAMMAR.FEMININE,  GRAMMAR.SINGULAR
FARMLAND.genre, FARMLAND.number         = GRAMMAR.MASCULINE, GRAMMAR.SINGULAR
PORT.genre, PORT.number                 = GRAMMAR.MASCULINE, GRAMMAR.SINGULAR
DOCK.genre, DOCK.number                 = GRAMMAR.MASCULINE, GRAMMAR.SINGULAR
PASTURE.genre, PASTURE.number           = GRAMMAR.MASCULINE, GRAMMAR.SINGULAR
RUIN.genre, RUIN.number                 = GRAMMAR.FEMININE,  GRAMMAR.PLURAL
AIR.genre, AIR.number                   = GRAMMAR.FEMININE,  GRAMMAR.SINGULAR
VOID.genre, VOID.number                 = GRAMMAR.MASCULINE, GRAMMAR.SINGULAR


# Indicatore di fertilità del terreno  (TD) da convertire in percentuale come il dig difficulty
PLAIN.fertile    = True
SAVANNA.fertile  = True
HILL.fertile     = True
MOUNTAIN.fertile = True
PLATEAU.fertile  = True
SHRUB.fertile    = True
WOOD.fertile     = True
FOREST.fertile   = True
JUNGLE.fertile   = True
HEATH.fertile    = True
SWAMP.fertile    = True
TAIGA.fertile    = True
TUNDRA.fertile   = True
STEPPE.fertile   = True
SHORE.fertile    = True
PATH.fertile     = True
FARMLAND.fertile = True
PASTURE.fertile  = True


# Difficoltà nello scavare il settore
PLAIN.dig_difficulty        = 0
SAVANNA.dig_difficulty      = 0
HILL.dig_difficulty         = 0
MOUNTAIN.dig_difficulty     = 25
PLATEAU.dig_difficulty      = 0
HIGHMOUNTAIN.dig_difficulty = 50
PEAK.dig_difficulty         = 75
SHRUB.dig_difficulty        = 0
WOOD.dig_difficulty         = 0
FOREST.dig_difficulty       = 0
JUNGLE.dig_difficulty       = 0
DESERT.dig_difficulty       = 0
DUNNO.dig_difficulty        = 0
QUICKSAND.dig_difficulty    = 0
CAVERN.dig_difficulty       = 50
UNDERGROUND.dig_difficulty  = 0
VOLCANO.dig_difficulty      = 50
LAVA.dig_difficulty         = 99
HEATH.dig_difficulty        = 0
SWAMP.dig_difficulty        = 0
TAIGA.dig_difficulty        = 0
TUNDRA.dig_difficulty       = 0
ICE.dig_difficulty          = 50
STEPPE.dig_difficulty       = 0
ROCKY.dig_difficulty        = 50
RIVER.dig_difficulty        = 75
RAPIDS.dig_difficulty       = 90
WATERFALL.dig_difficulty    = 90
LAKE.dig_difficulty         = 90
SEA.dig_difficulty          = 90
OCEANFLOOR.dig_difficulty   = 90
REEF.dig_difficulty         = 90
SHORE.dig_difficulty        = 80
ESTATE.dig_difficulty       = 90
VILLAGE.dig_difficulty      = 50
CITY.dig_difficulty         = 75
WALL.dig_difficulty         = 90
BRIDGE.dig_difficulty       = 99
TERRACE.dig_difficulty      = 99
PATH.dig_difficulty         = 50
ROAD.dig_difficulty         = 75
FARMLAND.dig_difficulty     = 0
PORT.dig_difficulty         = 90
DOCK.dig_difficulty         = 90
PASTURE.dig_difficulty      = 0
RUIN.dig_difficulty         = 50
AIR.dig_difficulty          = 100
VOID.dig_difficulty         = 100


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
