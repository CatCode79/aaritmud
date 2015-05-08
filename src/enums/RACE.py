# -*- coding: utf-8 -*-

"""
Enumerazione delle razze del gioco.
"""


#= IMPORT ======================================================================

from src.element import EnumElement, Flags, finalize_enumeration
from src.enums   import CHANNEL, COLOR, LANGUAGE, SEX


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = True


#-------------------------------------------------------------------------------

class RaceElement(EnumElement):
    def __init__(self, name, description=""):
        super(RaceElement, self).__init__(name, description)

        self.playable           = False
        self.allowed_sexs       = Flags(SEX.MALE, SEX.FEMALE)
        self.weight_low         = 0
        self.weight_medium      = 0
        self.weight_high        = 0
        self.height_low         = 0
        self.height_medium      = 0
        self.height_high        = 0
        self.age_adolescence    = 0
        self.age_adult          = 0
        self.age_old            = 0
        self.have_hair          = False
        self.natural_language   = LANGUAGE.COMMON
        self.initial_languages  = [LANGUAGE.COMMON, ]
        self.voice_potence      = 0
        self.say_verb_you       = CHANNEL.SAY.verb_you
        self.say_verb_it        = CHANNEL.SAY.verb_it
        self.go_verb_you        = "Vai"
        self.go_verb_it         = "va"
        self.come_verb_it       = "è venuto"
        self.run_verb_you       = "Corri"
        self.run_verb_it        = "corre"
        self.runned_verb_it     = "ha corso"
        self.copper_coin        = "ikea_item_coin-human-copper"
        self.silver_coin        = "ikea_item_coin-human-silver"
        self.gold_coin          = "ikea_item_coin-human-gold"
        self.mithril_coin       = "ikea_item_coin-human-mithril"
        self.hand               = "mano"
        self.hands              = "mani"
        self.foot               = "piede"
        self.feet               = "piedi"
        self.feet2              = "ai tuoi piedi"
        self.skin               = "pelle"
        self.skins              = [COLOR.PINK, COLOR.DEEPPINK, COLOR.HOTPINK, COLOR.LIGHTPINK]
        self.tongue             = "[red]lingua[close]"
        self.smell_on_water     = False
        self.icon               = ""
        self.bodies             = ["human", ]
        self.affects            = []  # (TD)
    #- Fine Inizializzazione -

    def get_money_proto(self, type):
        from src.database import database
        from src.log      import log
        from src.item     import Item
        from src.mob      import Mob

        if not type:
            log.bug("type non è un parametr valido: %r" % type)
            return ""

        # ---------------------------------------------------------------------

        money_code = getattr(self, type + "_coin")
        if "item" in money_code.split("_"):
            table_name = "proto_items"
        else:
            table_name = "proto_mobs"

        table = database[table_name]
        try:
            return table[money_code]
        except KeyError:
            log.bug("Dato nella tabella %s non trovato con chiave %s" % (table_name, money_code))
            return None
    #- Fine Metodo -

    def get_money_instance(self, type):
        from src.log  import log
        from src.item import Item
        from src.mob  import Mob

        if not type:
            log.bug("type non è un parametr valido: %r" % type)
            return ""

        # ---------------------------------------------------------------------

        money_code = getattr(self, type + "_coin")
        if "item" in money_code.split("_"):
            return Item(money_code)
        else:
            return Mob(money_code)
    #- Fine Metodo -

    def get_money_icon(self, type):
        from src.log import log

        if not type:
            log.bug("type non è un parametr valido: %r" % type)
            return ""

        # ---------------------------------------------------------------------

        prototype = self.get_money_proto(type)
        if not prototype:
            log.bug("prototype ricavato per l'icona della moneta %s non è valido: %r" % (type, prototype))
            return "blank.gif"

        if not prototype.icon:
            log.bug("prototype %s senza icona valida per la tipologia di moneta %s: %r" % (prototype.code, type, prototype.icon))
            return "blank.gif"

        return prototype.icon
    #- Fine Metodo -


#-------------------------------------------------------------------------------

NONE     = RaceElement("Nessuna")

