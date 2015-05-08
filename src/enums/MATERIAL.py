# -*- coding: utf-8 -*-

"""
Enumerazione dei materiali.
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = False


#-------------------------------------------------------------------------------

# (TD) pensare se aggiungere il type (METALLIC, ORGANIC ...) e il burning (temperatura di bruciatura per organici o di fusione per i metalli), creare la FLAG.UNBURNABLE apposita
class MaterialElement(EnumElement):
    def __init__(self, name, state, hardness):
        super(MaterialElement, self).__init__(name, description="")

        # Stato in cui si trova normalmente in natura il materiale
        if state not in ("NONE", "SOLID", "LIQUID", "GASEOUS"):
            print "Materiale %s senza uno state valido: %r" % (name, state)
        self.state = state

        # Durezza del materialem una durezza di 0 indica che non ha senso la
        # durezza per quel materiale (cosa normale per le cose immateriali)
        # 1 si distrugge subito, 100 non si distrugge (quasi) mai
        if hardness < 0 or hardness > 100:
            print "Materiale %s senza una hardness valida: %d" % (name, hardness)
        self.hardness = hardness
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE         = MaterialElement("Nessuno",           "NONE",    1)

# Materiali lignei
SOFTWOOD     = MaterialElement("legno dolce",       "SOLID",  25)
WOOD         = MaterialElement("legno",             "SOLID",  33)
HARDWOOD     = MaterialElement("legno duro",        "SOLID",  50)
TROPICALWOOD = MaterialElement("legni tropicali",   "SOLID",  50)  # Da considerarsi un legno duro
BAMBOO       = MaterialElement("bamboo",            "SOLID",  50)
OAK          = MaterialElement("quercia",           "SOLID",  50)
EBONY        = MaterialElement("ebano",             "SOLID",  50)
CORK         = MaterialElement("sughero",           "SOLID",  25)
WICKERS      = MaterialElement("vimini",            "SOLID",  25)
STRAW        = MaterialElement("paglia",            "SOLID",  10)

# Materiali vegetali
VEGETABLE    = MaterialElement("vegetale",          "SOLID",  15)

# Materiali cartacei
PAPER        = MaterialElement("carta",             "SOLID",  10)
PARCHMENT    = MaterialElement("pergamena",         "SOLID",  13)
CARDBOARD    = MaterialElement("cartone",           "SOLID",  15)
PAPYRUS      = MaterialElement("papiro",            "SOLID",  13)

# Materiali per vestiti e tessuti vari
COTTON       = MaterialElement("cotone",            "SOLID",   5)
SILK         = MaterialElement("seta",              "SOLID",   5)
SATIN        = MaterialElement("raso",              "SOLID",   5)
LACE         = MaterialElement("pizzo",             "SOLID",   5)
WOOL         = MaterialElement("lana",              "SOLID",   7)
LINE         = MaterialElement("lino",              "SOLID",   5)
CANVAS       = MaterialElement("tela",              "SOLID",   7)
CLOTH        = MaterialElement("tessuto",           "SOLID",   7)
VELVET       = MaterialElement("velluto",           "SOLID",   5)
FELT         = MaterialElement("feltro",            "SOLID",   5)
HEMP         = MaterialElement("canapa",            "SOLID",   7)
LEATHER      = MaterialElement("cuoio",             "SOLID",  15)
FUR          = MaterialElement("pelliccia",         "SOLID",  12)
SNAKESKIN    = MaterialElement("pelle di serpente", "SOLID",  10)
FEATHERS     = MaterialElement("penne",             "SOLID",  10)
CELLULOSE    = MaterialElement("cellulosa",         "SOLID",   7)

# Materiali metallici e minerari
ALLOY        = MaterialElement("lega",              "SOLID",  75)  # lega generica di metalli
METAL        = MaterialElement("metallo",           "SOLID",  70)  # metallo generico se proprio non si sa cosa dare", magari cambiare il sinonimo
STEEL        = MaterialElement("acciaio",           "SOLID",  80)
GOLD         = MaterialElement("oro",               "SOLID",  65)
SILVER       = MaterialElement("argento",           "SOLID",  68)
ELECTRUM     = MaterialElement("electrum",          "SOLID",  67)  # è una lega di oro e argento
MITHRIL      = MaterialElement("mithril",           "SOLID",  100)
PLATINUM     = MaterialElement("platino",           "SOLID",  100)
TITANIUM     = MaterialElement("titanio",           "SOLID",  100)
ALUMINIUM    = MaterialElement("alluminio",         "SOLID",  65)
IRON         = MaterialElement("ferro",             "SOLID",  70)
LEAD         = MaterialElement("piombo",            "SOLID",  75)
COPPER       = MaterialElement("rame",              "SOLID",  75)
BRONZE       = MaterialElement("bronzo",            "SOLID",  75)
BRASS        = MaterialElement("ottone",            "SOLID",  75)
TIN          = MaterialElement("stagno",            "SOLID",  65)
WIRE         = MaterialElement("filo metallico",    "SOLID",  70)
PEWTER       = MaterialElement("peltro",            "SOLID",  65)
ADAMANTITE   = MaterialElement("adamantio",         "SOLID",  100)
MERCURY      = MaterialElement("mercurio",          "LIQUID",  5)

# Materiali pietrosi
MARBLE       = MaterialElement("marmo",             "SOLID",  90)
STONE        = MaterialElement("pietra",            "SOLID",  70)
FLINT        = MaterialElement("selce",             "SOLID",  55)
LODESTONE    = MaterialElement("magnetite",         "SOLID",  44)
GRANITE      = MaterialElement("granito",           "SOLID",  90)
QUARTZ       = MaterialElement("quarzo",            "SOLID",  45)

# Materiali terrosi
SHELL        = MaterialElement("conchiglia",        "SOLID",  66)
EARTH        = MaterialElement("terra",             "SOLID",  44)
COAL         = MaterialElement("carbone",           "SOLID",  46)
SAND         = MaterialElement("sabbia",            "SOLID",  20)
CLAY         = MaterialElement("argilla",           "SOLID",  25)
ASH          = MaterialElement("cenere",            "SOLID",  10)
ACID         = MaterialElement("acido",             "SOLID",   5)

# Materiali preziosi
ENAMEL       = MaterialElement("smalto",            "SOLID",  66)
OBSIDIAN     = MaterialElement("ossidiana",         "SOLID",  66)
AMBER        = MaterialElement("ambra",             "SOLID",  66)
AGATE        = MaterialElement("agata",             "SOLID",  66)
LAPISLAZULI  = MaterialElement("lapislazzuli",      "SOLID",  66)
JADE         = MaterialElement("giada",             "SOLID",  66)
DIAMOND      = MaterialElement("diamante",          "SOLID",  100)
PEARL        = MaterialElement("perla",             "SOLID",  66)
GEM          = MaterialElement("gemma",             "SOLID",  66)
RUBY         = MaterialElement("rubino",            "SOLID",  66)
CRISTAL      = MaterialElement("cristallo",         "SOLID",  66)
IVORY        = MaterialElement("avorio",            "SOLID",  66)
CORUNDUM     = MaterialElement("corindone",         "SOLID",  66)  # Ossido di alluminio in cristalli estremamente duri di colore vario e lucentezza adamantina, di diverse varietà tra le quali alcune utilizzate come gemme
CORAL        = MaterialElement("corallo",           "SOLID",  66)
EMERALD      = MaterialElement("smeraldo",          "SOLID",  66)
AMETHYST     = MaterialElement("ametista",          "SOLID",  66)
NACRE        = MaterialElement("madreperla",        "SOLID",  66)
ONYX         = MaterialElement("onice",             "SOLID",  66)
MOONSTONE    = MaterialElement("pietra della luna", "SOLID",  66)  # Si tratta della varietà di feldspato detta "adularia", un silicato di potassio e alluminio con qualità da gemma
SAPPHIR      = MaterialElement("zaffiro",           "SOLID",  66)
OPAL         = MaterialElement("opale",             "SOLID",  66)
HEMATITE     = MaterialElement("ematite",           "SOLID",  66)
GARNET       = MaterialElement("granato mandarino", "SOLID",  66)

# Materiali commestibili
CREAM        = MaterialElement("crema",             "SOLID",  10)
MEAT         = MaterialElement("carne",             "SOLID",  10)
FISH         = MaterialElement("pesce",             "SOLID",  10)
MILK         = MaterialElement("latte",             "LIQUID",  5)
CHEESE       = MaterialElement("formaggio",         "SOLID",  10)
BUTTER       = MaterialElement("burro",             "SOLID",  10)
MARGARINE    = MaterialElement("margarina",         "SOLID",  10)
LEGUME       = MaterialElement("legumi",            "SOLID",  10)
FLOUR        = MaterialElement("farina",            "SOLID",  10)
RICE         = MaterialElement("riso",              "SOLID",  10)
BREAD        = MaterialElement("pane",              "SOLID",  10)  # Se si vuole specificare pane grattugiato o un particolare tipo di pane senza mettere ingredienti etcetc
OIL          = MaterialElement("olio",              "LIQUID",  5)  # Oppure si può intendere come olio per le lampade
PULP         = MaterialElement("polpa di frutta",   "SOLID",  10)
CEREAL       = MaterialElement("cereale",           "SOLID",  10)
FRUIT        = MaterialElement("frutta",            "SOLID",  10)  # Si intendono tutti i tipi di frutta e frutti, anche quelli secchi come noci e noccioline
VEGETABLES   = MaterialElement("verdura",           "SOLID",  10)
SEED         = MaterialElement("sementi",           "SOLID",  10)
HERB         = MaterialElement("erbe",              "SOLID",  10)
ROOT         = MaterialElement("radice",            "SOLID",  10)
CHOCOLATE    = MaterialElement("cioccolato",        "SOLID",  10)
PEPPER       = MaterialElement("pepe",              "SOLID",  10)
KERNEL       = MaterialElement("nocciola",          "SOLID",  10)  # noccioli dei frutti
MUSHROOM     = MaterialElement("fungo",             "SOLID",  10)
CACAO        = MaterialElement("cacao",             "SOLID",  10)
EGG          = MaterialElement("uova",              "SOLID",  10)
SUGAR        = MaterialElement("zucchero",          "SOLID",  10)
WATER        = MaterialElement("acqua",             "LIQUID",  5)
ALCOHOL      = MaterialElement("alcol",             "LIQUID",  5)

# Materiali per pavimenti o soffitti:
TILES        = MaterialElement("tegole",            "SOLID",  70)

# Materiali vari
WEB          = MaterialElement("ragnatela",         "SOLID",  10)
SLIME        = MaterialElement("melma",             "SOLID",  10)
JELLY        = MaterialElement("gelatina",          "SOLID",  10)
WAX          = MaterialElement("cera",              "SOLID",  10)
RUBBER       = MaterialElement("gomma",             "SOLID",  10)
BALM         = MaterialElement("balsamo",           "LIQUID", 10)
RUNE         = MaterialElement("runa",              "SOLID",  50)
ESSENCE      = MaterialElement("essenza",           "GASEOUS", 0)  # Essenze profumate
LEAF         = MaterialElement("fogliame",          "SOLID",  10)
SPONGE       = MaterialElement("spugna",            "SOLID",  10)
ELASTIC      = MaterialElement("elastico",          "SOLID",  10)
FLOWER       = MaterialElement("fiori",             "SOLID",  10)
DUST         = MaterialElement("polvere",           "SOLID",  10)
THORN        = MaterialElement("spine",             "SOLID",  10)
SOAP         = MaterialElement("sapone",            "SOLID",  10)
INCENSE      = MaterialElement("incenso",           "SOLID",  10)   # Inteso come oggetto e non come profumo
SPORE        = MaterialElement("spore",             "SOLID",  10)
DRAGONSCALE  = MaterialElement("scaglie di drago",  "SOLID",  90)
GLASS        = MaterialElement("vetro",             "SOLID",  22)
POTTERY      = MaterialElement("ceramica",          "SOLID",  25)
PORCELAIN    = MaterialElement("porcellana",        "SOLID",  20)
ICE          = MaterialElement("ghiaccio",          "SOLID",  25)

# Materiali anatomici
FLESH        = MaterialElement("carne",             "SOLID",  20)
HAIR         = MaterialElement("capelli",           "SOLID",   2)  # Capelli ma anche crine di cavallo et similia
GUT          = MaterialElement("budella",           "SOLID",  20)
HORN         = MaterialElement("corno",             "SOLID",  35)
BLOOD        = MaterialElement("sangue",            "LIQUID",  1)
NAIL         = MaterialElement("unghia",            "SOLID",  15)  # Anche da intendersi artigli, zoccoli e tutto l'ungulame animale
TOOTH        = MaterialElement("dente",             "SOLID",  25)  # Anche zanne
BEAK         = MaterialElement("becco",             "SOLID",  30)
PRICK        = MaterialElement("aculei",            "SOLID",  25)
BONE         = MaterialElement("osso",              "SOLID",  31)

# Materiali.. immateriali
ENERGY       = MaterialElement("energia",           "NONE",    0)
NOTHINGNESS  = MaterialElement("nulla",             "NONE",    0)
VOID         = MaterialElement("vuoto",             "NONE",    0)
AIR          = MaterialElement("aria",              "GASEOUS", 0)
LIGHT        = MaterialElement("luce",              "NONE",    0)
SHADOW       = MaterialElement("ombra",             "NONE",    0)  # Anche oscurità può andare bene
SPIRIT       = MaterialElement("spirito",           "NONE",    0)  # materiale.. fantasma O_o
FIRE         = MaterialElement("fuoco",             "GASEOUS", 0)
MANA         = MaterialElement("mana",              "NONE",    0)  # Servirà per gli oggetti fatti magicamente dai maghi costruttori, o per riparare gli oggetti magicamente, al posto del metallo ci mette il mana, se si rovina lo si può rigenerare tramite mana
UNKNOWN      = MaterialElement("sconosciuto",       "NONE",    0)  # L'ho messo solo per gli oggetti che fanno da tappa buchi, tipo l'ultimo dell'accademia


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
