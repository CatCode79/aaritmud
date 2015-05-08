# -*- coding: utf-8 -*-

"""
Enumerazione delle parti del corpo.
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = True


#-------------------------------------------------------------------------------

class PartElement(EnumElement):
    def __init__(self, name, description=""):
        super(PartElement, self).__init__(name, description)
        self.equip_entity  = ""  # Messaggio alternativo per il comando equip al posto della descrizione
        self.equip_others  = ""  # Messaggio da inviare quando gli altri guardano l'equipaggiamento di uno
        self.equip_target  = ""  # Messaggio da inviare all'oggetto indossato che guarda l'equipaggiamento del suo padrone
        self.wear_entity   = ""  # Messaggio alternativo per il comando wear al posto della descrizione
        self.wear_others   = ""  # Messaggio da inviare quando gli altri guardano il wear di uno
        self.wear_target   = ""  # Messaggio da inviare all'oggetto indossato che guarda il wear del suo padrone
        self.remove_entity = ""  # Messaggio alternativo per il comando remove al posto della descrizione
        self.remove_others = ""  # Messaggio da inviare quando gli altri guardano il remove di uno
        self.remove_target = ""  # Messaggio da inviare all'oggetto indossato che guarda il remove del suo padrone
        #self.show_always     = False   (TT) da pensare
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE                = PartElement("nessuna",    "")
BODY                = PartElement("corpo",      "al corpo")
FLOATING            = PartElement("fluttuante", "che ti fluttua attorno")

# Parti generiche che può avere un mob umanoide
HEAD                = PartElement("testa",            "in testa")
TORSO               = PartElement("torso",            "al torso")
LEFT_UPPER_LIMB     = PartElement("braccio sinistro", "sul braccio sinistro")
RIGHT_UPPER_LIMB    = PartElement("braccio destro",   "sul braccio destro")
LEFT_LOWER_LIMB     = PartElement("gamba sinistra",   "sulla gamba sinistra")
RIGHT_LOWER_LIMB    = PartElement("gamba destra",     "sulla gamba destra")

# Parti che formano la testa di un umanoide
HAIR                = PartElement("capelli",               "ai capelli")
FOREHEAD            = PartElement("fronte",                "sulla fronte")
FACE                = PartElement("viso",                  "sul viso")
LEFT_EYEBROW        = PartElement("sopracciglio sinistro", "al sopracciglio sinistro")
RIGHT_EYEBROW       = PartElement("sopracciglio destro",   "al sopracciglio destro")
LEFT_EYELASH        = PartElement("ciglia sinistra",       "sulla ciglia sinistra")
RIGHT_EYELASH       = PartElement("ciglia destra",         "sulla ciglia destra")
LEFT_EYE            = PartElement("occhio sinistro",       "all'occhio sinistro")
RIGHT_EYE           = PartElement("occhio destro",         "all'occhio destro")
LEFT_EAR            = PartElement("orecchia sinistra",     "all'orecchia sinistra")
RIGHT_EAR           = PartElement("orecchia destra",       "all'orecchia destra")
NOSE                = PartElement("naso",                  "sul naso")
MUSTACHE            = PartElement("baffi",                 "ai baffi")
LIP                 = PartElement("labbra",                "sulle labbra")
MOUTH               = PartElement("bocca",                 "in bocca")
CHIN                = PartElement("mento",                 "al mento")
BEARD               = PartElement("barba",                 "alla barba")
NAPE                = PartElement("nuca",                  "alla nuca")
NECK                = PartElement("collo",                 "al collo")
THROAT              = PartElement("gola",                  "alla gola")  # (TT) mah servirà? da rimuovere penso
BRAIN               = PartElement("cervello",              "al cervello")

#TONGUE             = PartElement("Lingua")

# Parti che formano il torso di un umanoide
CHEST               = PartElement("torace",           "sul torace")
BREAST              = PartElement("petto",            "al petto")
BELLY               = PartElement("pancia",           "sulla pancia")
BELLYBUTTON         = PartElement("ombelico",         "all'ombelico")
WAIST               = PartElement("vita",             "alla vita")
LEFT_HIP            = PartElement("fianco sinistro",  "al fianco sinistro")
RIGHT_HIP           = PartElement("fianco destro",    "al fianco destro")
BACK                = PartElement("schiena",          "sulla schiena")
GROIN               = PartElement("inguine",          "all'inguine")
ASS                 = PartElement("sedere",           "al sedere")
LEFT_LUNG           = PartElement("polmone sinistro", "al polmone sinistro")
RIGHT_LUNG          = PartElement("polmone destro",   "al polmone destro")
HEART               = PartElement("cuore",            "al cuore")
STOMACH             = PartElement("stomaco",          "allo stomaco")
LIVER               = PartElement("fegato",           "al fegato")
LEFT_KIDNEY         = PartElement("rene sinistro",    "al rene sinistro")
RIGHT_KIDNEY        = PartElement("rene destro",      "al rene destro")
GUTS                = PartElement("budella",          "alle budella")

# Parti che formano un braccio umanoide
LEFT_SHOULDER       = PartElement("spalla sinistra",      "alla spalla sinistra")
LEFT_BICEPS         = PartElement("bicipite sinistro",    "al bicipite sinistro")
LEFT_ELBOW          = PartElement("gomito sinistro",      "sul gomito sinistro")
LEFT_FOREARM        = PartElement("avambraccio sinistro", "all'avambraccio sinistro")
LEFT_WRIST          = PartElement("polso sinistro",       "sul polso sinistro")
LEFT_HAND           = PartElement("mano sinistra",        "alla mano sinistra")
                    
RIGHT_SHOULDER      = PartElement("spalla destra",      "alla spalla destra")
RIGHT_BICEPS        = PartElement("bicipite destro",    "al bicipite destro")
RIGHT_ELBOW         = PartElement("gomito destro",      "sul gomito destro")
RIGHT_FOREARM       = PartElement("avambraccio destro", "all'avambraccio destro")
RIGHT_WRIST         = PartElement("polso destro",       "sul polso destro")
RIGHT_HAND          = PartElement("mano destra",        "alla mano destra")

# Parti che formano una mano umanoide
LEFT_BACKHAND       = PartElement("dorso della mano sinistra",  "sul dorso della mano sinistra")
LEFT_PALM           = PartElement("palmo della mano sinistra",  "sul palmo della mano sinistra")
LEFT_THUMB          = PartElement("pollice sinistro",           "al pollice sinistro")
LEFT_FOREFINGER     = PartElement("indice sinistro",            "all'indice sinistro")
LEFT_MIDDLE_FINGER  = PartElement("medio sinistro",             "al medio sinistro")
LEFT_RING_FINGER    = PartElement("anulare sinistro",           "all'anulare sinistro")
LEFT_LITTLE_FINGER  = PartElement("mignolo sinistro",           "al mignolo sinistro")
LEFT_NAILS          = PartElement("unghie della mano sinistra", "sulle unghie della mano sinistra")

RIGHT_BACKHAND      = PartElement("dorso della mano destra",  "sul dorso della mano destra")
RIGHT_PALM          = PartElement("palmo della mano destra",  "sul palmo della mano destra")
RIGHT_THUMB         = PartElement("pollice destro",           "al pollice destro")
RIGHT_FOREFINGER    = PartElement("indice destro",            "all'indice destro")
RIGHT_MIDDLE_FINGER = PartElement("medio destro",             "al medio destro")
RIGHT_RING_FINGER   = PartElement("anulare destro",           "all'anulare destro")
RIGHT_LITTLE_FINGER = PartElement("mignolo destro",           "al mignolo destro")
RIGHT_NAILS         = PartElement("unghie della mano destra", "sulle unghie della mano destra")

# Parti che formano una gamba umanoide
LEFT_THIGH          = PartElement("coscia sinistra",    "alla coscia sinistra")
LEFT_KNEE           = PartElement("ginocchio sinistro", "al ginocchio sinistro")
LEFT_TIBIA          = PartElement("tibia sinistra",     "sulla tibia sinistra")
LEFT_ANKLE          = PartElement("caviglia sinistra",  "sulla caviglia sinistra")
LEFT_FOOT           = PartElement("piede sinistro",     "al piede sinistro")

RIGHT_THIGH         = PartElement("coscia destra",    "alla coscia destra")
RIGHT_KNEE          = PartElement("ginocchio destro", "al ginocchio sinistro")
RIGHT_TIBIA         = PartElement("tibia destra",     "sulla tibia destra")
RIGHT_ANKLE         = PartElement("caviglia destra",  "sulla caviglia destra")
RIGHT_FOOT          = PartElement("piede destro",     "al piede destro")

# Parti relative a mob non umanoidi
LONGTONGUE          = PartElement("lingua lungua",     "sulla lingua lungua")
TENTACLE            = PartElement("tentacolo",         "al tentacolo")
EYESTALK            = PartElement("tentacolo oculare", "al tentacolo oculare")
FINS                = PartElement("pinna",             "sulla pinna")
WINGS               = PartElement("ala",               "sull'ala")
TAIL                = PartElement("coda",              "alla coda")
SCALES              = PartElement("scaglie",           "sulle scaglie")
CLAW                = PartElement("artiglio",          "all'artiglio")
FANG                = PartElement("zanna avvelenata",  "alla zanna avvelenata")
HORN                = PartElement("corno",             "sul corno")
TUSKS               = PartElement("zanna",             "alla zanna")
SHARPSCALES         = PartElement("scaglie ondulate",  "sulle scaglie ondulate")
BEAK                = PartElement("becco",             "al becco")
HOOVE               = PartElement("zoccolo",           "allo zoccolo")
PAW                 = PartElement("artiglio",          "sull'artiglio")
FORELEG             = PartElement("zampa posteriore",  "alla zampa posteriore")
FEATHERS            = PartElement("piume",             "sulle piume")

# Parti generiche (TT) non dovrebbe più servirmi
#FINGER              = PartElement("Dito", "Dito generico")

# Parti-decalcomanie (TT) non dovrebbe più servirmi
#SCAR                = PartElement("Cicatrice", "Si può inserire in qualunque parte del corpo, come se fosse una decalcomania")
#MOLE                = PartElement("Neo",       "Stesso utilizzo della cicatrice, in parti esterne del corpo")

# "Parti" per gestire alcune cose speciali:
WIELD               = PartElement("impugnata", "impugnat$O con la $hand1")
HOLD                = PartElement("tenuta",    "tenut$O nella $hand2")


# Messaggi speciali per alcune parti del corpo particolari.
# Il sistema è stato implementato nella funzione get_part_descriptions.
FLOATING.equip_entity  = ""  # non serve, prende la descrizione di default
FLOATING.equip_others  = "che $GLI fluttua attorno"
FLOATING.equip_target  = "che $GLI fluttui attorno"
FLOATING.wear_entity   = "che comincia a fluttuarti attorno"
FLOATING.wear_others   = "che comincia a fluttuar$gli attorno"
FLOATING.wear_target   = "che cominci a fluttuar$gli attorno"
FLOATING.remove_entity = "che smette a fluttuarti attorno"
FLOATING.remove_others = "che smette di fluttuar$gli attorno"
FLOATING.remove_target = "che smetti di fluttuar$gli attorno"

WIELD.remove_entity = "con la $hand1"
WIELD.remove_others = "con la $hand1"
WIELD.remove_target = "con la $hand1"
HOLD.remove_entity  = "con la $hand2"
HOLD.remove_others  = "con la $hand2"
HOLD.remove_target  = "con la $hand2"

BACK.remove_entity = "dalla schiena"
BACK.remove_others = "dalla schiena"
BACK.remove_target = "dalla schiena"


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