# Quando non esiste nessuna razza utilizzabile per il mob che state creando
# allora potrebbe essere il caso di usare una delle seguenti famiglie.
# Se invece il mob è abbastanza caratteristico e si suppone verrà utilizzato
# spesso allora forse è meglio creare una razza apposita
# Per altre possibili categorie: http://www.zoologia-animali.com/index.htm
HUMANOID   = RaceElement("Umanoide",  "Razza che possiede la forma umana: braccia, gambe e camminano in posizione eretta o semi-eretta")
MAMMAL     = RaceElement("Mammifero", "Razza che si riferisce ad un generico mammifero")
BIRD       = RaceElement("Uccello",   "Razza che si riferisce ad un generico uccello")
REPTILE    = RaceElement("Rettile",   "Razza che si riferisce ad un generico rettile")
AMPHIBIAN  = RaceElement("Anfibio",   "Razza che si riferisce ad un generico anfibio")
FISH       = RaceElement("Pesce",     "Razza che si riferisce ad un generico pesce")
CRUSTACEAN = RaceElement("Crostaceo", "Razza che si riferisce ad un generico crostaceo")
RODENT     = RaceElement("Roditore",  "Razza che si riferisce ad un generico roditore")
INSECT     = RaceElement("Insetto",   "Razza che si riferisce ad un generico insetto")
UNDEAD     = RaceElement("Non-Morto", "Razza che si riferisce ad un generico essere ritornato dall'oltretomba")
MAGICAL    = RaceElement("Magica",    "Razza che si riferisce ad un generica creatura nata dalla magia")
MONSTER    = RaceElement("Mostro",    "Razza che si riferisce ad un generico mostro")

# Razze Umanoidi, FLAG.HUMANOID
ARIAL    = RaceElement("[skyblue]Arial[close]",         "Uccelli antropomorfi simili agli umani nella forma ma quasi completamente ricoperti di piume e provvisti di ali sulla schiena che gli permettono di volare.")
CELT     = RaceElement("[white]Celta[close]",           "Il Celta è una razza umana che si è adattata al Lungo Inverno del Nord.")
CENTAUR  = RaceElement("[brown]Centaur$o[close]",       "Fiero e un po' arrogante il Centauro difficilmente ti farà salire in groppa 'per farti fare un giretto'.")
DROW     = RaceElement("[blueviolet]Drow[close]",       "Il Drow è l'antitesi dell'Elfo Alto e nemesi di molte razze su Nakilen, padroni del sottoterra e legati da una società matriarcale molto rigida e crudele.")
HIGHELF  = RaceElement("[royalblue]Elf$o Alt$o[close]", "L'Elfo Alto è la razza che si autodefinisce più pura e nobile di qualsiasi altra.")
WOODELF  = RaceElement("[lime]Elf$o Silvan$o[close]",   "L'Elfo Silvano è la razza che maggiormente riesce a trovare un equilibrio con la Natura.")
FELAR    = RaceElement("[orange]Felar[close]",          "Felini antropomorfi, flessuosi nei movimenti, agili nel salto e, a volte, dalla zampa 'troppo lesta' tesa ad alleggerire l'altrui borsa di denaro.")
FRIJEN   = RaceElement("[lightcyan]Frijen[close]",      "Sono creature dalle fattezze femminili e dagli occhi e il cuore freddo come il ghiaccio.")
GITH     = RaceElement("Gith",                          "Una razza particolare che ha il dono di viaggiare nei differenti piani, molto rara da incontrare. Non esistono tribù o stanziamenti Gith su Nakilen.")
GNOME    = RaceElement("[pink]Gnom$o[close]",           "Il pallino degli Gnomi è quello di ficcare il naso dappertutto e di costruire strumenti ingegnosi (preferibilmente rumorosi e che facciano qualche botto ogni tanto..)")
KENSAI   = RaceElement("[red]Kensai[close]",            "Il Kensai è un razza umana venuta da una lontana isola i cui guerrieri sono temuti in tutte le terre di Nakilen.")
HALFELF  = RaceElement("[green]Mezzelf$o[close]",       "Il Mezzelfo è spesso emarginato, nasce tra un umano ed un'altra razza elfica acquisendo pregi e difetti d'entrambe le razze.")
MINOTAUR = RaceElement("[gray]Minotaur$o[close]",       "Il Minotauro è una massa di muscoli provvista di corna, zoccoli, coda e tanta poca pazienza.")
DWARF    = RaceElement("[yellow]Nan$o[close]",          "Abili guerrieri, minatori e bevitori si dice che un tempo potessero addirittura domare i Draghi.")
ORC      = RaceElement("[olive]Orc$o[close]",           "L'Orco è un surrogato di caotiche azioni che portano spesso alla rottura di qualcosa.. o di qualcuno.")
PIXIE    = RaceElement("[cyan]Pixie[close]",            "Dal corpo minuto e provvisti di ali questi velocissimi esseri allietano, almeno secondo loro, chi è loro vicino facendo loro scherzi in continuazione.")
SATYR    = RaceElement("Satir$o",                       "")
THEPA    = RaceElement("[seagreen]Thepa[close]",        "Lucertole antropomorfe dalla pelle squamata, provvisti di coda e da lunghe zanne, riescono a nuotare molto bene sott'acqua potendo respirarvi liberamente.")
TUAREG   = RaceElement("[sandybrown]Tuareg[close]",     "Il Tuareg è una razza umana che si è adattata al Grand Deserto del Sud.")
HUMAN    = RaceElement("Uman$o",                        "L'Umano è la razza più diffusa su Nakilen e con maggiori capacità d'adattamento.")
HALFLING = RaceElement("Halfling",                      "Gli halfling sono simili a esseri umani, ma alti la metà circa. Di norma sono molto socievoli e amano tranquillità e il cibo")

# Razze Mammifere, FLAG.MAMMAL
BEAR     = RaceElement("Ors$o", "")
BAT      = RaceElement("Pipistrell$o", "")
BOAR     = RaceElement("Cinghiale", "")
CAT      = RaceElement("[white]Gatt$o[close]",          "Il gatto è la razza preferita da [limegreen]O[white]nirik[close]")
DOG      = RaceElement("Cane", "")
FERRET   = RaceElement("Furetto", "")
HORSE    = RaceElement("Cavall$o", "")
MONKEY   = RaceElement("Scimmia", "")
MULE     = RaceElement("Mul$o", "")
WOLF     = RaceElement("Lup$o", "")
OX       = RaceElement("Bue", "")
TIGER    = RaceElement("Tigre", "")
PIG      = RaceElement("Porc$o", "")
RABBIT   = RaceElement("Conigli$o", "")
FOX      = RaceElement("Volpe", "")

# Razze uccello, FLAG.BIRD
CROW        = RaceElement("Corv$o", "")
EAGLE       = RaceElement("Aquila", "")
HAWK        = RaceElement("Falc$o", "")
NIGHTINGALE = RaceElement("Usignol$o", "")
SWAN        = RaceElement("Cign$o", "")

# Razze Rettili, FLAG.REPTILE
DRAGON    = RaceElement("Drag$o", "")
DRACONIAN = RaceElement("Draconian$o", "")
SNAKE     = RaceElement("Serpente", "")
PYTHON    = RaceElement("Pitone", "")

# Razze anfibie, FLAG.AMPHIBIAN
FROG      = RaceElement("Rana", "")

# Razze pesce, FLAG.FISH
DOLPHIN   = RaceElement("Delfino", "")

# Razze crostacee, FLAG.CRUSTACEAN
CRAYFISH  = RaceElement("Gambero", "")

# Razze roditore, FLAG.RODENT
RAT       = RaceElement("Ratt$o", "")

# Razze Insetto, FLAG.INSECT (sono compresi anche gli anellidi per ora)
ANT       = RaceElement("Formica", "")
BEE       = RaceElement("Ape", "")
BEETLE    = RaceElement("Coleotter$o", "")
BUTTERFLY = RaceElement("Farfalla", "")
FLY       = RaceElement("Mosca", "")
LOCUST    = RaceElement("Locusta", "")
SPIDER    = RaceElement("Ragn$o", "")
WORM      = RaceElement("Verme", "")
CENTIPEDE = RaceElement("Centopiedi", "")

# Razze non-morte, FLAG.UNDEAD (forse alcune razze sono invece da considerarsi magiche)
GHOUL     = RaceElement("Ghoul", "")
SHADOW    = RaceElement("Ombra", "")
SKELETON  = RaceElement("Scheletro", "")
WIGHT     = RaceElement("Wight", "")
ZOMBIE    = RaceElement("Zombie", "")
SPIRIT    = RaceElement("Spirito", "")  # La differnza tra spirit e ghost? Lo spirito è una forma dell'anima di una creatura ancora viva? mh... da pensare
GHOST     = RaceElement("Fantasma", "")

# Razze magiche, FLAG.MAGICAL
UNICORN  = RaceElement("Unicorno", "")

# Razze Mostruose, FLAG.MONSTER: (alcune di queste razze mi sa che sono da spostare in humanoid)
BUGBEAR         = RaceElement("Bugbear", "")
GARGOYLE        = RaceElement("Gargoyle", "")
GNOLL           = RaceElement("Gnoll", "")
GOBLIN          = RaceElement("Goblin", "")
GOLEM           = RaceElement("Golem", "")
GORGON          = RaceElement("Gorgone", "")
HARPY           = RaceElement("Arpia", "")
HOBGOBLIN       = RaceElement("Hobgoblin", "")
KOBOLD          = RaceElement("Koboldo", "")
TROLL           = RaceElement("Troll", "rigenerazione e suscettibile al fuoco, come i classici")
ILLITHID        = RaceElement("Illithid", "Mindflayer per gli amici..")
SLIME           = RaceElement("Slime", "")  # leggere caratteristiche e habitat qui: http://en.wikipedia.org/wiki/Green_slime_(Dungeons_%26_Dragons)
MIMIC           = RaceElement("Mimic", "Riesce ad ingannare le creature fingendo d'essere un oggetto comune attaccandole quando si avvicinano e cibandosene una volte sconfitte")
MOLD            = RaceElement("Muffa", "")  # la muffa! sulle armi in legno! nooooo, serve la moldproof! (solo Sulfrum poteva inventarsi una cosa simile..)
RUSTMONSTER     = RaceElement("Rustmonster", "")  # http://www.nerdnyc.com/tmp/5.jpg   per questo servirà anche la flag rustproof
SHRIEKER        = RaceElement("Shrieker", "")  # Che brutto... http://scienceblogs.com/afarensis/upload/2006/08/Shrieker.JPG non utilizzatelo tranne che nelle aree Incubo o quella del Portale
STIRGE          = RaceElement("Stirge", "")
DEMON           = RaceElement("Demone", "")
AIR_ELEMENTAL   = RaceElement("Atronach dell'Aria", "")
EARTH_ELEMENTAL = RaceElement("Atronach della Terra", "")
FIRE_ELEMENTAL  = RaceElement("Atronach del Fuoco", "")
WATER_ELEMENTAL = RaceElement("Atronach dell'Acqua", "")


#===============================================================================

# Razze giocabili
HUMAN.playable    = True
CELT.playable     = True
TUAREG.playable   = True
KENSAI.playable   = True
DWARF.playable    = True
FELAR.playable    = True
FRIJEN.playable   = True
ARIAL.playable    = True
THEPA.playable    = True
ORC.playable      = True
CENTAUR.playable  = True
HIGHELF.playable  = True
DROW.playable     = True
MINOTAUR.playable = True
PIXIE.playable    = True


# Limitazioni sulla sessualità razziale
FRIJEN.allowed_sexs = Flags(SEX.FEMALE)
THEPA.allowed_sexs  = Flags(SEX.NEUTRAL)


# Peso minimo, medio e massimo, valori relativi ai maschi adulti
HUMAN.weight_low,    HUMAN.weight_medium,    HUMAN.weight_high     = 40000,  60000, 100000
CELT.weight_low,     CELT.weight_medium,     CELT.weight_high      = 45000,  65000, 105000
TUAREG.weight_low,   TUAREG.weight_medium,   TUAREG.weight_high    = 38000,  58000,  98000
KENSAI.weight_low,   KENSAI.weight_medium,   KENSAI.weight_high    = 39000,  59000,  99000
DWARF.weight_low,    DWARF.weight_medium,    DWARF.weight_high     = 43000,  63000, 103000
FELAR.weight_low,    FELAR.weight_medium,    FELAR.weight_high     = 34000,  54000,  94000
FRIJEN.weight_low,   FRIJEN.weight_medium,   FRIJEN.weight_high    = 37000,  54000,  90000
ARIAL.weight_low,    ARIAL.weight_medium,    ARIAL.weight_high     = 30000,  50000,  90000
THEPA.weight_low,    THEPA.weight_medium,    THEPA.weight_high     = 50000,  70000, 110000
ORC.weight_low,      ORC.weight_medium,      ORC.weight_high       = 55000,  75000, 115000
GNOME.weight_low,    GNOME.weight_medium,    GNOME.weight_high     = 32000,  47000,  62000
CENTAUR.weight_low,  CENTAUR.weight_medium,  CENTAUR.weight_high   = 80000, 115000, 130000
HIGHELF.weight_low,  HIGHELF.weight_medium,  HIGHELF.weight_high   = 42000,  62000, 102000
WOODELF.weight_low,  WOODELF.weight_medium,  WOODELF.weight_high   = 35000,  55000,  95000
HALFELF.weight_low,  HALFELF.weight_medium,  HALFELF.weight_high   = 39000,  59000,  99000
DROW.weight_low,     DROW.weight_medium,     DROW.weight_high      = 37000,  57000,  97000
CAT.weight_low,      CAT.weight_medium,      CAT.weight_high       =  2000,   4000,   6000
MINOTAUR.weight_low, MINOTAUR.weight_medium, MINOTAUR.weight_high  = 90000, 125000, 160000
PIXIE.weight_low,    PIXIE.weight_medium,    PIXIE.weight_high     =   300,    600,    900

# Altezza minima, media e massima, valori relativi ai maschi adulti
HUMAN.height_low,    HUMAN.height_medium,    HUMAN.height_high    = 140, 170, 200
CELT.height_low,     CELT.height_medium,     CELT.height_high     = 150, 175, 205
TUAREG.height_low,   TUAREG.height_medium,   TUAREG.height_high   = 138, 168, 198
KENSAI.height_low,   KENSAI.height_medium,   KENSAI.height_high   = 136, 166, 196
DWARF.height_low,    DWARF.height_medium,    DWARF.height_high    = 120, 140, 160
FELAR.height_low,    FELAR.height_medium,    FELAR.height_high    = 134, 164, 194
FRIJEN.height_low,   FRIJEN.height_medium,   FRIJEN.height_high   = 145, 175, 205
ARIAL.height_low,    ARIAL.height_medium,    ARIAL.height_high    = 136, 166, 196
THEPA.height_low,    THEPA.height_medium,    THEPA.height_high    = 153, 179, 209
ORC.height_low,      ORC.height_medium,      ORC.height_high      = 155, 182, 214
GNOME.height_low,    GNOME.height_medium,    GNOME.height_high    = 110, 135, 150
CENTAUR.height_low,  CENTAUR.height_medium,  CENTAUR.height_high  = 160, 185, 220
HIGHELF.height_low,  HIGHELF.height_medium,  HIGHELF.height_high  = 143, 173, 203
WOODELF.height_low,  WOODELF.height_medium,  WOODELF.height_high  = 135, 165, 195
HALFELF.height_low,  HALFELF.height_medium,  HALFELF.height_high  = 139, 169, 199
DROW.height_low,     DROW.height_medium,     DROW.height_high     = 137, 167, 197
CAT.height_low,      CAT.height_medium,      CAT.height_high      =  10,  15,  20
MINOTAUR.height_low, MINOTAUR.height_medium, MINOTAUR.height_high = 170, 210, 240  # L'altezza di un minotauro include gli zoccoli ma si calcola fino alla testa escludendo le corna
PIXIE.height_low,    PIXIE.height_medium,    PIXIE.height_high    =  15,  20,  25

# Suddivisione per fascia di età di ogni razza
HUMAN.age_adolescence,    HUMAN.age_adult,    HUMAN.age_old    = 12, 18,  60
CELT.age_adolescence,     CELT.age_adult,     CELT.age_old     = 10, 17,  65
TUAREG.age_adolescence,   TUAREG.age_adult,   TUAREG.age_old   = 11, 17,  57
KENSAI.age_adolescence,   KENSAI.age_adult,   KENSAI.age_old   = 11, 18,  62
DWARF.age_adolescence,    DWARF.age_adult,    DWARF.age_old    = 14, 33, 400
FELAR.age_adolescence,    FELAR.age_adult,    FELAR.age_old    = 13, 24, 150
FRIJEN.age_adolescence,   FRIJEN.age_adult,   FRIJEN.age_old   = 14, 22, 140
ARIAL.age_adolescence,    ARIAL.age_adult,    ARIAL.age_old    =  9, 16, 135
THEPA.age_adolescence,    THEPA.age_adult,    THEPA.age_old    = 10, 16, 125
ORC.age_adolescence,      ORC.age_adult,      ORC.age_old      =  7, 22,  95
GNOME.age_adolescence,    GNOME.age_adult,    GNOME.age_old    = 12, 18,  70
CENTAUR.age_adolescence,  CENTAUR.age_adult,  CENTAUR.age_old  =  5, 15,  75
HIGHELF.age_adolescence,  HIGHELF.age_adult,  HIGHELF.age_old  = 16, 35, 400
WOODELF.age_adolescence,  WOODELF.age_adult,  WOODELF.age_old  = 14, 26, 350
HALFELF.age_adolescence,  HALFELF.age_adult,  HALFELF.age_old  = 13, 24, 300
DROW.age_adolescence,     DROW.age_adult,     DROW.age_old     =  8, 37, 350
CAT.age_adolescence,      CAT.age_adult,      CAT.age_old      =  1,  2,  10
MINOTAUR.age_adolescence, MINOTAUR.age_adult, MINOTAUR.age_old = 15, 23, 250
PIXIE.age_adolescence,    PIXIE.age_adult,    PIXIE.age_old    =  1,  3,  45

# Razze che possiedono i capelli
HUMAN.have_hair    = True
CELT.have_hair     = True
TUAREG.have_hair   = True
KENSAI.have_hair   = True
DWARF.have_hair    = True
FRIJEN.have_hair   = True
GNOME.have_hair    = True
ORC.have_hair      = True
PIXIE.have_hair    = True
CENTAUR.have_hair  = True
HIGHELF.have_hair  = True
WOODELF.have_hair  = True
HALFELF.have_hair  = True
DROW.have_hair     = True

# Linguaggi naturali e preferiti
HUMAN.natural_language    = LANGUAGE.COMMON
CELT.natural_language     = LANGUAGE.COMMON
TUAREG.natural_language   = LANGUAGE.COMMON
KENSAI.natural_language   = LANGUAGE.COMMON
DWARF.natural_language    = LANGUAGE.DWARVEN
FELAR.natural_language    = LANGUAGE.KHAJIT
FRIJEN.natural_language   = LANGUAGE.FRIJEN
ARIAL.natural_language    = LANGUAGE.ARIAL
THEPA.natural_language    = LANGUAGE.ARGONIAN
GNOME.natural_language    = LANGUAGE.GNOME
ORC.natural_language      = LANGUAGE.ORCISH
CENTAUR.natural_language  = LANGUAGE.CENTAUR
HIGHELF.natural_language  = LANGUAGE.ELVEN
WOODELF.natural_language  = LANGUAGE.ELVEN
HALFELF.natural_language  = LANGUAGE.ELVEN
DROW.natural_language     = LANGUAGE.DROW
#CAT.natural_language     = LANGUAGE.FELIN
MINOTAUR.natural_language = LANGUAGE.TAUREN
PIXIE.natural_language    = LANGUAGE.PIXIE

# Lista dei linguaggi solitamente conosciuti, dal quello con maggiore
# diffusione a quello minore
HUMAN.initial_languages    = [LANGUAGE.COMMON, ]
CELT.initial_languages     = [LANGUAGE.COMMON, ]
TUAREG.initial_languages   = [LANGUAGE.COMMON, ]
KENSAI.initial_languages   = [LANGUAGE.COMMON, ]
DWARF.initial_languages    = [LANGUAGE.DWARVEN, LANGUAGE.COMMON, LANGUAGE.TAUREN]
FELAR.initial_languages    = [LANGUAGE.KHAJIT, LANGUAGE.COMMON]
FRIJEN.initial_languages   = [LANGUAGE.FRIJEN, LANGUAGE.ELVEN, LANGUAGE.COMMON]
ARIAL.initial_languages    = [LANGUAGE.ARIAL, LANGUAGE.COMMON]
THEPA.initial_languages    = [LANGUAGE.ARGONIAN, LANGUAGE.COMMON]
GNOME.initial_languages    = [LANGUAGE.GNOME, LANGUAGE.COMMON]
ORC.initial_languages      = [LANGUAGE.ORCISH, LANGUAGE.COMMON]
CENTAUR.initial_languages  = [LANGUAGE.CENTAUR, LANGUAGE.COMMON, LANGUAGE.ELVEN]
HIGHELF.initial_languages  = [LANGUAGE.ELVEN, LANGUAGE.COMMON, LANGUAGE.DROW]
WOODELF.initial_languages  = [LANGUAGE.ELVEN, LANGUAGE.COMMON]
HALFELF.initial_languages  = [LANGUAGE.COMMON, LANGUAGE.ELVEN]
DROW.initial_languages     = [LANGUAGE.DROW, LANGUAGE.COMMON, LANGUAGE.ELVEN]
MINOTAUR.initial_languages = [LANGUAGE.TAUREN, LANGUAGE.COMMON, LANGUAGE.DWARVEN]
PIXIE.initial_languages    = [LANGUAGE.PIXIE, LANGUAGE.COMMON, LANGUAGE.ELVEN]


# La potenza della voce varia da razza a razza
CELT.voice_potence     = +1  # I Celti son abituati a parlare un po' più forte del normale
FRIJEN.voice_potence   = +1  # Le Frijen hanno una voce più acuta che facilmente viene portata lontano dai venti del Nord
DWARF.voice_potence    = +4  # I Nani parlano forte e basta :P
THEPA.voice_potence    = -2  # Fisiologicamente la gola dei Thepa produce meno suono
GNOME.voice_potence    = -4  # Gli gnomi per la loro corporatura producono suoni meno potenti
ORC.voice_potence      = +6  # Gli orchi invece proprio per la loro grossa corporatura producono voci potenti
WOODELF.voice_potence  = -2  # Gli elfi silvani sono abiutati a stare nella natura e parlano più piano
DROW.voice_potence     = -2  # I drow sono abiutati a stare nelle profondità della terra e parlano più piano
MINOTAUR.voice_potence = +8  # Ancor più i minotauri
PIXIE.voice_potence    = -8  # Ancor meno i pixie


# Lista dei verbi utilizzati al posto del verb_you e verb_it del canale
# CHANNEL.SAY, è meglio inserire solo quelli relativi alle razze non
# intelligenti.
# (TD) nota per me stesso: pag 703
DWARF.say_verb_you,    DWARF.say_verb_it    = "Borbotti",  " borbotta"
FELAR.say_verb_you,    FELAR.say_verb_it    = "Miagoli",   " miagola"
ARIAL.say_verb_you,    ARIAL.say_verb_it    = "Fischi",    " fischia"
THEPA.say_verb_you,    THEPA.say_verb_it    = "Sibili",    " sibila"
ORC.say_verb_you,      ORC.say_verb_it      = "grugnisci", " Grugnisce"
CENTAUR.say_verb_you,  CENTAUR.say_verb_it  = "Nitrisci",  " nitrisce"
CAT.say_verb_you,      CAT.say_verb_it      = "Miagoli",   " miagola"
MINOTAUR.say_verb_you, MINOTAUR.say_verb_it = "Muggisci",  " muggisce"
PIXIE.say_verb_you,    PIXIE.say_verb_it    = "Ronzi",     " ronza"
HORSE.say_verb_you,    HORSE.say_verb_it    = "Nitrisci", " nistrisce"

# Verbi che indicano uno spostamento tra una stanza ed un'altra
PIXIE.go_verb_you, PIXIE.go_verb_it, PIXIE.come_verb_it = "Guizzi", "guizza",     "ha guizzato"
CAT.go_verb_you,   CAT.go_verb_it,   CAT.come_verb_it   = "Zampetti", "zampetta", "ha zampettato"

PIXIE.run_verb_you, PIXIE.run_verb_it,     PIXIE.runned_verb_it   = "Sfrecci",     "sfreccia",     "ha sfrecciato"
CAT.run_verb_you,   CAT.run_verb_it,       CAT.runned_verb_it     = "Trotterelli", "trotterella",  "ha trotterellato"
HORSE.run_verb_you, HORSE.run_verb_it,     HORSE.runned_verb_it   = "Galoppi",     "galoppa",      "ha galoppato"
CENTAUR.run_verb_you, CENTAUR.run_verb_it, CENTAUR.runned_verb_it = "Galoppi",     "galoppa",      "ha galoppato"

# Lista delle parti del corpo variabili da razza a razza
DWARF.hand,    DWARF.hands    = "mano ruvida",     "mani ruvide"
FELAR.hand,    FELAR.hands    = "mano artigliata", "mani artigliate"
FRIJEN.hand,   FRIJEN.hands   = "mano gelida",     "mani gelide"
ARIAL.hand,    ARIAL.hands    = "mano piumata",    "mani piumate"
THEPA.hand,    THEPA.hands    = "mano squamosa",   "mani squamose"
CAT.hand,      CAT.hands      = "zampa",           "zampe"
MINOTAUR.hand, MINOTAUR.hands = "possente mano",   "possenti mani"

ARIAL.foot,    ARIAL.feet,    ARIAL.feet2    = "zampa artigliata", "zampe artigliate", "alle tue zampe artigliate"
FELAR.foot,    FELAR.feet,    FELAR.feet2    = "zampa",            "zampe",            "alle tue zampe"
FRIJEN.foot,   FRIJEN.feet,   FRIJEN.feet2   = "piede gelido",     "piedi gelidi",     "ai tuoi piedi gelidi"
THEPA.foot,    THEPA.feet,    THEPA.feet2    = "zampa squamosa",   "zampe squamose",   "alle tue zampe squamose"
CENTAUR.foot,  CENTAUR.feet,  CENTAUR.feet2  = "zoccolo",          "zoccoli",          "ai tuoi zoccoli"
CAT.foot,      CAT.feet,      CAT.feet2      = "zampa",            "zampe",            "alle tue zampe"
MINOTAUR.foot, MINOTAUR.feet, MINOTAUR.feet2 = "zoccolo",          "zoccoli",          "ai tuoi zoccoli"

MAMMAL.skin         = "pelliccia"
BIRD.skin           = "livrea piumata"
REPTILE.skin        = "pelle squamosa"
FISH.skin           = "pelle squamosa"
CRUSTACEAN.skin     = "corazza"
RODENT.skin         = "pelliccia"
INSECT.skin         = "pelo"
UNDEAD.skin         = "pelle morta"
ARIAL.skin          = "livrea piumata"
FELAR.skin          = "pelliccia"
SATYR.skin          = "pelliccia"
THEPA.skin          = "pelle squamosa"
BEAR.skin           = "pelliccia"
BOAR.skin           = "pelliccia"
CAT.skin            = "pelliccia"
DOG.skin            = "pelliccia"
FERRET.skin         = "pelliccia"
MONKEY.skin         = "pelliccia"
WOLF.skin           = "pelliccia"
TIGER.skin          = "pelliccia"
RABBIT.skin         = "pelliccia"
FOX.skin            = "pelliccia"
CROW.skin           = "livrea piumata"
EAGLE.skin          = "livrea piumata"
HAWK.skin           = "livrea piumata"
NIGHTINGALE.skin    = "livrea piumata"
SWAN.skin           = "livrea piumata"
DRAGON.skin         = "pelle squamosa"
DRACONIAN.skin      = "pelle squamosa"
SNAKE.skin          = "pelle squamosa"
PYTHON.skin         = "pelle squamosa"
CRAYFISH.skin       = "corazza"
ANT.skin            = "corazza"
BEE.skin            = "peluria"
BEETLE.skin         = "corazza"
BUTTERFLY.skin      = "peluria"
FLY.skin            = "peluria"
LOCUST.skin         = "corazza"
SPIDER.skin         = "peluria"
CENTIPEDE.skin      = "corazza"
GHOUL.skin          = "pelle morta"
SHADOW.skin         = "nebbia"
SKELETON.skin       = "pelle e ossa"
WIGHT.skin          = "nebbia"
ZOMBIE.skin         = "pelle morta"
SPIRIT.skin         = "nebbia"
GHOST.skin          = "nebbia"
BUGBEAR.skin        = "pelliccia"
GNOLL.skin          = "pelliccia"
GOLEM.skin          = "pietra"
GORGON.skin         = "pelle squamosa"
HARPY.skin          = "livrea piumata"
KOBOLD.skin         = "pelle squamosa"
SLIME.skin          = "gelatina"
MOLD.skin           = "patina di spore"
RUSTMONSTER.skin    = "patina di ruggine"
AIR_ELEMENTAL.skin   = "pelle aerea"
EARTH_ELEMENTAL.skin = "pelle terriccia"
FIRE_ELEMENTAL.skin  = "pelle infuocata"
WATER_ELEMENTAL.skin = "pelle acquea"

DRAGON.tongue    = "[red]lingua biforcuta[close]"
DRACONIAN.tongue = "[red]lingua biforcuta[close]"
PYTHON.tongue    = "[red]lingua biforcuta[close]"
REPTILE.tongue   = "[red]lingua biforcuta[close]"
SNAKE.tongue     = "[red]lingua biforcuta[close]"
THEPA.tongue     = "[red]lingua biforcuta[close]"

# Elenco delle razze che possono annusare sott'acqua
AMPHIBIAN.smell_on_water      = True
FISH.smell_on_water           = True
CRUSTACEAN.smell_on_water     = True
THEPA.smell_on_water          = True
FROG.smell_on_water           = True
DOLPHIN.smell_on_water        = True
CRAYFISH.smell_on_water       = True
SLIME.smell_on_water          = True
WATER_ELEMENTAL.smell_on_water = True


#-------------------------------------------------------------------------------

def get_playable_races():
    playble_races = []
    for race in elements:
        if race.playable:
            playble_races.append(race)
    return playble_races
#- Fine Funzione -


def sort_playable_first():
    from src.color import remove_colors

    playable_races = []
    for race in elements:
        if race.playable:
            playable_races.append(race)

    mob_races = []
    for race in elements:
        if not race.playable:
            mob_races.append(race)

    return (sorted(playable_races, key=lambda race_name: remove_colors(race.name))
          + sorted(mob_races,      key=lambda race_name: remove_colors(race.name)))
# - Fine Metodo -


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)


#===============================================================================

# Note sulle razze di Aarit:
#THOUL: bocciata
#DEEPGNOME: bocciata
#githyanki e githzerai fuse nella razza GITH
#ooze è lo slime con poche differenze
#i mindflyer sono gli illithid
#